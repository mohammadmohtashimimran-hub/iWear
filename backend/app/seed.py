"""Seed data for fresh install — roles, permissions, order statuses, payment types, voucher types, store settings, optional CoA and eyewear masters."""
import click
from flask import current_app
from app.extensions import db
from app.models import (
    StoreSetting,
    Role,
    Permission,
    RolePermission,
    User,
    OrderStatus,
    PaymentType,
    VoucherType,
    ChartOfAccount,
    FrameType,
    LensType,
    LensIndex,
    LensCoating,
    ProductCategory,
    ProductBrand,
    ProductType,
    Product,
    Addon,
    AddonOption,
    ProductVariant,
    ProductImage,
    ReportingIntent,
    IntentKeyword,
    PredefinedQuery,
)
from app.models.users import user_roles


def _get_or_create(model, unique_attr, defaults, **lookup):
    """Get existing or create. lookup is e.g. name='Admin'. unique_attr is the attribute name for uniqueness."""
    value = lookup.get(unique_attr)
    if value is None:
        return None
    instance = model.query.filter_by(**{unique_attr: value}).first()
    if instance:
        return instance
    instance = model(**{**defaults, **lookup})
    db.session.add(instance)
    return instance


def seed_store_settings():
    defaults = [
        ("store_name", "iWear", "Store display name"),
        ("store_logo_url", "", "Logo URL for header"),
        ("currency_code", "PKR", "Currency code"),
        ("support_email", "", "Support contact email"),
        ("footer_text", "", "Footer text"),
        ("meta_title", "iWear Store", "Default page title"),
        ("timezone", "Asia/Karachi", "Timezone"),
    ]
    for key, value, desc in defaults:
        if StoreSetting.query.filter_by(key=key).first() is None:
            db.session.add(StoreSetting(key=key, value=value, description=desc))


def seed_roles():
    for name in ("Super Admin", "Admin", "Finance Manager", "Inventory Manager", "Sales Staff", "Viewer"):
        if Role.query.filter_by(name=name).first() is None:
            db.session.add(Role(name=name))


def seed_permissions():
    perms = [
        ("Create/Edit Products", "inventory:write", "Create or edit products and variants"),
        ("Approve Purchases", "purchase:approve", "Approve purchase orders"),
        ("Post Vouchers", "finance:post", "Create and post vouchers"),
        ("View Financial Reports", "finance:read", "View financial reports"),
        ("Access AI Reports", "ai:query", "Use AI Business Insights Assistant"),
        ("Manage Users", "users:manage", "Create/edit users and roles"),
        ("View Inventory", "inventory:read", "View products and stock"),
        ("Manage Orders", "sales:write", "Create and manage orders"),
        ("View Orders", "sales:read", "View orders and sales"),
    ]
    for name, code, desc in perms:
        if Permission.query.filter_by(code=code).first() is None:
            db.session.add(Permission(name=name, code=code, description=desc))


