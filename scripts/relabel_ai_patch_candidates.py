from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import build_patch_verification_dataset as dataset_builder


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


def relabel_candidate(candidate: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    next_candidate = dict(candidate)
    note = ""
    if not validation.get("patch_applied"):
        next_candidate["expected_outcome"] = "environment_invalid"
        note = "Validation relabel: generated patch did not apply."
    elif validation.get("oracle_passed"):
        next_candidate["expected_outcome"] = "correct"
        note = "Validation relabel: generated patch applied and retained oracle passed."
    else:
        next_candidate["expected_outcome"] = "incorrect"
        note = "Validation relabel: generated patch applied but retained oracle failed."
    next_candidate["label_confidence"] = "high"
    next_candidate["construction_notes"] = f"{candidate.get('construction_notes', '')} {note}".strip()
    return next_candidate


def build_summary(candidates: list[dict[str, Any]], validations: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "candidate_count": len(candidates),
        "expected_outcome_counts": dict(sorted(Counter(c["expected_outcome"] for c in candidates).items())),
        "candidate_type_counts": dict(sorted(Counter(c["candidate_type"] for c in candidates).items())),
        "patch_applied_count": sum(1 for record in validations if record.get("patch_applied")),
        "oracle_ran_count": sum(1 for record in validations if record.get("oracle_ran")),
        "oracle_passed_count": sum(1 for record in validations if record.get("oracle_passed")),
        "environment_invalid_count": sum(1 for c in candidates if c["expected_outcome"] == "environment_invalid"),
        "ready_for_revalidation": all(c["expected_outcome"] != "environment_invalid" for c in candidates),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Relabel generated AI patch candidates after executable validation.")
    parser.add_argument("--pending-candidates", required=True)
    parser.add_argument("--validation", required=True)
    parser.add_argument("--out-candidates", required=True)
    parser.add_argument("--out-evidence-packets", required=True)
    parser.add_argument("--summary-out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candidates = read_jsonl(Path(args.pending_candidates))
    validations = read_jsonl(Path(args.validation))
    validation_by_id = {record["model_candidate_id"]: record for record in validations}
    missing = [candidate["model_candidate_id"] for candidate in candidates if candidate["model_candidate_id"] not in validation_by_id]
    if missing:
        raise SystemExit(f"missing validation records for model_candidate_id values: {missing}")
    relabeled = [relabel_candidate(candidate, validation_by_id[candidate["model_candidate_id"]]) for candidate in candidates]
    write_jsonl(Path(args.out_candidates), relabeled)
    write_jsonl(Path(args.out_evidence_packets), [dataset_builder.build_evidence_packet(candidate) for candidate in relabeled])
    summary = build_summary(relabeled, validations)
    write_json(Path(args.summary_out), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
