"""CheckoutLab — FastAPI application entry point."""
from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from checkoutlab.app.database import create_tables, get_db
from checkoutlab.app.models import Coupon, Product
from checkoutlab.app.schemas import (
    CheckoutRequest,
    CheckoutResponse,
    CouponResponse,
    ProductResponse,
)
from checkoutlab.app.services.checkout import CheckoutError, process_checkout

app = FastAPI(
    title="CheckoutLab",
    description="Synthetic checkout application for ProofLoop demonstration.",
    version="0.1.0",
)


@app.on_event("startup")
def on_startup() -> None:
    create_tables()


# ── Products ─────────────────────────────────────────────────────────────────

@app.get("/products", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)) -> list[ProductResponse]:
    products = db.query(Product).all()
    return [ProductResponse.model_validate(p) for p in products]


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)) -> ProductResponse:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="product_not_found")
    return ProductResponse.model_validate(product)


# ── Coupons ───────────────────────────────────────────────────────────────────

@app.get("/coupons/{code}", response_model=CouponResponse)
def get_coupon(code: str, db: Session = Depends(get_db)) -> CouponResponse:
    coupon = db.query(Coupon).filter(Coupon.code == code.upper()).first()
    if coupon is None:
        raise HTTPException(status_code=404, detail="coupon_not_found")
    return CouponResponse.model_validate(coupon)


# ── Checkout ──────────────────────────────────────────────────────────────────

@app.post("/checkout", response_model=CheckoutResponse, status_code=201)
def checkout(
    request: CheckoutRequest, db: Session = Depends(get_db)
) -> CheckoutResponse:
    try:
        return process_checkout(db, request)
    except CheckoutError as exc:
        raise HTTPException(status_code=400, detail=exc.detail) from exc
