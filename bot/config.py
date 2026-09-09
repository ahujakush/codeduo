"""
Configuration module for AI Problem Solver.
Loads settings from environment variables and .env file.
"""

import os
import logging
from dataclasses import dataclass, field
from typing import Set
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class BotConfig:
    ai_provider: str = field(
        default_factory=lambda: os.getenv("AI_PROVIDER", "azure").strip().lower()
    )

    # Azure OpenAI Configuration (Primary)
    azure_api_key: str = field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_API_KEY", "").strip()
    )
    azure_endpoint: str = field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
    )
    azure_api_version: str = field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview").strip()
    )
    azure_deployment: str = field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-5.4-mini").strip()
    )

    # Google Gemini Configuration
    gemini_api_key: str = field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY", "").strip()
    )
    gemini_model: str = field(
        default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    )

    # OpenAI Configuration
    openai_api_key: str = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "").strip()
    )
    openai_model: str = field(
        default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    )

    # Groq Configuration
    groq_api_key: str = field(
        default_factory=lambda: os.getenv("GROQ_API_KEY", "").strip()
    )
    groq_model: str = field(
        default_factory=lambda: os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
    )

    default_persona: str = field(
        default_factory=lambda: os.getenv("DEFAULT_PERSONA", "solver").strip().lower()
    )
    max_memory_turns: int = field(
        default_factory=lambda: int(os.getenv("MAX_MEMORY_TURNS", "10"))
    )


config = BotConfig()
