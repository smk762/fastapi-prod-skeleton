from __future__ import annotations
import secrets
import time
from typing import Callable

import anyio
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.logging import log
from app.infra.metrics import observe_request

logger = log()

REQUEST_ID_HEADER = "X-Request-Id"
TRACEPARENT_HEADER = "traceparent"

class RequestContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable):
        rid = request.headers.get(REQUEST_ID_HEADER) or f"req_{secrets.token_urlsafe(12)}"
        request.state.request_id = rid
        request.state.traceparent = request.headers.get(TRACEPARENT_HEADER)

        start = time.perf_counter()
        try:
            resp: Response = await call_next(request)
            return resp
        finally:
            duration = time.perf_counter() - start
            status = getattr(getattr(request, "scope", {}), "status", None)
            # Response status isn't directly in scope; metrics is recorded in observe_request middleware below.
            logger.info(
                "request",
                request_id=rid,
                method=request.method,
                path=request.url.path,
                query=str(request.url.query),
                traceparent=request.state.traceparent,
                duration_ms=int(duration * 1000),
            )

class TimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, timeout_ms: int):
        super().__init__(app)
        self.timeout_ms = timeout_ms

    async def dispatch(self, request: Request, call_next: Callable):
        method = request.method
        path = request.url.path
        start = time.perf_counter()

        try:
            with anyio.fail_after(self.timeout_ms / 1000):
                response = await call_next(request)
        except TimeoutError:
            # 504 with consistent envelope
            rid = getattr(request.state, "request_id", "unknown")
            response = Response(
                content=f'{{"error": {{"code":"TIMEOUT","message":"request timed out","request_id":"{rid}"}}}}',
                media_type="application/json",
                status_code=504,
            )
        finally:
            duration = time.perf_counter() - start
            status_code = getattr(locals().get("response", None), "status_code", 500)
            observe_request(method=method, path=path, status_code=status_code, duration_s=duration)

        # Propagate request id and trace headers back
        response.headers[REQUEST_ID_HEADER] = getattr(request.state, "request_id", "unknown")
        if getattr(request.state, "traceparent", None):
            response.headers[TRACEPARENT_HEADER] = request.state.traceparent
        return response
