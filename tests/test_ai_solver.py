"""
Unit tests for AI Solvers and Solver Factory.
"""

import pytest
from bot.config import BotConfig
from bot.ai.base import PERSONA_PROMPTS
from bot.ai.mock_solver import MockAISolver
from bot.ai.factory import create_ai_solver


@pytest.mark.asyncio
async def test_mock_solver_linear_equation():
    solver = MockAISolver()
    solution = await solver.solve_text("Solve 2x + 5 = 15")
    assert "Math Equation Solved" in solution
    assert "[5]" in solution or "5" in solution


@pytest.mark.asyncio
async def test_mock_solver_arithmetic():
    solver = MockAISolver()
    solution = await solver.solve_text("Calculate 15 * 4 + 20")
    assert "Arithmetic Computation" in solution
    assert "80" in solution


@pytest.mark.asyncio
async def test_mock_solver_coding():
    solver = MockAISolver()
    solution = await solver.solve_text("How to write a fibonacci function in python?")
    assert "Fibonacci Sequence" in solution
    assert "def fibonacci" in solution


@pytest.mark.asyncio
async def test_mock_solver_fallback():
    solver = MockAISolver()
    solution = await solver.solve_text("What is the capital of France?")
    assert "Offline Solver Mode" in solution
    assert "GEMINI_API_KEY" in solution


@pytest.mark.asyncio
async def test_mock_solver_image():
    solver = MockAISolver()
    img_data = b"fake_image_bytes"
    solution = await solver.solve_image(img_data, mime_type="image/png", caption="Help me solve")
    assert "Image Received - Offline Mode" in solution
    assert "fake_image_bytes" not in solution  # should report metadata
    assert "image/png" in solution


def test_persona_system_prompts():
    solver = MockAISolver()
    for persona in ["solver", "coder", "math", "tutor", "concise"]:
        prompt = solver.get_system_prompt(persona)
        assert len(prompt) > 20
        assert prompt == PERSONA_PROMPTS[persona]


def test_factory_fallback_to_mock():
    # Empty config
    cfg = BotConfig(
        telegram_bot_token="test",
        ai_provider="gemini",
        gemini_api_key="",
        openai_api_key="",
        groq_api_key="",
    )
    solver = create_ai_solver(cfg)
    assert isinstance(solver, MockAISolver)
