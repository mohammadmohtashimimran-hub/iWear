"""DailySalesSummary, MonthlyProfitSummary, InventoryValuationSummary, FinancialReportLog,
   ReportingIntent, IntentKeyword, PredefinedQuery, AssistantQueryLog."""
from datetime import datetime, date

from app.extensions import db


class DailySalesSummary(db.Model):
    __tablename__ = "daily_sales_summary"

    id = db.Column(db.Integer, primary_key=True)
    summary_date = db.Column(db.Date, unique=True, nullable=False)
    gross_sales = db.Column(db.Numeric(14, 2), nullable=False)
    discounts = db.Column(db.Numeric(14, 2), default=0)
    taxes = db.Column(db.Numeric(14, 2), default=0)
    net_sales = db.Column(db.Numeric(14, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class MonthlyProfitSummary(db.Model):
    __tablename__ = "monthly_profit_summary"

    id = db.Column(db.Integer, primary_key=True)
    summary_month = db.Column(db.Integer, nullable=False)
    summary_year = db.Column(db.Integer, nullable=False)
    gross_profit = db.Column(db.Numeric(14, 2), nullable=False)
    net_profit = db.Column(db.Numeric(14, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("summary_month", "summary_year", name="uq_monthly_profit_month_year"),
    )


class InventoryValuationSummary(db.Model):
    __tablename__ = "inventory_valuation_summary"

    id = db.Column(db.Integer, primary_key=True)
    summary_date = db.Column(db.Date, unique=True, nullable=False)
    total_inventory_value = db.Column(db.Numeric(14, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FinancialReportLog(db.Model):
    __tablename__ = "financial_reports_log"

    id = db.Column(db.Integer, primary_key=True)
    report_name = db.Column(db.String(128), nullable=False)
    generated_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    generated_at = db.Column(db.DateTime, nullable=False)
    report_parameters_json = db.Column(db.Text)

    user = db.relationship("User", backref=db.backref("financial_report_logs", lazy="dynamic"))


class ReportingIntent(db.Model):
    __tablename__ = "reporting_intents"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    code = db.Column(db.String(64), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)

    intent_keywords = db.relationship(
        "IntentKeyword",
        back_populates="reporting_intent",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    predefined_queries = db.relationship(
        "PredefinedQuery",
        back_populates="reporting_intent",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    assistant_query_logs = db.relationship(
        "AssistantQueryLog",
        back_populates="interpreted_intent",
        lazy="dynamic",
        foreign_keys="AssistantQueryLog.interpreted_intent_id",
    )


class IntentKeyword(db.Model):
    __tablename__ = "intent_keywords"

    id = db.Column(db.Integer, primary_key=True)
    reporting_intent_id = db.Column(
        db.Integer,
        db.ForeignKey("reporting_intents.id", ondelete="CASCADE"),
        nullable=False,
    )
    keyword = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reporting_intent = db.relationship("ReportingIntent", back_populates="intent_keywords")


class PredefinedQuery(db.Model):
    __tablename__ = "predefined_queries"

    id = db.Column(db.Integer, primary_key=True)
    reporting_intent_id = db.Column(
        db.Integer,
        db.ForeignKey("reporting_intents.id", ondelete="CASCADE"),
        nullable=False,
    )
    query_name = db.Column(db.String(128), nullable=False)
    sql_template = db.Column(db.Text, nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reporting_intent = db.relationship("ReportingIntent", back_populates="predefined_queries")


class AssistantQueryLog(db.Model):
    __tablename__ = "assistant_query_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    raw_query = db.Column(db.Text, nullable=False)
    interpreted_intent_id = db.Column(
        db.Integer,
        db.ForeignKey("reporting_intents.id", ondelete="SET NULL"),
    )
    response_status = db.Column(db.String(32), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("assistant_query_logs", lazy="dynamic"))
    interpreted_intent = db.relationship(
        "ReportingIntent",
        back_populates="assistant_query_logs",
        foreign_keys=[interpreted_intent_id],
    )