def seed_role_permissions():
    db.session.flush()  # get IDs
    role_map = {r.name: r.id for r in Role.query.all()}
    perm_map = {p.code: p.id for p in Permission.query.all()}
    # Super Admin gets all
    super_admin_id = role_map.get("Super Admin")
    if super_admin_id:
        for pid in perm_map.values():
            if RolePermission.query.filter_by(role_id=super_admin_id, permission_id=pid).first() is None:
                db.session.add(RolePermission(role_id=super_admin_id, permission_id=pid))
    # Admin: same as super admin for simplicity (or subset)
    admin_id = role_map.get("Admin")
    if admin_id:
        for pid in perm_map.values():
            if RolePermission.query.filter_by(role_id=admin_id, permission_id=pid).first() is None:
                db.session.add(RolePermission(role_id=admin_id, permission_id=pid))
    # Finance Manager: finance + view
    finance_id = role_map.get("Finance Manager")
    if finance_id:
        for code in ("finance:post", "finance:read", "inventory:read", "sales:read"):
            pid = perm_map.get(code)
            if pid and RolePermission.query.filter_by(role_id=finance_id, permission_id=pid).first() is None:
                db.session.add(RolePermission(role_id=finance_id, permission_id=pid))
    # Inventory Manager: inventory + purchase
    inv_id = role_map.get("Inventory Manager")
    if inv_id:
        for code in ("inventory:write", "inventory:read", "purchase:approve"):
            pid = perm_map.get(code)
            if pid and RolePermission.query.filter_by(role_id=inv_id, permission_id=pid).first() is None:
                db.session.add(RolePermission(role_id=inv_id, permission_id=pid))
    # Sales Staff: sales + inventory read
    sales_id = role_map.get("Sales Staff")
    if sales_id:
        for code in ("sales:write", "sales:read", "inventory:read"):
            pid = perm_map.get(code)
            if pid and RolePermission.query.filter_by(role_id=sales_id, permission_id=pid).first() is None:
                db.session.add(RolePermission(role_id=sales_id, permission_id=pid))
    # Viewer: read only
    viewer_id = role_map.get("Viewer")
    if viewer_id:
        for code in ("inventory:read", "sales:read", "finance:read", "ai:query"):
            pid = perm_map.get(code)
            if pid and RolePermission.query.filter_by(role_id=viewer_id, permission_id=pid).first() is None:
                db.session.add(RolePermission(role_id=viewer_id, permission_id=pid))


def seed_order_statuses():
    for name, code, desc in [
        ("Pending", "pending", "Order placed, not yet confirmed"),
        ("Confirmed", "confirmed", "Order confirmed"),
        ("Shipped", "shipped", "Order shipped"),
        ("Delivered", "delivered", "Delivered / COD collected"),
        ("Cancelled", "cancelled", "Order cancelled"),
    ]:
        if OrderStatus.query.filter_by(code=code).first() is None:
            db.session.add(OrderStatus(name=name, code=code, description=desc))


def seed_payment_types():
    for name, code, desc in [
        ("Cash", "cash", "Cash payment"),
        ("Cash on Delivery", "cod", "Pay on delivery (COD)"),
        ("Card", "card", "Card payment"),
    ]:
        if PaymentType.query.filter_by(code=code).first() is None:
            db.session.add(PaymentType(name=name, code=code, description=desc))


def seed_voucher_types():
    for name, code, desc in [
        ("Sales Voucher", "SV", "Sales entry"),
        ("Purchase Voucher", "PV", "Purchase entry"),
        ("Journal Voucher", "JV", "Manual journal"),
        ("Payment Voucher", "PayV", "Payment out"),
        ("Receipt Voucher", "RV", "Receipt in"),
        ("Expense Voucher", "EV", "Expense entry"),
        ("Sales Return Voucher", "SRV", "Sales return"),
        ("Purchase Return Voucher", "PRV", "Purchase return"),
    ]:
        if VoucherType.query.filter_by(code=code).first() is None:
            db.session.add(VoucherType(name=name, code=code, description=desc))


def seed_chart_of_accounts():
    if ChartOfAccount.query.first() is not None:
        return
    accounts = [
        ("1100", "Cash in Hand", "asset"),
        ("1110", "Cash at Bank", "asset"),
        ("1130", "Inventory Asset (Frames)", "asset"),
        ("1140", "Inventory Asset (Lenses)", "asset"),
        ("1150", "Inventory Asset (Accessories)", "asset"),
        ("2100", "Supplier Payables", "liability"),
        ("3100", "Owner Capital", "equity"),
        ("4100", "Sales – Frames", "revenue"),
        ("4110", "Sales – Lenses", "revenue"),
        ("4120", "Sales – Accessories", "revenue"),
        ("4200", "Sales Discounts", "revenue"),
        ("4300", "Sales Returns", "revenue"),
        ("5100", "COGS – Frames", "expense"),
        ("5110", "COGS – Lenses", "expense"),
        ("5120", "COGS – Accessories", "expense"),
        ("6200", "Electricity", "expense"),
        ("6590", "Miscellaneous Expense", "expense"),
    ]
    for code, name, acc_type in accounts:
        db.session.add(ChartOfAccount(account_code=code, account_name=name, account_type=acc_type, is_active=True))


