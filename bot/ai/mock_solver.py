"""
Mock / Local Fallback AI Solver.
Provides offline math equation solving (via SymPy) and heuristic answers
when no external AI API key is configured.
"""

import re
import sympy as sp
from typing import List, Optional
from bot.ai.base import BaseAISolver
from bot.memory.chat_memory import ChatMessage


class MockAISolver(BaseAISolver):
    """Offline deterministic solver for math and test queries."""

    def get_provider_name(self) -> str:
        return "Mock / Local Solver (Offline)"

    def get_model_name(self) -> str:
        return "sympy-heuristic-solver-v1"

    async def solve_text(
        self, prompt: str, history: Optional[List[ChatMessage]] = None, persona: str = "solver"
    ) -> str:
        prompt_clean = prompt.strip()

        # 1. Check if it's a math equation or arithmetic
        math_solution = self._try_solve_math(prompt_clean)
        if math_solution:
            return math_solution

        # 2. Check for common coding queries
        code_solution = self._try_solve_code(prompt_clean)
        if code_solution:
            return code_solution

        # 3. General Fallback with setup instructions
        return (
            f"🤖 **[Offline Solver Mode]**\n\n"
            f"🔍 **Input Received**: \"{prompt_clean}\"\n"
            f"💡 **Active Persona**: `{persona}`\n\n"
            f"📝 **Status & Response**:\n"
            f"The bot is running in **Mock/Offline mode** because no AI API key (Gemini / OpenAI / Groq) is currently configured.\n\n"
            f"✅ **How to enable Full AI Power**:\n"
            f"1. Open the `.env` file in the project directory.\n"
            f"2. Add your free **Google Gemini API Key**:\n"
            f"   ```bash\n"
            f"   GEMINI_API_KEY=your_key_here\n"
            f"   AI_PROVIDER=gemini\n"
            f"   ```\n"
            f"   (Get a free key at [Google AI Studio](https://aistudio.google.com/))\n"
            f"3. Or configure `OPENAI_API_KEY` or `GROQ_API_KEY`.\n"
            f"4. Restart the bot!"
        )

    async def solve_image(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        caption: Optional[str] = None,
        persona: str = "solver",
    ) -> str:
        size_kb = len(image_bytes) / 1024
        return (
            f"🖼️ **[Image Received - Offline Mode]**\n\n"
            f"• **Image Size**: {size_kb:.1f} KB\n"
            f"• **MIME Type**: `{mime_type}`\n"
            f"• **User Caption**: {caption or 'None'}\n\n"
            f"💡 **Note**: Multimodal vision analysis requires an active **Google Gemini** or **OpenAI** API key. "
            f"Please configure `GEMINI_API_KEY` in `.env` to unlock image and handwritten problem solving!"
        )

    def _try_solve_math(self, text: str) -> Optional[str]:
        """Attempt to solve algebraic equation or arithmetic using SymPy."""
        cleaned = re.sub(
            r"^(solve|find|calculate|evaluate|what is|simplify|equation)\s*:?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        ).strip()

        # Check for equation with '='
        if "=" in cleaned:
            match = re.search(r"([^=]+)=([^=]+)", cleaned)
            if match:
                lhs_str, rhs_str = match.group(1).strip(), match.group(2).strip()
                try:
                    # Replace 2x with 2*x, 3y with 3*y
                    lhs_str = re.sub(r"(\d+)([a-zA-Z])", r"\1*\2", lhs_str)
                    rhs_str = re.sub(r"(\d+)([a-zA-Z])", r"\1*\2", rhs_str)
                    lhs_str = lhs_str.replace("^", "**")
                    rhs_str = rhs_str.replace("^", "**")

                    symbols = list(sp.symbols("x y z a b c n"))
                    var = None
                    for s in symbols:
                        if str(s) in lhs_str or str(s) in rhs_str:
                            var = s
                            break

                    if var:
                        lhs = sp.sympify(lhs_str)
                        rhs = sp.sympify(rhs_str)
                        eq = sp.Eq(lhs, rhs)
                        solutions = sp.solve(eq, var)
                        return (
                            f"📐 **Math Equation Solved (SymPy)**\n\n"
                            f"🔍 **Equation**: `{lhs} = {rhs}`\n"
                            f"💡 **Target Variable**: `{var}`\n\n"
                            f"📝 **Step-by-Step**:\n"
                            f"1. Move terms to standard form: `{sp.simplify(lhs - rhs)} = 0`\n"
                            f"2. Solve for `{var}`.\n\n"
                            f"✅ **Solution**: `{var} = {solutions}`"
                        )
                except Exception:
                    pass

        # Check for simple arithmetic (e.g. 25 * 4 + 10)
        arith_str = re.sub(r"[^\d\+\-\*\/\(\)\.\s\^]", "", cleaned).strip()
        if arith_str and any(op in arith_str for op in ["+", "-", "*", "/", "^"]):
            try:
                expr = sp.sympify(arith_str.replace("^", "**"))
                result = expr.evalf()
                # If integer, print as int
                if result == int(result):
                    result = int(result)
                return (
                    f"🔢 **Arithmetic Computation**\n\n"
                    f"🔍 **Expression**: `{arith_str}`\n"
                    f"✅ **Result**: `{result}`"
                )
            except Exception:
                pass

        return None

    def _try_solve_code(self, text: str) -> Optional[str]:
        """Detect common coding keywords and provide templates in offline mode."""
        lower = text.lower()
        if "fibonacci" in lower:
            return (
                "💻 **Fibonacci Sequence (Python)**\n\n"
                "```python\n"
                "def fibonacci(n: int):\n"
                "    a, b = 0, 1\n"
                "    for _ in range(n):\n"
                "        yield a\n"
                "        a, b = b, a + b\n\n"
                "# Example: print first 10 Fibonacci numbers\n"
                "print(list(fibonacci(10)))\n"
                "```\n"
                "• **Time Complexity**: O(n)\n"
                "• **Space Complexity**: O(1)"
            )
        if "prime" in lower and ("check" in lower or "number" in lower or "is" in lower):
            return (
                "💻 **Prime Number Checker (Python)**\n\n"
                "```python\n"
                "import math\n\n"
                "def is_prime(n: int) -> bool:\n"
                "    if n < 2:\n"
                "        return False\n"
                "    for i in range(2, int(math.isqrt(n)) + 1):\n"
                "        if n % i == 0:\n"
                "            return False\n"
                "    return True\n"
                "```\n"
                "• **Time Complexity**: O(√n)"
            )
        return None
