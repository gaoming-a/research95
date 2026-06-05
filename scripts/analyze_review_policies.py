from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable


DEFAULT_SOURCE_ROUTING_REVIEWERS = {"gpt", "claude", "deepseek", "qwen"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze aggregation and routing policies over review records.")
    parser.add_argument(
        "--run",
        action="append",
        required=True,
        help="Run input in label=run_dir format. run_dir must contain executions.jsonl and reviews.jsonl.",
    )
    parser.add_argument(
        "--reviewers",
        default=None,
        help="Comma-separated reviewer keys. If omitted, infer reviewers from the input review records.",
    )
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    records: list[dict[str, Any]] = []
    reviewers = parse_reviewers(args.reviewers)
    for value in args.run:
        label, run_dir = parse_run_arg(value)
        records.extend(load_run(label, Path(run_dir), reviewers))

    if reviewers is None:
        reviewers = tuple(sorted({reviewer for row in records for reviewer in row["reviews"]}))
        records = require_reviewers(records, reviewers)

    policies = build_policies(reviewers)
    result = {
        "records": len(records),
        "generation_records": len({row["generation_id"] for row in records}),
        "policies": {
            name: evaluate_policy(records, policy)
            for name, policy in policies.items()
        },
    }

    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"out": str(output), "policies": sorted(result["policies"])}, indent=2))


