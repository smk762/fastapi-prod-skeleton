from __future__ import annotations
from fastapi import APIRouter, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

metrics_router = APIRouter()

REQ_COUNT = Counter(
    "http_requests_total",
    "HTTP requests",
    ["method", "path", "status_code"],
)

REQ_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "path", "status_code"],
    # buckets left default by prometheus_client if not specified
)

def observe_request(*, method: str, path: str, status_code: int, duration_s: float) -> None:
    REQ_COUNT.labels(method=method, path=path, status_code=str(status_code)).inc()
    REQ_LATENCY.labels(method=method, path=path, status_code=str(status_code)).observe(duration_s)

@metrics_router.get("/metrics", include_in_schema=False)
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