def _ai_intent_templates():
    """Return the SQL templates for AI reporting intents, dialect-aware.

    The iWear schema uses ``first_name`` / ``last_name`` on customers,
    a ``status_id`` FK on orders (not a string status column), and
    timestamps as generic ``DATETIME``. Date functions differ between
    SQLite (``DATE(col)``, ``strftime('%m', col)``) and PostgreSQL
    (``col::date``, ``EXTRACT(MONTH FROM col)``), so both variants live
    here and we select by ``db.engine.dialect.name`` at seed time.
    """
    is_sqlite = db.engine.dialect.name == "sqlite"

    # Date/time helpers
    if is_sqlite:
        today_cmp = "DATE(created_at) = DATE('{{today}}')"
        month_year_cmp = (
            "CAST(strftime('%m', created_at) AS INTEGER) = {{month}} "
            "AND CAST(strftime('%Y', created_at) AS INTEGER) = {{year}}"
        )
    else:
        today_cmp = "created_at::date = DATE '{{today}}'"
        month_year_cmp = (
            "EXTRACT(MONTH FROM created_at) = {{month}} "
            "AND EXTRACT(YEAR FROM created_at) = {{year}}"
        )

    return [
        (
            "Daily Sales", "daily_sales",
            ["sales today", "today sales", "daily sales", "sales report"],
            f"SELECT COUNT(*) AS order_count, "
            f"COALESCE(SUM(grand_total), 0) AS total_sales "
            f"FROM orders WHERE {today_cmp}",
        ),
        (
            "Monthly Profit", "monthly_profit",
            ["profit", "monthly profit", "net profit", "revenue this month",
             "monthly revenue", "how much revenue", "income this month",
             "sales this month", "month earnings", "profit this month"],
            f"SELECT COALESCE(SUM(grand_total), 0) AS revenue "
            f"FROM orders WHERE {month_year_cmp}",
        ),
        (
            "Best Selling Products", "best_selling",
            ["best selling", "top products", "best products", "top sellers",
             "most sold products", "which products sell most",
             "top selling items", "best sellers", "popular products"],
            "SELECT p.name AS product_name, SUM(oi.quantity) AS total_qty "
            "FROM order_items oi "
            "JOIN product_variants pv ON pv.id = oi.product_variant_id "
            "JOIN products p ON p.id = pv.product_id "
            "GROUP BY p.id, p.name "
            "ORDER BY total_qty DESC LIMIT 10",
        ),
        (
            "Low Stock", "low_stock",
            ["low stock", "out of stock", "stock alert", "running low",
             "needs restocking", "restocking", "items need restock",
             "products running low", "stock running out", "reorder"],
            "SELECT pv.sku, p.name, pv.low_stock_threshold "
            "FROM product_variants pv "
            "JOIN products p ON p.id = pv.product_id "
            "WHERE pv.low_stock_threshold IS NOT NULL AND pv.active = 1",
        ),
        (
            "Top Customers", "top_customers",
            ["top customers", "best customers", "biggest customers",
             "customer ranking", "who buys most", "highest spending customers",
             "top buyers", "loyal customers", "vip customers"],
            "SELECT c.first_name || ' ' || COALESCE(c.last_name, '') AS customer_name, "
            "COUNT(o.id) AS order_count, "
            "COALESCE(SUM(o.grand_total), 0) AS total_spent "
            "FROM orders o JOIN customers c ON c.id = o.customer_id "
            "GROUP BY c.id, c.first_name, c.last_name "
            "ORDER BY total_spent DESC LIMIT 10",
        ),
        (
            "Pending Orders", "pending_orders",
            ["pending orders", "open orders", "unfulfilled orders",
             "orders to ship", "awaiting fulfilment", "orders awaiting",
             "orders not shipped", "unshipped orders", "pending shipments"],
            "SELECT o.order_number, "
            "c.first_name || ' ' || COALESCE(c.last_name, '') AS customer_name, "
            "o.grand_total, os.name AS status "
            "FROM orders o "
            "JOIN customers c ON c.id = o.customer_id "
            "JOIN order_statuses os ON os.id = o.status_id "
            "WHERE LOWER(os.code) IN ('pending', 'confirmed') "
            "ORDER BY o.id DESC LIMIT 25",
        ),
        (
            "Sales by Category", "sales_by_category",
            ["sales by category", "category sales", "category performance",
             "revenue by category", "category breakdown",
             "sales per category", "how are categories doing"],
            "SELECT pc.name AS category, "
            "COUNT(DISTINCT o.id) AS orders, "
            "COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS revenue "
            "FROM order_items oi "
            "JOIN product_variants pv ON pv.id = oi.product_variant_id "
            "JOIN products p ON p.id = pv.product_id "
            "JOIN product_categories pc ON pc.id = p.category_id "
            "JOIN orders o ON o.id = oi.order_id "
            "GROUP BY pc.id, pc.name "
            "ORDER BY revenue DESC",
        ),
        (
            "Average Order Value", "average_order_value",
            ["average order value", "aov", "average basket", "average sale",
             "basket size", "average spend per order", "typical order value",
             "mean order value"],
            "SELECT COUNT(*) AS order_count, "
            "ROUND(COALESCE(AVG(grand_total), 0), 2) AS avg_order_value "
            "FROM orders",
        ),
        (
            "New Customers This Month", "new_customers_month",
            ["new customers", "new customers this month", "customer signups",
             "new signups", "fresh customers", "new registrations",
             "new user signups"],
            f"SELECT COUNT(*) AS new_customer_count "
            f"FROM customers WHERE {month_year_cmp}",
        ),
        (
            "Slow Moving Stock", "slow_moving_stock",
            ["slow moving stock", "slow stock", "dead stock",
             "products not selling", "unsold products", "not selling",
             "stagnant inventory", "non moving products"],
            "SELECT p.name AS product_name, p.quantity AS on_hand "
            "FROM products p "
            "WHERE p.active = 1 AND p.id NOT IN ("
            "SELECT DISTINCT pv.product_id FROM product_variants pv "
            "JOIN order_items oi ON oi.product_variant_id = pv.id"
            ") ORDER BY p.id LIMIT 25",
        ),
    ]


