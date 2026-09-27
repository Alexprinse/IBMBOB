"""CheckoutLab — payment service stub."""
from __future__ import annotations

from decimal import Decimal


class PaymentResult:
    def __init__(self, success: bool, transaction_id: str, amount_charged: Decimal) -> None:
        self.success = success
        self.transaction_id = transaction_id
        self.amount_charged = amount_charged


def charge(amount: Decimal) -> PaymentResult:
    """
    Stub payment processor. Accepts any non-negative amount.
    Raises ValueError for negative amounts (invariant guard at the boundary).
    """
    if amount < Decimal("0.00"):
        raise ValueError(f"Payment amount must be >= 0, got {amount}")
    return PaymentResult(
        success=True,
        transaction_id=f"txn-stub-{int(amount * 100):010d}",
        amount_charged=amount,
    )
