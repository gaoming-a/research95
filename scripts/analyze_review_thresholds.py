from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze reviewer-specific and aggregate confidence thresholds over review records."
    )
    parser.add_argument(
        "--run",
        action="append",
        required=True,
        help="Input in label=run_dir form. run_dir must contain reviews.jsonl and executions.jsonl.",
    )
    parser.add_argument("--reviewers", required=True, help="Comma-separated reviewer keys.")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    reviewers = [item.strip() for item in args.reviewers.split(",") if item.strip()]
    if not reviewers:
        raise SystemExit("--reviewers must contain at least one reviewer")

    output: dict[str, Any] = {"runs": {}, "combined": {}}
    combined_records: list[dict[str, Any]] = []
    for run_spec in args.run:
        label, run_dir = parse_run(run_spec)
        records = load_records(label, Path(run_dir), reviewers)
        output["runs"][label] = analyze_records(records, reviewers)
        combined_records.extend(records)
    output["combined"] = analyze_records(combined_records, reviewers)

    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"out": str(path), "records": len(combined_records)}, indent=2))


def parse_run(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise SystemExit("--run must use label=run_dir format")
    label, run_dir = value.split("=", 1)
    if not label or not run_dir:
        raise SystemExit("--run must use non-empty label=run_dir format")
    return label, run_dir


def load_records(label: str, run_dir: Path, reviewers: list[str]) -> list[dict[str, Any]]:
    executions_path = run_dir / "executions.jsonl"
    if not executions_path.exists():
        executions_path = run_dir / "seed" / "executions.jsonl"
    executions = {row["generation_id"]: row for row in read_jsonl(executions_path)}
    reviews_by_generation: dict[str, dict[str, dict[str, Any]]] = {}
    for review in read_jsonl(run_dir / "reviews.jsonl"):
        reviews_by_generation.setdefault(review["generation_id"], {})[review["reviewer_model"]] = review

    records = []
    for generation_id, execution in sorted(executions.items()):
        reviews = reviews_by_generation.get(generation_id, {})
        missing = sorted(set(reviewers) - set(reviews))
        if missing:
            raise SystemExit(f"{label}: missing reviews for {generation_id}: {missing}")
        records.append(
            {
                "run": label,
                "generation_id": generation_id,
                "actual_buggy": not bool(execution.get("passed")),
                "reviews": {reviewer: reviews[reviewer] for reviewer in reviewers},
            }
        )
    return records


def analyze_records(records: list[dict[str, Any]], reviewers: list[str]) -> dict[str, Any]:
    policies: dict[str, Any] = {}
    for reviewer in reviewers:
        for threshold in range(1, 6):
            name = f"single:{reviewer}:confidence>={threshold}"
            policies[name] = score_policy(
                records,
                lambda row, reviewer=reviewer, threshold=threshold: review_vote(
                    row["reviews"][reviewer], threshold
                ),
            )
    for threshold in range(1, 6):
        policies[f"aggregate:any:confidence>={threshold}"] = score_policy(
            records,
            lambda row, threshold=threshold: any(
                review_vote(row["reviews"][reviewer], threshold) for reviewer in reviewers
            ),
        )
        policies[f"aggregate:majority:confidence>={threshold}"] = score_policy(
            records,
            lambda row, threshold=threshold: sum(
                review_vote(row["reviews"][reviewer], threshold) for reviewer in reviewers
            )
            > len(reviewers) / 2,
        )
        policies[f"aggregate:at_least_2:confidence>={threshold}"] = score_policy(
            records,
            lambda row, threshold=threshold: sum(
                review_vote(row["reviews"][reviewer], threshold) for reviewer in reviewers
            )
            >= 2,
        )

    ranked_by_f1 = sorted(
        policies.items(),
        key=lambda item: (item[1]["f1"], item[1]["recall"], item[1]["precision"]),
        reverse=True,
    )
    ranked_by_low_fpr = sorted(
        policies.items(),
        key=lambda item: (item[1]["false_positive_rate"], -item[1]["recall"], -item[1]["precision"]),
    )
    return {
        "records": len(records),
        "policies": policies,
        "top_f1": ranked_by_f1[:10],
        "top_low_fpr": ranked_by_low_fpr[:10],
    }


def review_vote(review: dict[str, Any], threshold: int) -> bool:
    if not bool(review.get("valid_review_json", True)):
        return False
    if not bool(review.get("bug_found", False)):
        return False
    try:
        confidence = int(review.get("confidence", 0))
    except (TypeError, ValueError):
        confidence = 0
    return confidence >= threshold


def score_policy(records: list[dict[str, Any]], predict_buggy: Any) -> dict[str, Any]:
    tp = fp = tn = fn = 0
    predicted_buggy = 0
    for row in records:
        prediction = bool(predict_buggy(row))
        actual = bool(row["actual_buggy"])
        if prediction:
            predicted_buggy += 1
        if prediction and actual:
            tp += 1
        elif prediction and not actual:
            fp += 1
        elif not prediction and not actual:
            tn += 1
        else:
            fn += 1
    return {
        "records": len(records),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": safe_divide(tp, tp + fp),
        "recall": safe_divide(tp, tp + fn),
        "f1": safe_divide(2 * tp, 2 * tp + fp + fn),
        "false_positive_rate": safe_divide(fp, fp + tn),
        "predicted_buggy": predicted_buggy,
    }


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


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
