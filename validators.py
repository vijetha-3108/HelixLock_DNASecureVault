"""
Lightweight input validation helpers.

We intentionally avoid heavy schema libraries to keep the Flask deps minimal.
Each helper raises `ValidationError` which the routes catch and translate
into a clean JSON 400 response.
"""
from __future__ import annotations

import re

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")
ROLES = ("user", "admin")


class ValidationError(ValueError):
    """Raised when user-supplied input fails validation."""


def require_str(value, field: str, *, min_len: int = 1, max_len: int = 1000) -> str:
    if not isinstance(value, str):
        raise ValidationError(f"{field} must be a string")
    v = value.strip()
    if len(v) < min_len:
        raise ValidationError(f"{field} must be at least {min_len} chars")
    if len(v) > max_len:
        raise ValidationError(f"{field} must be at most {max_len} chars")
    return v


def validate_username(value) -> str:
    v = require_str(value, "username", min_len=3, max_len=32)
    if not USERNAME_RE.match(v):
        raise ValidationError("username may only contain letters, digits, '_', '.', '-'")
    return v


def validate_password(value) -> str:
    if not isinstance(value, str) or len(value) < 6:
        raise ValidationError("password must be at least 6 characters")
    if len(value) > 128:
        raise ValidationError("password must be at most 128 characters")
    return value


def validate_role(value) -> str:
    if value is None:
        return "user"
    if value not in ROLES:
        raise ValidationError(f"role must be one of {ROLES}")
    return value
