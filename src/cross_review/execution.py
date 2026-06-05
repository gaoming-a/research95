from __future__ import annotations

import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


def run_python_solution(
    code: str,
    tests: list[str],
    timeout_seconds: int = 5,
) -> dict[str, Any]:
    script = build_script(code, tests)
    start = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="cross_review_") as temp_dir:
        script_path = Path(temp_dir) / "candidate.py"
        script_path.write_text(script, encoding="utf-8")
        try:
            completed = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
            duration_ms = int((time.perf_counter() - start) * 1000)
            passed = completed.returncode == 0
            return {
                "passed": passed,
                "returncode": completed.returncode,
                "stdout": completed.stdout[-4000:],
                "stderr": completed.stderr[-4000:],
                "duration_ms": duration_ms,
                "timeout": False,
            }
        except subprocess.TimeoutExpired as exc:
            duration_ms = int((time.perf_counter() - start) * 1000)
            return {
                "passed": False,
                "returncode": None,
                "stdout": (exc.stdout or "")[-4000:] if isinstance(exc.stdout, str) else "",
                "stderr": "Execution timed out",
                "duration_ms": duration_ms,
                "timeout": True,
            }


def build_script(code: str, tests: list[str]) -> str:
    blocks = [code.rstrip(), "\n".join(test.strip() for test in tests)]
    return "\n\n".join(block for block in blocks if block).rstrip() + "\n"
