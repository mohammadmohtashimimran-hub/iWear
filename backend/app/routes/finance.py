"""Finance routes — chart of accounts, voucher types, vouchers, trial balance, P&L."""
from datetime import date, datetime
from decimal import Decimal

from flask import Blueprint, jsonify, request
from sqlalchemy import func

from app.extensions import db
from app.models import (
    ChartOfAccount,
    VoucherType,
    Voucher,
    VoucherEntry,
    JournalEntry,
    Order,
    OrderStatus,
    Payment,
)
from app.auth.decorators import require_permission
from app.services.finance_service import create_voucher, post_cod_sale
from flask_jwt_extended import jwt_required

finance_bp = Blueprint("finance", __name__, url_prefix="/api/finance")


@finance_bp.get("/chart-of-accounts")
@jwt_required()
@require_permission("finance:read")
def list_chart_of_accounts():
    accounts = ChartOfAccount.query.filter_by(is_active=True).order_by(ChartOfAccount.account_code).all()
    return jsonify([{
        "id": a.id,
        "account_code": a.account_code,
        "account_name": a.account_name,
        "account_type": a.account_type,
        "parent_id": a.parent_id,
    } for a in accounts])


@finance_bp.post("/chart-of-accounts")
@jwt_required()
@require_permission("finance:post")
def create_chart_account():
    data = request.get_json() or {}
    code = (data.get("account_code") or "").strip()
    name = (data.get("account_name") or "").strip()
    if not code or not name:
        return jsonify({"error": "account_code and account_name required"}), 400
    if ChartOfAccount.query.filter_by(account_code=code).first():
        return jsonify({"error": "account_code already exists"}), 409
    acc = ChartOfAccount(
        account_code=code,
        account_name=name,
        account_type=data.get("account_type", "asset"),
        parent_id=data.get("parent_id"),
        is_active=True,
    )
    db.session.add(acc)
    db.session.commit()
    return jsonify({"id": acc.id, "account_code": acc.account_code}), 201


@finance_bp.get("/voucher-types")
@jwt_required()
@require_permission("finance:read")
def list_voucher_types():
    types = VoucherType.query.all()
    return jsonify([{"id": t.id, "code": t.code, "name": t.name} for t in types])


@finance_bp.post("/vouchers")
@jwt_required()
@require_permission("finance:post")
def create_voucher_route():
    """Create voucher with entries. Body: voucher_type_code, voucher_date, lines[], narration, reference_type, reference_id."""
    data = request.get_json() or {}
    code = (data.get("voucher_type_code") or "").strip()
    voucher_date_str = data.get("voucher_date") or date.today().isoformat()
    lines = data.get("lines") or []
    if not code or not lines:
        return jsonify({"error": "voucher_type_code and lines required"}), 400
    try:
        voucher_date = date.fromisoformat(voucher_date_str)
    except ValueError:
        return jsonify({"error": "Invalid voucher_date"}), 400
    try:
        v = create_voucher(
            code,
            voucher_date,
            lines,
            narration=data.get("narration"),
            reference_type=data.get("reference_type"),
            reference_id=data.get("reference_id"),
        )
        db.session.commit()
        return jsonify({"id": v.id, "voucher_number": v.voucher_number}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@finance_bp.get("/vouchers")
@jwt_required()
@require_permission("finance:read")
def list_vouchers():
    vouchers = Voucher.query.order_by(Voucher.id.desc()).limit(100).all()
    return jsonify([{
        "id": v.id,
        "voucher_number": v.voucher_number,
        "voucher_type": v.voucher_type.code if v.voucher_type else None,
        "voucher_date": v.voucher_date.isoformat() if v.voucher_date else None,
        "narration": v.narration,
    } for v in vouchers])


@finance_bp.get("/trial-balance")
@jwt_required()
@require_permission("finance:read")
def trial_balance():
    """Sum of debit and credit per account (from voucher_entries) up to today."""
    entries = db.session.query(
        VoucherEntry.chart_of_account_id,
        ChartOfAccount.account_code,
        ChartOfAccount.account_name,
        func.sum(VoucherEntry.debit).label("total_dr"),
        func.sum(VoucherEntry.credit).label("total_cr"),
    ).join(ChartOfAccount).group_by(VoucherEntry.chart_of_account_id, ChartOfAccount.account_code, ChartOfAccount.account_name).all()
    out = []
    for row in entries:
        dr = float(row.total_dr or 0)
        cr = float(row.total_cr or 0)
        balance = dr - cr
        if balance != 0:
            out.append({"account_code": row.account_code, "account_name": row.account_name, "debit": dr, "credit": cr, "balance": balance})
    return jsonify({"items": out})


@finance_bp.get("/profit-loss")
@jwt_required()
@require_permission("finance:read")
def profit_loss():
    """Simple P&L: revenue (4xxx) - expenses (5xxx, 6xxx)."""
    rev = db.session.query(func.coalesce(func.sum(VoucherEntry.credit) - func.sum(VoucherEntry.debit), 0)).join(ChartOfAccount).filter(
        ChartOfAccount.account_code.like("4%")
    ).scalar() or 0
    exp = db.session.query(func.coalesce(func.sum(VoucherEntry.debit) - func.sum(VoucherEntry.credit), 0)).join(ChartOfAccount).filter(
        ChartOfAccount.account_code.like("5%") | ChartOfAccount.account_code.like("6%")
    ).scalar() or 0
    return jsonify({"revenue": float(rev), "expenses": float(exp), "net_profit": float(rev) - float(exp)})


@finance_bp.post("/orders/<int:order_id>/confirm-cod")
@jwt_required()
@require_permission("finance:post")
def confirm_order_cod(order_id):
    """Mark order as delivered and post Sales Voucher (DR Cash, CR Revenue)."""
    order = Order.query.get_or_404(order_id)
    payment = Payment.query.filter_by(order_id=order_id).first()
    if not payment:
        return jsonify({"error": "No payment for order"}), 400
    if payment.status == "paid":
        return jsonify({"error": "Already confirmed"}), 400
    amount = float(order.grand_total)
    try:
        post_cod_sale(order_id, amount)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    payment.status = "paid"
    payment.paid_at = datetime.utcnow()
    delivered = OrderStatus.query.filter_by(code="delivered").first()
    if delivered:
        order.status_id = delivered.id
    db.session.commit()
    return jsonify({"message": "COD confirmed, voucher posted"})


@finance_bp.get("/")
def index():
    return jsonify({"module": "finance", "endpoints": ["/chart-of-accounts", "/voucher-types", "/vouchers", "/trial-balance", "/profit-loss"]})
