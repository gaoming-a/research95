from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

PASSED_SUMMARIES = [
    REPO_ROOT / "data" / "reviews" / "evp8_deepseek_deepseek-v4-pro_full_summary.json",
    REPO_ROOT / "data" / "reviews" / "evp8_qwen_qwen3.7-max_full_summary.json",
    REPO_ROOT / "data" / "reviews" / "evp8_moonshotai_kimi-k2.6_full_summary.json",
    REPO_ROOT / "data" / "reviews" / "evp8_mistralai_devstral-2512_full_summary.json",
    REPO_ROOT / "data" / "reviews" / "evp8_google_gemini-2.5-flash_full_summary.json",
]

BLOCKED_SUMMARIES = [
    REPO_ROOT
    / "outputs"
    / "evp8_phase2_later_models_full"
    / "moonshotai_kimi-k2.6"
    / "blocked_attempt_20260622_default_reasoning"
    / "evp8_moonshotai_kimi-k2.6_full_summary.blocked_default_reasoning.json",
    REPO_ROOT
    / "outputs"
    / "evp8_phase2_later_models_full"
    / "moonshotai_kimi-k2.6"
    / "blocked_attempt_20260622_reasoning_disabled_top_level_429"
    / "evp8_moonshotai_kimi-k2.6_full_summary.blocked_reasoning_disabled_top_level_429.json",
]

RAW_MARKERS = ("raw_" + "response_text", "prompt_" + "text")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def cost_summary(summary: dict[str, Any]) -> dict[str, Any]:
    value = summary.get("cost_summary", {})
    if not isinstance(value, dict):
        return {}
    return value


def row_from_summary(path: Path, summary: dict[str, Any], status: str) -> dict[str, Any]:
    costs = cost_summary(summary)
    return {
        "actual_model_id_counts": summary.get("actual_model_id_counts", {}),
        "actual_provider_counts": summary.get("actual_provider_counts", {}),
        "configured_model_id": summary.get("configured_model_id"),
        "cost_cny": costs.get("total_cost_cny", 0) or 0,
        "cost_observability_counts": costs.get("cost_observability_counts", {}),
        "cost_usd": costs.get("total_cost_usd", 0) or 0,
        "decision_counts": summary.get("decision_counts", {}),
        "invalid_parse_count": summary.get("invalid_parse_count", 0),
        "later_model_full_gate": summary.get("later_model_full_gate"),
        "parse_valid_count": summary.get("parse_valid_count"),
        "path": repo_relative(path),
        "review_count": summary.get("review_count"),
        "run_gate": summary.get("run_gate") or summary.get("first_batch_full_gate") or summary.get("later_model_full_gate"),
        "status": status,
        "unknown_cost_record_count": costs.get("unknown_cost_record_count", 0),
    }


def sum_float(rows: list[dict[str, Any]], key: str) -> float:
    return float(sum(float(row.get(key) or 0) for row in rows))


def build_result(args: argparse.Namespace) -> dict[str, Any]:
    passed_rows = [row_from_summary(path, read_json(path), "passed_result") for path in PASSED_SUMMARIES if path.exists()]
    blocked_rows = [
        row_from_summary(path, read_json(path), "blocked_attempt") for path in BLOCKED_SUMMARIES if path.exists()
    ]

    passed_usd_excluding_qwen = sum_float(
        [row for row in passed_rows if row.get("configured_model_id") != "qwen/qwen3.7-max"], "cost_usd"
    )
    passed_qwen_cny = sum_float(
        [row for row in passed_rows if row.get("configured_model_id") == "qwen/qwen3.7-max"], "cost_cny"
    )
    later_passed_usd = sum_float(
        [
            row
            for row in passed_rows
            if row.get("configured_model_id")
            in {"moonshotai/kimi-k2.6", "mistralai/devstral-2512", "google/gemini-2.5-flash"}
        ],
        "cost_usd",
    )
    blocked_usd = sum_float(blocked_rows, "cost_usd")
    observable_usd_excluding_qwen = passed_usd_excluding_qwen + blocked_usd
    later_observable_usd = later_passed_usd + blocked_usd
    planning_ceiling_usd = float(args.later_model_planning_ceiling_usd)

    checks = [
        {"check": "no_api_call_attempted", "passed": True},
        {"check": "passed_summary_count", "observed": len(passed_rows), "expected": 5, "passed": len(passed_rows) == 5},
        {"check": "blocked_attempt_count_observed", "observed": len(blocked_rows), "passed": len(blocked_rows) >= 2},
        {
            "check": "later_observable_usd_within_planning_ceiling",
            "observed": later_observable_usd,
            "ceiling": planning_ceiling_usd,
            "passed": later_observable_usd <= planning_ceiling_usd,
        },
        {
            "check": "blocked_attempt_cost_requires_freeze",
            "observed": blocked_usd,
            "passed": blocked_usd > 0,
        },
    ]
    result = {
        "api_call_attempted": False,
        "audit_id": "evp8_cost_accounting_summary_v0_1",
        "blocked_attempt_costs": blocked_rows,
        "boundary": (
            "This no-API cost accounting summary reads tracked raw-output-free passed summaries "
            "and ignored raw-output-free blocked-attempt summaries. It does not read raw model responses "
            "or prompt text."
        ),
        "checks": checks,
        "claim_boundary": (
            "Blocked attempts are cost/engineering-risk evidence only. They are not valid model-result records "
            "and must not be included in five-model decision-pattern synthesis."
        ),
        "cost_status": "passed_results_complete_with_blocked_attempt_cost_overrun",
        "decision": {
            "api_freeze": True,
            "next_step": "Do not run more model APIs; proceed to paper tables, figures, claim-boundary audit, and artifact freeze.",
        },
        "ignored_blocked_summaries_read": [row["path"] for row in blocked_rows],
        "later_model_planning_ceiling_usd": planning_ceiling_usd,
        "passed_result_costs": passed_rows,
        "raw_outputs_read": False,
        "model_response_body_read": False,
        "rendered_prompt_body_read": False,
        "totals": {
            "blocked_attempt_usd": blocked_usd,
            "later_model_observable_usd_including_blocked": later_observable_usd,
            "later_model_passed_result_usd": later_passed_usd,
            "passed_qwen_cny": passed_qwen_cny,
            "passed_result_usd_excluding_qwen": passed_usd_excluding_qwen,
            "tracked_plus_blocked_observable_usd_excluding_qwen": observable_usd_excluding_qwen,
        },
    }
    result["passed"] = all(item["passed"] for item in checks if item["check"] != "blocked_attempt_count_observed")
    if contains_raw_markers(result):
        raise SystemExit("cost accounting result contains raw-output field markers")
    return result