def seed_ai_intents():
    """Reporting intents, keywords, and predefined queries for AI assistant.

    Upserts the SQL template on every run so fixes to the SQL roll out
    on the next ``flask seed`` without needing a manual row delete.
    """
    for name, code, keywords, sql_template in _ai_intent_templates():
        intent = ReportingIntent.query.filter_by(code=code).first()
        if not intent:
            intent = ReportingIntent(name=name, code=code)
            db.session.add(intent)
            db.session.flush()
        for kw in keywords:
            if not IntentKeyword.query.filter_by(reporting_intent_id=intent.id, keyword=kw).first():
                db.session.add(IntentKeyword(reporting_intent_id=intent.id, keyword=kw))
        existing = PredefinedQuery.query.filter_by(reporting_intent_id=intent.id).first()
        if existing:
            # Upsert: update the template so re-running seed rolls out SQL fixes.
            existing.sql_template = sql_template
            existing.active = True
        else:
            db.session.add(PredefinedQuery(
                reporting_intent_id=intent.id,
                query_name=code,
                sql_template=sql_template,
                active=True,
            ))


def seed_catalog_masters():
    """Categories, brands, types for product dropdowns."""
    for name in ("Frames", "Sunglasses", "Lenses", "Accessories"):
        if ProductCategory.query.filter_by(name=name).first() is None:
            db.session.add(ProductCategory(name=name))
    for name in ("Ray-Ban", "Oakley", "Titan", "iWear House"):
        if ProductBrand.query.filter_by(name=name).first() is None:
            db.session.add(ProductBrand(name=name))
    for name in ("Optical", "Sunglasses", "Contact Lenses"):
        if ProductType.query.filter_by(name=name).first() is None:
            db.session.add(ProductType(name=name))


