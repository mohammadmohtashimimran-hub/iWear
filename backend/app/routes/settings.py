"""Store settings API — GET/PUT for vendor config (no auth required for GET)."""
from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import StoreSetting, Country, City
from app.auth.decorators import require_permission
from flask_jwt_extended import jwt_required

settings_bp = Blueprint("settings", __name__, url_prefix="/api/settings")


def _settings_to_dict():
    rows = StoreSetting.query.all()
    return {r.key: r.value for r in rows}


@settings_bp.get("/")
def get_settings():
    """GET /api/settings — return all store settings as key-value (for frontend/vendor)."""
    return jsonify(_settings_to_dict())


@settings_bp.put("/")
def update_settings():
    """PUT /api/settings — update settings from JSON body { key: value, ... }. Creates or updates."""
    if not request.is_json:
        return jsonify({"error": "JSON required"}), 400
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "Object required"}), 400
    for key, value in data.items():
        if not key or len(key) > 128:
            continue
        row = StoreSetting.query.filter_by(key=key).first()
        str_val = str(value) if value is not None else None
        if row:
            row.value = str_val
        else:
            db.session.add(StoreSetting(key=key, value=str_val))
    db.session.commit()
    return jsonify(_settings_to_dict())


# ---- Countries & Cities (public read, admin write) ----

@settings_bp.get("/countries")
def list_countries():
    countries = Country.query.order_by(Country.name).all()
    return jsonify([{"id": c.id, "name": c.name} for c in countries])


@settings_bp.post("/countries")
@jwt_required()
@require_permission("inventory:write")
def create_country():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name required"}), 400
    if Country.query.filter(Country.name.ilike(name)).first():
        return jsonify({"error": "Country already exists"}), 409
    c = Country(name=name)
    db.session.add(c)
    db.session.commit()
    return jsonify({"id": c.id, "name": c.name}), 201


@settings_bp.patch("/countries/<int:cid>")
@jwt_required()
@require_permission("inventory:write")
def update_country(cid):
    c = Country.query.get_or_404(cid)
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if name:
        c.name = name
    db.session.commit()
    return jsonify({"id": c.id, "name": c.name})


@settings_bp.delete("/countries/<int:cid>")
@jwt_required()
@require_permission("inventory:write")
def delete_country(cid):
    c = Country.query.get_or_404(cid)
    db.session.delete(c)
    db.session.commit()
    return "", 204


@settings_bp.get("/cities")
def list_cities():
    country_id = request.args.get("country_id", type=int)
    q = City.query
    if country_id is not None:
        q = q.filter_by(country_id=country_id)
    cities = q.order_by(City.name).all()
    return jsonify([{"id": c.id, "name": c.name, "country_id": c.country_id} for c in cities])


@settings_bp.post("/cities")
@jwt_required()
@require_permission("inventory:write")
def create_city():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    country_id = data.get("country_id")
    if not name or not country_id:
        return jsonify({"error": "name and country_id required"}), 400
    Country.query.get_or_404(int(country_id))
    c = City(name=name, country_id=int(country_id))
    db.session.add(c)
    db.session.commit()
    return jsonify({"id": c.id, "name": c.name, "country_id": c.country_id}), 201


@settings_bp.patch("/cities/<int:cid>")
@jwt_required()
@require_permission("inventory:write")
def update_city(cid):
    c = City.query.get_or_404(cid)
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if name:
        c.name = name
    if "country_id" in data:
        Country.query.get_or_404(int(data["country_id"]))
        c.country_id = int(data["country_id"])
    db.session.commit()
    return jsonify({"id": c.id, "name": c.name, "country_id": c.country_id})


@settings_bp.delete("/cities/<int:cid>")
@jwt_required()
@require_permission("inventory:write")
def delete_city(cid):
    c = City.query.get_or_404(cid)
    db.session.delete(c)
    db.session.commit()
    return "", 204
