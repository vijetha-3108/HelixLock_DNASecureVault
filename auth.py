import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g

from config import Config
from backend.database.db import find_user_by_id, add_log


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def create_token(user):
    payload = {
        "sub": user["_id"],
        "username": user["username"],
        "role": user.get("role", "user"),
        "exp": datetime.utcnow() + timedelta(hours=Config.JWT_EXP_HOURS),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")


def decode_token(token):
    return jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])


def _extract_token():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth.split(" ", 1)[1].strip()
    return request.headers.get("X-Auth-Token")


def _client_ip():
    fwd = request.headers.get("X-Forwarded-For", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.remote_addr or "unknown"


def auth_required(role=None):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            token = _extract_token()
            if not token:
                add_log({
                    "event": "unauthorized_access",
                    "severity": "warning",
                    "path": request.path,
                    "ip": _client_ip(),
                    "ua": request.headers.get("User-Agent", ""),
                })
                return jsonify({"error": "Missing token"}), 401
            try:
                payload = decode_token(token)
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except Exception:
                add_log({
                    "event": "invalid_token",
                    "severity": "warning",
                    "path": request.path,
                    "ip": _client_ip(),
                })
                return jsonify({"error": "Invalid token"}), 401

            user = find_user_by_id(payload["sub"])
            if not user:
                return jsonify({"error": "User not found"}), 401
            if role and user.get("role") != role:
                add_log({
                    "event": "forbidden_access",
                    "severity": "warning",
                    "user_id": user["_id"],
                    "username": user.get("username"),
                    "required_role": role,
                    "path": request.path,
                    "ip": _client_ip(),
                })
                return jsonify({"error": "Forbidden"}), 403

            g.user = user
            return fn(*args, **kwargs)
        return wrapper
    return deco
