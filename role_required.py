"""
RBAC middleware. Use ON TOP of `auth_required()` to gate a route by role.

    @auth_required()
    @role_required("admin")
    def admin_only(): ...

`auth_required` is kept for token verification; `role_required` is the
explicit role gate so route files read clearly.
"""
from functools import wraps
from flask import g, jsonify

from backend.services import log_service


def role_required(*roles):
    allowed = set(roles)

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = getattr(g, "user", None)
            if not user:
                return jsonify({"error": "Unauthorized"}), 401
            if user.get("role") not in allowed:
                log_service.warn(
                    "forbidden_access",
                    user_id=user["_id"],
                    username=user.get("username"),
                    required_roles=list(allowed),
                )
                return jsonify({"error": "Forbidden"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
