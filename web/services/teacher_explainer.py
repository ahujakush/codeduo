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
    "Three-Address Code (TAC) generation to a student. "
    "Do NOT recite raw syntax or repeat code lines over and over. "
    "Instead, explain conversationally in simple, engaging terms:\n"
    "1. Give a warm greeting and explain what this code was trying to do.\n"
    "2. Explain how the compiler breaks down complex expressions into simpler steps.\n"
    "3. Explain the use of explicit temporaries (t1, t2) and jump labels (L1, L2) to handle control flow.\n"
    "4. End with an inspiring summary of how this intermediate representation helps the compiler!\n"
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
                            f"Generated TAC:\n{optimization_summary[:400]}\n\n"
                            "Explain this TAC generation to the student like a teacher in an easy, friendly format."
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
        "Hello there! Let's examine how the compiler breaks down your code into an Intermediate Representation. "
        "First, notice how complex arithmetic operations are broken into smaller steps? The compiler creates temporary variables like t1 and t2 to hold these intermediate values. "
        "Next, control flow structures like if-else and loops are translated into simple conditional and unconditional jumps using goto statements and labels. "
        "This explicit, step-by-step structure makes it much easier for the compiler to analyze and optimize the code later on. "
        "The result is a clean, universal Three-Address Code format! Great job!"
    )
