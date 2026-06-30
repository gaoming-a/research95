"""Analyze EVP-8-HARD tool-contestation results on repeated false accepts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
FALSE_ACCEPT_ANALYSIS = REPO_ROOT / "data" / "reviews" / "evp8_hard_false_accept_case_analysis_v0_1.json"
DEFAULT_QWEN_REVIEWS = REPO_ROOT / "data" / "reviews" / "evp8_hard_tool_contestation_qwen_qwen3.7-max_full_reviews.jsonl"
DEFAULT_DEEPSEEK_REVIEWS = REPO_ROOT / "data" / "reviews" / "evp8_hard_tool_contestation_deepseek_deepseek-v4-pro_full_reviews.jsonl"
DEFAULT_OUT_JSON = REPO_ROOT / "data" / "reviews" / "evp8_hard_tool_contestation_opportunity_analysis_v0_1.json"
DEFAULT_OUT_MD = REPO_ROOT / "docs" / "experiments" / "evp8_hard_tool_contestation_opportunity_analysis_v0_1.md"


def display_path(path: Path) -> str:
    absolute = path if path.is_absolute() else REPO_ROOT / path
    try:
        return absolute.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(absolute)


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


def candidate_id(record: dict[str, Any]) -> str:
    for key in ("anonymous_candidate_id", "candidate_id", "hard_candidate_id"):
        value = record.get(key)
        if value:
            return str(value)
    raise KeyError(f"candidate id missing from keys: {sorted(record)}")


def normalize_decision(record: dict[str, Any]) -> str:
    if record.get("parse_status", "valid") != "valid":
        return "invalid_output"
    decision = record.get("decision")
    return str(decision) if decision in {"accept", "reject", "escalate"} else "invalid_output"


def model_id_from_reviews(path: Path, records: list[dict[str, Any]]) -> str:
    for record in records:
        if record.get("configured_model_id"):
            return str(record["configured_model_id"])
    if "qwen" in path.name:
        return "qwen/qwen3.7-max"
    if "deepseek" in path.name:
        return "deepseek/deepseek-v4-pro"
    return path.stem


def raw_field_findings(records: list[dict[str, Any]]) -> list[str]:
    forbidden = {"raw_response_text", "response", "prompt", "rendered_prompt"}
    findings: set[str] = set()
    for record in records:
        findings.update(key for key in forbidden if key in record)
    return sorted(findings)


def analyze_model(path: Path, opportunity_cases: list[dict[str, Any]]) -> dict[str, Any]:
    records = read_jsonl(path)
    raw_findings = raw_field_findings(records)
    by_id = {candidate_id(record): record for record in records}
    rows = []
    missing = []
    for case in opportunity_cases:
        cid = case["candidate_id"]
        record = by_id.get(cid)
        if record is None:
            missing.append(cid)
            rows.append(
                {
                    "candidate_id": cid,
                    "task_id": case.get("task_id"),
                    "theme": case.get("theme"),
                    "new_decision": "missing",
                    "transition": "accept->missing",
                    "risk_flags": [],
                    "coverage_concern": None,
                    "visible_tests_sufficient": None,
                    "tool_evidence_reliability": None,
                    "would_challenge_visible_test_only_accept": None,
                    "challenge_reason": None,
                    "primary_reason": None,
                }
            )
            continue
        decision = normalize_decision(record)
        rows.append(
            {
                "candidate_id": cid,
                "task_id": case.get("task_id"),
                "theme": case.get("theme"),
                "new_decision": decision,
                "transition": f"accept->{decision}",
                "risk_flags": record.get("risk_flags") or [],
                "coverage_concern": record.get("coverage_concern"),
                "visible_tests_sufficient": record.get("visible_tests_sufficient"),
                "tool_evidence_reliability": record.get("tool_evidence_reliability"),
                "would_challenge_visible_test_only_accept": record.get("would_challenge_visible_test_only_accept"),
                "challenge_reason": record.get("challenge_reason"),
                "primary_reason": record.get("primary_reason"),
            }
        )
    decisions = Counter(row["new_decision"] for row in rows)
    coverage = Counter(str(row["coverage_concern"]) for row in rows)
    reliability = Counter(str(row["tool_evidence_reliability"]) for row in rows)
    visible_sufficient = Counter(str(row["visible_tests_sufficient"]) for row in rows)
    challenge = Counter(str(row["would_challenge_visible_test_only_accept"]) for row in rows)
    challenge_true = sum(1 for row in rows if row["would_challenge_visible_test_only_accept"] is True)
    insufficient_or_challenged = sum(
        1
        for row in rows
        if row["visible_tests_sufficient"] is False
        or row["tool_evidence_reliability"] == "insufficient_for_accept"
        or row["coverage_concern"] in {"medium", "high"}
        or row["would_challenge_visible_test_only_accept"] is True
    )
    safe_handled = sum(1 for row in rows if row["new_decision"] in {"reject", "escalate"})
    return {
        "parsed_reviews_path": display_path(path),
        "model_id": model_id_from_reviews(path, records),
        "raw_field_findings": raw_findings,
        "review_count": len(records),
        "opportunity_record_count": len(rows),
        "missing_opportunity_ids": missing,
        "decision_counts_on_opportunity_set": dict(sorted(decisions.items())),
        "coverage_concern_counts": dict(sorted(coverage.items())),
        "visible_tests_sufficient_counts": dict(sorted(visible_sufficient.items())),
        "tool_evidence_reliability_counts": dict(sorted(reliability.items())),
        "challenge_visible_test_only_accept_counts": dict(sorted(challenge.items())),
        "strict_corrected_to_reject": decisions.get("reject", 0),
        "safe_handled_by_reject_or_escalate": safe_handled,
        "repeated_accept": decisions.get("accept", 0),
        "escalated": decisions.get("escalate", 0),
        "challenge_true": challenge_true,
        "insufficient_or_challenged": insufficient_or_challenged,
        "accept_but_challenged": sum(
            1
            for row in rows
            if row["new_decision"] == "accept" and row["would_challenge_visible_test_only_accept"] is True
        ),
        "accept_without_challenge": sum(
            1
            for row in rows
            if row["new_decision"] == "accept" and row["would_challenge_visible_test_only_accept"] is not True
        ),
        "cases": rows,
    }


def build_analysis(args: argparse.Namespace) -> dict[str, Any]:
    false_accept_analysis = read_json(args.false_accept_analysis)
    opportunity_cases = list(false_accept_analysis.get("cases") or [])
    review_paths = [path for path in args.parsed_reviews if path.exists()]
    model_summaries: dict[str, dict[str, Any]] = {}
    for path in review_paths:
        model_summary = analyze_model(path, opportunity_cases)
        model_summaries[model_summary["model_id"]] = model_summary
    raw_errors = {
        model_id: summary["raw_field_findings"]
        for model_id, summary in model_summaries.items()
        if summary["raw_field_findings"]
    }
    missing_errors = {
        model_id: summary["missing_opportunity_ids"]
        for model_id, summary in model_summaries.items()
        if summary["missing_opportunity_ids"]
    }
    if not model_summaries:
        status = "waiting_for_model_results"
    elif raw_errors or missing_errors:
        status = "blocked"
    elif len(model_summaries) == 1:
        status = "partial_passed_waiting_for_second_model"
    else:
        status = "passed"
    return {
        "analysis_id": "evp8_hard_tool_contestation_opportunity_analysis_v0_1",
        "analysis_status": status,
        "cohort_id": "EVP-8-HARD",
        "packet_variant": "e6_tool_contestation_no_verdict",
        "api_call_attempted": False,
        "raw_model_outputs_read": False,
        "prompt_text_read": False,
        "false_accept_analysis": display_path(args.false_accept_analysis),
        "opportunity_set_size": len(opportunity_cases),
        "opportunity_candidate_ids": [case["candidate_id"] for case in opportunity_cases],
        "expected_parsed_reviews": [display_path(path) for path in args.parsed_reviews],
        "existing_parsed_reviews": [display_path(path) for path in review_paths],
        "models": model_summaries,
        "checks": [
            {"check": "api_call_not_attempted_by_analysis", "passed": True, "detail": False},
            {"check": "raw_model_outputs_not_read", "passed": True, "detail": False},
            {"check": "opportunity_set_size_is_9", "passed": len(opportunity_cases) == 9, "detail": len(opportunity_cases)},
            {"check": "parsed_reviews_do_not_contain_raw_fields", "passed": not raw_errors, "detail": raw_errors},
            {"check": "opportunity_coverage_complete_for_existing_models", "passed": not missing_errors, "detail": missing_errors},
        ],
        "claim_boundary": (
            "Challenge, insufficient-evidence, or escalation outcomes are risk-triage signals; "
            "they are not automatic proof that the model identified semantic incorrectness."
        ),
        "next_step": (
            "Run authorized EVP-8-HARD tool-contestation Qwen API, then rerun this analysis."
            if status == "waiting_for_model_results"
            else "Interpret tool-contestation signals separately from strict reject corrections."
        ),
    }


def write_markdown(path: Path, analysis: dict[str, Any]) -> None:
    lines = [
        "# EVP-8-HARD Tool-Contestation Opportunity Analysis v0.1",
        "",
        f"- Status: `{analysis['analysis_status']}`",
        f"- Opportunity set size: `{analysis['opportunity_set_size']}`",
        f"- API call attempted: `{str(analysis['api_call_attempted']).lower()}`",
        f"- Raw model outputs read: `{str(analysis['raw_model_outputs_read']).lower()}`",
        "",
        "## Purpose",
        "",
        "This analysis focuses only on the nine candidates that the tool baseline,",
        "Qwen E6-full, and DeepSeek E6-full all falsely accepted. It checks whether",
        "a tool-contestation prompt makes the model challenge a visible-test-only",
        "accept premise, mark visible tests as insufficient, or move accept to",
        "reject/escalate.",
        "",
    ]
    if not analysis["models"]:
        lines.extend(
            [
                "## Waiting State",
                "",
                "No tool-contestation parsed reviews exist yet.",
                "",
                "Expected parsed review files:",
                "",
            ]
        )
        lines.extend(f"- `{path}`" for path in analysis["expected_parsed_reviews"])
    else:
        lines.extend(
            [
                "## Model Results",
                "",
                "| Model | repeated accept | accept without challenge | challenge true | insufficient/challenged | reject | escalate | safe handled |",
                "|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for model_id, summary in sorted(analysis["models"].items()):
            decisions = summary["decision_counts_on_opportunity_set"]
            lines.append(
                "| {model} | {accept} | {accept_no_challenge} | {challenge} | {insufficient} | {reject} | {escalate} | {safe} |".format(
                    model=model_id,
                    accept=summary["repeated_accept"],
                    accept_no_challenge=summary["accept_without_challenge"],
                    challenge=summary["challenge_true"],
                    insufficient=summary["insufficient_or_challenged"],
                    reject=decisions.get("reject", 0),
                    escalate=summary["escalated"],
                    safe=summary["safe_handled_by_reject_or_escalate"],
                )
            )
        lines.extend(["", "## Claim Boundary", "", analysis["claim_boundary"]])
    lines.extend(["", "## Checks", ""])
    lines.extend(f"- `{check['check']}`: `{str(check['passed']).lower()}`" for check in analysis["checks"])
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--false-accept-analysis", type=Path, default=FALSE_ACCEPT_ANALYSIS)
    parser.add_argument(
        "--parsed-reviews",
        type=Path,
        nargs="*",
        default=[DEFAULT_QWEN_REVIEWS, DEFAULT_DEEPSEEK_REVIEWS],
    )
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    analysis = build_analysis(args)
    out_json = args.out_json if args.out_json.is_absolute() else REPO_ROOT / args.out_json
    out_md = args.out_md if args.out_md.is_absolute() else REPO_ROOT / args.out_md
    write_json(out_json, analysis)
    write_markdown(out_md, analysis)
    print(json.dumps(analysis, ensure_ascii=False, indent=2, sort_keys=True))
    if args.check and analysis["analysis_status"] == "blocked":
        raise SystemExit("tool-contestation opportunity analysis blocked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
