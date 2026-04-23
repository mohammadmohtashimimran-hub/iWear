"""ProductCategory, ProductBrand, ProductType, Product, Stock — catalog & legacy stock."""
from datetime import datetime

from app.extensions import db


class ProductCategory(db.Model):
    __tablename__ = "product_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)

    products = db.relationship("Product", back_populates="category", lazy="dynamic")
    addons = db.relationship("Addon", back_populates="category", lazy="dynamic", cascade="all, delete-orphan")


class ProductBrand(db.Model):
    __tablename__ = "product_brands"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)

    products = db.relationship("Product", back_populates="brand", lazy="dynamic")


class ProductType(db.Model):
    __tablename__ = "product_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)

    products = db.relationship("Product", back_populates="product_type", lazy="dynamic")


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    price_pkr = db.Column(db.Numeric(12, 2))  # PKR price (shown to Pakistan users)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey("product_categories.id", ondelete="SET NULL"))
    brand_id = db.Column(db.Integer, db.ForeignKey("product_brands.id", ondelete="SET NULL"))
    type_id = db.Column(db.Integer, db.ForeignKey("product_types.id", ondelete="SET NULL"))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = db.relationship("ProductCategory", back_populates="products")
    brand = db.relationship("ProductBrand", back_populates="products")
    product_type = db.relationship("ProductType", back_populates="products")
    stock = db.relationship(
        "Stock",
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan",
    )
    product_variants = db.relationship(
        "ProductVariant",
        back_populates="product",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    product_images = db.relationship(
        "ProductImage",
        back_populates="product",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )


class Addon(db.Model):
    """Addon group tied to a product category (e.g. 'Glasses' addon for Frames)."""
    __tablename__ = "addons"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey("product_categories.id", ondelete="CASCADE"), nullable=False)
    is_required = db.Column(db.Boolean, default=False)
    requires_image = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = db.relationship("ProductCategory", back_populates="addons")
    options = db.relationship("AddonOption", back_populates="addon", lazy="dynamic", cascade="all, delete-orphan", order_by="AddonOption.name")


class AddonOption(db.Model):
    """A selectable item within an addon group (e.g. 'Single Vision Lens — $500')."""
    __tablename__ = "addon_options"

    id = db.Column(db.Integer, primary_key=True)
    addon_id = db.Column(db.Integer, db.ForeignKey("addons.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    price_pkr = db.Column(db.Numeric(12, 2))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    addon = db.relationship("Addon", back_populates="options")


class Stock(db.Model):
    """Legacy: one row per product, qty_on_hand. Prefer movement-based inventory (StockMovement) going forward."""
    __tablename__ = "stock"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    qty_on_hand = db.Column(db.Integer, nullable=False, default=0)

    product = db.relationship("Product", back_populates="stock")
