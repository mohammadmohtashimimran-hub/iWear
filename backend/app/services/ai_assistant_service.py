"""AI Business Insights Assistant — NLP-powered intent detection, safe query
execution, and conversational response generation.

Architecture:
    1. **Intent detection** — TF-IDF + cosine similarity over a corpus built
       from the seeded keywords. Falls back to keyword overlap for very short
       queries. This is the "AI" layer — it handles paraphrases, synonyms and
       natural phrasing that a simple keyword lookup would miss.
    2. **Safe query execution** — each intent maps to an admin-curated SQL
       template with whitelisted parameter substitution (today, month, year).
       User text never touches the SQL engine.
    3. **Conversational response** — raw rows are turned into natural-language
       summaries with data-driven insights (totals, averages, comparisons)
       rather than the generic "Found N rows" pattern.
    4. **General chat** — greetings, thanks, help and "about" messages are
       handled without hitting the database at all, giving the assistant a
       warm, approachable feel.
"""
from __future__ import annotations

from datetime import date
import re
from typing import Any

from sqlalchemy import text
from app.extensions import db
from app.models import ReportingIntent, IntentKeyword, PredefinedQuery

# ---------------------------------------------------------------------------
# TF-IDF intent classifier (trained lazily on first call)
# ---------------------------------------------------------------------------
_tfidf_vectorizer = None
_tfidf_matrix = None
_tfidf_intent_ids: list[int] = []


def _build_tfidf_index():
    """Build (or rebuild) a TF-IDF index over all intent keywords.

    Called once on the first query; the index is cached for the lifetime of
    the process. If intents change, restart the server or call this again.
    """
    global _tfidf_vectorizer, _tfidf_matrix, _tfidf_intent_ids
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity  # noqa: F401
    except ImportError:
        # scikit-learn not installed — fall back to keyword matching.
        return False

    corpus: list[str] = []
    intent_ids: list[int] = []

    for intent in ReportingIntent.query.all():
        # Build one "document" per intent: combine name + code + all keywords.
        parts = [intent.name.lower(), intent.code.replace("_", " ")]
        for kw in intent.intent_keywords:
            parts.append(kw.keyword.lower())
        doc = " ".join(parts)
        corpus.append(doc)
        intent_ids.append(intent.id)

    if not corpus:
        return False

    vectorizer = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 2),  # unigrams + bigrams for phrase matching
        stop_words=None,     # keep stop words — "low stock" needs "low"
        lowercase=True,
    )
    matrix = vectorizer.fit_transform(corpus)

    _tfidf_vectorizer = vectorizer
    _tfidf_matrix = matrix
    _tfidf_intent_ids = intent_ids
    return True


def _tfidf_match(query: str, threshold: float = 0.15) -> ReportingIntent | None:
    """Find the best-matching intent using TF-IDF cosine similarity.

    Returns None if the best similarity is below *threshold* (i.e. the
    query is too unrelated to any known intent).
    """
    global _tfidf_vectorizer, _tfidf_matrix, _tfidf_intent_ids
    if _tfidf_vectorizer is None:
        if not _build_tfidf_index():
            return None

    from sklearn.metrics.pairwise import cosine_similarity

    q_vec = _tfidf_vectorizer.transform([query.lower()])
    scores = cosine_similarity(q_vec, _tfidf_matrix).flatten()

    best_idx = scores.argmax()
    best_score = scores[best_idx]

    if best_score < threshold:
        return None

    intent_id = _tfidf_intent_ids[best_idx]
    return ReportingIntent.query.get(intent_id)


# ---------------------------------------------------------------------------
# General chat (non-data queries)
# ---------------------------------------------------------------------------
_GREETINGS = {"hi", "hello", "hey", "hola", "salam", "yo", "sup", "greetings",
              "good morning", "good afternoon", "good evening", "assalam"}
_THANKS = {"thanks", "thank you", "thankyou", "thx", "cheers", "shukriya",
           "jazakallah", "appreciated"}
