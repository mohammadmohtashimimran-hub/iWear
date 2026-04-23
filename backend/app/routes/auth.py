"""Auth routes — login, register, logout, JWT."""
from datetime import datetime, timedelta
from uuid import uuid4

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_current_user,
    get_jwt,
    jwt_required,
)
from flask_bcrypt import check_password_hash

from app.extensions import db, bcrypt
from app.models import User, Role, Session, AuditLog, Customer, Order
from app.models.users import user_roles

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _audit(user_id, action, entity_type=None, entity_id=None, details=None):
    db.session.add(
        AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type or "",
            entity_id=entity_id,
            details_json=str(details) if details is not None else None,
        )
    )


@auth_bp.post("/login")
def login():
    """POST /api/auth/login — email, password -> JWT access token. Creates session."""
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401
    jti = str(uuid4())
    expires = datetime.utcnow() + timedelta(seconds=current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES", 86400))
    db.session.add(
        Session(
            user_id=user.id,
            token_jti=jti,
            expires_at=expires,
            is_active=True,
        )
    )
    _audit(user.id, "login", "user", user.id)
    db.session.commit()
    token = create_access_token(
        identity=str(user.id),
        additional_claims={"sid": jti},
    )
    return jsonify({"access_token": token, "token_type": "bearer", "user_id": user.id, "email": user.email, "phone": user.phone})


@auth_bp.post("/register")
def register():
    """POST /api/auth/register — create user with email, phone, password."""
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    phone = (data.get("phone") or "").strip()
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    if not phone:
        return jsonify({"error": "Phone number is required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409
    viewer = Role.query.filter_by(name="Viewer").first()
    role_id = [viewer.id] if viewer else []
    user = User(
        email=email,
        phone=phone,
        password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
    )
    db.session.add(user)
    db.session.flush()
    if role_id:
        db.session.execute(user_roles.insert().values(user_id=user.id, role_id=role_id[0]))
    _audit(user.id, "register", "user", user.id)
    db.session.commit()
    return jsonify({"id": user.id, "email": user.email, "phone": user.phone}), 201


@auth_bp.post("/logout")
@jwt_required()
def logout():
    """POST /api/auth/logout — invalidate current token (set session is_active=False)."""
    claims = get_jwt()
    jti = claims.get("sid")
    if jti:
        Session.query.filter_by(token_jti=jti).update({"is_active": False})
        db.session.commit()
    return jsonify({"message": "Logged out"})


@auth_bp.get("/me")
@jwt_required()
def me():
    """GET /api/auth/me — current user info + saved checkout profile."""
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404
    roles = [r.name for r in user.roles]
    result = {"id": user.id, "email": user.email, "phone": user.phone, "roles": roles}

    customer = Customer.query.filter_by(email=user.email).first()
    if customer:
        result["first_name"] = customer.first_name
        result["last_name"] = customer.last_name or ""

    last_order = (
        Order.query
        .filter_by(user_id=user.id)
        .order_by(Order.created_at.desc())
        .first()
    )
    if last_order:
        if not customer:
            c = Customer.query.get(last_order.customer_id)
            if c:
                result["first_name"] = c.first_name
                result["last_name"] = c.last_name or ""
        result["shipping_address"] = last_order.shipping_address or ""
        result["shipping_country_id"] = last_order.shipping_country_id
        result["shipping_city_id"] = last_order.shipping_city_id

    return jsonify(result)


@auth_bp.get("/")
def index():
    """Placeholder: list auth info."""
    return jsonify({"module": "auth", "endpoints": ["POST /login", "POST /register", "POST /logout", "GET /me"]})
