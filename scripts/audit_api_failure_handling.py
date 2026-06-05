from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


WORK_DIR = Path("outputs") / "api_failure_handling"
RUN_DIR = WORK_DIR / "failed_run"
DUMMY_KEY = "local-test-key"
OPENROUTER_KEY_PREFIX = "".join(["sk-", "or-v1-"])


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def display_command(command: list[str]) -> list[str]:
    if command and Path(command[0]) == Path(sys.executable):
        return ["python", *command[1:]]
    return command


def run_command(command: list[str], env: dict[str, str] | None = None) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    return {
        "command": display_command(command),
        "exit_code": completed.returncode,
        "stdout_tail": completed.stdout[-2000:],
        "stderr_tail": completed.stderr[-2000:],
    }


def clean_work_dir() -> None:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    WORK_DIR.mkdir(parents=True, exist_ok=True)


def contains_secret(value: Any) -> bool:
    text = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
    return DUMMY_KEY in text or OPENROUTER_KEY_PREFIX in text


def file_list(path: Path) -> list[str]:
    if not path.exists():
        return []
    return sorted(item.as_posix() for item in path.rglob("*") if item.is_file())


def build_audit() -> dict[str, Any]:
    clean_work_dir()
    env = os.environ.copy()
    env.update(
        {
            "OPENROUTER_API_KEY": DUMMY_KEY,
            "OPENROUTER_BASE_URL": "http://127.0.0.1:9",
            "OPENROUTER_TIMEOUT_SECONDS": "1",
            "OPENROUTER_MAX_RETRIES": "1",
            "OPENROUTER_RETRY_BACKOFF_SECONDS": "0",
        }
    )
    failed_run = run_command(
        [
            sys.executable,
            "scripts/run_patch_verification_api_pilot.py",
            "--candidates",
            "outputs/patch_verification_pilot_001/candidates.jsonl",
            "--evidence-packets",
            "outputs/patch_verification_pilot_001/evidence_packets.jsonl",
            "--out-dir",
            str(RUN_DIR),
            "--model",
            "local/failure-path-check",
            "--limit",
            "1",
            "--allow-direct-api-run",
        ],
        env=env,
    )
    run_error_path = RUN_DIR / "run_error.json"
    run_error = read_json(run_error_path)
    completeness_run = run_command(
        [
            sys.executable,
            "scripts/audit_api_run_completeness.py",
            "--run-dir",
            str(RUN_DIR),
            "--expected-candidates",
            "1",
            "--out-json",
            str(RUN_DIR / "run_completeness.json"),
            "--out-md",
            str(RUN_DIR / "run_completeness.md"),
        ]
    )
    completeness = read_json(RUN_DIR / "run_completeness.json")
    created_files = file_list(RUN_DIR)
    leakage_checks = {
        "stdout_has_no_secret": not contains_secret(failed_run["stdout_tail"]),
        "stderr_has_no_secret": not contains_secret(failed_run["stderr_tail"]),
        "run_error_has_no_secret": not contains_secret(run_error or {}),
    }
    expected_error_shape = bool(
        run_error
        and run_error.get("stage") == "api_call"
        and run_error.get("candidate_id") == "candidate_0001"
        and run_error.get("condition") == "llm_only"
        and run_error.get("records_completed") == 0
        and run_error.get("partial_reviews_path")
        and "must not be used as an experiment result" in str(run_error.get("note", ""))
    )
    failure_message = failed_run["stdout_tail"] + failed_run["stderr_tail"]
    completeness_rejects_run = bool(
        completeness
        and completeness.get("passed") is False
        and completeness.get("checks", {}).get("no_run_error_file") is False
    )
    passed = bool(
        failed_run["exit_code"] != 0
        and "run_error.json" in failure_message
        and run_error_path.exists()
        and expected_error_shape
        and all(leakage_checks.values())
        and completeness_run["exit_code"] == 0
        and completeness_rejects_run
    )
    return {
        "passed": passed,
        "work_dir": WORK_DIR.as_posix(),
        "run_dir": RUN_DIR.as_posix(),
        "failed_run": failed_run,
        "run_error_path": run_error_path.as_posix(),
        "run_error": run_error,
        "created_files": created_files,
        "leakage_checks": leakage_checks,
        "expected_error_shape": expected_error_shape,
        "completeness_run": completeness_run,
        "completeness": completeness,
        "completeness_rejects_run": completeness_rejects_run,
        "boundary": "This audit uses a local refused connection and must not reach OpenRouter or any model API.",
    }


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# API Failure Handling Audit",
        "",
        "## Summary",
        "",
        f"- passed: {bool_mark(audit['passed'])}",
        f"- work dir: `{audit['work_dir']}`",
        f"- run dir: `{audit['run_dir']}`",
        f"- runner failed before completion: {bool_mark(audit['failed_run']['exit_code'] != 0)}",
        f"- run_error shape passed: {bool_mark(audit['expected_error_shape'])}",
        f"- stdout has no dummy secret: {bool_mark(audit['leakage_checks']['stdout_has_no_secret'])}",
        f"- stderr has no dummy secret: {bool_mark(audit['leakage_checks']['stderr_has_no_secret'])}",
        f"- run_error has no dummy secret: {bool_mark(audit['leakage_checks']['run_error_has_no_secret'])}",
        f"- completeness rejects failed run: {bool_mark(audit['completeness_rejects_run'])}",
        "",
        "## Boundary",
        "",
        audit["boundary"],
        "",
    ]
    if not audit["passed"]:
        lines.extend(
            [
                "## Debug",
                "",
                f"- failed run exit code: {audit['failed_run']['exit_code']}",
                f"- failed run stdout tail: `{audit['failed_run']['stdout_tail']}`",
                f"- failed run stderr tail: `{audit['failed_run']['stderr_tail']}`",
                "",
            ]
        )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit API mid-run failure handling without external model calls.")
    parser.add_argument("--out-json", default="outputs/api_failure_handling/latest.json")
    parser.add_argument("--out-md", default="outputs/api_failure_handling/latest.md")
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
