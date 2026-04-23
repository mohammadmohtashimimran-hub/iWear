"""AI Business Insights Assistant — intent detection unit tests.

These tests focus on the keyword-based detect_intent helper, which is the core
piece of logic for the AI assistant. Routing/auth is exercised in
test_health/test_auth — here we just want fast, deterministic coverage of the
matching algorithm so the report can cite real numbers.
"""
from app.extensions import db
from app.models import ReportingIntent, IntentKeyword, PredefinedQuery
from app.services.ai_assistant_service import (
    detect_intent,
    normalize,
    run_predefined_query,
    format_response,
)


def _seed_two_intents():
    sales = ReportingIntent(name="Test Sales", code="test_sales")
    profit = ReportingIntent(name="Test Profit", code="test_profit")
    db.session.add_all([sales, profit])
    db.session.flush()
    for kw in ("sales today", "today sales", "daily sales"):
        db.session.add(IntentKeyword(reporting_intent_id=sales.id, keyword=kw))
    for kw in ("profit", "monthly profit", "net profit"):
        db.session.add(IntentKeyword(reporting_intent_id=profit.id, keyword=kw))
    db.session.add(PredefinedQuery(
        reporting_intent_id=sales.id,
        query_name="test_sales",
        sql_template="SELECT 1 AS result",
        active=True,
    ))
    db.session.commit()
    return sales, profit


def test_normalize_strips_and_lowercases():
    assert normalize("  HELLO   World ") == "hello world"
    assert normalize(None) == ""
    assert normalize("") == ""


def test_detect_intent_matches_keyword(db):
    sales, profit = _seed_two_intents()
    matched = detect_intent("show me sales today please")
    assert matched is not None
    assert matched.code == "test_sales"


def test_detect_intent_matches_other_intent(db):
    sales, profit = _seed_two_intents()
    matched = detect_intent("what is the monthly profit")
    assert matched is not None
    assert matched.code == "test_profit"


def test_detect_intent_returns_none_for_no_match(db):
    _seed_two_intents()
    assert detect_intent("xyz unrelated text") is None
    assert detect_intent("") is None


def test_run_predefined_query_returns_rows(db):
    sales, _ = _seed_two_intents()
    rows, columns = run_predefined_query(sales.id)
    assert rows is not None
    assert columns == ["result"]
    assert rows[0][0] == 1


def test_format_response_handles_empty_and_data(db):
    summary, table = format_response([], ["x"], "Daily Sales")
    assert "no data" in summary.lower() or "No data" in summary
    assert table == []
    summary, table = format_response([[1]], ["x"], "Daily Sales")
    assert "1" in summary  # mentions the count or value
    assert table == [{"x": 1}]


def test_seeded_intents_all_execute_against_empty_db(db):
    """Run every SQL template from the real seed against an empty SQLite DB.

    The purpose is to catch schema/dialect regressions. Every SELECT should
    return without raising, even if the result set is empty. A regression
    here means one of the SQL templates has drifted away from the real
    schema (e.g. references a column that no longer exists) or uses
    PostgreSQL-only syntax that SQLite cannot parse.
    """
    from app.seed import (
        seed_roles,
        seed_permissions,
        seed_role_permissions,
        seed_order_statuses,
        seed_payment_types,
        seed_voucher_types,
        seed_chart_of_accounts,
        seed_catalog_masters,
        seed_eyewear_masters,
        seed_ai_intents,
    )

    # Seed just enough for the SQL templates to bind without foreign-key panic.
    seed_roles()
    seed_permissions()
    seed_role_permissions()
    seed_order_statuses()
    seed_payment_types()
    seed_voucher_types()
    seed_chart_of_accounts()
    seed_catalog_masters()
    seed_eyewear_masters()
    seed_ai_intents()
    db.session.commit()

    # Every intent should have a predefined query; running it must not raise.
    intents = ReportingIntent.query.order_by(ReportingIntent.id).all()
    assert len(intents) >= 10, "expected at least 10 seeded intents"
    for intent in intents:
        rows, columns = run_predefined_query(intent.id)
        # rows may be [] on an empty DB; we just require it did not raise/swallow.
        assert rows is not None, f"Intent {intent.code!r} failed to execute"
        assert columns, f"Intent {intent.code!r} returned no columns"
