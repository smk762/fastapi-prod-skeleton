from __future__ import annotations
import json
from datetime import datetime

from fastapi import APIRouter, Depends, Header, Request, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import asc, or_, and_

from app.api.v1.schemas import ItemCreate, ItemOut, ItemListOut, ItemUpdate, ErrorEnvelope
from app.domain import errors
from app.infra.deps import db_session, request_id
from app.infra.auth import require_scopes, Principal
from app.infra.models import Item
from app.infra.pagination import decode_cursor, encode_cursor
from app.infra.idempotency import (
    get_idempotent_response,
    store_idempotent_response,
    hash_request,
    route_key,
)

router = APIRouter()

@router.post(
    "",
    response_model=ItemOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorEnvelope},
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        409: {"model": ErrorEnvelope},
        504: {"model": ErrorEnvelope},
    },
    summary="Create item (idempotent with Idempotency-Key)",
)
def create_item(
    payload: ItemCreate,
    request: Request,
    db: Session = Depends(db_session),
    principal: Principal = Depends(require_scopes("items:write")),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    rid = request_id(request)
    if not idempotency_key:
        raise errors.invalid_argument("Idempotency-Key header required for create", rid)

    rk = route_key("POST", "/v1/items")
    req_hash = hash_request(payload.model_dump())

    replay = get_idempotent_response(
        db,
        principal_id=principal.subject,
        route_key_value=rk,
        idem_key=idempotency_key,
        request_hash=req_hash,
    )
    if replay:
        kind, status_code, body = replay
        if kind == "IDEMPOTENCY_KEY_REUSED":
            raise errors.conflict("idempotency key reused with different payload", rid)
        # Replay original response
        return ItemOut.model_validate_json(body)

    item = Item(name=payload.name)
    db.add(item)
    db.commit()
    db.refresh(item)

    out = ItemOut(id=item.id, name=item.name, created_at=item.created_at)
    store_idempotent_response(
        db,
        principal_id=principal.subject,
        route_key_value=rk,
        idem_key=idempotency_key,
        request_hash=req_hash,
        status_code=201,
        response_body=out.model_dump(mode="json"),
    )
    return out

@router.get(
    "",
    response_model=ItemListOut,
    responses={401: {"model": ErrorEnvelope}, 403: {"model": ErrorEnvelope}, 504: {"model": ErrorEnvelope}},
    summary="List items (cursor pagination, stable ordering)",
)
def list_items(
    request: Request,
    db: Session = Depends(db_session),
    principal: Principal = Depends(require_scopes("items:read")),
    limit: int = 25,
    cursor: str | None = None,
):
    limit = max(1, min(limit, 100))

    q = db.query(Item)
    # Stable ordering: created_at ASC, id ASC
    q = q.order_by(asc(Item.created_at), asc(Item.id))

    if cursor:
        c = decode_cursor(cursor)
        # Return items strictly greater than (created_at, id)
        q = q.filter(
            or_(
                Item.created_at > datetime.fromisoformat(c.created_at),
                and_(Item.created_at == datetime.fromisoformat(c.created_at), Item.id > c.id),
            )
        )

    rows = q.limit(limit + 1).all()
    has_more = len(rows) > limit
    rows = rows[:limit]

    next_cursor = None
    if has_more and rows:
        last = rows[-1]
        next_cursor = encode_cursor(last.created_at.isoformat(), last.id)

    return ItemListOut(
        items=[ItemOut(id=r.id, name=r.name, created_at=r.created_at) for r in rows],
        next_cursor=next_cursor,
    )

@router.get(
    "/{item_id}",
    response_model=ItemOut,
    responses={404: {"model": ErrorEnvelope}, 401: {"model": ErrorEnvelope}, 403: {"model": ErrorEnvelope}},
)
def get_item(
    item_id: int,
    request: Request,
    db: Session = Depends(db_session),
    principal: Principal = Depends(require_scopes("items:read")),
):
    rid = request_id(request)
    item = db.query(Item).filter_by(id=item_id).one_or_none()
    if not item:
        raise errors.not_found("item not found", rid)
    return ItemOut(id=item.id, name=item.name, created_at=item.created_at)

@router.put(
    "/{item_id}",
    response_model=ItemOut,
    responses={404: {"model": ErrorEnvelope}, 401: {"model": ErrorEnvelope}, 403: {"model": ErrorEnvelope}},
    summary="Update item (idempotent PUT)",
)
def update_item(
    item_id: int,
    payload: ItemUpdate,
    request: Request,
    db: Session = Depends(db_session),
    principal: Principal = Depends(require_scopes("items:write")),
):
    rid = request_id(request)
    item = db.query(Item).filter_by(id=item_id).one_or_none()
    if not item:
        raise errors.not_found("item not found", rid)
    item.name = payload.name
    db.add(item)
    db.commit()
    db.refresh(item)
    return ItemOut(id=item.id, name=item.name, created_at=item.created_at)

@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={401: {"model": ErrorEnvelope}, 403: {"model": ErrorEnvelope}, 504: {"model": ErrorEnvelope}},
    summary="Delete item (idempotent DELETE)",
)
def delete_item(
    item_id: int,
    request: Request,
    db: Session = Depends(db_session),
    principal: Principal = Depends(require_scopes("items:write")),
):
    item = db.query(Item).filter_by(id=item_id).one_or_none()
    if item:
        db.delete(item)
        db.commit()
    return Response(status_code=204)
