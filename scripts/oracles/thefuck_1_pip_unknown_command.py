from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    python = repo_root / "outputs" / "envs" / "thefuck1_f2p_py311" / "Scripts" / "python.exe"
    if not python.exists():
        print(f"missing oracle python: {python}", file=sys.stderr)
        return 2
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    command = [
        str(python),
        "-m",
        "pytest",
        "-q",
        "tests/rules/test_pip_unknown_command.py::test_get_new_command",
    ]
    completed = subprocess.run(command, cwd=Path.cwd(), env=env, text=True)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
