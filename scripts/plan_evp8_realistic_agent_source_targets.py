"""Plan no-API generation targets for the realistic/agent-patch cohort.

This script does not call model APIs and does not generate patches. It reads
the stable task registry, runner-supported source-bug definitions, and the
latest realistic source inventory, then writes a task-level target matrix for
future agent-like patch generation.
"""

from __future__ import annotations

import argparse
import ast
import json
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_source_target_matrix_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_realistic_agent_source_target_matrix_v0_1.md"
REGISTRY = REPO_ROOT / "data" / "cohorts" / "task_cohort_registry.json"
SOURCE_BUGS_FILE = REPO_ROOT / "scripts" / "build_patch_verification_dataset.py"
SOURCE_INVENTORY = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_source_inventory_v0_1.json"

PRIMARY_PROJECTS = {"PySnooper", "cookiecutter", "luigi", "tqdm"}
SECONDARY_PROJECTS = {"httpie"}
EXCLUDED_TASKS = {
    "bugsinpy_httpie_5": "known_hard_generation_case_and_p2p_broad_size_3",
}
PRIMARY_PATCHES_PER_TASK = 9
SECONDARY_PATCHES_PER_TASK = 3


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{display_path(path)} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def display_path(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def load_source_bug_ids() -> set[str]:
    module = ast.parse(SOURCE_BUGS_FILE.read_text(encoding="utf-8"))
    for node in module.body:
        if isinstance(node, ast.Assign) and any(getattr(target, "id", None) == "SOURCE_BUGS" for target in node.targets):
            rows = ast.literal_eval(node.value)
            return {str(row["task_id"]) for row in rows}
    raise ValueError("SOURCE_BUGS assignment not found")


def stable_registry_tasks() -> list[dict[str, Any]]:
    registry = read_json(REGISTRY)
    tasks = registry.get("tasks", [])
    if not isinstance(tasks, list):
        raise ValueError("registry tasks must be a list")
    stable = []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        if task.get("p2p_broad_main_included") is True and task.get("project_level_p2p_status") == "completed":
            stable.append(task)
    return stable


def task_priority(project: str) -> str:
    if project in PRIMARY_PROJECTS:
        return "primary_non_httpie"
    if project in SECONDARY_PROJECTS:
        return "secondary_httpie_cap"
    return "not_targeted_by_current_runner"


def plan_targets() -> dict[str, Any]:
    source_bug_ids = load_source_bug_ids()
    inventory = read_json(SOURCE_INVENTORY)
    source_counts = inventory.get("readiness", {}).get("current_counts", {})
    stable_tasks = stable_registry_tasks()
    targets: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []

    for task in stable_tasks:
        task_id = str(task["task_id"])
        project = str(task["project"])
        collection = task.get("collection_summary") or {}
        supported = task_id in source_bug_ids
        if task_id in EXCLUDED_TASKS:
            exclusions.append(
                {
                    "task_id": task_id,
                    "project": project,
                    "reason": EXCLUDED_TASKS[task_id],
                    "runner_supported": supported,
                }
            )
            continue
        priority = task_priority(project)
        if priority == "not_targeted_by_current_runner" or not supported:
            exclusions.append(
                {
                    "task_id": task_id,
                    "project": project,
                    "reason": "not_supported_by_current_agent_generation_runner",
                    "runner_supported": supported,
                }
            )
            continue
        patches_per_task = PRIMARY_PATCHES_PER_TASK if priority == "primary_non_httpie" else SECONDARY_PATCHES_PER_TASK
        targets.append(
            {
                "task_id": task_id,
                "project": project,
                "priority": priority,
                "patches_per_task": patches_per_task,
                "planned_generation_slots": patches_per_task,
                "p2p_broad_size": collection.get("p2p_broad_size"),
                "existing_candidate_count": collection.get("candidate_count"),
                "test_framework": collection.get("test_framework"),
                "p2p_broad_manifest": task.get("p2p_broad_manifest"),
            }
        )

    project_counts = Counter(row["project"] for row in targets)
    slot_counts = Counter()
    for row in targets:
        slot_counts[row["project"]] += int(row["planned_generation_slots"])
    total_slots = sum(int(row["planned_generation_slots"]) for row in targets)
    primary_slots = sum(int(row["planned_generation_slots"]) for row in targets if row["priority"] == "primary_non_httpie")
    secondary_slots = total_slots - primary_slots
    checks = [
        check("api_call_not_attempted", True, False),
        check("patch_generation_not_attempted", True, False),
        check("candidate_manifest_not_created", True, False),
        check("prompt_text_not_stored", True, False),
        check("source_inventory_detected", inventory.get("inventory_status") == "passed", inventory.get("inventory_status")),
        check("target_project_count_at_least_3", len(project_counts) >= 3, len(project_counts)),
        check("planned_generation_slots_at_least_50", total_slots >= 50, total_slots),
        check("primary_non_httpie_slots_at_least_40", primary_slots >= 40, primary_slots),
    ]
    return {
        "analysis_id": "evp8_realistic_agent_source_target_matrix_v0_1",
        "date": "2026-06-29",
        "scope": {
            "api_call_attempted": False,
            "patch_generation_attempted": False,
            "candidate_manifest_created": False,
            "prompt_text_stored": False,
            "raw_model_outputs_read": False,
        },
        "inputs": {
            "task_registry": display_path(REGISTRY),
            "source_bug_definitions": display_path(SOURCE_BUGS_FILE),
            "source_inventory": display_path(SOURCE_INVENTORY),
        },
        "source_inventory_current_counts": source_counts,
        "strategy": {
            "primary_projects": sorted(PRIMARY_PROJECTS),
            "secondary_projects": sorted(SECONDARY_PROJECTS),
            "primary_patches_per_task": PRIMARY_PATCHES_PER_TASK,
            "secondary_patches_per_task": SECONDARY_PATCHES_PER_TASK,
            "rationale": (
                "Use non-httpie stable P2P tasks as the main source of new agent-like patches, "
                "then add a capped httpie slice only if the non-httpie runner-supported pool cannot "
                "reach the 50-slot source target. The current shortest path uses a larger bounded "
                "variant budget on the six runner-supported non-httpie tasks instead of expanding "
                "the generation runner in this step."
            ),
        },
        "target_summary": {
            "target_task_count": len(targets),
            "target_project_count": len(project_counts),
            "project_task_counts": dict(sorted(project_counts.items())),
            "project_slot_counts": dict(sorted(slot_counts.items())),
            "planned_generation_slots": total_slots,
            "primary_non_httpie_slots": primary_slots,
            "secondary_httpie_slots": secondary_slots,
        },
        "targets": targets,
        "excluded_stable_tasks": exclusions,
        "future_execution_boundary": {
            "next_step": "Run generator dry-run commands first, then seek explicit API authorization for generation only.",
            "dry_run_required_before_api": True,
            "post_generation_required_steps": [
                "validate generated candidates",
                "relabel with evaluator-only hidden outcomes",
                "rerun realistic source inventory",
                "construct separated evaluator/model-visible cohort only if fresh gates pass",
            ],
        },
        "checks": checks,
        "target_matrix_status": "passed" if all(item["passed"] for item in checks) else "failed",
    }


def write_markdown(path: Path, matrix: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = matrix["target_summary"]
    lines = [
        "# EVP-8 Realistic Agent-Patch Source Target Matrix v0.1",
        "",
        "Date: 2026-06-29",
        "",
        "This is a no-API target matrix. It does not generate patches and does not",
        "authorize model calls. It selects stable tasks for future realistic",
        "agent-like patch source construction.",
        "",
        "## Boundary Checks",
        "",
    ]
    for item in matrix["checks"]:
        lines.append(f"- {item['check']}: {'passed' if item['passed'] else 'failed'} ({item['detail']})")
    lines += [
        "",
        "## Strategy",
        "",
        matrix["strategy"]["rationale"],
        "",
        f"- primary projects: {', '.join(matrix['strategy']['primary_projects'])}",
        f"- secondary projects: {', '.join(matrix['strategy']['secondary_projects'])}",
        f"- primary patches per task: {matrix['strategy']['primary_patches_per_task']}",
        f"- secondary patches per task: {matrix['strategy']['secondary_patches_per_task']}",
        "",
        "## Target Summary",
        "",
        f"- target tasks: {summary['target_task_count']}",
        f"- target projects: {summary['target_project_count']}",
        f"- planned generation slots: {summary['planned_generation_slots']}",
        f"- primary non-httpie slots: {summary['primary_non_httpie_slots']}",
        f"- secondary httpie slots: {summary['secondary_httpie_slots']}",
        "",
        "Project slot counts:",
        "",
    ]
    for project, count in summary["project_slot_counts"].items():
        lines.append(f"- `{project}`: {count}")
    lines += [
        "",
        "## Targets",
        "",
        "| task | project | priority | slots | P2P broad size | existing candidates |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ]
    for row in matrix["targets"]:
        lines.append(
            f"| `{row['task_id']}` | `{row['project']}` | `{row['priority']}` | "
            f"{row['planned_generation_slots']} | {row['p2p_broad_size']} | {row['existing_candidate_count']} |"
        )
    lines += [
        "",
        "## Excluded Stable Tasks",
        "",
        "| task | project | reason |",
        "| --- | --- | --- |",
    ]
    for row in matrix["excluded_stable_tasks"]:
        lines.append(f"| `{row['task_id']}` | `{row['project']}` | `{row['reason']}` |")
    lines += [
        "",
        "## Next Gate",
        "",
        matrix["future_execution_boundary"]["next_step"],
        "",
        "Required after generation:",
        "",
    ]
    for step in matrix["future_execution_boundary"]["post_generation_required_steps"]:
        lines.append(f"- {step}")
    lines += [
        "",
        "No verifier API run is allowed from this matrix alone.",
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
    matrix = plan_targets()
    write_json(args.out_json, matrix)
    write_markdown(args.out_md, matrix)
    if args.check and matrix["target_matrix_status"] != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
