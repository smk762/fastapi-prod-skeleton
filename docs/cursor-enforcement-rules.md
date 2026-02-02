# Cursor Enforcement Rules (Reject These Patterns)

These are rules the IDE agent should enforce during generation/review.

## Contract & versioning
- Reject endpoints not under `/v1`.
- Reject undocumented request/response schemas (must be typed and appear in OpenAPI).
- Reject breaking response changes (field removal/rename).

## Idempotency
- Reject `POST` creates without `Idempotency-Key` support OR explicit justification in docs.
- Reject handlers that perform side-effects before idempotency check is performed.
- Reject returning different responses for the same idempotency key + same principal.

## Pagination
- Reject offset pagination on mutable collections.
- Reject cursor formats that are not opaque (must be base64/opaque).
- Reject unstable ordering (must include a unique tie-breaker like `id`).

## Errors
- Reject `500` for validation or known domain errors.
- Reject error responses without:
  - `error.code`
  - `error.message`
  - `error.request_id`
- Reject ad-hoc error JSON shapes per endpoint.

## Timeouts & cancellation
- Reject long blocking calls without timeout/cancellation cooperation.
- Reject spawning background tasks in request path without ownership/cancellation.
- Reject creating new event loops/threads per request.

## Auth & security
- Reject unauthenticated access to non-public endpoints.
- Reject mixing authn and authz (must check scopes/roles explicitly).
- Reject missing rate-limit plan (even if stubbed).

## Observability
- Reject logs without `request_id`.
- Reject missing metrics on new endpoint families.
- Reject missing correlation propagation for `traceparent` header.

## Backward compatibility
- Reject enum narrowing/removal without compatibility plan.
- Reject removal of fields/endpoints without a deprecation metric and timeline.
