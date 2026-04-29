"""Attack-simulation routes — thin layer over `attack_service`."""
from flask import Blueprint, request, jsonify, g

from config import Config
from backend.utils.auth import auth_required
from backend.services import attack_service
from backend.services.attack_service import AttackError
from backend.extensions import limiter

attack_bp = Blueprint("attack", __name__)


def _err(e):
    if isinstance(e, AttackError):
        return jsonify({"error": str(e)}), e.status
    return jsonify({"error": "Internal error"}), 500


@attack_bp.post("/wrong-key")
@auth_required()
@limiter.limit(lambda: Config.RATE_LIMIT_ATTACK)
def wrong_key():
    try:
        data = request.get_json(force=True, silent=True) or {}
        return jsonify(attack_service.wrong_key_attack(
            g.user, data.get("item_id"), data.get("wrong_key") or "",
        ))
    except AttackError as e:
        return _err(e)


@attack_bp.post("/tamper")
@auth_required()
@limiter.limit(lambda: Config.RATE_LIMIT_ATTACK)
def tamper():
    try:
        data = request.get_json(force=True, silent=True) or {}
        return jsonify(attack_service.tamper_attack(
            g.user, data.get("item_id"), data.get("key") or "",
        ))
    except AttackError as e:
        return _err(e)


@attack_bp.post("/unauthorized")
@limiter.limit(lambda: Config.RATE_LIMIT_ATTACK)
def unauthorized():
    return jsonify(attack_service.unauthorized_attack()), 401
