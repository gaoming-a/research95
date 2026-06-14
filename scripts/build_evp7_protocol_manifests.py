"""Build tracked manifests for the frozen EVP-7 protocol pilot.

The script intentionally reads only tracked registry/scope files. Candidate
patch JSONL files currently live under ignored outputs, so candidate-level
EVP-7 records are a later protocol step.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "data" / "cohorts" / "task_cohort_registry.json"
TASKS_OUT = REPO_ROOT / "data" / "tasks" / "evp7_tasks.jsonl"
BLOCKERS_OUT = REPO_ROOT / "data" / "exclusions" / "blocked_bugsinpy_projects.jsonl"
SUMMARY_OUT = REPO_ROOT / "data" / "tasks" / "evp7_manifest_summary.json"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _dump_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records)
    path.write_text(text, encoding="utf-8")


def _task_bug_id(task_id: str) -> str | None:
    parts = task_id.rsplit("_", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[1]
    return None


def _scope_summary(manifest_path: str | None) -> dict[str, Any]:
    if not manifest_path:
        return {}
    path = REPO_ROOT / manifest_path
    if not path.exists():
        return {"manifest_read_status": "missing_tracked_file"}
    manifest = _load_json(path)
    counts = manifest.get("counts", {})
    return {
        "manifest_read_status": "read",
        "scope_id": manifest.get("scope_id"),
        "scope_type": manifest.get("scope_type"),
        "test_framework": manifest.get("test_framework"),
        "test_paths": manifest.get("test_paths") or ([manifest.get("test_path")] if manifest.get("test_path") else []),
        "runs_per_version": manifest.get("runs_per_version") or manifest.get("stability_runs"),
        "collected_tests": counts.get("collected_tests") or manifest.get("collection", {}).get("buggy_collected_count"),
        "p2p_broad_size": counts.get("p2p_broad_tests") or counts.get("included_p2p_tests"),
        "excluded_fail_to_pass_oracle": counts.get("excluded_fail_to_pass_oracle"),
        "exclusion_reason_counts": counts.get("exclusion_reason_counts", {}),
        "fail_to_pass_nodeids": manifest.get("fail_to_pass_nodeids", []),
        "p2p_broad_tests_count": len(manifest.get("p2p_broad_tests", [])),
        "p2p_broad_tests_sample": manifest.get("p2p_broad_tests", [])[:10],
    }


def _candidate_count(collection: dict[str, Any]) -> int | None:
    if collection.get("candidate_count") is not None:
        return collection.get("candidate_count")
    label_counts = collection.get("candidate_label_counts")
    if isinstance(label_counts, dict) and label_counts:
        return sum(int(value) for value in label_counts.values())
    return None


def build_manifests(registry_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    registry = _load_json(registry_path)
    tasks = registry.get("tasks", [])
    main_tasks = [
        task
        for task in tasks
        if task.get("p2p_broad_main_included") is True
        and task.get("project_level_p2p_status") == "completed"
    ]
    blocked_tasks = [
        task
        for task in tasks
        if not (
            task.get("p2p_broad_main_included") is True
            and task.get("project_level_p2p_status") == "completed"
        )
    ]

    evp7_records: list[dict[str, Any]] = []
    for task in sorted(main_tasks, key=lambda item: item["task_id"]):
        collection = task.get("collection_summary", {})
        candidate_count = _candidate_count(collection)
        evp7_records.append(
            {
                "task_id": task["task_id"],
                "project": task.get("project"),
                "source": "BugsInPy",
                "bug_id": _task_bug_id(task["task_id"]),
                "language": "python",
                "cohort_id": "EVP-7",
                "cohort_role": "protocol_pilot_core",
                "task_status": "validated_project_level_p2p_broad",
                "project_level_p2p_status": task.get("project_level_p2p_status"),
                "p2p_scope": task.get("label_scope", {}).get("main"),
                "p2p_broad_manifest": task.get("p2p_broad_manifest"),
                "candidate_count": candidate_count,
                "candidate_label_counts": collection.get("candidate_label_counts", {}),
                "p2p_scope_summary": _scope_summary(task.get("p2p_broad_manifest")),
                "inclusion_reason": "Completed project-level P2P-broad and marked p2p_broad_main_included=true in the tracked cohort registry.",
                "notes": task.get("notes"),
                "metadata_backfill_required": [
                    "buggy_commit",
                    "fixed_commit",
                    "issue_summary",
                    "touched_files",
                ],
            }
        )

    blocker_records: list[dict[str, Any]] = []
    for task in sorted(blocked_tasks, key=lambda item: item["task_id"]):
        blocker_records.append(
            {
                "task_id": task["task_id"],
                "project": task.get("project"),
                "source": "BugsInPy",
                "bug_id": _task_bug_id(task["task_id"]),
                "cohort_id": "EVP-7",
                "decision": "excluded_from_protocol_pilot_core",
                "project_level_p2p_status": task.get("project_level_p2p_status"),
                "blocked_reason": task.get("blocked_reason", []),
                "available_evidence": task.get("available_evidence", {}),
                "label_scope": task.get("label_scope", {}),
                "appendix_smoke_included": task.get("appendix_smoke_included", False),
                "p2p_broad_manifest": task.get("p2p_broad_manifest"),
                "p2p_scope_policy_record": task.get("p2p_scope_policy_record"),
                "collection_summary": task.get("collection_summary", {}),
                "notes": task.get("notes"),
            }
        )

    records_with_candidate_count = [
        record for record in evp7_records if record.get("candidate_count") is not None
    ]
    records_missing_candidate_count = [
        record["task_id"] for record in evp7_records if record.get("candidate_count") is None
    ]
    summary = {
        "cohort_id": "EVP-7",
        "main_task_count": len(evp7_records),
        "main_projects": sorted({record["project"] for record in evp7_records}),
        "blocked_task_count": len(blocker_records),
        "blocked_projects": sorted({record["project"] for record in blocker_records if record.get("project")}),
        "candidate_count_known_from_registry": sum(
            record.get("candidate_count") or 0 for record in records_with_candidate_count
        ),
        "candidate_count_missing_in_registry_tasks": records_missing_candidate_count,
        "candidate_records_status": "task-level manifest only; candidate-level EVP-7 records are managed by scripts/build_evp7_candidate_manifest.py.",
        "expansion_decision": "Option A approved: freeze EVP-7 and stop blind BugsInPy expansion until protocol gates pass.",
    }
    return evp7_records, blocker_records, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH)
    parser.add_argument("--tasks-out", type=Path, default=TASKS_OUT)
    parser.add_argument("--blockers-out", type=Path, default=BLOCKERS_OUT)
    parser.add_argument("--summary-out", type=Path, default=SUMMARY_OUT)
    parser.add_argument("--check", action="store_true", help="Validate outputs after writing.")
    args = parser.parse_args()

    evp7_records, blocker_records, summary = build_manifests(args.registry)
    _dump_jsonl(args.tasks_out, evp7_records)
    _dump_jsonl(args.blockers_out, blocker_records)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.check:
        for path, expected in [(args.tasks_out, summary["main_task_count"]), (args.blockers_out, None)]:
            rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
            if expected is not None and len(rows) != expected:
                raise SystemExit(f"{path} has {len(rows)} records, expected {expected}")
        if summary["main_task_count"] < 12:
            raise SystemExit("EVP-7 main task count fell below the established 12-task pilot floor")
        if "cookiecutter" not in summary["main_projects"] or "PySnooper" not in summary["main_projects"]:
            raise SystemExit("EVP-7 project summary is incomplete")

    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
