from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            value = json.loads(stripped)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number} is not a JSON object")
            records.append(value)
    return records


def write_json(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def project_from_task_dir(task_dir: Path) -> str:
    parts = task_dir.name.split("_")
    if len(parts) < 2:
        return task_dir.name
    return "_".join(parts[:-1])


def checkout_project_root(task_dir: Path, version: str, project: str) -> Path:
    return task_dir / version / project


def has_python_files(root: Path) -> bool:
    return root.exists() and any(path.suffix == ".py" for path in root.rglob("*.py"))


def source_file_count(root: Path) -> int:
    if not root.exists():
        return 0
    return sum(1 for path in root.rglob("*.py") if ".git" not in path.parts and "__pycache__" not in path.parts)


def diff_file_count(task_dir: Path, project: str) -> int:
    buggy = checkout_project_root(task_dir, "buggy", project)
    fixed = checkout_project_root(task_dir, "fixed", project)
    if not buggy.exists() or not fixed.exists():
        return 0
    count = 0
    for fixed_file in fixed.rglob("*.py"):
        if ".git" in fixed_file.parts or "__pycache__" in fixed_file.parts:
            continue
        relative = fixed_file.relative_to(fixed)
        buggy_file = buggy / relative
        if buggy_file.exists() and buggy_file.read_bytes() != fixed_file.read_bytes():
            count += 1
    return count


def seed_task_map(seed_records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for record in seed_records:
        task_id = str(record.get("task_id") or record.get("bug_id") or "")
        if task_id:
            result[task_id] = record
    return result


def screen(source_root: Path, seed_records: list[dict[str, Any]], target_count: int) -> dict[str, Any]:
    seed_by_task = seed_task_map(seed_records)
    records: list[dict[str, Any]] = []
    for task_dir in sorted(path for path in source_root.iterdir() if path.is_dir()):
        project = project_from_task_dir(task_dir)
        task_id = f"bugsinpy_{task_dir.name}"
        buggy_root = checkout_project_root(task_dir, "buggy", project)
        fixed_root = checkout_project_root(task_dir, "fixed", project)
        seed = seed_by_task.get(task_id, {})
        candidate = {
            "task_id": task_id,
            "project": project,
            "buggy_checkout_available": buggy_root.exists(),
            "fixed_checkout_available": fixed_root.exists(),
            "buggy_python_files": source_file_count(buggy_root),
            "fixed_python_files": source_file_count(fixed_root),
            "changed_python_file_count": diff_file_count(task_dir, project),
            "prior_visible_test_command": seed.get("visible_regression_test_command"),
            "prior_visible_test_file": seed.get("visible_test_file"),
            "prior_source_files": seed.get("source_files"),
            "status": "screened_only",
            "next_required_step": "write_or_migrate_patch_verification_oracle_before candidate generation",
        }
        candidate["eligible_for_registry"] = (
            candidate["buggy_checkout_available"]
            and candidate["fixed_checkout_available"]
            and has_python_files(buggy_root)
            and has_python_files(fixed_root)
            and candidate["changed_python_file_count"] > 0
        )
        records.append(candidate)
    eligible = [record for record in records if record["eligible_for_registry"]]
    selected = eligible[:target_count]
    return {
        "source_root_exists": source_root.exists(),
        "screened_task_count": len(records),
        "eligible_task_count": len(eligible),
        "selected_task_count": len(selected),
        "target_count": target_count,
        "project_counts": dict(sorted(Counter(record["project"] for record in selected).items())),
        "selected_tasks": selected,
        "all_screened_tasks": records,
        "boundary": (
            "This is an expansion screening registry, not an expanded patch-verification dataset. "
            "Each selected task still needs a task-specific oracle and candidate validation before "
            "it can support experimental claims."
        ),
    }


def build_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# BugsInPy Expansion Screening",
        "",
        "## Boundary",
        "",
        summary["boundary"],
        "",
        "## Summary",
        "",
        f"- screened tasks: {summary['screened_task_count']}",
        f"- eligible tasks: {summary['eligible_task_count']}",
        f"- selected tasks: {summary['selected_task_count']} / target {summary['target_count']}",
        f"- selected project counts: `{summary['project_counts']}`",
        "",
        "## Selected Task Registry",
        "",
        "| task_id | project | changed Python files | prior visible test | next step |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for task in summary["selected_tasks"]:
        visible = task.get("prior_visible_test_command") or "not migrated"
        lines.append(
            f"| `{task['task_id']}` | `{task['project']}` | {task['changed_python_file_count']} | "
            f"`{visible}` | {task['next_required_step']} |"
        )
    lines.extend(
        [
            "",
            "## Acceptance Rule For Real Expansion",
            "",
            "A screened task becomes part of the expanded experiment only after:",
            "",
            "1. a patch-verification oracle exists in `scripts/oracles/` or an equivalent validated command is wrapped;",
            "2. buggy and fixed/reference behavior are both checked;",
            "3. reference, no-op, irrelevant, and at least one difficult negative candidate are materialized;",
            "4. `validate_patch_candidates.py` reports validated records for all candidates;",
            "5. visible evidence and hidden evaluator fields pass leakage checks.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Screen retained BugsInPy checkouts for the next task expansion.")
    parser.add_argument("--source-root", default="../research/data/real_bugs/bugsinpy_workspace")
    parser.add_argument("--prior-seed-tasks", default="../research/outputs/real_bug_review_pilot_17_patch_context_001/seed/tasks.jsonl")
    parser.add_argument("--target-count", type=int, default=15)
    parser.add_argument("--out-json", default="outputs/bugsinpy_expansion/screening.json")
    parser.add_argument("--out-md", default="docs/experiments/bugsinpy_expansion_screening.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_root = Path(args.source_root)
    if not source_root.exists():
        raise FileNotFoundError(f"source root does not exist: {source_root}")
    summary = screen(source_root, read_jsonl(Path(args.prior_seed_tasks)), args.target_count)
    write_json(Path(args.out_json), summary)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(summary), encoding="utf-8")
    print(
        json.dumps(
            {
                "screened_task_count": summary["screened_task_count"],
                "eligible_task_count": summary["eligible_task_count"],
                "selected_task_count": summary["selected_task_count"],
                "out_md": args.out_md,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
