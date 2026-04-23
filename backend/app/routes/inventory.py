"""Inventory routes — products, variants, stock, movements, suppliers, warehouses, low-stock, purchase orders."""
import os
import uuid

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import (
    Product,
    ProductVariant,
    ProductImage,
    ProductCategory,
    ProductBrand,
    ProductType,
    Addon,
    AddonOption,
    Supplier,
    Warehouse,
    StockMovement,
    StockAdjustment,
    PurchaseOrder,
    PurchaseOrderItem,
)
from app.auth.decorators import require_permission
from app.services.inventory_service import get_current_stock, get_low_stock_variants
from flask_jwt_extended import jwt_required

inventory_bp = Blueprint("inventory", __name__, url_prefix="/api/inventory")

_ALLOWED_IMG_EXT = {"png", "jpg", "jpeg", "gif", "webp"}
_MAX_IMAGES_PER_PRODUCT = 10
_UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "products"))


def _allowed_image(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in _ALLOWED_IMG_EXT


def _paginate(query, page=1, per_page=20):
    page = max(1, int(page))
    per_page = min(100, max(1, int(per_page)))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return pagination.items, pagination.total, pagination.pages


# ---- Categories, brands, types (read for filters) ----
@inventory_bp.get("/categories")
def list_categories():
    items = ProductCategory.query.all()
    return jsonify([{"id": c.id, "name": c.name} for c in items])


@inventory_bp.get("/brands")
def list_brands():
    items = ProductBrand.query.all()
    return jsonify([{"id": b.id, "name": b.name} for b in items])


@inventory_bp.get("/types")
def list_types():
    items = ProductType.query.all()
    return jsonify([{"id": t.id, "name": t.name} for t in items])


# ---- Categories CRUD ----
@inventory_bp.post("/categories")
@jwt_required()
@require_permission("inventory:write")
def create_category():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name required"}), 400
    c = ProductCategory(name=name)
    db.session.add(c)
    db.session.commit()
    return jsonify({"id": c.id, "name": c.name}), 201


@inventory_bp.patch("/categories/<int:cid>")
@jwt_required()
@require_permission("inventory:write")
def update_category(cid):
    c = ProductCategory.query.get_or_404(cid)
    data = request.get_json() or {}
    if "name" in data and data["name"].strip():
        c.name = data["name"].strip()
    db.session.commit()
    return jsonify({"id": c.id, "name": c.name})


@inventory_bp.delete("/categories/<int:cid>")
@jwt_required()
@require_permission("inventory:write")
def delete_category(cid):
    c = ProductCategory.query.get_or_404(cid)
    db.session.delete(c)
    db.session.commit()
    return "", 204


# ---- Brands CRUD ----
@inventory_bp.post("/brands")
@jwt_required()
@require_permission("inventory:write")
def create_brand():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name required"}), 400
    b = ProductBrand(name=name)
    db.session.add(b)
    db.session.commit()
    return jsonify({"id": b.id, "name": b.name}), 201


@inventory_bp.patch("/brands/<int:bid>")
@jwt_required()
@require_permission("inventory:write")
def update_brand(bid):
    b = ProductBrand.query.get_or_404(bid)
    data = request.get_json() or {}
    if "name" in data and data["name"].strip():
        b.name = data["name"].strip()
    db.session.commit()
    return jsonify({"id": b.id, "name": b.name})


@inventory_bp.delete("/brands/<int:bid>")
@jwt_required()
@require_permission("inventory:write")
def delete_brand(bid):
    b = ProductBrand.query.get_or_404(bid)
    db.session.delete(b)
    db.session.commit()
    return "", 204


# ---- Types CRUD ----
@inventory_bp.post("/types")
@jwt_required()
@require_permission("inventory:write")
def create_type():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name required"}), 400
    t = ProductType(name=name)
    db.session.add(t)
    db.session.commit()
    return jsonify({"id": t.id, "name": t.name}), 201


@inventory_bp.patch("/types/<int:tid>")
@jwt_required()
@require_permission("inventory:write")
def update_type(tid):
    t = ProductType.query.get_or_404(tid)
    data = request.get_json() or {}
    if "name" in data and data["name"].strip():
        t.name = data["name"].strip()
    db.session.commit()
    return jsonify({"id": t.id, "name": t.name})


@inventory_bp.delete("/types/<int:tid>")
@jwt_required()
@require_permission("inventory:write")
def delete_type(tid):
    t = ProductType.query.get_or_404(tid)
    db.session.delete(t)
    db.session.commit()
    return "", 204


# ---- Addon groups (per-category) ----
def _addon_to_dict(a, include_options=False):
    out = {
        "id": a.id, "name": a.name, "description": a.description,
        "category_id": a.category_id,
        "category_name": a.category.name if a.category else None,
        "is_required": a.is_required, "requires_image": a.requires_image,
        "active": a.active,
    }
    if include_options:
        out["options"] = [{
            "id": o.id, "name": o.name, "description": o.description,
            "price": float(o.price) if o.price is not None else 0, "active": o.active,
        } for o in a.options.all()]
    return out


@inventory_bp.get("/addons")
def list_addons():
    category_id = request.args.get("category_id", type=int)
    q = Addon.query
    if category_id is not None:
        q = q.filter(Addon.category_id == category_id)
    items = q.order_by(Addon.category_id, Addon.name).all()
    return jsonify([_addon_to_dict(a, include_options=True) for a in items])


@inventory_bp.get("/addons/<int:addon_id>")
def get_addon(addon_id):
    a = Addon.query.get_or_404(addon_id)
    return jsonify(_addon_to_dict(a, include_options=True))


@inventory_bp.post("/addons")
@jwt_required()
@require_permission("inventory:write")
def create_addon():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    category_id = data.get("category_id")
    if not name or not category_id:
        return jsonify({"error": "name and category_id required"}), 400
    ProductCategory.query.get_or_404(int(category_id))
    a = Addon(
        name=name,
        description=data.get("description"),
        category_id=int(category_id),
        is_required=data.get("is_required", False),
        requires_image=data.get("requires_image", False),
        active=data.get("active", True),
    )
    db.session.add(a)
    db.session.commit()
    return jsonify(_addon_to_dict(a)), 201


@inventory_bp.patch("/addons/<int:addon_id>")
@jwt_required()
@require_permission("inventory:write")
def update_addon(addon_id):
    a = Addon.query.get_or_404(addon_id)
    data = request.get_json() or {}
    if "name" in data and data["name"].strip():
        a.name = data["name"].strip()
    if "description" in data:
        a.description = data["description"]
    if "category_id" in data and data["category_id"]:
        ProductCategory.query.get_or_404(int(data["category_id"]))
        a.category_id = int(data["category_id"])
    if "is_required" in data:
        a.is_required = data["is_required"]
    if "requires_image" in data:
        a.requires_image = data["requires_image"]
    if "active" in data:
        a.active = data["active"]
    db.session.commit()
    return jsonify(_addon_to_dict(a))


@inventory_bp.delete("/addons/<int:addon_id>")
@jwt_required()
@require_permission("inventory:write")
def delete_addon(addon_id):
    a = Addon.query.get_or_404(addon_id)
    db.session.delete(a)
    db.session.commit()
    return "", 204


# ---- Addon options (items within a group) ----
@inventory_bp.post("/addons/<int:addon_id>/options")
@jwt_required()
@require_permission("inventory:write")
def create_addon_option(addon_id):
    Addon.query.get_or_404(addon_id)
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name required"}), 400
    o = AddonOption(
        addon_id=addon_id, name=name,
        description=data.get("description"),
        price=data.get("price", 0),
        active=data.get("active", True),
    )
    db.session.add(o)
    db.session.commit()
    return jsonify({"id": o.id, "name": o.name, "price": float(o.price)}), 201


@inventory_bp.patch("/addons/<int:addon_id>/options/<int:option_id>")
@jwt_required()
@require_permission("inventory:write")
def update_addon_option(addon_id, option_id):
    o = AddonOption.query.filter_by(id=option_id, addon_id=addon_id).first_or_404()
    data = request.get_json() or {}
    if "name" in data and data["name"].strip():
        o.name = data["name"].strip()
    if "description" in data:
        o.description = data["description"]
    if "price" in data:
        o.price = data["price"]
    if "active" in data:
        o.active = data["active"]
    db.session.commit()
    return jsonify({"id": o.id, "name": o.name, "price": float(o.price)})


@inventory_bp.delete("/addons/<int:addon_id>/options/<int:option_id>")
@jwt_required()
@require_permission("inventory:write")
def delete_addon_option(addon_id, option_id):
    o = AddonOption.query.filter_by(id=option_id, addon_id=addon_id).first_or_404()
    db.session.delete(o)
    db.session.commit()
    return "", 204


# ---- Products CRUD ----
@inventory_bp.get("/products")
def list_products():
    page = request.args.get("page", 1)
    per_page = request.args.get("per_page", 20)
    category_id = request.args.get("category_id", type=int)
    brand_id = request.args.get("brand_id", type=int)
    active = request.args.get("active")
    q = Product.query
    if category_id is not None:
        q = q.filter(Product.category_id == category_id)
    if brand_id is not None:
        q = q.filter(Product.brand_id == brand_id)
    if active is not None:
        q = q.filter(Product.active == (active.lower() == "true"))
    q = q.order_by(Product.id)
    items, total, pages = _paginate(q, page, per_page)
    return jsonify({
        "items": [_product_to_dict(p) for p in items],
        "total": total,
        "pages": pages,
    })


def _product_to_dict(p):
    primary = ProductImage.query.filter_by(product_id=p.id, is_primary=True).first()
    return {
        "id": p.id,
        "name": p.name,
        "slug": p.slug,
        "description": p.description,
        "price": float(p.price) if p.price is not None else None,
        "price_pkr": float(p.price_pkr) if p.price_pkr is not None else None,
        "quantity": p.quantity if p.quantity is not None else 0,
        "category_id": p.category_id,
        "brand_id": p.brand_id,
        "type_id": p.type_id,
        "active": p.active,
        "primary_image": primary.image_url if primary else None,
    }


@inventory_bp.get("/products/<int:product_id>")
def get_product(product_id):
    p = Product.query.get_or_404(product_id)
    out = _product_to_dict(p)
    out["variants"] = [{"id": v.id, "sku": v.sku, "unit_price": float(v.unit_price) if v.unit_price else None} for v in p.product_variants]
    out["images"] = [{"id": i.id, "image_url": i.image_url, "is_primary": i.is_primary} for i in p.product_images]
    return jsonify(out)


@inventory_bp.post("/products")
@jwt_required()
@require_permission("inventory:write")
def create_product():
    try:
        data = request.get_json() or {}
        name = (data.get("name") or "").strip()
        if not name:
            return jsonify({"error": "name required"}), 400
        slug = (data.get("slug") or name.lower().replace(" ", "-"))[:255]
        if Product.query.filter_by(slug=slug).first():
            return jsonify({"error": "slug already exists"}), 409
        price = data.get("price", 0)
        try:
            price = float(price) if price is not None else 0
        except (TypeError, ValueError):
            price = 0
        quantity = data.get("quantity", 0)
        try:
            quantity = int(quantity) if quantity is not None else 0
        except (TypeError, ValueError):
            quantity = 0
        price_pkr = data.get("price_pkr")
        if price_pkr is not None:
            try:
                price_pkr = float(price_pkr)
            except (TypeError, ValueError):
                price_pkr = None
        product = Product(
            name=name,
            slug=slug,
            description=data.get("description"),
            price=price,
            price_pkr=price_pkr,
            quantity=max(0, quantity),
            category_id=data.get("category_id") or None,
            brand_id=data.get("brand_id") or None,
            type_id=data.get("type_id") or None,
            active=data.get("active", True),
        )
        db.session.add(product)
        db.session.commit()
        return jsonify(_product_to_dict(product)), 201
    except Exception as e:
        db.session.rollback()
        from flask import current_app
        current_app.logger.exception("create_product failed")
        return jsonify({"error": str(e)}), 500


@inventory_bp.patch("/products/<int:product_id>")
@jwt_required()
@require_permission("inventory:write")
def update_product(product_id):
    p = Product.query.get_or_404(product_id)
    data = request.get_json() or {}
    if "name" in data:
        p.name = (data["name"] or "").strip() or p.name
    if "slug" in data and data["slug"]:
        p.slug = data["slug"][:255]
    if "description" in data:
        p.description = data["description"]
    if "price" in data:
        p.price = data["price"]
    if "price_pkr" in data:
        p.price_pkr = data["price_pkr"] if data["price_pkr"] is not None else None
    if "quantity" in data:
        try:
            p.quantity = max(0, int(data["quantity"]))
        except (TypeError, ValueError):
            pass
    if "category_id" in data:
        p.category_id = data["category_id"]
    if "brand_id" in data:
        p.brand_id = data["brand_id"]
    if "type_id" in data:
        p.type_id = data["type_id"]
    if "active" in data:
        p.active = data["active"]
    db.session.commit()
    return jsonify(_product_to_dict(p))


@inventory_bp.delete("/products/<int:product_id>")
@jwt_required()
@require_permission("inventory:write")
def delete_product(product_id):
    p = Product.query.get_or_404(product_id)
    for img in ProductImage.query.filter_by(product_id=product_id).all():
        _delete_image_file(img.image_url)
    db.session.delete(p)
    db.session.commit()
    return "", 204


# ---- Product images ----
def _delete_image_file(image_url):
    """Remove an uploaded file from disk given its URL path."""
    if not image_url:
        return
    filename = os.path.basename(image_url)
    filepath = os.path.join(_UPLOAD_DIR, filename)
    if os.path.isfile(filepath):
        os.remove(filepath)


@inventory_bp.post("/products/<int:product_id>/images")
@jwt_required()
@require_permission("inventory:write")
def upload_product_images(product_id):
    Product.query.get_or_404(product_id)
    existing_count = ProductImage.query.filter_by(product_id=product_id).count()
    files = request.files.getlist("images")
    if not files or not files[0].filename:
        return jsonify({"error": "No images provided"}), 400
    if existing_count + len(files) > _MAX_IMAGES_PER_PRODUCT:
        return jsonify({"error": f"Maximum {_MAX_IMAGES_PER_PRODUCT} images allowed. Currently {existing_count}."}), 400

    os.makedirs(_UPLOAD_DIR, exist_ok=True)
    uploaded = []
    for f in files:
        if not f or not _allowed_image(f.filename):
            continue
        ext = f.filename.rsplit(".", 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        f.save(os.path.join(_UPLOAD_DIR, filename))
        img = ProductImage(
            product_id=product_id,
            image_url=f"/uploads/products/{filename}",
            alt_text=secure_filename(f.filename),
            is_primary=(existing_count == 0 and len(uploaded) == 0),
        )
        db.session.add(img)
        uploaded.append(img)

    db.session.commit()
    return jsonify({
        "images": [{"id": i.id, "image_url": i.image_url, "is_primary": i.is_primary, "alt_text": i.alt_text} for i in uploaded],
    }), 201


@inventory_bp.delete("/products/<int:product_id>/images/<int:image_id>")
@jwt_required()
@require_permission("inventory:write")
def delete_product_image(product_id, image_id):
    img = ProductImage.query.filter_by(id=image_id, product_id=product_id).first_or_404()
    was_primary = img.is_primary
    _delete_image_file(img.image_url)
    db.session.delete(img)
    db.session.commit()
    if was_primary:
        next_img = ProductImage.query.filter_by(product_id=product_id).first()
        if next_img:
            next_img.is_primary = True
            db.session.commit()
    return "", 204


@inventory_bp.patch("/products/<int:product_id>/images/<int:image_id>")
@jwt_required()
@require_permission("inventory:write")
def update_product_image(product_id, image_id):
    img = ProductImage.query.filter_by(id=image_id, product_id=product_id).first_or_404()
    data = request.get_json() or {}
    if data.get("is_primary"):
        ProductImage.query.filter_by(product_id=product_id).update({"is_primary": False})
        img.is_primary = True
    if "alt_text" in data:
        img.alt_text = data["alt_text"]
    db.session.commit()
    return jsonify({"id": img.id, "image_url": img.image_url, "is_primary": img.is_primary, "alt_text": img.alt_text})


# ---- Product variants ----
@inventory_bp.post("/products/<int:product_id>/variants")
@jwt_required()
@require_permission("inventory:write")
def create_variant(product_id):
    Product.query.get_or_404(product_id)
    data = request.get_json() or {}
    sku = (data.get("sku") or "").strip()
    if not sku:
        return jsonify({"error": "sku required"}), 400
    if ProductVariant.query.filter_by(sku=sku).first():
        return jsonify({"error": "sku already exists"}), 409
    v = ProductVariant(
        product_id=product_id,
        sku=sku,
        barcode=data.get("barcode"),
        color=data.get("color"),
        size=data.get("size"),
        unit_price=data.get("unit_price"),
        low_stock_threshold=data.get("low_stock_threshold"),
        active=data.get("active", True),
    )
    db.session.add(v)
    db.session.commit()
    return jsonify({"id": v.id, "sku": v.sku, "product_id": v.product_id}), 201


@inventory_bp.patch("/variants/<int:variant_id>")
@jwt_required()
@require_permission("inventory:write")
def update_variant(variant_id):
    v = ProductVariant.query.get_or_404(variant_id)
    data = request.get_json() or {}
    if "sku" in data and data["sku"]:
        v.sku = data["sku"][:64]
    if "barcode" in data:
        v.barcode = data["barcode"]
    if "color" in data:
        v.color = data["color"]
    if "size" in data:
        v.size = data["size"]
    if "unit_price" in data:
        v.unit_price = data["unit_price"]
    if "low_stock_threshold" in data:
        v.low_stock_threshold = data["low_stock_threshold"]
    if "active" in data:
        v.active = data["active"]
    db.session.commit()
    return jsonify({"id": v.id, "sku": v.sku})


# ---- Stock ----
@inventory_bp.get("/stock")
def get_stock():
    """GET ?variant_id=&warehouse_id= (variant_id required). Returns current stock."""
    variant_id = request.args.get("variant_id", type=int)
    warehouse_id = request.args.get("warehouse_id", type=int)
    if variant_id is None:
        return jsonify({"error": "variant_id required"}), 400
    qty = get_current_stock(variant_id, warehouse_id)
    return jsonify({"product_variant_id": variant_id, "warehouse_id": warehouse_id, "quantity": qty})


@inventory_bp.get("/low-stock")
@jwt_required()
@require_permission("inventory:read")
def low_stock():
    """GET /api/inventory/low-stock — variants where current stock < low_stock_threshold."""
    warehouse_id = request.args.get("warehouse_id", type=int)
    items = get_low_stock_variants(warehouse_id)
    return jsonify({"items": items})


@inventory_bp.post("/movements")
@jwt_required()
@require_permission("inventory:write")
def create_movement():
    data = request.get_json() or {}
    product_variant_id = data.get("product_variant_id")
    warehouse_id = data.get("warehouse_id")
    movement_type = (data.get("movement_type") or "").strip()
    quantity = data.get("quantity", 0)
    if not all([product_variant_id, warehouse_id, movement_type]):
        return jsonify({"error": "product_variant_id, warehouse_id, movement_type required"}), 400
    quantity = int(quantity)
    if quantity <= 0:
        return jsonify({"error": "quantity must be positive"}), 400
    ProductVariant.query.get_or_404(product_variant_id)
    Warehouse.query.get_or_404(warehouse_id)
    m = StockMovement(
        product_variant_id=product_variant_id,
        warehouse_id=warehouse_id,
        movement_type=movement_type,
        quantity=quantity,
        reference_type=data.get("reference_type"),
        reference_id=data.get("reference_id"),
        note=data.get("note"),
    )
    db.session.add(m)
    db.session.commit()
    return jsonify({"id": m.id, "product_variant_id": m.product_variant_id, "warehouse_id": m.warehouse_id, "movement_type": m.movement_type, "quantity": m.quantity}), 201


# ---- Suppliers ----
@inventory_bp.get("/suppliers")
def list_suppliers():
    items = Supplier.query.filter_by(active=True).all()
    return jsonify([{"id": s.id, "name": s.name, "phone": s.phone, "email": s.email, "city": s.city} for s in items])


@inventory_bp.post("/suppliers")
@jwt_required()
@require_permission("inventory:write")
def create_supplier():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name required"}), 400
    s = Supplier(
        name=name,
        phone=data.get("phone"),
        email=data.get("email"),
        address=data.get("address"),
        city=data.get("city"),
        active=data.get("active", True),
    )
    db.session.add(s)
    db.session.commit()
    return jsonify({"id": s.id, "name": s.name}), 201


# ---- Warehouses ----
@inventory_bp.get("/warehouses")
def list_warehouses():
    items = Warehouse.query.filter_by(active=True).all()
    return jsonify([{"id": w.id, "name": w.name, "code": w.code, "location": w.location} for w in items])


@inventory_bp.post("/warehouses")
@jwt_required()
@require_permission("inventory:write")
def create_warehouse():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    code = (data.get("code") or "").strip()
    if not name or not code:
        return jsonify({"error": "name and code required"}), 400
    if Warehouse.query.filter_by(code=code).first():
        return jsonify({"error": "code already exists"}), 409
    w = Warehouse(name=name, code=code, location=data.get("location"), active=True)
    db.session.add(w)
    db.session.commit()
    return jsonify({"id": w.id, "name": w.name, "code": w.code}), 201


# ---- Purchase orders ----
@inventory_bp.get("/purchase-orders")
@jwt_required()
@require_permission("inventory:read")
def list_purchase_orders():
    items = PurchaseOrder.query.order_by(PurchaseOrder.id.desc()).limit(100).all()
    return jsonify([{
        "id": po.id,
        "po_number": po.po_number,
        "supplier_id": po.supplier_id,
        "warehouse_id": po.warehouse_id,
        "status": po.status,
        "total_amount": float(po.total_amount) if po.total_amount else 0,
    } for po in items])


@inventory_bp.post("/purchase-orders")
@jwt_required()
@require_permission("purchase:approve")
def create_purchase_order():
    data = request.get_json() or {}
    supplier_id = data.get("supplier_id")
    warehouse_id = data.get("warehouse_id")
    po_number = (data.get("po_number") or "").strip()
    if not supplier_id or not po_number:
        return jsonify({"error": "supplier_id and po_number required"}), 400
    if PurchaseOrder.query.filter_by(po_number=po_number).first():
        return jsonify({"error": "po_number already exists"}), 409
    po = PurchaseOrder(
        supplier_id=supplier_id,
        warehouse_id=warehouse_id,
        po_number=po_number,
        status=data.get("status", "draft"),
        total_amount=data.get("total_amount", 0),
        notes=data.get("notes"),
    )
    db.session.add(po)
    db.session.flush()
    for line in data.get("items", []):
        variant_id = line.get("product_variant_id")
        qty = line.get("quantity", 0)
        unit_cost = line.get("unit_cost", 0)
        if variant_id and qty and unit_cost is not None:
            db.session.add(PurchaseOrderItem(
                purchase_order_id=po.id,
                product_variant_id=variant_id,
                quantity=int(qty),
                unit_cost=unit_cost,
                line_total=int(qty) * float(unit_cost),
            ))
    db.session.commit()
    return jsonify({"id": po.id, "po_number": po.po_number}), 201


@inventory_bp.post("/purchase-orders/<int:po_id>/receive")
@jwt_required()
@require_permission("inventory:write")
def receive_purchase_order(po_id):
    """Goods receipt: create IN stock_movements for each PO line, update PO status."""
    po = PurchaseOrder.query.get_or_404(po_id)
    if not po.warehouse_id:
        return jsonify({"error": "PO has no warehouse"}), 400
    for item in po.purchase_order_items:
        m = StockMovement(
            product_variant_id=item.product_variant_id,
            warehouse_id=po.warehouse_id,
            movement_type="PURCHASE",
            quantity=item.quantity,
            reference_type="purchase_order",
            reference_id=po.id,
        )
        db.session.add(m)
    po.status = "received"
    db.session.commit()
    return jsonify({"message": "Received", "purchase_order_id": po.id})


@inventory_bp.get("/")
def index():
    return jsonify({"module": "inventory", "endpoints": ["/products", "/stock", "/low-stock", "/suppliers", "/warehouses", "/purchase-orders"]})
