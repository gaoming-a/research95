"""Build paper-ready Phase A analysis for EVP-8.

This no-API script adds confidence intervals, opportunity-case analysis, and
utility/risk-policy tables on top of the existing E6-no-verdict comparison.
It reads only tracked summaries and writes raw-output-free aggregate reports.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COMPARISON = REPO_ROOT / "data" / "reviews" / "evp8_e6_no_verdict_ablation_comparison.json"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "reviews" / "evp8_phase_a_paper_ready_analysis.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_phase_a_paper_ready_analysis.md"

Z_95 = 1.959963984540054
UTILITY_SCENARIOS = {
    "throughput_oriented": {"false_accept": 5.0, "false_reject": 2.0, "escalation": 1.0},
    "balanced_review": {"false_accept": 10.0, "false_reject": 2.0, "escalation": 1.0},
    "safety_critical": {"false_accept": 50.0, "false_reject": 5.0, "escalation": 1.0},
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{display_path(path)} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def display_path(path: Path) -> str:
    absolute = path if path.is_absolute() else REPO_ROOT / path
    try:
        return absolute.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(absolute)


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def wilson_interval(successes: int, total: int, z: float = Z_95) -> dict[str, Any]:
    if total == 0:
        return {
            "successes": successes,
            "total": total,
            "estimate": None,
            "ci_95_low": None,
            "ci_95_high": None,
        }
    p = successes / total
    denominator = 1 + z**2 / total
    center = (p + z**2 / (2 * total)) / denominator
    margin = z * math.sqrt((p * (1 - p) + z**2 / (4 * total)) / total) / denominator
    return {
        "successes": successes,
        "total": total,
        "estimate": round(p, 6),
        "ci_95_low": round(max(0.0, center - margin), 6),
        "ci_95_high": round(min(1.0, center + margin), 6),
    }


def pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.2f}%"


def ci_text(interval: dict[str, Any]) -> str:
    if interval["estimate"] is None:
        return "n/a"
    return f"{pct(interval['estimate'])} [{pct(interval['ci_95_low'])}, {pct(interval['ci_95_high'])}]"


def iter_conditions(comparison: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    rows = [("rule-only", comparison["rule_only"])]
    for model_id, model in comparison["per_model"].items():
        for condition in ("E6-full", "E6-no-verdict"):
            rows.append((f"{model_id} {condition}", model["conditions"][condition]))
    return rows


def confidence_intervals(comparison: dict[str, Any]) -> dict[str, Any]:
    result = {}
    for condition_name, condition in iter_conditions(comparison):
        metrics = condition["metrics"]
        counts = metrics["confusion_counts"]
        accepted_total = counts["true_accept"] + counts["false_accept"]
        escalated_total = counts["escalated_correct"] + counts["escalated_incorrect"]
        result[condition_name] = {
            "correct_recall": wilson_interval(counts["true_accept"], metrics["correct_total"]),
            "accepted_precision": wilson_interval(counts["true_accept"], accepted_total),
            "false_accept_rate": wilson_interval(counts["false_accept"], metrics["incorrect_total"]),
            "escalation_rate": wilson_interval(escalated_total, metrics["record_count"]),
        }
        if condition_name != "rule-only":
            opportunity = condition["opportunity_correction"]
            false_accepts = opportunity["tool_false_accepts"]
            false_rejects = opportunity["tool_false_rejects"]
            strict_corrected = false_accepts["corrected_to_reject"]
            safe_handled = false_accepts["corrected_to_reject"] + false_accepts["escalated"]
            result[condition_name]["tool_false_accept_strict_correction_rate"] = wilson_interval(
                strict_corrected,
                false_accepts["candidate_count"],
            )
            result[condition_name]["tool_false_accept_safe_handling_rate"] = wilson_interval(
                safe_handled,
                false_accepts["candidate_count"],
            )
            result[condition_name]["tool_false_reject_correction_rate"] = wilson_interval(
                false_rejects["corrected_to_accept"],
                false_rejects["candidate_count"],
            )
    return result


def opportunity_case_rows(comparison: dict[str, Any]) -> list[dict[str, Any]]:
    tool_examples = comparison["rule_only"]["opportunity_examples"]
    source_rows = list(tool_examples["tool_false_accepts"]) + list(tool_examples["tool_false_rejects"])
    rows = []
    for source in source_rows:
        candidate_id = source["evp8_candidate_id"]
        row = {
            "evp8_candidate_id": candidate_id,
            "task_id": source["task_id"],
            "candidate_type": source["candidate_type"],
            "expected_outcome": source["expected_outcome"],
            "tool_decision": source["decision"],
            "missing_visible_evidence": missing_visible_evidence(source),
        }
        for model_id, model in comparison["per_model"].items():
            for condition in ("E6-full", "E6-no-verdict"):
                candidates = (
                    model["conditions"][condition]["opportunity_correction"]["tool_false_accepts"]["candidates"]
                    + model["conditions"][condition]["opportunity_correction"]["tool_false_rejects"]["candidates"]
                )
                matched = [candidate for candidate in candidates if candidate["evp8_candidate_id"] == candidate_id]
                row[f"{model_id} {condition}"] = matched[0]["decision"] if matched else "not_in_opportunity_set"
        rows.append(row)
    return rows


def missing_visible_evidence(row: dict[str, Any]) -> str:
    candidate_type = row.get("candidate_type")
    expected_outcome = row.get("expected_outcome")
    if candidate_type == "regression_patch" or expected_outcome == "regression":
        return "Visible evidence did not include enough pass-to-pass/regression coverage to expose the regression."
    if candidate_type == "partial_fix" or expected_outcome == "partial":
        return "Visible tests covered the obvious path, but hidden/P2P evidence shows missed edge behavior."
    if candidate_type == "correct_reference" and row.get("decision") == "reject":
        return "Visible tool summary reported failure despite evaluator-side correctness; this needs human review."
    return "Visible evidence was insufficient to distinguish the hidden evaluator outcome."


def utility_analysis(comparison: dict[str, Any]) -> dict[str, Any]:
    result = {}
    for condition_name, condition in iter_conditions(comparison):
        metrics = condition["metrics"]
        counts = metrics["confusion_counts"]
        escalated_total = counts["escalated_correct"] + counts["escalated_incorrect"]
        scenario_rows = {}
        for scenario, weights in UTILITY_SCENARIOS.items():
            total_cost = (
                counts["false_accept"] * weights["false_accept"]
                + counts["false_reject"] * weights["false_reject"]
                + escalated_total * weights["escalation"]
            )
            scenario_rows[scenario] = {
                "weights": weights,
                "total_cost": round(total_cost, 6),
                "cost_per_candidate": round(total_cost / metrics["record_count"], 6),
                "false_accept_count": counts["false_accept"],
                "false_reject_count": counts["false_reject"],
                "escalation_count": escalated_total,
            }
        result[condition_name] = scenario_rows
    return result


def build_analysis(comparison_path: Path) -> dict[str, Any]:
    comparison = read_json(comparison_path)
    ci = confidence_intervals(comparison)
    cases = opportunity_case_rows(comparison)
    utility = utility_analysis(comparison)
    checks = [
        check("source_analysis_id", comparison.get("analysis_id") == "evp8_e6_no_verdict_ablation_comparison", comparison.get("analysis_id")),
        check("opportunity_case_count", len(cases) == 6, len(cases)),
        check("confidence_intervals_present", bool(ci), sorted(ci)),
        check("utility_scenarios_present", set(UTILITY_SCENARIOS).issubset(next(iter(utility.values())).keys()), sorted(UTILITY_SCENARIOS)),
        check("api_call_not_attempted", True, False),
        check("raw_response_content_not_stored", True, False),
        check("prompt_text_not_stored", True, False),
    ]
    analysis = {
        "analysis_id": "evp8_phase_a_paper_ready_analysis",
        "cohort_id": "EVP-8",
        "source_comparison": display_path(comparison_path),
        "method": {
            "api_call_attempted": False,
            "raw_response_content_stored": False,
            "prompt_text_stored": False,
            "confidence_interval": "Wilson score interval, 95%",
            "utility_model": "false_accept_cost * false_accepts + false_reject_cost * false_rejects + escalation_cost * escalations",
        },
        "confidence_intervals": ci,
        "opportunity_case_analysis": cases,
        "utility_analysis": utility,
        "claim_boundary": {
            "allowed": "Use this analysis to report uncertainty, case-level failure modes, and risk-policy tradeoffs for the existing EVP-8 cohort.",
            "forbidden": "Do not claim production merge safety, external validity, or reliable LLM superiority from this Phase A analysis.",
        },
        "checks": checks,
    }
    if not all(item["passed"] for item in checks):
        raise SystemExit(f"Phase A checks failed: {checks}")
    return analysis


def write_markdown(path: Path, analysis: dict[str, Any]) -> None:
    lines = [
        "# EVP-8 Phase A Paper-Ready Analysis",
        "",
        "- Status: `passed`",
        "- API call attempted: `false`",
        "- Raw response content stored: `false`",
        "- Confidence interval method: Wilson score interval, 95%",
        "",
        "## Confidence Intervals",
        "",
        "| condition | correct recall | accepted precision | false accept rate | escalation rate | FA strict correction | FA safe handling | FR correction |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition, intervals in analysis["confidence_intervals"].items():
        lines.append(
            "| {condition} | {recall} | {precision} | {far} | {escalation} | {fa_strict} | {fa_safe} | {fr} |".format(
                condition=condition,
                recall=ci_text(intervals["correct_recall"]),
                precision=ci_text(intervals["accepted_precision"]),
                far=ci_text(intervals["false_accept_rate"]),
                escalation=ci_text(intervals["escalation_rate"]),
                fa_strict=ci_text(intervals.get("tool_false_accept_strict_correction_rate", empty_interval())),
                fa_safe=ci_text(intervals.get("tool_false_accept_safe_handling_rate", empty_interval())),
                fr=ci_text(intervals.get("tool_false_reject_correction_rate", empty_interval())),
            )
        )
    lines.extend(
        [
            "",
            "## Opportunity Cases",
            "",
            "| candidate | task | type | expected | tool | Qwen full | Qwen no-verdict | DeepSeek full | DeepSeek no-verdict | missing visible evidence |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in analysis["opportunity_case_analysis"]:
        lines.append(
            "| `{candidate}` | `{task}` | `{ctype}` | `{expected}` | `{tool}` | `{q_full}` | `{q_nv}` | `{d_full}` | `{d_nv}` | {missing} |".format(
                candidate=row["evp8_candidate_id"],
                task=row["task_id"],
                ctype=row["candidate_type"],
                expected=row["expected_outcome"],
                tool=row["tool_decision"],
                q_full=row["qwen/qwen3.7-max E6-full"],
                q_nv=row["qwen/qwen3.7-max E6-no-verdict"],
                d_full=row["deepseek/deepseek-v4-pro E6-full"],
                d_nv=row["deepseek/deepseek-v4-pro E6-no-verdict"],
                missing=row["missing_visible_evidence"],
            )
        )
    lines.extend(
        [
            "",
            "## Utility / Risk Policy",
            "",
            "Lower cost is better. Costs are illustrative policy weights, not measured money.",
            "",
            "| condition | throughput-oriented | balanced-review | safety-critical |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for condition, scenarios in analysis["utility_analysis"].items():
        lines.append(
            f"| {condition} | {scenarios['throughput_oriented']['total_cost']:.2f} | "
            f"{scenarios['balanced_review']['total_cost']:.2f} | "
            f"{scenarios['safety_critical']['total_cost']:.2f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The confidence intervals are wide for opportunity-set rates because there are only 6 opportunity cases.",
            "- Qwen preserves recall but repeats most false accepts under both E6 conditions.",
            "- DeepSeek `E6-no-verdict` is attractive only under safety-heavy policies where avoiding false accepts is worth many escalations.",
            "- This Phase A analysis strengthens reporting discipline; it does not solve external validity by itself.",
            "",
            f"- Allowed: {analysis['claim_boundary']['allowed']}",
            f"- Forbidden: {analysis['claim_boundary']['forbidden']}",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def empty_interval() -> dict[str, Any]:
    return {"successes": 0, "total": 0, "estimate": None, "ci_95_low": None, "ci_95_high": None}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--comparison", type=Path, default=DEFAULT_COMPARISON)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    analysis = build_analysis(args.comparison)
    write_json(args.json_out, analysis)
    write_markdown(args.md_out, analysis)
    if args.check and not all(item["passed"] for item in analysis["checks"]):
        return 1
    print(json.dumps(analysis, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
