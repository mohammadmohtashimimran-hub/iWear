"""AI Business Insights Assistant — natural language query -> intent -> predefined SQL -> response."""
from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import ReportingIntent, AssistantQueryLog
from app.auth.decorators import require_permission
from app.services.ai_assistant_service import (
    detect_intent,
    run_predefined_query,
    format_response,
    get_no_match_response,
    _detect_general_chat,
)
from flask_jwt_extended import jwt_required, get_current_user

ai_assistant_bp = Blueprint("ai_assistant", __name__, url_prefix="/api/ai-assistant")


@ai_assistant_bp.post("/query")
@jwt_required()
@require_permission("ai:query")
def query():
    """POST { "query": "natural language" } -> { "intent", "summary", "table", "status" }."""
    data = request.get_json() or {}
    raw_query = (data.get("query") or "").strip()
    if not raw_query:
        return jsonify({"error": "query required"}), 400

    user = get_current_user()
    user_id = user.id if user else None

    # 1. Check for general chat (greetings, thanks, help) — no DB query needed.
    chat_response = _detect_general_chat(raw_query)
    if chat_response:
        db.session.add(AssistantQueryLog(
            user_id=user_id,
            raw_query=raw_query,
            interpreted_intent_id=None,
            response_status="chat",
        ))
        db.session.commit()
        return jsonify(chat_response)

    # 2. Detect reporting intent via TF-IDF (with keyword fallback).
    intent = detect_intent(raw_query)
    interpreted_id = intent.id if intent else None
    status = "ok" if intent else "no_intent"

    if intent:
        rows, columns = run_predefined_query(intent.id)
        summary, table = format_response(rows, columns, intent.name, intent.code)
    else:
        summary = get_no_match_response()
        table = []

    db.session.add(AssistantQueryLog(
        user_id=user_id,
        raw_query=raw_query,
        interpreted_intent_id=interpreted_id,
        response_status=status,
    ))
    db.session.commit()
    return jsonify({
        "intent": intent.name if intent else None,
        "summary": summary,
        "table": table,
        "status": status,
    })


@ai_assistant_bp.get("/")
def index():
    return jsonify({"module": "ai_assistant", "endpoints": ["POST /query", "GET /intents", "GET /history"]})


@ai_assistant_bp.get("/intents")
@jwt_required()
@require_permission("ai:query")
def list_intents():
    """List available reporting intents so the UI can show suggestions."""
    intents = ReportingIntent.query.order_by(ReportingIntent.name).all()
    return jsonify([
        {
            "id": i.id,
            "code": i.code,
            "name": i.name,
            "description": getattr(i, "description", None),
            "examples": [k.keyword for k in i.intent_keywords[:5]],
        }
        for i in intents
    ])


@ai_assistant_bp.get("/history")
@jwt_required()
@require_permission("ai:query")
def query_history():
    """Last 20 assistant queries for the current user."""
    user = get_current_user()
    if not user:
        return jsonify([])
    rows = (
        AssistantQueryLog.query.filter_by(user_id=user.id)
        .order_by(AssistantQueryLog.id.desc())
        .limit(20)
        .all()
    )
    return jsonify([
        {
            "id": r.id,
            "raw_query": r.raw_query,
            "intent_id": r.interpreted_intent_id,
            "status": r.response_status,
            "created_at": r.created_at.isoformat() if getattr(r, "created_at", None) else None,
        }
        for r in rows
    ])
