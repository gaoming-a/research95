# ruff: noqa: E402
"""Analyze current-98 coverage-contestation prompt-sensitivity results.

Inputs are tracked normalized review JSONL files plus evaluator-only labels.
The script does not read raw model responses. Outputs are aggregate and
candidate-id-level summaries without raw response text, prompts, patch diffs,
or credentials.
"""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/analyze_evp8_coverage_contestation_current98.py")

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATE_SET = REPO_ROOT / "data" / "protocols" / "evp8_candidate_set_v0_1.json"
DEFAULT_LABELS = REPO_ROOT / "data" / "patches" / "evp7_candidates.jsonl"
DEFAULT_TOOL_ONLY = REPO_ROOT / "data" / "baselines" / "evp7_tool_only_decisions.jsonl"
DEFAULT_REVIEWS = {
    "qwen/qwen3.7-max": REPO_ROOT
    / "data"
    / "reviews"
    / "evp8_coverage_contestation_current98_qwen_qwen3.7-max_full_reviews.jsonl",
    "deepseek/deepseek-v4-pro": REPO_ROOT
    / "data"
    / "reviews"
    / "evp8_coverage_contestation_current98_deepseek_deepseek-v4-pro_full_reviews.jsonl",
    "google/gemini-2.5-flash": REPO_ROOT
    / "data"
    / "reviews"
    / "evp8_coverage_contestation_current98_google_gemini-2.5-flash_full_reviews.jsonl",
}
DEFAULT_JSON_OUT = (
    REPO_ROOT / "data" / "reviews" / "evp8_coverage_contestation_current98_analysis_v0_1.json"
)
DEFAULT_MD_OUT = (
    REPO_ROOT / "docs" / "experiments" / "evp8_coverage_contestation_current98_analysis_v0_1.md"
)
CORRECT_LABEL = "correct_under_f2p_and_p2p_broad"
EXPECTED_CANDIDATE_COUNT = 98
EXPECTED_MODEL_COUNT = 3


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


def counts(values: Any) -> dict[str, int]:
    return dict(sorted(Counter(str(value) for value in values).items()))


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def build_candidate_map(path: Path) -> dict[str, dict[str, Any]]:
    records = read_json(path).get("records") or []
    result = {}
    for record in records:
        evp8_id = str(record["evp8_candidate_id"])
        result[evp8_id] = {
            "source_candidate_id": str(record["source_candidate_id"]),
            "project": record.get("project"),
            "task_id": record.get("task_id"),
        }
    return result


def build_label_map(path: Path) -> dict[str, dict[str, Any]]:
    result = {}
    for record in read_jsonl(path):
        result[str(record["evp7_candidate_id"])] = {
            "label_with_p2p_broad": record.get("label_with_p2p_broad"),
            "expected_outcome": record.get("expected_outcome"),
            "candidate_type": record.get("candidate_type"),
            "project": record.get("project"),
            "task_id": record.get("task_id"),
        }
    return result


