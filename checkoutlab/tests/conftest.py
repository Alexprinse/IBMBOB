"""Shared pytest fixtures for CheckoutLab tests."""
from __future__ import annotations

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from checkoutlab.app.database import get_db
from checkoutlab.app.main import app
from checkoutlab.app.models import Base, Coupon, DiscountType, Product

# ── In-memory SQLite engine for tests ────────────────────────────────────────

# Use a file-based name so all in-process connections share the same DB
TEST_DATABASE_URL = "sqlite:///./test_checkoutlab.db"


@pytest.fixture()
def db_engine():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    import os
    try:
        os.remove("test_checkoutlab.db")
    except FileNotFoundError:
        pass


@pytest.fixture()
def db_session(db_engine):
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSession()
    yield session
    session.close()


@pytest.fixture()
def client(db_session):
    """TestClient with DB overridden to use the in-memory session."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    # Suppress the startup event so it doesn't call create_tables() on prod engine
    app.router.on_startup.clear()
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()
    # Re-register startup for non-test usage
    from checkoutlab.app.database import create_tables
    app.router.on_startup = [create_tables]


# ── Seed helpers ──────────────────────────────────────────────────────────────

@pytest.fixture()
def product_50(db_session) -> Product:
    """A product priced at $50.00 with 10 in stock."""
    p = Product(name="Widget A", price=Decimal("50.00"), stock=10)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


@pytest.fixture()
def product_30(db_session) -> Product:
    """A product priced at $30.00 with 5 in stock."""
    p = Product(name="Widget B", price=Decimal("30.00"), stock=5)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


@pytest.fixture()
def coupon_10pct(db_session) -> Coupon:
    """A 10% percentage coupon — SAVE10."""
    c = Coupon(
        code="SAVE10",
        discount_type=DiscountType.PERCENTAGE,
        discount_value=Decimal("10"),
        is_active=True,
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return c


@pytest.fixture()
def coupon_fixed_5(db_session) -> Coupon:
    """A $5.00 fixed-amount coupon — FIXED5."""
    c = Coupon(
        code="FIXED5",
        discount_type=DiscountType.FIXED,
        discount_value=Decimal("5.00"),
        is_active=True,
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return c


@pytest.fixture()
def coupon_large_fixed(db_session) -> Coupon:
    """A $75.00 fixed coupon — larger than a $50 order subtotal. Used to test inv-01."""
    c = Coupon(
        code="BIGDISCOUNT",
        discount_type=DiscountType.FIXED,
        discount_value=Decimal("75.00"),
        is_active=True,
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return c


@pytest.fixture()
def coupon_150pct(db_session) -> Coupon:
    """A 150% PERCENTAGE coupon — over 100%, used to test af-03/inv-01 via PERCENTAGE path."""
    c = Coupon(
        code="SUPER150",
        discount_type=DiscountType.PERCENTAGE,
        discount_value=Decimal("150"),
        is_active=True,
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return c
