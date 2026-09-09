"""
Web Application Configuration.
Loads Azure, ElevenLabs, Gemini, and server parameters from environment.
"""

import os
import logging
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class WebConfig:
    # Server configuration
    host: str = field(default_factory=lambda: os.getenv("WEB_HOST", "0.0.0.0").strip())
    port: int = field(default_factory=lambda: int(os.getenv("WEB_PORT", "8000")))

    # AI Provider Priority
    ai_provider: str = field(
        default_factory=lambda: os.getenv("AI_PROVIDER", "azure").strip().lower()
    )

    # Azure OpenAI Configuration (Primary Brain)
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
    azure_model: str = field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_MODEL", "gpt-5.4-mini").strip()
    )

    # ElevenLabs Voice Narration Configuration
    elevenlabs_api_key: str = field(
        default_factory=lambda: os.getenv("ELEVENLABS_API_KEY", "").strip()
    )
    elevenlabs_voice_id: str = field(
        default_factory=lambda: os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL").strip()
    )
    elevenlabs_model_id: str = field(
        default_factory=lambda: os.getenv("ELEVENLABS_MODEL_ID", "eleven_turbo_v2_5").strip()
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

    default_persona: str = field(
        default_factory=lambda: os.getenv("DEFAULT_PERSONA", "solver").strip().lower()
    )

    def is_azure_configured(self) -> bool:
        return bool(self.azure_api_key and self.azure_endpoint)

    def is_elevenlabs_configured(self) -> bool:
        return bool(self.elevenlabs_api_key and self.elevenlabs_voice_id)


web_config = WebConfig()