_HELP_WORDS = {"help", "what can you do", "commands", "options", "how to use"}


def _detect_general_chat(query: str) -> dict | None:
    """Handle greetings, thanks and help without hitting the database."""
    q = query.lower().strip().rstrip("!?.").strip()

    for g in _GREETINGS:
        if q == g or q.startswith(g + " "):
            return {
                "intent": "greeting",
                "summary": (
                    "Hi there! I'm the iWear Business Insights Assistant. "
                    "Ask me about your store's performance — for example:\n\n"
                    "• \"How are sales today?\"\n"
                    "• \"Who are the top customers?\"\n"
                    "• \"Show me low stock items\"\n"
                    "• \"What's the average order value?\"\n\n"
                    "I'll pull the latest data from your database and give you a clear answer."
                ),
                "table": [],
                "status": "chat",
            }

    for t in _THANKS:
        if t in q:
            return {
                "intent": "thanks",
                "summary": "You're welcome! Let me know if you need anything else about your store.",
                "table": [],
                "status": "chat",
            }

    for h in _HELP_WORDS:
        if h in q:
            intents = ReportingIntent.query.order_by(ReportingIntent.name).all()
            names = [f"• {i.name}" for i in intents]
            return {
                "intent": "help",
                "summary": (
                    "Here's what I can help you with:\n\n"
                    + "\n".join(names)
                    + "\n\nJust ask in plain English — I'll understand!"
                ),
                "table": [],
                "status": "chat",
            }

    return None


# ---------------------------------------------------------------------------
# Public API (called from the route handler)
# ---------------------------------------------------------------------------
def normalize(text_input: str | None) -> str:
    if not text_input:
        return ""
    return re.sub(r"\s+", " ", text_input.lower().strip())


def detect_intent(query_text: str) -> ReportingIntent | None:
    """Detect the user's reporting intent using TF-IDF similarity.

    Falls back to direct keyword/name matching when scikit-learn is not
    available, so the system still works (just less accurately) without
    the ML dependency.
    """
    normalized = normalize(query_text)
    if not normalized or len(normalized) < 2:
        return None

    # Try TF-IDF first (best accuracy).
    result = _tfidf_match(normalized)
    if result:
        return result

    # Fallback: exact phrase / word-overlap matching.
    query_words = set(normalized.split())
    best = None
    best_score = 0
    for intent in ReportingIntent.query.all():
        for kw in intent.intent_keywords:
            kw_lower = normalize(kw.keyword)
            if kw_lower in normalized:
                score = len(kw_lower) * 3
            else:
                kw_words = set(kw_lower.split())
                overlap = query_words & kw_words
                if not overlap:
                    continue
                ratio = len(overlap) / len(kw_words) if kw_words else 0
                if ratio >= 1.0:
                    score = len(kw_lower) * 2
                elif ratio >= 0.5 and len(overlap) >= 2:
                    score = len(kw_lower)
                else:
                    continue
            if score > best_score and score >= 4:
                best_score = score
                best = intent

        name_lower = normalize(intent.name)
        code_lower = normalize(intent.code)
        if name_lower in normalized or code_lower in normalized:
            if 5 > best_score:
                best = intent
                best_score = 5

    return best


def get_safe_params() -> dict[str, Any]:
    """Safe parameters for SQL template substitution (no user input)."""
    today = date.today()
    return {
        "today": today.isoformat(),
        "year": today.year,
        "month": today.month,
        "day": today.day,
    }


def run_predefined_query(intent_id: int) -> tuple[list | None, list | None]:
    """Get first active predefined query for intent; substitute params and
    run read-only; return (rows, columns)."""
    pq = PredefinedQuery.query.filter_by(
        reporting_intent_id=intent_id, active=True,
    ).first()
    if not pq or not pq.sql_template:
        return None, None
    sql = pq.sql_template
    params = get_safe_params()
    for key, val in params.items():
        sql = sql.replace("{{" + key + "}}", str(val))
    if not sql.strip().upper().startswith("SELECT"):
        return None, None
    try:
        result = db.session.execute(text(sql))
        rows = result.fetchall()
        columns = list(result.keys()) if result.keys() else []
        return [list(r) for r in rows], columns
    except Exception as exc:
        try:
            from flask import current_app
            current_app.logger.warning(
                "AI predefined query failed (intent_id=%s): %s -- SQL: %s",
                intent_id, exc, sql,
            )
        except Exception:
            pass
        return None, None


