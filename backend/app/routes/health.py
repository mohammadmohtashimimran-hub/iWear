"""Health check endpoint."""
from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.get("/health")
def health():
    """GET /api/health — liveness/readiness check."""
    return jsonify({"status": "ok"})
