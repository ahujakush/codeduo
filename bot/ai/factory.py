"""
AI Solver Factory.
Instantiates the appropriate AI solver (Azure OpenAI, Gemini, OpenAI, Groq, or Mock).
"""

import logging
from bot.config import BotConfig, config
from bot.ai.base import BaseAISolver
from bot.ai.mock_solver import MockAISolver

logger = logging.getLogger(__name__)


def create_ai_solver(cfg: BotConfig = config) -> BaseAISolver:
    """Instantiate and return the configured AI Solver."""
    provider = cfg.ai_provider.lower()

    if provider == "mock":
        return MockAISolver()

    # 1. Azure OpenAI Brain (from GTM Plan)
    if provider == "azure" or (not provider and cfg.azure_api_key and cfg.azure_endpoint):
        if cfg.azure_api_key and cfg.azure_endpoint and cfg.azure_api_key != "your_azure_api_key_here":
            try:
                from web.services.azure_solver import AzureOpenAISolver
                logger.info(f"Using Azure OpenAI Brain (deployment={cfg.azure_deployment}, endpoint={cfg.azure_endpoint})")
                return AzureOpenAISolver(
                    api_key=cfg.azure_api_key,
                    endpoint=cfg.azure_endpoint,
                    deployment_name=cfg.azure_deployment,
                    api_version=cfg.azure_api_version,
                )
            except Exception as e:
                logger.error(f"Failed to initialize Azure OpenAI solver: {e}")

    # 2. Google Gemini
    if provider == "gemini" or (not provider and cfg.gemini_api_key):
        if cfg.gemini_api_key and cfg.gemini_api_key != "your_gemini_api_key_here":
            try:
                from bot.ai.gemini_solver import GeminiAISolver
                logger.info(f"Using Google Gemini AI solver (model={cfg.gemini_model})")
                return GeminiAISolver(api_key=cfg.gemini_api_key, model_name=cfg.gemini_model)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini solver: {e}")

    # 3. OpenAI
    if provider == "openai" or (not provider and cfg.openai_api_key):
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

    # 4. Groq
    if provider == "groq" or (not provider and cfg.groq_api_key):
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

    # Secondary check: If preferred provider lacked a key, check any other available key
    if cfg.azure_api_key and cfg.azure_endpoint:
        try:
            from web.services.azure_solver import AzureOpenAISolver
            return AzureOpenAISolver(
                api_key=cfg.azure_api_key,
                endpoint=cfg.azure_endpoint,
                deployment_name=cfg.azure_deployment,
                api_version=cfg.azure_api_version,
            )
        except Exception:
            pass

    if cfg.gemini_api_key:
        try:
            from bot.ai.gemini_solver import GeminiAISolver
            return GeminiAISolver(api_key=cfg.gemini_api_key, model_name=cfg.gemini_model)
        except Exception:
            pass

    # 5. Offline Fallback
    logger.warning("No valid AI API key detected. Falling back to local offline MockAISolver.")
    return MockAISolver()
