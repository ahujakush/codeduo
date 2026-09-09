"""
Unit and integration tests for CodingDuo Web Application with 6 language boilerplates
and teacher-style audio walkthroughs.
"""

import pytest
from fastapi.testclient import TestClient
from web.app import app
from web.services.elevenlabs_service import sanitize_for_speech
from web.services.boilerplates import LANGUAGE_BOILERPLATES


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
    # Bird mascot removed
    assert "mascot-svg" not in response.text
    assert "mascot-beak" not in response.text


def test_health_check_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["platform"] == "CodingDuo"
    assert "optimizer" in data
    assert "azure" not in data["optimizer"].lower()


def test_boilerplates_endpoint_has_6_famous_languages(client):
    response = client.get("/api/boilerplates")
    assert response.status_code == 200
    langs = response.json()
    # Verify the 6 famous languages are present
    assert "python" in langs
    assert "cpp" in langs
    assert "java" in langs
    assert "javascript" in langs
    assert "go" in langs
    assert "rust" in langs
    assert len(langs) == 6

    # Verify each contains clean code and filename
    for key, item in langs.items():
        assert "name" in item
        assert "code" in item
        assert "filename" in item
        assert len(item["code"]) > 50


def test_teacher_explanation_endpoint(client):
    response = client.post(
        "/api/teacher-explanation",
        json={
            "code": "x = 4 * 2 + a\ny = 4 * 2 + a + b\nfor i in range(100): sum += (a + b)",
            "solution": "Pass 1: Constant folding on 4*2. Pass 2: Loop invariant motion on a+b.",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "teacher_script" in data
    script = data["teacher_script"]
    # Teacher script should be pedagogical and conversational
    assert len(script) > 30
    assert "compiler" in script.lower() or "optimize" in script.lower() or "constant" in script.lower() or "loop" in script.lower()


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


def test_optimize_valid_python_boilerplate(client):
    code = LANGUAGE_BOILERPLATES["python"]["code"]
    response = client.post(
        "/api/optimize",
        json={"code": code, "pass_type": "all_passes"},
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
