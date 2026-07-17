# ruff: noqa: E402
"""Write a raw-output-free run packet for Gemini repaired EVP-8 v0.3.

The packet links readiness, dry-run, API-run, label-conditioned analysis,
sanitized false-accept analysis, and manuscript-audit artifacts for the
user-authorized Gemini repaired run. It never reads ignored raw responses.
"""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/write_evp8_gemini_repaired_v0_3_run_packet.py")

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON_OUT = (
    REPO_ROOT / "data" / "protocols" / "evp8_gemini_repaired_v0_3_run_packet.json"
)
DEFAULT_MD_OUT = (
    REPO_ROOT / "docs" / "experiments" / "evp8_gemini_repaired_v0_3_run_packet.md"
)

ARTIFACTS = {
    "config_example": REPO_ROOT / "configs" / "evp8_gemini_repaired_v0_3.example.json",
    "preflight": REPO_ROOT
    / "data"
    / "protocols"
    / "evp8_gemini_repaired_v0_3_preflight_summary.json",
    "smoke_check_only": REPO_ROOT
    / "data"
    / "protocols"
    / "evp8_gemini_repaired_v0_3_smoke_check_only.json",
    "full_check_only": REPO_ROOT
    / "data"
    / "protocols"
    / "evp8_gemini_repaired_v0_3_full_check_only.json",
    "smoke_summary": REPO_ROOT
    / "data"
    / "reviews"
    / "evp8_gemini_repaired_v0_3_prompt_v0_2_google_gemini-2.5-flash_smoke_summary.json",
    "full_summary": REPO_ROOT
    / "data"
    / "reviews"
    / "evp8_gemini_repaired_v0_3_prompt_v0_2_google_gemini-2.5-flash_full_summary.json",
    "label_conditioned_summary": REPO_ROOT
    / "data"
    / "reviews"
    / "evp8_gemini_repaired_v0_3_prompt_v0_2_label_conditioned_summary.json",
    "label_conditioned_md": REPO_ROOT
    / "docs"
    / "experiments"
    / "evp8_gemini_repaired_v0_3_prompt_v0_2_label_conditioned_summary.md",
    "false_accept_case_analysis": REPO_ROOT
    / "data"
    / "reviews"
    / "apsec_false_accept_case_analysis_v0_2.json",
    "apsec_manuscript": REPO_ROOT / "docs" / "paper" / "apsec_technical_track_rewrite_v0_1.md",
    "apsec_audit": REPO_ROOT / "data" / "reviews" / "apsec_manuscript_rewrite_audit_v0_1.json",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def check_detail(summary: dict[str, Any], check_name: str) -> Any:
    for row in summary.get("checks", []):
        if row.get("check") == check_name:
            return row.get("detail")
    return None


def evidence_row(label_summary: dict[str, Any], level: str) -> dict[str, Any]:
    row = label_summary["per_evidence_level"][level]
    confusion = row["confusion_counts"]
    return {
        "level": level,
        "accept": row["decision_counts"].get("accept", 0),
        "reject": row["decision_counts"].get("reject", 0),
        "escalate": row["decision_counts"].get("escalate", 0),
        "correct_accept": confusion["true_accept"],
        "false_accept": confusion["false_accept"],
        "accepted_precision": row["accepted_precision"],
        "correct_recall": row["correct_recall"],
        "false_accept_rate": row["false_accept_rate"],
        "escalation_rate": row["escalation_rate"],
    }


def pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.2f}%"


