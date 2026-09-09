"""
Unit tests for CodingDuo AI Optimization Solvers.
"""

import pytest
from bot.config import BotConfig
from bot.ai.base import COMPILER_PERSONA_PROMPTS
from bot.ai.mock_solver import MockAISolver
from bot.ai.factory import create_ai_solver


@pytest.mark.asyncio
async def test_mock_solver_constant_folding():
    solver = MockAISolver()
    tac = "t1 = 4 * 2\nt2 = a + t1\nans = t2"
    solution = await solver.solve_text(tac)
    assert "Optimized Intermediate Code" in solution
    assert "Constant Folding" in solution
    assert "t1 = 8" in solution


@pytest.mark.asyncio
async def test_mock_solver_cse():
    solver = MockAISolver()
    tac = "t1 = a + b\nt2 = a + b\nans = t1 + t2"
    solution = await solver.solve_text(tac)
    assert "Common Subexpression Elimination" in solution
    assert "t2 = t1" in solution


@pytest.mark.asyncio
async def test_mock_solver_strength_reduction():
    solver = MockAISolver()
    tac = "t1 = x * 2\nans = t1"
    solution = await solver.solve_text(tac)
    assert "Strength Reduction" in solution
    assert "x << 1" in solution


@pytest.mark.asyncio
async def test_mock_solver_image():
    solver = MockAISolver()
    img_data = b"fake_flowgraph_bytes"
    solution = await solver.solve_image(img_data, mime_type="image/png", caption="Optimize CFG")
    assert "IR Flowgraph" in solution
    assert "Optimized Basic Blocks" in solution


def test_persona_system_prompts():
    solver = MockAISolver()
    for persona in ["all_passes", "cse", "loop_opt", "dead_code", "peephole"]:
        prompt = solver.get_system_prompt(persona)
        assert len(prompt) > 20
        assert prompt == COMPILER_PERSONA_PROMPTS[persona]


def test_factory_fallback_to_mock():
    cfg = BotConfig(
        telegram_bot_token="test",
        ai_provider="mock",
        azure_api_key="",
        azure_endpoint="",
        gemini_api_key="",
        openai_api_key="",
        groq_api_key="",
    )
    solver = create_ai_solver(cfg)
    assert isinstance(solver, MockAISolver)
    assert solver.get_provider_name() == "AI Optimization Engine"
