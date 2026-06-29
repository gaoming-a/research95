"""Raw-output-free audit for EVP-8-HARD Qwen/DeepSeek results.

The audit can run before model execution. In that state it writes a waiting
summary and does not fail, so the result-analysis boundary is explicit before
any API call.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVALUATOR = REPO_ROOT / "data" / "patches" / "evp8_hard_evaluator_manifest_v0_1.jsonl"
DEFAULT_BASELINE = REPO_ROOT / "data" / "baselines" / "evp8_hard_tool_only_baseline_v0_1.jsonl"
DEFAULT_REVIEWS_GLOB = REPO_ROOT / "data" / "reviews" / "evp8_hard_*_full_reviews.jsonl"
DEFAULT_OUT = REPO_ROOT / "data" / "protocols" / "evp8_hard_qwen_deepseek_result_audit_v0_1.json"
CORRECT_LABEL = "correct"
DECISIONS = {"accept", "reject", "escalate"}


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


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def count_values(values: Iterable[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 6) if denominator else None


def is_correct(row: dict[str, Any]) -> bool:
    return row.get("normalized_label") == CORRECT_LABEL


def normalize_decision(row: dict[str, Any]) -> str:
    if row.get("parse_status", "valid") != "valid":
        return "invalid_output"
    decision = row.get("decision")
    return decision if decision in DECISIONS else "invalid_output"


def confusion(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {
        "true_accept": 0,
        "false_accept": 0,
        "true_reject": 0,
        "false_reject": 0,
        "escalated_correct": 0,
        "escalated_incorrect": 0,
        "invalid_correct": 0,
        "invalid_incorrect": 0,
    }
    examples = {
        "false_accepts": [],
        "false_rejects": [],
        "escalated_correct": [],
        "escalated_incorrect": [],
        "invalid_outputs": [],
    }
    for row in rows:
        correct = bool(row["is_correct"])
        decision = row["decision_normalized"]
        candidate_id = row["candidate_id"]
        if decision == "accept" and correct:
            counts["true_accept"] += 1
        elif decision == "accept":
            counts["false_accept"] += 1
            examples["false_accepts"].append(candidate_id)
        elif decision == "reject" and correct:
            counts["false_reject"] += 1
            examples["false_rejects"].append(candidate_id)
        elif decision == "reject":
            counts["true_reject"] += 1
        elif decision == "escalate" and correct:
            counts["escalated_correct"] += 1
            examples["escalated_correct"].append(candidate_id)
        elif decision == "escalate":
            counts["escalated_incorrect"] += 1
            examples["escalated_incorrect"].append(candidate_id)
        elif correct:
            counts["invalid_correct"] += 1
            examples["invalid_outputs"].append(candidate_id)
        else:
            counts["invalid_incorrect"] += 1
            examples["invalid_outputs"].append(candidate_id)
    accepted = counts["true_accept"] + counts["false_accept"]
    correct_total = counts["true_accept"] + counts["false_reject"] + counts["escalated_correct"] + counts["invalid_correct"]
    incorrect_total = counts["false_accept"] + counts["true_reject"] + counts["escalated_incorrect"] + counts["invalid_incorrect"]
    invalid_total = counts["invalid_correct"] + counts["invalid_incorrect"]
    escalated_total = counts["escalated_correct"] + counts["escalated_incorrect"]
    return {
        "counts": counts,
        "metrics": {
            "accepted_precision": ratio(counts["true_accept"], accepted),
            "correct_recall": ratio(counts["true_accept"], correct_total),
            "false_accept_rate": ratio(counts["false_accept"], incorrect_total),
            "false_reject_rate": ratio(counts["false_reject"], correct_total),
            "escalation_rate": ratio(escalated_total, len(rows)),
            "invalid_output_rate": ratio(invalid_total, len(rows)),
            "accepted_total": accepted,
            "correct_total": correct_total,
            "incorrect_total": incorrect_total,
            "record_count": len(rows),
        },
        "examples": examples,
    }


def joined_tool_rows(evaluator: dict[str, dict[str, Any]], baseline: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for record in baseline:
        candidate_id = str(record["candidate_id"])
        label_row = evaluator[candidate_id]
        rows.append(
            {
                "candidate_id": candidate_id,
                "is_correct": is_correct(label_row),
                "normalized_label": label_row.get("normalized_label"),
                "candidate_type": label_row.get("candidate_type"),
                "decision_normalized": normalize_decision(record),
                "decision": record.get("decision"),
            }
        )
    return rows


def joined_model_rows(evaluator: dict[str, dict[str, Any]], reviews: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for record in reviews:
        candidate_id = str(record["anonymous_candidate_id"])
        label_row = evaluator.get(candidate_id, {})
        rows.append(
            {
                "candidate_id": candidate_id,
                "is_correct": bool(label_row) and is_correct(label_row),
                "normalized_label": label_row.get("normalized_label"),
                "candidate_type": label_row.get("candidate_type"),
                "decision_normalized": normalize_decision(record),
                "decision": record.get("decision"),
                "parse_status": record.get("parse_status"),
            }
        )
    return rows


def model_name_from_reviews(path: Path, reviews: list[dict[str, Any]]) -> str:
    for record in reviews:
        model_id = record.get("configured_model_id")
        if model_id:
            return str(model_id)
    return path.stem.removeprefix("evp8_hard_").removesuffix("_full_reviews")


def opportunity_correction(model_rows: list[dict[str, Any]], tool_summary: dict[str, Any]) -> dict[str, Any]:
    by_id = {row["candidate_id"]: row for row in model_rows}
    examples = tool_summary["examples"]
    false_accept_ids = list(examples["false_accepts"])
    false_reject_ids = list(examples["false_rejects"])

    def rows_for(ids: list[str]) -> list[dict[str, Any]]:
        return [by_id[candidate_id] for candidate_id in ids if candidate_id in by_id]

    false_accept_rows = rows_for(false_accept_ids)
    false_reject_rows = rows_for(false_reject_ids)
    return {
        "tool_false_accepts": {
            "candidate_count": len(false_accept_ids),
            "model_record_count": len(false_accept_rows),
            "corrected_to_reject": sum(1 for row in false_accept_rows if row["decision_normalized"] == "reject"),
            "repeated_accept": sum(1 for row in false_accept_rows if row["decision_normalized"] == "accept"),
            "escalated": sum(1 for row in false_accept_rows if row["decision_normalized"] == "escalate"),
            "invalid_output": sum(1 for row in false_accept_rows if row["decision_normalized"] == "invalid_output"),
            "decision_counts": count_values(row["decision_normalized"] for row in false_accept_rows),
        },
        "tool_false_rejects": {
            "candidate_count": len(false_reject_ids),
            "model_record_count": len(false_reject_rows),
            "corrected_to_accept": sum(1 for row in false_reject_rows if row["decision_normalized"] == "accept"),
            "repeated_reject": sum(1 for row in false_reject_rows if row["decision_normalized"] == "reject"),
            "escalated": sum(1 for row in false_reject_rows if row["decision_normalized"] == "escalate"),
            "invalid_output": sum(1 for row in false_reject_rows if row["decision_normalized"] == "invalid_output"),
            "decision_counts": count_values(row["decision_normalized"] for row in false_reject_rows),
        },
    }


def raw_field_findings(records: list[dict[str, Any]]) -> list[str]:
    forbidden = {"raw_response_text", "response", "prompt", "rendered_prompt"}
    findings: set[str] = set()
    for record in records:
        findings.update(key for key in forbidden if key in record)
    return sorted(findings)


def discover_review_paths(explicit_paths: list[Path]) -> list[Path]:
    if explicit_paths:
        paths = [resolve(path) for path in explicit_paths]
        missing = [path for path in paths if not path.exists()]
        if missing:
            raise SystemExit(f"Missing parsed review file(s): {', '.join(display_path(path) for path in missing)}")
        return paths
    return sorted(DEFAULT_REVIEWS_GLOB.parent.glob(DEFAULT_REVIEWS_GLOB.name))


def build_summary(args: argparse.Namespace) -> dict[str, Any]:
    evaluator_rows = read_jsonl(resolve(args.evaluator_manifest))
    evaluator = {str(row["hard_candidate_id"]): row for row in evaluator_rows}
    baseline_rows = read_jsonl(resolve(args.tool_only_baseline))
    tool_rows = joined_tool_rows(evaluator, baseline_rows)
    tool_summary = confusion(tool_rows)
    review_paths = discover_review_paths(args.parsed_reviews)

    model_summaries: dict[str, Any] = {}
    raw_findings: dict[str, list[str]] = {}
    model_integrity_errors: dict[str, Any] = {}
    expected_candidate_ids = set(evaluator)
    for path in review_paths:
        reviews = read_jsonl(path)
        findings = raw_field_findings(reviews)
        raw_findings[display_path(path)] = findings
        rows = joined_model_rows(evaluator, reviews)
        model_id = model_name_from_reviews(path, reviews)
        observed_candidate_ids = [row["candidate_id"] for row in rows]
        observed_unique_ids = set(observed_candidate_ids)
        missing_ids = sorted(expected_candidate_ids - observed_unique_ids)
        extra_ids = sorted(observed_unique_ids - expected_candidate_ids)
        duplicate_ids = sorted(
            candidate_id
            for candidate_id, count in count_values(observed_candidate_ids).items()
            if count > 1
        )
        if len(rows) != len(evaluator) or missing_ids or extra_ids or duplicate_ids:
            model_integrity_errors[model_id] = {
                "review_count": len(rows),
                "expected_count": len(evaluator),
                "missing_candidate_ids": missing_ids,
                "extra_candidate_ids": extra_ids,
                "duplicate_candidate_ids": duplicate_ids,
            }
        model_confusion = confusion(rows)
        model_summaries[model_id] = {
            "parsed_reviews_path": display_path(path),
            "review_count": len(reviews),
            "expected_review_count": len(evaluator),
            "complete_candidate_coverage": model_id not in model_integrity_errors,
            "decision_counts": count_values(row["decision_normalized"] for row in rows),
            "label_counts": count_values(row["normalized_label"] for row in rows),
            "confusion": model_confusion,
            "delta_vs_tool": {
                "false_accept_count": model_confusion["counts"]["false_accept"] - tool_summary["counts"]["false_accept"],
                "false_reject_count": model_confusion["counts"]["false_reject"] - tool_summary["counts"]["false_reject"],
                "accepted_total": model_confusion["metrics"]["accepted_total"] - tool_summary["metrics"]["accepted_total"],
                "escalated_total": (
                    model_confusion["counts"]["escalated_correct"]
                    + model_confusion["counts"]["escalated_incorrect"]
                    - tool_summary["counts"]["escalated_correct"]
                    - tool_summary["counts"]["escalated_incorrect"]
                ),
            },
            "opportunity_correction_vs_tool": opportunity_correction(rows, tool_summary),
        }

    raw_field_errors = {path: findings for path, findings in raw_findings.items() if findings}
    status = "waiting_for_model_results" if not model_summaries else "passed"
    if raw_field_errors or model_integrity_errors:
        status = "blocked"
    return {
        "analysis_id": "evp8_hard_qwen_deepseek_result_audit_v0_1",
        "audit_status": status,
        "cohort_id": "EVP-8-HARD",
        "inputs": {
            "evaluator_manifest": display_path(resolve(args.evaluator_manifest)),
            "tool_only_baseline": display_path(resolve(args.tool_only_baseline)),
            "parsed_review_files": [display_path(path) for path in review_paths],
        },
        "scope": {
            "api_call_attempted": False,
            "raw_model_outputs_read": False,
            "prompt_text_read": False,
            "raw_response_text_allowed_in_parsed_reviews": False,
        },
        "candidate_count": len(evaluator),
        "tool_only_baseline": {
            "decision_counts": count_values(row["decision_normalized"] for row in tool_rows),
            "label_counts": count_values(row["normalized_label"] for row in tool_rows),
            "confusion": tool_summary,
        },
        "models": model_summaries,
        "checks": [
            {"check": "api_call_not_attempted_by_audit", "passed": True, "detail": False},
            {"check": "raw_model_outputs_not_read", "passed": True, "detail": False},
            {
                "check": "parsed_reviews_status_is_explicit",
                "passed": True,
                "detail": {
                    "parsed_review_model_count": len(model_summaries),
                    "status": "present" if model_summaries else "waiting_for_model_results",
                },
            },
            {"check": "parsed_reviews_do_not_contain_raw_fields", "passed": not raw_field_errors, "detail": raw_field_errors},
            {"check": "model_review_candidate_coverage_complete", "passed": not model_integrity_errors, "detail": model_integrity_errors},
        ],
        "next_step": (
            "Run authorized Qwen/DeepSeek executions, then rerun this audit."
            if status == "waiting_for_model_results"
            else "Use this raw-output-free audit for label-conditioned EVP-8-HARD analysis."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluator-manifest", type=Path, default=DEFAULT_EVALUATOR)
    parser.add_argument("--tool-only-baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--parsed-reviews", type=Path, nargs="*", default=[])
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = build_summary(args)
    write_json(resolve(args.out), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    if summary["audit_status"] == "blocked":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
