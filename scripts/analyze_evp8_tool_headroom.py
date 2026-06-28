"""Analyze deterministic tool-only headroom for EVP-8.

This is a no-API audit. It joins the frozen EVP-8 candidate set with
deterministic tool-only decisions and evaluator-only labels, then reports
whether the current cohort has enough tool-baseline errors for an
LLM-added-value ablation.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATE_SET = REPO_ROOT / "data" / "protocols" / "evp8_candidate_set_v0_1.json"
DEFAULT_LABELS = REPO_ROOT / "data" / "patches" / "evp7_candidates.jsonl"
DEFAULT_TOOL_DECISIONS = REPO_ROOT / "data" / "baselines" / "evp7_tool_only_decisions.jsonl"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "protocols" / "evp8_tool_headroom_audit_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_tool_headroom_audit_v0_1.md"

TOOL_CONDITION = "tool_only_visible_tool_summary"
CORRECT_LABEL = "correct_under_f2p_and_p2p_broad"
ALLOWED_DECISIONS = {"accept", "reject", "escalate"}
EXPECTED_CANDIDATE_COUNT = 98


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{display_path(path)} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{display_path(path)}:{line_number} must contain a JSON object")
        records.append(value)
    return records


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def display_path(path: Path) -> str:
    absolute = path if path.is_absolute() else REPO_ROOT / path
    try:
        return absolute.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(absolute)


def pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.2f}%"


def proportion(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 6)


def count_values(values: Any) -> dict[str, int]:
    return dict(sorted(Counter(str(value) for value in values).items()))


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def candidate_map(candidate_set_path: Path) -> dict[str, dict[str, Any]]:
    candidate_set = read_json(candidate_set_path)
    records = candidate_set.get("records")
    if not isinstance(records, list):
        raise ValueError("candidate_set records must be a list")
    result = {}
    for record in records:
        evp8_id = str(record["evp8_candidate_id"])
        if evp8_id in result:
            raise ValueError(f"duplicate EVP-8 candidate id: {evp8_id}")
        result[evp8_id] = {
            "source_candidate_id": str(record["source_candidate_id"]),
            "project": record.get("project"),
            "task_id": record.get("task_id"),
        }
    return result


def label_map(labels_path: Path) -> dict[str, dict[str, Any]]:
    result = {}
    for record in read_jsonl(labels_path):
        candidate_id = str(record["evp7_candidate_id"])
        if candidate_id in result:
            raise ValueError(f"duplicate EVP-7 candidate id: {candidate_id}")
        result[candidate_id] = {
            "label_with_p2p_broad": record.get("label_with_p2p_broad"),
            "expected_outcome": record.get("expected_outcome"),
            "candidate_type": record.get("candidate_type"),
            "project": record.get("project"),
            "task_id": record.get("task_id"),
        }
    return result


def tool_decision_map(tool_decisions_path: Path) -> dict[str, dict[str, Any]]:
    result = {}
    for record in read_jsonl(tool_decisions_path):
        if record.get("condition") != TOOL_CONDITION:
            continue
        candidate_id = str(record["candidate_id"])
        if candidate_id in result:
            raise ValueError(f"duplicate tool decision for {candidate_id}::{TOOL_CONDITION}")
        decision = record.get("decision")
        if decision not in ALLOWED_DECISIONS:
            raise ValueError(f"unsupported tool decision for {candidate_id}: {decision!r}")
        result[candidate_id] = {
            "decision": decision,
            "confidence": record.get("confidence"),
            "primary_reason": record.get("primary_reason"),
            "risk_flags": record.get("risk_flags") or [],
            "human_review_needed": record.get("human_review_needed"),
        }
    return result


def joined_records(
    candidate_set_path: Path,
    labels_path: Path,
    tool_decisions_path: Path,
) -> list[dict[str, Any]]:
    candidates = candidate_map(candidate_set_path)
    labels = label_map(labels_path)
    decisions = tool_decision_map(tool_decisions_path)
    records = []
    missing_labels = []
    missing_decisions = []
    for evp8_id, candidate in sorted(candidates.items()):
        source_id = candidate["source_candidate_id"]
        label = labels.get(source_id)
        decision = decisions.get(source_id)
        if label is None:
            missing_labels.append(source_id)
            continue
        if decision is None:
            missing_decisions.append(source_id)
            continue
        records.append(
            {
                "evp8_candidate_id": evp8_id,
                "source_candidate_id": source_id,
                "project": candidate.get("project"),
                "task_id": candidate.get("task_id"),
                "decision": decision["decision"],
                "tool_confidence": decision.get("confidence"),
                "tool_primary_reason": decision.get("primary_reason"),
                "tool_risk_flags": decision.get("risk_flags") or [],
                "is_correct": label["label_with_p2p_broad"] == CORRECT_LABEL,
                "label_with_p2p_broad": label["label_with_p2p_broad"],
                "expected_outcome": label["expected_outcome"],
                "candidate_type": label["candidate_type"],
            }
        )
    if missing_labels or missing_decisions:
        raise ValueError(
            "join failed: "
            f"missing_labels={missing_labels}, missing_tool_decisions={missing_decisions}"
        )
    return records


def confusion_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    counts = {
        "true_accept": 0,
        "false_accept": 0,
        "true_reject": 0,
        "false_reject": 0,
        "escalated_correct": 0,
        "escalated_incorrect": 0,
    }
    for record in records:
        decision = record["decision"]
        is_correct = bool(record["is_correct"])
        if decision == "accept" and is_correct:
            counts["true_accept"] += 1
        elif decision == "accept":
            counts["false_accept"] += 1
        elif decision == "reject" and is_correct:
            counts["false_reject"] += 1
        elif decision == "reject":
            counts["true_reject"] += 1
        elif decision == "escalate" and is_correct:
            counts["escalated_correct"] += 1
        elif decision == "escalate":
            counts["escalated_incorrect"] += 1
    return counts


def metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    counts = confusion_counts(records)
    correct_total = counts["true_accept"] + counts["false_reject"] + counts["escalated_correct"]
    incorrect_total = counts["false_accept"] + counts["true_reject"] + counts["escalated_incorrect"]
    accepted_total = counts["true_accept"] + counts["false_accept"]
    rejected_total = counts["true_reject"] + counts["false_reject"]
    escalated_total = counts["escalated_correct"] + counts["escalated_incorrect"]
    opportunity_set_size = (
        counts["false_accept"]
        + counts["false_reject"]
        + counts["escalated_correct"]
        + counts["escalated_incorrect"]
    )
    return {
        "record_count": len(records),
        "correct_total": correct_total,
        "incorrect_total": incorrect_total,
        "decision_counts": count_values(record["decision"] for record in records),
        "correct_decision_counts": count_values(record["decision"] for record in records if record["is_correct"]),
        "incorrect_decision_counts": count_values(record["decision"] for record in records if not record["is_correct"]),
        "confusion_counts": counts,
        "accept_rate": proportion(accepted_total, len(records)),
        "reject_rate": proportion(rejected_total, len(records)),
        "escalation_rate": proportion(escalated_total, len(records)),
        "correct_recall": proportion(counts["true_accept"], correct_total),
        "accepted_precision": proportion(counts["true_accept"], accepted_total),
        "false_accept_rate": proportion(counts["false_accept"], incorrect_total),
        "false_reject_rate": proportion(counts["false_reject"], correct_total),
        "incorrect_reject_rate": proportion(counts["true_reject"], incorrect_total),
        "opportunity_set_size": opportunity_set_size,
        "opportunity_set_rate": proportion(opportunity_set_size, len(records)),
        "unsafe_error_count": counts["false_accept"] + counts["false_reject"],
    }


def breakdown(records: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record.get(key))].append(record)
    return {
        group: {
            "record_count": len(group_records),
            "decision_counts": count_values(record["decision"] for record in group_records),
            "confusion_counts": confusion_counts(group_records),
        }
        for group, group_records in sorted(grouped.items())
    }


def examples(records: list[dict[str, Any]], *, decision: str | None = None, correct: bool | None = None) -> list[dict[str, Any]]:
    selected = []
    for record in records:
        if decision is not None and record["decision"] != decision:
            continue
        if correct is not None and record["is_correct"] is not correct:
            continue
        selected.append(
            {
                "evp8_candidate_id": record["evp8_candidate_id"],
                "source_candidate_id": record["source_candidate_id"],
                "task_id": record["task_id"],
                "candidate_type": record["candidate_type"],
                "expected_outcome": record["expected_outcome"],
                "decision": record["decision"],
                "tool_primary_reason": record["tool_primary_reason"],
            }
        )
    return selected


def build_analysis(
    candidate_set_path: Path,
    labels_path: Path,
    tool_decisions_path: Path,
) -> dict[str, Any]:
    records = joined_records(candidate_set_path, labels_path, tool_decisions_path)
    metric_values = metrics(records)
    selected_source_ids = {record["source_candidate_id"] for record in records}
    checks = [
        check("candidate_count", len(records) == EXPECTED_CANDIDATE_COUNT, len(records)),
        check("source_candidate_ids_unique", len(selected_source_ids) == len(records), len(selected_source_ids)),
        check("all_decisions_supported", all(record["decision"] in ALLOWED_DECISIONS for record in records), True),
        check("api_call_not_attempted", True, False),
        check("raw_model_outputs_not_read", True, False),
        check("prompt_text_not_stored", True, False),
        check("opportunity_set_reported", isinstance(metric_values["opportunity_set_size"], int), metric_values["opportunity_set_size"]),
    ]
    analysis = {
        "analysis_id": "evp8_tool_headroom_audit_v0_1",
        "cohort_id": "EVP-8",
        "tool_condition": TOOL_CONDITION,
        "inputs": {
            "candidate_set": display_path(candidate_set_path),
            "evaluator_only_labels": display_path(labels_path),
            "tool_only_decisions": display_path(tool_decisions_path),
        },
        "method": {
            "correct_label": CORRECT_LABEL,
            "incorrect_definition": "any selected candidate whose label_with_p2p_broad is not the correct label",
            "api_call_attempted": False,
            "raw_model_outputs_read": False,
            "prompt_text_stored": False,
            "opportunity_set_definition": (
                "tool false accepts + tool false rejects + tool escalations on correct "
                "and incorrect candidates"
            ),
        },
        "label_distribution": {
            "selected_candidate_count": len(records),
            "correct_count": sum(1 for record in records if record["is_correct"]),
            "incorrect_count": sum(1 for record in records if not record["is_correct"]),
            "label_with_p2p_broad": count_values(record["label_with_p2p_broad"] for record in records),
            "expected_outcome": count_values(record["expected_outcome"] for record in records),
            "candidate_type": count_values(record["candidate_type"] for record in records),
        },
        "rule_only_metrics": metric_values,
        "breakdowns": {
            "expected_outcome": breakdown(records, "expected_outcome"),
            "candidate_type": breakdown(records, "candidate_type"),
        },
        "opportunity_examples": {
            "tool_false_accepts": examples(records, decision="accept", correct=False),
            "tool_false_rejects": examples(records, decision="reject", correct=True),
            "tool_escalations_correct": examples(records, decision="escalate", correct=True),
            "tool_escalations_incorrect": examples(records, decision="escalate", correct=False),
        },
        "headroom_decision": {
            "status": "sufficient_for_ablation" if metric_values["opportunity_set_size"] > 0 else "too_tool_solved",
            "reason": (
                "The deterministic tool baseline has at least one false accept, false reject, "
                "or escalation opportunity."
                if metric_values["opportunity_set_size"] > 0
                else "The deterministic tool baseline leaves no observed correction opportunity."
            ),
        },
        "checks": checks,
    }
    if not all(item["passed"] for item in checks):
        raise SystemExit(f"headroom audit checks failed: {checks}")
    return analysis


def write_markdown(path: Path, analysis: dict[str, Any]) -> None:
    metrics_value = analysis["rule_only_metrics"]
    counts = metrics_value["confusion_counts"]
    lines = [
        "# EVP-8 Tool-Only Headroom Audit v0.1",
        "",
        "- Status: `passed`",
        f"- Tool condition: `{analysis['tool_condition']}`",
        f"- Candidate count: `{analysis['label_distribution']['selected_candidate_count']}`",
        f"- Correct / incorrect: `{analysis['label_distribution']['correct_count']}` / `{analysis['label_distribution']['incorrect_count']}`",
        f"- Headroom decision: `{analysis['headroom_decision']['status']}`",
        f"- API call attempted: `{str(analysis['method']['api_call_attempted']).lower()}`",
        f"- Raw model outputs read: `{str(analysis['method']['raw_model_outputs_read']).lower()}`",
        "",
        "## Rule-Only Metrics",
        "",
        "| metric | value |",
        "| --- | ---: |",
        f"| accept count | {metrics_value['decision_counts'].get('accept', 0)} |",
        f"| reject count | {metrics_value['decision_counts'].get('reject', 0)} |",
        f"| escalate count | {metrics_value['decision_counts'].get('escalate', 0)} |",
        f"| true accepts | {counts['true_accept']} |",
        f"| false accepts | {counts['false_accept']} |",
        f"| false rejects | {counts['false_reject']} |",
        f"| escalated correct | {counts['escalated_correct']} |",
        f"| escalated incorrect | {counts['escalated_incorrect']} |",
        f"| accepted precision | {pct(metrics_value['accepted_precision'])} |",
        f"| correct recall | {pct(metrics_value['correct_recall'])} |",
        f"| false accept rate | {pct(metrics_value['false_accept_rate'])} |",
        f"| false reject rate | {pct(metrics_value['false_reject_rate'])} |",
        f"| opportunity-set size | {metrics_value['opportunity_set_size']} |",
        "",
        "## False Accepts",
        "",
        "| candidate | task | type | expected outcome |",
        "| --- | --- | --- | --- |",
    ]
    false_accepts = analysis["opportunity_examples"]["tool_false_accepts"]
    if false_accepts:
        for record in false_accepts:
            lines.append(
                f"| `{record['evp8_candidate_id']}` | `{record['task_id']}` | "
                f"`{record['candidate_type']}` | `{record['expected_outcome']}` |"
            )
    else:
        lines.append("| n/a | n/a | n/a | n/a |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- {analysis['headroom_decision']['reason']}",
            "- This audit does not prove LLM added value; it only shows whether there are tool-baseline mistakes for the ablation to test.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-set", type=Path, default=DEFAULT_CANDIDATE_SET)
    parser.add_argument("--labels", type=Path, default=DEFAULT_LABELS)
    parser.add_argument("--tool-decisions", type=Path, default=DEFAULT_TOOL_DECISIONS)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    analysis = build_analysis(args.candidate_set, args.labels, args.tool_decisions)
    write_json(args.json_out, analysis)
    write_markdown(args.md_out, analysis)
    if args.check and not all(item["passed"] for item in analysis["checks"]):
        return 1
    print(json.dumps(analysis, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
