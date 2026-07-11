"""Freeze and validate P2 transform families on excluded development tasks."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXCLUSIONS = ROOT / "data/protocols/dsa_p2_development_exclusion_registry_v0_1.json"
SOURCE_SELECTION = ROOT / "data/protocols/dsa_p2_source_selection_v0_1.json"
REGISTRY_OUT = ROOT / "data/protocols/dsa_p2_transform_registry_v0_1.json"
VALIDATION_OUT = ROOT / "data/protocols/dsa_p2_transform_validation_v0_1.json"

TRANSFORMS = [
    {
        "transform_id": "T1_omit_secondary_source_file",
        "priority": 1,
        "applicability": "reference diff changes at least two files",
        "operation": "retain the first hash-ordered changed source file and omit one later changed source file",
        "scientific_intent": "partial fix that leaves one independently changed source surface unresolved",
    },
    {
        "transform_id": "T2_omit_secondary_hunk",
        "priority": 2,
        "applicability": "reference diff contains at least two hunks",
        "operation": "retain all but one hash-ordered non-test hunk",
        "scientific_intent": "partial fix that omits one localized semantic component",
    },
    {
        "transform_id": "T3_omit_secondary_edit_block",
        "priority": 3,
        "applicability": "reference diff contains at least two separated edit blocks",
        "operation": "retain all but one hash-ordered edit block and recompute the unified-diff hunk header",
        "scientific_intent": "within-hunk partial fix without adding new code",
    },
    {
        "transform_id": "T4_partial_multiline_reversion",
        "priority": 4,
        "applicability": "reference diff changes at least three non-header lines",
        "operation": "restore one hash-ordered reference edit while retaining at least one other reference edit",
        "scientific_intent": "minimal partial reversion for a multi-line reference fix",
    },
]


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def diff_shape(text: str) -> dict[str, int]:
    lines = text.splitlines()
    file_count = sum(line.startswith("diff --git ") for line in lines)
    hunk_count = sum(line.startswith("@@ ") for line in lines)
    edit_block_count = 0
    changed_line_count = 0
    in_edit = False
    for line in lines:
        changed = (
            (line.startswith("+") and not line.startswith("+++"))
            or (line.startswith("-") and not line.startswith("---"))
        )
        if changed:
            changed_line_count += 1
            if not in_edit:
                edit_block_count += 1
                in_edit = True
        elif not line.startswith("\\"):
            in_edit = False
    return {
        "file_count": file_count,
        "hunk_count": hunk_count,
        "edit_block_count": edit_block_count,
        "changed_line_count": changed_line_count,
    }


def select_transform(shape: dict[str, int]) -> str | None:
    if shape["file_count"] >= 2:
        return TRANSFORMS[0]["transform_id"]
    if shape["hunk_count"] >= 2:
        return TRANSFORMS[1]["transform_id"]
    if shape["edit_block_count"] >= 2:
        return TRANSFORMS[2]["transform_id"]
    if shape["changed_line_count"] >= 3:
        return TRANSFORMS[3]["transform_id"]
    return None


def task_path(catalog: Path, task_id: str) -> Path:
    project, bug_id = task_id.removeprefix("bugsinpy_").rsplit("_", 1)
    return catalog / "projects" / project / "bugs" / bug_id / "bug_patch.txt"


def registry() -> dict[str, Any]:
    return {
        "registry_id": "dsa_p2_transform_registry_v0_1",
        "frozen_date": "2026-07-11",
        "status": "frozen_for_p3_author_review",
        "priority_rule": "apply the first applicable transform by ascending priority; never choose by candidate outcome",
        "transforms": TRANSFORMS,
        "source_task_boundary": {
            "design_and_validation_tasks": "development exclusion registry only",
            "primary_or_reserve_transform_application_in_p2": False,
            "first_primary_or_reserve_application_phase": "P4 after P3 author sign-off",
            "candidate_with_no_applicable_transform": "replace only by frozen reserve order in P4",
        },
        "candidate_acceptance_rule": {
            "oracle_positive": "official reference fix after dual-environment visible and hidden checks",
            "hard_negative": "transformed patch passes all frozen visible checks and fails at least one frozen independent hidden oracle in both environments",
            "discard_without_reclassification": [
                "transformed patch fails a visible check",
                "transformed patch passes all hidden checks",
                "environment disagreement",
                "transform is not applicable",
            ],
        },
        "prohibited_adaptation": [
            "do not change transform priority after observing a source-task outcome",
            "do not add a task-specific transform",
            "do not retain a candidate because it produces a larger model effect",
            "do not inspect model output before candidate labels are frozen",
        ],
    }


def validate(catalog: Path) -> dict[str, Any]:
    exclusions = read_json(EXCLUSIONS)
    selection = read_json(SOURCE_SELECTION)
    development = set(exclusions["excluded_task_ids"])
    selected = {
        item["task_id"]
        for protocol in (selection["regular"], selection["short"])
        for role in ("primary", "reserve")
        for item in protocol[role]
    }
    records: list[dict[str, Any]] = []
    for task_id in sorted(development):
        path = task_path(catalog, task_id)
        if not path.exists():
            records.append({"task_id": task_id, "reference_diff_available": False})
            continue
        content = path.read_bytes()
        shape = diff_shape(content.decode("utf-8", errors="replace"))
        records.append(
            {
                "task_id": task_id,
                "reference_diff_available": True,
                "reference_diff_sha256": sha256_bytes(content),
                "shape": shape,
                "selected_transform_id": select_transform(shape),
                "transform_materialized": False,
                "hidden_result_observed": False,
            }
        )
    transform_counts = Counter(
        record.get("selected_transform_id")
        for record in records
        if record.get("selected_transform_id")
    )
    checks = {
        "development_source_overlap_zero": not (development & selected),
        "all_validation_records_are_development_tasks": all(record["task_id"] in development for record in records),
        "reference_diff_available_for_all_development_tasks": all(record["reference_diff_available"] for record in records),
        "each_transform_has_at_least_three_development_examples": all(
            transform_counts[transform["transform_id"]] >= 3 for transform in TRANSFORMS
        ),
        "no_transform_materialized_in_p2": all(not record.get("transform_materialized", False) for record in records),
        "no_hidden_result_observed": all(not record.get("hidden_result_observed", False) for record in records),
    }
    return {
        "validation_id": "dsa_p2_transform_validation_v0_1",
        "validation_date": "2026-07-11",
        "status": "passed" if all(checks.values()) else "failed",
        "catalog_commit": subprocess_git_head(catalog),
        "development_task_count": len(development),
        "selected_source_task_count": len(selected),
        "applicable_development_task_count": sum(record.get("selected_transform_id") is not None for record in records),
        "atomic_patch_not_applicable_count": sum(
            record.get("reference_diff_available") and record.get("selected_transform_id") is None
            for record in records
        ),
        "selected_transform_counts": dict(sorted(transform_counts.items())),
        "checks": checks,
        "records": records,
        "boundary": "Validation checks structural applicability only on excluded development reference diffs; no transformed candidate or outcome is generated.",
    }


def subprocess_git_head(catalog: Path) -> str:
    import subprocess

    return subprocess.check_output(
        ["git", "-C", str(catalog), "rev-parse", "HEAD"], text=True, encoding="utf-8"
    ).strip()


def serialize(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog-root", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    catalog = Path(args.catalog_root).resolve()
    outputs = {REGISTRY_OUT: serialize(registry()), VALIDATION_OUT: serialize(validate(catalog))}
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    else:
        stale = [str(path.relative_to(ROOT)) for path, content in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            raise SystemExit(f"stale or missing outputs: {stale}")
        if read_json(VALIDATION_OUT)["status"] != "passed":
            raise SystemExit("transform validation did not pass")
    summary = read_json(VALIDATION_OUT) if VALIDATION_OUT.exists() else validate(catalog)
    print(json.dumps({"status": summary["status"], "selected_transform_counts": summary["selected_transform_counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
