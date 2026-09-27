"""API integration tests — test the HTTP layer via TestClient."""
from __future__ import annotations

import pytest


def test_list_products_empty(client):
    """GET /products returns empty list when no products seeded."""
    resp = client.get("/products")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_product_not_found(client):
    """GET /products/999 returns 404."""
    resp = client.get("/products/999")
    assert resp.status_code == 404


def test_checkout_no_coupon_http(client, product_50):
    """POST /checkout without coupon returns 201 with correct totals."""
    resp = client.post(
        "/checkout",
        json={"items": [{"product_id": product_50.id, "quantity": 1}]},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert float(data["subtotal"]) == pytest.approx(50.0)
    assert float(data["discount_applied"]) == pytest.approx(0.0)
    assert float(data["total"]) == pytest.approx(50.0)
    assert data["status"] == "completed"


def test_checkout_percentage_coupon_http(client, product_50, coupon_10pct):
    """POST /checkout with 10% coupon: 10% off $50 = $45."""
    resp = client.post(
        "/checkout",
        json={
            "items": [{"product_id": product_50.id, "quantity": 1}],
            "coupon_code": "SAVE10",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert float(data["discount_applied"]) == pytest.approx(5.0)
    assert float(data["total"]) == pytest.approx(45.0)


def test_checkout_fixed_coupon_http(client, product_50, coupon_fixed_5):
    """POST /checkout with $5 fixed coupon on $50 order: total = $45."""
    resp = client.post(
        "/checkout",
        json={
            "items": [{"product_id": product_50.id, "quantity": 1}],
            "coupon_code": "FIXED5",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert float(data["discount_applied"]) == pytest.approx(5.0)
    assert float(data["total"]) == pytest.approx(45.0)


def test_checkout_coupon_not_found_returns_400(client, product_50):
    """POST /checkout with unknown coupon returns 400 with coupon_not_found."""
    resp = client.post(
        "/checkout",
        json={
            "items": [{"product_id": product_50.id, "quantity": 1}],
            "coupon_code": "FAKECODE",
        },
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "coupon_not_found"


def test_checkout_product_not_found_returns_400(client):
    """POST /checkout with non-existent product returns 400."""
    resp = client.post(
        "/checkout",
        json={"items": [{"product_id": 99999, "quantity": 1}]},
    )
    assert resp.status_code == 400
    assert "product_not_found" in resp.json()["detail"]


def test_checkout_insufficient_stock_returns_400(client, product_50):
    """POST /checkout with quantity > stock returns 400."""
    resp = client.post(
        "/checkout",
        json={"items": [{"product_id": product_50.id, "quantity": 9999}]},
    )
    assert resp.status_code == 400
    assert "insufficient_stock" in resp.json()["detail"]


def test_get_coupon_http(client, coupon_10pct):
    """GET /coupons/SAVE10 returns coupon metadata."""
    resp = client.get("/coupons/SAVE10")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "SAVE10"
    assert data["discount_type"] == "PERCENTAGE"


def test_get_coupon_not_found_http(client):
    """GET /coupons/GHOST returns 404."""
    resp = client.get("/coupons/GHOST")
    assert resp.status_code == 404


def test_checkout_returns_order_id(client, product_50):
    """POST /checkout response includes an order_id."""
    resp = client.post(
        "/checkout",
        json={"items": [{"product_id": product_50.id, "quantity": 1}]},
    )
    assert resp.status_code == 201
    assert "order_id" in resp.json()
    assert isinstance(resp.json()["order_id"], int)
