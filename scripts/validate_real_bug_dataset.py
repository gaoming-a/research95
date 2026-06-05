from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = {
    "bug_id",
    "source",
    "project",
    "language",
    "buggy_workdir",
    "fixed_workdir",
    "buggy_test_command",
    "fixed_test_command",
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate real-bug metadata and optionally execute buggy/fixed regression tests."
    )
    parser.add_argument("--metadata", required=True, help="JSONL metadata file for real engineering bugs.")
    parser.add_argument("--root", default=".", help="Root used to resolve relative workdir paths.")
    parser.add_argument("--out", required=True, help="Output JSONL validation report.")
    parser.add_argument("--run-tests", action="store_true", help="Execute test commands instead of schema checks only.")
    parser.add_argument("--timeout-seconds", type=int, default=120)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    records = read_jsonl(Path(args.metadata))
    results = [
        validate_record(
            record=record,
            root=root,
            run_tests=args.run_tests,
            timeout_seconds=args.timeout_seconds,
        )
        for record in records
    ]
    write_jsonl(Path(args.out), results)
    print(
        json.dumps(
            {
                "records": len(results),
                "schema_valid": sum(1 for row in results if row["schema_valid"]),
                "buggy_failed": sum(1 for row in results if row.get("buggy_test", {}).get("outcome") == "expected_fail"),
                "fixed_passed": sum(1 for row in results if row.get("fixed_test", {}).get("outcome") == "expected_pass"),
                "out": args.out,
            },
            indent=2,
        )
    )


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number} must contain a JSON object")
        rows.append(value)
    return rows


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def validate_record(
    record: dict[str, Any],
    root: Path,
    run_tests: bool,
    timeout_seconds: int,
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(REQUIRED_FIELDS - set(record))
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")

    buggy_workdir = resolve_inside_root(root, str(record.get("buggy_workdir", "")), errors, "buggy_workdir")
    fixed_workdir = resolve_inside_root(root, str(record.get("fixed_workdir", "")), errors, "fixed_workdir")

    for field in ("buggy_test_command", "fixed_test_command"):
        if not isinstance(record.get(field), str) or not record.get(field, "").strip():
            errors.append(f"{field} must be a non-empty command string")

    result: dict[str, Any] = {
        "bug_id": record.get("bug_id"),
        "source": record.get("source"),
        "project": record.get("project"),
        "schema_valid": not errors,
        "errors": errors,
    }
    if errors or not run_tests:
        result["status"] = "schema_only" if not errors else "invalid_metadata"
        return result

    result["buggy_test"] = run_command(
        command=str(record["buggy_test_command"]),
        cwd=buggy_workdir,
        cwd_label=str(record["buggy_workdir"]),
        timeout_seconds=timeout_seconds,
        expected_exit_code=record.get("buggy_expected_exit_code", "nonzero"),
    )
    result["fixed_test"] = run_command(
        command=str(record["fixed_test_command"]),
        cwd=fixed_workdir,
        cwd_label=str(record["fixed_workdir"]),
        timeout_seconds=timeout_seconds,
        expected_exit_code=record.get("fixed_expected_exit_code", 0),
    )
    result["status"] = (
        "validated"
        if result["buggy_test"]["outcome"] == "expected_fail"
        and result["fixed_test"]["outcome"] == "expected_pass"
        else "test_mismatch"
    )
    return result


def resolve_inside_root(root: Path, value: str, errors: list[str], field: str) -> Path:
    if not value:
        errors.append(f"{field} is empty")
        return root
    path = (root / value).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        errors.append(f"{field} escapes root: {value}")
        return path
    if not path.exists() or not path.is_dir():
        errors.append(f"{field} does not exist or is not a directory: {value}")
    return path


def run_command(
    command: str,
    cwd: Path,
    cwd_label: str,
    timeout_seconds: int,
    expected_exit_code: int | str,
) -> dict[str, Any]:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
        )
        elapsed = time.monotonic() - started
        return {
            "command": command,
            "cwd": cwd_label,
            "exit_code": completed.returncode,
            "elapsed_seconds": round(elapsed, 3),
            "outcome": classify_exit(completed.returncode, expected_exit_code),
            "stdout_tail": tail(completed.stdout),
            "stderr_tail": tail(completed.stderr),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "cwd": cwd_label,
            "exit_code": None,
            "elapsed_seconds": timeout_seconds,
            "outcome": "timeout",
            "stdout_tail": tail(exc.stdout if isinstance(exc.stdout, str) else ""),
            "stderr_tail": tail(exc.stderr if isinstance(exc.stderr, str) else ""),
        }


def classify_exit(exit_code: int, expected_exit_code: int | str) -> str:
    if expected_exit_code == "nonzero":
        return "expected_fail" if exit_code != 0 else "unexpected_pass"
    expected = int(expected_exit_code)
    if exit_code == expected:
        return "expected_pass" if expected == 0 else "expected_fail"
    return "unexpected_fail" if exit_code != 0 else "unexpected_pass"


def tail(text: str, max_chars: int = 2000) -> str:
    return text[-max_chars:] if len(text) > max_chars else text


if __name__ == "__main__":
    main()
