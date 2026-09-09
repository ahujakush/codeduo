"""
Unit and integration tests for FastAPI DuoSolve Web Application.
"""

import pytest
from fastapi.testclient import TestClient
from web.app import app
from web.services.elevenlabs_service import sanitize_for_speech


@pytest.fixture
def client():
    return TestClient(app)


def test_home_page_serves_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "DuoSolve" in response.text
    assert "duosolve" in response.text
    assert "mascot-svg" in response.text


def test_health_check_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "provider" in data
    assert "model" in data


def test_stats_endpoint(client):
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["streak_days"] == 5
    assert data["gems"] == 750
    assert data["hearts"] == 5
    assert data["xp"] >= 1420


def test_solve_empty_prompt_returns_400(client):
    response = client.post("/api/solve", json={"prompt": "   "})
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]


def test_solve_valid_math_problem(client):
    response = client.post(
        "/api/solve",
        json={"prompt": "Solve 3x + 15 = 45", "persona": "solver"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "10" in data["solution"]
    assert len(data["solution"]) > 10


def test_clear_session(client):
    response = client.post("/api/clear", json={"chat_id": "test_session_123", "prompt": "dummy"})
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_speech_sanitizer():
    raw = "Here is the equation: \\[ 3x + 15 = 45 \\] and ```python\nx = 10\n``` **Good job!**"
    cleaned = sanitize_for_speech(raw)
    assert "\\[" not in cleaned
    assert "\\]" not in cleaned
    assert "```" not in cleaned
    assert "Good job!" in cleaned
    assert "equals" in cleaned
    assert "plus" in cleaned