def fmt_money(value: Any) -> str:
    try:
        return f"{float(value):.6f}"
    except (TypeError, ValueError):
        return "0.000000"


def render_markdown(result: dict[str, Any]) -> str:
    totals = result["totals"]
    lines = [
        "# EVP-8 Cost Accounting Summary v0.1",
        "",
        result["boundary"],
        "",
        "## Summary",
        "",
        f"- status: `{result['cost_status']}`",
        f"- API freeze: `{str(result['decision']['api_freeze']).lower()}`",
        f"- passed-result USD excluding Qwen: `{fmt_money(totals['passed_result_usd_excluding_qwen'])}`",
        f"- passed Qwen CNY: `{fmt_money(totals['passed_qwen_cny'])}`",
        f"- blocked-attempt USD: `{fmt_money(totals['blocked_attempt_usd'])}`",
        f"- observable USD including blocked attempts, excluding Qwen: `{fmt_money(totals['tracked_plus_blocked_observable_usd_excluding_qwen'])}`",
        f"- later-model observable USD including blocked attempts: `{fmt_money(totals['later_model_observable_usd_including_blocked'])}`",
        f"- later-model planning ceiling USD: `{fmt_money(result['later_model_planning_ceiling_usd'])}`",
        "",
        "## Passed Result Costs",
        "",
        "| model | reviews | valid | USD | CNY | unknown cost |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in result["passed_result_costs"]:
        lines.append(
            f"| `{row['configured_model_id']}` | {row['review_count']} | {row['parse_valid_count']} | "
            f"{fmt_money(row['cost_usd'])} | {fmt_money(row['cost_cny'])} | {row['unknown_cost_record_count']} |"
        )
    lines.extend(["", "## Blocked Attempt Costs", "", "| model | gate | reviews | valid | invalid | USD | unknown cost |", "|---|---|---:|---:|---:|---:|---:|"])
    for row in result["blocked_attempt_costs"]:
        lines.append(
            f"| `{row['configured_model_id']}` | `{row['later_model_full_gate']}` | {row['review_count']} | "
            f"{row['parse_valid_count']} | {row['invalid_parse_count']} | {fmt_money(row['cost_usd'])} | "
            f"{row['unknown_cost_record_count']} |"
        )
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| check | passed | observed |",
            "|---|---:|---:|",
        ]
    )
    for item in result["checks"]:
        observed = item.get("observed", "")
        lines.append(f"| `{item['check']}` | `{str(item['passed']).lower()}` | `{observed}` |")
    lines.extend(["", "## Claim Boundary", "", result["claim_boundary"], ""])
    return "\n".join(lines)


def contains_raw_markers(value: Any) -> bool:
    serialized = json.dumps(value, ensure_ascii=False)
    return any(marker in serialized for marker in RAW_MARKERS)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize EVP-8 passed and blocked-attempt cost accounting.")
    parser.add_argument("--out-json", default="data/reviews/evp8_cost_accounting_summary.json")
    parser.add_argument("--out-md", default="docs/experiments/evp8_cost_accounting_summary.md")
    parser.add_argument("--later-model-planning-ceiling-usd", type=float, default=30.0)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_result(args)
    write_json(Path(args.out_json), result)
    write_text(Path(args.out_md), render_markdown(result))
    print(
        json.dumps(
            {
                "api_freeze": result["decision"]["api_freeze"],
                "blocked_attempt_usd": result["totals"]["blocked_attempt_usd"],
                "cost_status": result["cost_status"],
                "out_json": args.out_json,
                "out_md": args.out_md,
                "passed": result["passed"],
                "passed_result_usd_excluding_qwen": result["totals"]["passed_result_usd_excluding_qwen"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    if args.check and not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
