from __future__ import annotations
import base64
import json
import time
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from jose import jwt

client = TestClient(app)

def make_token(sub="user1", scopes=("items:read","items:write")) -> str:
    payload = {
        "sub": sub,
        "scopes": list(scopes),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "exp": int(time.time()) + 3600,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def auth_headers(scopes=("items:read","items:write")):
    return {"Authorization": f"Bearer {make_token(scopes=scopes)}"}

def test_create_requires_idempotency_key():
    r = client.post("/v1/items", json={"name":"a"}, headers=auth_headers())
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "INVALID_ARGUMENT"

def test_idempotent_create_replays_same_response():
    h = auth_headers()
    h["Idempotency-Key"] = "abc123"

    r1 = client.post("/v1/items", json={"name":"a"}, headers=h)
    assert r1.status_code == 201
    r2 = client.post("/v1/items", json={"name":"a"}, headers=h)
    assert r2.status_code == 201
    assert r1.json()["id"] == r2.json()["id"]

def test_cursor_pagination_is_opaque():
    h = auth_headers(scopes=("items:read","items:write"))
    for i in range(3):
        hh = dict(h)
        hh["Idempotency-Key"] = f"k{i}"
        client.post("/v1/items", json={"name":f"n{i}"}, headers=hh)

    r = client.get("/v1/items?limit=2", headers=auth_headers(scopes=("items:read",)))
    assert r.status_code == 200
    body = r.json()
    assert "next_cursor" in body
    if body["next_cursor"]:
        # Ensure it's urlsafe base64-ish and not raw JSON
        assert "{" not in body["next_cursor"]
