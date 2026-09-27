"""CheckoutLab — Pydantic request/response schemas."""
from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

# ── Request schemas ─────────────────────────────────────────────────────────

class OrderItemRequest(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)


class CheckoutRequest(BaseModel):
    items: list[OrderItemRequest] = Field(..., min_length=1)
    coupon_code: str | None = None


# ── Response schemas ─────────────────────────────────────────────────────────

class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal

    model_config = {"from_attributes": True}


class CheckoutResponse(BaseModel):
    order_id: int
    items: list[OrderItemResponse]
    subtotal: Decimal
    discount_applied: Decimal
    total: Decimal
    coupon_code: str | None = None
    status: str

    model_config = {"from_attributes": True}


class ProductResponse(BaseModel):
    id: int
    name: str
    price: Decimal
    stock: int

    model_config = {"from_attributes": True}


class CouponResponse(BaseModel):
    code: str
    discount_type: str
    discount_value: Decimal
    is_active: bool

    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):
    detail: str
