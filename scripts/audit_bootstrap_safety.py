from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


WORK_DIR = Path("outputs") / "bootstrap_safety"
MODEL_SELECTION_OUT = WORK_DIR / "model_selection.local.json"
API_CONFIG_OUT = WORK_DIR / "api_pilot.local.json"
MISSING_ENV = WORK_DIR / ".env.missing"


BASE_COMMAND = [
    sys.executable,
    "scripts/bootstrap_api_prereqs.py",
    "--model",
    "deepseek-v4-pro",
    "--api-provider",
    "deepseek_official",
    "--provider",
    "DeepSeek",
    "--selection-source",
    "DeepSeek official API docs and user-confirmed primary model",
    "--selection-source-url",
    "https://api-docs.deepseek.com",
    "--capability-source",
    "DeepSeek official V4 model family",
    "--capability-band",
    "single documented primary pilot model",
    "--reason",
    "Local bootstrap safety audit for the first DeepSeek official API within-model llm_only versus evidence_first comparison.",
    "--env",
    str(MISSING_ENV),
    "--model-selection-out",
    str(MODEL_SELECTION_OUT),
    "--api-config-out",
    str(API_CONFIG_OUT),
]


def run_command(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {
        "command": display_command(command),
        "exit_code": completed.returncode,
        "stdout_tail": completed.stdout[-2000:],
        "stderr_tail": completed.stderr[-2000:],
    }


def display_command(command: list[str]) -> list[str]:
    if command and Path(command[0]) == Path(sys.executable):
        return ["python", *command[1:]]
    return command


def clean_work_dir() -> None:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    WORK_DIR.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_audit() -> dict[str, Any]:
    clean_work_dir()

    dry_run = run_command([*BASE_COMMAND, "--dry-run", "--allow-missing-credentials"])
    dry_run_created_files = [path.as_posix() for path in [MODEL_SELECTION_OUT, API_CONFIG_OUT] if path.exists()]

    strict_missing_credentials = run_command(BASE_COMMAND)
    strict_created_files = [path.as_posix() for path in [MODEL_SELECTION_OUT, API_CONFIG_OUT] if path.exists()]

    passed = bool(
        dry_run["exit_code"] == 0
        and not dry_run_created_files
        and strict_missing_credentials["exit_code"] != 0
        and not strict_created_files
    )

    return {
        "passed": passed,
        "work_dir": WORK_DIR.as_posix(),
        "dry_run": {
            **dry_run,
            "created_files": dry_run_created_files,
            "passed": dry_run["exit_code"] == 0 and not dry_run_created_files,
        },
        "strict_missing_credentials": {
            **strict_missing_credentials,
            "created_files": strict_created_files,
            "passed": strict_missing_credentials["exit_code"] != 0 and not strict_created_files,
        },
        "boundary": "This audit must not call model APIs and must not write formal configs under configs/.",
    }


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def build_markdown(audit: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Bootstrap Safety Audit",
            "",
            "## Summary",
            "",
            f"- passed: {bool_mark(audit['passed'])}",
            f"- work dir: `{audit['work_dir']}`",
            f"- dry-run passed without writing files: {bool_mark(audit['dry_run']['passed'])}",
            f"- strict missing-credentials command failed without writing files: {bool_mark(audit['strict_missing_credentials']['passed'])}",
            "",
            "## Boundary",
            "",
            audit["boundary"],
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit bootstrap_api_prereqs.py safety behavior without API calls.")
    parser.add_argument("--out-json", default="outputs/bootstrap_safety/latest.json")
    parser.add_argument("--out-md", default="outputs/bootstrap_safety/latest.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = build_audit()
    write_json(Path(args.out_json), audit)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(audit), encoding="utf-8")
    print(json.dumps({"out_json": args.out_json, "out_md": args.out_md, "passed": audit["passed"]}, ensure_ascii=False, indent=2))
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
