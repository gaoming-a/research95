from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze false-positive patterns in real-bug review records.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--reviewers", required=True, help="Comma-separated reviewer keys.")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    reviewers = [item.strip() for item in args.reviewers.split(",") if item.strip()]
    if not reviewers:
        raise SystemExit("--reviewers must contain at least one reviewer")

    run_dir = Path(args.run_dir)
    seed_dir = run_dir / "seed"
    tasks = {row["task_id"]: row for row in read_jsonl(seed_dir / "tasks.jsonl")}
    generations = {row["generation_id"]: row for row in read_jsonl(seed_dir / "generations.jsonl")}
    executions = {row["generation_id"]: row for row in read_jsonl(seed_dir / "executions.jsonl")}
    reviews_by_generation: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for review in read_jsonl(run_dir / "reviews.jsonl"):
        reviews_by_generation[review["generation_id"]][review["reviewer_model"]] = review

    records = []
    project_counts: Counter[str] = Counter()
    reviewer_fp_counts: Counter[str] = Counter()
    reviewer_tp_counts: Counter[str] = Counter()
    majority_fp_records = []
    majority_fn_records = []

    for generation_id, execution in sorted(executions.items()):
        generation = generations[generation_id]
        task = tasks[generation["task_id"]]
        reviews = reviews_by_generation[generation_id]
        missing = sorted(set(reviewers) - set(reviews))
        if missing:
            raise SystemExit(f"Missing reviews for {generation_id}: {missing}")

        actual_buggy = not bool(execution.get("passed"))
        votes = []
        for reviewer in reviewers:
            review = reviews[reviewer]
            vote = bool(review.get("valid_review_json", True)) and bool(review.get("bug_found", False))
            votes.append((reviewer, vote, review))
            if vote and actual_buggy:
                reviewer_tp_counts[reviewer] += 1
            if vote and not actual_buggy:
                reviewer_fp_counts[reviewer] += 1

        majority_bug = sum(1 for _, vote, _ in votes if vote) > len(reviewers) / 2
        project = str(task.get("project") or "unknown")
        project_counts[project] += 1
        record = {
            "generation_id": generation_id,
            "task_id": generation["task_id"],
            "project": project,
            "variant": generation.get("variant"),
            "actual_buggy": actual_buggy,
            "majority_bug": majority_bug,
            "vote_count": sum(1 for _, vote, _ in votes if vote),
            "source_files": generation.get("source_files", []),
            "code_truncated": "# ... truncated ..." in str(generation.get("code", "")),
            "reviewer_votes": {
                reviewer: {
                    "bug_found": vote,
                    "valid_review_json": bool(review.get("valid_review_json", True)),
                    "bug_type": review.get("bug_type"),
                    "confidence": review.get("confidence"),
                    "location": review.get("location"),
                    "explanation": review.get("explanation"),
                }
                for reviewer, vote, review in votes
            },
        }
        records.append(record)
        if majority_bug and not actual_buggy:
            majority_fp_records.append(record)
        if not majority_bug and actual_buggy:
            majority_fn_records.append(record)

    output = {
        "records": len(records),
        "projects": dict(project_counts),
        "majority_false_positives": len(majority_fp_records),
        "majority_false_negatives": len(majority_fn_records),
        "majority_false_positive_ids": [row["generation_id"] for row in majority_fp_records],
        "majority_false_negative_ids": [row["generation_id"] for row in majority_fn_records],
        "reviewer_false_positive_counts": dict(reviewer_fp_counts),
        "reviewer_true_positive_counts": dict(reviewer_tp_counts),
        "majority_false_positives_by_project": dict(Counter(row["project"] for row in majority_fp_records)),
        "majority_false_positives_truncated": sum(1 for row in majority_fp_records if row["code_truncated"]),
        "majority_false_negatives_truncated": sum(1 for row in majority_fn_records if row["code_truncated"]),
        "majority_false_positive_records": majority_fp_records,
        "majority_false_negative_records": majority_fn_records,
    }

    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        json.dumps(
            {
                "out": str(path),
                "records": output["records"],
                "majority_false_positives": output["majority_false_positives"],
                "majority_false_negatives": output["majority_false_negatives"],
            },
            indent=2,
        )
    )


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"Expected object at {path}:{line_number}")
            records.append(value)
    return records


if __name__ == "__main__":
    main()
