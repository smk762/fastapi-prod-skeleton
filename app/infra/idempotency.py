from __future__ import annotations
import hashlib
import json
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.infra.models import IdempotencyRecord

def hash_request(body: dict) -> str:
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def route_key(method: str, path: str) -> str:
    return f"{method.upper()} {path}"

def get_idempotent_response(
    db: Session,
    *,
    principal_id: str,
    route_key_value: str,
    idem_key: str,
    request_hash: str,
):
    rec = (
        db.query(IdempotencyRecord)
        .filter_by(principal_id=principal_id, route_key=route_key_value, idem_key=idem_key)
        .one_or_none()
    )
    if not rec:
        return None
    if rec.request_hash != request_hash:
        # Same key reused with different payload: reject
        return ("IDEMPOTENCY_KEY_REUSED", 409, None)
    return ("REPLAY", rec.status_code, rec.response_body)

def store_idempotent_response(
    db: Session,
    *,
    principal_id: str,
    route_key_value: str,
    idem_key: str,
    request_hash: str,
    status_code: int,
    response_body: dict,
):
    rec = IdempotencyRecord(
        principal_id=principal_id,
        route_key=route_key_value,
        idem_key=idem_key,
        request_hash=request_hash,
        status_code=status_code,
        response_body=json.dumps(response_body, separators=(",", ":")),
    )
    db.add(rec)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Concurrent insert: safe to ignore; next read will replay
