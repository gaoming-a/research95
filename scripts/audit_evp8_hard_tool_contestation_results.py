"""Raw-output-free audit wrapper for EVP-8-HARD tool-contestation results."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

import audit_evp8_hard_qwen_deepseek_results as base_audit  # noqa: E402


DEFAULT_QWEN_REVIEWS = REPO_ROOT / "data" / "reviews" / "evp8_hard_tool_contestation_qwen_qwen3.7-max_full_reviews.jsonl"
DEFAULT_DEEPSEEK_REVIEWS = REPO_ROOT / "data" / "reviews" / "evp8_hard_tool_contestation_deepseek_deepseek-v4-pro_full_reviews.jsonl"
DEFAULT_OUT = REPO_ROOT / "data" / "protocols" / "evp8_hard_tool_contestation_result_audit_v0_1.json"
FALSE_ACCEPT_ANALYSIS = REPO_ROOT / "data" / "reviews" / "evp8_hard_false_accept_case_analysis_v0_1.json"


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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


def build_waiting_summary() -> dict[str, Any]:
    false_accept = read_json(FALSE_ACCEPT_ANALYSIS)
    expected = [DEFAULT_QWEN_REVIEWS, DEFAULT_DEEPSEEK_REVIEWS]
    return {
        "analysis_id": "evp8_hard_tool_contestation_result_audit_v0_1",
        "audit_status": "waiting_for_model_results",
        "cohort_id": "EVP-8-HARD",
        "packet_variant": "e6_tool_contestation_no_verdict",
        "api_call_attempted": False,
        "raw_model_outputs_read": False,
        "prompt_text_read": False,
        "expected_parsed_reviews": [display_path(path) for path in expected],
        "existing_parsed_reviews": [display_path(path) for path in expected if path.exists()],
        "primary_opportunity_set": {
            "source": display_path(FALSE_ACCEPT_ANALYSIS),
            "repeated_false_accept_count": false_accept.get("repeated_false_accept_count"),
            "primary_metrics": [
                "would_challenge_visible_test_only_accept",
                "visible_tests_sufficient",
                "coverage_concern",
                "decision",
            ],
        },
        "checks": [
            {"check": "api_call_not_attempted_by_audit", "passed": True, "detail": False},
            {"check": "raw_model_outputs_not_read", "passed": True, "detail": False},
            {
                "check": "waiting_until_tool_contestation_parsed_reviews_exist",
                "passed": True,
                "detail": {display_path(path): path.exists() for path in expected},
            },
        ],
        "next_step": "Run authorized EVP-8-HARD tool-contestation Qwen API, then rerun this audit.",
    }


def build_summary(args: argparse.Namespace) -> dict[str, Any]:
    review_paths = [path for path in (DEFAULT_QWEN_REVIEWS, DEFAULT_DEEPSEEK_REVIEWS) if path.exists()]
    if not review_paths:
        return build_waiting_summary()
    namespace = argparse.Namespace(
        evaluator_manifest=base_audit.DEFAULT_EVALUATOR,
        tool_only_baseline=base_audit.DEFAULT_BASELINE,
        parsed_reviews=review_paths,
    )
    summary = base_audit.build_summary(namespace)
    summary["analysis_id"] = "evp8_hard_tool_contestation_result_audit_v0_1"
    summary["packet_variant"] = "e6_tool_contestation_no_verdict"
    summary["tool_contestation_fields"] = {
        "required_in_parsed_reviews": [
            "coverage_concern",
            "visible_tests_sufficient",
            "tool_evidence_reliability",
            "would_challenge_visible_test_only_accept",
            "challenge_reason",
        ]
    }
    summary["primary_opportunity_set"] = {
        "source": display_path(FALSE_ACCEPT_ANALYSIS),
        "repeated_false_accept_count": read_json(FALSE_ACCEPT_ANALYSIS).get("repeated_false_accept_count"),
        "metric": "tool-contestation behavior on nine repeated false accepts",
    }
    if len(review_paths) == 1 and summary["audit_status"] == "passed":
        summary["audit_status"] = "partial_passed_waiting_for_second_model"
        summary["next_step"] = "Use Qwen-only result, or execute DeepSeek after Qwen coverage passes."
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    summary = build_summary(args)
    write_json(args.out if args.out.is_absolute() else REPO_ROOT / args.out, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    if args.check and summary["audit_status"] == "blocked":
        raise SystemExit("tool-contestation result audit blocked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
