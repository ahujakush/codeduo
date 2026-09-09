"""
Unit and integration tests for CodingDuo Web Application.
"""

import pytest
from fastapi.testclient import TestClient
from web.app import app
from web.services.elevenlabs_service import sanitize_for_speech


@pytest.fixture
def client():
    return TestClient(app)


def test_home_page_serves_codingduo(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "codingduo" in response.text.lower()
    assert "intermediate code optimizer" in response.text.lower()
    assert "duolingo" not in response.text.lower()
    assert "azure" not in response.text.lower()


def test_health_check_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["platform"] == "CodingDuo"
    assert "optimizer" in data
    assert "azure" not in data["optimizer"].lower()


def test_presets_endpoint(client):
    response = client.get("/api/presets")
    assert response.status_code == 200
    presets = response.json()
    assert "cse_const" in presets
    assert "loop_invariant" in presets
    assert "dead_code" in presets
    assert "strength_reduction" in presets


def test_stats_endpoint(client):
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "CodingDuo"
    assert data["streak_days"] == 5
    assert data["gems"] == 750


def test_optimize_empty_code_returns_400(client):
    response = client.post("/api/optimize", json={"code": "   "})
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]


def test_optimize_valid_tac_code(client):
    tac_input = (
        "t1 = 4 * 2\n"
        "t2 = a + t1\n"
        "t3 = 4 * 2\n"
        "t4 = b + t3\n"
        "ans = t2 + t4"
    )
    response = client.post(
        "/api/optimize",
        json={"code": tac_input, "pass_type": "all_passes"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Optimized Intermediate Code" in data["solution"] or "IR Analysis" in data["solution"]
    assert "azure" not in data["optimizer"].lower()


def test_compiler_speech_sanitizer():
    raw = (
        "Applied TAC optimization with CSE and DCE. "
        "Temporary t1 is folded to 8 and hoisted."
    )
    cleaned = sanitize_for_speech(raw)
    assert "Three Address Code" in cleaned
    assert "Common Subexpression Elimination" in cleaned
    assert "Dead Code Elimination" in cleaned
    assert "temporary 1" in cleaned
