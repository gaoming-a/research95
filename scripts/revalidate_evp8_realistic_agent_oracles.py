"""Revalidate EVP-8 realistic agent labels with task-specific Python envs.

This is evaluator-side only. It reads hidden oracle paths from the evaluator
manifest, recreates patched workdirs, runs oracles with the same project envs
used by visible tests where available, and writes corrected evaluator labels.
"""

from __future__ import annotations

import argparse
import json
import os
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


DEFAULT_EVALUATOR_IN = REPO_ROOT / "data" / "patches" / "evp8_realistic_agent_evaluator_manifest_v0_1.jsonl"
DEFAULT_MODEL_VISIBLE_IN = REPO_ROOT / "data" / "evidence" / "evp8_realistic_agent_model_visible_seed_v0_2.jsonl"
DEFAULT_WORKDIR_ROOT = REPO_ROOT / "outputs" / "evp8_realistic_agent_oracle_revalidation_v0_1" / "workdirs"
DEFAULT_RECORDS_OUT = REPO_ROOT / "data" / "patches" / "evp8_realistic_agent_oracle_revalidation_v0_1.jsonl"
DEFAULT_EVALUATOR_OUT = REPO_ROOT / "data" / "patches" / "evp8_realistic_agent_evaluator_manifest_v0_2.jsonl"
DEFAULT_SUMMARY_OUT = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_corrected_oracle_revalidation_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_realistic_agent_corrected_oracle_revalidation_v0_1.md"

PROJECT_PYTHONS = {
    "bugsinpy_PySnooper_1": REPO_ROOT / "outputs" / "envs" / "pysnooper_p2p_py311" / "Scripts" / "python.exe",
    "bugsinpy_PySnooper_3": REPO_ROOT / "outputs" / "envs" / "pysnooper3_p2p_py311" / "Scripts" / "python.exe",
    "cookiecutter": REPO_ROOT / "outputs" / "envs" / "cookiecutter_p2p_py311" / "Scripts" / "python.exe",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


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


def python_for(row: dict[str, Any]) -> tuple[str, str]:
    task_python = PROJECT_PYTHONS.get(str(row.get("task_id")))
    if task_python and task_python.exists():
        return str(task_python), display_path(task_python)
    project_python = PROJECT_PYTHONS.get(str(row.get("project")))
    if project_python and project_python.exists():
        return str(project_python), display_path(project_python)
    return sys.executable, "current_process_python"


def run_command(command: list[str], cwd: Path, timeout_seconds: int) -> dict[str, Any]:
    started = time.monotonic()
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(cwd) if not existing else str(cwd) + os.pathsep + existing
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
        "exit_code": completed.returncode,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "stdout_tail": completed.stdout[-1500:],
        "stderr_tail": completed.stderr[-1500:],
    }


