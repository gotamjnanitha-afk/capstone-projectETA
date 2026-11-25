import ast
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

def analyze_python(code: str) -> tuple[list[dict], bool]:
    findings: list[dict] = []
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        findings.append({
            "severity": "error", "category": "Syntax",
            "message": exc.msg, "line": exc.lineno,
            "suggestion": "Correct the syntax at this line before running the program."
        })
        return findings, False

    # Heuristic checks: findings are potential issues, not proof of a bug.
    for node in ast.walk(tree):
        if isinstance(node, ast.For) and isinstance(node.iter, ast.Call):
            func = node.iter.func
            if (isinstance(func, ast.Name) and func.id == "range"
                and node.iter.args and isinstance(node.iter.args[0], ast.Call)
                and isinstance(node.iter.args[0].func, ast.Name)
                and node.iter.args[0].func.id == "len"):
                findings.append({
                    "severity": "warning", "category": "Possible off-by-one",
                    "message": "Review this range/len loop for an index boundary error.",
                    "line": getattr(node, "lineno", None),
                    "suggestion": "Prefer `for item in collection` or `range(len(collection))`."
                })
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            findings.append({
                "severity": "info", "category": "Division",
                "message": "Division detected; verify the denominator cannot be zero.",
                "line": getattr(node, "lineno", None),
                "suggestion": "Add an explicit zero/empty-input check where appropriate."
            })
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            findings.append({
                "severity": "warning", "category": "Exception handling",
                "message": "Bare `except` catches every exception and can hide errors.",
                "line": getattr(node, "lineno", None),
                "suggestion": "Catch the specific exception types you expect."
            })
        if isinstance(node, ast.FunctionDef) and not ast.get_docstring(node):
            findings.append({
                "severity": "info", "category": "Maintainability",
                "message": f"Function `{node.name}` has no docstring.",
                "line": getattr(node, "lineno", None),
                "suggestion": "Add a short docstring describing inputs and return value."
            })

    return findings, True

def run_ruff(code: str) -> tuple[list[dict], bool]:
    if not shutil.which("ruff"):
        return [], False
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / "submitted.py"
        path.write_text(code, encoding="utf-8")
        result = subprocess.run(
            ["ruff", "check", "--output-format", "json", str(path)],
            capture_output=True, text=True, timeout=8
        )
        try:
            raw = __import__("json").loads(result.stdout or "[]")
        except Exception:
            raw = []
        findings = []
        for item in raw[:40]:
            loc = item.get("location") or {}
            findings.append({
                "severity": "warning",
                "category": "Ruff: " + str(item.get("code", "Lint")),
                "message": item.get("message", "Lint issue"),
                "line": loc.get("row"),
                "suggestion": item.get("fix", {}).get("message") if item.get("fix") else "Review the lint message."
            })
        return findings, True
