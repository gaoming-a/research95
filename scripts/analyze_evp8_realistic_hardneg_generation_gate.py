"""Analyze the fresh realistic hard-negative generation gate.

This joins local validation records with model-visible visible-test outcomes
to identify candidates that apply, pass declared visible tests, and fail hidden
oracles. It writes aggregate artifacts without patch text or raw responses.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VALIDATION = REPO_ROOT / "outputs" / "evp8_realistic_hardneg_validation_qwen_001" / "validation.jsonl"
DEFAULT_VISIBLE = REPO_ROOT / "data" / "evidence" / "evp8_realistic_hardneg_visible_test_outcomes_v0_1.jsonl"
DEFAULT_GENERATION_AUDIT = REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_generation_result_audit_v0_1.json"
DEFAULT_VISIBLE_SUMMARY = REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_visible_test_outcomes_v0_1.json"
DEFAULT_OUT_JSON = REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_generation_gate_v0_1.json"
DEFAULT_OUT_MD = REPO_ROOT / "docs" / "experiments" / "evp8_realistic_hardneg_generation_gate_v0_1.md"
MIN_HARD_NEGATIVES = 30
MIN_PROJECTS = 3


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{display_path(path)} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{display_path(path)}:{line_no} must contain a JSON object")
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


def classify(validation: dict[str, Any], visible: dict[str, Any]) -> str:
    patch_applied = validation.get("patch_applied") is True
    oracle_passed = validation.get("oracle_passed")
    visible_passed = (visible.get("visible_run_summary") or {}).get("passed") is True
    if not patch_applied:
        return "patch_apply_failed"
    if visible_passed and oracle_passed is False:
        return "visible_pass_hidden_fail"
    if visible_passed and oracle_passed is True:
        return "visible_pass_hidden_pass"
    if not visible_passed and oracle_passed is False:
        return "visible_fail_hidden_fail"
    if not visible_passed and oracle_passed is True:
        return "visible_fail_hidden_pass"
    return "inconclusive"


def build_analysis(
    validation_path: Path,
    visible_path: Path,
    generation_audit_path: Path,
    visible_summary_path: Path,
    min_hard_negatives: int,
    min_projects: int,
) -> dict[str, Any]:
    validation_rows = read_jsonl(validation_path)
    visible_rows = read_jsonl(visible_path)
    generation_audit = read_json(generation_audit_path)
    visible_summary = read_json(visible_summary_path)
    validation_by_id = {str(row.get("model_candidate_id")): row for row in validation_rows}
    visible_by_id = {str(row.get("candidate_id")): row for row in visible_rows}
    missing_visible = sorted(set(validation_by_id) - set(visible_by_id))
    extra_visible = sorted(set(visible_by_id) - set(validation_by_id))

    class_counts: Counter[str] = Counter()
    class_by_task: dict[str, Counter[str]] = defaultdict(Counter)
    class_by_project: dict[str, Counter[str]] = defaultdict(Counter)
    hard_negative_ids: list[str] = []

    for candidate_id, validation in sorted(validation_by_id.items()):
        visible = visible_by_id.get(candidate_id)
        if not visible:
            continue
        classification = classify(validation, visible)
        task_id = str(validation.get("task_id") or visible.get("task_id") or "unknown")
        project = str(validation.get("project") or visible.get("project") or "unknown")
        class_counts[classification] += 1
        class_by_task[task_id][classification] += 1
        class_by_project[project][classification] += 1
        if classification == "visible_pass_hidden_fail":
            hard_negative_ids.append(candidate_id)

    hard_negative_projects = sorted(
        project for project, counts in class_by_project.items() if counts.get("visible_pass_hidden_fail", 0) > 0
    )
    hard_negative_tasks = sorted(
        task_id for task_id, counts in class_by_task.items() if counts.get("visible_pass_hidden_fail", 0) > 0
    )
    gate_passed = len(hard_negative_ids) >= min_hard_negatives and len(hard_negative_projects) >= min_projects
    checks = [
        check("api_call_not_attempted_by_analysis", True, False),
        check("raw_model_outputs_not_read", True, False),
        check("patch_text_not_stored", True, False),
        check("generation_audit_passed", generation_audit.get("status") == "passed", generation_audit.get("status")),
        check("visible_tests_completed", visible_summary.get("run_status_counts") == {"completed": len(visible_rows)}, visible_summary.get("run_status_counts")),
        check("validation_count_matches_visible_count", len(validation_rows) == len(visible_rows), {"validation": len(validation_rows), "visible": len(visible_rows)}),
        check("visible_coverage_complete", not missing_visible and not extra_visible, {"missing": missing_visible, "extra": extra_visible}),
        check("hard_negative_min_count_gate", len(hard_negative_ids) >= min_hard_negatives, len(hard_negative_ids)),
        check("hard_negative_min_project_gate", len(hard_negative_projects) >= min_projects, hard_negative_projects),
    ]
    return {
        "analysis_id": "evp8_realistic_hardneg_generation_gate_v0_1",
        "date": datetime.now().date().isoformat(),
        "scope": {
            "api_call_attempted": False,
            "raw_model_outputs_read": False,
            "patch_text_stored": False,
            "prompt_text_stored": False,
        },
        "inputs": {
            "validation": display_path(validation_path),
            "visible_test_outcomes": display_path(visible_path),
            "generation_audit": display_path(generation_audit_path),
            "visible_test_summary": display_path(visible_summary_path),
        },
        "candidate_count": len(validation_rows),
        "classification_counts": counter_dict(class_counts),
        "classification_by_task": {task: counter_dict(counts) for task, counts in sorted(class_by_task.items())},
        "classification_by_project": {project: counter_dict(counts) for project, counts in sorted(class_by_project.items())},
        "hard_negative_gate": {
            "required_property": "patch_applied && declared_visible_tests_passed && hidden_oracle_failed",
            "visible_pass_hidden_fail_count": len(hard_negative_ids),
            "visible_pass_hidden_fail_projects": hard_negative_projects,
            "visible_pass_hidden_fail_tasks": hard_negative_tasks,
            "minimum_count": min_hard_negatives,
            "minimum_projects": min_projects,
            "passed": gate_passed,
        },
        "readiness": {
            "ready_for_verifier_api": gate_passed,
            "next_step": (
                "Construct separated evaluator/model-visible hard-negative cohort and visible-tool headroom gate."
                if gate_passed
                else "Add a supplement focused on missing project diversity and at least four more visible-pass/hidden-fail candidates."
            ),
        },
        "checks": checks,
        "analysis_status": "passed" if all(item["passed"] for item in checks[:7]) else "blocked",
    }


def write_markdown(path: Path, analysis: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    gate = analysis["hard_negative_gate"]
    lines = [
        "# EVP-8 Realistic Hard-Negative Generation Gate v0.1",
        "",
        f"Date: {analysis['date']}",
        "",
        "This raw-output-free analysis joins validation records with visible-test",
        "outcomes. It does not store patch text, prompt text, or raw model responses.",
        "",
        f"- status: `{analysis['analysis_status']}`",
        f"- candidates: {analysis['candidate_count']}",
        f"- ready for verifier API: `{analysis['readiness']['ready_for_verifier_api']}`",
        "",
        "## Classification Counts",
        "",
    ]
    for key, value in analysis["classification_counts"].items():
        lines.append(f"- `{key}`: {value}")
    lines += [
        "",
        "## Hard-Negative Gate",
        "",
        f"- required property: `{gate['required_property']}`",
        f"- visible-pass/hidden-fail count: {gate['visible_pass_hidden_fail_count']}",
        f"- projects: {', '.join(f'`{project}`' for project in gate['visible_pass_hidden_fail_projects']) or 'none'}",
        f"- tasks: {', '.join(f'`{task}`' for task in gate['visible_pass_hidden_fail_tasks']) or 'none'}",
        f"- minimum count: {gate['minimum_count']}",
        f"- minimum projects: {gate['minimum_projects']}",
        f"- gate passed: `{gate['passed']}`",
        "",
        "## By Task",
        "",
        "| task | visible-pass hidden-fail | visible-pass hidden-pass | visible-fail hidden-fail | visible-fail hidden-pass |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for task, counts in analysis["classification_by_task"].items():
        lines.append(
            f"| `{task}` | {counts.get('visible_pass_hidden_fail', 0)} | "
            f"{counts.get('visible_pass_hidden_pass', 0)} | "
            f"{counts.get('visible_fail_hidden_fail', 0)} | "
            f"{counts.get('visible_fail_hidden_pass', 0)} |"
        )
    lines += [
        "",
        "## Checks",
        "",
    ]
    for row in analysis["checks"]:
        lines.append(f"- {row['check']}: {'passed' if row['passed'] else 'failed'} ({row['detail']})")
    lines += [
        "",
        "## Next Step",
        "",
        analysis["readiness"]["next_step"],
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validation", type=Path, default=DEFAULT_VALIDATION)
    parser.add_argument("--visible", type=Path, default=DEFAULT_VISIBLE)
    parser.add_argument("--generation-audit", type=Path, default=DEFAULT_GENERATION_AUDIT)
    parser.add_argument("--visible-summary", type=Path, default=DEFAULT_VISIBLE_SUMMARY)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    parser.add_argument("--min-hard-negatives", type=int, default=MIN_HARD_NEGATIVES)
    parser.add_argument("--min-projects", type=int, default=MIN_PROJECTS)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    analysis = build_analysis(
        validation_path=args.validation,
        visible_path=args.visible,
        generation_audit_path=args.generation_audit,
        visible_summary_path=args.visible_summary,
        min_hard_negatives=args.min_hard_negatives,
        min_projects=args.min_projects,
    )
    write_json(args.out_json, analysis)
    write_markdown(args.out_md, analysis)
    if args.check and analysis["analysis_status"] != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
