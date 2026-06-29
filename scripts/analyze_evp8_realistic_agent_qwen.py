"""Analyze Qwen verifier output on the EVP-8 realistic agent-patch cohort."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVALUATOR_IN = REPO_ROOT / "data" / "patches" / "evp8_realistic_agent_evaluator_manifest_v0_1.jsonl"
DEFAULT_BASELINE_IN = REPO_ROOT / "data" / "baselines" / "evp8_realistic_agent_visible_tool_baseline_v0_1.jsonl"
DEFAULT_REVIEWS_IN = REPO_ROOT / "data" / "reviews" / "evp8_realistic_agent_qwen_qwen_qwen3.7-max_full_reviews.jsonl"
DEFAULT_RUN_SUMMARY_IN = REPO_ROOT / "data" / "reviews" / "evp8_realistic_agent_qwen_qwen_qwen3.7-max_full_summary.json"
DEFAULT_SUMMARY_OUT = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_qwen_result_analysis_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_realistic_agent_qwen_result_analysis_v0_1.md"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{display_path(path)} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def display_path(path: Path) -> str:
    absolute = path if path.is_absolute() else REPO_ROOT / path
    try:
        return absolute.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(absolute)


def index_by_id(rows: list[dict[str, Any]], id_field: str, name: str) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for row in rows:
        candidate_id = str(row.get(id_field) or "")
        if not candidate_id:
            raise ValueError(f"{name} row missing {id_field}")
        if candidate_id in index:
            raise ValueError(f"{name} duplicate candidate id: {candidate_id}")
        index[candidate_id] = row
    return index


def wilson_interval(successes: int, total: int, z: float = 1.96) -> dict[str, float | None]:
    if total == 0:
        return {"low": None, "high": None}
    phat = successes / total
    denominator = 1 + z * z / total
    centre = phat + z * z / (2 * total)
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total)
    return {
        "low": round((centre - margin) / denominator, 4),
        "high": round((centre + margin) / denominator, 4),
    }


def metric(successes: int, total: int) -> dict[str, Any]:
    return {
        "successes": successes,
        "total": total,
        "value": None if total == 0 else round(successes / total, 4),
        "wilson_95": wilson_interval(successes, total),
    }


def decision_metrics(decisions: dict[str, str], labels: dict[str, str]) -> dict[str, Any]:
    correct_ids = {candidate_id for candidate_id, label in labels.items() if label == "correct"}
    wrong_ids = set(labels) - correct_ids
    accepted = {candidate_id for candidate_id, decision in decisions.items() if decision == "accept"}
    rejected = {candidate_id for candidate_id, decision in decisions.items() if decision == "reject"}
    escalated = {candidate_id for candidate_id, decision in decisions.items() if decision == "escalate"}
    return {
        "accepted_precision": metric(len(accepted & correct_ids), len(accepted)),
        "correct_recall": metric(len(accepted & correct_ids), len(correct_ids)),
        "false_accept_rate_among_wrong": metric(len(accepted & wrong_ids), len(wrong_ids)),
        "wrong_reject_rate": metric(len(rejected & wrong_ids), len(wrong_ids)),
        "correct_reject_rate": metric(len(rejected & correct_ids), len(correct_ids)),
        "escalation_rate": metric(len(escalated), len(labels)),
    }


def build_summary(
    evaluator_rows: list[dict[str, Any]],
    baseline_rows: list[dict[str, Any]],
    review_rows: list[dict[str, Any]],
    run_summary: dict[str, Any],
) -> dict[str, Any]:
    evaluator = index_by_id(evaluator_rows, "candidate_id", "evaluator")
    baseline = index_by_id(baseline_rows, "candidate_id", "baseline")
    reviews = index_by_id(review_rows, "anonymous_candidate_id", "reviews")
    ids = sorted(evaluator)
    if ids != sorted(baseline) or ids != sorted(reviews):
        raise ValueError("candidate id sets do not match")
    labels = {candidate_id: str(evaluator[candidate_id]["normalized_label"]) for candidate_id in ids}
    baseline_decisions = {candidate_id: str(baseline[candidate_id]["decision"]) for candidate_id in ids}
    qwen_decisions = {candidate_id: str(reviews[candidate_id]["decision"]) for candidate_id in ids}

    qwen_by_label: dict[str, Counter[str]] = defaultdict(Counter)
    baseline_by_label: dict[str, Counter[str]] = defaultdict(Counter)
    transition_counts: Counter[str] = Counter()
    disagreements: list[dict[str, Any]] = []
    for candidate_id in ids:
        label = labels[candidate_id]
        qwen_decision = qwen_decisions[candidate_id]
        baseline_decision = baseline_decisions[candidate_id]
        qwen_by_label[label][qwen_decision] += 1
        baseline_by_label[label][baseline_decision] += 1
        transition = f"{baseline_decision}->{qwen_decision}"
        transition_counts[transition] += 1
        if qwen_decision != baseline_decision:
            disagreements.append(
                {
                    "candidate_id": candidate_id,
                    "label": label,
                    "baseline_decision": baseline_decision,
                    "qwen_decision": qwen_decision,
                    "qwen_primary_reason": reviews[candidate_id].get("primary_reason"),
                    "qwen_risk_flags": reviews[candidate_id].get("risk_flags") or [],
                }
            )

    wrong_ids = {candidate_id for candidate_id in ids if labels[candidate_id] != "correct"}
    baseline_false_accepts = {
        candidate_id for candidate_id in wrong_ids if baseline_decisions[candidate_id] == "accept"
    }
    qwen_false_accepts = {
        candidate_id for candidate_id in wrong_ids if qwen_decisions[candidate_id] == "accept"
    }
    avoided_false_accepts = sorted(baseline_false_accepts - qwen_false_accepts)
    new_false_accepts = sorted(qwen_false_accepts - baseline_false_accepts)
    correct_ids = [candidate_id for candidate_id in ids if labels[candidate_id] == "correct"]

    return {
        "analysis_id": "evp8_realistic_agent_qwen_result_analysis_v0_1",
        "cohort_id": "EVP-8-REALISTIC-AGENT",
        "configured_model_id": run_summary.get("configured_model_id"),
        "review_count": len(review_rows),
        "parse_valid_count": run_summary.get("parse_valid_count"),
        "run_gate": run_summary.get("run_gate"),
        "label_counts": dict(sorted(Counter(labels.values()).items())),
        "visible_tool_decision_counts": dict(sorted(Counter(baseline_decisions.values()).items())),
        "qwen_decision_counts": dict(sorted(Counter(qwen_decisions.values()).items())),
        "visible_tool_by_label": {label: dict(sorted(counter.items())) for label, counter in sorted(baseline_by_label.items())},
        "qwen_by_label": {label: dict(sorted(counter.items())) for label, counter in sorted(qwen_by_label.items())},
        "baseline_to_qwen_transition_counts": dict(sorted(transition_counts.items())),
        "baseline_qwen_disagreement_count": len(disagreements),
        "baseline_qwen_disagreements": disagreements,
        "visible_tool_metrics": decision_metrics(baseline_decisions, labels),
        "qwen_metrics": decision_metrics(qwen_decisions, labels),
        "false_accept_reduction": {
            "visible_tool_false_accepts": len(baseline_false_accepts),
            "qwen_false_accepts": len(qwen_false_accepts),
            "avoided_false_accepts": len(avoided_false_accepts),
            "new_false_accepts": len(new_false_accepts),
            "relative_reduction": (
                None
                if not baseline_false_accepts
                else round((len(baseline_false_accepts) - len(qwen_false_accepts)) / len(baseline_false_accepts), 4)
            ),
            "avoided_false_accept_candidate_ids": avoided_false_accepts,
            "new_false_accept_candidate_ids": new_false_accepts,
        },
        "correct_patch_outcomes": [
            {
                "candidate_id": candidate_id,
                "visible_tool_decision": baseline_decisions[candidate_id],
                "qwen_decision": qwen_decisions[candidate_id],
                "qwen_primary_reason": reviews[candidate_id].get("primary_reason"),
            }
            for candidate_id in correct_ids
        ],
        "interpretation": {
            "qwen_added_value_over_visible_tool": len(disagreements) > 0,
            "qwen_matches_visible_tool_exactly": len(disagreements) == 0,
            "claim_boundary": "This run measures whether Qwen reduces visible-tool false accepts on realistic agent patches; it cannot support a strong correct-recall claim because the cohort has one correct patch.",
        },
    }


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    qwen = summary["qwen_metrics"]
    tool = summary["visible_tool_metrics"]
    reduction = summary["false_accept_reduction"]
    lines = [
        "# EVP-8 Realistic Agent Qwen Result Analysis v0.1",
        "",
        "Date: 2026-06-30",
        "",
        f"- model: `{summary['configured_model_id']}`",
        f"- reviews: `{summary['review_count']}`",
        f"- parse valid: `{summary['parse_valid_count']}`",
        f"- run gate: `{summary['run_gate']}`",
        f"- labels: `{summary['label_counts']}`",
        f"- visible-tool decisions: `{summary['visible_tool_decision_counts']}`",
        f"- Qwen decisions: `{summary['qwen_decision_counts']}`",
        f"- baseline to Qwen transitions: `{summary['baseline_to_qwen_transition_counts']}`",
        "",
        "Metric comparison:",
        "",
        f"- visible-tool accepted precision: `{tool['accepted_precision']['successes']}/{tool['accepted_precision']['total']}` = `{tool['accepted_precision']['value']}`",
        f"- Qwen accepted precision: `{qwen['accepted_precision']['successes']}/{qwen['accepted_precision']['total']}` = `{qwen['accepted_precision']['value']}`",
        f"- visible-tool false accept rate among wrong: `{tool['false_accept_rate_among_wrong']['successes']}/{tool['false_accept_rate_among_wrong']['total']}` = `{tool['false_accept_rate_among_wrong']['value']}`",
        f"- Qwen false accept rate among wrong: `{qwen['false_accept_rate_among_wrong']['successes']}/{qwen['false_accept_rate_among_wrong']['total']}` = `{qwen['false_accept_rate_among_wrong']['value']}`",
        f"- false accepts avoided by Qwen: `{reduction['avoided_false_accepts']}`",
        f"- new false accepts introduced by Qwen: `{reduction['new_false_accepts']}`",
        f"- correct patch outcomes: `{summary['correct_patch_outcomes']}`",
        "",
        "Interpretation:",
        "",
    ]
    if summary["interpretation"]["qwen_matches_visible_tool_exactly"]:
        lines.extend(
            [
                "- Qwen exactly matched the deterministic visible-tool baseline on all 53 candidates.",
                "- It did not reduce false accepts in this evidence setting.",
                "- The result supports a negative finding: with a visible merge-gate summary present, Qwen behaves like a policy follower rather than adding independent semantic verification value.",
            ]
        )
    else:
        lines.extend(
            [
                "- Qwen changed at least one deterministic visible-tool decision.",
                "- The changed cases should be inspected before claiming added value.",
            ]
        )
    lines.append(f"- Claim boundary: {summary['interpretation']['claim_boundary']}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluator-in", type=Path, default=DEFAULT_EVALUATOR_IN)
    parser.add_argument("--baseline-in", type=Path, default=DEFAULT_BASELINE_IN)
    parser.add_argument("--reviews-in", type=Path, default=DEFAULT_REVIEWS_IN)
    parser.add_argument("--run-summary-in", type=Path, default=DEFAULT_RUN_SUMMARY_IN)
    parser.add_argument("--summary-out", type=Path, default=DEFAULT_SUMMARY_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--expected-count", type=int, default=53)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = build_summary(
        evaluator_rows=read_jsonl(args.evaluator_in),
        baseline_rows=read_jsonl(args.baseline_in),
        review_rows=read_jsonl(args.reviews_in),
        run_summary=read_json(args.run_summary_in),
    )
    if args.check:
        if summary["review_count"] != args.expected_count:
            raise SystemExit(f"expected {args.expected_count} reviews, got {summary['review_count']}")
        if summary["parse_valid_count"] != args.expected_count:
            raise SystemExit(f"expected {args.expected_count} parse-valid reviews, got {summary['parse_valid_count']}")
        if summary["run_gate"] != "passed":
            raise SystemExit(f"run gate is not passed: {summary['run_gate']}")
    write_json(args.summary_out, summary)
    write_markdown(args.md_out, summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
