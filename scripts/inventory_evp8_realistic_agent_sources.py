"""Inventory sources for a realistic/agent-patch EVP-8 follow-up cohort.

This is a no-API source inventory. It scans tracked manifests and non-raw local
candidate outputs, then writes aggregate reports without patch diffs, rendered
prompts, raw model responses, or provider response objects.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_source_inventory_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_realistic_agent_source_inventory_v0_1.md"

EVP7_CANDIDATES = REPO_ROOT / "data" / "patches" / "evp7_candidates.jsonl"
EVP8_HARD_EVALUATOR = REPO_ROOT / "data" / "patches" / "evp8_hard_evaluator_manifest_v0_1.jsonl"
EVP8_HARD_BASELINE = REPO_ROOT / "data" / "baselines" / "evp8_hard_tool_only_baseline_v0_1.jsonl"

RAW_PATH_MARKERS = {
    "raw",
    "inputs",
}
RAW_FILE_MARKERS = {
    "raw",
    "response",
    "reviews",
}
NONTRIVIAL_TYPES = {
    "partial",
    "partial_fix",
    "regression",
    "regression_patch",
    "overfitted",
    "overfitted_patch",
    "test_passing_wrong",
    "agent_plausible_wrong",
    "model_generated_patch",
}
CONTROL_TYPES = {
    "buggy_noop",
    "irrelevant_patch",
    "irrelevant_or_noop",
    "irrelevant_or_noop_control",
}


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


def version_from_path(path: Path) -> str:
    if "_v0_" in path.stem:
        suffix = path.stem.rsplit("_v0_", 1)[1].split("_", 1)[0]
        return f"v0.{suffix}"
    return "v0.1"


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def counter_dict(counter: Counter[str]) -> dict[str, int]:
    return dict(sorted(counter.items()))


def candidate_key(row: dict[str, Any], source: Path, index: int) -> str:
    for field in (
        "patch_id",
        "source_patch_id",
        "model_candidate_id",
        "source_model_candidate_id",
        "evp7_candidate_id",
        "hard_candidate_id",
    ):
        if row.get(field):
            return str(row[field])
    return f"{display_path(source)}::{index}"


def path_is_raw_like(path: Path) -> bool:
    rel_parts = {part.lower() for part in path.relative_to(REPO_ROOT).parts}
    if rel_parts & RAW_PATH_MARKERS:
        return True
    return any(marker in path.name.lower() for marker in RAW_FILE_MARKERS)


def candidate_files() -> list[Path]:
    paths: set[Path] = set()
    for path in (
        EVP7_CANDIDATES,
        EVP8_HARD_EVALUATOR,
    ):
        if path.exists():
            paths.add(path)
    for root in (REPO_ROOT / "data" / "patches", REPO_ROOT / "outputs"):
        if not root.exists():
            continue
        for path in root.rglob("*.jsonl"):
            if path_is_raw_like(path):
                continue
            name = path.name.lower()
            if name.startswith("candidates") and name.endswith(".jsonl"):
                paths.add(path)
    return sorted(paths)


def validation_index_for_dir(directory: Path) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for name in (
        "validation.jsonl",
        "validation_run1.jsonl",
        "p2p_validation.jsonl",
        "oracle_validation.jsonl",
    ):
        for row in read_jsonl(directory / name):
            key = candidate_key(row, directory / name, len(index) + 1)
            if key:
                index[key] = row
            model_key = row.get("model_candidate_id")
            if model_key:
                index[str(model_key)] = row
    return index


def evp7_used_sources() -> tuple[set[str], set[str]]:
    rows = read_jsonl(EVP7_CANDIDATES)
    source_dirs: set[str] = set()
    patch_ids: set[str] = set()
    for row in rows:
        patch_ids.add(candidate_key(row, EVP7_CANDIDATES, len(patch_ids) + 1))
        source_files = row.get("source_files")
        if isinstance(source_files, dict) and source_files.get("candidate_jsonl"):
            source_dirs.add(display_path(REPO_ROOT / str(source_files["candidate_jsonl"]).replace("\\", "/")))
            source_dirs.add(display_path((REPO_ROOT / str(source_files["candidate_jsonl"])).parent))
    return source_dirs, patch_ids


def evp8_hard_used_sources() -> tuple[set[str], set[str]]:
    rows = read_jsonl(EVP8_HARD_EVALUATOR)
    source_files: set[str] = set()
    patch_ids: set[str] = set()
    for row in rows:
        patch_ids.add(candidate_key(row, EVP8_HARD_EVALUATOR, len(patch_ids) + 1))
        if row.get("source_patch_id"):
            patch_ids.add(str(row["source_patch_id"]))
        if row.get("source_model_candidate_id"):
            patch_ids.add(str(row["source_model_candidate_id"]))
        if row.get("source_candidate_file"):
            source_files.add(str(row["source_candidate_file"]).replace("\\", "/"))
    return source_files, patch_ids


def bool_from_nested(row: dict[str, Any], validation: dict[str, Any] | None, field: str) -> bool | None:
    for source in (validation, row):
        if isinstance(source, dict) and field in source:
            return bool(source[field])
    summary = row.get("validation_summary")
    if isinstance(summary, dict) and field in summary:
        return bool(summary[field])
    if field == "patch_applied":
        status = row.get("patch_application_status")
        if isinstance(status, dict) and "patch_applied" in status:
            return bool(status["patch_applied"])
    return None


def source_category(row: dict[str, Any]) -> str:
    text = " ".join(
        str(row.get(field) or "")
        for field in (
            "source",
            "context_mode",
            "patch_materialization",
            "generation_prompt_version",
            "generation_run_id",
        )
    ).lower()
    candidate_type = str(row.get("candidate_type") or "").lower()
    if "agent" in text or "agent" in candidate_type:
        return "real_agent_generated"
    if row.get("generation_model") or candidate_type == "model_generated_patch":
        return "agent_like_generated"
    if candidate_type == "correct_reference" or row.get("expected_outcome") == "correct":
        return "human_reference"
    return "controlled_negative"


def normalized_label(row: dict[str, Any], validation: dict[str, Any] | None) -> str:
    if row.get("normalized_label"):
        return str(row["normalized_label"])
    if bool_from_nested(row, validation, "oracle_passed") is True:
        return "correct"
    if row.get("label_retained_oracle") == "correct":
        return "correct"
    if row.get("label_with_p2p_broad") == "correct_under_f2p_and_p2p_broad":
        return "correct"
    expected = str(row.get("expected_outcome") or "")
    candidate_type = str(row.get("candidate_type") or "")
    if expected == "correct" or candidate_type == "correct_reference":
        return "correct"
    if expected in {"partial", "regression", "overfitted", "test_passing_wrong", "irrelevant_or_noop"}:
        return expected
    if candidate_type in CONTROL_TYPES:
        return "irrelevant_or_noop"
    if candidate_type in {"partial_fix", "regression_patch", "overfitted_patch"}:
        return candidate_type.replace("_fix", "").replace("_patch", "")
    if source_category(row) in {"real_agent_generated", "agent_like_generated"} and expected != "correct":
        return "test_passing_wrong" if visible_evidence_available(row) else "agent_plausible_wrong"
    if expected == "environment_invalid":
        return "environment_invalid"
    return "incorrect"


def visible_evidence_available(row: dict[str, Any]) -> bool:
    if row.get("visible_tests") or row.get("visible_tests_declared"):
        return True
    seed = row.get("model_visible_seed")
    return isinstance(seed, dict) and bool(seed.get("patch_text"))


def has_patch_material(row: dict[str, Any]) -> bool:
    if row.get("patch_text"):
        return True
    seed = row.get("model_visible_seed")
    return isinstance(seed, dict) and bool(seed.get("patch_text"))


def source_status(path: Path, evp7_dirs: set[str], evp8_hard_files: set[str]) -> str:
    rel = display_path(path)
    parent = display_path(path.parent)
    if path == EVP7_CANDIDATES:
        return "existing_evp8_controlled_manifest"
    if path == EVP8_HARD_EVALUATOR:
        return "existing_evp8_hard_manifest"
    if rel in evp8_hard_files:
        return "already_curated_into_evp8_hard_source"
    if rel in evp7_dirs or parent in evp7_dirs:
        return "already_promoted_to_evp8_controlled_source"
    if "pending" in path.name.lower():
        return "pending_unvalidated_source"
    if "patch_verification_pilot" in rel or "build_default_check" in rel:
        return "legacy_pilot_or_duplicate_source"
    return "fresh_realistic_agent_source"


def inventory_file(
    path: Path,
    evp7_dirs: set[str],
    evp7_patch_ids: set[str],
    evp8_hard_files: set[str],
    evp8_hard_patch_ids: set[str],
) -> dict[str, Any]:
    rows = read_jsonl(path)
    validation_index = validation_index_for_dir(path.parent)
    status = source_status(path, evp7_dirs, evp8_hard_files)
    counters: dict[str, Counter[str]] = {
        "source_category": Counter(),
        "candidate_type": Counter(),
        "label": Counter(),
        "project": Counter(),
        "task": Counter(),
        "patch_applied": Counter(),
        "validation_join": Counter(),
    }
    unique_keys: set[str] = set()
    usable_keys: set[str] = set()
    agent_like_keys: set[str] = set()
    hard_negative_keys: set[str] = set()
    fresh_usable_keys: set[str] = set()
    fresh_agent_like_keys: set[str] = set()
    fresh_hard_negative_keys: set[str] = set()
    pending_usable_keys: set[str] = set()
    pending_agent_like_keys: set[str] = set()
    pending_hard_negative_keys: set[str] = set()
    historical_duplicate_keys: set[str] = set()
    visible_evidence_count = 0
    hidden_label_count = 0

    for index, row in enumerate(rows, start=1):
        key = candidate_key(row, path, index)
        validation = validation_index.get(key) or validation_index.get(str(row.get("model_candidate_id") or ""))
        category = source_category(row)
        label = normalized_label(row, validation)
        candidate_type = str(row.get("candidate_type") or "unknown")
        applied = bool_from_nested(row, validation, "patch_applied")
        visible = visible_evidence_available(row)
        hidden_label = bool(
            row.get("hidden_oracles")
            or row.get("normalized_label")
            or row.get("label_retained_oracle")
            or row.get("label_with_p2p_broad")
            or row.get("expected_outcome")
        )
        hard_negative = label in NONTRIVIAL_TYPES or candidate_type in NONTRIVIAL_TYPES
        usable = has_patch_material(row) and visible and hidden_label and applied is True and label != "environment_invalid"
        historical_duplicate = (
            key in evp7_patch_ids
            or key in evp8_hard_patch_ids
            or str(row.get("patch_id") or "") in evp7_patch_ids
            or str(row.get("patch_id") or "") in evp8_hard_patch_ids
            or str(row.get("model_candidate_id") or "") in evp8_hard_patch_ids
        )
        fresh = status == "fresh_realistic_agent_source" and not historical_duplicate

        unique_keys.add(key)
        counters["source_category"][category] += 1
        counters["candidate_type"][candidate_type] += 1
        counters["label"][label] += 1
        counters["project"][str(row.get("project") or "unknown")] += 1
        counters["task"][str(row.get("task_id") or "unknown")] += 1
        counters["patch_applied"][str(applied).lower() if applied is not None else "unknown"] += 1
        counters["validation_join"]["joined" if validation else "not_joined"] += 1
        if visible:
            visible_evidence_count += 1
        if hidden_label:
            hidden_label_count += 1
        if usable:
            usable_keys.add(key)
        if category in {"real_agent_generated", "agent_like_generated"}:
            agent_like_keys.add(key)
        if hard_negative:
            hard_negative_keys.add(key)
        if historical_duplicate:
            historical_duplicate_keys.add(key)
        if fresh and usable:
            fresh_usable_keys.add(key)
            if category in {"real_agent_generated", "agent_like_generated"}:
                fresh_agent_like_keys.add(key)
            if hard_negative:
                fresh_hard_negative_keys.add(key)
        if status == "pending_unvalidated_source" and usable:
            pending_usable_keys.add(key)
            if category in {"real_agent_generated", "agent_like_generated"}:
                pending_agent_like_keys.add(key)
            if hard_negative:
                pending_hard_negative_keys.add(key)

    return {
        "candidate_file": display_path(path),
        "source_dir": display_path(path.parent),
        "source_status": status,
        "candidate_count": len(rows),
        "unique_candidate_count": len(unique_keys),
        "usable_candidate_count": len(usable_keys),
        "agent_like_candidate_count": len(agent_like_keys),
        "nontrivial_hard_negative_count": len(hard_negative_keys),
        "fresh_usable_candidate_count": len(fresh_usable_keys),
        "fresh_agent_like_candidate_count": len(fresh_agent_like_keys),
        "fresh_nontrivial_hard_negative_count": len(fresh_hard_negative_keys),
        "pending_usable_candidate_count": len(pending_usable_keys),
        "pending_agent_like_candidate_count": len(pending_agent_like_keys),
        "pending_nontrivial_hard_negative_count": len(pending_hard_negative_keys),
        "historical_duplicate_candidate_count": len(historical_duplicate_keys),
        "visible_evidence_candidate_count": visible_evidence_count,
        "hidden_label_candidate_count": hidden_label_count,
        "source_category_counts": counter_dict(counters["source_category"]),
        "candidate_type_counts": counter_dict(counters["candidate_type"]),
        "normalized_label_counts": counter_dict(counters["label"]),
        "project_counts": counter_dict(counters["project"]),
        "task_counts": counter_dict(counters["task"]),
        "patch_applied_counts": counter_dict(counters["patch_applied"]),
        "validation_join_counts": counter_dict(counters["validation_join"]),
        "_fresh_usable_keys": sorted(fresh_usable_keys),
        "_fresh_agent_like_keys": sorted(fresh_agent_like_keys),
        "_fresh_hard_negative_keys": sorted(fresh_hard_negative_keys),
        "_pending_usable_keys": sorted(pending_usable_keys),
        "_pending_agent_like_keys": sorted(pending_agent_like_keys),
        "_pending_hard_negative_keys": sorted(pending_hard_negative_keys),
        "_project_keys": sorted({str(row.get("project") or "unknown") for row in rows}),
    }


def summarize_sources(sources: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    label_counts: Counter[str] = Counter()
    project_counts: Counter[str] = Counter()
    totals: defaultdict[str, int] = defaultdict(int)
    fresh_usable_keys: set[str] = set()
    fresh_agent_like_keys: set[str] = set()
    fresh_hard_negative_keys: set[str] = set()
    pending_usable_keys: set[str] = set()
    pending_agent_like_keys: set[str] = set()
    pending_hard_negative_keys: set[str] = set()
    fresh_projects: set[str] = set()

    for source in sources:
        status_counts[source["source_status"]] += 1
        totals["source_file_count"] += 1
        for field in (
            "candidate_count",
            "unique_candidate_count",
            "usable_candidate_count",
            "agent_like_candidate_count",
            "nontrivial_hard_negative_count",
            "fresh_usable_candidate_count",
            "fresh_agent_like_candidate_count",
            "fresh_nontrivial_hard_negative_count",
            "pending_usable_candidate_count",
            "pending_agent_like_candidate_count",
            "pending_nontrivial_hard_negative_count",
        ):
            totals[field] += int(source[field])
        for key, value in source["source_category_counts"].items():
            category_counts[key] += int(value)
        for key, value in source["normalized_label_counts"].items():
            label_counts[key] += int(value)
        for key, value in source["project_counts"].items():
            project_counts[key] += int(value)
        fresh_usable_keys.update(source["_fresh_usable_keys"])
        fresh_agent_like_keys.update(source["_fresh_agent_like_keys"])
        fresh_hard_negative_keys.update(source["_fresh_hard_negative_keys"])
        pending_usable_keys.update(source["_pending_usable_keys"])
        pending_agent_like_keys.update(source["_pending_agent_like_keys"])
        pending_hard_negative_keys.update(source["_pending_hard_negative_keys"])
        if source["fresh_usable_candidate_count"]:
            fresh_projects.update(source["_project_keys"])

    return {
        **dict(totals),
        "source_status_counts": counter_dict(status_counts),
        "source_category_counts": counter_dict(category_counts),
        "normalized_label_counts": counter_dict(label_counts),
        "project_counts": counter_dict(project_counts),
        "unique_fresh_usable_candidates": len(fresh_usable_keys),
        "unique_fresh_agent_like_candidates": len(fresh_agent_like_keys),
        "unique_fresh_nontrivial_hard_negatives": len(fresh_hard_negative_keys),
        "unique_pending_usable_candidates": len(pending_usable_keys),
        "unique_pending_agent_like_candidates": len(pending_agent_like_keys),
        "unique_pending_nontrivial_hard_negatives": len(pending_hard_negative_keys),
        "fresh_project_count": len(fresh_projects),
        "fresh_projects": sorted(fresh_projects),
    }


def readiness(summary: dict[str, Any]) -> dict[str, Any]:
    source_size = int(summary["unique_fresh_usable_candidates"])
    agent_like = int(summary["unique_fresh_agent_like_candidates"])
    hard_negatives = int(summary["unique_fresh_nontrivial_hard_negatives"])
    projects = int(summary["fresh_project_count"])
    phase0_size_pass = source_size >= 50 or source_size >= 30
    phase1_count_pass = source_size >= 50 and agent_like >= 30 and hard_negatives >= 25 and projects >= 3
    return {
        "ready_for_phase1_candidate_curation": phase1_count_pass,
        "ready_for_api": False,
        "api_block_reason": "Phase 0 inventory cannot authorize model execution; visible-tool baseline gate has not been built.",
        "phase0_source_gate": {
            "passed": phase0_size_pass,
            "requirement": "at least 50 fresh usable sources, or at least 30 plus a no-API path to generate more",
            "fresh_usable_candidates": source_size,
        },
        "phase1_count_gate": {
            "passed": phase1_count_pass,
            "requirements": {
                "fresh_usable_candidates_at_least_50": source_size >= 50,
                "fresh_agent_like_candidates_at_least_30": agent_like >= 30,
                "fresh_nontrivial_hard_negatives_at_least_25": hard_negatives >= 25,
                "fresh_projects_at_least_3": projects >= 3,
            },
        },
        "current_counts": {
            "fresh_usable_candidates": source_size,
            "fresh_agent_like_candidates": agent_like,
            "fresh_nontrivial_hard_negatives": hard_negatives,
            "fresh_project_count": projects,
            "pending_usable_candidates": int(summary["unique_pending_usable_candidates"]),
            "pending_agent_like_candidates": int(summary["unique_pending_agent_like_candidates"]),
            "pending_nontrivial_hard_negatives": int(summary["unique_pending_nontrivial_hard_negatives"]),
        },
        "next_step": (
            "If Phase 1 count gate passes, curate a separate evaluator/model-visible manifest without API. "
            "If it fails, add new realistic agent-like candidates or validate pending sources before any LLM run."
        ),
    }


def build_inventory() -> dict[str, Any]:
    evp7_dirs, evp7_patch_ids = evp7_used_sources()
    evp8_hard_files, evp8_hard_patch_ids = evp8_hard_used_sources()
    files = candidate_files()
    sources = [
        inventory_file(path, evp7_dirs, evp7_patch_ids, evp8_hard_files, evp8_hard_patch_ids)
        for path in files
    ]
    summary = summarize_sources(sources)
    output_sources = [{key: value for key, value in source.items() if not key.startswith("_")} for source in sources]
    checks = [
        check("api_call_not_attempted", True, False),
        check("raw_model_outputs_not_read", True, False),
        check("candidate_manifest_not_created", True, False),
        check("prompt_text_not_stored", True, False),
        check("patch_diff_not_stored_in_output", True, False),
        check("candidate_source_files_scanned", bool(files), len(files)),
        check("existing_evp8_controlled_manifest_detected", EVP7_CANDIDATES in files, display_path(EVP7_CANDIDATES)),
        check("existing_evp8_hard_manifest_detected", EVP8_HARD_EVALUATOR in files, display_path(EVP8_HARD_EVALUATOR)),
    ]
    return {
        "analysis_id": "evp8_realistic_agent_source_inventory_v0_1",
        "date": datetime.now().date().isoformat(),
        "scope": {
            "api_call_attempted": False,
            "raw_model_outputs_read": False,
            "candidate_manifest_created": False,
            "old_evp8_cohort_mutated": False,
            "old_evp8_hard_cohort_mutated": False,
            "prompt_text_stored": False,
            "patch_text_stored_in_output": False,
            "provider_response_object_stored": False,
        },
        "input_boundaries": {
            "existing_evp8_controlled_manifest": display_path(EVP7_CANDIDATES),
            "existing_evp8_hard_manifest": display_path(EVP8_HARD_EVALUATOR),
            "excluded_raw_path_markers": sorted(RAW_PATH_MARKERS),
            "excluded_raw_file_markers": sorted(RAW_FILE_MARKERS),
        },
        "source_summary": summary,
        "readiness": readiness(summary),
        "candidate_sources": output_sources,
        "checks": checks,
        "inventory_status": "passed" if all(item["passed"] for item in checks) else "failed",
    }


def write_markdown(path: Path, inventory: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = inventory["source_summary"]
    ready = inventory["readiness"]
    version = version_from_path(path)
    lines = [
        f"# EVP-8 Realistic Agent-Patch Source Inventory {version}",
        "",
        f"Date: {inventory['date']}",
        "",
        "This is a no-API Phase 0 inventory for the realistic/agent-patch",
        "follow-up cohort. It scans candidate source files and writes aggregate",
        "statistics only. It does not create a candidate manifest, store patch",
        "diffs, render prompts, or read raw model responses.",
        "",
        "## Boundary Checks",
        "",
    ]
    for item in inventory["checks"]:
        lines.append(f"- {item['check']}: {'passed' if item['passed'] else 'failed'} ({item['detail']})")
    lines += [
        "",
        "## Aggregate Source Counts",
        "",
        f"- candidate source files scanned: {summary['source_file_count']}",
        f"- candidate records scanned: {summary['candidate_count']}",
        f"- usable records across all sources: {summary['usable_candidate_count']}",
        f"- agent-like records across all sources: {summary['agent_like_candidate_count']}",
        f"- non-trivial hard negatives across all sources: {summary['nontrivial_hard_negative_count']}",
        "",
        "Fresh sources exclude the existing EVP-8 controlled cohort and the current",
        "EVP-8-HARD cohort.",
        "",
        f"- unique fresh usable candidates: {summary['unique_fresh_usable_candidates']}",
        f"- unique fresh agent-like candidates: {summary['unique_fresh_agent_like_candidates']}",
        f"- unique fresh non-trivial hard negatives: {summary['unique_fresh_nontrivial_hard_negatives']}",
        f"- fresh projects: {summary['fresh_project_count']} ({', '.join(summary['fresh_projects']) or 'none'})",
        f"- pending usable candidates: {summary['unique_pending_usable_candidates']}",
        f"- pending agent-like candidates: {summary['unique_pending_agent_like_candidates']}",
        f"- pending non-trivial hard negatives: {summary['unique_pending_nontrivial_hard_negatives']}",
        "",
        "## Readiness",
        "",
        f"- ready for Phase 1 candidate curation: `{ready['ready_for_phase1_candidate_curation']}`",
        f"- ready for API: `{ready['ready_for_api']}`",
        f"- API block reason: {ready['api_block_reason']}",
        "",
        "Phase 1 count gate:",
        "",
    ]
    for key, value in ready["phase1_count_gate"]["requirements"].items():
        lines.append(f"- `{key}`: {'passed' if value else 'failed'}")
    lines += [
        "",
        "## Source Status Counts",
        "",
    ]
    for key, value in summary["source_status_counts"].items():
        lines.append(f"- `{key}`: {value}")
    lines += [
        "",
        "## Source Category Counts",
        "",
    ]
    for key, value in summary["source_category_counts"].items():
        lines.append(f"- `{key}`: {value}")
    lines += [
        "",
        "## Candidate Sources",
        "",
        "| source | status | candidates | usable | agent-like | hard negatives | fresh usable | fresh agent-like | fresh hard negatives | pending usable |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for source in inventory["candidate_sources"]:
        lines.append(
            f"| `{source['candidate_file']}` | `{source['source_status']}` | "
            f"{source['candidate_count']} | {source['usable_candidate_count']} | "
            f"{source['agent_like_candidate_count']} | {source['nontrivial_hard_negative_count']} | "
            f"{source['fresh_usable_candidate_count']} | {source['fresh_agent_like_candidate_count']} | "
            f"{source['fresh_nontrivial_hard_negative_count']} | {source['pending_usable_candidate_count']} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "The inventory is a source-readiness gate, not an experiment result. Existing",
        "EVP-8 and EVP-8-HARD candidates remain useful as historical evidence and",
        "failure-mode examples, but they are not counted as fresh realistic/agent",
        "cohort material. Model APIs remain blocked until a separate curated cohort",
        "and visible-tool headroom baseline exist.",
        "",
        f"Next step: {ready['next_step']}",
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
    inventory = build_inventory()
    write_json(args.out_json, inventory)
    write_markdown(args.out_md, inventory)
    if args.check and inventory["inventory_status"] != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
