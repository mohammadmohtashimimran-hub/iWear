"""Sales routes — catalog, eyewear, cart, orders (COD)."""
import os
import re
import uuid
from datetime import datetime

from flask import Blueprint, Response, jsonify, request
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import (
    Product,
    ProductVariant,
    ProductImage,
    ProductCategory,
    ProductBrand,
    Addon,
    AddonOption,
    FrameType,
    LensType,
    LensIndex,
    LensCoating,
    Customer,
    CustomerAddress,
    Cart,
    CartItem,
    CartItemAddon,
    Order,
    OrderItem,
    OrderStatus,
    PaymentType,
    Payment,
    PrescriptionRecord,
    PrescriptionDetail,
)
from app.auth.decorators import require_permission
from flask_jwt_extended import jwt_required, get_current_user

sales_bp = Blueprint("sales", __name__, url_prefix="/api/sales")


# --- Placeholder SVG image service (used by seed data + fallbacks) ---
_PLACEHOLDER_PALETTE = {
    "black":      ("#0f172a", "#1e293b", "#ffffff"),
    "tortoise":   ("#78350f", "#b45309", "#fef3c7"),
    "gold":       ("#a16207", "#ca8a04", "#fef9c3"),
    "silver":     ("#64748b", "#94a3b8", "#f1f5f9"),
    "blue":       ("#1e3a8a", "#3730a3", "#e0e7ff"),
    "rose":       ("#9d174d", "#be185d", "#fce7f3"),
    "green":      ("#14532d", "#166534", "#dcfce7"),
    "purple":     ("#581c87", "#6d28d9", "#ede9fe"),
    "default":    ("#1e1b4b", "#4f46e5", "#eef0ff"),
}


@sales_bp.get("/placeholder/<label>.svg")
def placeholder_svg(label):
    """Render an inline SVG placeholder for demo/fallback product images.

    The URL is read directly by ``<img src=...>`` so the SVG can be cached
    like any other static asset. Colour is derived from a keyword
    embedded in the URL (e.g. ``aviator-black.svg``) so the same product
    can vary by variant.
    """
    raw = re.sub(r"[^A-Za-z0-9 \-]", "", label.replace("-", " ")).strip() or "iWear"
    text = raw.title()[:28]
    lower = label.lower()
    palette = _PLACEHOLDER_PALETTE["default"]
    for key, colours in _PLACEHOLDER_PALETTE.items():
        if key in lower:
            palette = colours
            break
    dark, mid, light = palette
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="400" height="300">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{light}"/>
      <stop offset="100%" stop-color="{mid}" stop-opacity="0.35"/>
    </linearGradient>
    <linearGradient id="lens" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.7"/>
      <stop offset="100%" stop-color="{mid}" stop-opacity="0.35"/>
    </linearGradient>
  </defs>
  <rect fill="url(#bg)" width="400" height="300"/>
  <g transform="translate(200 140)">
    <circle cx="-70" cy="0" r="55" fill="url(#lens)" stroke="{dark}" stroke-width="5"/>
    <circle cx="70" cy="0" r="55" fill="url(#lens)" stroke="{dark}" stroke-width="5"/>
    <path d="M -15 0 Q 0 -10 15 0" fill="none" stroke="{dark}" stroke-width="5" stroke-linecap="round"/>
    <line x1="-125" y1="-8" x2="-175" y2="-18" stroke="{dark}" stroke-width="5" stroke-linecap="round"/>
    <line x1="125" y1="-8" x2="175" y2="-18" stroke="{dark}" stroke-width="5" stroke-linecap="round"/>
  </g>
  <text x="200" y="255" font-family="Inter, sans-serif" font-size="20" fill="{dark}" text-anchor="middle" font-weight="700">{text}</text>
  <text x="200" y="278" font-family="Inter, sans-serif" font-size="11" fill="{dark}" text-anchor="middle" opacity="0.65">iWear</text>
