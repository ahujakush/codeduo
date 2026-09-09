"""
Configuration module for the Telegram AI Problem-Solving Bot.
Loads settings from environment variables and .env file.
"""

import os
import logging
from dataclasses import dataclass, field
from typing import Set
from dotenv import load_dotenv

# Load .env file
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class BotConfig:
    telegram_bot_token: str = field(
        default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    )
    ai_provider: str = field(
        default_factory=lambda: os.getenv("AI_PROVIDER", "gemini").strip().lower()
    )
    gemini_api_key: str = field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY", "").strip()
    )
    gemini_model: str = field(
        default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    )
    openai_api_key: str = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "").strip()
    )
    openai_model: str = field(
        default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    )
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
    allowed_user_ids: Set[int] = field(default_factory=set)

    def __post_init__(self):
        raw_ids = os.getenv("ALLOWED_USER_IDS", "").strip()
        if raw_ids:
            try:
                self.allowed_user_ids = {
                    int(uid.strip()) for uid in raw_ids.split(",") if uid.strip()
                }
            except ValueError as err:
                logger.warning(f"Invalid ALLOWED_USER_IDS specified in .env: {err}")

    def is_user_allowed(self, user_id: int) -> bool:
        """Check if a Telegram user is permitted to interact with the bot."""
        if not self.allowed_user_ids:
            return True
        return user_id in self.allowed_user_ids

    def is_telegram_configured(self) -> bool:
        """Check if a valid Telegram Bot token is configured."""
        token = self.telegram_bot_token
        return bool(token and token != "your_telegram_bot_token_here" and ":" in token)


config = BotConfig()
