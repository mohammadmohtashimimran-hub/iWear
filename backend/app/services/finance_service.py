"""Finance: voucher creation, double-entry validation, auto-posting helpers."""
from datetime import date
from decimal import Decimal

from app.extensions import db
from app.models import (
    Voucher,
    VoucherEntry,
    VoucherType,
    ChartOfAccount,
    JournalEntry,
)


def _next_voucher_number(prefix):
    """e.g. prefix SV -> SV-20260227-0001."""
    today = date.today().strftime("%Y%m%d")
    p = prefix + "-" + today + "-"
    last = Voucher.query.filter(Voucher.voucher_number.like(p + "%")).order_by(Voucher.id.desc()).first()
    if not last:
        n = 1
    else:
        try:
            n = int(last.voucher_number.rsplit("-", 1)[-1]) + 1
        except ValueError:
            n = 1
    return p + str(n).zfill(4)


def create_voucher(voucher_type_code, voucher_date, lines, narration=None, reference_type=None, reference_id=None):
    """
    lines: list of { account_code, debit, credit, line_description }
    Total debit must equal total credit.
    """
    vt = VoucherType.query.filter_by(code=voucher_type_code).first()
    if not vt:
        raise ValueError(f"Voucher type {voucher_type_code} not found")
    total_dr = sum(Decimal(str(l.get("debit", 0) or 0)) for l in lines)
    total_cr = sum(Decimal(str(l.get("credit", 0) or 0)) for l in lines)
    if total_dr != total_cr:
        raise ValueError("Total debit must equal total credit")
    voucher_number = _next_voucher_number(voucher_type_code)
    v = Voucher(
        voucher_type_id=vt.id,
        voucher_number=voucher_number,
        voucher_date=voucher_date,
        narration=narration,
        reference_type=reference_type,
        reference_id=reference_id,
    )
    db.session.add(v)
    db.session.flush()
    for line in lines:
        acc = ChartOfAccount.query.filter_by(account_code=line["account_code"], is_active=True).first()
        if not acc:
            raise ValueError(f"Account {line['account_code']} not found")
        db.session.add(VoucherEntry(
            voucher_id=v.id,
            chart_of_account_id=acc.id,
            debit=line.get("debit", 0) or 0,
            credit=line.get("credit", 0) or 0,
            line_description=line.get("line_description"),
        ))
    db.session.add(JournalEntry(voucher_id=v.id, posting_date=voucher_date))
    return v


def post_cod_sale(order_id, amount, voucher_date=None):
    """On COD confirmed: DR Cash 1100, CR Sales 4100."""
    voucher_date = voucher_date or date.today()
    return create_voucher(
        "SV",
        voucher_date,
        [
            {"account_code": "1100", "debit": amount, "credit": 0, "line_description": f"COD order {order_id}"},
            {"account_code": "4100", "debit": 0, "credit": amount, "line_description": f"Sales order {order_id}"},
        ],
        narration=f"COD sale order {order_id}",
        reference_type="order",
        reference_id=order_id,
    )


def post_purchase(supplier_amount, voucher_date=None):
    """DR Inventory 1130, CR Supplier Payables 2100."""
    voucher_date = voucher_date or date.today()
    return create_voucher(
        "PV",
        voucher_date,
        [
            {"account_code": "1130", "debit": supplier_amount, "credit": 0, "line_description": "Purchase"},
            {"account_code": "2100", "debit": 0, "credit": supplier_amount, "line_description": "Supplier"},
        ],
        narration="Purchase from supplier",
    )


def post_expense(account_code, amount, narration_text, voucher_date=None):
    """DR Expense account, CR Cash 1100."""
    voucher_date = voucher_date or date.today()
    return create_voucher(
        "EV",
        voucher_date,
        [
            {"account_code": account_code, "debit": amount, "credit": 0, "line_description": narration_text},
            {"account_code": "1100", "debit": 0, "credit": amount, "line_description": "Cash"},
        ],
        narration=narration_text,
    )


def post_supplier_payment(amount, voucher_date=None):
    """DR Supplier Payables 2100, CR Cash at Bank 1110."""
    voucher_date = voucher_date or date.today()
    return create_voucher(
        "PayV",
        voucher_date,
        [
            {"account_code": "2100", "debit": amount, "credit": 0, "line_description": "Supplier payment"},
            {"account_code": "1110", "debit": 0, "credit": amount, "line_description": "Bank"},
        ],
        narration="Supplier payment",
    )
