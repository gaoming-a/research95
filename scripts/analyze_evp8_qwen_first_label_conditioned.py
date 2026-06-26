"""Build label-conditioned EVP-8 v0.3 Qwen-first statistics.

This script reads ignored raw model output only to parse the final JSON
decision in ``raw_response_text``. It joins those decisions with evaluator-only
labels locally and writes aggregate, raw-output-free summaries.
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
DEFAULT_RAW_RESPONSES = (
    REPO_ROOT
    / "outputs"
    / "evp8_main_v0_3_qwen_first_prompt_v0_2_json_mode_full"
    / "qwen_qwen3.7-max"
    / "raw_responses.jsonl"
)
DEFAULT_JSON_OUT = (
    REPO_ROOT
    / "data"
    / "reviews"
    / "evp8_qwen_first_main_v0_3_prompt_v0_2_label_conditioned_summary.json"
)
DEFAULT_MD_OUT = (
    REPO_ROOT
    / "docs"
    / "experiments"
    / "evp8_qwen_first_main_v0_3_prompt_v0_2_label_conditioned_summary.md"
)

EXPECTED_LEVELS = ("E0", "E1", "E2", "E3", "E4", "E5", "E6")
EXPECTED_CANDIDATE_COUNT = 98
CORRECT_LABEL = "correct_under_f2p_and_p2p_broad"
ALLOWED_DECISIONS = {"accept", "reject", "escalate"}


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


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def build_candidate_map(candidate_set_path: Path) -> dict[str, dict[str, Any]]:
    candidate_set = read_json(candidate_set_path)
    records = candidate_set.get("records")
    if not isinstance(records, list):
        raise ValueError("candidate set records must be a list")
    candidate_map: dict[str, dict[str, Any]] = {}
    for record in records:
        evp8_candidate_id = record["evp8_candidate_id"]
        if evp8_candidate_id in candidate_map:
            raise ValueError(f"duplicate evp8 candidate id: {evp8_candidate_id}")
        candidate_map[evp8_candidate_id] = {
            "source_candidate_id": record["source_candidate_id"],
            "project": record.get("project"),
            "task_id": record.get("task_id"),
        }
    return candidate_map


def build_label_map(labels_path: Path) -> dict[str, dict[str, Any]]:
    label_map: dict[str, dict[str, Any]] = {}
    for record in read_jsonl(labels_path):
        candidate_id = record["evp7_candidate_id"]
        if candidate_id in label_map:
            raise ValueError(f"duplicate evp7 candidate id: {candidate_id}")
        label_map[candidate_id] = {
            "label_with_p2p_broad": record.get("label_with_p2p_broad"),
            "expected_outcome": record.get("expected_outcome"),
            "candidate_type": record.get("candidate_type"),
            "project": record.get("project"),
            "task_id": record.get("task_id"),
        }
    return label_map


def parse_decision(record: dict[str, Any]) -> str:
    raw_response_text = record.get("raw_response_text")
    if not isinstance(raw_response_text, str) or not raw_response_text.strip():
        raise ValueError("raw_response_text is missing or empty")
    parsed = json.loads(raw_response_text)
    if not isinstance(parsed, dict):
        raise ValueError("raw_response_text must parse to a JSON object")
    decision = parsed.get("decision")
    if decision not in ALLOWED_DECISIONS:
        raise ValueError(f"unsupported decision: {decision!r}")
    return str(decision)


def normalized_reviews(
    raw_responses_path: Path,
    candidate_map: dict[str, dict[str, Any]],
    label_map: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    records = []
    for raw_record in read_jsonl(raw_responses_path):
        evp8_candidate_id = raw_record["anonymous_candidate_id"]
        evidence_level = raw_record["evidence_level"]
        if evp8_candidate_id not in candidate_map:
            raise ValueError(f"raw response references unknown candidate: {evp8_candidate_id}")
        if evidence_level not in EXPECTED_LEVELS:
            raise ValueError(f"unexpected evidence level: {evidence_level}")
        candidate = candidate_map[evp8_candidate_id]
        source_candidate_id = candidate["source_candidate_id"]
        if source_candidate_id not in label_map:
            raise ValueError(f"missing evaluator label for {source_candidate_id}")
        label = label_map[source_candidate_id]
        records.append(
            {
                "evp8_candidate_id": evp8_candidate_id,
                "source_candidate_id": source_candidate_id,
                "evidence_level": evidence_level,
                "decision": parse_decision(raw_record),
                "is_correct": label["label_with_p2p_broad"] == CORRECT_LABEL,
                "label_with_p2p_broad": label["label_with_p2p_broad"],
                "expected_outcome": label["expected_outcome"],
                "candidate_type": label["candidate_type"],
                "project": label["project"],
                "task_id": label["task_id"],
            }
        )
    return records


def validate_matrix(records: list[dict[str, Any]], candidate_ids: set[str]) -> list[dict[str, Any]]:
    observed = {(record["evp8_candidate_id"], record["evidence_level"]) for record in records}
    expected = {(candidate_id, level) for candidate_id in candidate_ids for level in EXPECTED_LEVELS}
    duplicate_count = len(records) - len(observed)
    return [
        check("candidate_count", len(candidate_ids) == EXPECTED_CANDIDATE_COUNT, len(candidate_ids)),
        check("raw_review_count", len(records) == EXPECTED_CANDIDATE_COUNT * len(EXPECTED_LEVELS), len(records)),
        check("review_matrix_has_no_duplicates", duplicate_count == 0, duplicate_count),
        check("review_matrix_missing_cells", len(expected - observed) == 0, len(expected - observed)),
        check("review_matrix_extra_cells", len(observed - expected) == 0, len(observed - expected)),
    ]


def count_values(values: Any) -> dict[str, int]:
    return dict(sorted(Counter(str(value) for value in values).items()))


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


def metrics_for_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    counts = confusion_counts(records)
    correct_total = counts["true_accept"] + counts["false_reject"] + counts["escalated_correct"]
    incorrect_total = counts["false_accept"] + counts["true_reject"] + counts["escalated_incorrect"]
    accepted_total = counts["true_accept"] + counts["false_accept"]
    escalated_total = counts["escalated_correct"] + counts["escalated_incorrect"]
    rejected_total = counts["true_reject"] + counts["false_reject"]
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
        "correct_escalation_rate": proportion(counts["escalated_correct"], correct_total),
        "incorrect_reject_rate": proportion(counts["true_reject"], incorrect_total),
    }


def label_breakdowns(records: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record.get(key))].append(record)
    return {
        group: {
            "record_count": len(group_records),
            "decision_counts": count_values(record["decision"] for record in group_records),
        }
        for group, group_records in sorted(grouped.items())
    }


def paired_transitions(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_candidate_level = {
        (record["evp8_candidate_id"], record["evidence_level"]): record
        for record in records
    }
    candidate_ids = sorted({record["evp8_candidate_id"] for record in records})
    result: dict[str, Any] = {"vs_e0": {}, "adjacent": {}}
    for target in EXPECTED_LEVELS[1:]:
        result["vs_e0"][f"E0->{target}"] = transition_summary(candidate_ids, by_candidate_level, "E0", target)
    for left, right in zip(EXPECTED_LEVELS, EXPECTED_LEVELS[1:]):
        result["adjacent"][f"{left}->{right}"] = transition_summary(candidate_ids, by_candidate_level, left, right)
    return result


def transition_summary(
    candidate_ids: list[str],
    by_candidate_level: dict[tuple[str, str], dict[str, Any]],
    source_level: str,
    target_level: str,
) -> dict[str, Any]:
    transitions: Counter[str] = Counter()
    accept_gains = {
        "correct_nonaccept_to_accept": 0,
        "incorrect_nonaccept_to_accept": 0,
        "correct_accept_to_nonaccept": 0,
        "incorrect_accept_to_nonaccept": 0,
    }
    for candidate_id in candidate_ids:
        source = by_candidate_level[(candidate_id, source_level)]
        target = by_candidate_level[(candidate_id, target_level)]
        correctness = "correct" if target["is_correct"] else "incorrect"
        transitions[f"{correctness}:{source['decision']}->{target['decision']}"] += 1
        source_accept = source["decision"] == "accept"
        target_accept = target["decision"] == "accept"
        if not source_accept and target_accept and target["is_correct"]:
            accept_gains["correct_nonaccept_to_accept"] += 1
        elif not source_accept and target_accept:
            accept_gains["incorrect_nonaccept_to_accept"] += 1
        elif source_accept and not target_accept and target["is_correct"]:
            accept_gains["correct_accept_to_nonaccept"] += 1
        elif source_accept and not target_accept:
            accept_gains["incorrect_accept_to_nonaccept"] += 1
    return {
        "transition_counts": dict(sorted(transitions.items())),
        "accept_transition_counts": accept_gains,
    }


def build_summary(
    candidate_set_path: Path,
    labels_path: Path,
    raw_responses_path: Path,
) -> dict[str, Any]:
    candidate_map = build_candidate_map(candidate_set_path)
    label_map = build_label_map(labels_path)
    selected_source_ids = {record["source_candidate_id"] for record in candidate_map.values()}
    selected_labels = [label_map[source_id] for source_id in selected_source_ids]
    records = normalized_reviews(raw_responses_path, candidate_map, label_map)
    validation_checks = validate_matrix(records, set(candidate_map))
    per_level = {
        level: metrics_for_records([record for record in records if record["evidence_level"] == level])
        for level in EXPECTED_LEVELS
    }
    level_deltas = {}
    baseline_recall = per_level["E0"]["correct_recall"] or 0.0
    baseline_far = per_level["E0"]["false_accept_rate"] or 0.0
    for level in EXPECTED_LEVELS:
        recall = per_level[level]["correct_recall"] or 0.0
        far = per_level[level]["false_accept_rate"] or 0.0
        level_deltas[level] = {
            "correct_recall_delta_vs_e0": round(recall - baseline_recall, 6),
            "false_accept_rate_delta_vs_e0": round(far - baseline_far, 6),
        }
    analysis = {
        "analysis_id": "evp8_qwen_first_main_v0_3_prompt_v0_2_label_conditioned_summary",
        "cohort_id": "EVP-8",
        "protocol_id": "evp8_accept_aware_qwen_first_main_v0_3",
        "model_id": "qwen/qwen3.7-max",
        "request_model_id": "qwen3.7-max",
        "provider_route": "qwen_official",
        "inputs": {
            "candidate_set": display_path(candidate_set_path),
            "evaluator_only_labels": display_path(labels_path),
            "qwen_full_raw_responses": display_path(raw_responses_path),
        },
        "method": {
            "correct_label": CORRECT_LABEL,
            "incorrect_definition": "any selected candidate whose label_with_p2p_broad is not the correct label",
            "decision_parse_source": "raw_response_text final JSON content only",
            "reasoning_content_used": False,
            "api_call_attempted": False,
            "raw_response_content_stored": False,
            "prompt_text_stored": False,
        },
        "label_distribution": {
            "selected_candidate_count": len(selected_source_ids),
            "correct_count": sum(1 for label in selected_labels if label["label_with_p2p_broad"] == CORRECT_LABEL),
            "incorrect_count": sum(1 for label in selected_labels if label["label_with_p2p_broad"] != CORRECT_LABEL),
            "label_with_p2p_broad": count_values(label["label_with_p2p_broad"] for label in selected_labels),
            "expected_outcome": count_values(label["expected_outcome"] for label in selected_labels),
            "candidate_type": count_values(label["candidate_type"] for label in selected_labels),
        },
        "per_evidence_level": per_level,
        "level_deltas_vs_e0": level_deltas,
        "paired_transitions": paired_transitions(records),
        "breakdowns_by_evidence_level": {
            level: {
                "expected_outcome": label_breakdowns(
                    [record for record in records if record["evidence_level"] == level],
                    "expected_outcome",
                ),
                "candidate_type": label_breakdowns(
                    [record for record in records if record["evidence_level"] == level],
                    "candidate_type",
                ),
            }
            for level in EXPECTED_LEVELS
        },
        "checks": validation_checks
        + [
            check("all_decisions_supported", all(record["decision"] in ALLOWED_DECISIONS for record in records), True),
            check("raw_response_content_not_stored", True, False),
            check("prompt_text_not_stored", True, False),
            check("api_call_not_attempted", True, False),
        ],
        "claim_boundary": {
            "allowed": (
                "Report label-conditioned Qwen v0.3 descriptive metrics for the frozen "
                "98-candidate E0-E6 packet set."
            ),
            "forbidden": (
                "Do not claim five-model effectiveness, DeepSeek/Qwen comparison, LLM "
                "superiority, or final evidence-level ranking from this Qwen-only analysis."
            ),
        },
    }
    if not all(item["passed"] for item in analysis["checks"]):
        raise SystemExit(f"label-conditioned analysis checks failed: {analysis['checks']}")
    return analysis


def write_markdown(path: Path, analysis: dict[str, Any]) -> None:
    lines = [
        f"# {analysis['analysis_id']}",
        "",
        f"- Status: `passed`",
        f"- Model: `{analysis['model_id']}`",
        f"- Protocol: `{analysis['protocol_id']}`",
        f"- Candidate count: `{analysis['label_distribution']['selected_candidate_count']}`",
        f"- Correct / incorrect: `{analysis['label_distribution']['correct_count']}` / `{analysis['label_distribution']['incorrect_count']}`",
        f"- API call attempted by analysis: `false`",
        f"- Raw response content stored: `false`",
        f"- Prompt text stored: `false`",
        f"- Reasoning content used: `false`",
        "",
        "## Per-Level Label-Conditioned Metrics",
        "",
        "| level | accept | correct accept | false accept | accepted precision | correct recall | false accept rate | false reject rate | escalation rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for level in EXPECTED_LEVELS:
        metrics = analysis["per_evidence_level"][level]
        confusion = metrics["confusion_counts"]
        accept_count = metrics["decision_counts"].get("accept", 0)
        lines.append(
            "| {level} | {accept} | {true_accept} | {false_accept} | {precision} | {recall} | {far} | {frr} | {escalation} |".format(
                level=level,
                accept=accept_count,
                true_accept=confusion["true_accept"],
                false_accept=confusion["false_accept"],
                precision=pct(metrics["accepted_precision"]),
                recall=pct(metrics["correct_recall"]),
                far=pct(metrics["false_accept_rate"]),
                frr=pct(metrics["false_reject_rate"]),
                escalation=pct(metrics["escalation_rate"]),
            )
        )
    lines.extend(
        [
            "",
            "## Correct vs Incorrect Decision Counts",
            "",
            "| level | correct decisions | incorrect decisions |",
            "| --- | --- | --- |",
        ]
    )
    for level in EXPECTED_LEVELS:
        metrics = analysis["per_evidence_level"][level]
        lines.append(
            f"| {level} | `{json.dumps(metrics['correct_decision_counts'], ensure_ascii=False, sort_keys=True)}` | "
            f"`{json.dumps(metrics['incorrect_decision_counts'], ensure_ascii=False, sort_keys=True)}` |"
        )
    lines.extend(
        [
            "",
            "## False Accept Breakdown",
            "",
            "| level | false accepts by expected outcome | false accepts by candidate type |",
            "| --- | --- | --- |",
        ]
    )
    for level in EXPECTED_LEVELS:
        outcome_breakdown = {
            key: value["decision_counts"].get("accept", 0)
            for key, value in analysis["breakdowns_by_evidence_level"][level]["expected_outcome"].items()
            if key != "correct"
        }
        outcome_breakdown = {key: value for key, value in outcome_breakdown.items() if value}
        type_breakdown = {
            key: value["decision_counts"].get("accept", 0)
            for key, value in analysis["breakdowns_by_evidence_level"][level]["candidate_type"].items()
            if key != "correct_reference"
        }
        type_breakdown = {key: value for key, value in type_breakdown.items() if value}
        lines.append(
            f"| {level} | `{json.dumps(outcome_breakdown, ensure_ascii=False, sort_keys=True)}` | "
            f"`{json.dumps(type_breakdown, ensure_ascii=False, sort_keys=True)}` |"
        )
    lines.extend(
        [
            "",
            "## E0-to-Level Accept Transitions",
            "",
            "| target | correct non-accept -> accept | incorrect non-accept -> accept |",
            "| --- | ---: | ---: |",
        ]
    )
    for target in EXPECTED_LEVELS[1:]:
        transition = analysis["paired_transitions"]["vs_e0"][f"E0->{target}"]["accept_transition_counts"]
        lines.append(
            f"| {target} | {transition['correct_nonaccept_to_accept']} | "
            f"{transition['incorrect_nonaccept_to_accept']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            f"- Allowed: {analysis['claim_boundary']['allowed']}",
            f"- Forbidden: {analysis['claim_boundary']['forbidden']}",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-set", type=Path, default=DEFAULT_CANDIDATE_SET)
    parser.add_argument("--labels", type=Path, default=DEFAULT_LABELS)
    parser.add_argument("--raw-responses", type=Path, default=DEFAULT_RAW_RESPONSES)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    analysis = build_summary(args.candidate_set, args.labels, args.raw_responses)
    write_json(args.json_out, analysis)
    write_markdown(args.md_out, analysis)
    if args.check and not all(item["passed"] for item in analysis["checks"]):
        return 1
    print(json.dumps(analysis, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
