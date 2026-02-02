# FastAPI Production-Grade API Skeleton

A reference FastAPI project skeleton that demonstrates **production-grade API design**:
- `/v1` path versioning
- idempotency keys for `POST` creates
- cursor-based pagination with stable ordering
- consistent error envelope with machine codes + request_id
- structured logging + trace header propagation
- request timeouts + cancellation
- JWT + scopes (example)
- Prometheus metrics

## Quickstart

### Local (venv)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
uvicorn app.main:app --reload
```

### Docker Compose (includes Redis stub for rate limit future)
```bash
docker compose up --build
```

Open:
- API docs: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics

## Key Docs
- `docs/api-design.md`
- `docs/agent-directives.md`
- `docs/cursor-enforcement-rules.md`

## Environment
Copy `.env.example` to `.env` and adjust.

## Notes
This repo uses SQLite by default for simplicity. Swap to Postgres by changing `DATABASE_URL`.