</svg>"""
    return Response(svg, mimetype="image/svg+xml", headers={"Cache-Control": "public, max-age=86400"})


def _resolve_variant(data):
    """Resolve a ProductVariant from request data.

    Accepts ``product_variant_id`` directly, or ``product_id`` as a fallback
    (picks the first active variant, or auto-creates a default one).
    Returns ``(variant, error_response)`` — one of the two is always None.
    """
    product_variant_id = data.get("product_variant_id")
    product_id = data.get("product_id")

    if product_variant_id:
        v = ProductVariant.query.get(product_variant_id)
        if not v:
            return None, (jsonify({"error": "Variant not found"}), 404)
        return v, None

    if not product_id:
        return None, (jsonify({"error": "product_variant_id or product_id required"}), 400)

    product = Product.query.get(product_id)
    if not product or not product.active:
        return None, (jsonify({"error": "Product not found"}), 404)

    v = ProductVariant.query.filter_by(product_id=product.id, active=True).first()
    if v:
        return v, None

    sku = f"DEFAULT-{product.id}"
    v = ProductVariant(
        product_id=product.id,
        sku=sku,
        unit_price=product.price,
        active=True,
    )
    db.session.add(v)
    db.session.flush()
    return v, None


def _next_order_number():
    """Generate unique order number: ORD-YYYYMMDD-XXXX."""
    prefix = "ORD-" + datetime.utcnow().strftime("%Y%m%d") + "-"
    last = Order.query.filter(Order.order_number.like(prefix + "%")).order_by(Order.id.desc()).first()
    if not last:
        n = 1
    else:
        try:
            n = int(last.order_number.rsplit("-", 1)[-1]) + 1
        except ValueError:
            n = 1
    return prefix + str(n).zfill(4)


# ---- Catalog (public) ----
@sales_bp.get("/products")
def list_products():
    """Public product list with pagination and filters."""
    page = request.args.get("page", 1)
    per_page = request.args.get("per_page", 20)
    category_id = request.args.get("category_id", type=int)
    brand_id = request.args.get("brand_id", type=int)
    type_id = request.args.get("type_id", type=int)
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    sort = (request.args.get("sort") or "").strip().lower()
    search = (request.args.get("search") or "").strip()
    q = Product.query.filter(Product.active.is_(True))
    if category_id is not None:
        q = q.filter(Product.category_id == category_id)
    if brand_id is not None:
        q = q.filter(Product.brand_id == brand_id)
    if type_id is not None:
        q = q.filter(Product.type_id == type_id)
    if min_price is not None:
        q = q.filter(Product.price >= min_price)
    if max_price is not None:
        q = q.filter(Product.price <= max_price)
    if search:
        q = q.filter(Product.name.ilike(f"%{search}%"))
    if sort == "price_asc":
        q = q.order_by(Product.price.asc().nullslast(), Product.id)
    elif sort == "price_desc":
        q = q.order_by(Product.price.desc().nullslast(), Product.id)
    elif sort == "newest":
        q = q.order_by(Product.id.desc())
    else:
        q = q.order_by(Product.id)
    total = q.count()
    per_page = min(50, max(1, int(per_page)))
    page = max(1, int(page))
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    out = []
    for p in items:
        variants = list(p.product_variants.filter(ProductVariant.active.is_(True)))
        primary_img = p.product_images.filter(ProductImage.is_primary.is_(True)).first() or p.product_images.first()
        out.append({
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "description": p.description,
            "price": float(p.price) if p.price else None,
            "price_pkr": float(p.price_pkr) if p.price_pkr else None,
            "category_id": p.category_id,
            "brand_id": p.brand_id,
            "image_url": primary_img.image_url if primary_img else None,
            "variants": [{"id": v.id, "sku": v.sku, "unit_price": float(v.unit_price) if v.unit_price else float(p.price), "unit_price_pkr": float(v.unit_price_pkr) if v.unit_price_pkr else (float(p.price_pkr) if p.price_pkr else None)} for v in variants],
        })
    return jsonify({"items": out, "total": total, "pages": (total + per_page - 1) // per_page})


@sales_bp.get("/products/<int:product_id>")
def get_product(product_id):
    p = Product.query.filter_by(id=product_id, active=True).first_or_404()
    variants = list(p.product_variants.filter(ProductVariant.active.is_(True)))
    images = list(p.product_images.all())
    addon_groups = []
    if p.category_id:
        groups = Addon.query.filter_by(category_id=p.category_id, active=True).order_by(Addon.name).all()
        for g in groups:
            opts = AddonOption.query.filter_by(addon_id=g.id, active=True).order_by(AddonOption.name).all()
            addon_groups.append({
                "id": g.id, "name": g.name, "description": g.description,
                "is_required": g.is_required,
                "requires_image": g.requires_image,
                "options": [{"id": o.id, "name": o.name, "description": o.description, "price": float(o.price) if o.price else 0, "price_pkr": float(o.price_pkr) if o.price_pkr else None} for o in opts],
            })
    return jsonify({
        "id": p.id,
        "name": p.name,
        "slug": p.slug,
        "description": p.description,
        "price": float(p.price) if p.price else None,
        "price_pkr": float(p.price_pkr) if p.price_pkr else None,
        "category_id": p.category_id,
        "brand_id": p.brand_id,
        "variants": [{"id": v.id, "sku": v.sku, "unit_price": float(v.unit_price) if v.unit_price else float(p.price), "unit_price_pkr": float(v.unit_price_pkr) if v.unit_price_pkr else (float(p.price_pkr) if p.price_pkr else None), "color": v.color, "size": v.size} for v in variants],
        "images": [{"id": i.id, "image_url": i.image_url, "is_primary": i.is_primary} for i in images],
        "addons": addon_groups,
    })


# ---- Eyewear masters (public) ----
@sales_bp.get("/frame-types")
def list_frame_types():
    return jsonify([{"id": f.id, "name": f.name} for f in FrameType.query.all()])


@sales_bp.get("/lens-types")
def list_lens_types():
    return jsonify([{"id": l.id, "name": l.name} for l in LensType.query.all()])


@sales_bp.get("/lens-indexes")
def list_lens_indexes():
    return jsonify([{"id": l.id, "name": l.name, "value": float(l.value)} for l in LensIndex.query.all()])


@sales_bp.get("/lens-coatings")
def list_lens_coatings():
    return jsonify([{"id": c.id, "name": c.name} for c in LensCoating.query.all()])


@sales_bp.post("/prescriptions")
def create_prescription():
    """Create prescription (guest or customer). Optional customer_id."""
    data = request.get_json() or {}
    customer_id = data.get("customer_id")
    notes = data.get("notes")
    rec = PrescriptionRecord(customer_id=customer_id, notes=notes)
    db.session.add(rec)
    db.session.flush()
    for detail in data.get("details", []):
        db.session.add(PrescriptionDetail(
            prescription_record_id=rec.id,
            eye_side=detail.get("eye_side", ""),
            sphere=detail.get("sphere"),
            cylinder=detail.get("cylinder"),
            axis=detail.get("axis"),
            add_power=detail.get("add_power"),
            pd=detail.get("pd"),
        ))
    db.session.commit()
    return jsonify({"id": rec.id, "customer_id": rec.customer_id}), 201


# ---- Customers ----
@sales_bp.get("/customers")
@jwt_required()
@require_permission("sales:read")
def list_customers():
    """Admin: list all customers with order count and total spent."""
    search = (request.args.get("search") or "").strip()
    q = Customer.query
    if search:
        q = q.filter(
            db.or_(
                Customer.first_name.ilike(f"%{search}%"),
                Customer.last_name.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%"),
                Customer.phone.ilike(f"%{search}%"),
            )
        )
    customers = q.order_by(Customer.id.desc()).limit(500).all()
    out = []
    for c in customers:
        order_count = c.orders.count()
        total_spent = sum(float(o.grand_total) for o in c.orders) if order_count else 0
        out.append({
            "id": c.id,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "phone": c.phone,
            "email": c.email,
            "active": c.active,
            "order_count": order_count,
            "total_spent": round(total_spent, 2),
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })
    return jsonify(out)


@sales_bp.post("/customers")
def create_customer():
    data = request.get_json() or {}
    first_name = (data.get("first_name") or "").strip()
    phone = (data.get("phone") or "").strip()
    if not first_name or not phone:
        return jsonify({"error": "first_name and phone required"}), 400
    c = Customer(
        first_name=first_name,
        last_name=data.get("last_name"),
        phone=phone,
        email=data.get("email"),
        active=True,
    )
    db.session.add(c)
    db.session.commit()
    return jsonify({"id": c.id, "first_name": c.first_name, "phone": c.phone}), 201


@sales_bp.post("/customers/<int:customer_id>/addresses")
def add_customer_address(customer_id):
    Customer.query.get_or_404(customer_id)
    data = request.get_json() or {}
    address_line_1 = (data.get("address_line_1") or "").strip()
    city = (data.get("city") or "").strip()
    if not address_line_1 or not city:
        return jsonify({"error": "address_line_1 and city required"}), 400
    a = CustomerAddress(
        customer_id=customer_id,
        address_line_1=address_line_1,
        address_line_2=data.get("address_line_2"),
        city=city,
        state=data.get("state"),
        postal_code=data.get("postal_code"),
        country=data.get("country"),
        is_default=data.get("is_default", False),
    )
    db.session.add(a)
    db.session.commit()
    return jsonify({"id": a.id}), 201


# ---- Cart ----
@sales_bp.post("/carts")
def create_cart():
    """Create cart (guest: no customer_id; or with customer_id)."""
    data = request.get_json() or {}
    customer_id = data.get("customer_id")
    cart = Cart(customer_id=customer_id, status="active")
    db.session.add(cart)
    db.session.commit()
    return jsonify({"id": cart.id, "customer_id": cart.customer_id}), 201


def _cart_response(cart):
    """Serialise a cart with its items (including addon details)."""
    items = []
    for ci in cart.cart_items:
        v = ci.product_variant
        p = v.product
        primary_img = p.product_images.filter(ProductImage.is_primary.is_(True)).first() or p.product_images.first()
        addons_out = []
        for cia in (ci.item_addons or []):
            opt = cia.addon_option
            group = opt.addon if opt else None
            addons_out.append({
                "id": cia.id,
                "addon_option_id": cia.addon_option_id,
                "group_name": group.name if group else None,
                "option_name": opt.name if opt else None,
                "price": float(opt.price) if opt and opt.price else 0,
                "image_url": cia.image_url,
            })
        items.append({
            "id": ci.id,
            "product_variant_id": ci.product_variant_id,
            "product_name": p.name,
            "sku": v.sku,
            "color": v.color,
            "size": v.size,
            "quantity": ci.quantity,
            "unit_price": float(ci.unit_price),
            "line_total": float(ci.quantity * ci.unit_price),
            "image_url": primary_img.image_url if primary_img else None,
            "addons": addons_out,
        })
    return {"id": cart.id, "status": cart.status, "items": items}


@sales_bp.get("/my-cart")
@jwt_required()
def get_my_cart():
    """Return the authenticated user's active cart (create one if none exists)."""
    user = get_current_user()
    cart = Cart.query.filter_by(user_id=user.id, status="active").first()
    if not cart:
        cart = Cart(user_id=user.id, status="active")
        db.session.add(cart)
        db.session.commit()
    return jsonify(_cart_response(cart))


