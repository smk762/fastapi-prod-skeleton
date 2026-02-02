# Production-Grade API Design Rules (Reference)

This repository is a FastAPI reference skeleton that implements the **production-grade API design concepts** below.

## Concepts implemented

1. **Contracts first**
   - OpenAPI is treated as the contract of record.
   - Examples included on key endpoints and error responses.
   - Versioning uses **`/v1` in the URL path**.

2. **Idempotency**
   - `PUT`/`DELETE` are idempotent.
   - `POST` create endpoints support `Idempotency-Key` with safe retries.
   - Key is scoped by `(principal, route)` and stores the original response for replay.

3. **Pagination**
   - Cursor-based pagination (opaque cursor).
   - Stable ordering (`created_at`, then `id`).
   - Filters apply before pagination.

4. **Errors**
   - Domain errors map to HTTP codes.
   - Error responses include: `code`, `message`, `request_id`.
   - Validation errors do **not** return 500.

5. **Timeouts + cancellation**
   - Middleware enforces a request timeout with cancellation.
   - All DB operations use request-scoped session and cooperate with cancellation.

6. **Auth**
   - JWT bearer auth (example implementation).
   - Scope-based authorization (example `items:read`, `items:write`).
   - Rate limiting is documented as a required production concern (stub included).

7. **Backward compatibility**
   - Additive changes only.
   - Enums tolerate unknown values.
   - Deprecation is documented as a measured process.

8. **Observability**
   - Structured logging with `request_id` in every log.
   - Trace header propagation (`traceparent`) supported.
   - Prometheus metrics endpoint (`/metrics`) for latency + errors.

## What this skeleton is (and isn't)

- ✅ A practical baseline you can extend in real systems
- ✅ Enforces operational concerns (request IDs, errors, retries, metrics)
- ✅ Demonstrates patterns interviewers probe for
- ❌ Not a full platform (no full RBAC, no full tracing pipeline, etc.)
