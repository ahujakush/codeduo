"""
AI Solver Factory.
Instantiates the appropriate AI solver based on environment configuration and available keys.
"""

import logging
from bot.config import BotConfig, config
from bot.ai.base import BaseAISolver
from bot.ai.mock_solver import MockAISolver

logger = logging.getLogger(__name__)


def create_ai_solver(cfg: BotConfig = config) -> BaseAISolver:
    """Instantiate and return the configured AI Solver."""
    provider = cfg.ai_provider.lower()

    # 1. Google Gemini
    if provider == "gemini" or (not provider and cfg.gemini_api_key):
        if cfg.gemini_api_key and cfg.gemini_api_key != "your_gemini_api_key_here":
            try:
                from bot.ai.gemini_solver import GeminiAISolver
                logger.info(f"Using Google Gemini AI solver (model={cfg.gemini_model})")
                return GeminiAISolver(api_key=cfg.gemini_api_key, model_name=cfg.gemini_model)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini solver: {e}")

    # 2. OpenAI
    if provider == "openai" or cfg.openai_api_key:
        if cfg.openai_api_key and cfg.openai_api_key != "your_openai_api_key_here":
            try:
                from bot.ai.openai_solver import OpenAISolver
                logger.info(f"Using OpenAI solver (model={cfg.openai_model})")
                return OpenAISolver(
                    api_key=cfg.openai_api_key,
                    model_name=cfg.openai_model,
                    provider_label="OpenAI",
                )
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI solver: {e}")

    # 3. Groq
    if provider == "groq" or cfg.groq_api_key:
        if cfg.groq_api_key and cfg.groq_api_key != "your_groq_api_key_here":
            try:
                from bot.ai.openai_solver import OpenAISolver
                logger.info(f"Using Groq solver (model={cfg.groq_model})")
                return OpenAISolver(
                    api_key=cfg.groq_api_key,
                    model_name=cfg.groq_model,
                    base_url="https://api.groq.com/openai/v1",
                    provider_label="Groq",
                )
            except Exception as e:
                logger.error(f"Failed to initialize Groq solver: {e}")

    # 4. Offline Fallback
    logger.warning("No valid AI API key detected. Falling back to local offline MockAISolver.")
    return MockAISolver()