def _addon_option_ids(addons_payload):
    """Extract a frozenset of addon_option_id values from the request payload."""
    if not addons_payload:
        return frozenset()
    return frozenset(int(a["addon_option_id"]) for a in addons_payload if a.get("addon_option_id"))


def _find_matching_cart_item(cart_id, variant_id, addon_ids):
    """Find a CartItem with the exact same variant AND addon set."""
    candidates = CartItem.query.filter_by(cart_id=cart_id, product_variant_id=variant_id).all()
    for ci in candidates:
        existing_ids = frozenset(cia.addon_option_id for cia in ci.item_addons)
        if existing_ids == addon_ids:
            return ci
    return None


def _attach_addons(cart_item, addons_payload):
    """Create CartItemAddon records for a new cart item."""
    if not addons_payload:
        return
    for a in addons_payload:
        opt_id = a.get("addon_option_id")
        if not opt_id:
            continue
        opt = AddonOption.query.get(int(opt_id))
        if not opt:
            continue
        db.session.add(CartItemAddon(
            cart_item_id=cart_item.id,
            addon_option_id=opt.id,
            image_url=a.get("image_url"),
        ))


@sales_bp.post("/my-cart/items")
@jwt_required()
def add_my_cart_item():
    """Add an item to the authenticated user's active cart."""
    user = get_current_user()
    cart = Cart.query.filter_by(user_id=user.id, status="active").first()
    if not cart:
        cart = Cart(user_id=user.id, status="active")
        db.session.add(cart)
        db.session.flush()
    data = request.get_json() or {}
    quantity = int(data.get("quantity", 1))
    if quantity < 1:
        return jsonify({"error": "Positive quantity required"}), 400
    v, err = _resolve_variant(data)
    if err:
        return err
    unit_price = data.get("unit_price")
    if unit_price is None:
        unit_price = v.unit_price or v.product.price
    addons_payload = data.get("addons") or []
    addon_ids = _addon_option_ids(addons_payload)
    existing = _find_matching_cart_item(cart.id, v.id, addon_ids)
    if existing:
        existing.quantity += quantity
        db.session.commit()
        return jsonify(_cart_response(cart)), 200
    ci = CartItem(cart_id=cart.id, product_variant_id=v.id, quantity=quantity, unit_price=unit_price)
    db.session.add(ci)
    db.session.flush()
    _attach_addons(ci, addons_payload)
    db.session.commit()
    return jsonify(_cart_response(cart)), 201


