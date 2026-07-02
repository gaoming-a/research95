"""Write the no-API third-project source-selection packet for EVP-8 realistic hard negatives.

The packet does not authorize generation or verifier API calls. It selects the
next third-project source to repair the current 30-case/3-project gate gap and
records why already-tried projects should not be reused as successful evidence.
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
COMBINED_GATE = REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_combined_generation_gate_with_full_file_v0_1.json"
REDESIGN_REVIEW = REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_third_project_redesign_review_v0_1.json"
SOURCE_TARGET_MATRIX = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_source_target_matrix_v0_1.json"
SOURCE_BUGS_FILE = REPO_ROOT / "scripts" / "build_patch_verification_dataset.py"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_third_project_source_selection_packet_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_realistic_hardneg_third_project_source_selection_packet_v0_1.md"

SELECTED_PROJECT = "luigi"
SELECTED_TASKS = ["bugsinpy_luigi_3", "bugsinpy_luigi_4"]


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


def load_source_bug_ids() -> set[str]:
    module = ast.parse(SOURCE_BUGS_FILE.read_text(encoding="utf-8"))
    for node in module.body:
        if isinstance(node, ast.Assign) and any(getattr(target, "id", None) == "SOURCE_BUGS" for target in node.targets):
            rows = ast.literal_eval(node.value)
            return {str(row["task_id"]) for row in rows}
    raise ValueError("SOURCE_BUGS assignment not found")


def project_attempts(redesign: dict[str, Any]) -> dict[str, dict[str, Any]]:
    attempts: dict[str, dict[str, Any]] = {}
    for row in redesign.get("failed_third_project_attempts", []):
        if isinstance(row, dict) and row.get("project"):
            attempts[str(row["project"])] = row
    return attempts


def build_packet() -> dict[str, Any]:
    gate = read_json(COMBINED_GATE)
    redesign = read_json(REDESIGN_REVIEW)
    target_matrix = read_json(SOURCE_TARGET_MATRIX)
    source_bug_ids = load_source_bug_ids()
    attempts = project_attempts(redesign)

    hard_gate = gate.get("hard_negative_gate") or {}
    gate_projects = set(hard_gate.get("visible_pass_hidden_fail_projects") or [])
    by_project = gate.get("classification_by_project") or {}
    readiness = gate.get("readiness") or {}
    luigi_attempt = attempts.get(SELECTED_PROJECT, {})

    rejected_sources = [
        {
            "project": "httpie",
            "decision": "do_not_reuse_as_next_source",
            "observed_gate_counts": by_project.get("httpie", {}),
            "reason": "observed hidden-failing candidates failed visible tests; direct repeats do not target visible-pass/hidden-fail.",
        },
        {
            "project": "thefuck",
            "decision": "do_not_reuse_as_next_source",
            "observed_gate_counts": by_project.get("thefuck", {}),
            "reason": "observed candidates were visible-pass/hidden-pass; this project behaved as correct-like under the current setup.",
        },
        {
            "project": "tqdm",
            "decision": "do_not_reuse_as_next_source",
            "observed_gate_counts": by_project.get("tqdm", {}),
            "reason": "observed wrong candidates failed visible tests, so the current source does not create false-accept opportunity cases.",
        },
        {
            "project": "youtube-dl",
            "decision": "do_not_reuse_as_next_source",
            "observed_gate_counts": by_project.get("youtube-dl", {}),
            "reason": "one supplement failed before candidate construction and the later full-file attempt produced visible-pass/hidden-pass cases.",
        },
    ]

    selected_source = {
        "project": SELECTED_PROJECT,
        "tasks": SELECTED_TASKS,
        "selection_status": "selected_for_new_source_acquisition_protocol",
        "why_selected": [
            "The current gate needs a third project; existing visible-pass/hidden-fail projects are only PySnooper and cookiecutter.",
            "Luigi is not already counted as a gate-passing project, so it can add genuine project diversity if validation succeeds.",
            "The previous Luigi supplement failed before candidate construction, so its blocker is materialization/interface design rather than an observed visible-pass/hidden-fail yield failure.",
            "Both selected Luigi tasks exist in tracked source-bug definitions, enabling a no-API protocol to be written before any generation call.",
        ],
        "required_protocol_change": (
            "Freeze a separate source-acquisition/materialization protocol before generation. "
            "Do not silently retry the exact search/replace edit-plan interface."
        ),
        "minimum_success_gate_after_future_validation": {
            "new_visible_pass_hidden_fail_cases_needed": max(0, int(hard_gate.get("minimum_count", 30)) - int(hard_gate.get("visible_pass_hidden_fail_count", 0))),
            "new_project_needed": SELECTED_PROJECT,
            "required_property": hard_gate.get("required_property"),
        },
    }

    checks = [
        check("api_call_not_attempted", True, False),
        check("raw_model_outputs_not_read", True, False),
        check("prompt_text_not_read", True, False),
        check("patch_text_not_read", True, False),
        check("combined_gate_passed_as_analysis", gate.get("analysis_status") == "passed", gate.get("analysis_status")),
        check("current_gate_not_ready_for_verifier_api", readiness.get("ready_for_verifier_api") is False, readiness.get("ready_for_verifier_api")),
        check("current_hard_negative_gate_failed", hard_gate.get("passed") is False, hard_gate.get("passed")),
        check("selected_project_not_already_gate_passing", SELECTED_PROJECT not in gate_projects, sorted(gate_projects)),
        check("selected_tasks_in_source_bug_definitions", all(task in source_bug_ids for task in SELECTED_TASKS), SELECTED_TASKS),
        check(
            "selected_project_previous_failure_before_candidate_construction",
            "before candidate construction" in str(luigi_attempt.get("result", "")),
            luigi_attempt.get("result"),
        ),
        check(
            "source_target_matrix_does_not_already_solve_third_project",
            SELECTED_PROJECT not in set((target_matrix.get("target_summary") or {}).get("project_slot_counts", {}).keys()),
            (target_matrix.get("target_summary") or {}).get("project_slot_counts", {}),
        ),
    ]

    return {
        "packet_id": "evp8_realistic_hardneg_third_project_source_selection_packet_v0_1",
        "date": "2026-07-02",
        "scope": {
            "api_call_attempted": False,
            "generation_api_authorized": False,
            "verifier_api_authorized": False,
            "raw_model_outputs_read": False,
            "prompt_text_read": False,
            "patch_text_read": False,
        },
        "inputs": {
            "combined_gate": display_path(COMBINED_GATE),
            "third_project_redesign_review": display_path(REDESIGN_REVIEW),
            "source_target_matrix": display_path(SOURCE_TARGET_MATRIX),
            "source_bug_definitions": display_path(SOURCE_BUGS_FILE),
        },
        "current_gate": {
            "visible_pass_hidden_fail_count": hard_gate.get("visible_pass_hidden_fail_count"),
            "minimum_count": hard_gate.get("minimum_count"),
            "visible_pass_hidden_fail_projects": sorted(gate_projects),
            "minimum_projects": hard_gate.get("minimum_projects"),
            "ready_for_verifier_api": readiness.get("ready_for_verifier_api"),
        },
        "selected_source": selected_source,
        "rejected_sources": rejected_sources,
        "forbidden_actions": [
            "run Qwen or DeepSeek verifier API while ready_for_verifier_api is false",
            "run generation API from this packet alone",
            "retry the same exact search/replace interface for Luigi without a new protocol",
            "count Luigi task-file smoke artifacts as a passed realistic third-project gate",
            "reuse failed third-project attempts as successful verifier-ready evidence",
        ],
        "allowed_next_work": [
            "write a no-API Luigi source-acquisition/materialization protocol",
            "define dry-run materialization checks and validation commands without calling APIs",
            "run only protocol/check-only gates before asking for any generation API authorization",
            "after any future generated candidates, rerun validation and the combined hard-negative gate",
        ],
        "checks": checks,
        "packet_status": "passed" if all(item["passed"] for item in checks) else "failed",
    }


def write_markdown(path: Path, packet: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    gate = packet["current_gate"]
    selected = packet["selected_source"]
    lines = [
        "# EVP-8 Realistic Hard-Negative Third-Project Source Selection Packet v0.1",
        "",
        "Date: 2026-07-02",
        "",
        "This is a no-API source-selection packet. It does not call model APIs,",
        "authorize generation, authorize verifier APIs, read raw model outputs,",
        "read prompt text, or read patch text.",
        "",
        "## Status",
        "",
        f"- packet status: `{packet['packet_status']}`",
        f"- selected project: `{selected['project']}`",
        f"- selected tasks: {', '.join(f'`{task}`' for task in selected['tasks'])}",
        "- generation API authorized: `False`",
        "- verifier API authorized: `False`",
        "",
        "## Current Gate",
        "",
        f"- visible-pass/hidden-fail cases: `{gate['visible_pass_hidden_fail_count']}` / `{gate['minimum_count']}`",
        f"- visible-pass/hidden-fail projects: {', '.join(f'`{project}`' for project in gate['visible_pass_hidden_fail_projects'])}",
        f"- minimum projects: `{gate['minimum_projects']}`",
        f"- ready for verifier API: `{gate['ready_for_verifier_api']}`",
        "",
        "## Selection Rationale",
        "",
    ]
    for reason in selected["why_selected"]:
        lines.append(f"- {reason}")
    lines += [
        "",
        "Required protocol change:",
        "",
        selected["required_protocol_change"],
        "",
        "Minimum future validation success gate:",
        "",
        f"- new visible-pass/hidden-fail cases needed: `{selected['minimum_success_gate_after_future_validation']['new_visible_pass_hidden_fail_cases_needed']}`",
        f"- new project needed: `{selected['minimum_success_gate_after_future_validation']['new_project_needed']}`",
        f"- required property: `{selected['minimum_success_gate_after_future_validation']['required_property']}`",
        "",
        "## Rejected Direct Sources",
        "",
        "| project | observed counts | decision reason |",
        "| --- | --- | --- |",
    ]
    for row in packet["rejected_sources"]:
        lines.append(f"| `{row['project']}` | `{row['observed_gate_counts']}` | {row['reason']} |")
    lines += [
        "",
        "## Checks",
        "",
        "| check | passed | detail |",
        "| --- | ---: | --- |",
    ]
    for item in packet["checks"]:
        lines.append(f"| `{item['check']}` | {str(item['passed']).lower()} | `{item['detail']}` |")
    lines += [
        "",
        "## Allowed Next Work",
        "",
    ]
    for action in packet["allowed_next_work"]:
        lines.append(f"- {action}")
    lines += [
        "",
        "## Forbidden Actions",
        "",
    ]
    for action in packet["forbidden_actions"]:
        lines.append(f"- {action}")
    lines += [
        "",
        "## Decision",
        "",
        "Proceed only to a no-API Luigi source-acquisition/materialization protocol.",
        "Do not run verifier APIs, and do not run generation APIs from this packet alone.",
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
    packet = build_packet()
    write_json(args.out_json, packet)
    write_markdown(args.out_md, packet)
    if args.check and packet["packet_status"] != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