def seed_admin_user():
    """Create default admin user for first login (change password in production)."""
    import os
    from app.extensions import bcrypt
    email = (os.environ.get("ADMIN_EMAIL") or "admin@iwear.local").strip().lower()
    password = os.environ.get("ADMIN_PASSWORD") or "Admin123!"
    if User.query.filter_by(email=email).first():
        return
    admin_role = Role.query.filter_by(name="Admin").first()
    if not admin_role:
        return
    user = User(
        email=email,
        password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
    )
    db.session.add(user)
    db.session.flush()
    db.session.execute(user_roles.insert().values(user_id=user.id, role_id=admin_role.id))


def seed_eyewear_masters():
    for name in ("Full Frame", "Half Frame", "Rimless", "Aviator"):
        if FrameType.query.filter_by(name=name).first() is None:
            db.session.add(FrameType(name=name))
    for name in ("Single Vision", "Bifocal", "Progressive", "Reading"):
        if LensType.query.filter_by(name=name).first() is None:
            db.session.add(LensType(name=name))
    for name, val in [("1.50", 1.50), ("1.60", 1.60), ("1.67", 1.67), ("1.74", 1.74)]:
        if LensIndex.query.filter_by(name=name).first() is None:
            db.session.add(LensIndex(name=name, value=val))
    for name in ("Anti-Reflective", "Blue Cut", "UV Protection", "Scratch Resistant"):
        if LensCoating.query.filter_by(name=name).first() is None:
            db.session.add(LensCoating(name=name))


def _seed_addon_groups(frames_cat, sun_cat):
    """Seed a rich set of addon groups so the storefront has something to
    configure on demo frames.

    - Frame Glass (Frames): Screen Glass / Transition Glass / Polarised / Standard
    - Lens Options (Frames): Single Vision / Bifocal / Progressive / Blue Light / Photochromic
    - Sight (Frames): prescription capture — ``requires_image=True`` so the
      UI surfaces the "Upload Image or Enter Values" tab toggle
    - UV Tint (Sunglasses): Grey / Brown / Mirrored / Gradient

    Idempotent: skips any addon group whose (name, category_id) pair
    already exists, so manual additions on top are preserved.
    """
    PKR_RATE = 280  # approximate USD → PKR conversion for demo

    def add_group(name, cat, description, options, requires_image=False, is_required=False):
        if not cat:
            return
        existing = Addon.query.filter_by(name=name, category_id=cat.id).first()
        if existing:
            return
        group = Addon(
            name=name,
            description=description,
            price=0,
            category_id=cat.id,
            is_required=is_required,
            requires_image=requires_image,
            active=True,
        )
        db.session.add(group)
        db.session.flush()
        for opt_name, opt_desc, opt_price in options:
            db.session.add(AddonOption(
                addon_id=group.id, name=opt_name,
                description=opt_desc, price=opt_price,
                price_pkr=round(opt_price * PKR_RATE) if opt_price else None,
                active=True,
            ))

    add_group(
        "Frame Glass", frames_cat,
        "Choose the type of glass fitted into your frame.",
        [
            ("Standard Clear", "Plain clear optical glass, no tint.", 0),
            ("Screen Glass", "Blue light filter for long screen hours.", 25),
            ("Transition Glass", "Darkens in sunlight, clears indoors.", 60),
            ("Polarised Glass", "Cuts glare for driving and outdoors.", 45),
        ],
    )

    add_group(
        "Lens Options", frames_cat,
        "Choose your lens type for prescription frames.",
        [
            ("Single Vision", "Standard prescription lens for one focal distance.", 0),
            ("Bifocal", "Two focal areas — distance and reading.", 35),
            ("Progressive", "Smooth gradient from distance to reading.", 75),
            ("Blue Light Filter", "Reduces digital eye strain from screens.", 25),
            ("Photochromic", "Lenses that darken automatically in sunlight.", 60),
        ],
    )

    add_group(
        "Sight", frames_cat,
        "Your prescription values — upload a photo or enter SPH/CYL/Axis manually.",
        [
            ("With Prescription", "Use my own prescription (upload or type values).", 0),
            ("Non-Prescription", "Plain lenses, no optical correction.", 0),
        ],
        requires_image=True,
    )

    add_group(
        "UV Tint", sun_cat,
        "Tint your lenses for a custom look.",
        [
            ("Grey", "Classic neutral tint.", 0),
            ("Brown", "Warm tint, great for driving.", 0),
            ("Mirrored Silver", "Reflective mirror finish.", 15),
            ("Gradient Smoke", "Darker top, lighter bottom.", 10),
        ],
    )


