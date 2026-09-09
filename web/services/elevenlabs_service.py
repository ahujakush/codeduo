"""
ElevenLabs Text-to-Speech (TTS) Voice Narration Service.
Converts AI solutions into natural spoken audio stream with smart text cleaning.
"""

import re
import logging
from typing import Optional
import httpx
from web.config import web_config

logger = logging.getLogger(__name__)


def sanitize_for_speech(text: str, max_chars: int = 1200) -> str:
    """
    Clean markdown formatting, code blocks, and LaTeX symbols
    so the speech sounds conversational and natural.
    """
    if not text:
        return ""

    cleaned = text

    # 1. Replace code blocks with spoken summaries
    cleaned = re.sub(
        r"```[a-zA-Z]*\n([\s\S]*?)```",
        r"Here is the code implementation. ",
        cleaned,
    )
    # 2. Inline code
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)

    # 3. Clean LaTeX math delimiters \( \), \[ \], $$ $$
    cleaned = re.sub(r"\\[\(\[]\s*", "", cleaned)
    cleaned = re.sub(r"\\[\)\]]\s*", "", cleaned)
    cleaned = re.sub(r"\$\$?", "", cleaned)

    # 4. Convert math operators into natural spoken English
    cleaned = re.sub(r"(\w+)\s*\^\s*2\b", r"\1 squared", cleaned)
    cleaned = re.sub(r"(\w+)\s*\^\s*3\b", r"\1 cubed", cleaned)
    cleaned = re.sub(r"\s*=\s*", " equals ", cleaned)
    cleaned = re.sub(r"\s*\+\s*", " plus ", cleaned)
    cleaned = re.sub(r"\s*-\s*", " minus ", cleaned)
    cleaned = re.sub(r"\s*\*\s*", " times ", cleaned)
    cleaned = re.sub(r"\s*/\s*", " divided by ", cleaned)

    # 5. Remove markdown headers, bold, bullets
    cleaned = re.sub(r"^[#\*\-]+\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"\*([^*]+)\*", r"\1", cleaned)
    cleaned = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", cleaned)

    # 6. Normalize whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # 7. Truncate if exceeds character limit
    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars].rsplit(" ", 1)[0] + "... and that completes the solution."

    return cleaned


class ElevenLabsTTSService:
    """Service to generate speech audio bytes via ElevenLabs API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_id: Optional[str] = None,
        model_id: Optional[str] = None,
    ):
        self.api_key = api_key or web_config.elevenlabs_api_key
        self.voice_id = voice_id or web_config.elevenlabs_voice_id
        self.model_id = model_id or web_config.elevenlabs_model_id
        self.base_url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"

    async def generate_speech_bytes(self, text: str) -> bytes:
        """Generate MP3 audio bytes for given text."""
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY is not configured.")

        speech_text = sanitize_for_speech(text)
        if not speech_text:
            speech_text = "No solution text to read aloud."

        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }

        payload = {
            "text": speech_text,
            "model_id": self.model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8,
                "style": 0.2,
                "use_speaker_boost": True,
            },
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(self.base_url, json=payload, headers=headers)
            if resp.status_code != 200:
                logger.error(f"ElevenLabs TTS failed ({resp.status_code}): {resp.text}")
                raise RuntimeError(f"ElevenLabs error ({resp.status_code}): {resp.text}")
            return resp.content


# Global service singleton
elevenlabs_service = ElevenLabsTTSService()
