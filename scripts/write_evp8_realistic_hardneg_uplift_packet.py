# ruff: noqa: E402
"""Write the no-API uplift packet for the realistic hard-negative gate.

This script reads tracked aggregate gate files only. It does not call model
APIs, read raw model responses, read prompt text, or read patch text.
"""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/write_evp8_realistic_hardneg_uplift_packet.py")

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GATE = (
    REPO_ROOT
    / "data"
    / "protocols"
    / "evp8_realistic_hardneg_combined_generation_gate_with_full_file_v0_1.json"
)
DEFAULT_OUT_JSON = (
    REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_uplift_packet_v0_1.json"
)
DEFAULT_OUT_MD = (
    REPO_ROOT / "docs" / "experiments" / "evp8_realistic_hardneg_uplift_packet_v0_1.md"
)


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


def build_packet(gate_path: Path) -> dict[str, Any]:
    gate = read_json(gate_path)
    hard_gate = gate.get("hard_negative_gate") or {}
    if not isinstance(hard_gate, dict):
        raise ValueError("hard_negative_gate must be an object")

    current_count = int(hard_gate.get("visible_pass_hidden_fail_count", 0))
    minimum_count = int(hard_gate.get("minimum_count", 30))
    current_projects = list(hard_gate.get("visible_pass_hidden_fail_projects") or [])
    minimum_projects = int(hard_gate.get("minimum_projects", 3))
    current_project_count = len(set(map(str, current_projects)))

    missing_count = max(0, minimum_count - current_count)
    missing_project_count = max(0, minimum_projects - current_project_count)
    gate_passed = bool(hard_gate.get("passed"))
    ready_for_verifier_api = bool((gate.get("readiness") or {}).get("ready_for_verifier_api"))

    checks = [
        check("api_call_not_attempted", True, False),
        check("raw_model_outputs_not_read", True, False),
        check("prompt_text_not_read", True, False),
        check("patch_text_not_read", True, False),
        check("input_gate_present", gate_path.exists(), display_path(gate_path)),
        check("input_gate_passed_as_analysis", gate.get("analysis_status") == "passed", gate.get("analysis_status")),
        check("hard_negative_count_gate_passed", current_count >= minimum_count, current_count),
        check("hard_negative_project_gate_passed", current_project_count >= minimum_projects, current_projects),
        check("verifier_api_still_blocked", ready_for_verifier_api is False, ready_for_verifier_api),
    ]

    status = "ready_for_verifier_api_planning" if gate_passed and ready_for_verifier_api else "blocked_needs_third_project_source_gate"
    if current_count < minimum_count:
        status = "blocked_needs_more_cases_and_third_project"
    elif current_project_count < minimum_projects:
        status = "blocked_needs_third_project_source_gate"

    return {
        "analysis_id": "evp8_realistic_hardneg_uplift_packet_v0_1",
        "date": "2026-07-02",
        "status": status,
        "scope": {
            "api_call_attempted": False,
            "raw_model_outputs_read": False,
            "prompt_text_read": False,
            "patch_text_read": False,
            "candidate_manifest_mutated": False,
            "experiment_results_modified": False,
        },
        "inputs": {
            "combined_generation_gate": display_path(gate_path),
        },
        "current_gate": {
            "required_property": hard_gate.get("required_property"),
            "minimum_visible_pass_hidden_fail_cases": minimum_count,
            "current_visible_pass_hidden_fail_cases": current_count,
            "missing_visible_pass_hidden_fail_cases": missing_count,
            "minimum_projects": minimum_projects,
            "current_projects": sorted(set(map(str, current_projects))),
            "missing_project_count": missing_project_count,
            "gate_passed": gate_passed,
            "ready_for_verifier_api": ready_for_verifier_api,
        },
        "allowed_next_work": [
            "write a new no-API third-project source-selection packet",
            "freeze a source-acquisition protocol before any generation API",
            "generate or validate candidates only after prompt/schema/leakage gates pass",
            "rerun the combined hard-negative gate after validation",
        ],
        "forbidden_next_work": [
            "run Qwen or DeepSeek verifier API while ready_for_verifier_api is false",
            "merge this branch into the main verifier experiment as three-project ready",
            "count escalation as strict correctness correction",
            "reuse failed third-project attempts as successful verifier-ready evidence",
        ],
        "paper_boundary": {
            "current_use": "two-project source-acquisition / gate-readiness negative result",
            "uplift_condition": (
                "Upgrade to a verifier-ready realistic supplement only after at least 30 "
                "visible-pass/hidden-fail cases across at least 3 projects pass the tracked gate."
            ),
            "if_gate_still_fails": "keep the branch as a negative result and do not run verifier APIs",
        },
        "checks": checks,
        "passed": all(item["passed"] for item in checks[:6]) and ready_for_verifier_api is False,
    }


def write_markdown(path: Path, packet: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    gate = packet["current_gate"]
    lines = [
        "# EVP-8 Realistic Hard-Negative Uplift Packet v0.1",
        "",
        "Date: 2026-07-02",
        "",
        "This is a no-API planning gate. It reads tracked aggregate gate files only",
        "and does not call model APIs, read raw model responses, read prompt text,",
        "or read patch text.",
        "",
        "## Status",
        "",
        f"- status: `{packet['status']}`",
        f"- passed as boundary packet: `{packet['passed']}`",
        f"- ready for verifier API: `{gate['ready_for_verifier_api']}`",
        "",
        "## Current Gate Gap",
        "",
        f"- required property: `{gate['required_property']}`",
        f"- visible-pass/hidden-fail cases: `{gate['current_visible_pass_hidden_fail_cases']}` / `{gate['minimum_visible_pass_hidden_fail_cases']}`",
        f"- missing cases: `{gate['missing_visible_pass_hidden_fail_cases']}`",
        f"- projects: `{', '.join(gate['current_projects'])}`",
        f"- missing project count: `{gate['missing_project_count']}`",
        "",
        "## Checks",
        "",
        "| check | passed | detail |",
        "|---|---:|---|",
    ]
    for item in packet["checks"]:
        detail = json.dumps(item["detail"], ensure_ascii=False)
        lines.append(f"| `{item['check']}` | {str(item['passed']).lower()} | `{detail}` |")
    lines += [
        "",
        "## Allowed Next Work",
        "",
    ]
    for item in packet["allowed_next_work"]:
        lines.append(f"- {item}")
    lines += [
        "",
        "## Forbidden Next Work",
        "",
    ]
    for item in packet["forbidden_next_work"]:
        lines.append(f"- {item}")
    lines += [
        "",
        "## Paper Boundary",
        "",
        f"- current use: {packet['paper_boundary']['current_use']}",
        f"- uplift condition: {packet['paper_boundary']['uplift_condition']}",
        f"- if gate still fails: {packet['paper_boundary']['if_gate_still_fails']}",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate-json", type=Path, default=DEFAULT_GATE)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    packet = build_packet(args.gate_json)
    write_json(args.out_json, packet)
    write_markdown(args.out_md, packet)
    if args.check and not packet["passed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
