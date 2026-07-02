"""Audit final experiment-setting validity for the CCF-C paper route.

This script is no-API and raw-output-free. It reads tracked aggregate audits
only, then writes a paper-facing validity packet that separates supported
results, setting artifacts, and remaining threats.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "reviews" / "final_experiment_setting_validity_audit_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "final_experiment_setting_validity_audit_v0_1.md"

SOURCES = {
    "five_model_synthesis": REPO_ROOT / "data" / "protocols" / "evp8_five_model_synthesis_v0_1.json",
    "v0_2_accept_aware_synthesis": REPO_ROOT
    / "data"
    / "protocols"
    / "evp8_deepseek_qwen_accept_v0_2_prompt_v0_2_full_synthesis.json",
    "v0_3_qwen_synthesis": REPO_ROOT / "data" / "protocols" / "evp8_qwen_first_main_v0_3_prompt_v0_2_full_synthesis.json",
    "v0_3_qwen_label_conditioned": REPO_ROOT
    / "data"
    / "reviews"
    / "evp8_qwen_first_main_v0_3_prompt_v0_2_label_conditioned_summary.json",
    "e6_no_verdict_comparison": REPO_ROOT / "data" / "reviews" / "evp8_e6_no_verdict_ablation_comparison.json",
    "hard_claim_traceability": REPO_ROOT / "data" / "reviews" / "evp8_hard_paper_claim_traceability_v0_1.json",
    "hard_tool_contestation_audit": REPO_ROOT / "data" / "protocols" / "evp8_hard_tool_contestation_result_audit_v0_1.json",
    "realistic_hardneg_gate": REPO_ROOT
    / "data"
    / "protocols"
    / "evp8_realistic_hardneg_combined_generation_gate_with_full_file_v0_1.json",
    "realistic_hardneg_claim_decision": REPO_ROOT
    / "data"
    / "protocols"
    / "evp8_realistic_hardneg_paper_claim_decision_packet_v0_1.json",
    "prompt_boundary_v0_3": REPO_ROOT / "data" / "protocols" / "evp8_prompt_boundary_audit_v0_3_qwen_first_prompt_v0_2.json",
}
TEXT_SOURCES = {
    "leakage_policy": REPO_ROOT / "docs" / "experiments" / "leakage_policy.md",
}


def display_path(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{display_path(path)} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def all_checks_passed(items: list[dict[str, Any]]) -> bool:
    return all(bool(item.get("passed")) for item in items)


def source_checks_passed(data: dict[str, Any]) -> bool:
    checks = data.get("checks")
    if not isinstance(checks, list):
        return False
    return all_checks_passed([item for item in checks if isinstance(item, dict)])


def build_audit() -> dict[str, Any]:
    data = {name: read_json(path) for name, path in SOURCES.items()}

    five = data["five_model_synthesis"]
    v02 = data["v0_2_accept_aware_synthesis"]
    v03 = data["v0_3_qwen_synthesis"]
    qwen_label = data["v0_3_qwen_label_conditioned"]
    no_verdict = data["e6_no_verdict_comparison"]
    hard_claim = data["hard_claim_traceability"]
    hard_contest = data["hard_tool_contestation_audit"]
    realistic_gate = data["realistic_hardneg_gate"]
    prompt_boundary = data["prompt_boundary_v0_3"]

    hard_gate = realistic_gate.get("hard_negative_gate") or {}
    hard_readiness = realistic_gate.get("readiness") or {}
    qwen_method = qwen_label.get("method") or {}

    checks = [
        check("api_call_not_attempted_by_validity_audit", True, False),
        check("raw_model_outputs_not_read_by_validity_audit", True, False),
        check("patch_text_not_read_by_validity_audit", True, False),
        check("prompt_text_not_read_by_validity_audit", True, False),
        check("five_model_synthesis_passed", five.get("later_model_audit_status") == "passed", five.get("later_model_audit_status")),
        check("five_model_all_source_checks_passed", source_checks_passed(five), len(five.get("checks", []))),
        check("v0_2_accept_aware_synthesis_passed", v02.get("audit_status") == "passed", v02.get("audit_status")),
        check("v0_3_qwen_synthesis_passed", v03.get("audit_status") == "passed", v03.get("audit_status")),
        check("qwen_label_conditioned_matrix_complete", source_checks_passed(qwen_label), len(qwen_label.get("checks", []))),
        check(
            "qwen_hidden_labels_joined_after_execution",
            qwen_method.get("api_call_attempted") is False
            and qwen_method.get("reasoning_content_used") is False
            and qwen_method.get("raw_response_content_stored") is False,
            qwen_method,
        ),
        check("e6_no_verdict_comparison_checks_passed", source_checks_passed(no_verdict), len(no_verdict.get("checks", []))),
        check("hard_claim_traceability_passed", hard_claim.get("passed") is True, hard_claim.get("passed")),
        check("hard_tool_contestation_audit_passed", hard_contest.get("audit_status") == "passed", hard_contest.get("audit_status")),
        check(
            "hard_tool_contestation_complete_coverage",
            all((row.get("complete_candidate_coverage") is True) for row in (hard_contest.get("models") or {}).values()),
            list((hard_contest.get("models") or {}).keys()),
        ),
        check("realistic_hardneg_gate_analysis_passed", realistic_gate.get("analysis_status") == "passed", realistic_gate.get("analysis_status")),
        check("realistic_hardneg_gate_not_overclaimed", hard_gate.get("passed") is False and hard_readiness.get("ready_for_verifier_api") is False, hard_readiness),
        check(
            "prompt_boundary_v0_3_no_rendered_prompt_stored",
            prompt_boundary.get("prompt_boundary_audit_status") == "passed"
            and prompt_boundary.get("rendered_prompt_text_stored") is False
            and prompt_boundary.get("api_call_attempted") is False
            and prompt_boundary.get("evidence_packets_generated") is False,
            {
                "prompt_boundary_audit_status": prompt_boundary.get("prompt_boundary_audit_status"),
                "api_call_attempted": prompt_boundary.get("api_call_attempted"),
                "rendered_prompt_text_stored": prompt_boundary.get("rendered_prompt_text_stored"),
                "evidence_packets_generated": prompt_boundary.get("evidence_packets_generated"),
            },
        ),
    ]

    supported_results = [
        {
            "id": "evp8_five_model_decision_patterns",
            "status": "supported_descriptive",
            "evidence": ["five_model_synthesis"],
            "allowed_wording": "On the frozen EVP-8 packet set, five models show descriptive per-level decision-pattern differences.",
            "setting_validity": "run/parse/model coverage passed; raw outputs are summarized through tracked aggregate audits.",
        },
        {
            "id": "accept_aware_v0_2_v0_3_repair",
            "status": "supported_as_setting_repair",
            "evidence": ["v0_2_accept_aware_synthesis", "v0_3_qwen_synthesis", "v0_3_qwen_label_conditioned"],
            "allowed_wording": "Accept-aware construction repairs the earlier zero-accept artifact and allows descriptive recall/false-accept analysis.",
            "setting_validity": "matrix completeness, no duplicate/missing cells, and post-execution label-conditioned analysis pass.",
        },
        {
            "id": "verdict_dependence_and_no_verdict_ablation",
            "status": "supported_qualified",
            "evidence": ["e6_no_verdict_comparison"],
            "allowed_wording": "Removing verdict-like fields changes model behavior, with model-dependent risk-control tradeoffs.",
            "setting_validity": "same frozen 98-candidate matrix is checked across rule-only, E6-full, and E6-no-verdict rows.",
        },
        {
            "id": "tool_contestation_risk_triage",
            "status": "supported_qualified",
            "evidence": ["hard_claim_traceability", "hard_tool_contestation_audit"],
            "allowed_wording": "Tool-contestation shifts known false accepts mostly toward escalation, supporting risk triage rather than strict semantic correction.",
            "setting_validity": "47-candidate coverage is complete and strict correction remains separated from escalation.",
        },
        {
            "id": "realistic_hardneg_source_acquisition_boundary",
            "status": "supported_negative_boundary",
            "evidence": ["realistic_hardneg_gate", "realistic_hardneg_claim_decision"],
            "allowed_wording": "The fresh realistic branch currently supports a two-project source-acquisition/gate-readiness negative result, not a verifier-ready main experiment.",
            "setting_validity": "tracked gate has 26/30 visible-pass/hidden-fail cases across two projects and keeps verifier API blocked.",
        },
    ]

    setting_artifacts_controlled = [
        {
            "risk": "v0.1 zero-accept artifact",
            "status": "controlled_by_repair_and_claim_boundary",
            "evidence": ["v0_2_accept_aware_synthesis", "v0_3_qwen_synthesis"],
            "paper_handling": "Do not use v0.1 zero-accept as the main behavioral claim; use it only as protocol history.",
        },
        {
            "risk": "hidden evaluator leakage",
            "status": "controlled_by_packet_boundary_and_post_execution_join",
            "evidence": ["leakage_policy", "qwen_label_conditioned_method", "prompt_boundary_v0_3"],
            "paper_handling": "State that hidden labels are evaluator-only and used after execution for analysis.",
        },
        {
            "risk": "verdict anchoring",
            "status": "measured_not_eliminated",
            "evidence": ["e6_no_verdict_comparison", "hard_claim_traceability"],
            "paper_handling": "Report with-verdict and no-verdict/tool-contestation separately.",
        },
        {
            "risk": "escalation counted as correction",
            "status": "controlled_by_metric_boundary",
            "evidence": ["hard_claim_traceability", "hard_tool_contestation_audit"],
            "paper_handling": "Keep strict correction and safe handling separate.",
        },
        {
            "risk": "third-project external-validity gap",
            "status": "not_controlled_must_be_threat",
            "evidence": ["realistic_hardneg_gate"],
            "paper_handling": "Write as limitation and negative source-acquisition result unless the gate is later repaired.",
        },
    ]

    forbidden_claims = [
        "LLMs are reliable autonomous patch correctness verifiers.",
        "More visible evidence monotonically improves correctness verification.",
        "Escalation is equivalent to strict correction.",
        "The fresh realistic hard-negative branch is verifier-ready across three projects.",
        "The controlled EVP-8 or EVP-8-HARD cohorts prove broad external validity for real agent patch distributions.",
    ]

    remaining_threats = [
        {
            "threat": "Cohort size and project diversity remain limited for broad generalization.",
            "severity": "medium_for_ccf_c_high_for_ccf_b",
            "required_paper_response": "Scope the claim to candidate patch verification and report project/task counts explicitly.",
        },
        {
            "threat": "Realistic hard-negative third-project gate remains blocked.",
            "severity": "medium",
            "required_paper_response": "Use it as a source-acquisition negative result, not as main verifier evidence.",
        },
        {
            "threat": "Prompt and evidence formatting can influence model policy behavior.",
            "severity": "medium",
            "required_paper_response": "Present results as evidence-conditioned risk behavior, not intrinsic semantic proof.",
        },
        {
            "threat": "Some historical experiments are diagnostic rather than paper-facing.",
            "severity": "low_if_claim_map_is_followed",
            "required_paper_response": "Keep historical versions in appendix/method provenance and avoid mixing them into main claims.",
        },
    ]

    overall_status = "passed_with_bounded_claims" if all_checks_passed(checks) else "failed"
    return {
        "audit_id": "final_experiment_setting_validity_audit_v0_1",
        "date": "2026-07-03",
        "scope": {
            "api_call_attempted": False,
            "raw_model_outputs_read": False,
            "prompt_text_read": False,
            "patch_text_read": False,
            "experiment_results_modified": False,
        },
        "inputs": {
            **{name: display_path(path) for name, path in SOURCES.items()},
            **{name: display_path(path) for name, path in TEXT_SOURCES.items()},
        },
        "checks": checks,
        "overall_status": overall_status,
        "paper_target": "stable CCF-C submission",
        "bottom_line": (
            "The current results are usable as real bounded evidence for evidence-conditioned risk behavior, "
            "provided the paper does not claim reliable autonomous correctness verification."
        ),
        "supported_results": supported_results,
        "setting_artifacts_controlled": setting_artifacts_controlled,
        "remaining_threats": remaining_threats,
        "forbidden_claims": forbidden_claims,
        "recommended_next_action": "Freeze this validity boundary into the manuscript claim map and threats-to-validity section before further experiments.",
    }


def write_markdown(path: Path, audit: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Final Experiment-Setting Validity Audit v0.1",
        "",
        "Date: 2026-07-03",
        "",
        "This is a no-API, raw-output-free validity packet for the stable CCF-C paper route.",
        "It audits whether the current results can be treated as real bounded evidence rather",
        "than artifacts of prompt, label, leakage, parser, or post-hoc setting errors.",
        "",
        "## Bottom Line",
        "",
        f"- overall status: `{audit['overall_status']}`",
        f"- paper target: `{audit['paper_target']}`",
        f"- conclusion: {audit['bottom_line']}",
        "",
        "## Checks",
        "",
        "| check | passed | detail |",
        "| --- | ---: | --- |",
    ]
    for item in audit["checks"]:
        lines.append(f"| `{item['check']}` | {str(item['passed']).lower()} | `{item['detail']}` |")

    lines += ["", "## Supported Results", "", "| id | status | allowed wording | setting validity |", "| --- | --- | --- | --- |"]
    for row in audit["supported_results"]:
        lines.append(f"| `{row['id']}` | `{row['status']}` | {row['allowed_wording']} | {row['setting_validity']} |")

    lines += ["", "## Setting Artifacts And Controls", "", "| risk | status | paper handling |", "| --- | --- | --- |"]
    for row in audit["setting_artifacts_controlled"]:
        lines.append(f"| {row['risk']} | `{row['status']}` | {row['paper_handling']} |")

    lines += ["", "## Remaining Threats", "", "| threat | severity | required paper response |", "| --- | --- | --- |"]
    for row in audit["remaining_threats"]:
        lines.append(f"| {row['threat']} | `{row['severity']}` | {row['required_paper_response']} |")

    lines += ["", "## Forbidden Claims", ""]
    for claim in audit["forbidden_claims"]:
        lines.append(f"- {claim}")

    lines += [
        "",
        "## Next Action",
        "",
        audit["recommended_next_action"],
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audit = build_audit()
    write_json(args.out_json, audit)
    write_markdown(args.out_md, audit)
    if args.check and audit["overall_status"] == "failed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
