"""Promote validated EVP-7 candidate outputs into a tracked schema.

Inputs are the existing ignored candidate/validation outputs. The tracked output
keeps evaluator-only labels separate from fields that may later feed evidence
packet builders.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_MANIFEST = REPO_ROOT / "data" / "tasks" / "evp7_tasks.jsonl"
SUMMARY_IN = REPO_ROOT / "data" / "tasks" / "evp7_manifest_summary.json"
CANDIDATES_OUT = REPO_ROOT / "data" / "patches" / "evp7_candidates.jsonl"
SUMMARY_OUT = REPO_ROOT / "data" / "patches" / "evp7_candidate_summary.json"


TASK_INPUTS: dict[str, tuple[str, str]] = {
    "bugsinpy_httpie_5": (
        "outputs/httpie5_stability_audit_001/candidates.jsonl",
        "outputs/httpie5_project_p2p_scope_003/candidate_p2p_validation.jsonl",
    ),
    "bugsinpy_cookiecutter_1": (
        "outputs/cookiecutter1_candidate_validation_001/candidates.jsonl",
        "outputs/cookiecutter1_candidate_validation_001/p2p_validation.jsonl",
    ),
    "bugsinpy_cookiecutter_2": (
        "outputs/cookiecutter2_candidate_validation_001/candidates.jsonl",
        "outputs/cookiecutter2_candidate_validation_001/p2p_validation.jsonl",
    ),
    "bugsinpy_cookiecutter_3": (
        "outputs/cookiecutter3_candidate_validation_001/candidates.jsonl",
        "outputs/cookiecutter3_candidate_validation_001/p2p_validation.jsonl",
    ),
    "bugsinpy_tqdm_9": (
        "outputs/tqdm9_candidate_validation_001/candidates.jsonl",
        "outputs/tqdm9_candidate_validation_001/p2p_validation.jsonl",
    ),
    "bugsinpy_PySnooper_1": (
        "outputs/pysnooper1_candidate_validation_001/candidates.jsonl",
        "outputs/pysnooper1_candidate_validation_001/p2p_validation.jsonl",
    ),
    "bugsinpy_PySnooper_3": (
        "outputs/pysnooper3_candidate_validation_001/candidates.jsonl",
        "outputs/pysnooper3_candidate_validation_001/p2p_validation.jsonl",
    ),
    "bugsinpy_youtube-dl_2": (
        "outputs/youtubedl2_candidate_validation_001/candidates.jsonl",
        "outputs/youtubedl2_candidate_validation_001/p2p_validation.jsonl",
    ),
    "bugsinpy_youtube-dl_4": (
        "outputs/youtubedl4_candidate_validation_001/candidates.jsonl",
        "outputs/youtubedl4_candidate_validation_001/p2p_validation.jsonl",
    ),
    "bugsinpy_youtube-dl_6": (
        "outputs/youtubedl6_candidate_validation_001/candidates.jsonl",
        "outputs/youtubedl6_candidate_validation_001/p2p_validation.jsonl",
    ),
    "bugsinpy_youtube-dl_5": (
        "outputs/youtubedl5_candidate_validation_001/candidates.jsonl",
        "outputs/youtubedl5_candidate_validation_001/p2p_validation.jsonl",
    ),
    "bugsinpy_youtube-dl_7": (
        "outputs/youtubedl7_candidate_validation_001/candidates.jsonl",
        "outputs/youtubedl7_candidate_validation_001/p2p_validation.jsonl",
    ),
    "bugsinpy_youtube-dl_11": (
        "outputs/youtubedl11_candidate_validation_001/candidates.jsonl",
        "outputs/youtubedl11_candidate_validation_001/p2p_validation.jsonl",
    ),
    "bugsinpy_youtube-dl_16": (
        "outputs/youtubedl16_candidate_validation_001/candidates.jsonl",
        "outputs/youtubedl16_candidate_validation_001/p2p_validation.jsonl",
    ),
}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )


def _patch_stats(patch_text: str) -> dict[str, int]:
    added = 0
    deleted = 0
    files = set()
    for line in patch_text.splitlines():
        if line.startswith("+++ b/"):
            files.add(line[len("+++ b/") :])
        elif line.startswith("--- a/"):
            files.add(line[len("--- a/") :])
        elif line.startswith("+") and not line.startswith("+++"):
            added += 1
        elif line.startswith("-") and not line.startswith("---"):
            deleted += 1
    return {"files_changed": len(files), "added_lines": added, "deleted_lines": deleted}


def _failure_label(candidate_type: str, label: str) -> str:
    if label == "correct_under_f2p_and_p2p_broad":
        return "none"
    if candidate_type == "partial_fix":
        return "partial_fix"
    if candidate_type in {"buggy_noop", "empty_diff_control"}:
        return "no_op_patch"
    if candidate_type == "irrelevant_patch":
        return "irrelevant_edit"
    if label == "incorrect_regression":
        return "regression_introducing"
    return "unknown_issue_not_fixed"


def _task_sort_key(task_id: str) -> tuple[str, int | str]:
    prefix, separator, suffix = task_id.rpartition("_")
    if separator and suffix.isdigit():
        return prefix, int(suffix)
    return task_id, task_id


def _candidate_record(
    index: int,
    candidate: dict[str, Any],
    validation: dict[str, Any],
    task_record: dict[str, Any],
    candidate_source_path: str,
    validation_source_path: str,
) -> dict[str, Any]:
    patch_text = candidate.get("patch_text", "")
    label = validation.get("label_with_p2p_broad")
    candidate_type = candidate.get("candidate_type")
    evp7_candidate_id = f"evp7_candidate_{index:04d}"
    return {
        "evp7_candidate_id": evp7_candidate_id,
        "cohort_id": "EVP-7",
        "task_id": candidate["task_id"],
        "project": candidate.get("project"),
        "source": candidate.get("source", "bugsinpy"),
        "source_model_candidate_id": candidate.get("model_candidate_id"),
        "patch_id": candidate.get("patch_id"),
        "patch_source_label": candidate_type,
        "candidate_type": candidate_type,
        "expected_outcome": candidate.get("expected_outcome"),
        "failure_type_label": _failure_label(candidate_type, label),
        "label_with_p2p_broad": label,
        "label_retained_oracle": validation.get("label_retained_oracle"),
        "label_confidence": candidate.get("label_confidence"),
        "base_version": candidate.get("base_version"),
        "context_mode": candidate.get("context_mode"),
        "patch_materialization": candidate.get("patch_materialization"),
        "patch_sha256": hashlib.sha256(patch_text.encode("utf-8")).hexdigest(),
        "patch_size": _patch_stats(patch_text),
        "patch_text": patch_text,
        "issue_summary": candidate.get("issue_summary"),
        "touched_files": candidate.get("touched_files", []),
        "visible_tests": candidate.get("visible_tests", []),
        "hidden_oracles": candidate.get("hidden_oracles", []),
        "model_visible_seed": {
            "candidate_id": evp7_candidate_id,
            "project": candidate.get("project"),
            "task_id": candidate.get("task_id"),
            "issue_summary": candidate.get("issue_summary"),
            "touched_files": candidate.get("touched_files", []),
            "patch_text": patch_text,
        },
        "validation_summary": {
            "patch_applied": validation.get("patch_applied"),
            "retained_oracle_ran": validation.get("retained_oracle_ran"),
            "retained_oracle_passed": validation.get("retained_oracle_passed"),
            "p2p_broad_status": validation.get("p2p_broad_status"),
            "p2p_broad_test_count": validation.get("p2p_broad_test_count"),
            "p2p_broad_passed_count": validation.get("p2p_broad_passed_count"),
            "p2p_scope_id": validation.get("p2p_scope_id"),
        },
        "evaluator_only_fields": [
            "patch_id",
            "patch_source_label",
            "candidate_type",
            "expected_outcome",
            "failure_type_label",
            "label_with_p2p_broad",
            "label_retained_oracle",
            "hidden_oracles",
            "validation_summary.retained_oracle_passed",
        ],
        "source_files": {
            "candidate_jsonl": candidate_source_path,
            "validation_jsonl": validation_source_path,
            "p2p_manifest": task_record.get("p2p_broad_manifest"),
        },
    }


def build_candidates(task_manifest: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    task_records = {record["task_id"]: record for record in _read_jsonl(task_manifest)}
    missing = sorted(set(task_records) - set(TASK_INPUTS))
    if missing:
        raise SystemExit(f"Missing task input mapping for: {missing}")

    records: list[dict[str, Any]] = []
    next_index = 1
    for task_id in sorted(task_records, key=_task_sort_key):
        candidate_rel, validation_rel = TASK_INPUTS[task_id]
        candidate_path = REPO_ROOT / candidate_rel
        validation_path = REPO_ROOT / validation_rel
        candidates = _read_jsonl(candidate_path)
        validations = {
            row["model_candidate_id"]: row for row in _read_jsonl(validation_path)
        }
        if len(candidates) != len(validations):
            raise SystemExit(f"{task_id}: candidate/validation count mismatch")
        for candidate in candidates:
            local_id = candidate.get("model_candidate_id")
            validation = validations.get(local_id)
            if validation is None:
                raise SystemExit(f"{task_id}: missing validation for {local_id}")
            if candidate.get("patch_id") != validation.get("patch_id"):
                raise SystemExit(f"{task_id}: patch_id mismatch for {local_id}")
            records.append(
                _candidate_record(
                    next_index,
                    candidate,
                    validation,
                    task_records[task_id],
                    candidate_rel,
                    validation_rel,
                )
            )
            next_index += 1

    summary = {
        "cohort_id": "EVP-7",
        "candidate_count": len(records),
        "task_count": len({record["task_id"] for record in records}),
        "project_count": len({record["project"] for record in records}),
        "task_candidate_counts": {
            task_id: sum(1 for record in records if record["task_id"] == task_id)
            for task_id in sorted(task_records)
        },
        "label_with_p2p_broad_counts": _counts(record["label_with_p2p_broad"] for record in records),
        "candidate_type_counts": _counts(record["candidate_type"] for record in records),
        "failure_type_counts": _counts(record["failure_type_label"] for record in records),
        "evidence_packet_status": "managed_by_separate_builder",
        "evidence_packet_artifact": "data/evidence/evp7_evidence_packets.jsonl",
        "next_step": "Use scripts/build_evp7_evidence_packets.py to regenerate model-visible evidence packets and leakage-audit summary.",
    }
    return records, summary


def _counts(values: Any) -> dict[str, int]:
    result: dict[str, int] = {}
    for value in values:
        key = str(value)
        result[key] = result.get(key, 0) + 1
    return dict(sorted(result.items()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-manifest", type=Path, default=TASK_MANIFEST)
    parser.add_argument("--summary-in", type=Path, default=SUMMARY_IN)
    parser.add_argument("--candidates-out", type=Path, default=CANDIDATES_OUT)
    parser.add_argument("--summary-out", type=Path, default=SUMMARY_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    records, summary = build_candidates(args.task_manifest)
    _write_jsonl(args.candidates_out, records)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.check:
        manifest_summary = json.loads(args.summary_in.read_text(encoding="utf-8"))
        min_known = manifest_summary.get("candidate_count_known_from_registry", 0)
        if len(records) < min_known:
            raise SystemExit(
                f"candidate count {len(records)} < registry-known lower bound {min_known}"
            )
        ids = [record["evp7_candidate_id"] for record in records]
        if len(ids) != len(set(ids)):
            raise SystemExit("evp7_candidate_id values are not unique")
        expected_task_count = manifest_summary.get("main_task_count")
        actual_task_count = len({record["task_id"] for record in records})
        if expected_task_count is not None and actual_task_count != expected_task_count:
            raise SystemExit(
                f"expected candidates from {expected_task_count} tasks, got {actual_task_count}"
            )
        if any(not record.get("label_with_p2p_broad") for record in records):
            raise SystemExit("missing p2p labels")

    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
