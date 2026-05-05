"""
Smoke tests for the Telecom Churn Inference API.
Uses httpx + FastAPI TestClient (no live server needed).
"""

from fastapi.testclient import TestClient

from main import app


def client():
    """Create a test client with lifespan (model loads once)."""
    with TestClient(app) as c:
        yield c


# ── Health / Docs ─────────────────────────────────────────────────────────────


def test_docs_reachable():
    """GET /docs should return 200."""
    with TestClient(app) as c:
        resp = c.get("/docs")
        assert resp.status_code == 200


def test_openapi_schema():
    """GET /openapi.json should return valid schema."""
    with TestClient(app) as c:
        resp = c.get("/openapi.json")
        assert resp.status_code == 200
        data = resp.json()
        assert "paths" in data
        assert "/predict_churn" in data["paths"]


# ── Prediction endpoint ──────────────────────────────────────────────────────

# Full payload matching ALL features the model was trained on
VALID_PAYLOAD = {
    "customerID": "test-001",
    "gender": "Male",
    "SeniorCitizen": 0,
    "Partner": "Yes",
    "Dependents": "No",
    "tenure": 12,
    "PhoneService": "Yes",
    "MultipleLines": "No",
    "InternetService": "Fiber optic",
    "OnlineSecurity": "No",
    "OnlineBackup": "Yes",
    "DeviceProtection": "No",
    "TechSupport": "No",
    "StreamingTV": "No",
    "StreamingMovies": "No",
    "Contract": "Month-to-month",
    "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 50.0,
    "TotalCharges": "600.0",
}


def test_predict_returns_200():
    """POST /predict_churn with valid data should return 200."""
    with TestClient(app) as c:
        resp = c.post("/predict_churn", json=VALID_PAYLOAD)
        assert resp.status_code == 200


def test_predict_response_schema():
    """Response must contain the expected keys."""
    with TestClient(app) as c:
        resp = c.post("/predict_churn", json=VALID_PAYLOAD)
        data = resp.json()
        assert "customer_id" in data
        assert "churn_probability" in data
        assert "risk_assessment" in data
        assert "threshold_applied" in data


def test_predict_probability_range():
    """Churn probability must be between 0 and 1."""
    with TestClient(app) as c:
        resp = c.post("/predict_churn", json=VALID_PAYLOAD)
        prob = resp.json()["churn_probability"]
        assert 0.0 <= prob <= 1.0


def test_predict_invalid_payload():
    """Missing required field should return 422."""
    with TestClient(app) as c:
        resp = c.post("/predict_churn", json={"customerID": "bad"})
        assert resp.status_code == 422


def test_predict_negative_tenure():
    """Negative tenure should be rejected by Pydantic validation."""
    bad = {**VALID_PAYLOAD, "tenure": -1}
    with TestClient(app) as c:
        resp = c.post("/predict_churn", json=bad)
        assert resp.status_code == 422
