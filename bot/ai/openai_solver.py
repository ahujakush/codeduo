"""
OpenAI and Groq compatible AI Solver.
Uses the openai SDK to interact with GPT-4o, GPT-4o-mini, or Groq models.
"""

import base64
import logging
from typing import List, Optional
from openai import AsyncOpenAI
from bot.ai.base import BaseAISolver
from bot.memory.chat_memory import ChatMessage

logger = logging.getLogger(__name__)


class OpenAISolver(BaseAISolver):
    """OpenAI / Groq API solver."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "gpt-4o-mini",
        base_url: Optional[str] = None,
        provider_label: str = "OpenAI",
    ):
        self.api_key = api_key
        self.model_name = model_name
        self.provider_label = provider_label
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    def get_provider_name(self) -> str:
        return self.provider_label

    def get_model_name(self) -> str:
        return self.model_name

    async def solve_text(
        self, prompt: str, history: Optional[List[ChatMessage]] = None, persona: str = "solver"
    ) -> str:
        system_prompt = self.get_system_prompt(persona)
        messages = [{"role": "system", "content": system_prompt}]

        if history:
            for msg in history:
                messages.append({"role": msg.role, "content": msg.content})

        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.4,
            )
            content = response.choices[0].message.content
            return content.strip() if content else "⚠️ Empty response received from AI model."
        except Exception as err:
            logger.error(f"{self.provider_label} API error during solve_text: {err}", exc_info=True)
            return f"❌ **Error generating {self.provider_label} solution**: {err}"

    async def solve_image(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        caption: Optional[str] = None,
        persona: str = "solver",
    ) -> str:
        system_prompt = self.get_system_prompt(persona)
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:{mime_type};base64,{base64_image}"

        user_text = caption.strip() if caption else (
            "Please examine this image carefully. If it contains a problem, equation, diagram, "
            "code, or question, provide a complete step-by-step solution."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url, "detail": "auto"},
                    },
                ],
            },
        ]

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.3,
            )
            content = response.choices[0].message.content
            return content.strip() if content else "⚠️ Could not interpret the image."
        except Exception as err:
            logger.error(f"{self.provider_label} vision error: {err}", exc_info=True)
            return f"❌ **Error analyzing image with {self.provider_label}**: {err}"