def _seed_variants_and_images(product, slug, base_price, colors):
    """Give a demo product multiple colour variants and placeholder images.

    Variants are tagged ``Black``, ``Tortoise``, ``Gold``, etc. so the product
    detail page's variant chip selector renders. Placeholder images are
    served by the ``/api/sales/placeholder/<slug>.svg`` route so no binary
    assets are required in the repo.
    """
    PKR_RATE = 280
    for idx, color in enumerate(colors):
        sku = f"IW-{slug.upper().replace('-', '')[:8]}-{color.upper()[:3]}"
        if ProductVariant.query.filter_by(sku=sku).first():
            continue
        usd = base_price + (idx * 5)
        db.session.add(ProductVariant(
            product_id=product.id,
            sku=sku,
            color=color,
            size="Wide",
            unit_price=usd,
            unit_price_pkr=round(usd * PKR_RATE),
            active=True,
            low_stock_threshold=3,
        ))
    # Primary image + one alt per colour
    if not ProductImage.query.filter_by(product_id=product.id).first():
        db.session.add(ProductImage(
            product_id=product.id,
            image_url=f"/api/sales/placeholder/{slug}-front.svg",
            alt_text=f"{product.name} — front",
            is_primary=True,
        ))
        for color in colors[:2]:
            db.session.add(ProductImage(
                product_id=product.id,
                image_url=f"/api/sales/placeholder/{slug}-{color.lower()}.svg",
                alt_text=f"{product.name} — {color}",
                is_primary=False,
            ))


