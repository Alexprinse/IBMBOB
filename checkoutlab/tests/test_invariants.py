"""Business invariant tests — these MUST all pass in the final VERIFIED state.

inv-01: Payment amount never negative.
inv-02: Coupon cannot be applied to empty cart.
inv-03: Coupon codes are case-insensitive.

NOTE: test_payment_never_negative_when_coupon_exceeds_subtotal is the
critical test that exposes the seeded defect. It will FAIL until the
floor guard is applied.
"""
from __future__ import annotations

from decimal import Decimal

import pytest

from checkoutlab.app.schemas import CheckoutRequest, OrderItemRequest
from checkoutlab.app.services.checkout import CheckoutError, process_checkout

# ── inv-01 ────────────────────────────────────────────────────────────────────

def test_payment_never_negative_when_coupon_exceeds_subtotal(
    db_session, product_50, coupon_large_fixed
):
    """
    inv-01: When a $75 coupon is applied to a $50 order, the total must be
    $0.00, NOT -$25.00.

    This test EXPOSES THE SEEDED DEFECT. It will fail until the fix:
        final_total = max(Decimal("0.00"), subtotal - discount_amount)
    is applied in checkoutlab/app/services/checkout.py.
    """
    req = CheckoutRequest(
        items=[OrderItemRequest(product_id=product_50.id, quantity=1)],
        coupon_code="BIGDISCOUNT",
    )
    result = process_checkout(db_session, req)
    assert result.total >= Decimal("0.00"), (
        f"inv-01 VIOLATED: payment total is {result.total} (negative). "
        "The floor guard max(0, subtotal - discount) is missing."
    )


def test_payment_never_negative_100pct_equivalent(db_session, product_50, db_engine):
    """
    inv-01 edge case: A fixed coupon exactly equal to the subtotal should
    produce total == $0.00, not raise an error.
    """
    from checkoutlab.app.models import Coupon, DiscountType

    exact_coupon = Coupon(
        code="EXACT",
        discount_type=DiscountType.FIXED,
        discount_value=Decimal("50.00"),
        is_active=True,
    )
    db_session.add(exact_coupon)
    db_session.commit()

    req = CheckoutRequest(
        items=[OrderItemRequest(product_id=product_50.id, quantity=1)],
        coupon_code="EXACT",
    )
    result = process_checkout(db_session, req)
    assert result.total == Decimal("0.00")


# ── inv-02 ────────────────────────────────────────────────────────────────────

def test_coupon_cannot_be_applied_to_empty_cart(db_session, coupon_10pct):
    """inv-02: An empty items list is rejected regardless of coupon presence."""
    with pytest.raises((CheckoutError, Exception)):
        req = CheckoutRequest(items=[], coupon_code="SAVE10")
        process_checkout(db_session, req)


# ── inv-03 ────────────────────────────────────────────────────────────────────

def test_coupon_lookup_uppercase(db_session, product_50, coupon_10pct):
    """inv-03: Uppercase code works."""
    req = CheckoutRequest(
        items=[OrderItemRequest(product_id=product_50.id, quantity=1)],
        coupon_code="SAVE10",
    )
    result = process_checkout(db_session, req)
    assert result.discount_applied > Decimal("0.00")


def test_coupon_lookup_lowercase(db_session, product_50, coupon_10pct):
    """inv-03: Lowercase code resolves to the same coupon."""
    req = CheckoutRequest(
        items=[OrderItemRequest(product_id=product_50.id, quantity=1)],
        coupon_code="save10",
    )
    result = process_checkout(db_session, req)
    assert result.discount_applied > Decimal("0.00")


def test_coupon_lookup_mixed_case(db_session, product_50, coupon_10pct):
    """inv-03: Mixed-case code resolves to the same coupon."""
    req = CheckoutRequest(
        items=[OrderItemRequest(product_id=product_50.id, quantity=1)],
        coupon_code="Save10",
    )
    result = process_checkout(db_session, req)
    assert result.discount_applied > Decimal("0.00")


# ── Phase 7 regression tests (repair rp-01) ───────────────────────────────────

def test_percentage_coupon_over_100_does_not_produce_negative_total(
    db_session, product_50, coupon_150pct
):
    """
    af-03 / inv-01 regression: A PERCENTAGE coupon with discount_value=150
    (i.e. 150%) applied to a $50 order must produce total >= $0.00.

    Before repair: _compute_discount() applied (150/100) * 50 = $75 discount,
    then subtotal - discount = -$25 (no floor guard).
    After repair: rate is clamped to min(150, 100)/100 = 1.0; discount = $50,
    floor guard clamps final_total to $0.00.
    """
    req = CheckoutRequest(
        items=[OrderItemRequest(product_id=product_50.id, quantity=1)],
        coupon_code="SUPER150",
    )
    result = process_checkout(db_session, req)
    assert result.total >= Decimal("0.00"), (
        f"inv-01 VIOLATED via PERCENTAGE path: total is {result.total}. "
        "The PERCENTAGE rate clamp and/or floor guard is missing."
    )