def sanitize(text: str, workdir: Path) -> str:
    value = text or ""
    replacements = {
        str(workdir): "<candidate_workdir>",
        str(workdir).replace("\\", "/"): "<candidate_workdir>",
        str(REPO_ROOT): "<repo_root>",
        str(REPO_ROOT).replace("\\", "/"): "<repo_root>",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value


def dependency_error(result: dict[str, Any]) -> bool:
    text = f"{result.get('stdout_tail') or ''}\n{result.get('stderr_tail') or ''}"
    return "ModuleNotFoundError" in text or "ImportError" in text


def corrected_label(patch_applied: bool, oracle_ran: bool, oracle_passed: bool, dependency_errors: int) -> str:
    if not patch_applied:
        return "patch_apply_failed"
    if not oracle_ran or dependency_errors:
        return "environment_invalid"
    return "correct" if oracle_passed else "test_passing_wrong"


def revalidate_one(
    evaluator_row: dict[str, Any],
    model_visible_row: dict[str, Any],
    source_root: Path,
    workdir_root: Path,
    apply_timeout_seconds: int,
    oracle_timeout_seconds: int,
    keep_workdirs: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    candidate_id = evaluator_row["candidate_id"]
    workdir = workdir_root / candidate_id
    copy_checkout(source_root, model_visible_row, workdir)
    patch_result = apply_patch(model_visible_row, workdir, apply_timeout_seconds)
    python_executable, python_source = python_for(evaluator_row)
    oracle_results: list[dict[str, Any]] = []
    if patch_result.get("applied"):
        for oracle_path_text in evaluator_row.get("hidden_oracles") or []:
            oracle_path = REPO_ROOT / oracle_path_text
            result = run_command([python_executable, str(oracle_path)], workdir, oracle_timeout_seconds)
            result["oracle_path"] = oracle_path_text
            result["passed"] = result["exit_code"] == 0
            result["stdout_tail"] = sanitize(result["stdout_tail"], workdir)
            result["stderr_tail"] = sanitize(result["stderr_tail"], workdir)
            oracle_results.append(result)
    dependency_errors = sum(1 for result in oracle_results if dependency_error(result))
    oracle_ran = bool(oracle_results)
    oracle_passed = oracle_ran and all(result["passed"] for result in oracle_results)
    label = corrected_label(bool(patch_result.get("applied")), oracle_ran, oracle_passed, dependency_errors)
    record = {
        "candidate_id": candidate_id,
        "task_id": evaluator_row.get("task_id"),
        "project": evaluator_row.get("project"),
        "previous_normalized_label": evaluator_row.get("normalized_label"),
        "corrected_normalized_label": label,
        "label_changed": evaluator_row.get("normalized_label") != label,
        "patch_applied": bool(patch_result.get("applied")),
        "oracle_ran": oracle_ran,
        "oracle_passed": oracle_passed,
        "dependency_error_count": dependency_errors,
        "python_source": python_source,
        "oracle_results": oracle_results,
    }
    corrected = evaluator_row | {
        "normalized_label": label,
        "expected_outcome": "correct" if label == "correct" else "incorrect",
        "label_confidence": "high" if label in {"correct", "test_passing_wrong"} else "environment_invalid",
        "hidden_validation_summary": {
            "oracle_ran": oracle_ran,
            "oracle_passed": oracle_passed,
            "dependency_error_count": dependency_errors,
            "python_source": python_source,
            "corrected_revalidation_id": "evp8_realistic_agent_corrected_oracle_revalidation_v0_1",
        },
        "nontrivial_hard_negative": label == "test_passing_wrong",
    }
    if not keep_workdirs:
        remove_tree(workdir)
    return record, corrected


def build_summary(records: list[dict[str, Any]], corrected_rows: list[dict[str, Any]]) -> dict[str, Any]:
    changed = [record for record in records if record["label_changed"]]
    return {
        "analysis_id": "evp8_realistic_agent_corrected_oracle_revalidation_v0_1",
        "candidate_count": len(records),
        "previous_label_counts": dict(sorted(Counter(record["previous_normalized_label"] for record in records).items())),
        "corrected_label_counts": dict(sorted(Counter(record["corrected_normalized_label"] for record in records).items())),
        "label_changed_count": len(changed),
        "label_changed_by_task": dict(sorted(Counter(record["task_id"] for record in changed).items())),
        "patch_applied_count": sum(1 for record in records if record["patch_applied"]),
        "oracle_ran_count": sum(1 for record in records if record["oracle_ran"]),
        "oracle_passed_count": sum(1 for record in records if record["oracle_passed"]),
        "dependency_error_count": sum(record["dependency_error_count"] for record in records),
        "python_source_counts": dict(sorted(Counter(record["python_source"] for record in records).items())),
        "ready_for_recomputed_metrics": (
            len(records) == len(corrected_rows)
            and sum(record["dependency_error_count"] for record in records) == 0
            and all(record["patch_applied"] and record["oracle_ran"] for record in records)
        ),
        "changed_candidate_ids": [record["candidate_id"] for record in changed],
    }


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# EVP-8 Realistic Agent Corrected Oracle Revalidation v0.1",
        "",
        "Date: 2026-06-30",
        "",
        "This evaluator-side run revalidates hidden oracles with task-specific",
        "Python environments after false-accept inspection found dependency",
        "errors in the original validation tails.",
        "",
        f"- candidates: {summary['candidate_count']}",
        f"- previous labels: `{summary['previous_label_counts']}`",
        f"- corrected labels: `{summary['corrected_label_counts']}`",
        f"- label changes: {summary['label_changed_count']}",
        f"- dependency errors: {summary['dependency_error_count']}",
        f"- patch applied: {summary['patch_applied_count']}",
        f"- oracle ran: {summary['oracle_ran_count']}",
        f"- oracle passed: {summary['oracle_passed_count']}",
        f"- ready for recomputed metrics: `{summary['ready_for_recomputed_metrics']}`",
        "",
        "Label changes by task:",
        "",
    ]
    for task, count in summary["label_changed_by_task"].items():
        lines.append(f"- `{task}`: {count}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluator-in", type=Path, default=DEFAULT_EVALUATOR_IN)
    parser.add_argument("--model-visible-in", type=Path, default=DEFAULT_MODEL_VISIBLE_IN)
    parser.add_argument("--source-workspace-root", type=Path, default=source_root_default())
    parser.add_argument("--workdir-root", type=Path, default=DEFAULT_WORKDIR_ROOT)
    parser.add_argument("--records-out", type=Path, default=DEFAULT_RECORDS_OUT)
    parser.add_argument("--evaluator-out", type=Path, default=DEFAULT_EVALUATOR_OUT)
    parser.add_argument("--summary-out", type=Path, default=DEFAULT_SUMMARY_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--apply-timeout-seconds", type=int, default=30)
    parser.add_argument("--oracle-timeout-seconds", type=int, default=90)
    parser.add_argument("--keep-workdirs", action="store_true")
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    evaluator_rows = read_jsonl(args.evaluator_in)
    visible_rows = {row["candidate_id"]: row for row in read_jsonl(args.model_visible_in)}
    records: list[dict[str, Any]] = []
    corrected_rows: list[dict[str, Any]] = []
    args.workdir_root.mkdir(parents=True, exist_ok=True)
    for index, row in enumerate(evaluator_rows, start=1):
        record, corrected = revalidate_one(
            evaluator_row=row,
            model_visible_row=visible_rows[row["candidate_id"]],
            source_root=args.source_workspace_root,
            workdir_root=args.workdir_root,
            apply_timeout_seconds=args.apply_timeout_seconds,
            oracle_timeout_seconds=args.oracle_timeout_seconds,
            keep_workdirs=args.keep_workdirs,
        )
        records.append(record)
        corrected_rows.append(corrected)
        print(f"[{index}/{len(evaluator_rows)}] {record['candidate_id']} {record['previous_normalized_label']} -> {record['corrected_normalized_label']} oracle_passed={record['oracle_passed']}")
    summary = build_summary(records, corrected_rows)
    write_jsonl(args.records_out, records)
    write_jsonl(args.evaluator_out, corrected_rows)
    write_json(args.summary_out, summary)
    write_markdown(args.md_out, summary)
    if args.check:
        if summary["candidate_count"] != 53:
            raise SystemExit(f"expected 53 records, got {summary['candidate_count']}")
        if summary["dependency_error_count"] != 0:
            raise SystemExit(f"dependency errors remain: {summary['dependency_error_count']}")
        if not summary["ready_for_recomputed_metrics"]:
            raise SystemExit("corrected revalidation is not ready for recomputed metrics")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
