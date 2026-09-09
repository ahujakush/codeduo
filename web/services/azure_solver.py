"""
Azure OpenAI Brain Solver.
Integrates AsyncAzureOpenAI using credentials imported from GTM plan.
"""

import base64
import logging
from typing import List, Optional
from openai import AsyncAzureOpenAI
from bot.ai.base import BaseAISolver, PERSONA_PROMPTS
from bot.memory.chat_memory import ChatMessage

logger = logging.getLogger(__name__)

# Duolingo-inspired playful & encouraging persona overlays
DUO_PERSONA_EXTENSIONS = {
    "solver": (
        "\n\nPlayful Duolingo Vibe: Maintain a friendly, motivational tone. Celebrate progress "
        "and use crisp formatting with emojis (🔍 Problem, 💡 Concept, 📝 Steps, ✅ Final Answer)."
    ),
    "coder": (
        "\n\nPlayful Duolingo Coder Vibe: Clean code with clear comments, big-O complexity, "
        "and beginner-friendly debugging explanations."
    ),
    "tutor": (
        "\n\nSocratic Duo Tutor Vibe: Ask an engaging checkpoint question at the end to help "
        "the learner test what they just learned!"
    ),
}


class AzureOpenAISolver(BaseAISolver):
    """Azure OpenAI problem solver supporting gpt-5.4-mini / gpt-4o-mini."""

    def __init__(
        self,
        api_key: str,
        endpoint: str,
        deployment_name: str = "gpt-5.4-mini",
        api_version: str = "2024-12-01-preview",
    ):
        self.api_key = api_key
        self.endpoint = endpoint
        self.deployment_name = deployment_name
        self.api_version = api_version
        self.client = AsyncAzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version,
        )

    def get_provider_name(self) -> str:
        return "Azure OpenAI Brain"

    def get_model_name(self) -> str:
        return self.deployment_name

    async def solve_text(
        self, prompt: str, history: Optional[List[ChatMessage]] = None, persona: str = "solver"
    ) -> str:
        base_prompt = self.get_system_prompt(persona)
        system_instruction = base_prompt + DUO_PERSONA_EXTENSIONS.get(persona, "")

        messages = [{"role": "system", "content": system_instruction}]

        if history:
            for msg in history:
                messages.append({"role": msg.role, "content": msg.content})

        messages.append({"role": "user", "content": prompt})

        try:
            # Azure gpt-5.4-mini requires max_completion_tokens
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_completion_tokens=2048,
            )
            content = response.choices[0].message.content
            return content.strip() if content else "⚠️ Empty response from Azure OpenAI."
        except Exception as err:
            logger.error(f"Azure OpenAI solve_text error: {err}", exc_info=True)
            return f"❌ **Azure OpenAI Brain Error**: {err}"

    async def solve_image(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        caption: Optional[str] = None,
        persona: str = "solver",
    ) -> str:
        base_prompt = self.get_system_prompt(persona)
        system_instruction = base_prompt + "\nAnalyze this homework/problem image carefully and solve it step-by-step."

        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:{mime_type};base64,{base64_image}"

        user_text = caption.strip() if caption else (
            "Please solve the problem shown in this image step-by-step."
        )

        messages = [
            {"role": "system", "content": system_instruction},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url, "detail": "high"},
                    },
                ],
            },
        ]

        try:
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_completion_tokens=2048,
            )
            content = response.choices[0].message.content
            return content.strip() if content else "⚠️ Could not interpret the image."
        except Exception as err:
            logger.error(f"Azure OpenAI vision error: {err}", exc_info=True)
            return f"❌ **Azure Image Solving Error**: {err}"
