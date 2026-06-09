from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import validate_patch_candidates as base_validator


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def resolve_path(path_text: str, repo_root: Path) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else repo_root / path


def run_p2p_chunk(
    python: str,
    workdir: Path,
    nodeids: list[str],
    timeout_seconds: int,
    pythonpath: Path | None,
) -> dict[str, Any]:
    env = os.environ.copy()
    if pythonpath is not None:
        existing = env.get("PYTHONPATH")
        env["PYTHONPATH"] = str(pythonpath.resolve()) if not existing else f"{pythonpath.resolve()}{os.pathsep}{existing}"
    started = time.monotonic()
    process: subprocess.Popen[str] | None = None
    try:
        process = subprocess.Popen(
            [python, "-m", "pytest", "-q", *nodeids],
            cwd=str(workdir),
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
        )
        stdout, stderr = process.communicate(timeout=timeout_seconds)
        return {
            "nodeids": nodeids,
            "nodeid_count": len(nodeids),
            "exit_code": process.returncode,
            "passed": process.returncode == 0,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "timeout": False,
            "stdout_tail": base_validator.tail(stdout),
            "stderr_tail": base_validator.tail(stderr),
        }
    except subprocess.TimeoutExpired as exc:
        if process is not None:
            kill_process_tree(process.pid)
            stdout, stderr = process.communicate()
        else:
            stdout = exc.stdout if isinstance(exc.stdout, str) else ""
            stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return {
            "nodeids": nodeids,
            "nodeid_count": len(nodeids),
            "exit_code": None,
            "passed": False,
            "elapsed_seconds": timeout_seconds,
            "timeout": True,
            "stdout_tail": base_validator.tail(stdout),
            "stderr_tail": base_validator.tail(stderr),
        }


def kill_process_tree(pid: int) -> None:
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return
    subprocess.run(["pkill", "-TERM", "-P", str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def chunks(values: list[str], chunk_size: int) -> list[list[str]]:
    return [values[index : index + chunk_size] for index in range(0, len(values), chunk_size)]


def final_label(patch_applied: bool, oracle_passed: bool, p2p_passed: bool) -> str:
    if not patch_applied:
        return "non_applicable"
    if not oracle_passed:
        return "incorrect_issue_not_fixed"
    if not p2p_passed:
        return "incorrect_regression"
    return "correct_under_f2p_and_p2p_broad"


def validate_candidate(
    candidate: dict[str, Any],
    scope: dict[str, Any],
    source_root: Path,
    workdir_root: Path,
    apply_timeout_seconds: int,
    oracle_timeout_seconds: int,
    p2p_timeout_seconds: int,
    python: str,
    pythonpath: Path | None,
    p2p_batch_size: int,
) -> dict[str, Any]:
    workdir = workdir_root / candidate["model_candidate_id"]
    base_validator.copy_checkout(source_root, candidate, workdir)
    patch_result = base_validator.apply_patch(candidate, workdir, apply_timeout_seconds)
    oracle_result = (
        base_validator.run_oracles(candidate, workdir, oracle_timeout_seconds)
        if patch_result.get("applied")
        else {"ran": False, "passed": False, "reason": "patch_not_applied"}
    )
    p2p_results = []
    if patch_result.get("applied") and oracle_result.get("passed"):
        for nodeids in chunks(list(scope.get("p2p_broad_tests", [])), p2p_batch_size):
            p2p_results.append(run_p2p_chunk(python, workdir, nodeids, p2p_timeout_seconds, pythonpath))
    p2p_passed = bool(p2p_results) and all(result["passed"] for result in p2p_results)
    if not patch_result.get("applied"):
        p2p_status = "skipped_patch_not_applied"
    elif not oracle_result.get("passed"):
        p2p_status = "skipped_issue_not_fixed"
    else:
        p2p_status = "passed" if p2p_passed else "failed"
    return {
        "patch_id": candidate["patch_id"],
        "model_candidate_id": candidate["model_candidate_id"],
        "task_id": candidate["task_id"],
        "project": candidate["project"],
        "candidate_type": candidate["candidate_type"],
        "expected_outcome": candidate["expected_outcome"],
        "patch_applied": bool(patch_result.get("applied")),
        "retained_oracle_ran": bool(oracle_result.get("ran")),
        "retained_oracle_passed": bool(oracle_result.get("passed")),
        "p2p_scope_id": scope.get("scope_id", scope.get("task_id")),
        "p2p_broad_status": p2p_status,
        "p2p_broad_test_count": len(scope.get("p2p_broad_tests", [])),
        "p2p_broad_passed_count": sum(result["nodeid_count"] for result in p2p_results if result["passed"]),
        "label_retained_oracle": "correct" if oracle_result.get("passed") else "incorrect",
        "label_with_p2p_broad": final_label(
            bool(patch_result.get("applied")),
            bool(oracle_result.get("passed")),
            p2p_passed,
        ),
        "patch_result": patch_result,
        "oracle_result": oracle_result,
        "p2p_results": p2p_results,
    }


def build_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "record_count": len(records),
        "patch_applied_count": sum(1 for record in records if record["patch_applied"]),
        "retained_oracle_passed_count": sum(1 for record in records if record["retained_oracle_passed"]),
        "p2p_broad_test_count": records[0]["p2p_broad_test_count"] if records else 0,
        "label_with_p2p_broad_counts": count_by(records, "label_with_p2p_broad"),
    }


def count_by(records: list[dict[str, Any]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        key = str(record[field])
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate candidates with retained oracle plus P2P broad scope.")
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--p2p-scope", required=True)
    parser.add_argument("--source-workspace-root", default=str(base_validator.source_root_default()))
    parser.add_argument("--workdir-root", default="outputs/p2p_candidate_validation/workdirs")
    parser.add_argument("--out", required=True)
    parser.add_argument("--summary-out", required=True)
    parser.add_argument("--apply-timeout-seconds", type=int, default=30)
    parser.add_argument("--oracle-timeout-seconds", type=int, default=60)
    parser.add_argument("--p2p-timeout-seconds", type=int, default=20)
    parser.add_argument("--p2p-batch-size", type=int, default=50)
    parser.add_argument("--python", default=sys.executable)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    candidates = base_validator.read_jsonl(Path(args.candidates))
    scope = read_json(Path(args.p2p_scope))
    compat = scope.get("compat_shim", {})
    pythonpath = resolve_path(compat["path"], repo_root) if compat.get("enabled") and compat.get("path") else None
    records = [
        validate_candidate(
            candidate=candidate,
            scope=scope,
            source_root=Path(args.source_workspace_root),
            workdir_root=Path(args.workdir_root),
            apply_timeout_seconds=args.apply_timeout_seconds,
            oracle_timeout_seconds=args.oracle_timeout_seconds,
            p2p_timeout_seconds=args.p2p_timeout_seconds,
            python=args.python,
            pythonpath=pythonpath,
            p2p_batch_size=args.p2p_batch_size,
        )
        for candidate in candidates
    ]
    summary = build_summary(records)
    write_jsonl(Path(args.out), records)
    write_json(Path(args.summary_out), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
