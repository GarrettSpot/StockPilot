import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def make_product(**overrides):
    payload = {
        "name": "Wireless Mouse",
        "sku": "WMS-001",
        "category": "Peripherals",
        "quantity": 25,
        "reorder_level": 10,
        "price": 19.99,
        "supplier": "Acme",
    }
    payload.update(overrides)
    return payload


def test_health():
    assert client.get("/health").json() == {"status": "UP"}


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "StockPilot API"


def test_create_product():
    response = client.post("/api/products", json=make_product())
    assert response.status_code == 201
    body = response.json()
    assert body["sku"] == "WMS-001"
    assert body["status"] == "IN_STOCK"


def test_create_product_rejects_duplicate_sku():
    client.post("/api/products", json=make_product())
    response = client.post("/api/products", json=make_product())
    assert response.status_code == 409


def test_list_products():
    client.post("/api/products", json=make_product())
    client.post("/api/products", json=make_product(sku="KBD-002", name="Keyboard"))
    response = client.get("/api/products")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_product():
    created = client.post("/api/products", json=make_product()).json()
    response = client.get(f"/api/products/{created['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Wireless Mouse"


def test_get_product_not_found():
    assert client.get("/api/products/9999").status_code == 404


def test_update_product():
    created = client.post("/api/products", json=make_product()).json()
    response = client.put(f"/api/products/{created['id']}", json={"quantity": 3})
    assert response.status_code == 200
    assert response.json()["quantity"] == 3
    assert response.json()["status"] == "LOW_STOCK"


def test_delete_product():
    created = client.post("/api/products", json=make_product()).json()
    assert client.delete(f"/api/products/{created['id']}").status_code == 204
    assert client.get(f"/api/products/{created['id']}").status_code == 404


def test_stats():
    client.post("/api/products", json=make_product(quantity=50))
    client.post("/api/products", json=make_product(sku="LOW-1", quantity=2))
    client.post("/api/products", json=make_product(sku="OUT-1", quantity=0))
    response = client.get("/api/products/stats")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["inStock"] == 1
    assert body["lowStock"] == 1
    assert body["outOfStock"] == 1
