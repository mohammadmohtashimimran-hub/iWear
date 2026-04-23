"""PaymentType, Payment, VoucherType, ChartOfAccount, Voucher, VoucherEntry, JournalEntry,
   ExpenseCategory, Expense, PurchaseOrder, PurchaseOrderItem, SupplierPayment,
   SalesTransaction, TaxRecord."""
from datetime import datetime, date

from app.extensions import db


class PaymentType(db.Model):
    __tablename__ = "payment_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)

    payments = db.relationship("Payment", back_populates="payment_type", lazy="dynamic")
    supplier_payments = db.relationship(
        "SupplierPayment",
        back_populates="payment_type",
        lazy="dynamic",
        foreign_keys="SupplierPayment.payment_type_id",
    )


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id", ondelete="SET NULL"))
    payment_type_id = db.Column(
        db.Integer,
        db.ForeignKey("payment_types.id", ondelete="RESTRICT"),
        nullable=False,
    )
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_reference = db.Column(db.String(128))
    status = db.Column(db.String(32), nullable=False)
    paid_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship("Order", back_populates="payments")
    payment_type = db.relationship("PaymentType", back_populates="payments")


class VoucherType(db.Model):
    __tablename__ = "voucher_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)

    vouchers = db.relationship("Voucher", back_populates="voucher_type", lazy="dynamic")


class ChartOfAccount(db.Model):
    __tablename__ = "chart_of_accounts"

    id = db.Column(db.Integer, primary_key=True)
    account_code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    account_name = db.Column(db.String(255), nullable=False)
    account_type = db.Column(db.String(32), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("chart_of_accounts.id", ondelete="SET NULL"))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    parent = db.relationship("ChartOfAccount", remote_side="ChartOfAccount.id")
    voucher_entries = db.relationship("VoucherEntry", back_populates="chart_of_account", lazy="dynamic")


class Voucher(db.Model):
    __tablename__ = "vouchers"

    id = db.Column(db.Integer, primary_key=True)
    voucher_type_id = db.Column(
        db.Integer,
        db.ForeignKey("voucher_types.id", ondelete="RESTRICT"),
        nullable=False,
    )
    voucher_number = db.Column(db.String(64), unique=True, nullable=False, index=True)
    reference_type = db.Column(db.String(64))
    reference_id = db.Column(db.Integer)
    voucher_date = db.Column(db.Date, nullable=False)
    narration = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    voucher_type = db.relationship("VoucherType", back_populates="vouchers")
    voucher_entries = db.relationship(
        "VoucherEntry",
        back_populates="voucher",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    journal_entries = db.relationship("JournalEntry", back_populates="voucher", lazy="dynamic")


class VoucherEntry(db.Model):
    __tablename__ = "voucher_entries"

    id = db.Column(db.Integer, primary_key=True)
    voucher_id = db.Column(db.Integer, db.ForeignKey("vouchers.id", ondelete="CASCADE"), nullable=False)
    chart_of_account_id = db.Column(
        db.Integer,
        db.ForeignKey("chart_of_accounts.id", ondelete="RESTRICT"),
        nullable=False,
    )
    debit = db.Column(db.Numeric(14, 2), default=0)
    credit = db.Column(db.Numeric(14, 2), default=0)
    line_description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    voucher = db.relationship("Voucher", back_populates="voucher_entries")
    chart_of_account = db.relationship("ChartOfAccount", back_populates="voucher_entries")


class JournalEntry(db.Model):
    __tablename__ = "journal_entries"

    id = db.Column(db.Integer, primary_key=True)
    voucher_id = db.Column(db.Integer, db.ForeignKey("vouchers.id", ondelete="CASCADE"), nullable=False)
    posting_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    voucher = db.relationship("Voucher", back_populates="journal_entries")


class ExpenseCategory(db.Model):
    __tablename__ = "expense_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)

    expenses = db.relationship("Expense", back_populates="expense_category", lazy="dynamic")


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    expense_category_id = db.Column(
        db.Integer,
        db.ForeignKey("expense_categories.id", ondelete="RESTRICT"),
        nullable=False,
    )
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    description = db.Column(db.Text)
    expense_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    expense_category = db.relationship("ExpenseCategory", back_populates="expenses")


class PurchaseOrder(db.Model):
    __tablename__ = "purchase_orders"

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id", ondelete="SET NULL"))
    po_number = db.Column(db.String(64), unique=True, nullable=False, index=True)
    status = db.Column(db.String(32), nullable=False)
    total_amount = db.Column(db.Numeric(14, 2), default=0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier = db.relationship(
        "Supplier",
        backref=db.backref("purchase_orders", lazy="dynamic"),
    )
    warehouse = db.relationship(
        "Warehouse",
        backref=db.backref("purchase_orders", lazy="dynamic"),
    )
    purchase_order_items = db.relationship(
        "PurchaseOrderItem",
        back_populates="purchase_order",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )


class PurchaseOrderItem(db.Model):
    __tablename__ = "purchase_order_items"

    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(
        db.Integer,
        db.ForeignKey("purchase_orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_variant_id = db.Column(
        db.Integer,
        db.ForeignKey("product_variants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Numeric(10, 2), nullable=False)
    line_total = db.Column(db.Numeric(12, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    purchase_order = db.relationship("PurchaseOrder", back_populates="purchase_order_items")
    product_variant = db.relationship("ProductVariant", back_populates="purchase_order_items")


class SupplierPayment(db.Model):
    __tablename__ = "supplier_payments"

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False)
    payment_type_id = db.Column(db.Integer, db.ForeignKey("payment_types.id", ondelete="SET NULL"))
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    reference = db.Column(db.String(128))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    supplier = db.relationship(
        "Supplier",
        backref=db.backref("supplier_payments", lazy="dynamic"),
    )
    payment_type = db.relationship(
        "PaymentType",
        back_populates="supplier_payments",
        foreign_keys="SupplierPayment.payment_type_id",
    )


class SalesTransaction(db.Model):
    __tablename__ = "sales_transactions"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id", ondelete="RESTRICT"), nullable=False)
    transaction_date = db.Column(db.DateTime, nullable=False)
    gross_amount = db.Column(db.Numeric(12, 2), nullable=False)
    discount_amount = db.Column(db.Numeric(12, 2), default=0)
    tax_amount = db.Column(db.Numeric(12, 2), default=0)
    net_amount = db.Column(db.Numeric(12, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship("Order", back_populates="sales_transactions")


class TaxRecord(db.Model):
    __tablename__ = "tax_records"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    rate_percent = db.Column(db.Numeric(6, 2), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
