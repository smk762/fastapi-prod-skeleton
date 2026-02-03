# Scaling Guidance

This companion guide describes how to evolve the skeleton toward high-scale deployments once the API and operational basics are in place.

## Data plane scaling

- **Production database**: Swap SQLite for Postgres/MySQL with connection pooling, prepared plans, and replica-aware queries. Add read replicas or a sharding strategy for write-heavy workloads.
- **Cursor pagination tuning**: For very large datasets, pre-aggregate cursor fields, paginate on indexed columns, and avoid deep offset scans by keeping cursor data compact and ordered (`created_at` + `id`).
- **Caching**: Introduce Redis/memcached for caching hot lookups, idempotency keys, and rate-limit counters. Use cache invalidation strategies that respect the error envelope and request IDs.
- **Background processing**: Offload long-running tasks (notifications, analytics, uploads) to worker queues (Celery, Prefect, etc.) with retry policies, visibility into failures, and a TTL on retries.

## Control plane & throughput

- **Async/concurrency**: Make sure all I/O (DB, HTTP, cache) uses async clients so Uvicorn workers stay responsive; consider `asyncpg`, HTTP client pools, and explicit cancellation guards.
- **Rate limiting and throttling**: Build request throttles per principal/scope backed by Redis, combined with documented retry-after headers and idempotency key / nonce reuse limits.
- **Autoscaling**: Implement horizontal pod autoscaling or container scaling based on application latency, queue depth, or CPU/memory headroom. Couple with graceful shutdown via request timeouts/cancellation.
- **Global load balancing**: Use cloud edge or CDN layers to terminate TLS, enforce WAF rules, and route traffic across regions for geo-distribution.

## Observability and reliability at scale

- **Trace sampling**: Use distributed tracing (OpenTelemetry/Jaeger) with adjustable sampling to keep costs bounded. Ensure `traceparent` flows through async tasks and background jobs.
- **SLO-driven alerts**: Track latency/error budgets per endpoint/client, burn rate alerts, and automated escalations. Tie dashboards to service-level indicators in `docs/operational-readiness.md`.
- **Capacity and chaos testing**: Regularly test with synthetic load, DB failovers, and degraded cache/back-pressure scenarios. Validate idempotency and cursor behavior under parallel execution.

## Infrastructure and release management

- **Immutable infrastructure**: Build deployment artifacts (containers) with pinned base images, vulnerability scanning, and reproducible builds. Use image promotion rather than rebuilds.
- **Feature flags and dark launches**: Control rollout of new capabilities via flagging systems with auto-disable on regressions, keeping observability in sync with flag state.
- **Disaster recovery**: Define backup/restore for databases, redis data, service config. Automate failover drills and postmortems to validate RTO/RPO targets.
- **Cross-team runbooks**: Keep scaling decisions documented (e.g., shard strategy, cache layering, autoscaler policies, runbook for scaling incidents) and versioned with the repo.

Link back to `docs/operational-readiness.md` for the core observability/security checklist and keep this scaling guidance synced with any infrastructure or pipeline changes.
