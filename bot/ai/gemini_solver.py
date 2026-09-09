"""
Google Gemini AI Solver.
Uses the official google-genai SDK for text and multimodal (image) reasoning.
"""

import logging
from typing import List, Optional
from google import genai
from google.genai import types
from bot.ai.base import BaseAISolver
from bot.memory.chat_memory import ChatMessage

logger = logging.getLogger(__name__)


class GeminiAISolver(BaseAISolver):
    """Google Gemini AI solver supporting Gemini 2.5 Flash, 1.5 Pro, and vision."""

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = genai.Client(api_key=api_key)

    def get_provider_name(self) -> str:
        return "Google Gemini"

    def get_model_name(self) -> str:
        return self.model_name

    async def solve_text(
        self, prompt: str, history: Optional[List[ChatMessage]] = None, persona: str = "solver"
    ) -> str:
        system_instruction = self.get_system_prompt(persona)
        contents = []

        # Include past chat history for context
        if history:
            for msg in history:
                role = "user" if msg.role == "user" else "model"
                contents.append(types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg.content)]
                ))

        # Add current user prompt
        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)]
        ))

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.4,
        )

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config,
            )
            if response and response.text:
                return response.text.strip()
            return "⚠️ The AI model returned an empty response. Please try rephrasing your problem."
        except Exception as err:
            logger.error(f"Gemini API error during solve_text: {err}", exc_info=True)
            return f"❌ **Error generating AI solution**: {err}"

    async def solve_image(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        caption: Optional[str] = None,
        persona: str = "solver",
    ) -> str:
        system_instruction = self.get_system_prompt(persona)
        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

        user_text = caption.strip() if caption else (
            "Please examine this image carefully. If it contains a problem, equation, diagram, "
            "code, or question, provide a complete step-by-step solution."
        )

        contents = [
            types.Content(
                role="user",
                parts=[image_part, types.Part.from_text(text=user_text)]
            )
        ]

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.3,
        )

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config,
            )
            if response and response.text:
                return response.text.strip()
            return "⚠️ Could not interpret the image. Please ensure the image is clear and try again."
        except Exception as err:
            logger.error(f"Gemini API error during solve_image: {err}", exc_info=True)
            return f"❌ **Error analyzing image**: {err}"
