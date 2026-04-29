"""Admin / audit routes."""
from flask import Blueprint, request, jsonify, g

from backend.utils.auth import auth_required
from backend.middleware.role_required import role_required
from backend.services import admin_service, log_service

admin_bp = Blueprint("admin", __name__)


@admin_bp.get("/users")
@auth_required()
@role_required("admin")
def all_users():
    return jsonify({"users": admin_service.all_users()})


@admin_bp.get("/logs")
@auth_required()
@role_required("admin")
def all_logs():
    return jsonify({"logs": admin_service.filtered_logs(
        event=request.args.get("event"),
        severity=request.args.get("severity"),
        q=request.args.get("q") or "",
        limit=int(request.args.get("limit", 500)),
    )})


@admin_bp.get("/stats")
@auth_required()
@role_required("admin")
def stats():
    return jsonify(admin_service.system_stats())


@admin_bp.get("/me/logs")
@auth_required()
def my_logs():
    return jsonify({"logs": log_service.fetch_logs(user_id=g.user["_id"])})