@sales_bp.patch("/my-cart/items/<int:item_id>")
@jwt_required()
def update_my_cart_item(item_id):
    """Update quantity of an item in the user's active cart."""
    user = get_current_user()
    cart = Cart.query.filter_by(user_id=user.id, status="active").first()
    if not cart:
        return jsonify({"error": "No active cart"}), 404
    ci = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first_or_404()
    data = request.get_json() or {}
    qty = data.get("quantity")
    if qty is not None:
        qty = int(qty)
        if qty <= 0:
            db.session.delete(ci)
            db.session.commit()
            return jsonify(_cart_response(cart))
        ci.quantity = qty
    db.session.commit()
    return jsonify(_cart_response(cart))


@sales_bp.delete("/my-cart/items/<int:item_id>")
@jwt_required()
def remove_my_cart_item(item_id):
    """Remove an item from the user's active cart."""
    user = get_current_user()
    cart = Cart.query.filter_by(user_id=user.id, status="active").first()
    if not cart:
        return jsonify({"error": "No active cart"}), 404
    ci = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first_or_404()
    db.session.delete(ci)
    db.session.commit()
    return jsonify(_cart_response(cart))


@sales_bp.post("/my-cart/merge")
@jwt_required()
def merge_guest_cart():
    """Merge a guest cart (by id) into the authenticated user's cart."""
    user = get_current_user()
    data = request.get_json() or {}
    guest_cart_id = data.get("guest_cart_id")
    if not guest_cart_id:
        return jsonify({"error": "guest_cart_id required"}), 400
    guest_cart = Cart.query.get(guest_cart_id)
    if not guest_cart or guest_cart.status != "active":
        user_cart = Cart.query.filter_by(user_id=user.id, status="active").first()
        if not user_cart:
            user_cart = Cart(user_id=user.id, status="active")
            db.session.add(user_cart)
            db.session.commit()
        return jsonify(_cart_response(user_cart))

    user_cart = Cart.query.filter_by(user_id=user.id, status="active").first()
    if not user_cart:
        user_cart = Cart(user_id=user.id, status="active")
        db.session.add(user_cart)
        db.session.flush()

    for gi in guest_cart.cart_items:
        guest_addon_ids = frozenset(cia.addon_option_id for cia in gi.item_addons)
        existing = _find_matching_cart_item(user_cart.id, gi.product_variant_id, guest_addon_ids)
        if existing:
            existing.quantity += gi.quantity
        else:
            new_ci = CartItem(
                cart_id=user_cart.id,
                product_variant_id=gi.product_variant_id,
                quantity=gi.quantity,
                unit_price=gi.unit_price,
            )
            db.session.add(new_ci)
            db.session.flush()
            for cia in gi.item_addons:
                db.session.add(CartItemAddon(
                    cart_item_id=new_ci.id,
                    addon_option_id=cia.addon_option_id,
                    image_url=cia.image_url,
                ))

    guest_cart.status = "merged"
    db.session.commit()
    return jsonify(_cart_response(user_cart))