def seed_demo_products():
    """Insert a realistic set of demo eyewear products + addons so the
    storefront has meaningful content out of the box.

    Each demo product gets:
    - A rich description mentioning frame size, gender, material
    - 2-3 colour variants (so the variant chip selector renders)
    - A primary + alt placeholder SVG image (served by the placeholder route)

    The category-level addon groups (Frame Glass, Lens Options, Sight,
    UV Tint) are seeded in ``_seed_addon_groups`` so they apply to every
    product in the category automatically.

    Idempotent: skips any product whose slug already exists.
    """
    frames_cat = ProductCategory.query.filter_by(name="Frames").first()
    sun_cat = ProductCategory.query.filter_by(name="Sunglasses").first()
    rb = ProductBrand.query.filter_by(name="Ray-Ban").first()
    oa = ProductBrand.query.filter_by(name="Oakley").first()
    iw = ProductBrand.query.filter_by(name="iWear House").first()
    optical_t = ProductType.query.filter_by(name="Optical").first()
    sun_t = ProductType.query.filter_by(name="Sunglasses").first()

    _seed_addon_groups(frames_cat, sun_cat)

    demo = [
        ("Aviator Classic", "aviator-classic", 129.00, frames_cat, rb, optical_t,
         "Timeless aviator silhouette with anti-glare lenses and adjustable nose pads.\n\n"
         "Dimension: 58-14-140  ·  Size: Wide  ·  Gender: Unisex  ·  Material: Metal",
         ["Black", "Gold", "Silver"]),
        ("Wayfarer Bold", "wayfarer-bold", 149.00, frames_cat, rb, optical_t,
         "Iconic wayfarer frame in matte acetate. Comfortable, lightweight, and durable.\n\n"
         "Dimension: 52-18-145  ·  Size: Medium  ·  Gender: Unisex  ·  Material: Acetate",
         ["Black", "Tortoise"]),
        ("Sport Shield Sun", "sport-shield-sun", 179.00, sun_cat, oa, sun_t,
         "Wraparound sport sunglasses with polarised UV400 lenses — built for the outdoors.\n\n"
         "Dimension: 64-12-130  ·  Size: Wide  ·  Gender: Male  ·  Material: TR90",
         ["Black", "Blue"]),
        ("Round Vintage", "round-vintage", 99.00, frames_cat, iw, optical_t,
         "Slim metal round frame inspired by 1960s eyewear. Pairs well with any face shape.\n\n"
         "Dimension: 49-22-145  ·  Size: Narrow  ·  Gender: Unisex  ·  Material: Titanium",
         ["Gold", "Silver", "Black"]),
        ("Cat-Eye Chic", "cat-eye-chic", 119.00, frames_cat, iw, optical_t,
         "Elegant cat-eye design with subtle gradient acetate temples.\n\n"
         "Dimension: 53-17-140  ·  Size: Medium  ·  Gender: Female  ·  Material: Acetate",
         ["Rose", "Tortoise", "Black"]),
        ("Rimless Pro", "rimless-pro", 199.00, frames_cat, iw, optical_t,
         "Featherlight rimless frame for an almost-invisible look. Perfect for daily wear.\n\n"
         "Dimension: 54-16-140  ·  Size: Medium  ·  Gender: Unisex  ·  Material: Titanium",
         ["Silver", "Gold"]),
        ("Blue Light Reader", "blue-light-reader", 79.00, frames_cat, iw, optical_t,
         "Computer reading glasses with built-in blue light filter for screen comfort.\n\n"
         "Dimension: 51-18-140  ·  Size: Medium  ·  Gender: Unisex  ·  Material: TR90",
         ["Black", "Tortoise", "Blue"]),
        ("Polarised Voyager", "polarised-voyager", 159.00, sun_cat, oa, sun_t,
         "Travel-ready polarised sunglasses with scratch-resistant lenses.\n\n"
         "Dimension: 58-15-135  ·  Size: Medium  ·  Gender: Unisex  ·  Material: Metal",
         ["Black", "Gold", "Green"]),
    ]
    for name, slug, price, cat, brand, ptype, desc, colors in demo:
        PKR_RATE = 280
        p = Product.query.filter_by(slug=slug).first()
        if p is None:
            p = Product(
                name=name,
                slug=slug,
                description=desc,
                price=price,
                price_pkr=round(price * PKR_RATE),
                quantity=25,
                category_id=cat.id if cat else None,
                brand_id=brand.id if brand else None,
                type_id=ptype.id if ptype else None,
                active=True,
            )
            db.session.add(p)
            db.session.flush()
        _seed_variants_and_images(p, slug, price, colors)


def run_seed():
    seed_store_settings()
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
    seed_admin_user()
    seed_demo_products()
    db.session.commit()


def register_commands(app):
    @app.cli.command("seed")
    def seed_cmd():
        """Seed roles, permissions, order statuses, payment types, voucher types, store settings, CoA, eyewear masters."""
        with app.app_context():
            run_seed()
            click.echo("Seed completed.")

    @app.cli.command("reset-demo")
    def reset_demo_cmd():
        """Wipe all demo products + addons + images and re-seed fresh demo data.

        Useful when experimenting with the storefront and you want a clean
        slate without dropping the whole database.
        """
        with app.app_context():
            # Delete demo-owned rows in the right order to avoid FK violations.
            from app.models import (
                CartItem,
                CartItemAddon,
                OrderItem,
            )
            # 1. Remove cart/order references to variants so the cascade
            #    delete on Product does not choke on in-flight rows.
            CartItemAddon.query.delete()
            CartItem.query.delete()
            OrderItem.query.delete()
            # 2. Remove addons, then products (cascade takes variants + images).
            AddonOption.query.delete()
            Addon.query.delete()
            Product.query.delete()
            db.session.commit()
            # 3. Re-seed fresh demo data.
            run_seed()
            click.echo("Demo data reset: products, variants, images and addons re-seeded.")
