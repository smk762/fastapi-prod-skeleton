# Operational Readiness Checklist

This doc rounds out the production story with the operational, security, and deployment practices that should accompany the API-level rules in the other docs.

## Deployment and lifecycle automation

- **CI/CD pipelines**: Build, lint, test, and publish container images (or other deploy artifacts) in a single pipeline. Gate promotions on green tests+security scans.
- **Safe rollout/rollback**: Automate canary percentages or blue/green switches with health checks. Provide rollback steps in case a release violates an SLO.
- **Schema and migration hygiene**: Include migration generation + verification in CI, keep migrations in source control, and run them via the deployment pipeline with dry-run checks for destructive changes.
- **Environment parity**: Keep staging mirrors of prod (config, secrets, data sampling) and require smoke tests there before promoting.
- **Feature toggles**: Use feature flags to decouple deployments from releases, with dashboards showing flag states per environment.
- **Dependency/OSS scanning**: Run SCA tools (e.g., Safety/Dependabot) early, block builds on high/critical findings, and track fix timelines.

## Observability, SLOs, and incident readiness

- **SLOs & alerting**: Define key SLOs (e.g., 99.9% latency under 500ms, 99.95% request success) and alert on burn rate windows instead of raw error counts.
- **Metrics dashboards**: Visualize latency, error budget, rate of 4xx/5xx, idempotency cache hit rate, DB pool saturation, request queue depth, and saturation metrics (CPU/memory).
- **Logging decks**: Include structured logs with `request_id`, severity, and trace context. Maintain log retention rules and centralized aggregation (e.g., Loki, CloudWatch).
- **Tracing + correlation**: Propagate `traceparent` (already documented) through service calls, integrate with distributed tracing backend, and ensure spans include key service/tier metadata.
- **Incident runbooks**: Document playbooks for the top 3 outages (e.g., DB connection exhaustion, cache failover, auth failure), including detection, mitigation, owners, and postmortem expectations.
- **Post-incident hygiene**: Require blameless postmortems, timeline review, root-cause, action items, and update runbooks/SLOs accordingly.

## Security and secret ops

- **Secrets management**: Keep secrets out of source; inject at runtime via vaults/secret managers or env var injection from the orchestrator. Rotate secrets with automation.
- **TLS + certificate lifecycle**: Automate cert issuance/renewal (ACME, vault PKI) and ensure mutual TLS or TLS termination points are documented.
- **Authz/Audit trails**: Log scope/role checks, failed auth attempts, and maintain immutable audit trails compatible with compliance needs.
- **Patch management**: Track OS/package baseline, auto-apply security patches for base images, and rebuild/deploy on critical CVEs.
- **Incident response**: Define who to notify on breaches, escalation paths, and data breach disclosure timelines.

## Support documentation pointers

- Link these operational concerns from `README.md` and other docs so teams know where to look before hitting production.
- Keep the checklist versioned with the codebase; when practices evolve, update this doc alongside CI/CD pipeline/config changes.