@sales_bp.get("/carts/<int:cart_id>")
def get_cart(cart_id):
    cart = Cart.query.get_or_404(cart_id)
    return jsonify(_cart_response(cart))


@sales_bp.post("/carts/<int:cart_id>/items")
def add_cart_item(cart_id):
    cart = Cart.query.get_or_404(cart_id)
    if cart.status != "active":
        return jsonify({"error": "Cart not active"}), 400
    data = request.get_json() or {}
    quantity = int(data.get("quantity", 1))
    if quantity < 1:
        return jsonify({"error": "Positive quantity required"}), 400
    v, err = _resolve_variant(data)
    if err:
        return err
    unit_price = data.get("unit_price")
    if unit_price is None:
        unit_price = v.unit_price or v.product.price
    addons_payload = data.get("addons") or []
    addon_ids = _addon_option_ids(addons_payload)
    existing = _find_matching_cart_item(cart_id, v.id, addon_ids)
    if existing:
        existing.quantity += quantity
        db.session.commit()
        return jsonify({"id": existing.id, "quantity": existing.quantity}), 200
    ci = CartItem(cart_id=cart_id, product_variant_id=v.id, quantity=quantity, unit_price=unit_price)
    db.session.add(ci)
    db.session.flush()
    _attach_addons(ci, addons_payload)
    db.session.commit()
    return jsonify({"id": ci.id, "quantity": ci.quantity}), 201


