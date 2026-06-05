from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from cross_review.jsonl import read_jsonl


PRIMARY_LABELS = {
    "supported",
    "unsupported",
    "partially_supported",
    "oracle_irrelevant",
    "insufficient_evidence",
}
CANDIDATE_LABELS = {"buggy", "fixed_control"}
REQUIRED_FIELDS = {
    "claim_label_id",
    "source_run_id",
    "review_id",
    "project",
    "bug_id",
    "candidate_id",
    "candidate_oracle_label",
    "reviewer",
    "claim_text",
    "claim_location",
    "primary_label",
    "taxonomy_tags",
    "evidence_sources",
    "evidence_summary",
    "needs_additional_context",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate and summarize real-bug claim-level labels.")
    parser.add_argument("--labels", required=True, help="Claim-label JSONL.")
    parser.add_argument("--out", required=True, help="Summary JSON output.")
    parser.add_argument(
        "--allow-unlabeled",
        action="store_true",
        help="Allow blank primary_label/evidence fields for batch QA before labeling is complete.",
    )
    args = parser.parse_args()

    records = read_jsonl(args.labels)
    errors = validate_records(records, allow_unlabeled=args.allow_unlabeled)
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(f"Invalid claim labels: {len(errors)} error(s)")

    summary = summarize(records)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


def validate_records(records: list[dict[str, Any]], allow_unlabeled: bool) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()

    for index, record in enumerate(records, start=1):
        record_id = str(record.get("claim_label_id") or f"line_{index}")
        missing = sorted(field for field in REQUIRED_FIELDS if field not in record)
        if missing:
            errors.append(f"{record_id}: missing required fields: {', '.join(missing)}")
            continue

        if record_id in seen_ids:
            errors.append(f"{record_id}: duplicate claim_label_id")
        seen_ids.add(record_id)

        candidate_label = record.get("candidate_oracle_label")
        if candidate_label not in CANDIDATE_LABELS:
            errors.append(f"{record_id}: invalid candidate_oracle_label: {candidate_label!r}")

        primary_label = record.get("primary_label")
        if primary_label == "" and allow_unlabeled:
            continue
        if primary_label not in PRIMARY_LABELS:
            errors.append(f"{record_id}: invalid primary_label: {primary_label!r}")
            continue

        if not isinstance(record.get("taxonomy_tags"), list):
            errors.append(f"{record_id}: taxonomy_tags must be a list")
        if not isinstance(record.get("evidence_sources"), list):
            errors.append(f"{record_id}: evidence_sources must be a list")
        elif not record["evidence_sources"]:
            errors.append(f"{record_id}: labeled claim must include at least one non-LLM evidence source")
        if not str(record.get("evidence_summary") or "").strip():
            errors.append(f"{record_id}: labeled claim must include evidence_summary")
        if record.get("needs_additional_context") not in {True, False}:
            errors.append(f"{record_id}: needs_additional_context must be true or false after labeling")

    return errors


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    labeled = [record for record in records if record.get("primary_label")]
    unlabeled = [record for record in records if not record.get("primary_label")]
    by_candidate = nested_counts(labeled, "candidate_oracle_label", "primary_label")
    return {
        "claims": len(records),
        "labeled_claims": len(labeled),
        "unlabeled_claims": len(unlabeled),
        "input_by_candidate_outcome": flat_counts(records, "candidate_oracle_label"),
        "input_by_reviewer": flat_counts(records, "reviewer"),
        "by_candidate_outcome": by_candidate,
        "by_reviewer": nested_counts(labeled, "reviewer", "primary_label"),
        "by_source_run": nested_counts(labeled, "source_run_id", "primary_label"),
        "taxonomy_tag_counts": taxonomy_counts(labeled),
        "paper_table": paper_table(by_candidate),
    }


def nested_counts(records: list[dict[str, Any]], group_key: str, label_key: str) -> dict[str, dict[str, int]]:
    grouped: dict[str, Counter[str]] = {}
    for record in records:
        group = str(record.get(group_key))
        label = str(record.get(label_key))
        grouped.setdefault(group, Counter())[label] += 1
    return {group: dict(sorted(counter.items())) for group, counter in sorted(grouped.items())}


def flat_counts(records: list[dict[str, Any]], key: str) -> dict[str, int]:
    counter: Counter[str] = Counter(str(record.get(key)) for record in records)
    return dict(sorted(counter.items()))


def taxonomy_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for record in records:
        for tag in record.get("taxonomy_tags") or []:
            counter[str(tag)] += 1
    return dict(sorted(counter.items()))


def paper_table(by_candidate: dict[str, dict[str, int]]) -> dict[str, dict[str, int]]:
    labels = [
        "supported",
        "unsupported",
        "partially_supported",
        "oracle_irrelevant",
        "insufficient_evidence",
    ]
    table: dict[str, dict[str, int]] = {}
    for candidate_label in sorted(CANDIDATE_LABELS):
        counts = by_candidate.get(candidate_label, {})
        table[candidate_label] = {"claims": sum(counts.values())}
        table[candidate_label].update({label: int(counts.get(label, 0)) for label in labels})
    return table


if __name__ == "__main__":
    main()
