"""Build the no-API DSA P2 source frame from an official BugsInPy snapshot."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXCLUSIONS = ROOT / "data/protocols/dsa_p2_development_exclusion_registry_v0_1.json"
FRAME_OUT = ROOT / "data/protocols/dsa_p2_source_frame_v0_1.json"
SELECTION_OUT = ROOT / "data/protocols/dsa_p2_source_selection_v0_1.json"
SEED_TEXT = "DSA-2026-P2-SOURCE-FRAME-20260711-V1"
SEED_SHA256 = hashlib.sha256(SEED_TEXT.encode()).hexdigest()
HIGH_ENVIRONMENT_RISK_TOKENS = {
    "tensorflow": "heavy_tensorflow_stack",
    "torch": "heavy_torch_stack",
    "cython": "native_extension_build",
    "typed_ast": "native_typed_ast_build",
    "mysql": "external_database",
    "postgres": "external_database",
    "redis": "external_service",
    "selenium": "browser_service",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def parse_assignments(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"')
    return values


def read_nonempty_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]


def framework(commands: list[str]) -> str:
    lowered = "\n".join(commands).lower()
    if "pytest" in lowered or "py.test" in lowered:
        return "pytest"
    if "unittest" in lowered:
        return "unittest"
    if "nose" in lowered:
        return "nose"
    return "other"


def git_head(catalog: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(catalog), "rev-parse", "HEAD"], text=True, encoding="utf-8"
    ).strip()


def load_reproduction_results(path: Path) -> dict[tuple[str, str], str]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {
            (row["repo"], row["bugid"]): row["result"]
            for row in csv.DictReader(handle)
        }


def stable_key(namespace: str, value: str) -> str:
    return hashlib.sha256(f"{SEED_SHA256}|{namespace}|{value}".encode()).hexdigest()


def valid_git_object_id(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-fA-F]{7,40}", value))


def collect_frame(catalog: Path, reproduction: Path) -> dict[str, Any]:
    exclusions = read_json(EXCLUSIONS)
    excluded_tasks = set(exclusions["excluded_task_ids"])
    excluded_projects = set(exclusions["base_project_exclusions"])
    records: list[dict[str, Any]] = []
    improved_buggy = load_reproduction_results(reproduction / "new-conda-buggy.csv")
    improved_fixed = load_reproduction_results(reproduction / "new-conda-fixed.csv")
    original_buggy = load_reproduction_results(reproduction / "old-virtualenv-buggy.csv")
    original_fixed = load_reproduction_results(reproduction / "old-virtualenv-fixed.csv")
    projects_root = catalog / "projects"
    for project_dir in sorted(path for path in projects_root.iterdir() if path.is_dir()):
        project_info = parse_assignments(project_dir / "project.info")
        bugs_root = project_dir / "bugs"
        if not bugs_root.exists():
            continue
        bug_dirs = sorted(
            (path for path in bugs_root.iterdir() if path.is_dir() and path.name.isdigit()),
            key=lambda path: int(path.name),
        )
        for bug_dir in bug_dirs:
            info = parse_assignments(bug_dir / "bug.info")
            commands = read_nonempty_lines(bug_dir / "run_test.sh")
            requirements = (bug_dir / "requirements.txt").read_text(encoding="utf-8", errors="replace") if (bug_dir / "requirements.txt").exists() else ""
            setup_lines = read_nonempty_lines(bug_dir / "setup.sh")
            dependency_text = f"{requirements}\n{' '.join(setup_lines)}".lower()
            risk_tags = sorted(
                {risk for token, risk in HIGH_ENVIRONMENT_RISK_TOKENS.items() if token in dependency_text}
            )
            task_id = f"bugsinpy_{project_dir.name}_{bug_dir.name}"
            reproduction_key = (project_dir.name, bug_dir.name)
            improved_reproduction_passed = (
                improved_buggy.get(reproduction_key) == "fail"
                and improved_fixed.get(reproduction_key) == "pass"
            )
            completeness = {
                "project_repository_declared": bool(project_info.get("github_url")),
                "project_status_ok": project_info.get("status") == "OK",
                "python_version_declared": bool(info.get("python_version")),
                "buggy_commit_declared": valid_git_object_id(info.get("buggy_commit_id", "")),
                "fixed_commit_declared": valid_git_object_id(info.get("fixed_commit_id", "")),
                "test_file_declared": bool(info.get("test_file")),
                "f2p_command_declared": bool(commands),
                "supported_test_framework": framework(commands) in {"pytest", "unittest"},
            }
            eligible = (
                project_dir.name not in excluded_projects
                and task_id not in excluded_tasks
                and all(completeness.values())
                and improved_reproduction_passed
            )
            records.append(
                {
                    "task_id": task_id,
                    "project": project_dir.name,
                    "bug_id": int(bug_dir.name),
                    "project_repository": project_info.get("github_url"),
                    "python_version": info.get("python_version"),
                    "buggy_commit_id": info.get("buggy_commit_id"),
                    "fixed_commit_id": info.get("fixed_commit_id"),
                    "declared_test_file": info.get("test_file"),
                    "declared_f2p_commands": commands,
                    "test_framework": framework(commands),
                    "environment_risk_tags": risk_tags,
                    "external_reproduction_evidence": {
                        "improved_conda_buggy": improved_buggy.get(reproduction_key),
                        "improved_conda_fixed": improved_fixed.get(reproduction_key),
                        "improved_conda_expected_pair_passed": improved_reproduction_passed,
                        "original_virtualenv_buggy": original_buggy.get(reproduction_key),
                        "original_virtualenv_fixed": original_fixed.get(reproduction_key),
                        "original_environment_decay_observed": (
                            original_buggy.get(reproduction_key) != "fail"
                            or original_fixed.get(reproduction_key) != "pass"
                        ),
                    },
                    "metadata_completeness": completeness,
                    "excluded_by_project": project_dir.name in excluded_projects,
                    "excluded_by_task": task_id in excluded_tasks,
                    "eligible_for_source_frame": eligible,
                    "visible_oracle_source": "official declared F2P command(s)",
                    "hidden_oracle_source_plan": "project regression scope excluding declared F2P nodes; freeze in P3 and materialize in P4",
                    "candidate_hidden_result_observed": False,
                    "transform_applied": False,
                }
            )
    eligible_records = [record for record in records if record["eligible_for_source_frame"]]
    return {
        "frame_id": "dsa_p2_source_frame_v0_1",
        "created_date": "2026-07-11",
        "status": "source_level_feasibility_complete_p4_dual_clean_rerun_required",
        "official_source": {
            "repository": "https://github.com/soarsmu/bugsinpy.git",
            "catalog_commit": git_head(catalog),
            "catalog_task_count": len(records),
        },
        "reproduction_source": {
            "repository": "https://github.com/reproducing-research-projects/BugsInPy.git",
            "catalog_commit": git_head(reproduction),
            "improved_buggy_csv_sha256": hashlib.sha256((reproduction / "new-conda-buggy.csv").read_bytes()).hexdigest(),
            "improved_fixed_csv_sha256": hashlib.sha256((reproduction / "new-conda-fixed.csv").read_bytes()).hexdigest(),
            "role": "P2 source-level expected buggy-fail/fixed-pass feasibility only; two fresh clean-environment reruns remain mandatory in P4",
        },
        "selection_seed_sha256": SEED_SHA256,
        "development_exclusion_registry": EXCLUSIONS.relative_to(ROOT).as_posix(),
        "record_count": len(records),
        "eligible_record_count": len(eligible_records),
        "eligible_project_counts": dict(sorted(Counter(record["project"] for record in eligible_records).items(), key=lambda item: item[0].lower())),
        "risk_tag_counts": dict(sorted(Counter(tag for record in eligible_records for tag in record["environment_risk_tags"]).items())),
        "records": records,
        "data_boundary": {
            "legacy_paper_metric_read": False,
            "legacy_raw_output_read": False,
            "model_api_called": False,
            "prompt_created": False,
            "candidate_transform_applied": False,
            "candidate_hidden_result_read": False,
        },
    }


def select_round_robin(
    records: list[dict[str, Any]], projects: list[str], primary_count: int, reserve_count: int
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    project_order = sorted(projects, key=lambda project: stable_key("project", project))
    queues = {
        project: sorted(
            [record for record in records if record["project"] == project],
            key=lambda record: stable_key(project, record["task_id"]),
        )
        for project in project_order
    }
    if reserve_count < len(project_order):
        raise ValueError("reserve count must cover every selected project")
    protected_reserve = {project: queues[project].pop() for project in project_order}
    primary: list[dict[str, Any]] = []
    primary_counts: Counter[str] = Counter()
    while len(primary) < primary_count:
        progressed = False
        for project in project_order:
            if len(primary) >= primary_count:
                break
            if primary_counts[project] >= 4 or not queues[project]:
                continue
            primary.append(queues[project].pop(0))
            primary_counts[project] += 1
            progressed = True
        if not progressed:
            raise ValueError("insufficient primary capacity under four-task project cap")
    reserve: list[dict[str, Any]] = [protected_reserve[project] for project in project_order]
    reserve_counts: Counter[str] = Counter({project: 1 for project in project_order})
    while len(reserve) < reserve_count:
        progressed = False
        for project in project_order:
            if len(reserve) >= reserve_count:
                break
            if reserve_counts[project] >= 2 or not queues[project]:
                continue
            reserve.append(queues[project].pop(0))
            reserve_counts[project] += 1
            progressed = True
        if not progressed:
            raise ValueError("insufficient reserve capacity under two-task reserve cap")
    return primary, reserve


def compact(record: dict[str, Any], role: str, order: int) -> dict[str, Any]:
    return {
        "order": order,
        "role": role,
        "task_id": record["task_id"],
        "project": record["project"],
        "bug_id": record["bug_id"],
        "python_version": record["python_version"],
        "environment_risk_tags": record["environment_risk_tags"],
        "source_level_environment_gate": "external improved-environment buggy-fail/fixed-pass evidence passed; fresh dual-clean rerun required in P4",
        "transform_applied": False,
        "candidate_hidden_result_observed": False,
    }


def protocol_selection(
    name: str,
    records: list[dict[str, Any]],
    projects: list[str],
    primary_count: int,
    reserve_count: int,
    minimum_projects: int,
) -> dict[str, Any]:
    primary, reserve = select_round_robin(records, projects, primary_count, reserve_count)
    primary_project_counts = Counter(record["project"] for record in primary)
    return {
        "protocol": name,
        "selection_status": "source_order_frozen_p2_source_level_gate_passed",
        "project_pool": sorted(projects, key=str.lower),
        "primary_count": len(primary),
        "reserve_count": len(reserve),
        "primary_project_count": len(primary_project_counts),
        "primary_project_counts": dict(sorted(primary_project_counts.items(), key=lambda item: item[0].lower())),
        "minimum_projects": minimum_projects,
        "four_task_primary_project_cap_passed": max(primary_project_counts.values()) <= 4,
        "primary": [compact(record, "primary", index) for index, record in enumerate(primary, 1)],
        "reserve": [compact(record, "reserve", index) for index, record in enumerate(reserve, 1)],
    }


def build_selection(frame: dict[str, Any]) -> dict[str, Any]:
    eligible = [record for record in frame["records"] if record["eligible_for_source_frame"]]
    all_projects = sorted({record["project"] for record in eligible}, key=str.lower)
    low_risk_projects = sorted(
        {
            project
            for project in all_projects
            if any(record["project"] == project for record in eligible)
            and not any(record["project"] == project and record["environment_risk_tags"] for record in eligible)
        },
        key=str.lower,
    )
    regular = protocol_selection("Regular", eligible, all_projects, 30, 10, 8)
    short = protocol_selection("Short", eligible, low_risk_projects, 20, 8, 6)
    return {
        "selection_id": "dsa_p2_source_selection_v0_1",
        "created_date": "2026-07-11",
        "status": "source_selection_frozen_protocol_decision_recorded_separately",
        "source_frame": FRAME_OUT.relative_to(ROOT).as_posix(),
        "selection_seed_sha256": SEED_SHA256,
        "selection_rule": "hash-seeded project/task order; reserve one task per project before round-robin primary selection; max four primary tasks and two reserves per project",
        "regular": regular,
        "short": short,
        "gate": {
            "task_overlap_with_development": 0,
            "project_overlap_with_base_excluded_projects": 0,
            "regular_capacity_passed": regular["primary_project_count"] >= 8,
            "short_capacity_passed": short["primary_project_count"] >= 6,
            "source_environment_gate_passed": True,
        },
        "boundary": "This freezes source order only. It does not admit a task, apply a transform, inspect candidate hidden results, create a prompt, or authorize an API call.",
    }


def serialize(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog-root", required=True)
    parser.add_argument("--reproduction-root", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    frame = collect_frame(
        Path(args.catalog_root).resolve(), Path(args.reproduction_root).resolve()
    )
    selection = build_selection(frame)
    expected = {FRAME_OUT: serialize(frame), SELECTION_OUT: serialize(selection)}
    if args.write:
        for path, content in expected.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    else:
        stale = [str(path.relative_to(ROOT)) for path, content in expected.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            raise SystemExit(f"stale or missing outputs: {stale}")
    print(
        json.dumps(
            {
                "eligible_record_count": frame["eligible_record_count"],
                "eligible_project_counts": frame["eligible_project_counts"],
                "regular_primary_projects": selection["regular"]["primary_project_counts"],
                "short_primary_projects": selection["short"]["primary_project_counts"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
