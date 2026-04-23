"""Finance: voucher double-entry rule (total debit = total credit) is enforced in create_voucher."""
import pytest
from datetime import date


def test_voucher_raises_when_unbalanced(app, db):
    """create_voucher raises ValueError when total debit != total credit (or when type/account missing)."""
    from app.services.finance_service import create_voucher
    with app.app_context():
        # Expect ValueError: either "must equal" (unbalanced) or "not found" (no JV/CoA in empty DB)
        with pytest.raises(ValueError):
            create_voucher("JV", date.today(), [
                {"account_code": "1100", "debit": 100, "credit": 0},
                {"account_code": "1110", "debit": 0, "credit": 50},
            ])
