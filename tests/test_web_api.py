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
    # Verify famous languages are present
    assert "python" in langs
    assert "cpp" in langs
    assert "java" in langs
    assert "javascript" in langs
    assert "go" in langs
    assert "rust" in langs
    assert "html" in langs
    assert len(langs) >= 6

    # Verify each contains clean canonical starter code and filename
    for key, item in langs.items():
        assert "name" in item
        assert "code" in item
        assert "filename" in item
        assert len(item["code"]) >= 30
        assert "Hello, World!" in item["code"]


def test_teacher_explanation_endpoint(client):
    response = client.post(
        "/api/teacher-explanation",
        json={
            "code": "x = 4 * 2 + a\ny = 4 * 2 + a + b\nfor i in range(100): sum += (a + b)",
            "solution": "t1 = 4 * 2\n...",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "teacher_script" in data
    script = data["teacher_script"]
    # Teacher script should be pedagogical and conversational
    assert len(script) > 30
    assert "compiler" in script.lower() or "temporary" in script.lower() or "jump" in script.lower() or "tac" in script.lower() or "intermediate" in script.lower()


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
    assert "solution" in data
    assert len(data["solution"]) > 5
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


def test_check_code_detects_broken_python(client):
    broken_code = "def compute(a, b)\n    x = 4 * + a\n    for i in range 100:\n        total += i"
    response = client.post(
        "/api/check-code",
        json={"code": broken_code, "language": "python"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["has_errors"] is True
    assert len(data["errors"]) > 0
    first_err = data["errors"][0]
    assert "line_number" in first_err
    assert "faulty_line" in first_err
    assert "suggested_line" in first_err
    assert "message" in first_err


def test_check_code_clean_code(client):
    clean_code = "def compute(a, b):\n    return a + b"
    response = client.post(
        "/api/check-code",
        json={"code": clean_code, "language": "python"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["has_errors"] is False
    assert len(data["errors"]) == 0


def test_check_code_detects_user_javascript_mistake(client):
    code_with_triple_slash = (
        "function computeMetrics(a, b) {\n"
        "    const x = a + 1;\n"
        "    const deadValue = (a + b) ///0;\n"
        "    return x;\n"
        "}"
    )
    response = client.post(
        "/api/check-code",
        json={"code": code_with_triple_slash, "language": "javascript"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["has_errors"] is True
    assert len(data["errors"]) > 0
    first = data["errors"][0]
    # Suggested line must properly fix the mistake and NOT be identical to the faulty line
    assert first["faulty_line"].strip() != first["suggested_line"].strip()
    assert "///0" not in first["suggested_line"]
    assert "deadValue" in first["suggested_line"]

