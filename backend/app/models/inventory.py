"""Supplier, Warehouse, ProductVariant, ProductImage, StockMovement, StockAdjustment, InventoryValuation."""
from datetime import datetime

from app.extensions import db


class Supplier(db.Model):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(64))
    email = db.Column(db.String(255))
    address = db.Column(db.Text)
    city = db.Column(db.String(128))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # purchase_orders, supplier_payments set via backref from finance.PurchaseOrder, finance.SupplierPayment


class Warehouse(db.Model):
    __tablename__ = "warehouses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    location = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    stock_movements = db.relationship("StockMovement", back_populates="warehouse", lazy="dynamic")
    stock_adjustments = db.relationship("StockAdjustment", back_populates="warehouse", lazy="dynamic")
    inventory_valuations = db.relationship("InventoryValuation", back_populates="warehouse", lazy="dynamic")
    # purchase_orders set via backref from finance.PurchaseOrder


class ProductVariant(db.Model):
    __tablename__ = "product_variants"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    sku = db.Column(db.String(64), unique=True, nullable=False, index=True)
    barcode = db.Column(db.String(64), index=True)
    color = db.Column(db.String(64))
    size = db.Column(db.String(32))
    unit_price = db.Column(db.Numeric(10, 2))
    unit_price_pkr = db.Column(db.Numeric(12, 2))
    low_stock_threshold = db.Column(db.Integer)  # alert when stock below this (per warehouse/variant)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = db.relationship("Product", back_populates="product_variants")
    cart_items = db.relationship("CartItem", back_populates="product_variant", lazy="dynamic")
    stock_movements = db.relationship("StockMovement", back_populates="product_variant", lazy="dynamic")
    stock_adjustments = db.relationship("StockAdjustment", back_populates="product_variant", lazy="dynamic")
    inventory_valuations = db.relationship("InventoryValuation", back_populates="product_variant", lazy="dynamic")
    purchase_order_items = db.relationship(
        "PurchaseOrderItem",
        back_populates="product_variant",
        lazy="dynamic",
    )


class ProductImage(db.Model):
    __tablename__ = "product_images"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    image_url = db.Column(db.String(512), nullable=False)
    alt_text = db.Column(db.String(255))
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product", back_populates="product_images")


class StockMovement(db.Model):
    __tablename__ = "stock_movements"

    id = db.Column(db.Integer, primary_key=True)
    product_variant_id = db.Column(
        db.Integer,
        db.ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=False,
    )
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False)
    movement_type = db.Column(db.String(32), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    reference_type = db.Column(db.String(64))
    reference_id = db.Column(db.Integer)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product_variant = db.relationship("ProductVariant", back_populates="stock_movements")
    warehouse = db.relationship("Warehouse", back_populates="stock_movements")


class StockAdjustment(db.Model):
    __tablename__ = "stock_adjustments"

    id = db.Column(db.Integer, primary_key=True)
    product_variant_id = db.Column(
        db.Integer,
        db.ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=False,
    )
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False)
    adjustment_type = db.Column(db.String(32), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product_variant = db.relationship("ProductVariant", back_populates="stock_adjustments")
    warehouse = db.relationship("Warehouse", back_populates="stock_adjustments")


class InventoryValuation(db.Model):
    __tablename__ = "inventory_valuation"

    id = db.Column(db.Integer, primary_key=True)
    product_variant_id = db.Column(
        db.Integer,
        db.ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=False,
    )
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False)
    quantity_on_hand = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Numeric(12, 4), nullable=False)
    total_value = db.Column(db.Numeric(14, 2), nullable=False)
    valuation_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product_variant = db.relationship("ProductVariant", back_populates="inventory_valuations")
    warehouse = db.relationship("Warehouse", back_populates="inventory_valuations")