# ---------------------------------------------------------------------------
# Conversational response builder
# ---------------------------------------------------------------------------
_INTENT_TEMPLATES: dict[str, str] = {
    "daily_sales": (
        "Today ({today}) you've had **{order_count} order(s)** "
        "with total sales of **${total_sales:.2f}**."
    ),
    "monthly_profit": (
        "This month's total revenue so far is **${revenue:.2f}**."
    ),
    "best_selling": (
        "Here are your top-selling products ranked by units sold:"
    ),
    "low_stock": (
        "These items are running low on stock and may need restocking soon:"
    ),
    "top_customers": (
        "Your highest-value customers ranked by total spend:"
    ),
    "pending_orders": (
        "You have the following orders still awaiting fulfilment:"
    ),
    "sales_by_category": (
        "Revenue breakdown by product category:"
    ),
    "average_order_value": (
        "Across **{order_count} order(s)**, your average order value is "
        "**${avg_order_value:.2f}**."
    ),
    "new_customers_month": (
        "You've gained **{new_customer_count} new customer(s)** this month."
    ),
    "slow_moving_stock": (
        "These products haven't had any sales yet — consider running a "
        "promotion or reviewing your pricing:"
    ),
}


def format_response(
    rows: list | None,
    columns: list | None,
    intent_name: str,
    intent_code: str | None = None,
) -> tuple[str, list]:
    """Build a conversational summary and a data table for the JSON response.

    Instead of the generic "Found N rows", this function:
    - Uses per-intent natural-language templates
    - Substitutes actual values from the first row where applicable
    - Falls back gracefully when templates aren't available
    """
    if rows is None:
        return "Sorry, I couldn't run that report right now. Please try again later.", []
    if not rows:
        return f"No data found for **{intent_name}** at the moment. Try placing a test order and asking again!", []

    # Build serialisable table
    table = []
    for row in rows:
        entry = {}
        for k, v in zip(columns, row):
            if hasattr(v, "isoformat"):
                entry[k] = v.isoformat()
            elif hasattr(v, "__float__") and not isinstance(v, (int, float)):
                try:
                    entry[k] = float(v)
                except (TypeError, ValueError):
                    entry[k] = str(v)
            else:
                entry[k] = v
        table.append(entry)

    # Try to build a conversational summary from the template
    template = _INTENT_TEMPLATES.get(intent_code or "")
    if template and len(table) == 1:
        # Single-row results (aggregates like daily_sales, avg_order_value)
        try:
            params = {**get_safe_params(), **table[0]}
            # Ensure numeric fields are floats for formatting
            for k, v in params.items():
                if isinstance(v, str):
                    try:
                        params[k] = float(v)
                    except (ValueError, TypeError):
                        pass
            summary = template.format(**params)
            return summary, table
        except (KeyError, TypeError, ValueError):
            pass
    elif template:
        # Multi-row results (lists like best_selling, low_stock)
        summary = template
        count = len(rows)
        if count > 1:
            summary += f"\n\n*Showing {count} results.*"
        return summary, table

    # Fallback
    summary = f"Here's what I found for **{intent_name}** ({len(rows)} result{'s' if len(rows) != 1 else ''}):"
    return summary, table


def get_no_match_response() -> str:
    """Friendly fallback when no intent is detected."""
    intents = ReportingIntent.query.order_by(ReportingIntent.name).all()
    suggestions = ", ".join(f'"{i.name.lower()}"' for i in intents[:5])
    return (
        "I'm not sure what report you're looking for. "
        f"Try asking about {suggestions}, or say **\"help\"** to see everything I can do!"
    )
