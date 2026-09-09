"""
AI Intermediate Code Optimization Engine.
Applies code optimization passes to Three-Address Code, SSA, and IR.
"""

import base64
import logging
from typing import List, Optional
from openai import AsyncAzureOpenAI
from bot.ai.base import BaseAISolver
from bot.memory.chat_memory import ChatMessage

logger = logging.getLogger(__name__)

COMPILER_COACH_PROMPT = """
You are a Compiler Intermediate Code Generator.
Your ONLY job is to transform high-level C++ code into Three-Address Code (TAC).
STRICT RULES:
- Output MUST ONLY be the generated Three-Address Code (TAC).
- Always wrap your TAC output in a ```text Markdown code block.
- DO NOT perform code optimization or pass explanations.
- Use explicit temporaries (t1, t2, t3...) and conditional jump labels (L1, L2...).
"""


class AzureOpenAISolver(BaseAISolver):
    """Intermediate code optimization engine powered by advanced language models."""

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
        # Vendor neutral branding as requested
        return "AI Optimization Engine"

    def get_model_name(self) -> str:
        return "Compiler Optimizer v2"

    async def solve_text(
        self, prompt: str, history: Optional[List[ChatMessage]] = None, persona: str = "all_passes"
    ) -> str:
        system_instruction = COMPILER_COACH_PROMPT

        messages = [{"role": "system", "content": system_instruction}]

        if history:
            for msg in history:
                messages.append({"role": msg.role, "content": msg.content})

        messages.append({
            "role": "user",
            "content": prompt
        })

        try:
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_completion_tokens=2048,
            )
            content = response.choices[0].message.content
            return content.strip() if content else "⚠️ Empty response from optimization engine."
        except Exception as err:
            logger.error(f"Optimization engine solve_text error: {err}", exc_info=True)
            return f"❌ **Optimization Error**: {err}"

    async def solve_image(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        caption: Optional[str] = None,
        persona: str = "all_passes",
    ) -> str:
        system_instruction = (
            COMPILER_COACH_PROMPT
            + "\nThe user provided an image of C++ code. "
            "Extract the code and transform it into Three-Address Code (TAC)."
        )

        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:{mime_type};base64,{base64_image}"

        user_text = caption.strip() if caption else (
            "Transform the C++ code in this image into Three-Address Code (TAC)."
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
            return content.strip() if content else "⚠️ Could not interpret the IR image."
        except Exception as err:
            logger.error(f"Image IR optimization error: {err}", exc_info=True)
            return f"❌ **Error analyzing IR image**: {err}"
