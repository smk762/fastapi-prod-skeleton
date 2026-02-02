from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class AppError(Exception):
    code: str
    message: str
    http_status: int = 400
    request_id: str = "unknown"

def with_request_id(err: AppError, request_id: str) -> AppError:
    err.request_id = request_id
    return err

# Common constructors
def not_found(msg: str, request_id: str) -> AppError:
    return AppError(code="NOT_FOUND", message=msg, http_status=404, request_id=request_id)

def conflict(msg: str, request_id: str) -> AppError:
    return AppError(code="CONFLICT", message=msg, http_status=409, request_id=request_id)

def forbidden(msg: str, request_id: str) -> AppError:
    return AppError(code="FORBIDDEN", message=msg, http_status=403, request_id=request_id)

def unauthorized(msg: str, request_id: str) -> AppError:
    return AppError(code="UNAUTHORIZED", message=msg, http_status=401, request_id=request_id)

def invalid_argument(msg: str, request_id: str) -> AppError:
    return AppError(code="INVALID_ARGUMENT", message=msg, http_status=400, request_id=request_id)
