"""
Code Error Detection and Inline Fix Service.
Inspects code for syntax errors, typos, and malformed expressions,
providing exact line numbers, explanations, and suggested line replacements.
"""

import ast
import re
import json
import logging
from typing import Dict, List, Any, Optional
from bot.ai.factory import create_ai_solver

logger = logging.getLogger(__name__)


def check_python_ast(code: str) -> Optional[Dict[str, Any]]:
    """Check Python code using the official AST parser."""
    try:
        ast.parse(code)
        return None
    except SyntaxError as e:
        lines = code.split("\n")
        line_num = e.lineno or 1
        faulty_line = lines[line_num - 1] if 0 < line_num <= len(lines) else ""

        # Infer common fixes
        suggested = faulty_line
        msg = e.msg or "Syntax error"

        if "expected ':'" in msg or "invalid syntax" in msg:
            if re.match(r"^\s*(for|if|while|elif|else|def|class)\b", faulty_line) and not faulty_line.rstrip().endswith(":"):
                suggested = faulty_line.rstrip() + ":"
                msg = "Missing colon ':' at the end of the statement."
            elif "for " in faulty_line and "in range" in faulty_line and "(" not in faulty_line:
                suggested = re.sub(r"range\s+([0-9a-zA-Z_]+)", r"range(\1):", faulty_line)
                msg = "Missing parentheses around range argument and missing colon ':'."

        if "was never closed" in msg or "unexpected EOF" in msg:
            if faulty_line.count("(") > faulty_line.count(")"):
                suggested = faulty_line + ")" * (faulty_line.count("(") - faulty_line.count(")"))
                msg = "Unclosed parenthesis ')' on this line."

        return {
            "line_number": line_num,
            "faulty_line": faulty_line,
            "message": f"SyntaxError: {msg}",
            "suggested_line": suggested if suggested != faulty_line else (faulty_line + "  # Check syntax"),
        }


def check_heuristics(code: str, language: str = "generic") -> List[Dict[str, Any]]:
    """Check for obvious syntax mistakes using pattern matching across languages."""
    errors = []
    lines = code.split("\n")

    for idx, raw_line in enumerate(lines):
        line = raw_line.strip()
        line_num = idx + 1

        if not line or line.startswith(("#", "//", "/*")):
            continue

        # 1. Double operators like * +, / *, + + (without variable)
        if re.search(r"([\+\*\/])\s*([\+\*\/])", line) and "++" not in line and "**" not in line:
            # e.g. x = 4 * + a
            fixed = re.sub(r"\*\s*\+", "*", raw_line)
            fixed = re.sub(r"\+\s*\+", "+", fixed)
            errors.append({
                "line_number": line_num,
                "faulty_line": raw_line,
                "message": "Consecutive arithmetic operators detected (e.g. '* +').",
                "suggested_line": fixed if fixed != raw_line else raw_line.replace("* +", "*"),
            })
            continue

        # 2. Missing semicolon in C / C++ / Java / Rust (excluding function headers / blocks)
        if language in ("cpp", "c", "java", "rust"):
            if not line.endswith((";", "{", "}", ":", ">", ",")) and not line.startswith(("#", "//", "/*")):
                if not re.match(r"^\s*(if|for|while|else|struct|class|fn|public|private)\b", line):
                    errors.append({
                        "line_number": line_num,
                        "faulty_line": raw_line,
                        "message": "Missing semicolon ';' at the end of statement.",
                        "suggested_line": raw_line.rstrip() + ";",
                    })
                    continue

        # 3. Malformed assignment (e.g. t1 = = 5 or = 4)
        if "= =" in line and not any(kw in line for kw in ("if", "while", "assert")):
            fixed = raw_line.replace("= =", "=")
            errors.append({
                "line_number": line_num,
                "faulty_line": raw_line,
                "message": "Malformed assignment operator '= ='. Did you mean a single '='?",
                "suggested_line": fixed,
            })
            continue

        # 4. For loop missing colon in Python
        if language == "python" or "def " in code or "print(" in code:
            if re.match(r"^\s*(for|while|if|def)\b", raw_line) and not raw_line.rstrip().endswith(":"):
                errors.append({
                    "line_number": line_num,
                    "faulty_line": raw_line,
                    "message": "Missing colon ':' at the end of control statement.",
                    "suggested_line": raw_line.rstrip() + ":",
                })
                continue

    return errors


async def check_code_with_ai(code: str, language: str) -> List[Dict[str, Any]]:
    """Use the AI optimization engine to detect subtle syntax and logical mistakes."""
    prompt = f"""Analyze this {language} code for any syntax errors, typos, or malformed lines.
If there are no errors, return: {{"has_errors": false, "errors": []}}
If there ARE errors, return valid JSON with this exact structure:
{{
  "has_errors": true,
  "errors": [
    {{
      "line_number": <1-indexed integer>,
      "faulty_line": "<exact faulty line text>",
      "message": "<simple, friendly explanation of the mistake>",
      "suggested_line": "<the exact corrected replacement line>"
    }}
  ]
}}

Code:
{code}
"""
    try:
        solver = create_ai_solver()
        if hasattr(solver, "client") and hasattr(solver, "deployment_name"):
            res = await solver.client.chat.completions.create(
                model=solver.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise code linter and syntax validator. Always output valid JSON only.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_completion_tokens=400,
                response_format={"type": "json_object"} if hasattr(solver.client, "chat") else None,
            )
            raw = res.choices[0].message.content
            # Parse JSON
            match = re.search(r"\{[\s\S]*\}", raw)
            if match:
                data = json.loads(match.group(0))
                if data.get("has_errors") and data.get("errors"):
                    return data["errors"]
    except Exception as e:
        logger.warning(f"AI code check error: {e}")

    return []


async def analyze_code_for_errors(code: str, language: str = "python") -> Dict[str, Any]:
    """Combine AST, heuristics, and AI to identify mistakes and provide 1-click fixes."""
    if not code or not code.strip():
        return {"has_errors": False, "errors": []}

    errors = []

    # 1. Quick AST check for Python
    if language == "python" or "def " in code or "import " in code:
        ast_err = check_python_ast(code)
        if ast_err:
            errors.append(ast_err)

    # 2. Fast heuristic checks
    heuristic_errs = check_heuristics(code, language)
    for h in heuristic_errs:
        if not any(e["line_number"] == h["line_number"] for e in errors):
            errors.append(h)

    # 3. AI analysis if no local errors caught or if heuristics are empty
    if not errors and len(code.split("\n")) <= 60:
        ai_errs = await check_code_with_ai(code, language)
        if ai_errs:
            errors.extend(ai_errs)

    return {
        "has_errors": len(errors) > 0,
        "errors": errors[:5],  # Top 5 errors to avoid UI clutter
    }
