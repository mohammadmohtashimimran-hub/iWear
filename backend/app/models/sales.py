"""Customer, CustomerAddress, Cart, CartItem, OrderStatus, Order, OrderItem, Return, ReturnItem."""
from datetime import datetime

from app.extensions import db


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128))
    phone = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    addresses = db.relationship(
        "CustomerAddress",
        back_populates="customer",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    carts = db.relationship("Cart", back_populates="customer", lazy="dynamic")
    orders = db.relationship("Order", back_populates="customer", lazy="dynamic")
    prescription_records = db.relationship(
        "PrescriptionRecord",
        back_populates="customer",
        lazy="dynamic",
        foreign_keys="PrescriptionRecord.customer_id",
    )


class CustomerAddress(db.Model):
    __tablename__ = "customer_addresses"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    address_line_1 = db.Column(db.String(255), nullable=False)
    address_line_2 = db.Column(db.String(255))
    city = db.Column(db.String(128), nullable=False)
    state = db.Column(db.String(64))
    postal_code = db.Column(db.String(32))
    country = db.Column(db.String(64))
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    customer = db.relationship("Customer", back_populates="addresses")


class Cart(db.Model):
    __tablename__ = "carts"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="SET NULL"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), index=True)
    status = db.Column(db.String(32), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = db.relationship("Customer", back_populates="carts")
    user = db.relationship("User", backref=db.backref("carts", lazy="dynamic"))
    cart_items = db.relationship(
        "CartItem",
        back_populates="cart",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )


class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
    product_variant_id = db.Column(
        db.Integer,
        db.ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=False,
    )
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cart = db.relationship("Cart", back_populates="cart_items")
    product_variant = db.relationship("ProductVariant", back_populates="cart_items")
    item_addons = db.relationship(
        "CartItemAddon",
        back_populates="cart_item",
        lazy="joined",
        cascade="all, delete-orphan",
    )


class CartItemAddon(db.Model):
    __tablename__ = "cart_item_addons"

    id = db.Column(db.Integer, primary_key=True)
    cart_item_id = db.Column(db.Integer, db.ForeignKey("cart_items.id", ondelete="CASCADE"), nullable=False)
    addon_option_id = db.Column(db.Integer, db.ForeignKey("addon_options.id", ondelete="CASCADE"), nullable=False)
    image_url = db.Column(db.String(512))

    cart_item = db.relationship("CartItem", back_populates="item_addons")
    addon_option = db.relationship("AddonOption")


class OrderStatus(db.Model):
    __tablename__ = "order_statuses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)

    orders = db.relationship("Order", back_populates="status")


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), index=True)
    status_id = db.Column(db.Integer, db.ForeignKey("order_statuses.id", ondelete="RESTRICT"), nullable=False)
    order_number = db.Column(db.String(64), unique=True, nullable=False, index=True)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)
    discount_total = db.Column(db.Numeric(12, 2), default=0)
    tax_total = db.Column(db.Numeric(12, 2), default=0)
    grand_total = db.Column(db.Numeric(12, 2), nullable=False)
    shipping_address = db.Column(db.String(512))
    shipping_country_id = db.Column(db.Integer, db.ForeignKey("countries.id", ondelete="SET NULL"))
    shipping_city_id = db.Column(db.Integer, db.ForeignKey("cities.id", ondelete="SET NULL"))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = db.relationship("Customer", back_populates="orders")
    shipping_country = db.relationship("Country", foreign_keys=[shipping_country_id])
    shipping_city = db.relationship("City", foreign_keys=[shipping_city_id])
    user = db.relationship("User", backref=db.backref("orders", lazy="dynamic"))
    status = db.relationship("OrderStatus", back_populates="orders")
    order_items = db.relationship(
        "OrderItem",
        back_populates="order",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    returns = db.relationship("Return", back_populates="order", lazy="dynamic")
    payments = db.relationship("Payment", back_populates="order", lazy="dynamic")
    sales_transactions = db.relationship("SalesTransaction", back_populates="order", lazy="dynamic")


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_variant_id = db.Column(
        db.Integer,
        db.ForeignKey("product_variants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    discount_amount = db.Column(db.Numeric(10, 2), default=0)
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    line_total = db.Column(db.Numeric(12, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship("Order", back_populates="order_items")
    return_items = db.relationship("ReturnItem", back_populates="order_item", lazy="dynamic")


class Return(db.Model):
    __tablename__ = "returns"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    return_number = db.Column(db.String(64), unique=True, nullable=False, index=True)
    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship("Order", back_populates="returns")
    return_items = db.relationship(
        "ReturnItem",
        back_populates="return_",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )


class ReturnItem(db.Model):
    __tablename__ = "return_items"

    id = db.Column(db.Integer, primary_key=True)
    return_id = db.Column(db.Integer, db.ForeignKey("returns.id", ondelete="CASCADE"), nullable=False)
    order_item_id = db.Column(db.Integer, db.ForeignKey("order_items.id", ondelete="RESTRICT"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    return_ = db.relationship("Return", back_populates="return_items")
    order_item = db.relationship("OrderItem", back_populates="return_items")
