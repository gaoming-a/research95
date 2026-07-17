# ruff: noqa: E402
"""Analyze raw-free EVP-8 hard-negative stress matrix reviews."""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/analyze_evp8_realistic_hardneg_stress_matrix.py")

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SUMMARY_IN = REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_stress_cohort_v0_1.json"
PREFLIGHT_IN = (
    REPO_ROOT
    / "data"
    / "protocols"
    / "evp8_realistic_hardneg_stress_matrix_preflight_v0_1.json"
)
REVIEWS_DIR = REPO_ROOT / "data" / "reviews"
JSON_OUT = REPO_ROOT / "data" / "reviews" / "evp8_realistic_hardneg_stress_matrix_analysis_v0_1.json"
MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_realistic_hardneg_stress_matrix_analysis_v0_1.md"


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
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{display_path(path)}:{line_number} must contain a JSON object")
        rows.append(value)
    return rows


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def counts(values: Any) -> dict[str, int]:
    return dict(sorted(Counter(str(value) for value in values).items()))


def review_path(condition_id: str, model_id: str) -> Path:
    return REVIEWS_DIR / f"evp8_realistic_hardneg_stress_matrix_{condition_id}_{safe_name(model_id)}_reviews.jsonl"


def summary_path(condition_id: str, model_id: str) -> Path:
    return REVIEWS_DIR / f"evp8_realistic_hardneg_stress_matrix_{condition_id}_{safe_name(model_id)}_summary.json"


