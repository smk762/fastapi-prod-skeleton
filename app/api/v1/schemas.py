from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class ErrorEnvelope(BaseModel):
    error: dict = Field(..., examples=[{
        "code": "INVALID_ARGUMENT",
        "message": "email is required",
        "request_id": "req_abc123",
    }])

class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200, examples=["widget"])

class ItemUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=200, examples=["widget v2"])

class ItemOut(BaseModel):
    id: int
    name: str
    created_at: datetime

class ItemListOut(BaseModel):
    items: List[ItemOut]
    next_cursor: Optional[str] = Field(
        default=None,
        description="Opaque cursor for next page (or null).",
        examples=["eyJjcmVhdGVkX2F0IjoiMjAyNi0wMi0wMlQxMDowMDowMFoiLCJpZCI6MTIzfQ"],
    )
