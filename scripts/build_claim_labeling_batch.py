from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from cross_review.jsonl import read_jsonl, write_jsonl


LABEL_FIELDS = {
    "primary_label": "",
    "taxonomy_tags": [],
    "evidence_sources": [],
    "evidence_summary": "",
    "needs_additional_context": None,
    "labeler": "",
    "label_date": "",
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a balanced claim-level labeling batch from existing real-bug review records."
    )
    parser.add_argument(
        "--source-run",
        action="append",
        nargs=3,
        metavar=("RUN_ID", "SEED_DIR", "REVIEWS_JSONL"),
        required=True,
        help="Existing run to sample from: run id, seed directory, and reviews JSONL.",
    )
    parser.add_argument("--out", required=True, help="Output claim-labeling JSONL.")
    parser.add_argument("--summary-out", required=True, help="Output summary JSON.")
    parser.add_argument("--target-buggy", type=int, default=10)
    parser.add_argument("--target-fixed", type=int, default=10)
    parser.add_argument(
        "--reviewer-priority",
        default="qwen,gpt,claude,deepseek",
        help="Comma-separated reviewer preference for deterministic selection.",
    )
    args = parser.parse_args()

    reviewer_priority = [item.strip() for item in args.reviewer_priority.split(",") if item.strip()]
    claims: list[dict[str, Any]] = []

    for run_index, (run_id, seed_dir, reviews_path) in enumerate(args.source_run):
        claims.extend(load_claims(run_id, Path(seed_dir), Path(reviews_path), run_index, reviewer_priority))

    unique_claims = deduplicate_claims(claims)
    selected = select_balanced_claims(unique_claims, args.target_buggy, args.target_fixed)

    for index, record in enumerate(selected, start=1):
        record["claim_label_id"] = f"real_bug_claim_label_{index:04d}"
        for key, value in LABEL_FIELDS.items():
            record[key] = list(value) if isinstance(value, list) else value

    write_jsonl(args.out, selected)
    summary = summarize(claims, unique_claims, selected)
    summary_path = Path(args.summary_out)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


def load_claims(
    run_id: str,
    seed_dir: Path,
    reviews_path: Path,
    run_index: int,
    reviewer_priority: list[str],
) -> list[dict[str, Any]]:
    tasks = {row["task_id"]: row for row in read_jsonl(seed_dir / "tasks.jsonl")}
    generations = {row["generation_id"]: row for row in read_jsonl(seed_dir / "generations.jsonl")}
    executions = {row["generation_id"]: row for row in read_jsonl(seed_dir / "executions.jsonl")}
    reviews = read_jsonl(reviews_path)

    claims: list[dict[str, Any]] = []
    for review in reviews:
        if not review.get("valid_review_json", True):
            continue
        if not bool(review.get("bug_found")):
            continue

        generation_id = str(review.get("generation_id", ""))
        task_id = str(review.get("task_id", ""))
        if generation_id not in generations or generation_id not in executions or task_id not in tasks:
            continue

        generation = generations[generation_id]
        execution = executions[generation_id]
        task = tasks[task_id]
        reviewer = str(review.get("reviewer_model") or review.get("model_id") or "")
        variant = str(generation.get("variant") or execution.get("variant") or "")
        candidate_label = "fixed_control" if bool(execution.get("passed")) else "buggy"
        confidence = parse_confidence(review.get("confidence"))

        claims.append(
            {
                "source_run_id": run_id,
                "source_run_priority": run_index,
                "review_id": review.get("review_id"),
                "project": task.get("project"),
                "bug_id": task.get("bug_id") or task.get("task_id"),
                "task_id": task_id,
                "candidate_id": generation_id,
                "candidate_oracle_label": candidate_label,
                "candidate_variant": variant,
                "reviewer": reviewer,
                "reviewer_model_id": review.get("reviewer_model_id") or review.get("model_id"),
                "reviewer_priority": priority_index(reviewer, reviewer_priority),
                "claim_text": str(review.get("explanation") or ""),
                "claim_location": str(review.get("location") or ""),
                "claim_bug_type": review.get("bug_type"),
                "claim_confidence": confidence,
                "suggested_fix": review.get("suggested_fix"),
                "source_files": generation.get("source_files", []),
                "source_context": generation.get("source_context"),
                "source_excerpt": generation.get("code"),
                "target_behavior": task.get("visible_regression_test_command")
                or task.get("visible_test_file")
                or task.get("prompt"),
                "oracle": execution.get("oracle"),
                "oracle_passed": bool(execution.get("passed")),
            }
        )

    return claims


def deduplicate_claims(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[tuple[str, ...], dict[str, Any]] = {}
    for claim in claims:
        key = (
            normalize(claim.get("project")),
            normalize(claim.get("bug_id")),
            normalize(claim.get("candidate_variant")),
            normalize(claim.get("reviewer")),
            normalize(claim.get("claim_location")),
            normalize(claim.get("claim_text"))[:160],
        )
        existing = by_key.get(key)
        if existing is None or claim_sort_key(claim) < claim_sort_key(existing):
            by_key[key] = claim
    return sorted(by_key.values(), key=claim_sort_key)


def select_balanced_claims(
    claims: list[dict[str, Any]],
    target_buggy: int,
    target_fixed: int,
) -> list[dict[str, Any]]:
    buggy = [claim for claim in claims if claim.get("candidate_oracle_label") == "buggy"]
    fixed = [claim for claim in claims if claim.get("candidate_oracle_label") == "fixed_control"]
    return buggy[:target_buggy] + fixed[:target_fixed]


def claim_sort_key(claim: dict[str, Any]) -> tuple[Any, ...]:
    return (
        int(claim.get("source_run_priority", 999)),
        int(claim.get("reviewer_priority", 999)),
        -int(claim.get("claim_confidence") or 0),
        str(claim.get("project") or ""),
        str(claim.get("bug_id") or ""),
        str(claim.get("candidate_id") or ""),
        str(claim.get("review_id") or ""),
    )


def summarize(
    all_claims: list[dict[str, Any]],
    unique_claims: list[dict[str, Any]],
    selected: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "raw_claims": len(all_claims),
        "unique_claims": len(unique_claims),
        "selected_claims": len(selected),
        "selected_buggy_claims": sum(1 for claim in selected if claim.get("candidate_oracle_label") == "buggy"),
        "selected_fixed_control_claims": sum(
            1 for claim in selected if claim.get("candidate_oracle_label") == "fixed_control"
        ),
        "selected_by_run": count_by(selected, "source_run_id"),
        "selected_by_reviewer": count_by(selected, "reviewer"),
    }


def count_by(records: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        value = str(record.get(key))
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def priority_index(value: str, priority: list[str]) -> int:
    try:
        return priority.index(value)
    except ValueError:
        return len(priority)


def parse_confidence(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def normalize(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


if __name__ == "__main__":
    main()
