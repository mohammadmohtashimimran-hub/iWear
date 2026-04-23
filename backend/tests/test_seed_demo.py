"""Smoke test for ``seed_demo_products``.

Runs the full seed pipeline on a fresh in-memory SQLite database and
asserts that the resulting demo dataset is rich enough for the
storefront to render meaningfully:

- multiple demo products
- every demo product has at least two colour variants
- every demo product has at least one (primary) image
- the Frames category has the full set of addon groups
  (Frame Glass, Lens Options, Sight) and the Sunglasses category
  has UV Tint
- the ``Sight`` addon group is marked ``requires_image=True``
  so the UI surfaces the prescription capture toggle
"""
from app.extensions import db
from app.models import (
    Product,
    ProductVariant,
    ProductImage,
    ProductCategory,
    Addon,
)
from app.seed import run_seed


def test_run_seed_populates_rich_demo_data(db):
    run_seed()
    db.session.commit()

    products = Product.query.filter_by(active=True).all()
    assert len(products) >= 8, f"expected at least 8 demo products, got {len(products)}"

    for p in products:
        variants = list(p.product_variants)
        assert len(variants) >= 2, f"{p.slug} should have at least 2 colour variants"
        # Every variant has a non-null color and sku
        for v in variants:
            assert v.color, f"{p.slug} variant missing color"
            assert v.sku, f"{p.slug} variant missing sku"

        images = list(p.product_images)
        assert len(images) >= 1, f"{p.slug} should have at least 1 image"
        assert any(img.is_primary for img in images), f"{p.slug} should have a primary image"
        # The placeholder SVG route URL pattern is stable, so lock it in.
        for img in images:
            assert img.image_url.startswith("/api/sales/placeholder/")
            assert img.image_url.endswith(".svg")


def test_seeded_addon_groups_cover_both_categories(db):
    run_seed()
    db.session.commit()

    frames = ProductCategory.query.filter_by(name="Frames").first()
    sun = ProductCategory.query.filter_by(name="Sunglasses").first()
    assert frames and sun

    frames_groups = {a.name for a in Addon.query.filter_by(category_id=frames.id).all()}
    assert {"Frame Glass", "Lens Options", "Sight"}.issubset(frames_groups), frames_groups

    sun_groups = {a.name for a in Addon.query.filter_by(category_id=sun.id).all()}
    assert "UV Tint" in sun_groups, sun_groups

    sight = Addon.query.filter_by(name="Sight", category_id=frames.id).first()
    assert sight is not None
    assert sight.requires_image is True, "Sight addon must require image/prescription"
    assert len(list(sight.options)) >= 2


def test_seed_is_idempotent(db):
    run_seed()
    db.session.commit()
    first_count = Product.query.count()
    first_variants = ProductVariant.query.count()
    first_images = ProductImage.query.count()

    run_seed()
    db.session.commit()
    assert Product.query.count() == first_count
    assert ProductVariant.query.count() == first_variants
    assert ProductImage.query.count() == first_images


def test_placeholder_svg_route_renders(client, db):
    run_seed()
    db.session.commit()
    r = client.get("/api/sales/placeholder/aviator-classic-front.svg")
    assert r.status_code == 200
    assert r.mimetype == "image/svg+xml"
    body = r.get_data(as_text=True)
    assert "<svg" in body
    assert "Aviator Classic Front" in body
