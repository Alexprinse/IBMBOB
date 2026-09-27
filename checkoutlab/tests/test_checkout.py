"""Tests for checkout business logic (service layer, no HTTP)."""
from __future__ import annotations

from decimal import Decimal

import pytest

from checkoutlab.app.schemas import CheckoutRequest, OrderItemRequest
from checkoutlab.app.services.checkout import CheckoutError, process_checkout


def test_checkout_no_coupon(db_session, product_50):
    """Checkout without coupon: total equals subtotal."""
    req = CheckoutRequest(items=[OrderItemRequest(product_id=product_50.id, quantity=2)])
    result = process_checkout(db_session, req)
    assert result.subtotal == Decimal("100.00")
    assert result.discount_applied == Decimal("0.00")
    assert result.total == Decimal("100.00")
    assert result.status == "completed"


def test_checkout_percentage_coupon(db_session, product_50, coupon_10pct):
    """10% coupon on a $50 order: discount = $5, total = $45."""
    req = CheckoutRequest(
        items=[OrderItemRequest(product_id=product_50.id, quantity=1)],
        coupon_code="SAVE10",
    )
    result = process_checkout(db_session, req)
    assert result.subtotal == Decimal("50.00")
    assert result.discount_applied == Decimal("5.00")
    assert result.total == Decimal("45.00")


def test_checkout_fixed_coupon(db_session, product_50, coupon_fixed_5):
    """$5 fixed coupon on a $50 order: total = $45."""
    req = CheckoutRequest(
        items=[OrderItemRequest(product_id=product_50.id, quantity=1)],
        coupon_code="FIXED5",
    )
    result = process_checkout(db_session, req)
    assert result.subtotal == Decimal("50.00")
    assert result.discount_applied == Decimal("5.00")
    assert result.total == Decimal("45.00")


def test_coupon_not_found_raises(db_session, product_50):
    """Unknown coupon code raises CheckoutError with 'coupon_not_found'."""
    req = CheckoutRequest(
        items=[OrderItemRequest(product_id=product_50.id, quantity=1)],
        coupon_code="DOESNOTEXIST",
    )
    with pytest.raises(CheckoutError) as exc_info:
        process_checkout(db_session, req)
    assert exc_info.value.detail == "coupon_not_found"


def test_product_not_found_raises(db_session):
    """Non-existent product raises CheckoutError."""
    req = CheckoutRequest(items=[OrderItemRequest(product_id=99999, quantity=1)])
    with pytest.raises(CheckoutError) as exc_info:
        process_checkout(db_session, req)
    assert "product_not_found" in exc_info.value.detail


def test_insufficient_stock_raises(db_session, product_50):
    """Requesting more than available stock raises CheckoutError."""
    req = CheckoutRequest(
        items=[OrderItemRequest(product_id=product_50.id, quantity=999)]
    )
    with pytest.raises(CheckoutError) as exc_info:
        process_checkout(db_session, req)
    assert "insufficient_stock" in exc_info.value.detail


def test_coupon_use_count_incremented(db_session, product_50, coupon_10pct):
    """After a successful coupon redemption, use_count is incremented."""
    req = CheckoutRequest(
        items=[OrderItemRequest(product_id=product_50.id, quantity=1)],
        coupon_code="SAVE10",
    )
    process_checkout(db_session, req)
    db_session.refresh(coupon_10pct)
    assert coupon_10pct.use_count == 1


def test_stock_reduced_after_checkout(db_session, product_50):
    """Stock is reduced by the purchased quantity after checkout."""
    initial_stock = product_50.stock
    req = CheckoutRequest(items=[OrderItemRequest(product_id=product_50.id, quantity=3)])
    process_checkout(db_session, req)
    db_session.refresh(product_50)
    assert product_50.stock == initial_stock - 3


def test_case_insensitive_coupon_code(db_session, product_50, coupon_10pct):
    """Coupon codes are looked up case-insensitively (inv-03)."""
    req = CheckoutRequest(
        items=[OrderItemRequest(product_id=product_50.id, quantity=1)],
        coupon_code="save10",  # lowercase
    )
    result = process_checkout(db_session, req)
    assert result.discount_applied == Decimal("5.00")
