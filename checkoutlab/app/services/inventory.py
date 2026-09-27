"""CheckoutLab — inventory service stub."""
from __future__ import annotations

from sqlalchemy.orm import Session

from checkoutlab.app.models import Product


def get_product(db: Session, product_id: int) -> Product | None:
    """Return product by ID, or None if not found."""
    return db.get(Product, product_id)


def reserve_stock(db: Session, product_id: int, quantity: int) -> bool:
    """
    Attempt to reduce stock by quantity. Returns True on success, False if
    insufficient stock. Does NOT commit — the caller must commit.
    """
    product = db.get(Product, product_id)
    if product is None or product.stock < quantity:
        return False
    product.stock -= quantity
    return True
