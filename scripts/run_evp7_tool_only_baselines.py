"""Run deterministic tool-only baselines over EVP-7 evidence packets.

Decision records are generated only from model-visible evidence packets.
Evaluator labels are joined only for aggregate metrics.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKETS_IN = REPO_ROOT / "data" / "evidence" / "evp7_evidence_packets.jsonl"
CANDIDATES_IN = REPO_ROOT / "data" / "patches" / "evp7_candidates.jsonl"
DECISIONS_OUT = REPO_ROOT / "data" / "baselines" / "evp7_tool_only_decisions.jsonl"
METRICS_OUT = REPO_ROOT / "data" / "baselines" / "evp7_tool_only_metrics.json"

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


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )


def _packets_by_candidate(path: Path) -> dict[str, dict[str, dict[str, Any]]]:
    result: dict[str, dict[str, dict[str, Any]]] = {}
    for packet in _read_jsonl(path):
        candidate_id = packet["model_visible"]["candidate_id"]
        result.setdefault(candidate_id, {})[packet["evidence_level"]] = packet
    return result


def _candidate_labels(path: Path) -> dict[str, str]:
    return {
        record["evp7_candidate_id"]: record["label_with_p2p_broad"]
        for record in _read_jsonl(path)
    }


def _apply_only(candidate_id: str, packets: dict[str, dict[str, Any]]) -> dict[str, Any]:
    e2 = packets["E2"]
    patch_applies = (e2.get("visible_static_evidence") or {}).get("patch_applies")
    if patch_applies is False:
        return _decision(candidate_id, "tool_only_apply_only", "E2", "reject", 1.0, "Patch does not apply.", ["visible_static_evidence.patch_applies=false"], ["patch_apply_failed"])
    return _decision(candidate_id, "tool_only_apply_only", "E2", "escalate", 1.0, "Patch applies, but apply evidence alone is insufficient.", ["visible_static_evidence.patch_applies=true"], ["insufficient_evidence"])


def _visible_tests(candidate_id: str, packets: dict[str, dict[str, Any]]) -> dict[str, Any]:
    e4 = packets["E4"]
    test_results = (e4.get("visible_test_evidence") or {}).get("test_results", [])
    outcomes = [result.get("outcome") for result in test_results]
    if not outcomes:
        return _decision(candidate_id, "tool_only_visible_tests", "E4", "escalate", 0.5, "No visible test outcomes are available.", ["visible_test_evidence.missing"], ["insufficient_evidence"])
    if any(outcome in {"failed", "error", "timeout"} for outcome in outcomes):
        return _decision(candidate_id, "tool_only_visible_tests", "E4", "reject", 1.0, "At least one visible test outcome is failed, error, or timeout.", ["visible_test_evidence.test_results"], ["visible_test_failure"])
    if all(outcome == "passed" for outcome in outcomes):
        return _decision(candidate_id, "tool_only_visible_tests", "E4", "accept", 0.9, "All visible tests passed.", ["visible_test_evidence.test_results"], [])
    return _decision(candidate_id, "tool_only_visible_tests", "E4", "escalate", 0.5, "Visible test outcomes are incomplete or ambiguous.", ["visible_test_evidence.test_results"], ["insufficient_evidence"])


def _visible_tool_summary(candidate_id: str, packets: dict[str, dict[str, Any]]) -> dict[str, Any]:
    e6 = packets["E6"]
    summary = ((e6.get("visible_tool_evidence") or {}).get("summary") or {})
    test_counts = summary.get("visible_test_outcome_counts") or {}
    if any(int(test_counts.get(key, 0)) > 0 for key in ("failed", "error", "timeout")):
        return _decision(candidate_id, "tool_only_visible_tool_summary", "E6", "reject", 1.0, "Visible tool summary reports failed, error, or timeout test outcomes.", ["visible_tool_evidence.summary.visible_test_outcome_counts"], ["visible_test_failure"])
    if int(test_counts.get("passed", 0)) > 0:
        return _decision(candidate_id, "tool_only_visible_tool_summary", "E6", "accept", 0.9, "Visible tool summary reports passing visible tests and no visible failures.", ["visible_tool_evidence.summary.visible_test_outcome_counts"], [])
    return _decision(candidate_id, "tool_only_visible_tool_summary", "E6", "escalate", 0.5, "Visible tool summary is missing decisive test outcomes.", ["visible_tool_evidence.summary"], ["insufficient_evidence"])


def _decision(
    candidate_id: str,
    condition: str,
    evidence_level: str,
    decision: str,
    confidence: float,
    reason: str,
    evidence_used: list[str],
    risk_flags: list[str],
) -> dict[str, Any]:
    return {
        "decision_id": f"{candidate_id}__{condition}",
        "candidate_id": candidate_id,
        "verifier_id": condition,
        "condition": condition,
        "evidence_level": evidence_level,
        "decision": decision,
        "confidence": confidence,
        "primary_reason": reason,
        "evidence_used": evidence_used,
        "risk_flags": risk_flags,
        "suspected_failure_type": "unknown",
        "human_review_needed": decision == "escalate",
        "invalid_reason": None,
        "cost_usd": 0.0,
    }


def build_decisions(packets_path: Path) -> list[dict[str, Any]]:
    packets = _packets_by_candidate(packets_path)
    records: list[dict[str, Any]] = []
    for candidate_id, candidate_packets in sorted(packets.items()):
        records.extend(
            [
                _apply_only(candidate_id, candidate_packets),
                _visible_tests(candidate_id, candidate_packets),
                _visible_tool_summary(candidate_id, candidate_packets),
            ]
        )
    return records


def build_metrics(decisions: list[dict[str, Any]], labels: dict[str, str]) -> dict[str, Any]:
    by_condition = sorted({record["condition"] for record in decisions})
    groups = {condition: _metrics_for_condition(decisions, labels, condition) for condition in by_condition}
    return {
        "cohort_id": "EVP-7",
        "decision_count": len(decisions),
        "candidate_count": len(labels),
        "conditions": by_condition,
        "groups": groups,
        "g3_baseline_readiness": "passed" if all(group["record_count"] == len(labels) for group in groups.values()) else "not_passed",
        "label_join_boundary": "Decisions are generated from evidence packets only; evaluator labels are joined only for aggregate metrics.",
    }


def _metrics_for_condition(decisions: list[dict[str, Any]], labels: dict[str, str], condition: str) -> dict[str, Any]:
    selected = [record for record in decisions if record["condition"] == condition]
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
        label = labels[record["candidate_id"]]
        correct = label == "correct_under_f2p_and_p2p_broad"
        decision = record["decision"]
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
        "decision_counts": _counts(record["decision"] for record in selected),
        "confusion_counts": counts,
        "accepted_precision": _ratio(counts["true_accept"], accepted),
        "false_accept_rate": _ratio(counts["false_accept"], incorrect_total),
        "correct_recall": _ratio(counts["true_accept"], correct_total),
        "false_reject_rate": _ratio(counts["false_reject"], correct_total),
        "escalation_rate": _ratio(escalated, valid),
        "invalid_output_rate": _ratio(counts["invalid_output"], valid),
    }


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


def leakage_audit(decisions: list[dict[str, Any]]) -> list[str]:
    serialized = json.dumps(decisions, ensure_ascii=False)
    return [marker for marker in EVALUATOR_MARKERS if marker in serialized]


def _check(decisions: list[dict[str, Any]], metrics: dict[str, Any]) -> None:
    if len(decisions) != 174:
        raise SystemExit(f"expected 174 decisions, got {len(decisions)}")
    if metrics["g3_baseline_readiness"] != "passed":
        raise SystemExit("G3 baseline readiness did not pass")
    findings = leakage_audit(decisions)
    if findings:
        raise SystemExit(f"evaluator marker leaked into decisions: {findings}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packets-in", type=Path, default=PACKETS_IN)
    parser.add_argument("--candidates-in", type=Path, default=CANDIDATES_IN)
    parser.add_argument("--decisions-out", type=Path, default=DECISIONS_OUT)
    parser.add_argument("--metrics-out", type=Path, default=METRICS_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    decisions = build_decisions(args.packets_in)
    metrics = build_metrics(decisions, _candidate_labels(args.candidates_in))
    _write_jsonl(args.decisions_out, decisions)
    args.metrics_out.parent.mkdir(parents=True, exist_ok=True)
    args.metrics_out.write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check:
        _check(decisions, metrics)
    print(json.dumps(metrics, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
