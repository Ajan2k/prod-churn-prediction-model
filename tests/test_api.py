"""
Smoke tests for the Telecom Churn Inference API.
Uses httpx + FastAPI TestClient (no live server needed).
"""

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope="module")
def client():
    """Create a test client with lifespan (model loads once)."""
    with TestClient(app) as c:
        yield c


# ── Health / Docs ─────────────────────────────────────────────────────────────


def test_docs_reachable(client: TestClient):
    """GET /docs should return 200."""
    resp = client.get("/docs")
    assert resp.status_code == 200


def test_openapi_schema(client: TestClient):
    """GET /openapi.json should return valid schema."""
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    data = resp.json()
    assert "paths" in data
    assert "/predict_churn" in data["paths"]


# ── Prediction endpoint ──────────────────────────────────────────────────────


VALID_PAYLOAD = {
    "customerID": "test-001",
    "tenure": 12,
    "MonthlyCharges": 50.0,
    "TotalCharges": "600.0",
    "Contract": "Month-to-month",
    "PaymentMethod": "Electronic check",
}


def test_predict_returns_200(client: TestClient):
    """POST /predict_churn with valid data should return 200."""
    resp = client.post("/predict_churn", json=VALID_PAYLOAD)
    assert resp.status_code == 200


def test_predict_response_schema(client: TestClient):
    """Response must contain the expected keys."""
    resp = client.post("/predict_churn", json=VALID_PAYLOAD)
    data = resp.json()
    assert "customer_id" in data
    assert "churn_probability" in data
    assert "risk_assessment" in data
    assert "threshold_applied" in data


def test_predict_probability_range(client: TestClient):
    """Churn probability must be between 0 and 1."""
    resp = client.post("/predict_churn", json=VALID_PAYLOAD)
    prob = resp.json()["churn_probability"]
    assert 0.0 <= prob <= 1.0


def test_predict_invalid_payload(client: TestClient):
    """Missing required field should return 422."""
    resp = client.post("/predict_churn", json={"customerID": "bad"})
    assert resp.status_code == 422


def test_predict_negative_tenure(client: TestClient):
    """Negative tenure should be rejected by Pydantic validation."""
    bad = {**VALID_PAYLOAD, "tenure": -1}
    resp = client.post("/predict_churn", json=bad)
    assert resp.status_code == 422
