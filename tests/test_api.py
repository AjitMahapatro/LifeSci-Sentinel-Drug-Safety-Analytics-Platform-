"""API tests for the LifeSci Sentinel FastAPI backend.

These tests use FastAPI's TestClient. They verify endpoint routing, response
schemas, error handling, and AI input validation.

Some endpoints require a live PostgreSQL database. For those, we assert the
response either succeeds or returns a controlled 503 (database unavailable)
rather than surfacing a raw database exception. The pure validation and routing
checks do not require a database.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


def test_health_endpoint(client: TestClient):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["api"] == "running"
    assert body["status"] in ("ok", "degraded")
    assert "database" in body


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------


def test_analytics_overview(client: TestClient):
    resp = client.get("/api/analytics/overview")
    # Either 200 (db ok) or 503 (db unavailable / empty). Must be controlled.
    assert resp.status_code in (200, 503)


def test_analytics_trends(client: TestClient):
    resp = client.get("/api/analytics/trends")
    assert resp.status_code in (200, 503)


# ---------------------------------------------------------------------------
# Drugs
# ---------------------------------------------------------------------------


def test_drugs_endpoint_accepts_filters(client: TestClient):
    resp = client.get("/api/drugs", params={"limit": 5, "min_reports": 1})
    assert resp.status_code in (200, 503)


def test_drugs_endpoint_validates_limit(client: TestClient):
    # limit must be >= 1; a zero/invalid value should yield 4xx validation.
    resp = client.get("/api/drugs", params={"limit": 0})
    assert resp.status_code == 422


def test_drug_detail_not_found_returns_404(client: TestClient):
    resp = client.get("/api/drugs/__NO_SUCH_DRUG__")
    # If DB is available, expect 404 for unknown drug. If DB unavailable, 503.
    assert resp.status_code in (404, 503)


def test_drug_reactions_route(client: TestClient):
    resp = client.get("/api/drugs/LIPITOR/reactions")
    assert resp.status_code in (200, 404, 503)


# ---------------------------------------------------------------------------
# Reactions
# ---------------------------------------------------------------------------


def test_reactions_endpoint(client: TestClient):
    resp = client.get("/api/reactions", params={"limit": 5})
    assert resp.status_code in (200, 503)


def test_reaction_detail_not_found_returns_404(client: TestClient):
    resp = client.get("/api/reactions/__NO_SUCH_REACTION__")
    assert resp.status_code in (404, 503)


# ---------------------------------------------------------------------------
# Signals
# ---------------------------------------------------------------------------


def test_signals_endpoint(client: TestClient):
    resp = client.get("/api/signals", params={"limit": 5})
    assert resp.status_code in (200, 503)


def test_signals_endpoint_validates_params(client: TestClient):
    resp = client.get("/api/signals", params={"limit": 0})
    assert resp.status_code == 422


def test_signal_investigation_route(client: TestClient):
    resp = client.get("/api/signals/LIPITOR/HEADACHE/investigation")
    assert resp.status_code in (200, 404, 503)


# ---------------------------------------------------------------------------
# AI
# ---------------------------------------------------------------------------


def test_ai_query_empty_question_rejected(client: TestClient):
    resp = client.post("/api/ai/query", json={"question": "   "})
    assert resp.status_code == 422


def test_ai_query_missing_question_rejected(client: TestClient):
    resp = client.post("/api/ai/query", json={})
    assert resp.status_code == 422


def test_ai_query_returns_grounded_answer(client: TestClient):
    resp = client.post(
        "/api/ai/query", json={"question": "Which drugs have the highest serious rate?"}
    )
    # 200 if DB ok; otherwise 503 (AI service unavailable). Not a 500.
    assert resp.status_code in (200, 503)
    if resp.status_code == 200:
        body = resp.json()
        assert "answer" in body
        assert "evidence" in body
        assert "sources" in body
