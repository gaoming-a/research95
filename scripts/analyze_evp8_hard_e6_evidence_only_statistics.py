"""Statistical boundary for EVP-8-HARD E6 evidence-only results.

This script reads only tracked raw-output-free summaries. It adds interval
estimates around the hard-case evidence-only result so the paper claim does not
rest on point estimates alone.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT = REPO_ROOT / "data" / "protocols" / "evp8_hard_e6_evidence_only_result_audit_v0_1.json"
DEFAULT_OPPORTUNITY = REPO_ROOT / "data" / "reviews" / "evp8_hard_e6_evidence_only_opportunity_analysis_v0_1.json"
DEFAULT_OUT_JSON = REPO_ROOT / "data" / "reviews" / "evp8_hard_e6_evidence_only_statistical_boundary_v0_1.json"
DEFAULT_OUT_MD = REPO_ROOT / "docs" / "experiments" / "evp8_hard_e6_evidence_only_statistical_boundary_v0_1.md"
BOOTSTRAP_SAMPLES = 2000
BOOTSTRAP_SEED = 9508


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{display_path(path)} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def display_path(path: Path) -> str:
    absolute = path if path.is_absolute() else REPO_ROOT / path
    try:
        return absolute.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(absolute)


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> dict[str, Any]:
    if total == 0:
        return {"successes": successes, "n": 0, "point": None, "low": None, "high": None}
    p = successes / total
    denom = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    half_width = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denom
    return {
        "successes": successes,
        "n": total,
        "point": round(p, 6),
        "low": round(max(0.0, center - half_width), 6),
        "high": round(min(1.0, center + half_width), 6),
    }


def quantile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("cannot take quantile of empty values")
    ordered = sorted(values)
    index = (len(ordered) - 1) * q
    low = math.floor(index)
    high = math.ceil(index)
    if low == high:
        return ordered[low]
    return ordered[low] * (high - index) + ordered[high] * (index - low)


def bootstrap_ci(values: list[float], samples: int, seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    if not values:
        return {"n": 0, "point": None, "low": None, "high": None}
    draws: list[float] = []
    for _ in range(samples):
        sample = [rng.choice(values) for _ in values]
        draws.append(sum(sample) / len(sample))
    return {
        "n": len(values),
        "point": round(sum(values) / len(values), 6),
        "low": round(quantile(draws, 0.025), 6),
        "high": round(quantile(draws, 0.975), 6),
    }


def interval_text(interval: dict[str, Any]) -> str:
    if interval.get("point") is None:
        return "n/a"
    return f"{interval['point']:.3f} [{interval['low']:.3f}, {interval['high']:.3f}]"


def whole_cohort_intervals(system: dict[str, Any]) -> dict[str, Any]:
    counts = system["confusion"]["counts"]
    metrics = system["confusion"]["metrics"]
    accepted_total = int(metrics["accepted_total"])
    correct_total = int(metrics["correct_total"])
    incorrect_total = int(metrics["incorrect_total"])
    record_count = int(metrics["record_count"])
    escalated_total = int(counts["escalated_correct"] + counts["escalated_incorrect"])
    return {
        "false_accept_rate": wilson_interval(int(counts["false_accept"]), incorrect_total),
        "accepted_precision": wilson_interval(int(counts["true_accept"]), accepted_total),
        "correct_recall": wilson_interval(int(counts["true_accept"]), correct_total),
        "escalation_rate": wilson_interval(escalated_total, record_count),
    }


def opportunity_intervals(model_summary: dict[str, Any]) -> dict[str, Any]:
    total = int(model_summary["opportunity_record_count"])
    return {
        "safe_handling_rate": wilson_interval(int(model_summary["safe_handled_by_reject_or_escalate"]), total),
        "repeated_accept_rate": wilson_interval(int(model_summary["repeated_accept"]), total),
        "strict_reject_rate": wilson_interval(int(model_summary["strict_corrected_to_reject"]), total),
        "risk_flag_rate": wilson_interval(int(model_summary["nonempty_risk_flags"]), total),
    }


def case_vectors(model_summary: dict[str, Any]) -> dict[str, list[float]]:
    safe: list[float] = []
    repeated_accept: list[float] = []
    risk_flag: list[float] = []
    strict_reject: list[float] = []
    for case in model_summary["cases"]:
        decision = case["new_decision"]
        safe.append(1.0 if decision in {"reject", "escalate"} else 0.0)
        repeated_accept.append(1.0 if decision == "accept" else 0.0)
        strict_reject.append(1.0 if decision == "reject" else 0.0)
        risk_flag.append(1.0 if case.get("risk_flags") else 0.0)
    return {
        "safe_handling_rate": safe,
        "repeated_accept_rate": repeated_accept,
        "strict_reject_rate": strict_reject,
        "risk_flag_rate": risk_flag,
    }


def paired_delta_ci(left: list[float], right: list[float], samples: int, seed: int) -> dict[str, Any]:
    if len(left) != len(right):
        raise ValueError("paired vectors must have the same length")
    return bootstrap_ci([left_value - right_value for left_value, right_value in zip(left, right)], samples, seed)


def build_analysis(args: argparse.Namespace) -> dict[str, Any]:
    audit = read_json(args.audit)
    opportunity = read_json(args.opportunity)
    systems = {"tool-only baseline": audit["tool_only_baseline"], **audit["models"]}
    whole = {name: whole_cohort_intervals(system) for name, system in systems.items()}
    opportunity_models = opportunity["models"]
    opportunity_stats = {
        model_id: {
            "wilson_ci_95": opportunity_intervals(summary),
            "bootstrap_ci_95": {
                metric: bootstrap_ci(values, args.bootstrap_samples, args.bootstrap_seed)
                for metric, values in case_vectors(summary).items()
            },
        }
        for model_id, summary in opportunity_models.items()
    }

    paired_vs_tool = {}
    for model_id, summary in opportunity_models.items():
        vectors = case_vectors(summary)
        tool_vectors = {
            "safe_handling_rate": [0.0] * len(vectors["safe_handling_rate"]),
            "repeated_accept_rate": [1.0] * len(vectors["repeated_accept_rate"]),
            "strict_reject_rate": [0.0] * len(vectors["strict_reject_rate"]),
            "risk_flag_rate": [0.0] * len(vectors["risk_flag_rate"]),
        }
        paired_vs_tool[model_id] = {
            metric: paired_delta_ci(values, tool_vectors[metric], args.bootstrap_samples, args.bootstrap_seed)
            for metric, values in vectors.items()
        }

    qwen_id = "qwen/qwen3.7-max"
    deepseek_id = "deepseek/deepseek-v4-pro"
    paired_deepseek_minus_qwen = {}
    if qwen_id in opportunity_models and deepseek_id in opportunity_models:
        qwen_vectors = case_vectors(opportunity_models[qwen_id])
        deepseek_vectors = case_vectors(opportunity_models[deepseek_id])
        paired_deepseek_minus_qwen = {
            metric: paired_delta_ci(deepseek_vectors[metric], qwen_vectors[metric], args.bootstrap_samples, args.bootstrap_seed)
            for metric in qwen_vectors
        }

    analysis = {
        "analysis_id": "evp8_hard_e6_evidence_only_statistical_boundary_v0_1",
        "cohort_id": "EVP-8-HARD",
        "packet_variant": "e6_evidence_only_no_verdict",
        "inputs": {
            "audit": display_path(args.audit),
            "opportunity": display_path(args.opportunity),
        },
        "method": {
            "wilson_confidence_level": 0.95,
            "bootstrap_confidence_level": 0.95,
            "bootstrap_unit": "opportunity_candidate",
            "bootstrap_samples": args.bootstrap_samples,
            "bootstrap_seed": args.bootstrap_seed,
            "raw_model_outputs_read": False,
            "api_call_attempted": False,
        },
        "whole_cohort_wilson_ci_95": whole,
        "opportunity_set_wilson_and_bootstrap_ci_95": opportunity_stats,
        "opportunity_paired_delta_vs_tool_bootstrap_ci_95": paired_vs_tool,
        "opportunity_paired_delta_deepseek_minus_qwen_bootstrap_ci_95": paired_deepseek_minus_qwen,
        "claim_boundary": (
            "Intervals are wide because the hard-case cohort has 47 candidates "
            "and the primary opportunity set has only nine known false accepts. "
            "Use these results as evidence of behavior shift and triage tradeoff, "
            "not as a reliability guarantee."
        ),
        "checks": [
            {"check": "audit_passed", "passed": audit.get("audit_status") == "passed", "detail": audit.get("audit_status")},
            {
                "check": "opportunity_analysis_passed",
                "passed": opportunity.get("analysis_status") == "passed",
                "detail": opportunity.get("analysis_status"),
            },
            {"check": "api_call_not_attempted_by_statistics", "passed": True, "detail": False},
            {"check": "raw_model_outputs_not_read", "passed": True, "detail": False},
        ],
    }
    return analysis


def write_markdown(path: Path, analysis: dict[str, Any]) -> None:
    lines = [
        "# EVP-8-HARD E6 Evidence-Only Statistical Boundary v0.1",
        "",
        "- API call attempted: `false`",
        "- Raw model outputs read: `false`",
        f"- Bootstrap samples: `{analysis['method']['bootstrap_samples']}`",
        f"- Bootstrap seed: `{analysis['method']['bootstrap_seed']}`",
        "",
        "## Whole-Cohort Wilson 95% CI",
        "",
        "| System | false accept rate | accepted precision | correct recall | escalation rate |",
        "|---|---:|---:|---:|---:|",
    ]
    for system, intervals in analysis["whole_cohort_wilson_ci_95"].items():
        lines.append(
            "| {system} | {far} | {precision} | {recall} | {escalation} |".format(
                system=system,
                far=interval_text(intervals["false_accept_rate"]),
                precision=interval_text(intervals["accepted_precision"]),
                recall=interval_text(intervals["correct_recall"]),
                escalation=interval_text(intervals["escalation_rate"]),
            )
        )
    lines.extend(
        [
            "",
            "## Nine-Case Opportunity Set",
            "",
            "| Model | safe handling Wilson 95% CI | repeated accept Wilson 95% CI | strict reject Wilson 95% CI | safe delta vs tool bootstrap 95% CI |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    opp = analysis["opportunity_set_wilson_and_bootstrap_ci_95"]
    paired = analysis["opportunity_paired_delta_vs_tool_bootstrap_ci_95"]
    for model_id, stats in sorted(opp.items()):
        wilson = stats["wilson_ci_95"]
        lines.append(
            "| {model} | {safe} | {repeat} | {strict} | {delta} |".format(
                model=model_id,
                safe=interval_text(wilson["safe_handling_rate"]),
                repeat=interval_text(wilson["repeated_accept_rate"]),
                strict=interval_text(wilson["strict_reject_rate"]),
                delta=interval_text(paired[model_id]["safe_handling_rate"]),
            )
        )
    if analysis["opportunity_paired_delta_deepseek_minus_qwen_bootstrap_ci_95"]:
        delta = analysis["opportunity_paired_delta_deepseek_minus_qwen_bootstrap_ci_95"]
        lines.extend(
            [
                "",
                "## DeepSeek Minus Qwen on Opportunity Set",
                "",
                "| Metric | paired bootstrap 95% CI |",
                "|---|---:|",
            ]
        )
        for metric, interval in sorted(delta.items()):
            lines.append(f"| {metric} | {interval_text(interval)} |")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            analysis["claim_boundary"],
            "",
            "## Checks",
            "",
        ]
    )
    lines.extend(f"- `{check['check']}`: `{str(check['passed']).lower()}`" for check in analysis["checks"])
    lines.append("")
    write_text(path, "\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--opportunity", type=Path, default=DEFAULT_OPPORTUNITY)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    parser.add_argument("--bootstrap-samples", type=int, default=BOOTSTRAP_SAMPLES)
    parser.add_argument("--bootstrap-seed", type=int, default=BOOTSTRAP_SEED)
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
    if args.check and not all(check["passed"] for check in analysis["checks"]):
        raise SystemExit("EVP-8-HARD evidence-only statistical boundary blocked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
