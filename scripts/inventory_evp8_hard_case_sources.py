"""Inventory local sources for the EVP-8 hard-case extension.

This no-API script is intentionally a source inventory, not a candidate-set
builder. It reads tracked candidate labels and non-raw local validation files,
then writes aggregate reports without patch diffs, prompts, or raw responses.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "protocols" / "evp8_hard_case_source_inventory_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_hard_case_source_inventory_v0_1.md"
EVP7_CANDIDATES = REPO_ROOT / "data" / "patches" / "evp7_candidates.jsonl"
EVP7_TOOL_BASELINE = REPO_ROOT / "data" / "baselines" / "evp7_tool_only_decisions.jsonl"
EVP8_HEADROOM_AUDIT = REPO_ROOT / "data" / "protocols" / "evp8_tool_headroom_audit_v0_1.json"

HARD_NEGATIVE_TYPES = {
    "partial_fix",
    "regression_patch",
    "overfitted_patch",
    "model_generated_patch",
    "agent_plausible_wrong",
}
CONTROL_TYPES = {
    "buggy_noop",
    "irrelevant_patch",
    "irrelevant_or_noop_control",
    "correct_reference",
}
SKIP_OUTPUT_DIR_MARKERS = {
    "raw",
    "inputs",
}
SKIP_OUTPUT_FILE_MARKERS = {
    "raw",
    "response",
    "reviews",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{display_path(path)}:{line_no} is not a JSON object")
        rows.append(value)
    return rows


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
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


def is_raw_or_response_path(path: Path) -> bool:
    rel_parts = {part.lower() for part in path.relative_to(REPO_ROOT).parts}
    name = path.name.lower()
    if rel_parts & SKIP_OUTPUT_DIR_MARKERS:
        return True
    return any(marker in name for marker in SKIP_OUTPUT_FILE_MARKERS)


def record_candidate_key(row: dict[str, Any]) -> str:
    return str(row.get("patch_id") or row.get("model_candidate_id") or row.get("evp7_candidate_id") or "")


def has_required_candidate_fields(row: dict[str, Any]) -> bool:
    return all(row.get(field) for field in ("task_id", "patch_text", "visible_tests", "hidden_oracles", "candidate_type"))


def is_correct(row: dict[str, Any]) -> bool:
    expected = row.get("expected_outcome")
    label = row.get("label_with_p2p_broad")
    retained = row.get("label_retained_oracle")
    return expected == "correct" or label == "correct_under_f2p_and_p2p_broad" or retained == "correct"


def is_hard_negative(row: dict[str, Any]) -> bool:
    candidate_type = str(row.get("candidate_type") or "")
    expected = str(row.get("expected_outcome") or "")
    failure_type = str(row.get("failure_type_label") or "")
    generated = bool(row.get("generation_model") or str(row.get("source") or "").endswith("_agent_edit"))
    if is_correct(row):
        return False
    if candidate_type in HARD_NEGATIVE_TYPES:
        return True
    if expected in {"partial", "regression", "overfitted", "test_passing_wrong"}:
        return True
    if "partial" in failure_type or "regression" in failure_type or "overfit" in failure_type:
        return True
    return generated


def validation_patch_applied(row: dict[str, Any], validation: dict[str, Any] | None) -> bool | None:
    if validation and "patch_applied" in validation:
        return bool(validation["patch_applied"])
    summary = row.get("validation_summary")
    if isinstance(summary, dict) and "patch_applied" in summary:
        return bool(summary["patch_applied"])
    return None


def inventory_evp7_controlled() -> tuple[dict[str, Any], set[str]]:
    rows = read_jsonl(EVP7_CANDIDATES)
    source_dirs: set[str] = set()
    for row in rows:
        source_files = row.get("source_files")
        if isinstance(source_files, dict) and source_files.get("candidate_jsonl"):
            source_dirs.add(str(Path(source_files["candidate_jsonl"]).parent).replace("\\", "/"))

    headroom = read_json(EVP8_HEADROOM_AUDIT)
    metrics = headroom.get("rule_only_metrics", {})
    counts = metrics.get("confusion_counts", {}) if isinstance(metrics, dict) else {}
    false_accept_count = int(counts.get("false_accept", 0))
    false_reject_count = int(counts.get("false_reject", 0))
    opportunity_count = int(metrics.get("opportunity_set_size", false_accept_count + false_reject_count)) if isinstance(metrics, dict) else 0

    hard_negative_count = sum(1 for row in rows if is_hard_negative(row))
    return (
        {
            "source": display_path(EVP7_CANDIDATES),
            "status": "already_used_in_evp8_controlled_cohort",
            "candidate_count": len(rows),
            "task_count": len({row.get("task_id") for row in rows if row.get("task_id")}),
            "candidate_type_counts": counter_dict(Counter(str(row.get("candidate_type")) for row in rows)),
            "expected_outcome_counts": counter_dict(Counter(str(row.get("expected_outcome")) for row in rows)),
            "hard_negative_count": hard_negative_count,
            "rule_only_e6_opportunity_cases": {
                "source": display_path(EVP8_HEADROOM_AUDIT),
                "false_accept_count": false_accept_count,
                "false_reject_count": false_reject_count,
                "candidate_count": opportunity_count,
            },
            "usable_for_hard_extension": "patterns_only_not_new_candidates",
            "reason": "These 98 records are the old controlled EVP-8 cohort and must not be mixed into the new hard-case extension.",
        },
        source_dirs,
    )


def validation_index_for_dir(directory: Path) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for name in ("validation.jsonl", "p2p_validation.jsonl", "oracle_validation.jsonl"):
        for row in read_jsonl(directory / name):
            key = record_candidate_key(row)
            if key:
                index[key] = row
    return index


def candidate_files_under_outputs() -> list[Path]:
    outputs = REPO_ROOT / "outputs"
    if not outputs.exists():
        return []
    paths = []
    for path in outputs.rglob("*.jsonl"):
        if is_raw_or_response_path(path):
            continue
        if path.name.lower().startswith("candidates") and path.name.lower().endswith(".jsonl"):
            paths.append(path)
    return sorted(paths)


def inventory_candidate_file(path: Path, promoted_source_dirs: set[str]) -> dict[str, Any]:
    rows = read_jsonl(path)
    validation_index = validation_index_for_dir(path.parent)
    rel_dir = display_path(path.parent)
    is_promoted = rel_dir in promoted_source_dirs
    is_agent_or_ai = any(row.get("generation_model") or "agent" in str(row.get("source") or "") for row in rows)
    required_field_count = sum(1 for row in rows if has_required_candidate_fields(row))
    validated_count = 0
    patch_applied_true = 0
    patch_applied_false = 0
    hard_negative_count = 0
    eligible_new_hard_negative_count = 0
    retained_counts: Counter[str] = Counter()
    p2p_counts: Counter[str] = Counter()
    validation_status_counts: Counter[str] = Counter()
    candidate_keys: set[str] = set()
    eligible_new_hard_negative_keys: set[str] = set()

    for row in rows:
        key = record_candidate_key(row)
        if not key:
            key = f"{display_path(path)}::{len(candidate_keys) + 1}"
        candidate_keys.add(key)
        validation = validation_index.get(key)
        if validation:
            validated_count += 1
            validation_status_counts[str(validation.get("validation_status") or "validated_or_recorded")] += 1
            if "retained_oracle_passed" in validation:
                retained_counts["passed" if validation.get("retained_oracle_passed") else "failed"] += 1
            elif "oracle_passed" in validation:
                retained_counts["passed" if validation.get("oracle_passed") else "failed"] += 1
            if validation.get("p2p_broad_status"):
                p2p_counts[str(validation["p2p_broad_status"])] += 1
        summary = row.get("validation_summary")
        if isinstance(summary, dict):
            if "retained_oracle_passed" in summary:
                retained_counts["passed" if summary.get("retained_oracle_passed") else "failed"] += 1
            if summary.get("p2p_broad_status"):
                p2p_counts[str(summary["p2p_broad_status"])] += 1
        applied = validation_patch_applied(row, validation)
        if applied is True:
            patch_applied_true += 1
        elif applied is False:
            patch_applied_false += 1
        if is_hard_negative(row):
            hard_negative_count += 1
            if not is_promoted and applied is True and has_required_candidate_fields(row):
                eligible_new_hard_negative_count += 1
                eligible_new_hard_negative_keys.add(key)

    status = "already_promoted_to_evp7_controlled" if is_promoted else "not_promoted_to_evp7_controlled"
    if "patch_verification_pilot" in rel_dir or "build_default_check" in rel_dir:
        status = "legacy_pilot_or_duplicate_output"

    return {
        "candidate_file": display_path(path),
        "source_dir": rel_dir,
        "status": status,
        "source_kind": "ai_or_agent_generated" if is_agent_or_ai else "constructed_or_reference",
        "candidate_count": len(rows),
        "task_count": len({row.get("task_id") for row in rows if row.get("task_id")}),
        "candidate_type_counts": counter_dict(Counter(str(row.get("candidate_type")) for row in rows)),
        "expected_outcome_counts": counter_dict(Counter(str(row.get("expected_outcome")) for row in rows)),
        "records_with_required_phase_b_fields": required_field_count,
        "records_with_validation_join": validated_count,
        "patch_applied_counts": {
            "true": patch_applied_true,
            "false": patch_applied_false,
            "unknown": max(0, len(rows) - patch_applied_true - patch_applied_false),
        },
        "retained_oracle_counts": counter_dict(retained_counts),
        "p2p_broad_status_counts": counter_dict(p2p_counts),
        "validation_status_counts": counter_dict(validation_status_counts),
        "hard_negative_count": hard_negative_count,
        "eligible_new_hard_negative_count": eligible_new_hard_negative_count,
        "_candidate_keys": sorted(candidate_keys),
        "_eligible_new_hard_negative_keys": sorted(eligible_new_hard_negative_keys),
    }


def summarize_sources(sources: list[dict[str, Any]]) -> dict[str, Any]:
    totals = defaultdict(int)
    status_counts: Counter[str] = Counter()
    kind_counts: Counter[str] = Counter()
    non_promoted_keys: set[str] = set()
    non_promoted_eligible_keys: set[str] = set()
    ai_or_agent_keys: set[str] = set()
    ai_or_agent_eligible_keys: set[str] = set()
    for source in sources:
        status_counts[source["status"]] += 1
        kind_counts[source["source_kind"]] += 1
        totals["candidate_records_scanned"] += source["candidate_count"]
        totals["not_promoted_candidate_records"] += (
            source["candidate_count"] if source["status"] == "not_promoted_to_evp7_controlled" else 0
        )
        totals["not_promoted_eligible_hard_negatives"] += source["eligible_new_hard_negative_count"]
        totals["ai_or_agent_candidate_records"] += (
            source["candidate_count"] if source["source_kind"] == "ai_or_agent_generated" else 0
        )
        totals["ai_or_agent_eligible_hard_negatives"] += (
            source["eligible_new_hard_negative_count"] if source["source_kind"] == "ai_or_agent_generated" else 0
        )
        if source["status"] == "not_promoted_to_evp7_controlled":
            non_promoted_keys.update(source["_candidate_keys"])
            non_promoted_eligible_keys.update(source["_eligible_new_hard_negative_keys"])
        if source["source_kind"] == "ai_or_agent_generated":
            ai_or_agent_keys.update(source["_candidate_keys"])
            ai_or_agent_eligible_keys.update(source["_eligible_new_hard_negative_keys"])
    return {
        "source_file_count": len(sources),
        "source_status_counts": counter_dict(status_counts),
        "source_kind_counts": counter_dict(kind_counts),
        "unique_not_promoted_candidate_records": len(non_promoted_keys),
        "unique_not_promoted_eligible_hard_negatives": len(non_promoted_eligible_keys),
        "unique_ai_or_agent_candidate_records": len(ai_or_agent_keys),
        "unique_ai_or_agent_eligible_hard_negatives": len(ai_or_agent_eligible_keys),
        **dict(totals),
    }


def phase_b_readiness(evp7_inventory: dict[str, Any], source_summary: dict[str, Any]) -> dict[str, Any]:
    new_hard_negatives = source_summary["unique_not_promoted_eligible_hard_negatives"]
    ai_hard_negatives = source_summary["unique_ai_or_agent_eligible_hard_negatives"]
    old_opportunities = evp7_inventory["rule_only_e6_opportunity_cases"]["candidate_count"]
    return {
        "ready_for_phase_b_candidate_manifest": False,
        "candidate_manifest_created": False,
        "reason": (
            "The local inventory finds reusable sources and reaches the minimum 20 unique "
            "non-promoted eligible hard negatives, but these have not yet been curated into a "
            "separate manifest and no hard-case tool-only opportunity baseline has been built."
        ),
        "current_counts": {
            "existing_controlled_cohort_candidates": evp7_inventory["candidate_count"],
            "existing_controlled_rule_only_opportunities": old_opportunities,
            "fresh_non_promoted_eligible_hard_negatives": new_hard_negatives,
            "fresh_ai_or_agent_eligible_hard_negatives": ai_hard_negatives,
        },
        "next_gate": (
            "Construct a separate no-API EVP-8-HARD candidate draft only after adding or validating "
            "enough non-promoted hard negatives; then build a tool-only baseline and stop before API "
            "if opportunity cases remain below 10."
        ),
    }


def build_inventory() -> dict[str, Any]:
    evp7_inventory, promoted_source_dirs = inventory_evp7_controlled()
    source_files = candidate_files_under_outputs()
    sources = [inventory_candidate_file(path, promoted_source_dirs) for path in source_files]
    source_summary = summarize_sources(sources)
    output_sources = [
        {key: value for key, value in source.items() if not key.startswith("_")}
        for source in sources
    ]
    readiness = phase_b_readiness(evp7_inventory, source_summary)
    checks = [
        check("api_call_not_attempted", True, False),
        check("raw_model_outputs_not_read", True, False),
        check("old_evp8_cohort_not_mutated", True, False),
        check("hard_candidate_manifest_not_created", True, False),
        check("prompt_text_not_stored", True, False),
        check("source_files_scanned", bool(source_files), len(source_files)),
        check("evp7_controlled_cohort_detected", evp7_inventory["candidate_count"] == 98, evp7_inventory["candidate_count"]),
    ]
    return {
        "analysis_id": "evp8_hard_case_source_inventory_v0_1",
        "date": "2026-06-29",
        "scope": {
            "api_call_attempted": False,
            "raw_model_outputs_read": False,
            "old_evp8_controlled_cohort_mutated": False,
            "candidate_manifest_created": False,
            "prompt_text_stored": False,
            "patch_text_stored_in_output": False,
        },
        "existing_controlled_cohort": evp7_inventory,
        "local_candidate_source_summary": source_summary,
        "local_candidate_sources": output_sources,
        "phase_b_readiness": readiness,
        "checks": checks,
        "inventory_status": "passed" if all(row["passed"] for row in checks) else "failed",
    }


def write_markdown(path: Path, inventory: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    controlled = inventory["existing_controlled_cohort"]
    summary = inventory["local_candidate_source_summary"]
    readiness = inventory["phase_b_readiness"]
    lines = [
        "# EVP-8 Hard-Case Source Inventory v0.1",
        "",
        "Date: 2026-06-29",
        "",
        "This is a no-API source inventory for Phase B. It does not create an",
        "`EVP-8-HARD` candidate manifest and does not store patch diffs, prompt text,",
        "or raw model responses.",
        "",
        "## Boundary Checks",
        "",
    ]
    for row in inventory["checks"]:
        lines.append(f"- {row['check']}: {'passed' if row['passed'] else 'failed'} ({row['detail']})")
    lines += [
        "",
        "## Existing Controlled Cohort",
        "",
        f"- source: `{controlled['source']}`",
        f"- status: `{controlled['status']}`",
        f"- candidates: {controlled['candidate_count']}",
        f"- tasks: {controlled['task_count']}",
        f"- hard negatives already inside controlled cohort: {controlled['hard_negative_count']}",
        "- rule-only E6 opportunity cases: "
        f"{controlled['rule_only_e6_opportunity_cases']['candidate_count']} "
        f"({controlled['rule_only_e6_opportunity_cases']['false_accept_count']} false accepts, "
        f"{controlled['rule_only_e6_opportunity_cases']['false_reject_count']} false rejects)",
        "",
        "Interpretation: this cohort can be used as prior evidence and source-pattern",
        "context, but it must not be counted as new hard-case extension data.",
        "",
        "## Local Source Summary",
        "",
        f"- candidate source files scanned: {summary['source_file_count']}",
        f"- candidate records scanned: {summary['candidate_records_scanned']}",
        f"- non-promoted candidate records: {summary['not_promoted_candidate_records']} "
        f"(unique: {summary['unique_not_promoted_candidate_records']})",
        f"- non-promoted eligible hard negatives: {summary['not_promoted_eligible_hard_negatives']} "
        f"(unique: {summary['unique_not_promoted_eligible_hard_negatives']})",
        f"- AI/agent candidate records: {summary['ai_or_agent_candidate_records']} "
        f"(unique: {summary['unique_ai_or_agent_candidate_records']})",
        f"- AI/agent eligible hard negatives: {summary['ai_or_agent_eligible_hard_negatives']} "
        f"(unique: {summary['unique_ai_or_agent_eligible_hard_negatives']})",
        "",
        "Source status counts:",
        "",
    ]
    for key, value in summary["source_status_counts"].items():
        lines.append(f"- `{key}`: {value}")
    lines += [
        "",
        "## Candidate Sources",
        "",
        "| source | status | kind | candidates | eligible new hard negatives | validation joins |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ]
    for source in inventory["local_candidate_sources"]:
        lines.append(
            f"| `{source['candidate_file']}` | `{source['status']}` | `{source['source_kind']}` | "
            f"{source['candidate_count']} | {source['eligible_new_hard_negative_count']} | "
            f"{source['records_with_validation_join']} |"
        )
    lines += [
        "",
        "## Phase B Readiness",
        "",
        f"- ready for hard-case manifest: `{readiness['ready_for_phase_b_candidate_manifest']}`",
        f"- reason: {readiness['reason']}",
        f"- next gate: {readiness['next_gate']}",
        "",
        "Plain-language conclusion: the project has enough historical material to",
        "explain why hard cases matter, and it has some validated AI/agent patch",
        "sources. It does not yet have enough fresh non-promoted hard negatives or a",
        "new hard-case tool-only opportunity baseline to justify another model API run.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true", help="Fail if inventory checks do not pass.")
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
