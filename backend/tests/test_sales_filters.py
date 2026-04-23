"""Sales /api/sales/products listing — filter & sort coverage."""
from app.extensions import db
from app.models import Product, ProductCategory, ProductBrand


def _seed_products():
    cat_a = ProductCategory(name="Frames")
    cat_b = ProductCategory(name="Sunglasses")
    db.session.add_all([cat_a, cat_b])
    brand = ProductBrand(name="iWear")
    db.session.add(brand)
    db.session.flush()
    db.session.add_all([
        Product(name="Cheap", slug="cheap", price=50, quantity=10,
                category_id=cat_a.id, brand_id=brand.id, active=True),
        Product(name="Mid", slug="mid", price=120, quantity=5,
                category_id=cat_a.id, brand_id=brand.id, active=True),
        Product(name="Expensive", slug="expensive", price=300, quantity=2,
                category_id=cat_b.id, brand_id=brand.id, active=True),
        Product(name="Hidden", slug="hidden", price=10, quantity=0,
                category_id=cat_a.id, brand_id=brand.id, active=False),
    ])
    db.session.commit()
    return cat_a, cat_b


def test_list_products_returns_only_active(client, db):
    _seed_products()
    r = client.get("/api/sales/products")
    assert r.status_code == 200
    data = r.get_json()
    names = [p["name"] for p in data["items"]]
    assert "Hidden" not in names
    assert data["total"] == 3


def test_list_products_filters_by_price_range(client, db):
    _seed_products()
    r = client.get("/api/sales/products?min_price=80&max_price=200")
    data = r.get_json()
    names = [p["name"] for p in data["items"]]
    assert names == ["Mid"]


def test_list_products_filters_by_category(client, db):
    cat_a, cat_b = _seed_products()
    r = client.get(f"/api/sales/products?category_id={cat_b.id}")
    data = r.get_json()
    assert [p["name"] for p in data["items"]] == ["Expensive"]


def test_list_products_sort_price_asc_and_desc(client, db):
    _seed_products()
    r = client.get("/api/sales/products?sort=price_asc")
    asc = [p["name"] for p in r.get_json()["items"]]
    assert asc == ["Cheap", "Mid", "Expensive"]
    r = client.get("/api/sales/products?sort=price_desc")
    desc = [p["name"] for p in r.get_json()["items"]]
    assert desc == ["Expensive", "Mid", "Cheap"]


def test_list_products_search_substring(client, db):
    _seed_products()
    r = client.get("/api/sales/products?search=mid")
    data = r.get_json()
    assert [p["name"] for p in data["items"]] == ["Mid"]
