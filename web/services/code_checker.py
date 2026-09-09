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

        if suggested.strip() == faulty_line.strip():
            suggested = faulty_line.rstrip() + ":"

        return {
            "line_number": line_num,
            "faulty_line": faulty_line,
            "message": f"SyntaxError: {msg}",
            "suggested_line": suggested,
        }


async def check_code_with_ai(code: str, language: str) -> Optional[List[Dict[str, Any]]]:
    """Use the AI optimization engine to detect subtle syntax and logical mistakes with high precision."""
    prompt = f"""You are a master compiler linter and syntax diagnostic tool for {language}.
Analyze the provided code for syntax errors, typos, malformed operator sequences (e.g. '///0', '* +'), missing tokens (colons, semicolons, brackets), or invalid statements.

RULES:
1. If the code contains syntax mistakes, typos, or malformed expressions, you MUST find ALL of them and return them as a list:
{{
  "has_errors": true,
  "errors": [
    {{
      "line_number": <1-indexed line number in the code below>,
      "faulty_line": "<exact faulty line as written in the code>",
      "message": "<clear, helpful explanation of the mistake and how to fix it>",
      "suggested_line": "<exact corrected replacement line with proper syntax and matching indentation>"
    }}
  ]
}}
2. "suggested_line" MUST BE DIFFERENT from "faulty_line". It must properly fix the mistake and be syntactically valid {language} code.
3. If the code is valid code with no syntax errors, return:
{{
  "has_errors": false,
  "errors": []
}}
4. Respond in valid JSON only.

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
                        "content": f"You are a professional compiler frontend syntax validator for {language}. Always respond in valid JSON only.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_completion_tokens=600,
                response_format={"type": "json_object"} if hasattr(solver.client, "chat") else None,
            )
            raw = res.choices[0].message.content
            match = re.search(r"\{[\s\S]*\}", raw)
            if match:
                data = json.loads(match.group(0))
                if not data.get("has_errors"):
                    return []
                errors = data.get("errors", [])
                valid_errors = []
                for e in errors:
                    faulty = e.get("faulty_line", "").strip()
                    suggested = e.get("suggested_line", "").strip()
                    # Guarantee that the suggested fix is not identical to the mistake!
                    if faulty and suggested and faulty != suggested:
                        valid_errors.append(e)
                return valid_errors
    except Exception as e:
        logger.warning(f"AI code check error: {e}")

    return None


def check_heuristics(code: str, language: str = "generic") -> List[Dict[str, Any]]:
    """Fallback pattern matching for syntax mistakes when AI is offline or unreachable."""
    errors = []
    lines = code.split("\n")

    for idx, raw_line in enumerate(lines):
        line = raw_line.strip()
        line_num = idx + 1

        if not line or line.startswith(("#", "//", "/*")):
            continue

        # 1. Triple slash typo (e.g. ///0)
        if "///" in line:
            fixed = raw_line.replace("///", "/ ")
            errors.append({
                "line_number": line_num,
                "faulty_line": raw_line,
                "message": "Malformed operator sequence '///'. Replace with valid division operator '/'.",
                "suggested_line": fixed,
            })
            continue

        # 2. Double operators like * +, + +, / *
        if re.search(r"([\+\*\/])\s*([\+\*])", line) and "++" not in line and "**" not in line:
            fixed = re.sub(r"\*\s*\+", "*", raw_line)
            fixed = re.sub(r"\+\s*\+", "+", fixed)
            if fixed.strip() != raw_line.strip():
                errors.append({
                    "line_number": line_num,
                    "faulty_line": raw_line,
                    "message": "Consecutive arithmetic operators detected (e.g. '* +').",
                    "suggested_line": fixed,
                })
                continue

        # 3. Missing semicolon in C / C++ / Java / Rust
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

        # 4. Malformed assignment operator (e.g. '= =')
        if "= =" in line and not any(kw in line for kw in ("if", "while", "assert")):
            fixed = raw_line.replace("= =", "=")
            if fixed.strip() != raw_line.strip():
                errors.append({
                    "line_number": line_num,
                    "faulty_line": raw_line,
                    "message": "Malformed assignment operator '= ='. Did you mean a single '='?",
                    "suggested_line": fixed,
                })
                continue

        # 5. Missing colon in Python
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


async def analyze_code_for_errors(code: str, language: str = "python") -> Dict[str, Any]:
    """Combine AI diagnostic engine, AST, and heuristic fallback to provide smart 1-click fixes."""
    if not code or not code.strip():
        return {"has_errors": False, "errors": []}

    # 1. Primary: Run AI-first diagnostic analysis (Smart and context-aware)
    ai_errors = await check_code_with_ai(code, language)
    if ai_errors is not None:
        return {
            "has_errors": len(ai_errors) > 0,
            "errors": ai_errors,
        }

    # 2. Fallback: Python official AST parser
    errors = []
    if language == "python" or "def " in code or "import " in code:
        ast_err = check_python_ast(code)
        if ast_err and ast_err["suggested_line"].strip() != ast_err["faulty_line"].strip():
            errors.append(ast_err)

    # 3. Fallback: Fast heuristic pattern matcher
    heuristic_errs = check_heuristics(code, language)
    for h in heuristic_errs:
        if not any(e["line_number"] == h["line_number"] for e in errors):
            if h["suggested_line"].strip() != h["faulty_line"].strip():
                errors.append(h)

    return {
        "has_errors": len(errors) > 0,
        "errors": errors,
    }

