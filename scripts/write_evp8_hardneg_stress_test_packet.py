# ruff: noqa: E402
"""Write a no-API packet for the EVP-8 hard-negative stress-test route."""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/write_evp8_hardneg_stress_test_packet.py")

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
UPLIFT_PACKET = REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_uplift_packet_v0_1.json"
SOURCE_SELECTION_PACKET = (
    REPO_ROOT
    / "data"
    / "protocols"
    / "evp8_realistic_hardneg_third_project_source_selection_packet_v0_1.json"
)
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "protocols" / "evp8_hardneg_stress_test_packet_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_hardneg_stress_test_packet_v0_1.md"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{rel(path)} must contain a JSON object")
    return value


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def build_packet() -> dict[str, Any]:
    uplift = read_json(UPLIFT_PACKET)
    source_selection = read_json(SOURCE_SELECTION_PACKET)
    gate = uplift["current_gate"]
    selected_source = source_selection["selected_source"]
    current_cases = int(gate["current_visible_pass_hidden_fail_cases"])
    minimum_cases = int(gate["minimum_visible_pass_hidden_fail_cases"])
    current_projects = list(gate["current_projects"])
    minimum_projects = int(gate["minimum_projects"])
    missing_cases = max(0, minimum_cases - current_cases)
    missing_projects = max(0, minimum_projects - len(current_projects))
    ready = bool(gate["ready_for_verifier_api"])
    checks = [
        check("api_call_not_attempted", True, False),
        check("raw_model_outputs_not_read", True, False),
        check("prompt_text_not_read", True, False),
        check("patch_text_not_read", True, False),
        check("current_hard_negative_case_gate_passed", current_cases >= minimum_cases, current_cases),
        check("current_hard_negative_project_gate_passed", len(current_projects) >= minimum_projects, current_projects),
        check("verifier_api_blocked_until_gate_passes", not ready, ready),
        check("third_project_source_selected", selected_source.get("project") == "luigi", selected_source),
    ]
    packet = {
        "packet_id": "evp8_hardneg_stress_test_packet_v0_1",
        "date": "2026-07-06",
        "status": "blocked_needs_more_cases_and_third_project" if not ready else "ready_for_verifier_matrix",
        "scope": {
            "api_call_attempted": False,
            "verifier_api_authorized_by_packet": False,
            "generation_api_authorized_by_packet": False,
            "raw_model_outputs_read": False,
            "prompt_text_read": False,
            "patch_text_read": False,
        },
        "current_gate": {
            "minimum_visible_pass_hidden_fail_cases": minimum_cases,
            "current_visible_pass_hidden_fail_cases": current_cases,
            "missing_visible_pass_hidden_fail_cases": missing_cases,
            "minimum_projects": minimum_projects,
            "current_projects": current_projects,
            "missing_project_count": missing_projects,
            "ready_for_verifier_api": ready,
            "required_property": gate["required_property"],
        },
        "selected_next_source": {
            "project": selected_source["project"],
            "tasks": selected_source["tasks"],
            "new_visible_pass_hidden_fail_cases_needed": selected_source[
                "minimum_success_gate_after_future_validation"
            ]["new_visible_pass_hidden_fail_cases_needed"],
            "required_protocol_change": selected_source["required_protocol_change"],
        },
        "planned_stress_matrix_after_gate_passes": {
            "cohort": "validated visible-pass/hidden-fail hard-negative cohort with at least 30 cases across at least 3 projects",
            "models": [
                "qwen/qwen3.7-max",
                "deepseek/deepseek-v4-pro",
                "google/gemini-2.5-flash",
            ],
            "conditions": [
                "rule_only_visible_tool_baseline",
                "current_merge_gate_prompt",
                "e6_no_verdict_prompt",
                "coverage_contestation_prompt",
            ],
            "required_metrics": [
                "strict_reject",
                "safe_escalation",
                "repeated_false_accept",
                "correct_recall_loss",
                "coverage_challenge_rate",
                "verdict_dependence",
            ],
        },
        "allowed_next_work": [
            "write or refresh the Luigi no-API source-acquisition/materialization protocol",
            "perform dry-run materialization and validation checks without verifier API calls",
            "after candidate generation/validation, rerun the combined hard-negative gate",
            "only after the gate reaches at least 30 cases and 3 projects, prepare verifier API preflight for the stress matrix",
        ],
        "forbidden_next_work": [
            "run Qwen, DeepSeek, or Gemini hard-negative verifier API while ready_for_verifier_api is false",
            "treat the current 26-case two-project branch as the stress-test main cohort",
            "count escalation as strict rejection",
            "merge stress-test results into the main E0-E6 table without labeling the prompt condition",
        ],
        "checks": checks,
        "inputs": {
            "uplift_packet": rel(UPLIFT_PACKET),
            "third_project_source_selection": rel(SOURCE_SELECTION_PACKET),
        },
    }
    return packet


