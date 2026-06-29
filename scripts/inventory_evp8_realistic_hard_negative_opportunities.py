"""Inventory hard-negative opportunities after corrected realistic labels.

This is a no-API planning audit. It compares the corrected realistic agent
cohort with the historical EVP-8-HARD cohort, then writes a target matrix for
the next hard realistic test-passing-wrong construction step. It does not read
raw model responses, rendered prompts, or patch diffs.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

REALISTIC_EVALUATOR = REPO_ROOT / "data" / "patches" / "evp8_realistic_agent_evaluator_manifest_v0_3.jsonl"
REALISTIC_BASELINE = REPO_ROOT / "data" / "baselines" / "evp8_realistic_agent_visible_tool_baseline_v0_1.jsonl"
REALISTIC_MERGE_SUMMARY = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_merge_label_manifest_v0_3.json"
REALISTIC_QWEN_COMPARISON = (
    REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_qwen_merge_label_variant_comparison_v0_3.json"
)
REALISTIC_SOURCE_INVENTORY = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_source_inventory_v0_4.json"

HARD_EVALUATOR = REPO_ROOT / "data" / "patches" / "evp8_hard_evaluator_manifest_v0_1.jsonl"
HARD_BASELINE = REPO_ROOT / "data" / "baselines" / "evp8_hard_tool_only_baseline_v0_1.jsonl"
HARD_EVIDENCE_ONLY_OPPORTUNITY = (
    REPO_ROOT / "data" / "reviews" / "evp8_hard_e6_evidence_only_opportunity_analysis_v0_1.json"
)

DEFAULT_JSON_OUT = (
    REPO_ROOT / "data" / "protocols" / "evp8_realistic_hard_negative_opportunity_inventory_v0_1.json"
)
DEFAULT_MD_OUT = (
    REPO_ROOT / "docs" / "experiments" / "evp8_realistic_hard_negative_opportunity_inventory_v0_1.md"
)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{display_path(path)} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{display_path(path)}:{line_no} is not a JSON object")
        rows.append(value)
    return rows


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


def counter_dict(counter: Counter[str]) -> dict[str, int]:
    return dict(sorted(counter.items()))


def baseline_by_candidate(path: Path) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for row in read_jsonl(path):
        candidate_id = row.get("candidate_id") or row.get("hard_candidate_id")
        if candidate_id:
            index[str(candidate_id)] = row
    return index


def is_correct_label(label: str) -> bool:
    return label == "correct"


def bool_or_none(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    return None


def summarize_realistic_current() -> dict[str, Any]:
    rows = read_jsonl(REALISTIC_EVALUATOR)
    baseline = baseline_by_candidate(REALISTIC_BASELINE)
    merge_summary = read_json(REALISTIC_MERGE_SUMMARY)
    qwen_comparison = read_json(REALISTIC_QWEN_COMPARISON)

    label_counts: Counter[str] = Counter()
    decision_counts: Counter[str] = Counter()
    decision_by_label: dict[str, Counter[str]] = defaultdict(Counter)
    task_counts: Counter[str] = Counter()
    project_counts: Counter[str] = Counter()
    visible_pass_hidden_fail_by_task: Counter[str] = Counter()
    visible_pass_hidden_fail_by_project: Counter[str] = Counter()
    accepted_wrong_by_task: Counter[str] = Counter()
    accepted_wrong_by_project: Counter[str] = Counter()
    visible_pass_hidden_fail_ids: list[str] = []
    accepted_wrong_ids: list[str] = []
    visible_fail_hidden_pass_ids: list[str] = []

    for row in rows:
        candidate_id = str(row.get("candidate_id") or "")
        task_id = str(row.get("task_id") or "unknown")
        project = str(row.get("project") or "unknown")
        label = str(row.get("normalized_label") or "unknown")
        summary = row.get("hidden_validation_summary") if isinstance(row.get("hidden_validation_summary"), dict) else {}
        visible_passed = bool_or_none(summary.get("visible_tests_passed"))
        oracle_passed = bool_or_none(summary.get("oracle_passed"))
        decision = str(baseline.get(candidate_id, {}).get("decision") or "missing")

        label_counts[label] += 1
        decision_counts[decision] += 1
        decision_by_label[label][decision] += 1
        task_counts[task_id] += 1
        project_counts[project] += 1

        if visible_passed is True and oracle_passed is False:
            visible_pass_hidden_fail_ids.append(candidate_id)
            visible_pass_hidden_fail_by_task[task_id] += 1
            visible_pass_hidden_fail_by_project[project] += 1
        if visible_passed is False and oracle_passed is True:
            visible_fail_hidden_pass_ids.append(candidate_id)
        if decision == "accept" and not is_correct_label(label):
            accepted_wrong_ids.append(candidate_id)
            accepted_wrong_by_task[task_id] += 1
            accepted_wrong_by_project[project] += 1

    return {
        "cohort_id": "EVP-8-REALISTIC-AGENT",
        "input_files": {
            "evaluator_manifest": display_path(REALISTIC_EVALUATOR),
            "visible_tool_baseline": display_path(REALISTIC_BASELINE),
            "merge_label_summary": display_path(REALISTIC_MERGE_SUMMARY),
            "qwen_variant_comparison": display_path(REALISTIC_QWEN_COMPARISON),
        },
        "candidate_count": len(rows),
        "label_counts": counter_dict(label_counts),
        "visible_tool_decision_counts": counter_dict(decision_counts),
        "visible_tool_decision_by_label": {label: counter_dict(counts) for label, counts in sorted(decision_by_label.items())},
        "task_counts": counter_dict(task_counts),
        "project_counts": counter_dict(project_counts),
        "visible_pass_hidden_fail_count": len(visible_pass_hidden_fail_ids),
        "visible_pass_hidden_fail_by_task": counter_dict(visible_pass_hidden_fail_by_task),
        "visible_pass_hidden_fail_by_project": counter_dict(visible_pass_hidden_fail_by_project),
        "visible_tool_accepted_wrong_count": len(accepted_wrong_ids),
        "visible_tool_accepted_wrong_by_task": counter_dict(accepted_wrong_by_task),
        "visible_tool_accepted_wrong_by_project": counter_dict(accepted_wrong_by_project),
        "visible_fail_hidden_pass_count": len(visible_fail_hidden_pass_ids),
        "visible_tool_fully_separates_merge_labels": len(accepted_wrong_ids) == 0,
        "qwen_full_vs_no_verdict_change_count": qwen_comparison.get("full_vs_no_verdict_change_count"),
        "qwen_no_verdict_vs_visible_tool_change_count": qwen_comparison.get(
            "no_verdict_vs_visible_tool_change_count"
        ),
        "merge_label_policy": merge_summary.get("label_policy"),
        "interpretation": (
            "This corrected realistic cohort is externally useful for label-validity auditing, "
            "but it is not useful for measuring false-accept reduction because visible tests "
            "already separate the v0.3 merge labels."
        ),
    }


def summarize_historical_hard() -> dict[str, Any]:
    rows = read_jsonl(HARD_EVALUATOR)
    baseline = baseline_by_candidate(HARD_BASELINE)
    opportunity = read_json(HARD_EVIDENCE_ONLY_OPPORTUNITY)

    label_counts: Counter[str] = Counter()
    decision_counts: Counter[str] = Counter()
    false_accept_by_task: Counter[str] = Counter()
    false_accept_by_project: Counter[str] = Counter()
    false_reject_by_task: Counter[str] = Counter()
    false_accept_labels: Counter[str] = Counter()
    task_counts: Counter[str] = Counter()
    project_counts: Counter[str] = Counter()
    false_accept_ids: list[str] = []
    false_reject_ids: list[str] = []

    for row in rows:
        candidate_id = str(row.get("hard_candidate_id") or row.get("candidate_id") or "")
        task_id = str(row.get("task_id") or "unknown")
        project = str(row.get("project") or "unknown")
        label = str(row.get("normalized_label") or "unknown")
        decision = str(baseline.get(candidate_id, {}).get("decision") or "missing")

        label_counts[label] += 1
        decision_counts[decision] += 1
        task_counts[task_id] += 1
        project_counts[project] += 1

        if decision == "accept" and not is_correct_label(label):
            false_accept_ids.append(candidate_id)
            false_accept_by_task[task_id] += 1
            false_accept_by_project[project] += 1
            false_accept_labels[label] += 1
        if decision != "accept" and is_correct_label(label):
            false_reject_ids.append(candidate_id)
            false_reject_by_task[task_id] += 1

    model_summary: dict[str, Any] = {}
    models = opportunity.get("models") if isinstance(opportunity.get("models"), dict) else {}
    for model_id, model_data in sorted(models.items()):
        if not isinstance(model_data, dict):
            continue
        model_summary[model_id] = {
            "opportunity_record_count": model_data.get("opportunity_record_count"),
            "repeated_accept": model_data.get("repeated_accept"),
            "escalated": model_data.get("escalated"),
            "strict_corrected_to_reject": model_data.get("strict_corrected_to_reject"),
            "safe_handled_by_reject_or_escalate": model_data.get("safe_handled_by_reject_or_escalate"),
            "decision_counts_on_opportunity_set": model_data.get("decision_counts_on_opportunity_set"),
        }

    return {
        "cohort_id": "EVP-8-HARD",
        "input_files": {
            "evaluator_manifest": display_path(HARD_EVALUATOR),
            "visible_tool_baseline": display_path(HARD_BASELINE),
            "evidence_only_opportunity_analysis": display_path(HARD_EVIDENCE_ONLY_OPPORTUNITY),
        },
        "candidate_count": len(rows),
        "label_counts": counter_dict(label_counts),
        "visible_tool_decision_counts": counter_dict(decision_counts),
        "task_counts": counter_dict(task_counts),
        "project_counts": counter_dict(project_counts),
        "visible_tool_false_accept_count": len(false_accept_ids),
        "visible_tool_false_accept_by_task": counter_dict(false_accept_by_task),
        "visible_tool_false_accept_by_project": counter_dict(false_accept_by_project),
        "visible_tool_false_accept_label_counts": counter_dict(false_accept_labels),
        "visible_tool_false_reject_count": len(false_reject_ids),
        "visible_tool_false_reject_by_task": counter_dict(false_reject_by_task),
        "evidence_only_model_opportunity_summary": model_summary,
        "external_validity_limit": (
            "The opportunity cases are real hard negatives, but they are historical and "
            "concentrated in httpie, so they should calibrate failure modes rather than "
            "serve as the main new realistic cohort."
        ),
    }


def summarize_source_inventory() -> dict[str, Any]:
    inventory = read_json(REALISTIC_SOURCE_INVENTORY)
    readiness = inventory.get("readiness") if isinstance(inventory.get("readiness"), dict) else {}
    source_summary = inventory.get("source_summary") if isinstance(inventory.get("source_summary"), dict) else {}
    current_counts = readiness.get("current_counts") if isinstance(readiness.get("current_counts"), dict) else {}
    source_status_counts = source_summary.get("source_status_counts") if isinstance(source_summary.get("source_status_counts"), dict) else {}
    return {
        "input_file": display_path(REALISTIC_SOURCE_INVENTORY),
        "inventory_status": inventory.get("inventory_status"),
        "fresh_usable_candidates_claimed_before_correction": current_counts.get("fresh_usable_candidates"),
        "fresh_agent_like_candidates_claimed_before_correction": current_counts.get("fresh_agent_like_candidates"),
        "fresh_nontrivial_hard_negatives_claimed_before_correction": current_counts.get("fresh_nontrivial_hard_negatives"),
        "pending_agent_like_candidates": current_counts.get("pending_agent_like_candidates"),
        "pending_usable_candidates": current_counts.get("pending_usable_candidates"),
        "source_status_counts": dict(sorted(source_status_counts.items())),
        "stale_boundary": (
            "This source inventory counted fresh hard negatives before corrected oracle and merge-label "
            "repair. It remains useful for locating source files, but not for claiming validated "
            "visible-pass/hidden-fail negatives."
        ),
    }


def target_matrix(realistic: dict[str, Any], historical: dict[str, Any], source: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "target": "corrected_realistic_current_cohort",
            "status": "not_suitable_as_hard_negative_experiment",
            "evidence": {
                "candidate_count": realistic["candidate_count"],
                "visible_pass_hidden_fail_count": realistic["visible_pass_hidden_fail_count"],
                "visible_tool_accepted_wrong_count": realistic["visible_tool_accepted_wrong_count"],
                "visible_tool_fully_separates_merge_labels": realistic["visible_tool_fully_separates_merge_labels"],
            },
            "next_action": "Do not run more verifier API on this same evidence; use it as a label-validity audit case.",
        },
        {
            "target": "historical_evp8_hard_httpie_luigi",
            "status": "usable_as_calibration_not_main_external_validity",
            "evidence": {
                "candidate_count": historical["candidate_count"],
                "visible_tool_false_accept_count": historical["visible_tool_false_accept_count"],
                "visible_tool_false_accept_by_project": historical["visible_tool_false_accept_by_project"],
                "visible_tool_false_accept_by_task": historical["visible_tool_false_accept_by_task"],
            },
            "next_action": (
                "Use these cases to define failure modes and analysis metrics; do not count them as "
                "fresh realistic-cohort evidence."
            ),
        },
        {
            "target": "pending_or_unvalidated_realistic_sources",
            "status": "needs_validation_before_any_api",
            "evidence": {
                "pending_agent_like_candidates": source.get("pending_agent_like_candidates"),
                "pending_usable_candidates": source.get("pending_usable_candidates"),
            },
            "next_action": (
                "If the pending files still exist locally, validate/relabel them under corrected "
                "project environments, then recompute visible-pass/hidden-fail counts."
            ),
        },
        {
            "target": "new_realistic_hard_negative_generation",
            "status": "recommended_next_research_step",
            "evidence": {
                "required_property": "patch applies, declared visible tests pass, hidden oracle fails",
                "minimum_target": "at least 30 validated visible-pass/hidden-fail candidates across at least 3 projects",
                "preferred_balance": "agent-generated or agent-like patches first; constructed hard negatives only as labeled calibration",
            },
            "next_action": (
                "First write a no-API generation/validation packet that filters for visible-pass/hidden-fail "
                "after corrected oracle execution. Only then use the broad API authorization."
            ),
        },
    ]


def build_inventory() -> dict[str, Any]:
    realistic = summarize_realistic_current()
    historical = summarize_historical_hard()
    source = summarize_source_inventory()
    matrix = target_matrix(realistic, historical, source)

    hard_negative_ready = realistic["visible_pass_hidden_fail_count"] >= 30
    calibration_ready = historical["visible_tool_false_accept_count"] > 0
    checks = [
        check("api_call_not_attempted", True, False),
        check("raw_model_outputs_not_read", True, False),
        check("patch_text_not_written", True, False),
        check("corrected_realistic_manifest_detected", bool(realistic["candidate_count"]), realistic["candidate_count"]),
        check("historical_hard_manifest_detected", bool(historical["candidate_count"]), historical["candidate_count"]),
        check(
            "corrected_realistic_visible_pass_hidden_fail_absent",
            realistic["visible_pass_hidden_fail_count"] == 0,
            realistic["visible_pass_hidden_fail_count"],
        ),
        check(
            "historical_hard_calibration_opportunities_present",
            calibration_ready,
            historical["visible_tool_false_accept_count"],
        ),
        check("new_verifier_api_not_ready_as_expected", not hard_negative_ready, hard_negative_ready),
    ]
    return {
        "analysis_id": "evp8_realistic_hard_negative_opportunity_inventory_v0_1",
        "date": datetime.now().date().isoformat(),
        "scope": {
            "api_call_attempted": False,
            "raw_model_outputs_read": False,
            "rendered_prompt_read_or_written": False,
            "patch_text_written": False,
            "cohort_labels_mutated": False,
            "model_outputs_mutated": False,
        },
        "current_corrected_realistic_cohort": realistic,
        "historical_hard_cohort": historical,
        "source_inventory_boundary": source,
        "target_matrix": matrix,
        "readiness": {
            "ready_for_verifier_api": hard_negative_ready,
            "ready_for_generation_or_validation_planning": True,
            "api_authorization_recorded_but_not_used": True,
            "block_reason_for_verifier_api": (
                "No current corrected realistic visible-pass/hidden-fail cohort exists; "
                "calling verifier APIs now would mostly retest a visible-tool-separated dataset."
            ),
            "next_step": (
                "Build a no-API generation/validation packet for fresh realistic hard negatives, "
                "then run validation and visible-tool headroom before any verifier API."
            ),
        },
        "checks": checks,
        "inventory_status": "passed" if all(item["passed"] for item in checks) else "failed",
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    realistic = report["current_corrected_realistic_cohort"]
    historical = report["historical_hard_cohort"]
    readiness = report["readiness"]
    lines = [
        "# EVP-8 Realistic Hard-Negative Opportunity Inventory v0.1",
        "",
        f"Date: {report['date']}",
        "",
        "This is a no-API planning audit. It records the user's broad API",
        "authorization but does not use it, because the corrected realistic cohort",
        "currently has no validated visible-pass/hidden-fail opportunity set.",
        "",
        "## Boundary Checks",
        "",
    ]
    for item in report["checks"]:
        lines.append(f"- {item['check']}: {'passed' if item['passed'] else 'failed'} ({item['detail']})")
    lines += [
        "",
        "## Corrected Realistic Cohort",
        "",
        f"- candidates: {realistic['candidate_count']}",
        f"- labels: `{realistic['label_counts']}`",
        f"- visible-tool decisions: `{realistic['visible_tool_decision_counts']}`",
        f"- visible-pass/hidden-fail candidates: {realistic['visible_pass_hidden_fail_count']}",
        f"- visible-tool accepted wrong candidates: {realistic['visible_tool_accepted_wrong_count']}",
        f"- visible-tool fully separates merge labels: {realistic['visible_tool_fully_separates_merge_labels']}",
        "",
        realistic["interpretation"],
        "",
        "## Historical Hard Cohort",
        "",
        f"- candidates: {historical['candidate_count']}",
        f"- labels: `{historical['label_counts']}`",
        f"- visible-tool false accepts: {historical['visible_tool_false_accept_count']}",
        f"- false accepts by project: `{historical['visible_tool_false_accept_by_project']}`",
        f"- false accepts by task: `{historical['visible_tool_false_accept_by_task']}`",
        "",
        historical["external_validity_limit"],
        "",
        "Evidence-only opportunity summary:",
        "",
    ]
    for model_id, model in historical["evidence_only_model_opportunity_summary"].items():
        lines.append(
            f"- `{model_id}`: repeated accept {model.get('repeated_accept')}, "
            f"escalate {model.get('escalated')}, strict reject {model.get('strict_corrected_to_reject')}"
        )
    lines += [
        "",
        "## Target Matrix",
        "",
        "| target | status | next action |",
        "| --- | --- | --- |",
    ]
    for row in report["target_matrix"]:
        lines.append(f"| `{row['target']}` | `{row['status']}` | {row['next_action']} |")
    lines += [
        "",
        "## Readiness",
        "",
        f"- ready for verifier API: {readiness['ready_for_verifier_api']}",
        f"- API authorization recorded but not used: {readiness['api_authorization_recorded_but_not_used']}",
        f"- block reason: {readiness['block_reason_for_verifier_api']}",
        f"- next step: {readiness['next_step']}",
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
    report = build_inventory()
    write_json(args.out_json, report)
    write_markdown(args.out_md, report)
    if args.check and report["inventory_status"] != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
