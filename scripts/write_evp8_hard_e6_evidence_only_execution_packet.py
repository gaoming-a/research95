"""Write the no-API EVP-8-HARD E6 evidence-only execution packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "evp8_hard_e6_evidence_only.local.json"
EXAMPLE_CONFIG_PATH = REPO_ROOT / "configs" / "evp8_hard_e6_evidence_only.example.json"
CHECK_ONLY_PATH = REPO_ROOT / "data" / "protocols" / "evp8_hard_e6_evidence_only_check_only_v0_1.json"
FALSE_ACCEPT_ANALYSIS_PATH = REPO_ROOT / "data" / "reviews" / "evp8_hard_false_accept_case_analysis_v0_1.json"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "protocols" / "evp8_hard_e6_evidence_only_execution_packet_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_hard_e6_evidence_only_execution_packet_v0_1.md"


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


def local_config_is_ignored_boundary(path: Path) -> bool:
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    return path.parent == REPO_ROOT / "configs" and path.name.endswith(".local.json") and "configs/*.local.json" in gitignore


def output_paths(model_slug: str) -> dict[str, str]:
    safe_model = model_slug.replace("/", "_")
    return {
        "ignored_raw_responses": f"outputs/evp8_hard_e6_evidence_only_full/{safe_model}/raw_responses.jsonl",
        "tracked_summary": f"data/reviews/evp8_hard_e6_evidence_only_{safe_model}_full_summary.json",
        "tracked_parsed_reviews": f"data/reviews/evp8_hard_e6_evidence_only_{safe_model}_full_reviews.jsonl",
    }


def output_absence(outputs_by_model: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for model_id, outputs in outputs_by_model.items():
        for output_kind, path_value in outputs.items():
            path = REPO_ROOT / path_value
            checks.append(
                {
                    "model_id": model_id,
                    "output_kind": output_kind,
                    "path": path_value,
                    "exists": path.exists(),
                    "passed": not path.exists(),
                }
            )
    return checks


def build_packet() -> dict[str, Any]:
    example_config = read_json(EXAMPLE_CONFIG_PATH)
    check_only = read_json(CHECK_ONLY_PATH)
    false_accept_analysis = read_json(FALSE_ACCEPT_ANALYSIS_PATH)
    outputs_by_model = {
        "qwen/qwen3.7-max": output_paths("qwen/qwen3.7-max"),
        "deepseek/deepseek-v4-pro": output_paths("deepseek/deepseek-v4-pro"),
    }
    absence = output_absence(outputs_by_model)
    removed_fields = [
        "rule_based_visible_merge_gate_decision",
        "rule_based_visible_merge_gate_reasons",
        "source_decision",
    ]
    checks = [
        check("example_config_exists", EXAMPLE_CONFIG_PATH.exists(), display_path(EXAMPLE_CONFIG_PATH)),
        check("local_config_path_boundary", local_config_is_ignored_boundary(CONFIG_PATH), display_path(CONFIG_PATH)),
        check("example_config_not_authorized", example_config.get("api_execution_authorized") is False, example_config.get("api_execution_authorized")),
        check("check_only_passed", check_only.get("check_only_status") == "passed", check_only.get("check_only_status")),
        check("packet_variant_is_evidence_only", check_only.get("packet_variant") == "e6_evidence_only_no_verdict", check_only.get("packet_variant")),
        check("candidate_count_47", check_only.get("candidate_count") == 47, check_only.get("candidate_count")),
        check("verdict_fields_removed", check_only.get("removed_verdict_fields") == removed_fields, check_only.get("removed_verdict_fields")),
        check("check_only_no_api", check_only.get("api_call_attempted") is False, check_only.get("api_call_attempted")),
        check("check_only_no_raw_outputs", check_only.get("raw_outputs_generated") is False, check_only.get("raw_outputs_generated")),
        check("false_accept_analysis_ready", false_accept_analysis.get("repeated_false_accept_count") == 9, false_accept_analysis.get("repeated_false_accept_count")),
        check("expected_evidence_only_outputs_absent", all(item["passed"] for item in absence), absence),
    ]
    packet_status = "ready" if all(item["passed"] for item in checks) else "blocked"
    return {
        "packet_id": "evp8_hard_e6_evidence_only_execution_packet_v0_1",
        "cohort_id": "EVP-8-HARD",
        "packet_status": packet_status,
        "packet_variant": "e6_evidence_only_no_verdict",
        "api_call_attempted": False,
        "raw_outputs_generated": False,
        "rendered_prompt_text_stored": False,
        "execution_authorized_by_packet": False,
        "requires_explicit_user_command": True,
        "local_config": display_path(CONFIG_PATH),
        "example_config": display_path(EXAMPLE_CONFIG_PATH),
        "check_only_summary": display_path(CHECK_ONLY_PATH),
        "primary_opportunity_set": {
            "source": display_path(FALSE_ACCEPT_ANALYSIS_PATH),
            "repeated_false_accept_count": false_accept_analysis.get("repeated_false_accept_count"),
            "evaluation_rule": "measure whether the nine repeated false accepts change from accept to reject/escalate",
        },
        "removed_verdict_fields": removed_fields,
        "retained_evidence_boundary": [
            "issue_patch_seed",
            "patch_surface_map",
            "patch_application_static_status",
            "visible_fail_to_pass_test_evidence",
            "visible_pass_to_pass_regression_evidence",
            "broader_visible_tool_diagnostics",
            "visible_tool_summary_counts_and_contradictions_without_verdict",
        ],
        "planned_calls_per_model": 47,
        "execute_commands_after_explicit_user_authorization": [
            {
                "step": "qwen_evidence_only_first",
                "model_id": "qwen/qwen3.7-max",
                "command": "python scripts\\run_evp8_hard_qwen_deepseek.py --execute --config configs\\evp8_hard_e6_evidence_only.local.json --model-id qwen/qwen3.7-max",
                "outputs": outputs_by_model["qwen/qwen3.7-max"],
                "proceed_if": "summary.run_gate == passed and parsed reviews contain exactly 47 candidate decisions",
            },
            {
                "step": "audit_after_qwen_evidence_only",
                "command": "python scripts\\audit_evp8_hard_e6_evidence_only_results.py --out data\\protocols\\evp8_hard_e6_evidence_only_result_audit_v0_1.json",
                "outputs": {
                    "tracked_result_audit": "data/protocols/evp8_hard_e6_evidence_only_result_audit_v0_1.json"
                },
                "proceed_if": "audit status is passed or Qwen-only partial with complete Qwen coverage",
            },
            {
                "step": "deepseek_evidence_only_second",
                "model_id": "deepseek/deepseek-v4-pro",
                "command": "python scripts\\run_evp8_hard_qwen_deepseek.py --execute --config configs\\evp8_hard_e6_evidence_only.local.json --model-id deepseek/deepseek-v4-pro",
                "outputs": outputs_by_model["deepseek/deepseek-v4-pro"],
                "proceed_if": "Qwen evidence-only audit has complete Qwen coverage and user explicitly authorizes DeepSeek",
            },
        ],
        "expected_output_absence": absence,
        "checks": checks,
        "stop_gates": [
            "User has not explicitly authorized EVP-8-HARD E6-evidence-only Qwen API.",
            "Tracked example config is used for --execute.",
            "Any expected evidence-only output already exists before execution.",
            "Existing E6-full Qwen/DeepSeek summaries would be overwritten.",
            "Rendered prompt text or raw model response would be written to tracked files.",
            "Parsed review JSONL contains raw_response_text, provider response object, rendered prompt, or prompt text.",
            "Evidence-only result is interpreted as automatic correctness verification instead of risk handling.",
        ],
        "claim_boundary": (
            "This packet prepares an evidence-only ablation. It is not an API "
            "authorization and not a model result."
        ),
    }


def write_markdown(path: Path, packet: dict[str, Any]) -> None:
    lines = [
        "# EVP-8-HARD E6 Evidence-Only Execution Packet v0.1",
        "",
        f"- Status: `{packet['packet_status']}`",
        f"- Packet variant: `{packet['packet_variant']}`",
        f"- API call attempted: `{str(packet['api_call_attempted']).lower()}`",
        f"- Execution authorized by this packet: `{str(packet['execution_authorized_by_packet']).lower()}`",
        f"- Planned calls per model: `{packet['planned_calls_per_model']}`",
        "",
        "## Removed Fields",
        "",
    ]
    lines.extend(f"- `{field}`" for field in packet["removed_verdict_fields"])
    lines.extend(["", "## Execute Commands After Explicit User Authorization", ""])
    for command in packet["execute_commands_after_explicit_user_authorization"]:
        lines.append(f"- `{command['step']}`: `{command['command']}`")
        lines.append(f"  - proceed if: {command['proceed_if']}")
        lines.append("  - outputs:")
        for key, value in command["outputs"].items():
            lines.append(f"    - `{key}`: `{value}`")
    lines.extend(["", "## Primary Opportunity Set", ""])
    lines.append(f"- Source: `{packet['primary_opportunity_set']['source']}`")
    lines.append(f"- Repeated false accepts: `{packet['primary_opportunity_set']['repeated_false_accept_count']}`")
    lines.append(f"- Rule: {packet['primary_opportunity_set']['evaluation_rule']}")
    lines.extend(["", "## Stop Gates", ""])
    lines.extend(f"- {gate}" for gate in packet["stop_gates"])
    lines.extend(["", "## Checks", ""])
    lines.extend(f"- {item['check']}: `{str(item['passed']).lower()}`" for item in packet["checks"])
    lines.extend(["", "## Claim Boundary", "", packet["claim_boundary"], ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def assert_packet(packet: dict[str, Any]) -> None:
    if packet["packet_status"] != "ready":
        raise SystemExit(f"evidence-only execution packet is blocked: {packet['checks']}")
    if packet["execution_authorized_by_packet"] is not False:
        raise SystemExit("execution_authorized_by_packet must be false")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    packet = build_packet()
    write_json(args.json_out, packet)
    write_markdown(args.md_out, packet)
    if args.check:
        assert_packet(packet)
    print(json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
