from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def source_root_default() -> Path:
    return Path("..") / "research" / "data" / "real_bugs" / "bugsinpy_workspace"


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
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bug_checkout_root(source_root: Path, candidate: dict[str, Any]) -> Path:
    bug_dir = str(candidate["task_id"]).replace("bugsinpy_", "")
    return source_root / bug_dir / "buggy" / candidate["project"]


def copy_checkout(source_root: Path, candidate: dict[str, Any], workdir: Path) -> None:
    source = bug_checkout_root(source_root, candidate)
    if not source.exists():
        raise FileNotFoundError(f"missing buggy checkout: {source}")
    if workdir.exists():
        shutil.rmtree(workdir)

    def ignore_checkout_entries(directory: str, names: list[str]) -> set[str]:
        ignored = set(
            shutil.ignore_patterns(
                "env",
                ".git",
                ".tox",
                ".pytest_cache",
                "__pycache__",
                "*.pyc",
            )(directory, names)
        )
        for name in names:
            path = Path(directory) / name
            try:
                attributes = getattr(os.lstat(path), "st_file_attributes", 0)
            except OSError:
                continue
            reparse_point = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
            if path.is_symlink() or attributes & reparse_point:
                ignored.add(name)
        return ignored

    shutil.copytree(
        source,
        workdir,
        ignore=ignore_checkout_entries,
    )


def run_command(
    command: list[str],
    cwd: Path,
    timeout_seconds: int,
    extra_env: dict[str, str] | None = None,
) -> dict[str, Any]:
    started = time.monotonic()
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
        )
        return {
            "command": command,
            "exit_code": completed.returncode,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "stdout_tail": tail(completed.stdout),
            "stderr_tail": tail(completed.stderr),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "exit_code": None,
            "elapsed_seconds": timeout_seconds,
            "stdout_tail": tail(exc.stdout if isinstance(exc.stdout, str) else ""),
            "stderr_tail": tail(exc.stderr if isinstance(exc.stderr, str) else ""),
            "timeout": True,
        }


def has_patch_hunk(patch_text: str) -> bool:
    return any(line.startswith("@@") for line in patch_text.splitlines())


def apply_patch(candidate: dict[str, Any], workdir: Path, timeout_seconds: int) -> dict[str, Any]:
    patch_text = str(candidate["patch_text"])
    if not has_patch_hunk(patch_text):
        return {
            "attempted": False,
            "applied": True,
            "reason": "empty_diff",
            "exit_code": 0,
        }
    patch_path = workdir / ".candidate.patch"
    patch_path.write_text(patch_text, encoding="utf-8", newline="\n")
    result = run_command(
        ["git", "apply", "--whitespace=nowarn", str(patch_path.resolve())],
        cwd=workdir,
        timeout_seconds=timeout_seconds,
        extra_env={"GIT_CEILING_DIRECTORIES": str(workdir.parent.resolve())},
    )
    result["attempted"] = True
    result["applied"] = result["exit_code"] == 0
    return result


def run_oracles(candidate: dict[str, Any], workdir: Path, timeout_seconds: int) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[1]
    oracle_paths = candidate.get("hidden_oracles") or []
    if not oracle_paths:
        return {
            "ran": False,
            "passed": False,
            "reason": "missing_hidden_oracle",
            "results": [],
        }
    results = []
    for oracle_path_text in oracle_paths:
        oracle_path = repo_root / oracle_path_text
        result = run_command([sys.executable, str(oracle_path)], cwd=workdir, timeout_seconds=timeout_seconds)
        result["oracle_path"] = oracle_path_text
        result["passed"] = result["exit_code"] == 0
        results.append(result)
    return {
        "ran": True,
        "passed": all(result["passed"] for result in results),
        "results": results,
    }


def classify_validation(candidate: dict[str, Any], patch_result: dict[str, Any], oracle_result: dict[str, Any]) -> str:
    if not patch_result.get("applied"):
        return "patch_apply_failed"
    if not oracle_result.get("ran"):
        return "oracle_missing"
    expected = candidate["expected_outcome"]
    passed = bool(oracle_result.get("passed"))
    if expected == "correct":
        return "validated" if passed else "label_mismatch"
    if expected in {"incorrect", "partial", "overfitted", "irrelevant_or_noop"}:
        return "validated" if not passed else "label_mismatch"
    if expected == "environment_invalid":
        return "environment_invalid"
    return "unknown_expected_outcome"


