"""Run predeclared EVP-7 visible tests as an independent evidence source.

This runner does not read or emit evaluator labels. It uses the existing
candidate workdirs only as execution sandboxes and records model-visible test
outcomes for E4 evidence packets.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CANDIDATES_IN = REPO_ROOT / "data" / "patches" / "evp7_candidates.jsonl"
OUTCOMES_OUT = REPO_ROOT / "data" / "evidence" / "evp7_visible_test_outcomes.jsonl"
SUMMARY_OUT = REPO_ROOT / "data" / "evidence" / "evp7_visible_test_outcome_summary.json"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )


def _validation_row(candidate: dict[str, Any]) -> dict[str, Any]:
    validation_path = REPO_ROOT / candidate["source_files"]["validation_jsonl"]
    rows = _read_jsonl(validation_path)
    for row in rows:
        if row.get("model_candidate_id") == candidate.get("source_model_candidate_id"):
            return row
    raise SystemExit(f"missing validation row for {candidate['evp7_candidate_id']}")


def _python_executable(validation: dict[str, Any]) -> str | None:
    for result in validation.get("oracle_result", {}).get("results", []):
        command = result.get("command") or []
        if command:
            return command[0]
    return None


def _candidate_workdir(candidate: dict[str, Any]) -> tuple[Path | None, str | None]:
    validation_path = REPO_ROOT / candidate["source_files"]["validation_jsonl"]
    base = validation_path.parent
    local_id = candidate["source_model_candidate_id"]
    for dirname in ("p2p_workdirs", "candidate_workdirs"):
        workdir = base / dirname / local_id
        if workdir.exists():
            return workdir, dirname
    return None, None


def _pytest_command(python_executable: str, tests: list[str], addopts_override: str | None) -> list[str]:
    command = [python_executable, "-m", "pytest"]
    if addopts_override is not None:
        command.extend(["-o", f"addopts={addopts_override}"])
    command.extend(["-q", *tests])
    return command


def _unittest_command(python_executable: str, tests: list[str]) -> list[str]:
    return [python_executable, "-m", "unittest", "-q", *tests]


def _test_command(
    python_executable: str,
    tests: list[str],
    addopts_override: str | None,
    test_framework: str | None,
) -> list[str]:
    if test_framework == "unittest":
        return _unittest_command(python_executable, tests)
    return _pytest_command(python_executable, tests, addopts_override)


def _terminate(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        try:
            process.send_signal(signal.CTRL_BREAK_EVENT)
        except Exception:
            process.terminate()
    else:
        process.terminate()


def _run(command: list[str], cwd: Path, timeout: int, pythonpath: Path | None) -> dict[str, Any]:
    start = time.monotonic()
    process: subprocess.Popen[str] | None = None
    env = os.environ.copy()
    if pythonpath is not None:
        existing = env.get("PYTHONPATH")
        env["PYTHONPATH"] = str(pythonpath) if not existing else str(pythonpath) + os.pathsep + existing
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
            "stdout_tail": _tail(stdout),
            "stderr_tail": _tail(stderr),
        }
    except subprocess.TimeoutExpired:
        if process is not None:
            _terminate(process)
            stdout, stderr = process.communicate(timeout=5)
        else:
            stdout, stderr = "", ""
        return {
            "exit_code": None,
            "elapsed_seconds": round(time.monotonic() - start, 3),
            "timeout": True,
            "stdout_tail": _tail(stdout),
            "stderr_tail": _tail(stderr),
        }


def _tail(text: str, limit: int = 600) -> str:
    text = text or ""
    return text[-limit:]


def _scope_compat_shim(candidate: dict[str, Any]) -> tuple[Path | None, dict[str, Any]]:
    manifest_rel = candidate.get("source_files", {}).get("p2p_manifest")
    if not manifest_rel:
        return None, {"enabled": False, "reason": "missing_p2p_manifest"}
    manifest_path = REPO_ROOT / manifest_rel
    if not manifest_path.exists():
        return None, {"enabled": False, "p2p_manifest": manifest_rel, "reason": "missing_p2p_manifest_file"}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    compat = manifest.get("compat_shim", {})
    if not compat.get("enabled") or not compat.get("path"):
        return None, {"enabled": False, "p2p_manifest": manifest_rel, "reason": "compat_shim_not_enabled"}
    compat_path = REPO_ROOT / compat["path"]
    if not compat_path.exists():
        return None, {"enabled": False, "p2p_manifest": manifest_rel, "reason": "missing_compat_shim_path"}
    return compat_path, {
        "enabled": True,
        "p2p_manifest": manifest_rel,
        "compat_shim_path": compat["path"],
        "source": "tracked_p2p_scope_manifest",
        "test_framework": manifest.get("test_framework"),
    }


def _outcome_record(
    candidate: dict[str, Any],
    validation: dict[str, Any],
    dry_run: bool,
    timeout: int,
) -> dict[str, Any]:
    tests = list(candidate.get("visible_tests") or [])
    workdir, workdir_kind = _candidate_workdir(candidate)
    python_executable = _python_executable(validation)
    blockers = []
    if not tests:
        blockers.append("missing_visible_tests")
    if workdir is None:
        blockers.append("missing_candidate_workdir")
    if not python_executable:
        blockers.append("missing_python_executable")
    compat_path, compat_record = _scope_compat_shim(candidate)

    base_record: dict[str, Any] = {
        "cohort_id": "EVP-7",
        "candidate_id": candidate["evp7_candidate_id"],
        "task_id": candidate["task_id"],
        "project": candidate["project"],
        "visible_tests": tests,
        "source_files": {
            "candidate_jsonl": candidate["source_files"]["candidate_jsonl"],
            "validation_jsonl": candidate["source_files"]["validation_jsonl"],
        },
        "execution_source": {
            "candidate_workdir_kind": workdir_kind,
            "python_source": "validation_oracle_command_python",
            "pytest_addopts_override": validation.get("pytest_addopts_override"),
            "compat_shim": compat_record,
        },
    }
    if blockers:
        return base_record | {
            "run_status": "blocked",
            "blockers": blockers,
            "test_results": [
                {"test_name": test, "outcome": "not_run_blocked"}
                for test in tests
            ],
        }

    command = _test_command(
        str(python_executable),
        tests,
        validation.get("pytest_addopts_override"),
        compat_record.get("test_framework"),
    )
    if dry_run:
        return base_record | {
            "run_status": "planned",
            "blockers": [],
            "test_results": [
                {"test_name": test, "outcome": "planned"}
                for test in tests
            ],
        }

    result = _run(command, workdir, timeout, compat_path)
    if result["timeout"]:
        outcome = "timeout"
        run_status = "timeout"
    elif result["exit_code"] == 0:
        outcome = "passed"
        run_status = "completed"
    elif result["exit_code"] == 1:
        outcome = "failed"
        run_status = "completed"
    else:
        outcome = "error"
        run_status = "error"
    return base_record | {
        "run_status": run_status,
        "blockers": [],
        "elapsed_seconds": result["elapsed_seconds"],
        "exit_code": result["exit_code"],
        "timeout": result["timeout"],
        "test_results": [
            {"test_name": test, "outcome": outcome}
            for test in tests
        ],
        "visible_run_summary": {
            "passed": outcome == "passed",
            "outcome": outcome,
            "test_count": len(tests),
        },
    }


def build_outcomes(candidates_path: Path, dry_run: bool, timeout: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    candidates = _read_jsonl(candidates_path)
    records = [
        _outcome_record(candidate, _validation_row(candidate), dry_run=dry_run, timeout=timeout)
        for candidate in candidates
    ]
    status_by_task: dict[str, dict[str, int]] = {}
    for record in records:
        task_counts = status_by_task.setdefault(record["task_id"], {})
        status = record["run_status"]
        task_counts[status] = task_counts.get(status, 0) + 1
    summary = {
        "cohort_id": "EVP-7",
        "candidate_count": len(candidates),
        "record_count": len(records),
        "mode": "dry_run" if dry_run else "run",
        "run_status_counts": _counts(record["run_status"] for record in records),
        "run_status_counts_by_task": dict(sorted(status_by_task.items())),
        "test_outcome_counts": _counts(
            result["outcome"]
            for record in records
            for result in record.get("test_results", [])
        ),
        "blocked_count": sum(1 for record in records if record["run_status"] == "blocked"),
        "complete_visible_outcome_count": sum(
            1 for record in records if record["run_status"] in {"completed", "error", "timeout"}
        ),
        "leakage_policy": "records contain visible test names and outcomes only; evaluator labels are not read or emitted",
    }
    return records, summary


def _counts(values: Any) -> dict[str, int]:
    result: dict[str, int] = {}
    for value in values:
        key = str(value)
        result[key] = result.get(key, 0) + 1
    return dict(sorted(result.items()))


def _check(records: list[dict[str, Any]], summary: dict[str, Any], dry_run: bool) -> None:
    if summary["candidate_count"] != 46:
        raise SystemExit(f"EVP-7 candidate count changed: {summary['candidate_count']} != 46")
    if summary["record_count"] != 46:
        raise SystemExit(f"visible outcome record count changed: {summary['record_count']} != 46")
    forbidden = (
        "label_with_p2p_broad",
        "label_retained_oracle",
        "candidate_type",
        "failure_type_label",
        "expected_outcome",
        "hidden_oracles",
        "patch_id",
    )
    serialized = json.dumps(records, ensure_ascii=False)
    for marker in forbidden:
        if marker in serialized:
            raise SystemExit(f"forbidden marker leaked into visible outcomes: {marker}")
    if dry_run and summary["blocked_count"] != 0:
        raise SystemExit("dry-run plan has blocked candidates")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates-in", type=Path, default=CANDIDATES_IN)
    parser.add_argument("--outcomes-out", type=Path, default=OUTCOMES_OUT)
    parser.add_argument("--summary-out", type=Path, default=SUMMARY_OUT)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--run", action="store_true", help="Execute pytest instead of writing a dry-run plan.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    dry_run = not args.run
    records, summary = build_outcomes(args.candidates_in, dry_run=dry_run, timeout=args.timeout)
    _write_jsonl(args.outcomes_out, records)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.check:
        _check(records, summary, dry_run=dry_run)

    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
