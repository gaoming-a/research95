"""Build the P2 development-task exclusion projection.

Only task identifiers are projected from legacy engineering registries.  No
model output, paper-facing metric, prompt, or patch payload is read.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
P1_REGISTRY = ROOT / "data/protocols/dsa_legacy_task_exclusion_registry_v0_1.json"
ENGINEERING_REGISTRY = ROOT / "data/cohorts/task_cohort_registry.json"
P2P_SCOPE_DIR = ROOT / "data/p2p_scopes"
OUT = ROOT / "data/protocols/dsa_p2_development_exclusion_registry_v0_1.json"

# These checkout probes were recorded before they received a durable P2P scope
# or cohort-registry entry.  They are task IDs only and are excluded
# conservatively; they do not provide source-selection evidence.
EARLY_PROBE_TASK_IDS = {
    "bugsinpy_ansible_1",
    "bugsinpy_fastapi_4",
    "bugsinpy_luigi_1",
    "bugsinpy_scrapy_2",
    "bugsinpy_youtube-dl_3",
    "bugsinpy_youtube-dl_10",
    "bugsinpy_youtube-dl_13",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def projection_hash(values: list[str]) -> str:
    return hashlib.sha256(("\n".join(sorted(values)) + "\n").encode()).hexdigest()


def build() -> dict[str, Any]:
    p1 = read_json(P1_REGISTRY)
    engineering = read_json(ENGINEERING_REGISTRY)
    p1_tasks = {str(value) for value in p1["excluded_task_ids"]}
    registered_tasks = {
        str(record["task_id"])
        for record in engineering.get("tasks", [])
        if isinstance(record, dict) and record.get("task_id")
    }
    p2p_tasks: set[str] = set()
    for path in P2P_SCOPE_DIR.glob("bugsinpy_*"):
        match = re.match(r"(bugsinpy_.+?_[0-9]+)(?:_|\.)", path.name)
        if match:
            p2p_tasks.add(match.group(1))
    union = p1_tasks | registered_tasks | p2p_tasks | EARLY_PROBE_TASK_IDS
    project_counts: dict[str, int] = {}
    for task_id in union:
        project = task_id.removeprefix("bugsinpy_").rsplit("_", 1)[0]
        project_counts[project] = project_counts.get(project, 0) + 1
    return {
        "registry_id": "dsa_p2_development_exclusion_registry_v0_1",
        "effective_date": "2026-07-11",
        "status": "active",
        "purpose": "source exclusion and transform development only",
        "base_project_exclusions": sorted(p1["excluded_projects"], key=str.lower),
        "base_project_exclusion_count": len(p1["excluded_projects"]),
        "excluded_task_ids": sorted(union),
        "excluded_task_count": len(union),
        "excluded_task_project_counts": dict(sorted(project_counts.items(), key=lambda item: item[0].lower())),
        "task_id_projection_sources": [
            {
                "path": P1_REGISTRY.relative_to(ROOT).as_posix(),
                "projected_field": "excluded_task_ids",
                "count": len(p1_tasks),
                "projection_sha256": projection_hash(list(p1_tasks)),
            },
            {
                "path": ENGINEERING_REGISTRY.relative_to(ROOT).as_posix(),
                "projected_field": "tasks[].task_id",
                "count": len(registered_tasks),
                "projection_sha256": projection_hash(list(registered_tasks)),
            },
            {
                "path": P2P_SCOPE_DIR.relative_to(ROOT).as_posix(),
                "projected_field": "task IDs parsed from filenames only",
                "count": len(p2p_tasks),
                "projection_sha256": projection_hash(list(p2p_tasks)),
            },
            {
                "path": "frozen_early_probe_task_id_set",
                "projected_field": "task IDs only",
                "count": len(EARLY_PROBE_TASK_IDS),
                "projection_sha256": projection_hash(list(EARLY_PROBE_TASK_IDS)),
            },
        ],
        "data_boundary": {
            "paper_facing_metrics_read": False,
            "model_outputs_read": False,
            "raw_outputs_read": False,
            "prompt_text_read": False,
            "patch_text_read": False,
        },
        "not_a_candidate_pool": True,
    }


def serialize(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = serialize(build())
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(content, encoding="utf-8")
    elif not OUT.exists() or OUT.read_text(encoding="utf-8") != content:
        raise SystemExit(f"stale or missing output: {OUT.relative_to(ROOT)}")
    print(json.dumps({"status": "passed", "excluded_task_count": build()["excluded_task_count"]}))


if __name__ == "__main__":
    main()
