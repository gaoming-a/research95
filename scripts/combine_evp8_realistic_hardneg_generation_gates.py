"""Combine fresh realistic hard-negative gate analyses."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GATES = [
    REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_generation_gate_v0_1.json",
    REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_generation_supplement_001_gate_v0_1.json",
    REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_generation_deepseek_supplement_001_gate_v0_1.json",
]
DEFAULT_OUT_JSON = REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_combined_generation_gate_v0_1.json"
DEFAULT_OUT_MD = REPO_ROOT / "docs" / "experiments" / "evp8_realistic_hardneg_combined_generation_gate_v0_1.md"
MIN_HARD_NEGATIVES = 30
MIN_PROJECTS = 3


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


def counter_dict(counter: Counter[str]) -> dict[str, int]:
    return dict(sorted(counter.items()))


def add_nested(target: dict[str, Counter[str]], source: dict[str, Any]) -> None:
    for key, counts in source.items():
        if not isinstance(counts, dict):
            continue
        for label, value in counts.items():
            target[str(key)][str(label)] += int(value)


def build_combined(gate_paths: list[Path], min_hard_negatives: int, min_projects: int) -> dict[str, Any]:
    analyses = [read_json(path) for path in gate_paths]
    class_counts: Counter[str] = Counter()
    by_task: dict[str, Counter[str]] = defaultdict(Counter)
    by_project: dict[str, Counter[str]] = defaultdict(Counter)
    candidate_count = 0
    for analysis in analyses:
        candidate_count += int(analysis.get("candidate_count", 0))
        for key, value in (analysis.get("classification_counts") or {}).items():
            class_counts[str(key)] += int(value)
        add_nested(by_task, analysis.get("classification_by_task") or {})
        add_nested(by_project, analysis.get("classification_by_project") or {})

    hard_negative_projects = sorted(
        project for project, counts in by_project.items() if counts.get("visible_pass_hidden_fail", 0) > 0
    )
    hard_negative_tasks = sorted(
        task for task, counts in by_task.items() if counts.get("visible_pass_hidden_fail", 0) > 0
    )
    hard_negative_count = class_counts.get("visible_pass_hidden_fail", 0)
    gate_passed = hard_negative_count >= min_hard_negatives and len(hard_negative_projects) >= min_projects
    checks = [
        check("api_call_not_attempted_by_combiner", True, False),
        check("raw_model_outputs_not_read", True, False),
        check("patch_text_not_stored", True, False),
        check("input_gate_analyses_passed", all(a.get("analysis_status") == "passed" for a in analyses), [a.get("analysis_status") for a in analyses]),
        check("hard_negative_min_count_gate", hard_negative_count >= min_hard_negatives, hard_negative_count),
        check("hard_negative_min_project_gate", len(hard_negative_projects) >= min_projects, hard_negative_projects),
    ]
    return {
        "analysis_id": "evp8_realistic_hardneg_combined_generation_gate_v0_1",
        "date": datetime.now().date().isoformat(),
        "inputs": [display_path(path) for path in gate_paths],
        "scope": {
            "api_call_attempted": False,
            "raw_model_outputs_read": False,
            "patch_text_stored": False,
            "prompt_text_stored": False,
        },
        "candidate_count": candidate_count,
        "classification_counts": counter_dict(class_counts),
        "classification_by_project": {project: counter_dict(counts) for project, counts in sorted(by_project.items())},
        "classification_by_task": {task: counter_dict(counts) for task, counts in sorted(by_task.items())},
        "hard_negative_gate": {
            "required_property": "patch_applied && declared_visible_tests_passed && hidden_oracle_failed",
            "visible_pass_hidden_fail_count": hard_negative_count,
            "visible_pass_hidden_fail_projects": hard_negative_projects,
            "visible_pass_hidden_fail_tasks": hard_negative_tasks,
            "minimum_count": min_hard_negatives,
            "minimum_projects": min_projects,
            "passed": gate_passed,
        },
        "readiness": {
            "ready_for_verifier_api": gate_passed,
            "next_step": (
                "Construct separated cohort and visible-tool headroom gate."
                if gate_passed
                else "Do not run verifier API. Redesign source strategy for a third project or revise the paper claim to report a two-project hard-negative cohort."
            ),
        },
        "checks": checks,
        "analysis_status": "passed" if all(item["passed"] for item in checks[:4]) else "blocked",
    }


def write_markdown(path: Path, combined: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    gate = combined["hard_negative_gate"]
    lines = [
        "# EVP-8 Realistic Hard-Negative Combined Generation Gate v0.1",
        "",
        f"Date: {combined['date']}",
        "",
        "This combines raw-output-free gate analyses. It does not read raw",
        "responses, prompt text, or patch text.",
        "",
        f"- status: `{combined['analysis_status']}`",
        f"- candidates: {combined['candidate_count']}",
        f"- visible-pass/hidden-fail: {gate['visible_pass_hidden_fail_count']}",
        f"- projects: {', '.join(f'`{project}`' for project in gate['visible_pass_hidden_fail_projects']) or 'none'}",
        f"- gate passed: `{gate['passed']}`",
        f"- ready for verifier API: `{combined['readiness']['ready_for_verifier_api']}`",
        "",
        "## Classification Counts",
        "",
    ]
    for key, value in combined["classification_counts"].items():
        lines.append(f"- `{key}`: {value}")
    lines += [
        "",
        "## By Project",
        "",
        "| project | visible-pass hidden-fail | visible-pass hidden-pass | visible-fail hidden-fail | visible-fail hidden-pass |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for project, counts in combined["classification_by_project"].items():
        lines.append(
            f"| `{project}` | {counts.get('visible_pass_hidden_fail', 0)} | "
            f"{counts.get('visible_pass_hidden_pass', 0)} | "
            f"{counts.get('visible_fail_hidden_fail', 0)} | "
            f"{counts.get('visible_fail_hidden_pass', 0)} |"
        )
    lines += ["", "## Checks", ""]
    for row in combined["checks"]:
        lines.append(f"- {row['check']}: {'passed' if row['passed'] else 'failed'} ({row['detail']})")
    lines += ["", "## Next Step", "", combined["readiness"]["next_step"], ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate", type=Path, action="append", default=None)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    parser.add_argument("--min-hard-negatives", type=int, default=MIN_HARD_NEGATIVES)
    parser.add_argument("--min-projects", type=int, default=MIN_PROJECTS)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    combined = build_combined(args.gate or DEFAULT_GATES, args.min_hard_negatives, args.min_projects)
    write_json(args.out_json, combined)
    write_markdown(args.out_md, combined)
    if args.check and combined["analysis_status"] != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
