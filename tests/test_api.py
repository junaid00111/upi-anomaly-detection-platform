"""Tests for the FastAPI endpoints in api/main.py.

The database is mocked out so the tests can run on any machine
without a live PostgreSQL instance. ``api.main.get_connection`` is
patched to return a fake connection whose cursor returns scripted rows.
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


class FakeCursor:
    """Minimal stand-in for psycopg2 cursor + RealDictCursor."""

    def __init__(self, script):
        self.script = list(script)  # list of callables
        self.executed_query = None
        self.executed_params = None

    def execute(self, query, params=None):
        self.executed_query = query
        self.executed_params = params

    def fetchone(self):
        step = self.script.pop(0) if self.script else lambda: None
        return step(self)

    def fetchall(self):
        step = self.script.pop(0) if self.script else lambda: []
        return step(self)

    def close(self):
        pass


class FakeConnection:
    def __init__(self, script):
        self._script = script
        self.closed = False

    def cursor(self, cursor_factory=None):
        return FakeCursor(self._script)

    def close(self):
        self.closed = True


@pytest.fixture
def fake_db(monkeypatch):
    """Patch api.main.get_connection to return a FakeConnection.

    Usage: ``fake_db.set(script)`` then call the endpoint.
    """
    holder = {}

    def set_script(script):
        holder["script"] = script

    def fake_connection():
        return FakeConnection(holder.get("script", []))

    monkeypatch.setattr("api.main.get_connection", fake_connection)
    return type("FakeDB", (), {"set": staticmethod(set_script)})


# ----------------------------------------------------------------
# Root + health
# ----------------------------------------------------------------

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "online"
    assert body["service"] == "UPI Risk Monitoring API"


def test_health_endpoint(fake_db):
    fake_db.set([
        lambda cursor: (10000,),
    ])

    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "database": "connected",
        "transactions": 10000,
    }


def test_health_endpoint_reports_db_failure(fake_db):
    fake_db.set([])

    # Force get_connection to raise
    import api.main

    original = api.main.get_connection

    def boom():
        raise RuntimeError("connection refused")

    api.main.get_connection = boom
    try:
        response = client.get("/api/health")
    finally:
        api.main.get_connection = original

    assert response.status_code == 500


# ----------------------------------------------------------------
# Summary
# ----------------------------------------------------------------

def test_summary_endpoint(fake_db):
    fake_db.set([
        lambda cursor: {
            "total_transactions": 10000,
            "total_value": 37850000.0,
            "average_amount": 3785.0,
            "anomalous_transactions": 1886,
            "anomaly_rate": 18.86,
            "investigation_required": 68,
        },
    ])

    response = client.get("/api/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["total_transactions"] == 10000
    assert body["total_value"] == 37850000.0
    assert body["anomaly_rate"] == 18.86
    assert body["investigation_required"] == 68


def test_summary_endpoint_includes_all_keys(fake_db):
    row = {
        "total_transactions": 1,
        "total_value": 10.0,
        "average_amount": 10.0,
        "anomalous_transactions": 1,
        "anomaly_rate": 100.0,
        "investigation_required": 1,
    }
    fake_db.set([lambda cursor: row])

    body = client.get("/api/summary").json()
    assert set(body.keys()) == set(row.keys())


# ----------------------------------------------------------------
# Risk levels
# ----------------------------------------------------------------

def test_risk_levels_endpoint(fake_db):
    fake_db.set([
        lambda cursor: [
            {"risk_level": "Critical", "transaction_count": 12},
            {"risk_level": "High", "transaction_count": 56},
            {"risk_level": "Medium", "transaction_count": 1120},
            {"risk_level": "Low", "transaction_count": 8812},
        ],
    ])

    response = client.get("/api/risk-levels")
    assert response.status_code == 200
    levels = response.json()
    assert len(levels) == 4
    assert levels[0] == {"risk_level": "Critical", "transaction_count": 12}


# ----------------------------------------------------------------
# Transactions
# ----------------------------------------------------------------

def test_transactions_endpoint(fake_db):
    fake_db.set([
        # main query -> fetchall
        lambda cursor: [
            {
                "transaction_id": "UPI001",
                "timestamp": None,  # handled as None
                "amount_inr": 500.0,
                "risk_level": "Medium",
                "risk_score": 45.0,
                "category": "Shopping",
                "upi_app": "PhonePe",
                "location_state": "Maharashtra",
                "status": "SUCCESS",
                "anomaly_type": None,
                "anomaly_count": 2,
                "ml_model_agreement": 1,
            },
        ],
        # count query -> fetchone
        lambda cursor: {"total": 10000},
    ])

    response = client.get("/api/transactions?limit=1")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 10000
    assert body["count"] == 1
    assert len(body["transactions"]) == 1
    assert body["transactions"][0]["transaction_id"] == "UPI001"


def test_transactions_validates_limit(fake_db):
    fake_db.set([])

    response = client.get("/api/transactions?limit=0")
    assert response.status_code == 422  # FastAPI validation error
