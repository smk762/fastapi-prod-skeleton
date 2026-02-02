from __future__ import annotations
from typing import Generator
from fastapi import Request
from sqlalchemy.orm import Session

from app.infra.db import SessionLocal

def db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")