@sales_bp.patch("/carts/<int:cart_id>/items/<int:item_id>")
def update_cart_item(cart_id, item_id):
    ci = CartItem.query.filter_by(id=item_id, cart_id=cart_id).first_or_404()
    data = request.get_json() or {}
    qty = data.get("quantity")
    if qty is not None:
        qty = int(qty)
        if qty <= 0:
            db.session.delete(ci)
            db.session.commit()
            return "", 204
        ci.quantity = qty
    db.session.commit()
    return jsonify({"id": ci.id, "quantity": ci.quantity})


@sales_bp.delete("/carts/<int:cart_id>/items/<int:item_id>")
def remove_cart_item(cart_id, item_id):
    ci = CartItem.query.filter_by(id=item_id, cart_id=cart_id).first_or_404()
    db.session.delete(ci)
    db.session.commit()
    return "", 204


# ---- Order statuses ----
@sales_bp.get("/order-statuses")
def list_order_statuses():
    statuses = OrderStatus.query.order_by(OrderStatus.id).all()
    return jsonify([{"id": s.id, "code": s.code, "name": s.name, "description": s.description} for s in statuses])


@sales_bp.post("/order-statuses")
@jwt_required()
@require_permission("sales:write")
def create_order_status():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    code = (data.get("code") or "").strip().lower()
    if not name or not code:
        return jsonify({"error": "name and code required"}), 400
    if OrderStatus.query.filter_by(code=code).first():
        return jsonify({"error": "Status code already exists"}), 409
    s = OrderStatus(name=name, code=code, description=data.get("description"))
    db.session.add(s)
    db.session.commit()
    return jsonify({"id": s.id, "code": s.code, "name": s.name, "description": s.description}), 201


@sales_bp.patch("/order-statuses/<int:sid>")
@jwt_required()
@require_permission("sales:write")
def update_order_status_entry(sid):
    s = OrderStatus.query.get_or_404(sid)
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if name:
        s.name = name
    code = (data.get("code") or "").strip().lower()
    if code and code != s.code:
        if OrderStatus.query.filter_by(code=code).first():
            return jsonify({"error": "Status code already exists"}), 409
        s.code = code
    if "description" in data:
        s.description = data["description"]
    db.session.commit()
    return jsonify({"id": s.id, "code": s.code, "name": s.name, "description": s.description})


@sales_bp.delete("/order-statuses/<int:sid>")
@jwt_required()
@require_permission("sales:write")
def delete_order_status_entry(sid):
    s = OrderStatus.query.get_or_404(sid)
    if Order.query.filter_by(status_id=s.id).first():
        return jsonify({"error": "Cannot delete status that is in use by orders"}), 409
    db.session.delete(s)
    db.session.commit()
    return "", 204