def build_packet() -> dict[str, Any]:
    missing = [rel(path) for path in ARTIFACTS.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing artifacts: {missing}")

    preflight = read_json(ARTIFACTS["preflight"])
    smoke_check = read_json(ARTIFACTS["smoke_check_only"])
    full_check = read_json(ARTIFACTS["full_check_only"])
    smoke_summary = read_json(ARTIFACTS["smoke_summary"])
    full_summary = read_json(ARTIFACTS["full_summary"])
    label_summary = read_json(ARTIFACTS["label_conditioned_summary"])
    false_accept_cases = read_json(ARTIFACTS["false_accept_case_analysis"])
    apsec_audit = read_json(ARTIFACTS["apsec_audit"])
    e6 = evidence_row(label_summary, "E6")

    checks = [
        {
            "check": "preflight_strict_ready",
            "passed": bool(preflight.get("ready_for_user_execute_command")),
            "detail": preflight.get("ready_for_user_execute_command"),
        },
        {
            "check": "smoke_check_only_passed",
            "passed": smoke_check.get("check_only_status") == "passed"
            and smoke_check.get("api_call_attempted") is False,
            "detail": smoke_check.get("check_only_status"),
        },
        {
            "check": "full_check_only_passed",
            "passed": full_check.get("check_only_status") == "passed"
            and full_check.get("api_call_attempted") is False,
            "detail": full_check.get("check_only_status"),
        },
        {
            "check": "smoke_api_passed",
            "passed": smoke_summary.get("smoke_gate") == "passed"
            and smoke_summary.get("parse_valid_count") == smoke_summary.get("review_count"),
            "detail": {
                "smoke_gate": smoke_summary.get("smoke_gate"),
                "parse_valid_count": smoke_summary.get("parse_valid_count"),
                "review_count": smoke_summary.get("review_count"),
            },
        },
        {
            "check": "full_api_passed",
            "passed": full_summary.get("run_gate") == "passed"
            and full_summary.get("first_batch_full_gate") == "passed"
            and full_summary.get("parse_valid_count") == full_summary.get("review_count"),
            "detail": {
                "run_gate": full_summary.get("run_gate"),
                "first_batch_full_gate": full_summary.get("first_batch_full_gate"),
                "parse_valid_count": full_summary.get("parse_valid_count"),
                "review_count": full_summary.get("review_count"),
            },
        },
        {
            "check": "cost_gate_passed",
            "passed": full_summary.get("usage_cost_gate") == "passed",
            "detail": {
                "usage_cost_gate": full_summary.get("usage_cost_gate"),
                "total_cost_usd": full_summary.get("cost_summary", {}).get("total_cost_usd"),
            },
        },
        {
            "check": "tracked_summaries_exclude_raw_text",
            "passed": smoke_summary.get("raw_response_text_stored_in_tracked_summary") is False
            and full_summary.get("raw_response_text_stored_in_tracked_summary") is False,
            "detail": {
                "smoke": smoke_summary.get("raw_response_text_stored_in_tracked_summary"),
                "full": full_summary.get("raw_response_text_stored_in_tracked_summary"),
            },
        },
        {
            "check": "label_conditioned_gemini_e6_present",
            "passed": e6["accept"] == 25 and e6["correct_accept"] == 20 and e6["false_accept"] == 5,
            "detail": e6,
        },
        {
            "check": "sanitized_false_accept_analysis_includes_gemini",
            "passed": bool(
                false_accept_cases.get("model_false_accept_counts", {})
                .get("google/gemini-2.5-flash", {})
                .get("total")
                == 5
            ),
            "detail": false_accept_cases.get("model_false_accept_counts", {}).get(
                "google/gemini-2.5-flash"
            ),
        },
        {
            "check": "apsec_three_model_audit_passed",
            "passed": apsec_audit.get("status") == "passed",
            "detail": apsec_audit.get("status"),
        },
    ]

    packet = {
        "packet_id": "evp8_gemini_repaired_v0_3_run_packet",
        "date": "2026-07-06",
        "status": "passed" if all(check["passed"] for check in checks) else "failed",
        "api_boundary": {
            "authorized_model": "google/gemini-2.5-flash",
            "request_model_id": "google/gemini-2.5-flash",
            "provider_route": "openrouter_pinned_exact_model_id",
            "forbidden_without_new_authorization": [
                "Kimi repaired run",
                "Devstral repaired run",
                "new prompt revision API rerun",
                "realistic hard-negative verifier API",
            ],
        },
        "experiment_boundary": {
            "candidate_set_id": full_summary["candidate_set_id"],
            "candidate_count": full_check["candidate_count"],
            "packet_count": full_check["packet_count"],
            "evidence_levels": full_check["model_visible_levels"],
            "prompt_id": check_detail(preflight, "prompt_id"),
            "hidden_labels_joined_after_execution": True,
            "claim_boundary": "three-model repaired Qwen + DeepSeek + Gemini descriptive result, not broad-LLM superiority evidence",
        },
        "checks": checks,
        "execution_summary": {
            "smoke": {
                "review_count": smoke_summary["review_count"],
                "parse_valid_count": smoke_summary["parse_valid_count"],
                "decision_counts": smoke_summary["decision_counts"],
                "cost_usd": smoke_summary["cost_summary"]["total_cost_usd"],
                "raw_responses_out": smoke_summary["raw_responses_out"],
            },
            "full": {
                "review_count": full_summary["review_count"],
                "parse_valid_count": full_summary["parse_valid_count"],
                "decision_counts": full_summary["decision_counts"],
                "decision_counts_by_evidence_level": full_summary[
                    "decision_counts_by_evidence_level"
                ],
                "cost_usd": full_summary["cost_summary"]["total_cost_usd"],
                "raw_responses_out": full_summary["raw_responses_out"],
            },
        },
        "label_conditioned_e6": e6,
        "label_conditioned_by_level": [
            evidence_row(label_summary, level) for level in ["E0", "E1", "E2", "E3", "E4", "E5", "E6"]
        ],
        "tracked_artifacts": {key: rel(path) for key, path in ARTIFACTS.items()},
        "forbidden_claims": [
            "three repaired models prove a universal LLM verifier phenomenon",
            "Gemini is superior to deterministic rule-only evidence",
            "E6 false accepts are solved",
            "the realistic hard-negative branch is verifier-ready",
        ],
        "next_research_gap": [
            "The repaired main result is now three-model, but still not broad-model evidence.",
            "The APSEC package still requires IEEEtran/BibTeX/page-budget conversion before submission.",
        ],
    }
    return packet


def write_md(packet: dict[str, Any], path: Path) -> None:
    e6 = packet["label_conditioned_e6"]
    lines = [
        "# Gemini repaired EVP-8 v0.3 run packet",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Boundary",
        "",
        "- Authorized API model: `google/gemini-2.5-flash` through OpenRouter pinned routing.",
        "- This packet covers the frozen 98-candidate EVP-8 E0-E6 packet set only.",
        "- The paper-facing result is a three-model repaired Qwen + DeepSeek + Gemini descriptive result, not a broad-LLM conclusion.",
        "- Raw responses remain in ignored `outputs/**`; tracked summaries exclude raw response text, rendered prompts, patch diffs, and API keys.",
        "",
        "## Checks",
        "",
        "| check | passed | detail |",
        "| --- | --- | --- |",
    ]
    for check in packet["checks"]:
        lines.append(
            f"| {check['check']} | {str(check['passed']).lower()} | `{json.dumps(check['detail'], ensure_ascii=False)}` |"
        )
    lines.extend(
        [
            "",
            "## Execution Summary",
            "",
            "| scope | records | parse-valid | cost | decisions |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
    )
    for scope in ["smoke", "full"]:
        row = packet["execution_summary"][scope]
        lines.append(
            f"| {scope} | {row['review_count']} | {row['parse_valid_count']} | "
            f"${row['cost_usd']:.9f} | `{json.dumps(row['decision_counts'], ensure_ascii=False)}` |"
        )
    lines.extend(
        [
            "",
            "## Gemini Label-Conditioned E6 Result",
            "",
            "| accept | correct accept | false accept | accepted precision | correct recall | false accept rate | escalation rate |",
            "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            f"| {e6['accept']} | {e6['correct_accept']} | {e6['false_accept']} | "
            f"{pct(e6['accepted_precision'])} | {pct(e6['correct_recall'])} | "
            f"{pct(e6['false_accept_rate'])} | {pct(e6['escalation_rate'])} |",
            "",
            "## Tracked Artifacts",
            "",
        ]
    )
    for key, artifact in packet["tracked_artifacts"].items():
        lines.append(f"- `{key}`: `{artifact}`")
    lines.extend(["", "## Remaining Gaps", ""])
    for gap in packet["next_research_gap"]:
        lines.append(f"- {gap}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    packet = build_packet()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)

    existing_json = args.json_out.read_text(encoding="utf-8") if args.json_out.exists() else None
    existing_md = args.md_out.read_text(encoding="utf-8") if args.md_out.exists() else None

    json_text = json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    args.json_out.write_text(json_text, encoding="utf-8")
    write_md(packet, args.md_out)

    if args.check:
        current_md = args.md_out.read_text(encoding="utf-8")
        if existing_json is not None and existing_json != json_text:
            raise SystemExit(f"{rel(args.json_out)} is not current")
        if existing_md is not None and existing_md != current_md:
            raise SystemExit(f"{rel(args.md_out)} is not current")
        if existing_json is None or existing_md is None:
            raise SystemExit("run packet outputs were missing before --check")
        print("Gemini repaired v0.3 run packet outputs are current")
    else:
        print(f"wrote {rel(args.json_out)}")
        print(f"wrote {rel(args.md_out)}")


if __name__ == "__main__":
    main()
