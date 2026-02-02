# IDE Agent Directives

Use these directives when generating code or refactoring this project.

## Prime directive
**Design APIs as if you're on-call for them.**

## What to do first (always)
1. Update the OpenAPI contract by editing endpoints/schemas in code and examples.
2. Implement domain/service logic behind a clear interface.
3. Add observability hooks (logs/metrics) for new flows.
4. Add tests for:
   - success case
   - validation failures
   - domain errors mapping
   - idempotency replay behavior
   - cursor pagination stability

## Code generation expectations
- Prefer small, composable modules:
  - `app/api/v1/*` for routes
  - `app/domain/*` for business logic and errors
  - `app/infra/*` for DB, idempotency, auth, metrics
- No "god" files.
- No hidden global state in request paths.
- All error responses must use the shared error envelope.

## Operational requirements for any new endpoint
- Versioned under `/v1`
- Stable response envelope
- Machine error codes for predictable client handling
- `request_id` returned to clients and logged
- Timeouts respected; no leaked background tasks
- If endpoint creates side-effects, it must be idempotent or support idempotency keys
- Pagination must be cursor-based for lists

## When unsure
Default to:
- additive changes
- backward compatible behavior
- explicit error codes
- safe retries
