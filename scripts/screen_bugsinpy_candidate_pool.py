from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


LEGACY_OR_NATIVE_TOKENS = {
    "nose": "legacy_nose_dependency",
    "typed-ast": "native_typed_ast_dependency",
    "typed_ast": "native_typed_ast_dependency",
    "tensorflow": "heavy_ml_dependency",
    "torch": "heavy_ml_dependency",
    "cython": "native_build_dependency",
    "mysql": "external_service_dependency",
    "postgres": "external_service_dependency",
    "redis": "external_service_dependency",
    "selenium": "browser_dependency",
}

PREFERRED_PROJECTS = {
    "PySnooper",
    "fastapi",
    "sanic",
    "tornado",
    "scrapy",
    "thefuck",
    "youtube-dl",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_info(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not path.exists():
        return result
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip().strip('"')
    return result


def read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]


def framework_from_commands(commands: list[str]) -> str:
    lowered = "\n".join(commands).lower()
    if "nosetests" in lowered or " nose" in lowered:
        return "nose"
    if "pytest" in lowered or "py.test" in lowered:
        return "pytest"
    if "unittest" in lowered:
        return "unittest"
    return "other"


def blocker_reasons(project: str, requirements: str, commands: list[str], test_file: str) -> list[str]:
    text = "\n".join([requirements.lower(), "\n".join(commands).lower(), test_file.lower()])
    reasons = sorted({reason for token, reason in LEGACY_OR_NATIVE_TOKENS.items() if token in text})
    network_text = "\n".join([_non_self_editable_requirements(project, requirements), "\n".join(commands), test_file])
    if "http://" in network_text.lower() or "https://" in network_text.lower():
        reasons.append("network_reference_in_metadata")
    return reasons


def metadata_notes(project: str, requirements: str) -> list[str]:
    notes: list[str] = []
    for line in requirements.splitlines():
        lowered = line.strip().lower()
        if lowered.startswith("-e git+") and f"#egg={project.lower()}" in lowered:
            notes.append("self_editable_git_requirement")
            break
    return notes


def _non_self_editable_requirements(project: str, requirements: str) -> str:
    retained: list[str] = []
    for line in requirements.splitlines():
        lowered = line.strip().lower()
        if lowered.startswith("-e git+") and f"#egg={project.lower()}" in lowered:
            continue
        retained.append(line)
    return "\n".join(retained)


def score_candidate(project: str, framework: str, blockers: list[str], test_file: str, command_count: int) -> int:
    score = 0
    if project in PREFERRED_PROJECTS:
        score += 3
    if framework == "pytest":
        score += 3
    elif framework == "unittest":
        score += 2
    if blockers:
        score -= 5
    if test_file:
        score += 1
    if command_count <= 2:
        score += 1
    return score


def known_tasks(registry_path: Path) -> set[str]:
    if not registry_path.exists():
        return set()
    registry = read_json(registry_path)
    return {str(task["task_id"]) for task in registry.get("tasks", []) if isinstance(task, dict) and task.get("task_id")}


def collect_candidates(bugsinpy_root: Path, registry_path: Path) -> dict[str, Any]:
    projects_root = bugsinpy_root / "projects"
    known = known_tasks(registry_path)
    records: list[dict[str, Any]] = []
    for project_dir in sorted(path for path in projects_root.iterdir() if path.is_dir()):
        bugs_dir = project_dir / "bugs"
        if not bugs_dir.exists():
            continue
        for bug_dir in sorted(bugs_dir.iterdir(), key=lambda path: int(path.name) if path.name.isdigit() else 10**9):
            if not bug_dir.is_dir():
                continue
            task_id = f"bugsinpy_{project_dir.name}_{bug_dir.name}"
            info = parse_info(bug_dir / "bug.info")
            commands = read_lines(bug_dir / "run_test.sh")
            requirements = (bug_dir / "requirements.txt").read_text(encoding="utf-8", errors="replace") if (bug_dir / "requirements.txt").exists() else ""
            framework = framework_from_commands(commands)
            blockers = blocker_reasons(project_dir.name, requirements, commands, info.get("test_file", ""))
            record = {
                "task_id": task_id,
                "project": project_dir.name,
                "bug_id": bug_dir.name,
                "already_in_registry": task_id in known,
                "python_version": info.get("python_version", ""),
                "test_file": info.get("test_file", ""),
                "run_test_commands": commands,
                "test_framework_hint": framework,
                "metadata_blockers": blockers,
                "metadata_notes": metadata_notes(project_dir.name, requirements),
                "preferred_project": project_dir.name in PREFERRED_PROJECTS,
                "screening_score": score_candidate(
                    project=project_dir.name,
                    framework=framework,
                    blockers=blockers,
                    test_file=info.get("test_file", ""),
                    command_count=len(commands),
                ),
            }
            records.append(record)
    candidates = [record for record in records if not record["already_in_registry"]]
    promising = [
        record
        for record in candidates
        if record["screening_score"] >= 5
        and not record["metadata_blockers"]
        and record["test_framework_hint"] in {"pytest", "unittest"}
    ]
    promising.sort(key=lambda item: (-item["screening_score"], item["project"], int(item["bug_id"]) if str(item["bug_id"]).isdigit() else 10**9))
    return {
        "bugsinpy_root": str(bugsinpy_root),
        "registry_path": str(registry_path),
        "total_tasks": len(records),
        "already_registered_tasks": sum(1 for record in records if record["already_in_registry"]),
        "new_candidate_tasks": len(candidates),
        "promising_candidate_tasks": len(promising),
        "project_counts": dict(sorted(Counter(record["project"] for record in candidates).items())),
        "framework_counts": dict(sorted(Counter(record["test_framework_hint"] for record in candidates).items())),
        "blocker_counts": dict(sorted(Counter(reason for record in candidates for reason in record["metadata_blockers"]).items())),
        "promising_candidates": promising,
        "all_candidates": candidates,
    }


def render_markdown(summary: dict[str, Any], limit: int) -> str:
    lines = [
        "# BugsInPy Candidate Pool Screening",
        "",
        "## Decision Boundary",
        "",
        "This screening follows the decision to stop prioritizing legacy `nose` and",
        "Black `typed_ast` / MSVC repair work. It introduces a broader BugsInPy",
        "candidate pool and applies metadata-level filters before any checkout or",
        "project-level P2P construction.",
        "",
        "## Summary",
        "",
        f"- total BugsInPy tasks: {summary['total_tasks']}",
        f"- already registered tasks: {summary['already_registered_tasks']}",
        f"- new candidate tasks: {summary['new_candidate_tasks']}",
        f"- promising metadata-level candidates: {summary['promising_candidate_tasks']}",
        f"- framework counts: `{summary['framework_counts']}`",
        f"- metadata blocker counts: `{summary['blocker_counts']}`",
        "",
        "## Top Candidates",
        "",
        "| task_id | project | framework | test file | score | run command |",
        "| --- | --- | --- | --- | ---: | --- |",
    ]
    for record in summary["promising_candidates"][:limit]:
        command = "; ".join(record["run_test_commands"])[:140]
        lines.append(
            f"| `{record['task_id']}` | `{record['project']}` | `{record['test_framework_hint']}` | "
            f"`{record['test_file']}` | {record['screening_score']} | `{command}` |"
        )
    lines.extend(
        [
            "",
            "## Admission Rule",
            "",
            "A task from this pool can enter `p2p_broad_main` only after checkout,",
            "F2P validation, project-level P2P-broad construction with at least three",
            "stable P2P tests, candidate generation, and F2P + P2P-broad candidate",
            "revalidation. This metadata screen is not experimental evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Screen broader BugsInPy projects before checkout.")
    parser.add_argument("--bugsinpy-root", required=True)
    parser.add_argument("--registry", default="data/cohorts/task_cohort_registry.json")
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md", required=True)
    parser.add_argument("--top-limit", type=int, default=30)
    args = parser.parse_args()

    summary = collect_candidates(Path(args.bugsinpy_root), Path(args.registry))
    write_json(Path(args.out_json), summary)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(render_markdown(summary, args.top_limit), encoding="utf-8", newline="\n")
    print(json.dumps({key: summary[key] for key in ["total_tasks", "new_candidate_tasks", "promising_candidate_tasks"]}, indent=2))


if __name__ == "__main__":
    main()
