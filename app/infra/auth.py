from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Optional

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError

from app.config import settings
from app.domain import errors

bearer = HTTPBearer(auto_error=False)

@dataclass(frozen=True)
class Principal:
    subject: str
    scopes: set[str]

def decode_token(token: str) -> Principal:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )
        sub = payload.get("sub")
        scopes = set(payload.get("scopes", []))
        if not sub:
            raise ValueError("missing sub")
        return Principal(subject=sub, scopes=scopes)
    except (JWTError, ValueError) as e:
        raise e

def get_principal(
    request: Request, creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer)
) -> Principal:
    rid = getattr(request.state, "request_id", "unknown")
    if not creds:
        raise errors.unauthorized("missing bearer token", rid)
    try:
        return decode_token(creds.credentials)
    except Exception:
        raise errors.unauthorized("invalid token", rid)

def require_scopes(*required: str):
    required_set = set(required)

    def _dep(principal: Principal = Depends(get_principal), request: Request = None) -> Principal:
        # request is injected by FastAPI if included; tolerate None for tests
        rid = getattr(getattr(request, "state", None), "request_id", "unknown")
        if not required_set.issubset(principal.scopes):
            raise errors.forbidden("insufficient scope", rid)
        return principal

    return _dep
