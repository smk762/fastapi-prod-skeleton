from __future__ import annotations
import base64
import json
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass(frozen=True)
class Cursor:
    created_at: str
    id: int

def encode_cursor(created_at_iso: str, id: int) -> str:
    payload = {"created_at": created_at_iso, "id": id}
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

def decode_cursor(cursor: str) -> Cursor:
    # add padding back
    pad = "=" * (-len(cursor) % 4)
    raw = base64.urlsafe_b64decode((cursor + pad).encode("ascii"))
    payload = json.loads(raw.decode("utf-8"))
    return Cursor(created_at=payload["created_at"], id=int(payload["id"]))
