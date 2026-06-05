from __future__ import annotations

from collections import defaultdict
from typing import Any


def detection_metrics(
    executions: list[dict[str, Any]],
    reviews: list[dict[str, Any]],
) -> dict[str, Any]:
    execution_by_generation = {row["generation_id"]: row for row in executions}
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for review in reviews:
        generation_id = review["generation_id"]
        if generation_id not in execution_by_generation:
            raise ValueError(f"Review references unknown generation_id: {generation_id}")
        execution = execution_by_generation[generation_id]
        ground_truth_buggy = not bool(execution["passed"])
        predicted_buggy = bool(review.get("bug_found", False))
        generator_model = str(review.get("generator_model") or execution.get("generator_model") or "unknown")
        reviewer_model = str(review.get("reviewer_model") or "unknown")
        generator_model_id = str(review.get("generator_model_id") or execution.get("model_id") or generator_model)
        reviewer_model_id = str(review.get("reviewer_model_id") or review.get("model_id") or reviewer_model)
        bug_source = review.get("bug_source") or execution.get("bug_source")
        enriched = {
            "ground_truth_buggy": ground_truth_buggy,
            "predicted_buggy": predicted_buggy,
            "review_type": review.get("review_type", "unknown"),
            "generator_model": generator_model,
            "reviewer_model": reviewer_model,
            "generator_model_id": generator_model_id,
            "reviewer_model_id": reviewer_model_id,
            "bug_source": bug_source,
        }
        groups["overall"].append(enriched)
        groups[f"review_type:{enriched['review_type']}"].append(enriched)
        groups[f"generator_model:{generator_model}"].append(enriched)
        groups[f"reviewer_model:{reviewer_model}"].append(enriched)
        groups[f"generator_reviewer_pair:{generator_model}->{reviewer_model}"].append(enriched)
        groups[f"generator_model_id:{generator_model_id}"].append(enriched)
        groups[f"reviewer_model_id:{reviewer_model_id}"].append(enriched)
        groups[f"generator_reviewer_model_id_pair:{generator_model_id}->{reviewer_model_id}"].append(enriched)
        if bug_source:
            groups[f"bug_source:{bug_source}"].append(enriched)
        valid_review_json = bool(review.get("valid_review_json", True))
        groups[f"valid_review_json:{valid_review_json}"].append(enriched)

    return {name: summarize_binary_detection(rows) for name, rows in sorted(groups.items())}


def repair_metrics(
    executions: list[dict[str, Any]],
    repair_executions: list[dict[str, Any]],
) -> dict[str, Any]:
    execution_by_generation = {row["generation_id"]: row for row in executions}
    attempts = len(repair_executions)
    successful_repairs = 0
    failed_repairs = 0
    regressions = 0
    unnecessary_but_passing = 0

    for repair in repair_executions:
        generation_id = repair["generation_id"]
        if generation_id not in execution_by_generation:
            raise ValueError(f"Repair references unknown generation_id: {generation_id}")
        original_passed = bool(execution_by_generation[generation_id]["passed"])
        repair_passed = bool(repair["passed"])
        if not original_passed and repair_passed:
            successful_repairs += 1
        elif not original_passed and not repair_passed:
            failed_repairs += 1
        elif original_passed and not repair_passed:
            regressions += 1
        elif original_passed and repair_passed:
            unnecessary_but_passing += 1

    return {
        "repair_attempts": attempts,
        "successful_repairs": successful_repairs,
        "failed_repairs": failed_repairs,
        "regressions": regressions,
        "unnecessary_but_passing": unnecessary_but_passing,
        "repair_success_rate": safe_divide(successful_repairs, successful_repairs + failed_repairs),
        "regression_rate": safe_divide(regressions, regressions + unnecessary_but_passing),
    }


def summarize_binary_detection(rows: list[dict[str, Any]]) -> dict[str, Any]:
    tp = fp = tn = fn = 0
    for row in rows:
        actual = row["ground_truth_buggy"]
        predicted = row["predicted_buggy"]
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
    false_positive_rate = safe_divide(fp, fp + tn)

    return {
        "records": len(rows),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_positive_rate": false_positive_rate,
    }


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator
