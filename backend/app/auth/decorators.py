"""RBAC: require JWT and optional permission code."""
from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_current_user, verify_jwt_in_request


def require_permission(permission_code):
    """Decorator: verify JWT and that current user has the given permission code."""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user = get_current_user()
            if user is None:
                return jsonify({"error": "User not found"}), 403
            if not user.has_permission(permission_code):
                return jsonify({"error": "Insufficient permission"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper
