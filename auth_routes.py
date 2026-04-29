"""
Auth routes — request/response only. Business logic lives in
backend/services/auth_service.py.
"""
from flask import Blueprint, request, jsonify

from config import Config
from backend.services.auth_service import register_user, login_user, AuthError
from backend.utils.validators import ValidationError
from backend.utils.auth import _client_ip
from backend.extensions import limiter

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
@limiter.limit(lambda: Config.RATE_LIMIT_AUTH)
def register():
    try:
        data = request.get_json(force=True, silent=True) or {}
        return jsonify(register_user(data))
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except AuthError as e:
        return jsonify({"error": str(e), **e.extra}), e.status


@auth_bp.post("/login")
@limiter.limit(lambda: Config.RATE_LIMIT_AUTH)
def login():
    try:
        data = request.get_json(force=True, silent=True) or {}
        return jsonify(login_user(data, ip=_client_ip()))
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except AuthError as e:
        return jsonify({"error": str(e), **e.extra}), e.status
