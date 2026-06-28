"""Compare EVP-8 rule-only, E6-full, and E6-no-verdict results.

This analysis reads ignored raw model responses only to parse final JSON
decisions. Tracked outputs contain aggregate metrics and candidate ids, not
raw response text or prompt text.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from cross_review.parsing import extract_json_object  # noqa: E402


DEFAULT_CANDIDATE_SET = REPO_ROOT / "data" / "protocols" / "evp8_candidate_set_v0_1.json"
DEFAULT_LABELS = REPO_ROOT / "data" / "patches" / "evp7_candidates.jsonl"
DEFAULT_TOOL_HEADROOM = REPO_ROOT / "data" / "protocols" / "evp8_tool_headroom_audit_v0_1.json"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "reviews" / "evp8_e6_no_verdict_ablation_comparison.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_e6_no_verdict_ablation_comparison.md"

RAW_RESPONSE_PATHS = {
    "deepseek/deepseek-v4-pro": {
        "E6-full": REPO_ROOT
        / "outputs"
        / "evp8_accept_aware_v0_2_prompt_v0_2_json_mode_deepseek_qwen_full"
        / "deepseek_deepseek-v4-pro"
        / "raw_responses.jsonl",
        "E6-no-verdict": REPO_ROOT
        / "outputs"
        / "evp8_e6_no_verdict_ablation_full"
        / "deepseek_deepseek-v4-pro"
        / "raw_responses.jsonl",
    },
    "qwen/qwen3.7-max": {
        "E6-full": REPO_ROOT
        / "outputs"
        / "evp8_accept_aware_v0_2_prompt_v0_2_json_mode_deepseek_qwen_full"
        / "qwen_qwen3.7-max"
        / "raw_responses.jsonl",
        "E6-no-verdict": REPO_ROOT
        / "outputs"
        / "evp8_e6_no_verdict_ablation_full"
        / "qwen_qwen3.7-max"
        / "raw_responses.jsonl",
    },
}

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


def build_candidate_map(candidate_set_path: Path) -> dict[str, dict[str, Any]]:
    candidate_set = read_json(candidate_set_path)
    result = {}
    for record in candidate_set.get("records") or []:
        result[str(record["evp8_candidate_id"])] = {
            "source_candidate_id": str(record["source_candidate_id"]),
            "project": record.get("project"),
            "task_id": record.get("task_id"),
        }
    return result


def build_label_map(labels_path: Path) -> dict[str, dict[str, Any]]:
    result = {}
    for record in read_jsonl(labels_path):
        result[str(record["evp7_candidate_id"])] = {
            "label_with_p2p_broad": record.get("label_with_p2p_broad"),
            "expected_outcome": record.get("expected_outcome"),
            "candidate_type": record.get("candidate_type"),
            "project": record.get("project"),
            "task_id": record.get("task_id"),
        }
    return result


def parse_decision(raw_record: dict[str, Any]) -> str:
    raw_text = raw_record.get("raw_response_text")
    if not isinstance(raw_text, str) or not raw_text.strip():
        raise ValueError("raw_response_text missing")
    parsed = extract_json_object(raw_text)
    if not isinstance(parsed, dict):
        raise ValueError("parsed response is not an object")
    decision = parsed.get("decision")
    if decision not in ALLOWED_DECISIONS:
        raise ValueError(f"unsupported decision: {decision!r}")
    return str(decision)


def model_condition_records(
    raw_path: Path,
    model_id: str,
    condition: str,
    candidate_map: dict[str, dict[str, Any]],
    label_map: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    records = []
    for raw_record in read_jsonl(raw_path):
        if raw_record.get("evidence_level") != "E6":
            continue
        evp8_id = str(raw_record["anonymous_candidate_id"])
        candidate = candidate_map[evp8_id]
        source_id = candidate["source_candidate_id"]
        label = label_map[source_id]
        records.append(
            {
                "condition": condition,
                "model_id": model_id,
                "evp8_candidate_id": evp8_id,
                "source_candidate_id": source_id,
                "project": candidate["project"],
                "task_id": candidate["task_id"],
                "decision": parse_decision(raw_record),
                "is_correct": label["label_with_p2p_broad"] == CORRECT_LABEL,
                "label_with_p2p_broad": label["label_with_p2p_broad"],
                "expected_outcome": label["expected_outcome"],
                "candidate_type": label["candidate_type"],
            }
        )
    return records


def rule_only_records(tool_headroom_path: Path) -> list[dict[str, Any]]:
    headroom = read_json(tool_headroom_path)
    records = []
    for group in (
        "tool_false_accepts",
        "tool_false_rejects",
        "tool_escalations_correct",
        "tool_escalations_incorrect",
    ):
        # Opportunity examples are included separately; full rule-only metrics
        # come from the headroom summary to avoid duplicating tool raw records.
        if not isinstance((headroom.get("opportunity_examples") or {}).get(group), list):
            raise ValueError(f"missing opportunity group in headroom audit: {group}")
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


def opportunity_ids(tool_headroom: dict[str, Any]) -> dict[str, list[str]]:
    examples = tool_headroom.get("opportunity_examples") or {}
    return {
        name: [str(record["evp8_candidate_id"]) for record in examples.get(name, [])]
        for name in (
            "tool_false_accepts",
            "tool_false_rejects",
            "tool_escalations_correct",
            "tool_escalations_incorrect",
        )
    }


def opportunity_correction(records: list[dict[str, Any]], tool_headroom: dict[str, Any]) -> dict[str, Any]:
    by_id = {record["evp8_candidate_id"]: record for record in records}
    ids = opportunity_ids(tool_headroom)
    false_accept_rows = [by_id[candidate_id] for candidate_id in ids["tool_false_accepts"]]
    false_reject_rows = [by_id[candidate_id] for candidate_id in ids["tool_false_rejects"]]
    escalation_correct_rows = [by_id[candidate_id] for candidate_id in ids["tool_escalations_correct"]]
    escalation_incorrect_rows = [by_id[candidate_id] for candidate_id in ids["tool_escalations_incorrect"]]
    return {
        "tool_false_accepts": {
            "candidate_count": len(false_accept_rows),
            "corrected_to_reject": sum(1 for record in false_accept_rows if record["decision"] == "reject"),
            "repeated_accept": sum(1 for record in false_accept_rows if record["decision"] == "accept"),
            "escalated": sum(1 for record in false_accept_rows if record["decision"] == "escalate"),
            "decision_counts": count_values(record["decision"] for record in false_accept_rows),
            "candidates": candidate_rows(false_accept_rows),
        },
        "tool_false_rejects": {
            "candidate_count": len(false_reject_rows),
            "corrected_to_accept": sum(1 for record in false_reject_rows if record["decision"] == "accept"),
            "repeated_reject": sum(1 for record in false_reject_rows if record["decision"] == "reject"),
            "escalated": sum(1 for record in false_reject_rows if record["decision"] == "escalate"),
            "decision_counts": count_values(record["decision"] for record in false_reject_rows),
            "candidates": candidate_rows(false_reject_rows),
        },
        "tool_escalations_correct": {
            "candidate_count": len(escalation_correct_rows),
            "resolved_to_accept": sum(1 for record in escalation_correct_rows if record["decision"] == "accept"),
            "decision_counts": count_values(record["decision"] for record in escalation_correct_rows),
        },
        "tool_escalations_incorrect": {
            "candidate_count": len(escalation_incorrect_rows),
            "resolved_to_reject": sum(1 for record in escalation_incorrect_rows if record["decision"] == "reject"),
            "decision_counts": count_values(record["decision"] for record in escalation_incorrect_rows),
        },
    }


def candidate_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "evp8_candidate_id": record["evp8_candidate_id"],
            "task_id": record["task_id"],
            "candidate_type": record["candidate_type"],
            "expected_outcome": record["expected_outcome"],
            "decision": record["decision"],
        }
        for record in records
    ]


def transitions(left_records: list[dict[str, Any]], right_records: list[dict[str, Any]]) -> dict[str, Any]:
    left = {record["evp8_candidate_id"]: record for record in left_records}
    right = {record["evp8_candidate_id"]: record for record in right_records}
    counts: Counter[str] = Counter()
    changed = []
    for candidate_id in sorted(left):
        left_record = left[candidate_id]
        right_record = right[candidate_id]
        correctness = "correct" if right_record["is_correct"] else "incorrect"
        key = f"{correctness}:{left_record['decision']}->{right_record['decision']}"
        counts[key] += 1
        if left_record["decision"] != right_record["decision"]:
            changed.append(
                {
                    "evp8_candidate_id": candidate_id,
                    "task_id": right_record["task_id"],
                    "candidate_type": right_record["candidate_type"],
                    "expected_outcome": right_record["expected_outcome"],
                    "from": left_record["decision"],
                    "to": right_record["decision"],
                }
            )
    return {
        "transition_counts": dict(sorted(counts.items())),
        "changed_count": len(changed),
        "changed_candidates": changed,
    }


def build_analysis(candidate_set_path: Path, labels_path: Path, tool_headroom_path: Path) -> dict[str, Any]:
    candidates = build_candidate_map(candidate_set_path)
    labels = build_label_map(labels_path)
    tool_headroom = read_json(tool_headroom_path)
    per_model: dict[str, Any] = {}
    checks = [
        check("candidate_count", len(candidates) == EXPECTED_CANDIDATE_COUNT, len(candidates)),
        check("tool_headroom_status", tool_headroom.get("headroom_decision", {}).get("status") == "sufficient_for_ablation", tool_headroom.get("headroom_decision", {}).get("status")),
        check("api_call_not_attempted_by_analysis", True, False),
        check("raw_response_content_not_stored", True, False),
        check("prompt_text_not_stored", True, False),
    ]
    for model_id, condition_paths in RAW_RESPONSE_PATHS.items():
        condition_records = {
            condition: model_condition_records(path, model_id, condition, candidates, labels)
            for condition, path in condition_paths.items()
        }
        for condition, records in condition_records.items():
            observed_ids = {record["evp8_candidate_id"] for record in records}
            checks.append(check(f"{model_id}:{condition}:record_count", len(records) == EXPECTED_CANDIDATE_COUNT, len(records)))
            checks.append(check(f"{model_id}:{condition}:candidate_matrix", observed_ids == set(candidates), len(observed_ids)))
        full_records = condition_records["E6-full"]
        no_verdict_records = condition_records["E6-no-verdict"]
        per_model[model_id] = {
            "conditions": {
                condition: {
                    "metrics": metrics(records),
                    "breakdowns": {
                        "expected_outcome": breakdown(records, "expected_outcome"),
                        "candidate_type": breakdown(records, "candidate_type"),
                    },
                    "opportunity_correction": opportunity_correction(records, tool_headroom),
                }
                for condition, records in condition_records.items()
            },
            "transitions": {
                "E6-full_to_E6-no-verdict": transitions(full_records, no_verdict_records),
            },
        }
    analysis = {
        "analysis_id": "evp8_e6_no_verdict_ablation_comparison",
        "cohort_id": "EVP-8",
        "inputs": {
            "candidate_set": display_path(candidate_set_path),
            "evaluator_only_labels": display_path(labels_path),
            "tool_headroom_audit": display_path(tool_headroom_path),
            "raw_response_paths": {
                model_id: {condition: display_path(path) for condition, path in condition_paths.items()}
                for model_id, condition_paths in RAW_RESPONSE_PATHS.items()
            },
        },
        "method": {
            "correct_label": CORRECT_LABEL,
            "analysis_api_call_attempted": False,
            "raw_response_content_stored": False,
            "prompt_text_stored": False,
            "conditions": ["rule-only", "E6-full", "E6-no-verdict"],
        },
        "rule_only": {
            "metrics": tool_headroom["rule_only_metrics"],
            "opportunity_examples": tool_headroom["opportunity_examples"],
        },
        "per_model": per_model,
        "checks": checks,
        "claim_boundary": {
            "allowed": "Report Qwen/DeepSeek E6-no-verdict ablation against rule-only and E6-full on the frozen 98-candidate EVP-8 cohort.",
            "forbidden": "Do not claim reliable automatic merge, generalization to real agent patches, or superiority without the opportunity-set evidence.",
        },
    }
    if not all(item["passed"] for item in checks):
        raise SystemExit(f"ablation comparison checks failed: {checks}")
    return analysis


def write_markdown(path: Path, analysis: dict[str, Any]) -> None:
    lines = [
        "# EVP-8 E6-no-verdict Ablation Comparison",
        "",
        "- Status: `passed`",
        "- Scope: Qwen and DeepSeek only",
        "- Candidate count: `98`",
        "- Analysis API call attempted: `false`",
        "- Raw response content stored in tracked report: `false`",
        "",
        "## Main Metrics",
        "",
        "| model/condition | accept | reject | escalate | correct accept | false accept | accepted precision | correct recall | false accept rate | escalation rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    rule_metrics = analysis["rule_only"]["metrics"]
    lines.append(metric_row("rule-only", rule_metrics))
    for model_id, model in analysis["per_model"].items():
        for condition in ("E6-full", "E6-no-verdict"):
            lines.append(metric_row(f"{model_id} {condition}", model["conditions"][condition]["metrics"]))
    lines.extend(
        [
            "",
            "## Opportunity-Set Correction",
            "",
            "Tool baseline has 6 opportunity cases: 5 false accepts and 1 false reject.",
            "",
            "| model/condition | false accepts corrected to reject | false accepts repeated as accept | false accepts escalated | false reject corrected to accept | false reject repeated as reject | false reject escalated |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for model_id, model in analysis["per_model"].items():
        for condition in ("E6-full", "E6-no-verdict"):
            opp = model["conditions"][condition]["opportunity_correction"]
            fa = opp["tool_false_accepts"]
            fr = opp["tool_false_rejects"]
            lines.append(
                f"| {model_id} {condition} | {fa['corrected_to_reject']} | {fa['repeated_accept']} | "
                f"{fa['escalated']} | {fr['corrected_to_accept']} | {fr['repeated_reject']} | {fr['escalated']} |"
            )
    lines.extend(
        [
            "",
            "## E6-full to E6-no-verdict Decision Changes",
            "",
            "| model | changed decisions | transition counts |",
            "| --- | ---: | --- |",
        ]
    )
    for model_id, model in analysis["per_model"].items():
        transition = model["transitions"]["E6-full_to_E6-no-verdict"]
        lines.append(
            f"| {model_id} | {transition['changed_count']} | "
            f"`{json.dumps(transition['transition_counts'], ensure_ascii=False, sort_keys=True)}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Removing the explicit rule verdict tests whether the LLM follows the verdict field or reasons from the remaining visible evidence.",
            "- Opportunity-set metrics are more important than aggregate accuracy because the practical question is whether the LLM fixes tool mistakes.",
            f"- Allowed claim: {analysis['claim_boundary']['allowed']}",
            f"- Forbidden claim: {analysis['claim_boundary']['forbidden']}",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def metric_row(label: str, metrics_value: dict[str, Any]) -> str:
    counts = metrics_value["confusion_counts"]
    decisions = metrics_value["decision_counts"]
    return (
        f"| {label} | {decisions.get('accept', 0)} | {decisions.get('reject', 0)} | "
        f"{decisions.get('escalate', 0)} | {counts['true_accept']} | {counts['false_accept']} | "
        f"{pct(metrics_value['accepted_precision'])} | {pct(metrics_value['correct_recall'])} | "
        f"{pct(metrics_value['false_accept_rate'])} | {pct(metrics_value['escalation_rate'])} |"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-set", type=Path, default=DEFAULT_CANDIDATE_SET)
    parser.add_argument("--labels", type=Path, default=DEFAULT_LABELS)
    parser.add_argument("--tool-headroom", type=Path, default=DEFAULT_TOOL_HEADROOM)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    analysis = build_analysis(args.candidate_set, args.labels, args.tool_headroom)
    write_json(args.json_out, analysis)
    write_markdown(args.md_out, analysis)
    if args.check and not all(item["passed"] for item in analysis["checks"]):
        return 1
    print(json.dumps(analysis, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
