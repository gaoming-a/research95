"""Run visible tests for the EVP-8 realistic agent-patch cohort.

This is a no-API execution step. It reads only model-visible patch packets,
recreates patched workdirs from clean buggy checkouts, runs the declared visible
tests, and writes visible-tool evidence without hidden labels or oracle fields.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = REPO_ROOT / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_patch_candidates import apply_patch, copy_checkout, remove_tree, source_root_default  # noqa: E402


COHORT_ID = "EVP-8-REALISTIC-AGENT"
DEFAULT_MODEL_VISIBLE_IN = REPO_ROOT / "data" / "evidence" / "evp8_realistic_agent_model_visible_seed_v0_1.jsonl"
DEFAULT_WORKDIR_ROOT = REPO_ROOT / "outputs" / "evp8_realistic_agent_visible_tests_v0_1" / "workdirs"
DEFAULT_OUTCOMES_OUT = REPO_ROOT / "data" / "evidence" / "evp8_realistic_agent_visible_test_outcomes_v0_1.jsonl"
DEFAULT_SUMMARY_OUT = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_visible_test_outcomes_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_realistic_agent_visible_test_outcomes_v0_1.md"
LEGACY_PY311_PYTEST = REPO_ROOT / "scripts" / "run_pytest_legacy_py311.py"

PROJECT_PYTHONS = {
    "bugsinpy_PySnooper_1": REPO_ROOT / "outputs" / "envs" / "pysnooper_p2p_py311" / "Scripts" / "python.exe",
    "bugsinpy_PySnooper_3": REPO_ROOT / "outputs" / "envs" / "pysnooper3_p2p_py311" / "Scripts" / "python.exe",
    "cookiecutter": REPO_ROOT / "outputs" / "envs" / "cookiecutter_p2p_py311" / "Scripts" / "python.exe",
}

FORBIDDEN_OUTPUT_MARKERS = (
    "expected_outcome",
    "hidden_oracles",
    "oracle_passed",
    "oracle_result",
    "oracle_ran",
    "candidate_type",
    "source_patch_id",
    "source_model_candidate_id",
    "raw_generation",
    "validation_status",
    "model_candidate_id",
    "label_confidence",
    "normalized_label",
    "agent_patch_",
    "reference_fix",
)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{display_path(path)}:{line_number} must contain a JSON object")
        rows.append(value)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def display_path(path: Path) -> str:
    absolute = path if path.is_absolute() else REPO_ROOT / path
    try:
        return absolute.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(absolute)


def python_for(packet: dict[str, Any]) -> tuple[str, str]:
    task_python = PROJECT_PYTHONS.get(str(packet.get("task_id")))
    if task_python and task_python.exists():
        return str(task_python), display_path(task_python)
    project_python = PROJECT_PYTHONS.get(str(packet.get("project")))
    if project_python and project_python.exists():
        return str(project_python), display_path(project_python)
    return sys.executable, "current_process_python"


def pytest_command_for(packet: dict[str, Any], python_executable: str, tests: list[str]) -> list[str]:
    if packet.get("project") == "PySnooper":
        return [python_executable, str(LEGACY_PY311_PYTEST), "-q", *tests]
    if packet.get("project") == "cookiecutter":
        return [python_executable, "-m", "pytest", "-q", "-o", "addopts=", *tests]
    return [python_executable, "-m", "pytest", "-q", *tests]


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


def run_command(command: list[str], cwd: Path, timeout_seconds: int) -> dict[str, Any]:
    started = time.monotonic()
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(cwd) if not existing else str(cwd) + os.pathsep + existing
    process: subprocess.Popen[str] | None = None
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
        stdout, stderr = process.communicate(timeout=timeout_seconds)
        return {
            "exit_code": process.returncode,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "timeout": False,
            "stdout": stdout,
            "stderr": stderr,
        }
    except subprocess.TimeoutExpired:
        if process is not None:
            terminate(process)
            stdout, stderr = process.communicate(timeout=5)
        else:
            stdout, stderr = "", ""
        return {
            "exit_code": None,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "timeout": True,
            "stdout": stdout,
            "stderr": stderr,
        }


def sanitized_tail(text: str, workdir: Path, limit: int = 1200) -> str:
    value = text or ""
    replacements = {
        str(workdir): "<candidate_workdir>",
        str(workdir).replace("\\", "/"): "<candidate_workdir>",
        str(REPO_ROOT): "<repo_root>",
        str(REPO_ROOT).replace("\\", "/"): "<repo_root>",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value[-limit:]


def outcome_from_result(result: dict[str, Any]) -> tuple[str, str]:
    if result.get("timeout"):
        return "timeout", "timeout"
    if result.get("exit_code") == 0:
        return "completed", "passed"
    if result.get("exit_code") == 1:
        return "completed", "failed"
    return "error", "error"


def listed_tests(packet: dict[str, Any]) -> list[str]:
    evidence = packet.get("visible_test_evidence") or {}
    tests = evidence.get("listed_tests")
    if isinstance(tests, list):
        return [str(test) for test in tests if str(test)]
    return []


def visible_record(
    packet: dict[str, Any],
    source_root: Path,
    workdir_root: Path,
    apply_timeout_seconds: int,
    test_timeout_seconds: int,
    run: bool,
    keep_workdirs: bool,
) -> dict[str, Any]:
    tests = listed_tests(packet)
    candidate_id = str(packet["candidate_id"])
    workdir = workdir_root / candidate_id
    blockers: list[str] = []
    if not tests:
        blockers.append("missing_visible_tests")
    if not packet.get("patch_text"):
        blockers.append("missing_patch_text")

    base = {
        "cohort_id": COHORT_ID,
        "candidate_id": candidate_id,
        "task_id": packet.get("task_id"),
        "project": packet.get("project"),
        "visible_tests": tests,
        "execution_boundary": {
            "api_call_attempted": False,
            "hidden_labels_read": False,
            "oracle_fields_read": False,
            "source": "model_visible_seed",
            "stdout_stderr_tails_stored": True,
        },
    }
    if blockers:
        return base | {
            "run_status": "blocked",
            "blockers": blockers,
            "patch_apply_summary": {"attempted": False, "applied": False, "reason": "blocked_before_apply"},
            "visible_run_summary": {"outcome": "blocked", "test_count": len(tests), "passed": False},
            "test_results": [{"test_name": test, "outcome": "not_run_blocked"} for test in tests],
        }
    if not run:
        python_executable, python_source = python_for(packet)
        command = pytest_command_for(packet, python_executable, tests)
        return base | {
            "run_status": "planned",
            "blockers": [],
            "execution_boundary": base["execution_boundary"] | {
                "python_source": python_source,
                "legacy_py311_wrapper": command[1] == str(LEGACY_PY311_PYTEST),
                "pytest_addopts_overridden": packet.get("project") == "cookiecutter",
            },
            "patch_apply_summary": {"attempted": "planned", "applied": "planned"},
            "visible_run_summary": {"outcome": "planned", "test_count": len(tests), "passed": False},
            "test_results": [{"test_name": test, "outcome": "planned"} for test in tests],
            "command_shape": [Path(str(command[0])).name, *command[1:]],
        }

    copy_checkout(source_root, packet, workdir)
    patch_result = apply_patch(packet, workdir, apply_timeout_seconds)
    if not patch_result.get("applied"):
        record = base | {
            "run_status": "blocked",
            "blockers": ["patch_apply_failed"],
            "patch_apply_summary": {
                "attempted": bool(patch_result.get("attempted")),
                "applied": False,
                "exit_code": patch_result.get("exit_code"),
                "stdout_tail": sanitized_tail(str(patch_result.get("stdout_tail") or ""), workdir),
                "stderr_tail": sanitized_tail(str(patch_result.get("stderr_tail") or ""), workdir),
            },
            "visible_run_summary": {"outcome": "not_run_patch_apply_failed", "test_count": len(tests), "passed": False},
            "test_results": [{"test_name": test, "outcome": "not_run_patch_apply_failed"} for test in tests],
        }
        if not keep_workdirs:
            remove_tree(workdir)
        return record

    python_executable, python_source = python_for(packet)
    command = pytest_command_for(packet, python_executable, tests)
    result = run_command(command, workdir, test_timeout_seconds)
    run_status, outcome = outcome_from_result(result)
    record = base | {
        "run_status": run_status,
        "blockers": [],
        "execution_boundary": base["execution_boundary"] | {
            "python_source": python_source,
            "legacy_py311_wrapper": command[1] == str(LEGACY_PY311_PYTEST),
            "pytest_addopts_overridden": packet.get("project") == "cookiecutter",
        },
        "patch_apply_summary": {
            "attempted": bool(patch_result.get("attempted")),
            "applied": True,
            "exit_code": patch_result.get("exit_code"),
        },
        "elapsed_seconds": result["elapsed_seconds"],
        "exit_code": result["exit_code"],
        "timeout": result["timeout"],
        "visible_run_summary": {"outcome": outcome, "test_count": len(tests), "passed": outcome == "passed"},
        "test_results": [{"test_name": test, "outcome": outcome} for test in tests],
        "stdout_tail": sanitized_tail(result["stdout"], workdir),
        "stderr_tail": sanitized_tail(result["stderr"], workdir),
    }
    if not keep_workdirs:
        remove_tree(workdir)
    return record


def counts(values: Any) -> dict[str, int]:
    return dict(sorted(Counter(str(value) for value in values).items()))


def build_summary(records: list[dict[str, Any]], run: bool) -> dict[str, Any]:
    status_by_task: dict[str, Counter[str]] = {}
    for record in records:
        status_by_task.setdefault(str(record["task_id"]), Counter())[str(record["run_status"])] += 1
    outcomes = [result["outcome"] for record in records for result in record.get("test_results", [])]
    return {
        "analysis_id": "evp8_realistic_agent_visible_test_outcomes_v0_1",
        "cohort_id": COHORT_ID,
        "mode": "run" if run else "dry_run",
        "api_call_attempted": False,
        "hidden_labels_read": False,
        "oracle_fields_read": False,
        "raw_model_outputs_read": False,
        "record_count": len(records),
        "run_status_counts": counts(record["run_status"] for record in records),
        "run_status_counts_by_task": {task: dict(sorted(counter.items())) for task, counter in sorted(status_by_task.items())},
        "test_outcome_counts": counts(outcomes),
        "completed_or_error_or_timeout_count": sum(1 for record in records if record["run_status"] in {"completed", "error", "timeout"}),
        "blocked_count": sum(1 for record in records if record["run_status"] == "blocked"),
        "patch_apply_failed_count": sum(1 for record in records if "patch_apply_failed" in record.get("blockers", [])),
        "leakage_policy": "visible-test records exclude evaluator labels, oracle outcomes, source ids, prompts, and raw model responses",
    }


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# EVP-8 Realistic Agent Visible Test Outcomes v0.1",
        "",
        "Date: 2026-06-30",
        "",
        "This no-API run records visible test outcomes for the realistic",
        "agent-patch cohort. It uses model-visible patch packets and does not",
        "emit hidden labels, oracle outcomes, source ids, prompts, or raw model",
        "responses.",
        "",
        f"- mode: `{summary['mode']}`",
        f"- records: {summary['record_count']}",
        f"- completed/error/timeout: {summary['completed_or_error_or_timeout_count']}",
        f"- blocked: {summary['blocked_count']}",
        f"- patch apply failed: {summary['patch_apply_failed_count']}",
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


def check_outputs(records: list[dict[str, Any]], summary: dict[str, Any], expected_count: int | None) -> None:
    if expected_count is not None and summary["record_count"] != expected_count:
        raise SystemExit(f"expected {expected_count} records, got {summary['record_count']}")
    if summary["record_count"] <= 0:
        raise SystemExit("no visible-test records generated")
    serialized = json.dumps(records, ensure_ascii=False)
    for marker in FORBIDDEN_OUTPUT_MARKERS:
        if marker in serialized:
            raise SystemExit(f"forbidden marker leaked into visible-test outcomes: {marker}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-visible-in", type=Path, default=DEFAULT_MODEL_VISIBLE_IN)
    parser.add_argument("--source-workspace-root", type=Path, default=source_root_default())
    parser.add_argument("--workdir-root", type=Path, default=DEFAULT_WORKDIR_ROOT)
    parser.add_argument("--outcomes-out", type=Path, default=DEFAULT_OUTCOMES_OUT)
    parser.add_argument("--summary-out", type=Path, default=DEFAULT_SUMMARY_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--apply-timeout-seconds", type=int, default=30)
    parser.add_argument("--test-timeout-seconds", type=int, default=90)
    parser.add_argument("--expected-count", type=int, default=53)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--keep-workdirs", action="store_true")
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    packets = read_jsonl(args.model_visible_in)
    source_root = args.source_workspace_root
    if not source_root.exists():
        raise FileNotFoundError(f"source workspace root does not exist: {source_root}")
    args.workdir_root.mkdir(parents=True, exist_ok=True)
    records = []
    for index, packet in enumerate(packets, start=1):
        record = visible_record(
            packet=packet,
            source_root=source_root,
            workdir_root=args.workdir_root,
            apply_timeout_seconds=args.apply_timeout_seconds,
            test_timeout_seconds=args.test_timeout_seconds,
            run=args.run,
            keep_workdirs=args.keep_workdirs,
        )
        records.append(record)
        print(f"[{index}/{len(packets)}] {record['candidate_id']} {record['run_status']} {record['visible_run_summary']['outcome']}")
    summary = build_summary(records, run=args.run)
    write_jsonl(args.outcomes_out, records)
    write_json(args.summary_out, summary)
    write_markdown(args.md_out, summary)
    if args.check:
        check_outputs(records, summary, args.expected_count)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
