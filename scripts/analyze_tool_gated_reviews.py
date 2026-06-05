from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze an oracle/tool-gated review policy over existing review records."
    )
    parser.add_argument("--executions", required=True, help="Execution/oracle JSONL.")
    parser.add_argument("--reviews", required=True, help="Review JSONL.")
    parser.add_argument("--reviewers", default="", help="Optional comma-separated reviewer keys.")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    executions = {row["generation_id"]: row for row in read_jsonl(Path(args.executions))}
    reviews = read_jsonl(Path(args.reviews))
    reviewers = [key.strip() for key in args.reviewers.split(",") if key.strip()]
    if reviewers:
        reviews = [row for row in reviews if row.get("reviewer_model") in reviewers]

    by_generation: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for review in reviews:
        generation_id = str(review["generation_id"])
        if generation_id not in executions:
            raise SystemExit(f"Missing execution oracle for review {review['review_id']}: {generation_id}")
        by_generation[generation_id].append(review)

    output = {
        "records": len(reviews),
        "generations": len(by_generation),
        "reviewers": sorted({str(row.get("reviewer_model")) for row in reviews}),
        "definition": {
            "tool_gate": "accept review bug_found=true only when the validated execution oracle says the candidate failed",
            "passed_false_means": "validated buggy/failing candidate",
            "passed_true_means": "validated fixed/reference passing control",
            "limitation": "This is an oracle-gated upper bound for specificity control, not a model-only review result.",
        },
        "record_level": {
            "raw": metrics_for_review_records(reviews, executions, gated=False),
            "tool_gated": metrics_for_review_records(reviews, executions, gated=True),
        },
        "policies": policy_metrics(by_generation, executions),
        "accepted_review_ids": accepted_review_ids(reviews, executions),
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        json.dumps(
            {
                "out": args.out,
                "records": output["records"],
                "generations": output["generations"],
                "reviewers": output["reviewers"],
                "raw_fpr": output["record_level"]["raw"]["false_positive_rate"],
                "tool_gated_fpr": output["record_level"]["tool_gated"]["false_positive_rate"],
            },
            indent=2,
        )
    )


def policy_metrics(
    by_generation: dict[str, list[dict[str, Any]]], executions: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    reviewers = sorted({str(review.get("reviewer_model")) for rows in by_generation.values() for review in rows})
    policies: dict[str, dict[str, Any]] = {}
    for reviewer in reviewers:
        predictions = {}
        for generation_id, rows in by_generation.items():
            matching = [row for row in rows if row.get("reviewer_model") == reviewer]
            if not matching:
                continue
            predictions[generation_id] = gated_vote(matching[0], executions[generation_id])
        policies[f"single:{reviewer}"] = metrics_for_generation_predictions(predictions, executions)

    for name, threshold_fn in {
        "aggregate:any_tool_gated": lambda count, total: count >= 1,
        "aggregate:at_least_2_tool_gated": lambda count, total: count >= 2,
        "aggregate:majority_tool_gated": lambda count, total: count > total / 2,
    }.items():
        predictions = {}
        for generation_id, rows in by_generation.items():
            votes = [gated_vote(row, executions[generation_id]) for row in rows]
            predictions[generation_id] = threshold_fn(sum(1 for vote in votes if vote), len(votes))
        policies[name] = metrics_for_generation_predictions(predictions, executions)
    return policies


def metrics_for_review_records(
    reviews: list[dict[str, Any]], executions: dict[str, dict[str, Any]], gated: bool
) -> dict[str, Any]:
    predictions: list[tuple[bool, bool]] = []
    for review in reviews:
        execution = executions[str(review["generation_id"])]
        actual_buggy = not bool(execution["passed"])
        if gated:
            predicted_buggy = gated_vote(review, execution)
        else:
            predicted_buggy = bool(review.get("bug_found")) and bool(review.get("valid_review_json", True))
        predictions.append((predicted_buggy, actual_buggy))
    return metrics(predictions)


def metrics_for_generation_predictions(
    predictions: dict[str, bool], executions: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    pairs = []
    for generation_id, predicted_buggy in predictions.items():
        actual_buggy = not bool(executions[generation_id]["passed"])
        pairs.append((predicted_buggy, actual_buggy))
    return metrics(pairs)


def gated_vote(review: dict[str, Any], execution: dict[str, Any]) -> bool:
    review_votes_bug = bool(review.get("bug_found")) and bool(review.get("valid_review_json", True))
    oracle_failed = not bool(execution["passed"])
    return review_votes_bug and oracle_failed


def accepted_review_ids(reviews: list[dict[str, Any]], executions: dict[str, dict[str, Any]]) -> list[str]:
    return [
        str(review["review_id"])
        for review in reviews
        if gated_vote(review, executions[str(review["generation_id"])])
    ]


def metrics(predictions: list[tuple[bool, bool]]) -> dict[str, Any]:
    tp = sum(1 for predicted, actual in predictions if predicted and actual)
    fp = sum(1 for predicted, actual in predictions if predicted and not actual)
    tn = sum(1 for predicted, actual in predictions if not predicted and not actual)
    fn = sum(1 for predicted, actual in predictions if not predicted and actual)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    return {
        "records": len(predictions),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_positive_rate": fpr,
    }


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


if __name__ == "__main__":
    main()
