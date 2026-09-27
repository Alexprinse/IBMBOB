"""CheckoutLab — checkout business logic.

Phase 7 repair applied (repair_id: rp-01):
  - af-01: Added floor guard so final_total cannot be negative.
  - af-02: Guarded by the same floor; negative amount never reaches charge().
  - af-03: _compute_discount() now clamps PERCENTAGE discount_value to 100
           so an over-100% coupon cannot exceed the subtotal on its own.
"""
from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from checkoutlab.app.models import Coupon, DiscountType, Order, OrderItem
from checkoutlab.app.schemas import CheckoutRequest, CheckoutResponse, OrderItemResponse
from checkoutlab.app.services import inventory as inventory_svc
from checkoutlab.app.services import payment as payment_svc


class CheckoutError(Exception):
    """Raised for business-rule violations during checkout."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


def _resolve_coupon(db: Session, code: str) -> Coupon:
    """Look up a coupon by code (case-insensitive). Raises CheckoutError on failure."""
    coupon = (
        db.query(Coupon)
        .filter(Coupon.code == code.upper())
        .first()
    )
    if coupon is None:
        raise CheckoutError("coupon_not_found")
    if not coupon.is_active:
        raise CheckoutError("coupon_not_found")
    if coupon.expires_at is not None:
        now = datetime.now(tz=UTC).replace(tzinfo=None)
        if coupon.expires_at < now:
            raise CheckoutError("coupon_expired")
    if coupon.max_uses is not None and coupon.use_count >= coupon.max_uses:
        raise CheckoutError("coupon_already_used")
    return coupon


def _compute_discount(coupon: Coupon, subtotal: Decimal) -> Decimal:
    """Return the discount amount for the given coupon and subtotal.

    Repair af-03: PERCENTAGE rate is clamped to 100 so discount_value > 100
    cannot produce a computed discount that exceeds the subtotal on its own.
    """
    if coupon.discount_type == DiscountType.PERCENTAGE:
        rate = min(coupon.discount_value, Decimal("100")) / Decimal("100")
        return rate * subtotal
    # FIXED
    return coupon.discount_value


def process_checkout(db: Session, request: CheckoutRequest) -> CheckoutResponse:
    """
    Process a checkout request.

    Steps:
    1. Validate items and compute subtotal.
    2. Resolve coupon if provided.
    3. Apply discount.
    4. Charge payment.
    5. Persist order.
    """
    if not request.items:
        raise CheckoutError("cart_empty")

    # ── 1. Validate products and compute subtotal ────────────────────────────
    subtotal = Decimal("0.00")
    resolved_items: list[dict] = []

    for item_req in request.items:
        product = inventory_svc.get_product(db, item_req.product_id)
        if product is None:
            raise CheckoutError(f"product_not_found:{item_req.product_id}")
        if product.stock < item_req.quantity:
            raise CheckoutError(f"insufficient_stock:{item_req.product_id}")
        line_total = product.price * item_req.quantity
        subtotal += line_total
        resolved_items.append(
            {
                "product": product,
                "quantity": item_req.quantity,
                "unit_price": product.price,
                "line_total": line_total,
            }
        )

    # ── 2. Resolve coupon ────────────────────────────────────────────────────
    coupon: Coupon | None = None
    discount_amount = Decimal("0.00")

    if request.coupon_code:
        coupon = _resolve_coupon(db, request.coupon_code)
        discount_amount = _compute_discount(coupon, subtotal)

    # ── 3. Apply discount ────────────────────────────────────────────────────
    # Repair af-01 / af-02: floor guard ensures payment amount is never negative.
    # When a FIXED coupon's discount_value exceeds the subtotal, the total is
    # clamped to Decimal("0.00") rather than going negative (inv-01).
    final_total = max(Decimal("0.00"), subtotal - discount_amount)

    # ── 4. Charge payment ────────────────────────────────────────────────────
    payment_svc.charge(final_total)

    # ── 5. Persist order ─────────────────────────────────────────────────────
    order = Order(
        subtotal=subtotal,
        discount_applied=discount_amount,
        total=final_total,
        coupon_id=coupon.id if coupon else None,
        status="completed",
    )
    db.add(order)
    db.flush()  # get order.id before adding items

    for ri in resolved_items:
        item = OrderItem(
            order_id=order.id,
            product_id=ri["product"].id,
            quantity=ri["quantity"],
            unit_price=ri["unit_price"],
        )
        db.add(item)
        # Reserve stock
        ri["product"].stock -= ri["quantity"]

    if coupon:
        coupon.use_count += 1

    db.commit()
    db.refresh(order)

    # ── Build response ───────────────────────────────────────────────────────
    item_responses = [
        OrderItemResponse(
            product_id=ri["product"].id,
            product_name=ri["product"].name,
            quantity=ri["quantity"],
            unit_price=ri["unit_price"],
            line_total=ri["line_total"],
        )
        for ri in resolved_items
    ]

    return CheckoutResponse(
        order_id=order.id,
        items=item_responses,
        subtotal=subtotal,
        discount_applied=discount_amount,
        total=final_total,
        coupon_code=request.coupon_code,
        status=order.status,
    )
