from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import os
import logging

from config import Config
from backend.database.db import init_db
from backend.extensions import limiter
from backend.routes.auth_routes import auth_bp
from backend.routes.vault_routes import vault_bp
from backend.routes.admin_routes import admin_bp
from backend.routes.attack_routes import attack_bp


def create_app(test_config: dict | None = None):
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    app = Flask(__name__, static_folder=frontend_dir, static_url_path="")
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    )

    origins = (
        "*" if Config.CORS_ORIGINS.strip() == "*"
        else [o.strip() for o in Config.CORS_ORIGINS.split(",") if o.strip()]
    )
    CORS(app, resources={r"/api/*": {"origins": origins}})

    init_db(app)
    limiter.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(vault_bp, url_prefix="/api/vault")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(attack_bp, url_prefix="/api/attack")

    # ---------- Friendly global error envelope ----------
    @app.errorhandler(404)
    def not_found(e):
        # Let static/page routes fall through; only wrap API misses.
        from flask import request
        if request.path.startswith("/api/"):
            return jsonify({"error": "Endpoint not found", "path": request.path}), 404
        return e

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            "error": "Rate limit exceeded — please slow down.",
            "detail": str(e.description),
        }), 429

    @app.errorhandler(500)
    def internal(e):
        app.logger.exception("Unhandled error")
        return jsonify({"error": "Something went wrong on the server."}), 500

    # ---------- Static page routes ----------
    @app.route("/")
    def index():
        return send_from_directory(frontend_dir + "/html", "login.html")

    @app.route("/<path:page>.html")
    def html_page(page):
        return send_from_directory(frontend_dir + "/html", f"{page}.html")

    @app.route("/health")
    def health():
        return {"status": "ok", "service": "DNA Secure Vault"}

    return app