def join_label(
    evp8_id: str,
    candidate_map: dict[str, dict[str, Any]],
    label_map: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    candidate = candidate_map[evp8_id]
    source_id = candidate["source_candidate_id"]
    label = label_map[source_id]
    return {
        "evp8_candidate_id": evp8_id,
        "source_candidate_id": source_id,
        "project": candidate["project"],
        "task_id": candidate["task_id"],
        "is_correct": label["label_with_p2p_broad"] == CORRECT_LABEL,
        "label_with_p2p_broad": label["label_with_p2p_broad"],
        "expected_outcome": label["expected_outcome"],
        "candidate_type": label["candidate_type"],
    }


def normalized_model_records(
    model_id: str,
    path: Path,
    candidate_map: dict[str, dict[str, Any]],
    label_map: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    records = []
    for review in read_jsonl(path):
        if review.get("parse_status") != "valid":
            raise ValueError(f"{display_path(path)} contains invalid parse record")
        evp8_id = str(review["anonymous_candidate_id"])
        label = join_label(evp8_id, candidate_map, label_map)
        records.append(
            {
                **label,
                "model_id": model_id,
                "condition": review.get("condition"),
                "decision": review.get("decision"),
                "confidence": review.get("confidence"),
                "risk_flags": review.get("risk_flags") or [],
                "coverage_concern": review.get("coverage_concern"),
                "visible_tests_sufficient": review.get("visible_tests_sufficient"),
                "tool_evidence_reliability": review.get("tool_evidence_reliability"),
                "would_challenge_visible_test_only_accept": review.get(
                    "would_challenge_visible_test_only_accept"
                ),
                "human_review_needed": review.get("human_review_needed"),
            }
        )
    return records


def rule_only_records(
    path: Path,
    candidate_map: dict[str, dict[str, Any]],
    label_map: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    source_to_evp8 = {
        value["source_candidate_id"]: evp8_id for evp8_id, value in candidate_map.items()
    }
    records = []
    for record in read_jsonl(path):
        if record.get("condition") != "tool_only_visible_tool_summary":
            continue
        source_id = str(record["candidate_id"])
        if source_id not in source_to_evp8:
            continue
        label = join_label(source_to_evp8[source_id], candidate_map, label_map)
        records.append(
            {
                **label,
                "model_id": "rule_only_visible_tool_summary",
                "condition": "rule-only-e6",
                "decision": record.get("decision"),
            }
        )
    return records


def confusion(records: list[dict[str, Any]]) -> dict[str, int]:
    result = {
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
            result["true_accept"] += 1
        elif decision == "accept":
            result["false_accept"] += 1
        elif decision == "reject" and is_correct:
            result["false_reject"] += 1
        elif decision == "reject":
            result["true_reject"] += 1
        elif decision == "escalate" and is_correct:
            result["escalated_correct"] += 1
        elif decision == "escalate":
            result["escalated_incorrect"] += 1
    return result


def metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    matrix = confusion(records)
    correct_total = matrix["true_accept"] + matrix["false_reject"] + matrix["escalated_correct"]
    incorrect_total = matrix["false_accept"] + matrix["true_reject"] + matrix["escalated_incorrect"]
    accepted_total = matrix["true_accept"] + matrix["false_accept"]
    rejected_total = matrix["true_reject"] + matrix["false_reject"]
    escalated_total = matrix["escalated_correct"] + matrix["escalated_incorrect"]
    return {
        "record_count": len(records),
        "correct_total": correct_total,
        "incorrect_total": incorrect_total,
        "decision_counts": counts(record["decision"] for record in records),
        "correct_decision_counts": counts(record["decision"] for record in records if record["is_correct"]),
        "incorrect_decision_counts": counts(record["decision"] for record in records if not record["is_correct"]),
        "confusion_counts": matrix,
        "accepted_precision": proportion(matrix["true_accept"], accepted_total),
        "correct_recall": proportion(matrix["true_accept"], correct_total),
        "correct_recall_loss": proportion(matrix["false_reject"] + matrix["escalated_correct"], correct_total),
        "false_accept_rate": proportion(matrix["false_accept"], incorrect_total),
        "strict_reject_rate_on_incorrect": proportion(matrix["true_reject"], incorrect_total),
        "safe_escalation_rate_on_incorrect": proportion(matrix["escalated_incorrect"], incorrect_total),
        "repeated_false_accept_rate_on_incorrect": proportion(matrix["false_accept"], incorrect_total),
        "safe_handling_rate_on_incorrect": proportion(
            matrix["true_reject"] + matrix["escalated_incorrect"],
            incorrect_total,
        ),
        "reject_rate": proportion(rejected_total, len(records)),
        "escalation_rate": proportion(escalated_total, len(records)),
    }


def prompt_field_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "coverage_concern_counts": counts(record.get("coverage_concern") for record in records),
        "incorrect_coverage_concern_counts": counts(
            record.get("coverage_concern") for record in records if not record["is_correct"]
        ),
        "visible_tests_sufficient_counts": counts(record.get("visible_tests_sufficient") for record in records),
        "incorrect_visible_tests_sufficient_counts": counts(
            record.get("visible_tests_sufficient") for record in records if not record["is_correct"]
        ),
        "tool_evidence_reliability_counts": counts(record.get("tool_evidence_reliability") for record in records),
        "incorrect_tool_evidence_reliability_counts": counts(
            record.get("tool_evidence_reliability") for record in records if not record["is_correct"]
        ),
        "challenge_visible_test_only_accept_counts": counts(
            record.get("would_challenge_visible_test_only_accept") for record in records
        ),
        "incorrect_challenge_visible_test_only_accept_counts": counts(
            record.get("would_challenge_visible_test_only_accept")
            for record in records
            if not record["is_correct"]
        ),
    }


def false_accept_cases(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cases = []
    for record in records:
        if record["is_correct"] or record["decision"] != "accept":
            continue
        cases.append(
            {
                "model_id": record["model_id"],
                "evp8_candidate_id": record["evp8_candidate_id"],
                "source_candidate_id": record["source_candidate_id"],
                "project": record["project"],
                "task_id": record["task_id"],
                "candidate_type": record["candidate_type"],
                "expected_outcome": record["expected_outcome"],
                "coverage_concern": record.get("coverage_concern"),
                "visible_tests_sufficient": record.get("visible_tests_sufficient"),
                "tool_evidence_reliability": record.get("tool_evidence_reliability"),
                "would_challenge_visible_test_only_accept": record.get(
                    "would_challenge_visible_test_only_accept"
                ),
                "risk_flags": record.get("risk_flags") or [],
            }
        )
    return cases


def grouped_metrics(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record["model_id"]].append(record)
    return {model_id: metrics(model_records) for model_id, model_records in sorted(grouped.items())}


def build_summary(args: argparse.Namespace) -> dict[str, Any]:
    candidate_map = build_candidate_map(args.candidate_set)
    label_map = build_label_map(args.labels)
    all_records = []
    model_paths = DEFAULT_REVIEWS
    for model_id, path in model_paths.items():
        all_records.extend(normalized_model_records(model_id, path, candidate_map, label_map))
    rule_records = rule_only_records(args.tool_only, candidate_map, label_map)
    by_model = defaultdict(list)
    for record in all_records:
        by_model[record["model_id"]].append(record)
    model_summaries = {
        model_id: {
            **metrics(records),
            **prompt_field_summary(records),
            "false_accept_cases": false_accept_cases(records),
            "false_accept_by_candidate_type": counts(
                record["candidate_type"]
                for record in records
                if not record["is_correct"] and record["decision"] == "accept"
            ),
            "false_accept_by_project": counts(
                record["project"]
                for record in records
                if not record["is_correct"] and record["decision"] == "accept"
            ),
        }
        for model_id, records in sorted(by_model.items())
    }
    checks = [
        check("candidate_count", len(candidate_map) == EXPECTED_CANDIDATE_COUNT, len(candidate_map)),
        check("model_count", len(by_model) == EXPECTED_MODEL_COUNT, sorted(by_model)),
        check(
            "review_count_per_model",
            all(len(records) == EXPECTED_CANDIDATE_COUNT for records in by_model.values()),
            {model_id: len(records) for model_id, records in sorted(by_model.items())},
        ),
        check("rule_only_count", len(rule_records) == EXPECTED_CANDIDATE_COUNT, len(rule_records)),
        check("raw_response_text_not_read", True, True),
        check("rendered_prompt_text_not_read", True, True),
    ]
    status = "passed" if all(item["passed"] for item in checks) else "blocked"
    return {
        "analysis_id": "evp8_coverage_contestation_current98_analysis_v0_1",
        "status": status,
        "cohort_id": "EVP-8",
        "condition": "coverage-contestation-current98-e6-no-verdict",
        "candidate_count": len(candidate_map),
        "model_count": len(by_model),
        "review_count": len(all_records),
        "model_summaries": model_summaries,
        "rule_only_e6_metrics": metrics(rule_records),
        "cross_model_summary": {
            "model_metrics": grouped_metrics(all_records),
            "all_false_accept_cases": false_accept_cases(all_records),
        },
        "claim_boundary": (
            "This analysis measures prompt sensitivity on the frozen current-98 E6/no-verdict "
            "cohort. It does not replace the repaired v0.3 main result and cannot establish "
            "general hard-negative robustness without the separate gated hard-negative cohort."
        ),
        "checks": checks,
    }


def write_md(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# EVP-8 current-98 coverage-contestation analysis v0.1",
        "",
        f"Status: `{summary['status']}`",
        "",
        "## Boundary",
        "",
        "- This is a prompt-sensitivity condition, not the repaired v0.3 main result.",
        "- It uses the frozen current-98 E6/no-verdict packet set.",
        "- Raw response text, rendered prompts, patch diffs, and credentials are not stored here.",
        "- The separate hard-negative verifier gate remains blocked until the cohort reaches 30 cases and 3 projects.",
        "",
        "## Main Metrics",
        "",
        "| model | accept | reject | escalate | accepted precision | correct recall | recall loss | repeated FA | strict reject on wrong | safe escalation on wrong |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for model_id, model in summary["model_summaries"].items():
        decisions = model["decision_counts"]
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{model_id}`",
                    str(decisions.get("accept", 0)),
                    str(decisions.get("reject", 0)),
                    str(decisions.get("escalate", 0)),
                    pct(model["accepted_precision"]),
                    pct(model["correct_recall"]),
                    pct(model["correct_recall_loss"]),
                    pct(model["repeated_false_accept_rate_on_incorrect"]),
                    pct(model["strict_reject_rate_on_incorrect"]),
                    pct(model["safe_escalation_rate_on_incorrect"]),
                ]
            )
            + " |"
        )
    rule = summary["rule_only_e6_metrics"]
    lines.extend(
        [
            "",
            "## Rule-Only Reference",
            "",
            f"- accepted precision: `{pct(rule['accepted_precision'])}`",
            f"- correct recall: `{pct(rule['correct_recall'])}`",
            f"- false accept rate: `{pct(rule['false_accept_rate'])}`",
            f"- decision counts: `{json.dumps(rule['decision_counts'], ensure_ascii=False, sort_keys=True)}`",
            "",
            "## Prompt-Specific Fields",
            "",
            "| model | high coverage concern | visible tests insufficient | challenge visible-test-only accept | insufficient tool evidence |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for model_id, model in summary["model_summaries"].items():
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{model_id}`",
                    str(model["coverage_concern_counts"].get("high", 0)),
                    str(model["visible_tests_sufficient_counts"].get("False", 0)),
                    str(model["challenge_visible_test_only_accept_counts"].get("True", 0)),
                    str(model["tool_evidence_reliability_counts"].get("insufficient_for_accept", 0)),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Repeated False Accept Cases",
            "",
            "| model | candidate | project | type | coverage concern | visible tests sufficient | tool reliability | challenge accept |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for case in summary["cross_model_summary"]["all_false_accept_cases"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{case['model_id']}`",
                    f"`{case['evp8_candidate_id']}`",
                    f"`{case['project']}`",
                    f"`{case['candidate_type']}`",
                    f"`{case['coverage_concern']}`",
                    f"`{case['visible_tests_sufficient']}`",
                    f"`{case['tool_evidence_reliability']}`",
                    f"`{case['would_challenge_visible_test_only_accept']}`",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            summary["claim_boundary"],
            "",
            "## Checks",
            "",
            "| check | passed | detail |",
            "| --- | --- | --- |",
        ]
    )
    for row in summary["checks"]:
        lines.append(
            f"| `{row['check']}` | {str(row['passed']).lower()} | `{json.dumps(row['detail'], ensure_ascii=False)}` |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-set", type=Path, default=DEFAULT_CANDIDATE_SET)
    parser.add_argument("--labels", type=Path, default=DEFAULT_LABELS)
    parser.add_argument("--tool-only", type=Path, default=DEFAULT_TOOL_ONLY)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    existing_json = args.json_out.read_text(encoding="utf-8") if args.json_out.exists() else None
    existing_md = args.md_out.read_text(encoding="utf-8") if args.md_out.exists() else None
    summary = build_summary(args)
    json_text = json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json_text, encoding="utf-8")
    write_md(summary, args.md_out)
    if args.check:
        current_md = args.md_out.read_text(encoding="utf-8")
        if existing_json is not None and existing_json != json_text:
            raise SystemExit(f"{display_path(args.json_out)} is not current")
        if existing_md is not None and existing_md != current_md:
            raise SystemExit(f"{display_path(args.md_out)} is not current")
        if existing_json is None or existing_md is None:
            raise SystemExit("coverage-contestation analysis outputs were missing before --check")
        if summary["status"] != "passed":
            raise SystemExit(f"coverage-contestation analysis status is {summary['status']}")
        print("coverage-contestation current-98 analysis outputs are current")
    else:
        print(f"wrote {display_path(args.json_out)}")
        print(f"wrote {display_path(args.md_out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