def validate_candidate(
    candidate: dict[str, Any],
    source_root: Path,
    workdir_root: Path,
    apply_timeout_seconds: int,
    oracle_timeout_seconds: int,
    keep_workdirs: bool,
) -> dict[str, Any]:
    workdir = workdir_root / candidate["model_candidate_id"]
    copy_checkout(source_root, candidate, workdir)
    patch_result = apply_patch(candidate, workdir, apply_timeout_seconds)
    oracle_result = (
        run_oracles(candidate, workdir, oracle_timeout_seconds)
        if patch_result.get("applied")
        else {"ran": False, "passed": False, "reason": "patch_not_applied"}
    )
    status = classify_validation(candidate, patch_result, oracle_result)
    record = {
        "patch_id": candidate["patch_id"],
        "model_candidate_id": candidate["model_candidate_id"],
        "task_id": candidate["task_id"],
        "project": candidate["project"],
        "candidate_type": candidate["candidate_type"],
        "expected_outcome": candidate["expected_outcome"],
        "patch_materialization": candidate["patch_materialization"],
        "patch_applied": bool(patch_result.get("applied")),
        "oracle_ran": bool(oracle_result.get("ran")),
        "oracle_passed": bool(oracle_result.get("passed")),
        "validation_status": status,
        "patch_result": patch_result,
        "oracle_result": oracle_result,
    }
    if not keep_workdirs:
        shutil.rmtree(workdir, ignore_errors=True)
    return record


def build_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = count_by(records, "validation_status")
    candidate_types = count_by(records, "candidate_type")
    return {
        "record_count": len(records),
        "validation_status_counts": statuses,
        "candidate_type_counts": candidate_types,
        "patch_applied_count": sum(1 for record in records if record["patch_applied"]),
        "oracle_ran_count": sum(1 for record in records if record["oracle_ran"]),
        "oracle_all_passed_count": sum(1 for record in records if record["oracle_passed"]),
        "all_validated": statuses == {"validated": len(records)},
    }


def count_by(records: list[dict[str, Any]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        key = str(record[field])
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def tail(text: str, max_chars: int = 2000) -> str:
    return text[-max_chars:] if len(text) > max_chars else text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply patch candidates and validate them with retained oracles.")
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl.")
    parser.add_argument(
        "--source-workspace-root",
        default=str(source_root_default()),
        help="Root containing BugsInPy buggy/fixed checkouts.",
    )
    parser.add_argument(
        "--workdir-root",
        default="outputs/patch_verification_pilot_001/workdirs",
        help="Ignored directory where temporary candidate checkouts are copied.",
    )
    parser.add_argument("--out", required=True, help="Output JSONL validation report.")
    parser.add_argument("--summary-out", required=True, help="Output JSON validation summary.")
    parser.add_argument("--apply-timeout-seconds", type=int, default=30)
    parser.add_argument("--oracle-timeout-seconds", type=int, default=60)
    parser.add_argument(
        "--keep-workdirs",
        action="store_true",
        help="Keep copied candidate checkouts for debugging. By default they are removed after validation.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candidates = read_jsonl(Path(args.candidates))
    source_root = Path(args.source_workspace_root)
    if not source_root.exists():
        raise FileNotFoundError(f"source workspace root does not exist: {source_root}")
    workdir_root = Path(args.workdir_root)
    workdir_root.mkdir(parents=True, exist_ok=True)
    records = [
        validate_candidate(
            candidate=candidate,
            source_root=source_root,
            workdir_root=workdir_root,
            apply_timeout_seconds=args.apply_timeout_seconds,
            oracle_timeout_seconds=args.oracle_timeout_seconds,
            keep_workdirs=args.keep_workdirs,
        )
        for candidate in candidates
    ]
    summary = build_summary(records)
    write_jsonl(Path(args.out), records)
    write_json(Path(args.summary_out), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
