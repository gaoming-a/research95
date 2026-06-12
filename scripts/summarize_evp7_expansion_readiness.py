"""Summarize readiness for post-EVP-7 controlled expansion."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = REPO_ROOT / "data" / "cohorts" / "task_cohort_registry.json"
DEFAULT_POOL = REPO_ROOT / "outputs" / "candidate_pool_rescreen" / "parallel_latest.json"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "tasks" / "evp7_expansion_readiness.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp7_expansion_readiness.md"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def summarize(registry_path: Path, pool_path: Path) -> dict[str, Any]:
    registry = read_json(registry_path)
    pool = read_json(pool_path)
    tasks = registry.get("tasks", [])
    main_tasks = [task for task in tasks if task.get("p2p_broad_main_included") is True]
    blocked_tasks = [task for task in tasks if task.get("p2p_broad_main_included") is not True]
    project_risks = _project_risks(blocked_tasks)
    promising = pool.get("promising_candidates", [])
    top_by_project = _top_by_project(promising, project_risks)
    return {
        "cohort_id": "EVP-7",
        "current_main_task_count": len(main_tasks),
        "current_main_tasks": [task.get("task_id") for task in main_tasks],
        "current_main_projects": dict(sorted(Counter(task.get("project") for task in main_tasks).items())),
        "registry_blocked_or_pending_count": len(blocked_tasks),
        "registry_blocked_reason_counts": dict(sorted(_blocked_reason_counts(blocked_tasks).items())),
        "candidate_pool": {
            "source": _display(pool_path),
            "total_tasks": pool.get("total_tasks"),
            "already_registered_tasks": pool.get("already_registered_tasks"),
            "new_candidate_tasks": pool.get("new_candidate_tasks"),
            "promising_candidate_tasks": pool.get("promising_candidate_tasks"),
            "framework_counts": pool.get("framework_counts"),
            "metadata_blocker_counts": pool.get("blocker_counts"),
        },
        "top_probe_lanes": top_by_project,
        "readiness_decision": (
            "EVP-7 passed pilot-level G5 signal; expansion should proceed as controlled "
            "project-diverse probes, not blind BugsInPy sweeping or bulk admission."
        ),
        "next_execution_boundary": [
            "Run at most one bounded checkout/F2P/P2P probe per risky project lane at a time.",
            "Parallelize across independent projects only; do not run buggy and fixed checkout for the same task concurrently.",
            "Do not admit a task to p2p_broad_main until F2P, project-level P2P-broad, candidate construction, and candidate revalidation all pass.",
            "Avoid repeating known blockers unless the probe explicitly tests a new bounded policy.",
        ],
    }


def _project_risks(blocked_tasks: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    risks: dict[str, dict[str, Any]] = {}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for task in blocked_tasks:
        grouped[str(task.get("project"))].append(task)
    for project, items in grouped.items():
        risks[project] = {
            "registered_blocked_tasks": len(items),
            "blocked_reasons": dict(sorted(_blocked_reason_counts(items).items())),
            "statuses": dict(sorted(Counter(str(item.get("project_level_p2p_status")) for item in items).items())),
        }
    return risks


def _blocked_reason_counts(tasks: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for task in tasks:
        for reason in task.get("blocked_reason") or []:
            counts[str(reason)] += 1
    return counts


def _top_by_project(promising: list[dict[str, Any]], project_risks: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in promising:
        project = str(record.get("project"))
        if project in seen:
            continue
        seen.add(project)
        selected.append(
            {
                "task_id": record.get("task_id"),
                "project": project,
                "framework": record.get("test_framework_hint"),
                "screening_score": record.get("screening_score"),
                "test_file": record.get("test_file"),
                "run_commands": record.get("run_test_commands") or [],
                "known_project_risk": project_risks.get(project, {"registered_blocked_tasks": 0}),
                "probe_status": "metadata_only_not_admitted",
            }
        )
        if len(selected) >= 8:
            break
    return selected


def render_markdown(summary: dict[str, Any]) -> str:
    pool = summary["candidate_pool"]
    lines = [
        "# EVP-7 Expansion Readiness",
        "",
        "This report is a planning artifact. It does not admit new bugs into the main cohort.",
        "",
        "## Current Cohort",
        "",
        f"- Main tasks: {summary['current_main_task_count']}",
        f"- Main projects: `{json.dumps(summary['current_main_projects'], sort_keys=True)}`",
        f"- Blocked or pending registry tasks: {summary['registry_blocked_or_pending_count']}",
        "",
        "## Candidate Pool",
        "",
        f"- Source: `{pool['source']}`",
        f"- Total BugsInPy tasks: {pool['total_tasks']}",
        f"- Already registered tasks: {pool['already_registered_tasks']}",
        f"- New candidate tasks: {pool['new_candidate_tasks']}",
        f"- Metadata-promising candidates: {pool['promising_candidate_tasks']}",
        f"- Framework counts: `{json.dumps(pool['framework_counts'], sort_keys=True)}`",
        f"- Metadata blocker counts: `{json.dumps(pool['metadata_blocker_counts'], sort_keys=True)}`",
        "",
        "## Probe Lanes",
        "",
        "| Task | Project | Framework | Score | Known blocked tasks | Probe status |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    for lane in summary["top_probe_lanes"]:
        risk = lane["known_project_risk"]
        lines.append(
            f"| `{lane['task_id']}` | `{lane['project']}` | `{lane['framework']}` | "
            f"{lane['screening_score']} | {risk.get('registered_blocked_tasks', 0)} | "
            f"`{lane['probe_status']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            summary["readiness_decision"],
            "",
            "## Execution Boundary",
            "",
        ]
    )
    for item in summary["next_execution_boundary"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def _display(path: Path) -> str:
    absolute = path if path.is_absolute() else REPO_ROOT / path
    try:
        return str(absolute.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--pool", type=Path, default=DEFAULT_POOL)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    args = parser.parse_args()

    summary = summarize(args.registry, args.pool)
    write_json(args.json_out, summary)
    write_text(args.md_out, render_markdown(summary))
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
