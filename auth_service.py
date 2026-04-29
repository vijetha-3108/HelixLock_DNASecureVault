"""
Authentication service — pure business logic, no Flask request handling.
Routes call these functions and translate the return values to HTTP.
"""
from __future__ import annotations

from config import Config
from backend.database.db import create_user, find_user_by_username
from backend.utils.auth import hash_password, check_password, create_token
from backend.utils import security, validators
from backend.services import log_service


class AuthError(Exception):
    def __init__(self, message: str, status: int = 400, **extra):
        super().__init__(message)
        self.status = status
        self.extra = extra


def register_user(payload: dict) -> dict:
    username = validators.validate_username(payload.get("username"))
    password = validators.validate_password(payload.get("password"))
    role = validators.validate_role(payload.get("role"))

    if find_user_by_username(username):
        raise AuthError("Username already exists", status=409)

    user = create_user({
        "username": username,
        "password_hash": hash_password(password),
        "role": role,
        "failed_attempts": 0,
        "account_locked": False,
    })
    log_service.info("register", user_id=user["_id"], username=username, role=role)
    token = create_token(user)
    return {
        "token": token,
        "user": {"id": user["_id"], "username": username, "role": role},
    }


def login_user(payload: dict, ip: str) -> dict:
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    locked, retry = security.is_locked(username, ip)
    if locked:
        log_service.critical(
            "login_locked", username=username, retry_after=retry,
        )
        raise AuthError(
            f"Too many failed attempts. Try again in {retry}s.",
            status=429, retry_after=retry,
        )

    user = find_user_by_username(username)
    if not user or not check_password(password, user["password_hash"]):
        attempts = security.record_failure(username, ip)
        remaining = max(Config.LOGIN_MAX_ATTEMPTS - attempts, 0)
        log_service.warn(
            "login_failed", username=username,
            attempt=attempts, remaining=remaining,
        )
        raise AuthError(
            "Invalid credentials", status=401,
            attempts=attempts, remaining=remaining,
        )

    security.reset(username, ip)
    log_service.info(
        "login_success", user_id=user["_id"], username=username,
    )
    token = create_token(user)
    return {
        "token": token,
        "user": {
            "id": user["_id"],
            "username": user["username"],
            "role": user.get("role", "user"),
        },
    }
