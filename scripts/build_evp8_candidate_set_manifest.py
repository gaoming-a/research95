"""Build the EVP-8 Phase 0 smoke candidate-set manifest.

This is a no-API bridge from the tracked EVP-7 structural cohort to the new
EVP-8 protocol. It intentionally writes model-visible-safe selection records:
candidate IDs, task/project identity, touched files, and patch hashes. It does
not copy evaluator labels, hidden oracle paths, expected outcomes, or raw model
outputs into per-candidate records.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CANDIDATES_IN = REPO_ROOT / "data" / "patches" / "evp7_candidates.jsonl"
MANIFEST_OUT = REPO_ROOT / "data" / "protocols" / "evp8_candidate_set_v0_1.json"
SUMMARY_OUT = REPO_ROOT / "data" / "protocols" / "evp8_candidate_set_v0_1_summary.json"

CANDIDATE_SET_ID = "evp8_smoke_from_evp7_structural_98_v0_1"
FORBIDDEN_RECORD_KEYS = {
    "expected_outcome",
    "candidate_type",
    "failure_type_label",
    "label_with_p2p_broad",
    "label_retained_oracle",
    "hidden_oracles",
    "validation_summary",
    "patch_materialization",
    "patch_source_label",
    "source_model_candidate_id",
    "construction_notes",
}
EXPECTED_CANDIDATE_COUNT = 98
EXPECTED_TASK_COUNT = 21
EXPECTED_PROJECT_COUNT = 6


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _counts(values: Any) -> dict[str, int]:
    result: dict[str, int] = {}
    for value in values:
        key = str(value)
        result[key] = result.get(key, 0) + 1
    return dict(sorted(result.items()))


def _task_sort_key(candidate: dict[str, Any]) -> tuple[str, int]:
    candidate_id = candidate.get("evp7_candidate_id", "")
    suffix = candidate_id.rsplit("_", 1)[-1]
    numeric = int(suffix) if suffix.isdigit() else 0
    return candidate.get("task_id", ""), numeric


def _safe_record(candidate: dict[str, Any], index: int) -> dict[str, Any]:
    seed = candidate.get("model_visible_seed") or {}
    touched_files = seed.get("touched_files") or candidate.get("touched_files") or []
    return {
        "candidate_set_id": CANDIDATE_SET_ID,
        "evp8_candidate_id": f"evp8_smoke_candidate_{index:04d}",
        "source_candidate_id": candidate["evp7_candidate_id"],
        "source_cohort_id": candidate.get("cohort_id"),
        "source_manifest": str(CANDIDATES_IN.relative_to(REPO_ROOT)),
        "task_id": seed.get("task_id") or candidate.get("task_id"),
        "project": seed.get("project") or candidate.get("project"),
        "has_issue_summary": bool(seed.get("issue_summary") or candidate.get("issue_summary")),
        "has_patch_text_source": bool(seed.get("patch_text") or candidate.get("patch_text")),
        "patch_sha256": candidate.get("patch_sha256"),
        "patch_file_count": (candidate.get("patch_size") or {}).get("files_changed"),
        "touched_files": touched_files,
        "touched_file_count": len(touched_files),
        "selection_role": "evp8_phase0_smoke_protocol_validation",
        "model_visible_record": True,
        "label_fields_in_record": False,
    }


def build_manifest(candidates_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    candidates = sorted(_read_jsonl(candidates_path), key=_task_sort_key)
    records = [_safe_record(candidate, index + 1) for index, candidate in enumerate(candidates)]
    leakage_findings = leakage_audit(records)

    task_ids = [record["task_id"] for record in records]
    projects = [record["project"] for record in records]
    summary = {
        "candidate_set_id": CANDIDATE_SET_ID,
        "cohort_id": "EVP-8",
        "source_cohort_id": "EVP-7",
        "source_manifest": str(candidates_path.relative_to(REPO_ROOT)),
        "candidate_count": len(records),
        "task_count": len(set(task_ids)),
        "project_count": len(set(projects)),
        "task_candidate_counts": _counts(task_ids),
        "project_candidate_counts": _counts(projects),
        "aggregate_label_counts_model_visible": False,
        "aggregate_label_counts_boundary": (
            "Aggregate evaluator-side label counts are included only for candidate-set "
            "balance audit; per-candidate model-visible records do not include labels."
        ),
        "aggregate_candidate_type_counts": _counts(candidate.get("candidate_type") for candidate in candidates),
        "aggregate_expected_outcome_counts": _counts(candidate.get("expected_outcome") for candidate in candidates),
        "aggregate_p2p_label_counts": _counts(candidate.get("label_with_p2p_broad") for candidate in candidates),
        "record_leakage_findings_count": len(leakage_findings),
        "record_leakage_findings": leakage_findings[:20],
        "candidate_set_status": "frozen_for_phase0_smoke_protocol_validation",
        "journal_full_scale_boundary": (
            "This is not the final journal-scale full-run cohort. It freezes the "
            "current tracked structural cohort for EVP-8 packet/prompt/schema dry-runs "
            "and later smoke validation only."
        ),
        "api_call_attempted": False,
        "evidence_packets_generated": False,
    }
    manifest = {
        "candidate_set_id": CANDIDATE_SET_ID,
        "cohort_id": "EVP-8",
        "source_cohort_id": "EVP-7",
        "records": records,
        "summary": {
            "candidate_count": summary["candidate_count"],
            "task_count": summary["task_count"],
            "project_count": summary["project_count"],
            "candidate_set_status": summary["candidate_set_status"],
            "model_visible_records": True,
            "label_fields_in_records": False,
        },
    }
    return manifest, summary


def leakage_audit(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for index, record in enumerate(records):
        candidate_id = record.get("evp8_candidate_id", f"index_{index}")
        for key in record:
            if key in FORBIDDEN_RECORD_KEYS:
                findings.append(
                    {
                        "candidate_id": str(candidate_id),
                        "field": key,
                        "reason": "forbidden_model_visible_candidate_set_field",
                    }
                )
    return findings


def _check(manifest: dict[str, Any], summary: dict[str, Any]) -> None:
    if summary["candidate_count"] != EXPECTED_CANDIDATE_COUNT:
        raise SystemExit(f"candidate_count {summary['candidate_count']} != {EXPECTED_CANDIDATE_COUNT}")
    if summary["task_count"] != EXPECTED_TASK_COUNT:
        raise SystemExit(f"task_count {summary['task_count']} != {EXPECTED_TASK_COUNT}")
    if summary["project_count"] != EXPECTED_PROJECT_COUNT:
        raise SystemExit(f"project_count {summary['project_count']} != {EXPECTED_PROJECT_COUNT}")
    if summary["record_leakage_findings_count"] != 0:
        raise SystemExit(f"candidate-set leakage findings: {summary['record_leakage_findings']}")
    records = manifest.get("records") or []
    if len(records) != EXPECTED_CANDIDATE_COUNT:
        raise SystemExit("manifest records do not match expected candidate count")
    if len({record["evp8_candidate_id"] for record in records}) != len(records):
        raise SystemExit("evp8 candidate IDs are not unique")
    if len({record["source_candidate_id"] for record in records}) != len(records):
        raise SystemExit("source candidate IDs are not unique")
    if any(not record.get("has_issue_summary") for record in records):
        raise SystemExit("candidate set includes records without issue summaries")
    if any(not record.get("has_patch_text_source") for record in records):
        raise SystemExit("candidate set includes records without patch text source")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates-in", type=Path, default=CANDIDATES_IN)
    parser.add_argument("--manifest-out", type=Path, default=MANIFEST_OUT)
    parser.add_argument("--summary-out", type=Path, default=SUMMARY_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    manifest, summary = build_manifest(args.candidates_in)
    _write_json(args.manifest_out, manifest)
    _write_json(args.summary_out, summary)
    if args.check:
        _check(manifest, summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