def parse_run_arg(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise SystemExit("--run must use label=run_dir")
    label, run_dir = value.split("=", 1)
    if not label or not run_dir:
        raise SystemExit("--run must use label=run_dir")
    return label, run_dir


def load_run(label: str, run_dir: Path, reviewers: tuple[str, ...] | None) -> list[dict[str, Any]]:
    executions = {row["generation_id"]: row for row in read_jsonl(run_dir / "executions.jsonl")}
    reviews = read_jsonl(run_dir / "reviews.jsonl")
    reviews_by_generation: dict[str, dict[str, dict[str, Any]]] = {}

    for review in reviews:
        generation_id = review["generation_id"]
        reviewer = review["reviewer_model"]
        reviews_by_generation.setdefault(generation_id, {})[reviewer] = review

    records: list[dict[str, Any]] = []
    for generation_id, execution in sorted(executions.items()):
        by_reviewer = reviews_by_generation.get(generation_id, {})
        bug_source = execution.get("bug_source")
        if not bug_source:
            first_review = next(iter(by_reviewer.values()))
            bug_source = first_review.get("bug_source")
        records.append(
            {
                "run_label": label,
                "generation_id": generation_id,
                "task_id": execution["task_id"],
                "bug_source": bug_source,
                "ground_truth_buggy": not bool(execution["passed"]),
                "reviews": by_reviewer,
            }
        )
    if reviewers is None:
        return records
    return require_reviewers(records, reviewers, label)


def require_reviewers(
    records: list[dict[str, Any]], reviewers: tuple[str, ...], label: str | None = None
) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    for row in records:
        missing = sorted(set(reviewers) - set(row["reviews"]))
        if missing:
            prefix = f"{label}: " if label else ""
            raise SystemExit(f"{prefix}missing reviews for {row['generation_id']}: {missing}")
        filtered_row = dict(row)
        filtered_row["reviews"] = {reviewer: row["reviews"][reviewer] for reviewer in reviewers}
        filtered.append(filtered_row)
    return filtered


def parse_reviewers(value: str | None) -> tuple[str, ...] | None:
    if value is None:
        return None
    reviewers = tuple(item.strip() for item in value.split(",") if item.strip())
    if not reviewers:
        raise SystemExit("--reviewers must contain at least one reviewer key when provided")
    return reviewers


def build_policies(reviewers: tuple[str, ...]) -> dict[str, Callable[[dict[str, Any]], tuple[bool, list[str]]]]:
    policies: dict[str, Callable[[dict[str, Any]], tuple[bool, list[str]]]] = {}
    for reviewer in reviewers:
        policies[f"single:{reviewer}"] = lambda row, reviewer=reviewer: single_reviewer(row, reviewer)
    policies["aggregate:any_all"] = any_all
    policies["aggregate:at_least_2"] = at_least_2
    policies["aggregate:majority"] = majority
    if DEFAULT_SOURCE_ROUTING_REVIEWERS.issubset(set(reviewers)):
        policies["routing:source_low_false_positive"] = source_low_false_positive
        policies["routing:source_high_recall"] = source_high_recall
        policies["routing:source_cost_aware"] = source_cost_aware
    return policies


def single_reviewer(row: dict[str, Any], reviewer: str) -> tuple[bool, list[str]]:
    review = row["reviews"][reviewer]
    return bool(review.get("bug_found", False)), [reviewer]


def any_all(row: dict[str, Any]) -> tuple[bool, list[str]]:
    reviewers = list(row["reviews"])
    return any(bool(row["reviews"][reviewer].get("bug_found", False)) for reviewer in reviewers), reviewers


def at_least_2(row: dict[str, Any]) -> tuple[bool, list[str]]:
    reviewers = list(row["reviews"])
    votes = sum(1 for reviewer in reviewers if bool(row["reviews"][reviewer].get("bug_found", False)))
    return votes >= 2, reviewers


def majority(row: dict[str, Any]) -> tuple[bool, list[str]]:
    reviewers = list(row["reviews"])
    votes = sum(1 for reviewer in reviewers if bool(row["reviews"][reviewer].get("bug_found", False)))
    return votes > len(reviewers) / 2, reviewers


def source_low_false_positive(row: dict[str, Any]) -> tuple[bool, list[str]]:
    return single_reviewer(row, "qwen")


def source_high_recall(row: dict[str, Any]) -> tuple[bool, list[str]]:
    if row.get("bug_source") == "natural_logic_spec_boundary":
        return single_reviewer(row, "claude")
    return single_reviewer(row, "qwen")


def source_cost_aware(row: dict[str, Any]) -> tuple[bool, list[str]]:
    if row.get("bug_source") == "natural_logic_spec_boundary":
        return single_reviewer(row, "deepseek")
    return single_reviewer(row, "gpt")


def evaluate_policy(
    records: list[dict[str, Any]],
    policy: Callable[[dict[str, Any]], tuple[bool, list[str]]],
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    total_review_cost = 0.0
    review_calls = 0

    for row in records:
        predicted_buggy, reviewers_used = policy(row)
        actual_buggy = bool(row["ground_truth_buggy"])
        for reviewer in reviewers_used:
            total_review_cost += review_cost(row["reviews"][reviewer])
            review_calls += 1
        rows.append(
            {
                "actual": actual_buggy,
                "predicted": predicted_buggy,
                "bug_source": row.get("bug_source"),
            }
        )

    summary = summarize(rows)
    summary["review_calls"] = review_calls
    summary["review_cost"] = total_review_cost
    summary["cost_per_detected_tp"] = safe_divide(total_review_cost, summary["tp"])
    summary["predicted_buggy"] = summary["tp"] + summary["fp"]
    summary["by_bug_source"] = {
        bug_source: summarize([row for row in rows if row.get("bug_source") == bug_source])
        for bug_source in sorted({str(row.get("bug_source")) for row in rows})
    }
    return summary


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    tp = fp = tn = fn = 0
    for row in rows:
        actual = bool(row["actual"])
        predicted = bool(row["predicted"])
        if actual and predicted:
            tp += 1
        elif not actual and predicted:
            fp += 1
        elif not actual and not predicted:
            tn += 1
        else:
            fn += 1

    precision = safe_divide(tp, tp + fp)
    recall = safe_divide(tp, tp + fn)
    f1 = safe_divide(2 * precision * recall, precision + recall)
    return {
        "records": len(rows),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_positive_rate": safe_divide(fp, fp + tn),
    }


def review_cost(review: dict[str, Any]) -> float:
    usage = review.get("usage") or {}
    if not isinstance(usage, dict):
        return 0.0
    return float(usage.get("cost") or 0.0)


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
