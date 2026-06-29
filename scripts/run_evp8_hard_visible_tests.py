"""Run visible tests for the no-API EVP-8-HARD candidate draft.

The runner uses candidate execution sandboxes only as patched workdirs. It does
not emit evaluator labels, hidden oracle outcomes, source patch ids, prompts, or
raw model responses.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import time
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATOR_IN = REPO_ROOT / "data" / "patches" / "evp8_hard_evaluator_manifest_v0_1.jsonl"
OUTCOMES_OUT = REPO_ROOT / "data" / "evidence" / "evp8_hard_visible_test_outcomes_v0_1.jsonl"
SUMMARY_OUT = REPO_ROOT / "data" / "protocols" / "evp8_hard_visible_test_outcome_summary_v0_1.json"
MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_hard_visible_test_outcomes_v0_1.md"
HTTPIE_LEGACY_PYTEST = REPO_ROOT / "scripts" / "run_pytest_legacy_httpie.py"
HTTPIE_VISIBLE_TEST_PYTHON = REPO_ROOT / "outputs" / "envs" / "httpie_hard_visible_py311" / "Scripts" / "python.exe"

FORBIDDEN_OUTPUT_MARKERS = (
    "expected_outcome",
    "hidden_oracles",
    "oracle_passed",
    "candidate_type",
    "patch_id",
    "source_patch_id",
    "raw_generation",
    "validation_status",
    "model_candidate_id",
    "label_confidence",
    "normalized_label",
    "agent_patch_",
    "ai_patch_",
    "reference_fix",
    "empty_diff_control",
    "comment_only_patch",
    "missing_change",
)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def display_path(path: Path) -> str:
    absolute = path if path.is_absolute() else REPO_ROOT / path
    try:
        return absolute.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(absolute)


def validation_rows(source_candidate_file: str) -> list[dict[str, Any]]:
    source_path = REPO_ROOT / source_candidate_file
    rows: list[dict[str, Any]] = []
    for name in ("validation.jsonl", "p2p_validation.jsonl", "oracle_validation.jsonl"):
        path = source_path.parent / name
        if path.exists():
            rows.extend(read_jsonl(path))
    return rows


def validation_for(candidate: dict[str, Any]) -> dict[str, Any] | None:
    source_patch_id = candidate.get("source_patch_id")
    source_model_candidate_id = candidate.get("source_model_candidate_id")
    for row in validation_rows(str(candidate["source_candidate_file"])):
        if source_patch_id and row.get("patch_id") == source_patch_id:
            return row
        if source_model_candidate_id and row.get("model_candidate_id") == source_model_candidate_id:
            return row
    return None


def workdir_for(candidate: dict[str, Any], validation: dict[str, Any] | None) -> tuple[Path | None, str]:
    source_path = REPO_ROOT / str(candidate["source_candidate_file"])
    parent = source_path.parent
    source_patch_id = str(candidate.get("source_patch_id") or "")
    source_model_candidate_id = str(candidate.get("source_model_candidate_id") or "")
    candidates = [
        (parent / "agent_workdirs" / source_patch_id, "source_agent_workdir_by_stable_source_key"),
        (parent / "workdirs" / source_model_candidate_id, "source_workdir_by_local_candidate_key"),
        (parent / "workdirs" / source_patch_id, "source_workdir_by_stable_source_key"),
    ]
    if validation:
        command = (validation.get("patch_result") or {}).get("command") or []
        for part in command:
            part_text = str(part)
            if part_text.endswith(".candidate.patch"):
                candidates.append((Path(part_text).parent, "validation_patch_command_parent"))
    for path, source in candidates:
        if path and path.exists():
            return path, source
    return None, "missing_workdir"


def python_for(candidate: dict[str, Any], validation: dict[str, Any] | None) -> tuple[str, str]:
    if candidate.get("project") == "httpie" and HTTPIE_VISIBLE_TEST_PYTHON.exists():
        return str(HTTPIE_VISIBLE_TEST_PYTHON), "httpie_visible_py311_local_venv"
    if validation:
        for result in (validation.get("oracle_result") or {}).get("results", []):
            command = result.get("command") or []
            if command:
                candidate = Path(str(command[0]))
                if candidate.exists():
                    return str(candidate), "validation_oracle_python"
    return os.sys.executable, "current_process_python"


def pytest_command_for(candidate: dict[str, Any], python_executable: str, tests: list[str]) -> list[str]:
    if candidate.get("project") == "httpie" and Path(python_executable) == HTTPIE_VISIBLE_TEST_PYTHON:
        return [python_executable, str(HTTPIE_LEGACY_PYTEST), "-q", *tests]
    return [python_executable, "-m", "pytest", "-q", *tests]


def run_command(command: list[str], cwd: Path, timeout: int) -> dict[str, Any]:
    start = time.monotonic()
    process: subprocess.Popen[str] | None = None
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(cwd) if not existing else str(cwd) + os.pathsep + existing
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
        )
        stdout, stderr = process.communicate(timeout=timeout)
        return {
            "exit_code": process.returncode,
            "elapsed_seconds": round(time.monotonic() - start, 3),
            "timeout": False,
            "stdout_tail": tail(stdout),
            "stderr_tail": tail(stderr),
        }
    except subprocess.TimeoutExpired:
        if process is not None:
            terminate(process)
            stdout, stderr = process.communicate(timeout=5)
        else:
            stdout, stderr = "", ""
        return {
            "exit_code": None,
            "elapsed_seconds": round(time.monotonic() - start, 3),
            "timeout": True,
            "stdout_tail": tail(stdout),
            "stderr_tail": tail(stderr),
        }


def terminate(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        try:
            process.send_signal(signal.CTRL_BREAK_EVENT)
        except Exception:
            process.terminate()
    else:
        process.terminate()


def tail(text: str, limit: int = 500) -> str:
    return (text or "")[-limit:]


def sanitized_tail(text: str, workdir: Path, limit: int = 500) -> str:
    value = text or ""
    replacements = {
        str(workdir): "<candidate_workdir>",
        str(workdir).replace("\\", "/"): "<candidate_workdir>",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value[-limit:]


def outcome_from_result(result: dict[str, Any]) -> tuple[str, str]:
    if result["timeout"]:
        return "timeout", "timeout"
    if result["exit_code"] == 0:
        return "completed", "passed"
    if result["exit_code"] == 1:
        return "completed", "failed"
    return "error", "error"


def outcome_record(candidate: dict[str, Any], run: bool, timeout: int) -> dict[str, Any]:
    tests = list(candidate.get("visible_tests_declared") or [])
    validation = validation_for(candidate)
    workdir, workdir_source = workdir_for(candidate, validation)
    blockers = []
    if not tests:
        blockers.append("missing_visible_tests")
    if validation is None:
        blockers.append("missing_validation_record")
    if workdir is None:
        blockers.append("missing_candidate_workdir")

    base = {
        "cohort_id": "EVP-8-HARD",
        "candidate_id": candidate["hard_candidate_id"],
        "task_id": candidate["task_id"],
        "project": candidate["project"],
        "visible_tests": tests,
        "execution_boundary": {
            "workdir_source": workdir_source,
            "stdout_stderr_tails_stored": True,
            "api_call_attempted": False,
        },
    }
    if blockers:
        return base | {
            "run_status": "blocked",
            "blockers": blockers,
            "test_results": [{"test_name": test, "outcome": "not_run_blocked"} for test in tests],
        }
    assert validation is not None and workdir is not None
    python_executable, python_source = python_for(candidate, validation)
    command = pytest_command_for(candidate, python_executable, tests)
    if not run:
        return base | {
            "run_status": "planned",
            "blockers": [],
            "execution_boundary": base["execution_boundary"] | {
                "python_source": python_source,
                "legacy_httpie_wrapper": command[1] == str(HTTPIE_LEGACY_PYTEST),
            },
            "test_results": [{"test_name": test, "outcome": "planned"} for test in tests],
        }
    result = run_command(command, workdir, timeout)
    run_status, outcome = outcome_from_result(result)
    return base | {
        "run_status": run_status,
        "blockers": [],
        "execution_boundary": base["execution_boundary"] | {
            "python_source": python_source,
            "legacy_httpie_wrapper": command[1] == str(HTTPIE_LEGACY_PYTEST),
        },
        "elapsed_seconds": result["elapsed_seconds"],
        "exit_code": result["exit_code"],
        "timeout": result["timeout"],
        "test_results": [{"test_name": test, "outcome": outcome} for test in tests],
        "visible_run_summary": {
            "outcome": outcome,
            "test_count": len(tests),
            "passed": outcome == "passed",
        },
        "stdout_tail": sanitized_tail(result["stdout_tail"], workdir),
        "stderr_tail": sanitized_tail(result["stderr_tail"], workdir),
    }


def counts(values: Any) -> dict[str, int]:
    return dict(sorted(Counter(str(value) for value in values).items()))


def build_summary(records: list[dict[str, Any]], run: bool) -> dict[str, Any]:
    status_by_task: dict[str, Counter[str]] = {}
    for record in records:
        status_by_task.setdefault(record["task_id"], Counter())[record["run_status"]] += 1
    return {
        "analysis_id": "evp8_hard_visible_test_outcomes_v0_1",
        "cohort_id": "EVP-8-HARD",
        "mode": "run" if run else "dry_run",
        "api_call_attempted": False,
        "raw_model_outputs_read": False,
        "evaluator_labels_emitted": False,
        "record_count": len(records),
        "run_status_counts": counts(record["run_status"] for record in records),
        "run_status_counts_by_task": {task: dict(sorted(counter.items())) for task, counter in sorted(status_by_task.items())},
        "test_outcome_counts": counts(result["outcome"] for record in records for result in record.get("test_results", [])),
        "completed_or_error_or_timeout_count": sum(1 for record in records if record["run_status"] in {"completed", "error", "timeout"}),
        "blocked_count": sum(1 for record in records if record["run_status"] == "blocked"),
        "leakage_policy": "visible-test records exclude evaluator labels, hidden oracle outcomes, source patch ids, prompts, and raw model responses",
    }


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# EVP-8-HARD Visible Test Outcomes v0.1",
        "",
        "Date: 2026-06-29",
        "",
        "This no-API run records visible test outcomes for the hard-case draft. It",
        "does not emit evaluator labels, hidden oracle outcomes, source patch ids,",
        "prompts, or raw model responses.",
        "",
        f"- mode: `{summary['mode']}`",
        f"- records: {summary['record_count']}",
        f"- completed/error/timeout: {summary['completed_or_error_or_timeout_count']}",
        f"- blocked: {summary['blocked_count']}",
        "",
        "Run status counts:",
        "",
    ]
    for key, value in summary["run_status_counts"].items():
        lines.append(f"- `{key}`: {value}")
    lines += ["", "Test outcome counts:", ""]
    for key, value in summary["test_outcome_counts"].items():
        lines.append(f"- `{key}`: {value}")
    lines += ["", "Task status counts:", ""]
    for task, task_counts in summary["run_status_counts_by_task"].items():
        lines.append(f"- `{task}`: `{task_counts}`")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def check_outputs(records: list[dict[str, Any]], summary: dict[str, Any], run: bool) -> None:
    if summary["record_count"] <= 0:
        raise SystemExit("no visible-test records generated")
    serialized = json.dumps(records, ensure_ascii=False)
    for marker in FORBIDDEN_OUTPUT_MARKERS:
        if marker in serialized:
            raise SystemExit(f"forbidden marker leaked into visible-test outcomes: {marker}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluator-in", type=Path, default=EVALUATOR_IN)
    parser.add_argument("--outcomes-out", type=Path, default=OUTCOMES_OUT)
    parser.add_argument("--summary-out", type=Path, default=SUMMARY_OUT)
    parser.add_argument("--md-out", type=Path, default=MD_OUT)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    candidates = read_jsonl(args.evaluator_in)
    records = [outcome_record(candidate, run=args.run, timeout=args.timeout) for candidate in candidates]
    summary = build_summary(records, run=args.run)
    write_jsonl(args.outcomes_out, records)
    write_json(args.summary_out, summary)
    write_markdown(args.md_out, summary)
    if args.check:
        check_outputs(records, summary, run=args.run)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
