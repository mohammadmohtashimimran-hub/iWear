"""Inventory business logic: current stock from movements, low-stock list."""
from app.extensions import db
from app.models import StockMovement, ProductVariant, Warehouse


IN_TYPES = ("IN", "RECEIPT", "RETURN", "ADJUSTMENT_IN", "PURCHASE")


def get_current_stock(product_variant_id, warehouse_id=None):
    """Sum of stock_movements: IN types add, OUT types subtract. Optional warehouse filter."""
    base = db.session.query(StockMovement).filter(StockMovement.product_variant_id == product_variant_id)
    if warehouse_id is not None:
        base = base.filter(StockMovement.warehouse_id == warehouse_id)
    movements = base.all()
    total = 0
    for m in movements:
        if m.movement_type in IN_TYPES:
            total += m.quantity
        else:
            total -= m.quantity
    return total


def get_low_stock_variants(warehouse_id=None):
    """Return list of (product_variant, warehouse, current_qty, threshold) where current_qty < threshold and threshold is set."""
    variants = ProductVariant.query.filter(
        ProductVariant.low_stock_threshold.isnot(None),
        ProductVariant.active.is_(True),
    ).all()
    warehouse_ids = [w.id for w in Warehouse.query.filter_by(active=True).all()] if warehouse_id is None else [warehouse_id]
    result = []
    for v in variants:
        for wid in warehouse_ids:
            qty = get_current_stock(v.id, wid)
            if v.low_stock_threshold is not None and qty < v.low_stock_threshold:
                wh = Warehouse.query.get(wid)
                result.append({
                    "product_variant_id": v.id,
                    "sku": v.sku,
                    "product_id": v.product_id,
                    "warehouse_id": wid,
                    "warehouse_code": wh.code if wh else None,
                    "current_stock": qty,
                    "low_stock_threshold": v.low_stock_threshold,
                })
    return result
