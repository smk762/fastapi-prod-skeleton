# Lifecycle Event Example: External Service Checks

Use FastAPI's lifespan events (see [FastAPI Lifespan Events](https://fastapi.tiangolo.com/advanced/events/)) to register code that runs for the lifetime of the app. This example starts a scheduled monitor that checks external dependencies every five minutes and allows the app to tear it down cleanly during shutdown.

```python
from __future__ import annotations

import asyncio
import httpx
from contextlib import asynccontextmanager

from fastapi import FastAPI

EXTERNAL_HEALTH_URLS = [
    "https://auth.example.com/health",
    "https://payments.example.com/health",
]
CHECK_INTERVAL_SECONDS = 300


async def _check_service(url: str) -> None:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(url, params={"source": "lifespan"})
        response.raise_for_status()


async def _monitor_services(stop: asyncio.Event) -> None:
    while not stop.is_set():
        for url in EXTERNAL_HEALTH_URLS:
            try:
                await _check_service(url)
            except Exception as exc:  # noqa: BLE004
                # Replace with structured logging / alerting hook
                print(f"External service check failed for {url}: {exc}")
        await asyncio.wait_for(stop.wait(), timeout=CHECK_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop_event = asyncio.Event()
    monitor_task = asyncio.create_task(_monitor_services(stop_event))
    try:
        yield
    finally:
        stop_event.set()
        await monitor_task


app = FastAPI(lifespan=lifespan)
```

> Drawn from the FastAPI lifespan walkthrough, the code above yields before accepting traffic and resumes after shutting down so you can manage shared resources and scheduled monitors for the entire application lifespan.

Adapt the check logic to your actual services, wire in proper logging/metrics, and handle retries or alerting once an external dependency goes unhealthy.