def write_md(packet: dict[str, Any], path: Path) -> None:
    gate = packet["current_gate"]
    source = packet["selected_next_source"]
    lines = [
        "# EVP-8 hard-negative stress-test packet v0.1",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Current Gate",
        "",
        f"- visible-pass/hidden-fail cases: `{gate['current_visible_pass_hidden_fail_cases']}` / `{gate['minimum_visible_pass_hidden_fail_cases']}`",
        f"- projects: {', '.join(f'`{project}`' for project in gate['current_projects'])}",
        f"- missing cases: `{gate['missing_visible_pass_hidden_fail_cases']}`",
        f"- missing projects: `{gate['missing_project_count']}`",
        f"- ready for verifier API: `{str(gate['ready_for_verifier_api']).lower()}`",
        "",
        "## Selected Next Source",
        "",
        f"- project: `{source['project']}`",
        f"- tasks: {', '.join(f'`{task}`' for task in source['tasks'])}",
        f"- new visible-pass/hidden-fail cases needed: `{source['new_visible_pass_hidden_fail_cases_needed']}`",
        f"- required protocol change: {source['required_protocol_change']}",
        "",
        "## Planned Stress Matrix After Gate Passes",
        "",
        "| axis | values |",
        "| --- | --- |",
        f"| models | {', '.join(f'`{model}`' for model in packet['planned_stress_matrix_after_gate_passes']['models'])} |",
        f"| conditions | {', '.join(f'`{condition}`' for condition in packet['planned_stress_matrix_after_gate_passes']['conditions'])} |",
        f"| metrics | {', '.join(f'`{metric}`' for metric in packet['planned_stress_matrix_after_gate_passes']['required_metrics'])} |",
        "",
        "## Checks",
        "",
        "| check | passed | detail |",
        "| --- | --- | --- |",
    ]
    for row in packet["checks"]:
        lines.append(f"| `{row['check']}` | {str(row['passed']).lower()} | `{json.dumps(row['detail'], ensure_ascii=False)}` |")
    lines.extend(["", "## Forbidden Next Work", ""])
    lines.extend(f"- {item}" for item in packet["forbidden_next_work"])
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    packet = build_packet()
    json_text = json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    existing_json = args.json_out.read_text(encoding="utf-8") if args.json_out.exists() else None
    existing_md = args.md_out.read_text(encoding="utf-8") if args.md_out.exists() else None
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json_text, encoding="utf-8")
    write_md(packet, args.md_out)
    if args.check:
        current_md = args.md_out.read_text(encoding="utf-8")
        if existing_json is not None and existing_json != json_text:
            raise SystemExit(f"{rel(args.json_out)} is not current")
        if existing_md is not None and existing_md != current_md:
            raise SystemExit(f"{rel(args.md_out)} is not current")
        if existing_json is None or existing_md is None:
            raise SystemExit("hard-negative stress-test packet outputs were missing before --check")
        print("hard-negative stress-test packet outputs are current")
    else:
        print(f"wrote {rel(args.json_out)}")
        print(f"wrote {rel(args.md_out)}")


if __name__ == "__main__":
    main()