# ---- User orders (authenticated) ----
@sales_bp.get("/my-orders")
@jwt_required()
def get_my_orders():
    """Return all orders placed by the authenticated user."""
    user = get_current_user()
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.id.desc()).all()
    return jsonify([{
        "id": o.id,
        "order_number": o.order_number,
        "grand_total": float(o.grand_total),
        "status": o.status.code if o.status else None,
        "status_name": o.status.name if o.status else None,
        "items_count": o.order_items.count(),
        "created_at": o.created_at.isoformat() if o.created_at else None,
    } for o in orders])


# ---- Orders ----
@sales_bp.post("/orders")
def create_order():
    """Create order from cart. COD only. Requires cart_id, customer_id, optional address."""
    from flask_jwt_extended import verify_jwt_in_request
    data = request.get_json() or {}
    cart_id = data.get("cart_id")
    customer_id = data.get("customer_id")
    if not cart_id or not customer_id:
        return jsonify({"error": "cart_id and customer_id required"}), 400
    cart = Cart.query.get_or_404(cart_id)
    if cart.status != "active":
        return jsonify({"error": "Cart not active"}), 400
    Customer.query.get_or_404(customer_id)
    current_user_id = None
    try:
        verify_jwt_in_request(optional=True)
        u = get_current_user()
        if u:
            current_user_id = u.id
    except Exception:
        pass
    pending = OrderStatus.query.filter_by(code="pending").first()
    if not pending:
        return jsonify({"error": "Order status 'pending' not found"}), 500
    cod = PaymentType.query.filter_by(code="cod").first()
    if not cod:
        return jsonify({"error": "Payment type COD not found"}), 500

    subtotal = sum(float(ci.quantity * ci.unit_price) for ci in cart.cart_items)
    discount_total = data.get("discount_total") or 0
    tax_total = data.get("tax_total") or 0
    grand_total = subtotal - discount_total + tax_total

    order = Order(
        customer_id=customer_id,
        user_id=current_user_id,
        status_id=pending.id,
        order_number=_next_order_number(),
        subtotal=subtotal,
        discount_total=discount_total,
        tax_total=tax_total,
        grand_total=grand_total,
        shipping_address=data.get("shipping_address"),
        shipping_country_id=data.get("shipping_country_id") or None,
        shipping_city_id=data.get("shipping_city_id") or None,
        notes=data.get("notes"),
    )
    db.session.add(order)
    db.session.flush()
    for ci in cart.cart_items:
        line_total = float(ci.quantity * ci.unit_price)
        db.session.add(OrderItem(
            order_id=order.id,
            product_variant_id=ci.product_variant_id,
            quantity=ci.quantity,
            unit_price=ci.unit_price,
            discount_amount=0,
            tax_amount=0,
            line_total=line_total,
        ))
        product = ci.product_variant.product
        product.quantity = max(0, (product.quantity or 0) - ci.quantity)
    db.session.add(Payment(
        order_id=order.id,
        payment_type_id=cod.id,
        amount=grand_total,
        status="pending",
        payment_reference=data.get("payment_reference"),
    ))
    cart.status = "converted"
    db.session.commit()
    return jsonify({
        "id": order.id,
        "order_number": order.order_number,
        "grand_total": grand_total,
        "status": "pending",
        "message": "Order placed. Pay on delivery (COD).",
    }), 201


@sales_bp.get("/orders")
def list_orders():
    customer_id = request.args.get("customer_id", type=int)
    # Admin: no customer_id + JWT with sales:read returns all orders
    if customer_id is None:
        try:
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request(optional=True)
            user = get_current_user()
            if user and user.has_permission("sales:read"):
                q = Order.query.order_by(Order.id.desc()).limit(200)
                orders = q.all()
                return jsonify([{
                    "id": o.id,
                    "order_number": o.order_number,
                    "customer_id": o.customer_id,
                    "grand_total": float(o.grand_total),
                    "status": o.status.code if o.status else None,
                    "created_at": o.created_at.isoformat() if o.created_at else None,
                } for o in orders])
        except Exception:
            pass
        return jsonify({"error": "customer_id required"}), 400
    orders = Order.query.filter_by(customer_id=customer_id).order_by(Order.id.desc()).limit(50).all()
    return jsonify([{
        "id": o.id,
        "order_number": o.order_number,
        "grand_total": float(o.grand_total),
        "status": o.status.code if o.status else None,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    } for o in orders])


