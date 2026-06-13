"""Analyze EVP-7 merge-gate review decisions with G5 metrics.

The default input remains the deterministic schema dry-run. The same metric
path is also used for mock workflow records and real G5 LLM verifier outputs,
so this module explicitly labels the review source before stating what the
metrics can support.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEWS_IN = REPO_ROOT / "data" / "reviews" / "evp7_merge_gate_schema_dry_run.jsonl"
CANDIDATES_IN = REPO_ROOT / "data" / "patches" / "evp7_candidates.jsonl"
METRICS_OUT = REPO_ROOT / "data" / "reviews" / "evp7_schema_dry_run_metrics.json"

EVIDENCE_LEVELS = ("E0", "E2", "E4", "E6")
CORRECT_LABEL = "correct_under_f2p_and_p2p_broad"
FACR_THRESHOLDS = (0.0, 0.01, 0.05, 0.1)
UTILITY_WEIGHTS = {
    "accept_correct": 1.0,
    "accept_wrong": -5.0,
    "escalate": -0.25,
    "reject_correct": -1.0,
}
EVALUATOR_MARKERS = (
    "label_with_p2p_broad",
    "label_retained_oracle",
    "candidate_type",
    "failure_type_label",
    "expected_outcome",
    "hidden_oracles",
    "patch_id",
    "correct_under_f2p_and_p2p_broad",
    "incorrect_issue_not_fixed",
)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _candidate_labels(path: Path) -> dict[str, str]:
    return {
        record["evp7_candidate_id"]: record["label_with_p2p_broad"]
        for record in _read_jsonl(path)
    }


def build_metrics(reviews_path: Path, candidates_path: Path) -> dict[str, Any]:
    reviews_path = _abs(reviews_path)
    candidates_path = _abs(candidates_path)
    reviews = _read_jsonl(reviews_path)
    labels = _candidate_labels(candidates_path)
    run_kind = _run_kind(reviews)
    groups = {
        level: _metrics_for_level(reviews, labels, level)
        for level in EVIDENCE_LEVELS
    }
    baseline_utility = groups["E0"]["utility"]["score"]
    for level, group in groups.items():
        group["evidence_gain_vs_e0"] = round(group["utility"]["score"] - baseline_utility, 6)
        group["facr"] = _facr(group)

    signal_preview = _signal_preview(groups)
    metrics = {
        "cohort_id": "EVP-7",
        "analysis_input": str(reviews_path.relative_to(REPO_ROOT)),
        "run_kind": run_kind,
        "api_call_attempted": any(record.get("api_call_attempted") is True for record in reviews),
        "model_call_attempted": any(record.get("api_call_attempted") is True for record in reviews),
        "mock_run": any(record.get("mock_run") is True for record in reviews),
        "candidate_count": len(labels),
        "review_record_count": len(reviews),
        "evidence_levels": list(EVIDENCE_LEVELS),
        "metric_groups": groups,
        "utility_weights": UTILITY_WEIGHTS,
        "facr_thresholds": list(FACR_THRESHOLDS),
        "signal_preview": signal_preview,
        "g5_metric_scaffold": "passed" if _scaffold_passed(reviews, groups) else "not_passed",
        "g5_signal_claim_status": _signal_claim_status(run_kind, reviews, groups, signal_preview),
        "analysis_boundary": _analysis_boundary(run_kind),
        "label_join_boundary": "Evaluator labels are joined only for aggregate metrics, never copied into dry-run review records.",
    }
    if run_kind == "schema_dry_run":
        metrics["dry_run_boundary"] = (
            "Deterministic schema dry-run metrics validate the analysis path only; "
            "they are not model-effect evidence."
        )
    return metrics


def _metrics_for_level(reviews: list[dict[str, Any]], labels: dict[str, str], level: str) -> dict[str, Any]:
    selected = [record for record in reviews if record["evidence_level"] == level]
    counts = {
        "true_accept": 0,
        "false_accept": 0,
        "true_reject": 0,
        "false_reject": 0,
        "escalated_correct": 0,
        "escalated_incorrect": 0,
        "invalid_output": 0,
    }
    for record in selected:
        parsed = record.get("parsed_output") or {}
        decision = parsed.get("decision") if record.get("parse_status") == "valid" else "invalid_output"
        label = labels[record["candidate_id"]]
        correct = label == CORRECT_LABEL
        if decision == "accept" and correct:
            counts["true_accept"] += 1
        elif decision == "accept":
            counts["false_accept"] += 1
        elif decision == "reject" and correct:
            counts["false_reject"] += 1
        elif decision == "reject":
            counts["true_reject"] += 1
        elif decision == "escalate" and correct:
            counts["escalated_correct"] += 1
        elif decision == "escalate":
            counts["escalated_incorrect"] += 1
        else:
            counts["invalid_output"] += 1

    accepted = counts["true_accept"] + counts["false_accept"]
    correct_total = counts["true_accept"] + counts["false_reject"] + counts["escalated_correct"]
    incorrect_total = counts["false_accept"] + counts["true_reject"] + counts["escalated_incorrect"]
    escalated = counts["escalated_correct"] + counts["escalated_incorrect"]
    valid = len(selected)
    return {
        "record_count": len(selected),
        "decision_counts": _counts(
            (record.get("parsed_output") or {}).get("decision", "invalid_output")
            if record.get("parse_status") == "valid"
            else "invalid_output"
            for record in selected
        ),
        "confusion_counts": counts,
        "accepted_precision": _ratio(counts["true_accept"], accepted),
        "false_accept_rate": _ratio(counts["false_accept"], incorrect_total),
        "correct_recall": _ratio(counts["true_accept"], correct_total),
        "false_reject_rate": _ratio(counts["false_reject"], correct_total),
        "escalation_rate": _ratio(escalated, valid),
        "invalid_output_rate": _ratio(counts["invalid_output"], valid),
        "utility": _utility(counts, selected_count=valid),
    }


def _utility(counts: dict[str, int], selected_count: int) -> dict[str, Any]:
    escalated = counts["escalated_correct"] + counts["escalated_incorrect"]
    score = (
        UTILITY_WEIGHTS["accept_correct"] * counts["true_accept"]
        + UTILITY_WEIGHTS["accept_wrong"] * counts["false_accept"]
        + UTILITY_WEIGHTS["escalate"] * escalated
        + UTILITY_WEIGHTS["reject_correct"] * counts["false_reject"]
    )
    return {
        "score": round(score, 6),
        "score_per_candidate": _ratio_float(score, selected_count),
        "formula": "accept_correct - 5*accept_wrong - 0.25*escalate - reject_correct",
    }


def _facr(group: dict[str, Any]) -> dict[str, Any]:
    far = group["false_accept_rate"]
    recall = group["correct_recall"]
    return {
        f"far_le_{threshold:g}": recall if far is not None and recall is not None and far <= threshold else None
        for threshold in FACR_THRESHOLDS
    }


def _signal_preview(groups: dict[str, dict[str, Any]]) -> dict[str, Any]:
    metrics = ("false_accept_rate", "correct_recall", "escalation_rate")
    deltas = {
        metric: {
            level: _delta(groups[level][metric], groups["E0"][metric])
            for level in EVIDENCE_LEVELS
            if level != "E0"
        }
        for metric in metrics
    }
    utility_deltas = {
        level: groups[level]["evidence_gain_vs_e0"]
        for level in EVIDENCE_LEVELS
        if level != "E0"
    }
    return {
        "has_metric_variation": any(
            value not in {None, 0.0}
            for metric_deltas in deltas.values()
            for value in metric_deltas.values()
        )
        or any(value != 0.0 for value in utility_deltas.values()),
        "metric_deltas_vs_e0": deltas,
        "evidence_gain_vs_e0": utility_deltas,
        "interpretation_boundary": "Interpret this preview according to run_kind and analysis_boundary.",
    }


def _scaffold_passed(reviews: list[dict[str, Any]], groups: dict[str, dict[str, Any]]) -> bool:
    if len(reviews) != 200:
        return False
    return all(groups[level]["record_count"] == 50 for level in EVIDENCE_LEVELS)


def _run_kind(reviews: list[dict[str, Any]]) -> str:
    if not reviews:
        return "empty"
    if any(record.get("dry_run") is True or record.get("schema_dry_run_id") for record in reviews):
        return "schema_dry_run"
    if any(record.get("mock_run") is True for record in reviews):
        return "mock_workflow"
    if any(record.get("api_call_attempted") is True and record.get("mock_run") is False for record in reviews):
        return "real_llm"
    return "unknown"


def _signal_claim_status(
    run_kind: str,
    reviews: list[dict[str, Any]],
    groups: dict[str, dict[str, Any]],
    signal_preview: dict[str, Any],
) -> str:
    scaffold_passed = _scaffold_passed(reviews, groups)
    if run_kind != "real_llm":
        return "requires_real_llm_verifier_outputs"
    if not scaffold_passed:
        return "real_llm_verifier_outputs_incomplete"
    if signal_preview["has_metric_variation"]:
        return "real_llm_verifier_signal_observed_on_evp7"
    return "real_llm_verifier_outputs_available_no_metric_variation"


def _analysis_boundary(run_kind: str) -> str:
    if run_kind == "real_llm":
        return (
            "These metrics come from real LLM verifier outputs on the EVP-7 pilot. "
            "They can support EVP-7 pilot signal claims after quality audit, but "
            "not scale-generalized paper claims without controlled expansion."
        )
    if run_kind == "mock_workflow":
        return (
            "Mock workflow metrics validate parser, ordering, and aggregate metric "
            "plumbing only. They are not model-effect evidence."
        )
    if run_kind == "schema_dry_run":
        return (
            "Deterministic schema dry-run metrics validate the analysis path only. "
            "They are not model-effect evidence."
        )
    return "Unknown review source; do not use for model-effect claims without inspection."


def _counts(values: Any) -> dict[str, int]:
    result: dict[str, int] = {}
    for value in values:
        key = str(value)
        result[key] = result.get(key, 0) + 1
    return dict(sorted(result.items()))


def _ratio(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 6)


def _ratio_float(numerator: float, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 6)


def _delta(value: float | None, baseline: float | None) -> float | None:
    if value is None or baseline is None:
        return None
    return round(value - baseline, 6)


def leakage_audit_reviews(reviews_path: Path) -> list[str]:
    reviews_path = _abs(reviews_path)
    serialized = reviews_path.read_text(encoding="utf-8")
    return [marker for marker in EVALUATOR_MARKERS if marker in serialized]


def _abs(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def _check(metrics: dict[str, Any], reviews_path: Path) -> None:
    if metrics["g5_metric_scaffold"] != "passed":
        raise SystemExit(f"G5 metric scaffold did not pass: {metrics['g5_metric_scaffold']}")
    if metrics["run_kind"] != "real_llm" and metrics["g5_signal_claim_status"] != "requires_real_llm_verifier_outputs":
        raise SystemExit("non-real metrics must not mark G5 signal as observed")
    findings = leakage_audit_reviews(reviews_path)
    if findings:
        raise SystemExit(f"evaluator marker leaked into dry-run review records: {findings}")
    for level, group in metrics["metric_groups"].items():
        if group["record_count"] != 50:
            raise SystemExit(f"{level} record count changed: {group['record_count']}")
        required = {
            "accepted_precision",
            "false_accept_rate",
            "correct_recall",
            "false_reject_rate",
            "escalation_rate",
            "invalid_output_rate",
            "facr",
            "evidence_gain_vs_e0",
        }
        missing = required - set(group)
        if missing:
            raise SystemExit(f"{level} missing metric keys: {sorted(missing)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviews-in", type=Path, default=REVIEWS_IN)
    parser.add_argument("--candidates-in", type=Path, default=CANDIDATES_IN)
    parser.add_argument("--metrics-out", type=Path, default=METRICS_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    metrics = build_metrics(args.reviews_in, args.candidates_in)
    args.metrics_out.parent.mkdir(parents=True, exist_ok=True)
    args.metrics_out.write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check:
        _check(metrics, args.reviews_in)
    print(json.dumps(metrics, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
