"""Vault routes — thin HTTP layer over `vault_service`."""
from flask import Blueprint, request, jsonify, g

from backend.utils.auth import auth_required
from backend.utils.validators import ValidationError
from backend.services import vault_service
from backend.services.vault_service import VaultError

vault_bp = Blueprint("vault", __name__)


def _err(e):
    if isinstance(e, ValidationError):
        return jsonify({"error": str(e)}), 400
    if isinstance(e, VaultError):
        return jsonify({"error": str(e)}), e.status
    return jsonify({"error": "Internal error"}), 500


@vault_bp.post("/items")
@auth_required()
def create_item():
    try:
        data = request.get_json(force=True, silent=True) or {}
        return jsonify({"item": vault_service.create_item(g.user, data)})
    except (ValidationError, VaultError) as e:
        return _err(e)


@vault_bp.get("/items")
@auth_required()
def list_items():
    return jsonify({"items": vault_service.list_items(g.user)})


@vault_bp.post("/items/<item_id>/decrypt")
@auth_required()
def decrypt_item(item_id):
    try:
        data = request.get_json(force=True, silent=True) or {}
        key = data.get("key") or ""
        return jsonify(vault_service.decrypt_item(g.user, item_id, key))
    except (ValidationError, VaultError) as e:
        return _err(e)


@vault_bp.delete("/items/<item_id>")
@auth_required()
def remove_item(item_id):
    try:
        vault_service.remove_item(g.user, item_id)
        return jsonify({"ok": True})
    except (ValidationError, VaultError) as e:
        return _err(e)


@vault_bp.post("/visualize")
@auth_required()
def visualize():
    try:
        data = request.get_json(force=True, silent=True) or {}
        return jsonify(vault_service.visualize(
            data.get("text") or "", data.get("key") or "",
        ))
    except ValidationError as e:
        return _err(e)
