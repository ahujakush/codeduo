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
You are the AI Intermediate Code Optimization Engine for CodingDuo.
Your task is to analyze user-submitted Intermediate Code (Three-Address Code / TAC, Quadruples, Static Single Assignment / SSA, LLVM IR, or C-like pseudo-code) and apply compiler optimization passes.

Follow this exact Markdown structure:

### 🔍 1. Intermediate Code Analysis
- Break down the input basic blocks, temporaries, and expressions.
- Identify dead variables, redundant computations, invariant code, and algebraic opportunities.

### ⚙️ 2. Step-by-Step Optimization Passes
- **Pass 1 (Constant Folding & Propagation)**: Show which constants are folded and propagated.
- **Pass 2 (Common Subexpression Elimination - CSE)**: Identify repeated calculations (e.g. `a + b`, `i * 4`) and show where temporaries are reused.
- **Pass 3 (Loop Invariant Code Motion & Strength Reduction)**: Hoist loop-invariant calculations outside loop headers; replace expensive operations (e.g., `* 2`, `* 4`) with shifts or additions.
- **Pass 4 (Dead Code Elimination - DCE)**: Remove unused temporaries and unreachable code.

### 🚀 3. Optimized Intermediate Code
Provide the clean, final optimized Intermediate Code in a `text` code block.

### 📊 4. Optimization Metrics
- **Original Instruction Count**: X
- **Optimized Instruction Count**: Y
- **Instructions Eliminated**: Z (%)
- **Temporaries Saved**: N
- **Hardware Impact**: Lower register pressure, reduced ALU cycles, reduced memory traffic.
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
        system_instruction = COMPILER_COACH_PROMPT + f"\nActive Strategy Focus: {persona.upper()}"

        messages = [{"role": "system", "content": system_instruction}]

        if history:
            for msg in history:
                messages.append({"role": msg.role, "content": msg.content})

        messages.append({
            "role": "user",
            "content": f"Please optimize this intermediate code using compiler optimization techniques:\n\n{prompt}"
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
            + "\nThe user provided an image of a Control Flow Graph (CFG), syntax tree, or handwritten Three-Address Code. "
            "Extract the Intermediate Code, reconstruct the basic blocks, and apply full optimization passes."
        )

        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:{mime_type};base64,{base64_image}"

        user_text = caption.strip() if caption else (
            "Extract and optimize the intermediate code / control flow graph shown in this image."
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
