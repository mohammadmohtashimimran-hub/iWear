"""Inventory: stock calculation, low-stock (service logic)."""
from app.services.inventory_service import get_current_stock, get_low_stock_variants, IN_TYPES


def test_in_types_defined():
    assert "IN" in IN_TYPES
    assert "PURCHASE" in IN_TYPES