def candidate_map(cohort: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = {}
    for row in cohort.get("case_records") or []:
        if isinstance(row, dict):
            rows[str(row["candidate_id"])] = row
    return rows


def metrics(records: list[dict[str, Any]], case_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    total = len(records)
    valid = [row for row in records if row.get("parse_status") == "valid"]
    decision_counts = Counter(str(row.get("decision")) for row in valid)
    repeated_false_accept = decision_counts.get("accept", 0)
    strict_reject = decision_counts.get("reject", 0)
    safe_escalation = decision_counts.get("escalate", 0)
    by_project: dict[str, Counter[str]] = defaultdict(Counter)
    by_source_kind: dict[str, Counter[str]] = defaultdict(Counter)
    for row in valid:
        candidate = case_by_id.get(str(row.get("anonymous_candidate_id"))) or {}
        project = str(candidate.get("project") or "unknown")
        source_kind = str(candidate.get("source_kind") or "unknown")
        by_project[project][str(row.get("decision"))] += 1
        by_source_kind[source_kind][str(row.get("decision"))] += 1
    return {
        "record_count": total,
        "parse_valid_count": len(valid),
        "invalid_parse_count": total - len(valid),
        "decision_counts": dict(sorted(decision_counts.items())),
        "repeated_false_accept_count": repeated_false_accept,
        "repeated_false_accept_rate": repeated_false_accept / total if total else None,
        "strict_reject_count": strict_reject,
        "strict_reject_rate": strict_reject / total if total else None,
        "safe_escalation_count": safe_escalation,
        "safe_escalation_rate": safe_escalation / total if total else None,
        "safe_handling_count": strict_reject + safe_escalation,
        "safe_handling_rate": (strict_reject + safe_escalation) / total if total else None,
        "decision_counts_by_project": {
            project: dict(sorted(counter.items())) for project, counter in sorted(by_project.items())
        },
        "decision_counts_by_source_kind": {
            source: dict(sorted(counter.items())) for source, counter in sorted(by_source_kind.items())
        },
        "coverage_concern_counts": counts(row.get("coverage_concern") for row in valid),
        "challenge_visible_test_only_accept_counts": counts(
            row.get("would_challenge_visible_test_only_accept") for row in valid
        ),
    }


def cost_sum(summary_rows: list[dict[str, Any]]) -> dict[str, Any]:
    total_usd = 0.0
    total_cny = 0.0
    unknown = 0
    planned_review_calls = 0
    invalid_raw_retries = 0
    for row in summary_rows:
        cost = row.get("cost_summary") or {}
        total_usd += float(cost.get("total_cost_usd") or 0.0)
        total_cny += float(cost.get("total_cost_cny") or 0.0)
        unknown += int(cost.get("unknown_cost_record_count") or 0)
        planned_review_calls += int(row.get("review_count") or 0)
        invalid_raw_retries += int(row.get("invalid_raw_retry_count") or 0)
    return {
        "total_cost_usd": round(total_usd, 9),
        "total_cost_cny": round(total_cny, 9),
        "unknown_cost_record_count": unknown,
        "planned_review_call_count": planned_review_calls,
        "invalid_raw_retry_count": invalid_raw_retries,
        "effective_api_call_count_including_invalid_retries": planned_review_calls + invalid_raw_retries,
    }


def build_analysis() -> dict[str, Any]:
    cohort = read_json(SUMMARY_IN)
    preflight = read_json(PREFLIGHT_IN)
    case_by_id = candidate_map(cohort)
    model_ids = [str(model["model_id"]) for model in preflight.get("models") or []]
    condition_ids = [str(condition) for condition in preflight.get("prompt_conditions_ready") or []]
    per_condition_model: dict[str, dict[str, Any]] = {}
    summary_rows: list[dict[str, Any]] = []
    checks = []
    for condition_id in condition_ids:
        per_condition_model[condition_id] = {}
        for model_id in model_ids:
            reviews_file = review_path(condition_id, model_id)
            summary_file = summary_path(condition_id, model_id)
            reviews = read_jsonl(reviews_file) if reviews_file.exists() else []
            run_summary = read_json(summary_file) if summary_file.exists() else {}
            summary_rows.append(run_summary)
            run_metrics = metrics(reviews, case_by_id)
            per_condition_model[condition_id][model_id] = {
                "reviews": display_path(reviews_file),
                "summary": display_path(summary_file),
                "run_gate": run_summary.get("run_gate"),
                "metrics": run_metrics,
                "cost_summary": run_summary.get("cost_summary") or {},
            }
            checks.append({
                "check": f"{condition_id}_{safe_name(model_id)}_run_gate_passed",
                "passed": run_summary.get("run_gate") == "passed",
                "detail": run_summary.get("run_gate"),
            })
            checks.append({
                "check": f"{condition_id}_{safe_name(model_id)}_record_count_31",
                "passed": run_metrics["record_count"] == 31,
                "detail": run_metrics["record_count"],
            })
            checks.append({
                "check": f"{condition_id}_{safe_name(model_id)}_parse_valid_31",
                "passed": run_metrics["parse_valid_count"] == 31,
                "detail": run_metrics["parse_valid_count"],
            })
    aggregate_by_condition: dict[str, Any] = {}
    for condition_id in condition_ids:
        records: list[dict[str, Any]] = []
        for model_id in model_ids:
            records.extend(read_jsonl(review_path(condition_id, model_id)))
        aggregate_by_condition[condition_id] = metrics(records, case_by_id)
    status = "passed" if checks and all(row["passed"] for row in checks) else "blocked"
    return {
        "analysis_id": "evp8_realistic_hardneg_stress_matrix_analysis_v0_1",
        "status": status,
        "cohort_id": "EVP-8-REALISTIC-HARDNEG-STRESS",
        "input_cohort_summary": display_path(SUMMARY_IN),
        "input_preflight": display_path(PREFLIGHT_IN),
        "candidate_count": cohort.get("candidate_count"),
        "hidden_label_boundary": "All 31 stress-cohort candidates are visible-pass/hidden-fail hard negatives.",
        "model_ids": model_ids,
        "condition_ids": condition_ids,
        "per_condition_model": per_condition_model,
        "aggregate_by_condition": aggregate_by_condition,
        "cost_summary": cost_sum(summary_rows),
        "raw_response_text_stored": False,
        "rendered_prompt_text_stored": False,
        "patch_text_stored": False,
        "claim_boundary": (
            "This analysis measures false-accept handling on a hard-negative stress cohort. "
            "It does not measure correct recall and does not establish autonomous correctness verification."
        ),
        "checks": checks,
    }


def fmt_rate(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value) * 100:.2f}%"


def write_md(analysis: dict[str, Any], path: Path) -> None:
    lines = [
        "# EVP-8 hard-negative stress matrix analysis v0.1",
        "",
        f"Status: `{analysis['status']}`",
        "",
        "## Boundary",
        "",
        "- This is a hard-negative stress-test result: all candidates are visible-pass/hidden-fail.",
        "- Metrics are repeated false accept, strict reject, safe escalation, and safe handling.",
        "- Correct recall is not defined for this all-negative cohort.",
        "- Tracked outputs do not store raw response text, rendered prompts, or patch text.",
        "",
        "## Aggregate By Condition",
        "",
        "| condition | records | repeated false accepts | strict rejects | safe escalations | safe handling |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition_id, row in analysis["aggregate_by_condition"].items():
        lines.append(
            f"| `{condition_id}` | {row['record_count']} | "
            f"{row['repeated_false_accept_count']} ({fmt_rate(row['repeated_false_accept_rate'])}) | "
            f"{row['strict_reject_count']} ({fmt_rate(row['strict_reject_rate'])}) | "
            f"{row['safe_escalation_count']} ({fmt_rate(row['safe_escalation_rate'])}) | "
            f"{row['safe_handling_count']} ({fmt_rate(row['safe_handling_rate'])}) |"
        )
    lines.extend([
        "",
        "## Per Model",
        "",
        "| condition | model | accept | reject | escalate | safe handling |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ])
    for condition_id, models in analysis["per_condition_model"].items():
        for model_id, payload in models.items():
            row = payload["metrics"]
            decisions = row["decision_counts"]
            lines.append(
                f"| `{condition_id}` | `{model_id}` | "
                f"{decisions.get('accept', 0)} | {decisions.get('reject', 0)} | "
                f"{decisions.get('escalate', 0)} | "
                f"{row['safe_handling_count']} ({fmt_rate(row['safe_handling_rate'])}) |"
            )
    lines.extend([
        "",
        "## Cost",
        "",
        f"- total USD: `{analysis['cost_summary']['total_cost_usd']}`",
        f"- total CNY: `{analysis['cost_summary']['total_cost_cny']}`",
        f"- unknown-cost records: `{analysis['cost_summary']['unknown_cost_record_count']}`",
        f"- planned review calls: `{analysis['cost_summary']['planned_review_call_count']}`",
        f"- invalid raw retries: `{analysis['cost_summary']['invalid_raw_retry_count']}`",
        f"- effective API calls including retries: `{analysis['cost_summary']['effective_api_call_count_including_invalid_retries']}`",
        "",
        "## Checks",
        "",
        "| check | passed | detail |",
        "| --- | --- | --- |",
    ])
    for row in analysis["checks"]:
        lines.append(
            f"| `{row['check']}` | {str(row['passed']).lower()} | `{json.dumps(row['detail'], ensure_ascii=False)}` |"
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=MD_OUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    existing_json = args.json_out.read_text(encoding="utf-8") if args.json_out.exists() else None
    existing_md = args.md_out.read_text(encoding="utf-8") if args.md_out.exists() else None
    analysis = build_analysis()
    json_text = json.dumps(analysis, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json_text, encoding="utf-8")
    write_md(analysis, args.md_out)
    if args.check:
        if existing_json is not None and existing_json != json_text:
            raise SystemExit(f"{display_path(args.json_out)} is not current")
        current_md = args.md_out.read_text(encoding="utf-8")
        if existing_md is not None and existing_md != current_md:
            raise SystemExit(f"{display_path(args.md_out)} is not current")
        if existing_json is None or existing_md is None:
            raise SystemExit("analysis outputs were missing before --check")
        if analysis["status"] != "passed":
            raise SystemExit(f"analysis status is {analysis['status']}")
        print("hard-negative stress matrix analysis outputs are current")
    else:
        print(f"wrote {display_path(args.json_out)}")
        print(f"wrote {display_path(args.md_out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
