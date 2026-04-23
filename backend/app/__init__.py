"""App factory."""
import logging
import os
import sys
from flask import Flask, send_from_directory

from app.config import Config
from app.extensions import bcrypt, cors, db, jwt, migrate
from app import models  # noqa: F401 — register models with db for Flask-Migrate
from app.routes.health import health_bp
from app.routes.auth import auth_bp
from app.routes.inventory import inventory_bp
from app.routes.sales import sales_bp
from app.routes.finance import finance_bp
from app.routes.ai_assistant import ai_assistant_bp
from app.routes.settings import settings_bp


def create_app(config_object=Config):
    """Create and configure the Flask app."""
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Structured logging — single stream handler with consistent format.
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    if not app.logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        ))
        app.logger.addHandler(handler)
    app.logger.setLevel(getattr(logging, log_level, logging.INFO))
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

    # JWT: identity = user id; load User for get_current_user()
    from flask_jwt_extended import get_current_user as _get_current_user

    @jwt.user_lookup_loader
    def _user_lookup(jwt_header, jwt_data):
        from app.models import User
        identity = jwt_data.get("sub")
        if identity is not None:
            try:
                return User.query.get(int(identity))
            except (TypeError, ValueError):
                return None
        return None

    # Blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(ai_assistant_bp)
    app.register_blueprint(settings_bp)

    # Serve uploaded files (product images, etc.)
    _uploads_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))

    @app.route("/uploads/<path:filename>")
    def _serve_uploads(filename):
        return send_from_directory(_uploads_path, filename)

    # Serve built React SPA when frontend_dist exists (Docker / production)
    _frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend_dist")
    if os.path.isdir(_frontend_path):
        _assets_path = os.path.join(_frontend_path, "assets")

        @app.route("/")
        def _serve_index():
            return send_from_directory(_frontend_path, "index.html")

        @app.route("/assets/<path:filename>")
        def _serve_assets(filename):
            return send_from_directory(_assets_path, filename)

        @app.errorhandler(404)
        def _serve_spa_on_404(e):
            from flask import request
            if request.path.startswith("/api"):
                return e
            return send_from_directory(_frontend_path, "index.html")

    from app.seed import register_commands
    register_commands(app)

    return app
