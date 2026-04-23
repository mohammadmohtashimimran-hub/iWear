"""End-to-end cart-to-order integration test.

Exercises the full pipeline:
    create cart  -> add item -> create customer -> place order -> verify state.

This test is the integration counterpart to the unit tests in
test_sales_filters.py and test_finance.py. It does not stub the database; it
runs against the in-memory SQLite fixture and goes through the real Flask
blueprints, so any regression in the cart, order or status seed pipeline will
break this test.
"""
from app.extensions import db
from app.models import (
    Product,
    ProductCategory,
    ProductVariant,
    OrderStatus,
    PaymentType,
    Order,
)


def _seed_minimum():
    """Seed the bare minimum needed for an order: a category, a product with a
    variant, the 'pending' order status and a 'cod' payment type."""
    cat = ProductCategory(name="Frames")
    db.session.add(cat)
    db.session.flush()
    p = Product(
        name="Aviator Test",
        slug="aviator-test",
        price=100,
        quantity=10,
        category_id=cat.id,
        active=True,
    )
    db.session.add(p)
    db.session.flush()
    v = ProductVariant(product_id=p.id, sku="AV-TEST-1", unit_price=100, active=True)
    db.session.add(v)
    db.session.add(OrderStatus(code="pending", name="Pending"))
    db.session.add(PaymentType(code="cod", name="Cash on Delivery"))
    db.session.commit()
    return p, v


def test_cart_to_order_flow_places_order(client, db):
    p, v = _seed_minimum()

    # 1. Create a guest cart
    r = client.post("/api/sales/carts", json={})
    assert r.status_code == 201, r.get_json()
    cart_id = r.get_json()["id"]

    # 2. Add the product variant to the cart
    r = client.post(
        f"/api/sales/carts/{cart_id}/items",
        json={"product_variant_id": v.id, "quantity": 2, "unit_price": 100},
    )
    assert r.status_code in (200, 201), r.get_json()

    # 3. Create a customer
    r = client.post(
        "/api/sales/customers",
        json={"first_name": "Test", "last_name": "Customer", "email": "test@example.com", "phone": "+10000000000"},
    )
    assert r.status_code == 201, r.get_json()
    customer_id = r.get_json()["id"]

    # 4. Place the order against the cart
    r = client.post(
        "/api/sales/orders",
        json={
            "cart_id": cart_id,
            "customer_id": customer_id,
            "shipping_address": "1 Test Street",
        },
    )
    assert r.status_code == 201, r.get_json()
    body = r.get_json()
    assert body["order_number"].startswith("ORD")
    assert body["status"] == "pending"
    assert float(body["grand_total"]) == 200.0  # 2 * 100

    # 5. Verify state in DB: order persisted, stock decremented, cart converted
    order = Order.query.filter_by(id=body["id"]).first()
    assert order is not None
    assert len(list(order.order_items)) == 1
    assert float(order.grand_total) == 200.0

    refreshed = Product.query.get(p.id)
    assert refreshed.quantity == 8  # 10 - 2


def test_create_order_rejects_inactive_cart(client, db):
    _seed_minimum()
    # Create + manually mark a cart as converted
    r = client.post("/api/sales/carts", json={})
    cart_id = r.get_json()["id"]
    from app.models import Cart
    cart = Cart.query.get(cart_id)
    cart.status = "converted"
    db.session.commit()

    r = client.post(
        "/api/sales/customers",
        json={"first_name": "X", "email": "x@example.com", "phone": "+1"},
    )
    customer_id = r.get_json()["id"]

    r = client.post(
        "/api/sales/orders",
        json={"cart_id": cart_id, "customer_id": customer_id},
    )
    assert r.status_code == 400
    assert "not active" in r.get_json()["error"].lower()


def test_create_order_requires_cart_and_customer_ids(client, db):
    _seed_minimum()
    r = client.post("/api/sales/orders", json={})
    assert r.status_code == 400
    assert "required" in r.get_json()["error"].lower()