@sales_bp.patch("/orders/<int:order_id>")
@jwt_required()
@require_permission("sales:write")
def update_order_status(order_id):
    """Admin: update order status (e.g. pending -> confirmed)."""
    o = Order.query.get_or_404(order_id)
    data = request.get_json() or {}
    status_code = (data.get("status") or "").strip().lower()
    if not status_code:
        return jsonify({"error": "status required"}), 400
    status = OrderStatus.query.filter_by(code=status_code).first()
    if not status:
        return jsonify({"error": "Invalid status"}), 400
    o.status_id = status.id
    db.session.commit()
    return jsonify({
        "id": o.id,
        "order_number": o.order_number,
        "status": status.code,
    })


@sales_bp.get("/orders/<int:order_id>")
def get_order(order_id):
    o = Order.query.get_or_404(order_id)
    items = []
    for oi in o.order_items:
        v = ProductVariant.query.get(oi.product_variant_id)
        p = v.product if v else None
        primary_img = None
        if p:
            img = next((i for i in p.product_images if i.is_primary), None)
            if not img and p.product_images:
                img = p.product_images[0]
            if img:
                primary_img = img.image_url
        items.append({
            "product_variant_id": oi.product_variant_id,
            "product_name": p.name if p else "Unknown",
            "product_slug": p.slug if p else None,
            "image_url": primary_img,
            "sku": v.sku if v else None,
            "variant_name": " / ".join(filter(None, [v.color, v.size])) if v else None,
            "quantity": oi.quantity,
            "unit_price": float(oi.unit_price),
            "line_total": float(oi.line_total),
            "stock_remaining": p.quantity if p else None,
        })
    customer = Customer.query.get(o.customer_id) if o.customer_id else None
    return jsonify({
        "id": o.id,
        "order_number": o.order_number,
        "customer_id": o.customer_id,
        "customer_name": f"{customer.first_name} {customer.last_name or ''}".strip() if customer else None,
        "customer_phone": customer.phone if customer else None,
        "customer_email": customer.email if customer else None,
        "status": o.status.code if o.status else None,
        "status_name": o.status.name if o.status else None,
        "subtotal": float(o.subtotal),
        "discount_total": float(o.discount_total),
        "tax_total": float(o.tax_total),
        "grand_total": float(o.grand_total),
        "shipping_address": o.shipping_address,
        "shipping_country": o.shipping_country.name if o.shipping_country else None,
        "shipping_city": o.shipping_city.name if o.shipping_city else None,
        "notes": o.notes,
        "created_at": o.created_at.isoformat() if o.created_at else None,
        "items": items,
    })


# ---- Addon image upload (public, no auth) ----
_ADDON_IMG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "addon_images"))
_ALLOWED_IMG_EXT = {"png", "jpg", "jpeg", "gif", "webp", "bmp"}


def _allowed_addon_image(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in _ALLOWED_IMG_EXT


@sales_bp.post("/addon-image")
def upload_addon_image():
    """Accept a single image from a customer (e.g. prescription). Returns the URL."""
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    f = request.files["image"]
    if not f or not f.filename:
        return jsonify({"error": "Empty file"}), 400
    if not _allowed_addon_image(f.filename):
        return jsonify({"error": "File type not allowed"}), 400
    os.makedirs(_ADDON_IMG_DIR, exist_ok=True)
    ext = secure_filename(f.filename).rsplit(".", 1)[-1]
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    f.save(os.path.join(_ADDON_IMG_DIR, unique_name))
    image_url = f"/uploads/addon_images/{unique_name}"
    return jsonify({"image_url": image_url}), 201


@sales_bp.get("/")
def index():
    return jsonify({"module": "sales", "endpoints": ["/products", "/frame-types", "/lens-types", "/carts", "/orders"]})
