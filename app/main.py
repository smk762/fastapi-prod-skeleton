from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.config import settings
from app.logging import configure_logging, log
from app.api.v1.router import router as v1_router
from app.infra.db import init_db
from app.infra.middleware import RequestContextMiddleware, TimeoutMiddleware
from app.infra.metrics import metrics_router
from app.domain.errors import AppError

configure_logging(settings.LOG_LEVEL)
logger = log()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    openapi_url="/openapi.json",
)

# Middleware order matters: request context first, then timeout wrapper
app.add_middleware(RequestContextMiddleware)
app.add_middleware(TimeoutMiddleware, timeout_ms=settings.REQUEST_TIMEOUT_MS)

app.include_router(v1_router, prefix="/v1")
app.include_router(metrics_router)

@app.on_event("startup")
def _startup() -> None:
    init_db()
    logger.info("startup", env=settings.ENV)

@app.exception_handler(AppError)
def app_error_handler(_, exc: AppError):
    # Consistent error envelope
    return JSONResponse(
        status_code=exc.http_status,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": exc.request_id,
            }
        },
    )
