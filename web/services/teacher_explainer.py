"""
Teacher Explanation Service.
Generates warm, easy-to-understand pedagogical audio walkthroughs
explaining compiler code optimizations to a student in plain English.
"""

import logging
from typing import Optional
from bot.ai.factory import create_ai_solver

logger = logging.getLogger(__name__)

TEACHER_SYSTEM_PROMPT = (
    "You are Professor Byte, a warm, encouraging, friendly computer science teacher explaining "
    "compiler code optimizations to a student. "
    "Do NOT recite raw syntax or repeat code lines over and over. "
    "Instead, explain conversationally in simple, engaging terms:\n"
    "1. Give a warm greeting and explain what this code was trying to do.\n"
    "2. Point out what was wasteful (e.g. recalculating constants, repeating math inside a loop).\n"
    "3. Explain the 'aha!' moment of each compiler pass (like hoisting invariant math outside the loop so it only runs once instead of 100 times!).\n"
    "4. End with an inspiring summary of the cycle and memory savings achieved!\n"
    "Keep it conversational, natural, and under 130 words."
)


async def generate_teacher_explanation(original_code: str, optimization_summary: str) -> str:
    """Generate a spoken teacher explanation of the optimization passes."""
    try:
        solver = create_ai_solver()
        if hasattr(solver, "client") and hasattr(solver, "deployment_name"):
            res = await solver.client.chat.completions.create(
                model=solver.deployment_name,
                messages=[
                    {"role": "system", "content": TEACHER_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": (
                            f"Original Code:\n{original_code[:400]}\n\n"
                            f"Optimization Passes Applied:\n{optimization_summary[:400]}\n\n"
                            "Explain these optimizations to the student like a teacher in an easy, friendly format."
                        ),
                    },
                ],
                max_completion_tokens=220,
            )
            text = res.choices[0].message.content
            if text and len(text.strip()) > 20:
                return text.strip()
    except Exception as e:
        logger.warning(f"Could not generate dynamic teacher script, using pedagogical template: {e}")

    # Fallback pedagogical teacher explanation
    return (
        "Hello there! Let's examine how the compiler supercharges your code. "
        "First, notice those constant arithmetic operations? Instead of wasting CPU clock cycles calculating them at runtime, "
        "the compiler performs constant folding and evaluates them right now at compile time! "
        "Next, inside your loop, calculating values that never change across iterations is unnecessary work. "
        "The compiler hoists that invariant code outside the loop preheader so it runs just once rather than hundreds of times! "
        "Finally, dead temporary variables are eliminated to free up precious CPU registers. "
        "The result? Clean, blazingly fast execution with significantly reduced memory pressure! Great job!"
    )
