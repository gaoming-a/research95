"""Build the separated EVP-8 realistic agent-patch cohort manifest.

This script is no-API. It reads validated/relabelled local agent-patch outputs,
filters to fresh usable candidates, then writes evaluator-only labels,
model-visible seeds, and a conservative rule-only baseline.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = REPO_ROOT / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import inventory_evp8_realistic_agent_sources as inventory  # noqa: E402


COHORT_ID = "EVP-8-REALISTIC-AGENT"
SOURCE_FILES = [
    REPO_ROOT / "outputs" / "evp8_realistic_agent_validation_qwen_primary_001" / "candidates.relabeled.jsonl",
    REPO_ROOT / "outputs" / "evp8_realistic_agent_validation_qwen_supplement_001" / "candidates.relabeled.jsonl",
    REPO_ROOT / "outputs" / "evp8_realistic_agent_validation_qwen_supplement_002" / "candidates.relabeled.jsonl",
]
SOURCE_INVENTORY = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_source_inventory_v0_4.json"
DEFAULT_EVALUATOR_OUT = REPO_ROOT / "data" / "patches" / "evp8_realistic_agent_evaluator_manifest_v0_1.jsonl"
DEFAULT_MODEL_VISIBLE_OUT = REPO_ROOT / "data" / "evidence" / "evp8_realistic_agent_model_visible_seed_v0_1.jsonl"
DEFAULT_BASELINE_OUT = REPO_ROOT / "data" / "baselines" / "evp8_realistic_agent_rule_only_baseline_v0_1.jsonl"
DEFAULT_SUMMARY_OUT = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_cohort_manifest_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_realistic_agent_cohort_manifest_v0_1.md"

FORBIDDEN_MODEL_VISIBLE_KEYS = {
    "agent_applied_edits",
    "candidate_type",
    "construction_notes",
    "expected_outcome",
    "generation_rationale",
    "hidden_oracles",
    "hidden_validation_summary",
    "label_confidence",
    "model_candidate_id",
    "normalized_label",
    "oracle_command",
    "oracle_passed",
    "oracle_result",
    "oracle_ran",
    "oracle_workdir",
    "raw_generation_response_path",
    "raw_generation_response_sha256",
    "source_patch_id",
    "source_model_candidate_id",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{display_path(path)} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{display_path(path)}:{line_no} must contain a JSON object")
        rows.append(value)
    return rows


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def display_path(path: Path) -> str:
    absolute = path if path.is_absolute() else REPO_ROOT / path
    try:
        return absolute.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(absolute)


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def patch_size(patch_text: str) -> dict[str, int]:
    added = 0
    deleted = 0
    files: set[str] = set()
    for line in patch_text.splitlines():
        if line.startswith("+++ b/"):
            files.add(line[6:])
        elif line.startswith("+") and not line.startswith("+++"):
            added += 1
        elif line.startswith("-") and not line.startswith("---"):
            deleted += 1
    return {"added_lines": added, "deleted_lines": deleted, "files_changed": len(files)}


def validation_index_for_dir(directory: Path) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for row in read_jsonl(directory / "validation.jsonl"):
        for key in (row.get("patch_id"), row.get("model_candidate_id")):
            if key:
                index[str(key)] = row
    return index


def historical_duplicate(row: dict[str, Any], key: str, evp7_patch_ids: set[str], evp8_patch_ids: set[str]) -> bool:
    return (
        key in evp7_patch_ids
        or key in evp8_patch_ids
        or str(row.get("patch_id") or "") in evp7_patch_ids
        or str(row.get("patch_id") or "") in evp8_patch_ids
        or str(row.get("model_candidate_id") or "") in evp8_patch_ids
    )


def normalized_label(row: dict[str, Any], validation: dict[str, Any]) -> str:
    if validation.get("oracle_passed") is True or row.get("expected_outcome") == "correct":
        return "correct"
    return "test_passing_wrong"


def candidate_is_usable(row: dict[str, Any], validation: dict[str, Any] | None) -> tuple[bool, str]:
    required = ("task_id", "project", "issue_summary", "patch_text", "visible_tests", "touched_files")
    missing = [field for field in required if not row.get(field)]
    if missing:
        return False, f"missing_required_fields:{','.join(missing)}"
    if validation is None:
        return False, "missing_validation_record"
    if validation.get("patch_applied") is not True:
        return False, "patch_not_applied"
    if row.get("expected_outcome") == "environment_invalid":
        return False, "environment_invalid"
    return True, "included"


def collect_candidates() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    _evp7_dirs, evp7_patch_ids = inventory.evp7_used_sources()
    _evp8_files, evp8_patch_ids = inventory.evp8_hard_used_sources()
    selected: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    for source_path in SOURCE_FILES:
        validation_index = validation_index_for_dir(source_path.parent)
        for index, row in enumerate(read_jsonl(source_path), start=1):
            key = inventory.candidate_key(row, source_path, index)
            validation = validation_index.get(key) or validation_index.get(str(row.get("model_candidate_id") or ""))
            usable, reason = candidate_is_usable(row, validation)
            if key in seen_keys:
                excluded.append({"source": display_path(source_path), "candidate_key": key, "reason": "duplicate_key_within_realistic_sources"})
                continue
            if historical_duplicate(row, key, evp7_patch_ids, evp8_patch_ids):
                excluded.append({"source": display_path(source_path), "candidate_key": key, "reason": "historical_duplicate"})
                continue
            if not usable:
                excluded.append({"source": display_path(source_path), "candidate_key": key, "reason": reason})
                continue
            assert validation is not None
            seen_keys.add(key)
            selected.append({"source_path": source_path, "candidate": row, "validation": validation, "source_key": key})
    return selected, excluded


def evaluator_row(index: int, item: dict[str, Any]) -> dict[str, Any]:
    row = item["candidate"]
    validation = item["validation"]
    candidate_id = f"evp8_realistic_agent_candidate_{index:04d}"
    label = normalized_label(row, validation)
    patch_text = str(row["patch_text"])
    return {
        "cohort_id": COHORT_ID,
        "candidate_id": candidate_id,
        "source_candidate_file": display_path(item["source_path"]),
        "source_patch_id": row.get("patch_id"),
        "source_model_candidate_id": row.get("model_candidate_id"),
        "task_id": row.get("task_id"),
        "project": row.get("project"),
        "patch_sha256": hashlib.sha256(patch_text.encode("utf-8")).hexdigest(),
        "patch_size": patch_size(patch_text),
        "candidate_type": row.get("candidate_type"),
        "patch_source_kind": "real_agent_generated",
        "generation_model": row.get("generation_model"),
        "generation_run_id": row.get("generation_run_id"),
        "expected_outcome": row.get("expected_outcome"),
        "normalized_label": label,
        "label_confidence": row.get("label_confidence"),
        "hidden_oracles": row.get("hidden_oracles", []),
        "visible_tests_declared": row.get("visible_tests", []),
        "patch_application_status": {
            "patch_applied": validation.get("patch_applied"),
            "validation_status": validation.get("validation_status"),
        },
        "hidden_validation_summary": {
            "oracle_ran": validation.get("oracle_ran"),
            "oracle_passed": validation.get("oracle_passed"),
        },
        "nontrivial_hard_negative": label != "correct",
    }


def model_visible_row(index: int, item: dict[str, Any]) -> dict[str, Any]:
    row = item["candidate"]
    validation = item["validation"]
    patch_text = str(row["patch_text"])
    listed_tests = list(row.get("visible_tests") or [])
    return {
        "cohort_id": COHORT_ID,
        "candidate_id": f"evp8_realistic_agent_candidate_{index:04d}",
        "task_id": row.get("task_id"),
        "project": row.get("project"),
        "issue_summary": row.get("issue_summary"),
        "touched_files": row.get("touched_files", []),
        "patch_text": patch_text,
        "visible_context": row.get("visible_context"),
        "visible_static_evidence": {
            "patch_applies": validation.get("patch_applied") is True,
            "patch_size": patch_size(patch_text),
        },
        "visible_test_evidence": {
            "listed_tests": listed_tests,
            "run_status": "not_run_hint_only",
            "observed_outcome": "not_run_hint_only",
            "outcome_counts": {"not_run_hint_only": len(listed_tests)},
            "test_results": [{"test_name": test, "outcome": "not_run_hint_only"} for test in listed_tests],
        },
        "visible_tool_evidence": {
            "tool_summary_available": False,
            "visible_test_run_status": "not_run_hint_only",
            "visible_test_outcome_counts": {"not_run_hint_only": len(listed_tests)},
            "reason": "Only visible test names are available; visible test execution is a separate next gate.",
        },
    }


def forbidden_key_hits(value: Any, path: str = "$") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in FORBIDDEN_MODEL_VISIBLE_KEYS:
                hits.append(child_path)
            hits.extend(forbidden_key_hits(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(forbidden_key_hits(child, f"{path}[{index}]"))
    return hits


def baseline_row(seed: dict[str, Any]) -> dict[str, Any]:
    return {
        "api_call_attempted": False,
        "candidate_id": seed["candidate_id"],
        "cohort_id": COHORT_ID,
        "condition": "rule_only_visible_apply_and_test_hint",
        "confidence": 0.2,
        "decision": "escalate",
        "evidence_level": "rule-only",
        "human_review_needed": True,
        "primary_reason": "Patch applies, but only visible test names are available; no visible execution outcome supports accept or reject.",
        "risk_flags": ["visible_test_outcome_missing"],
    }


def build_summary(
    evaluator_rows: list[dict[str, Any]],
    model_visible_rows: list[dict[str, Any]],
    baseline_rows: list[dict[str, Any]],
    excluded: list[dict[str, Any]],
) -> dict[str, Any]:
    evaluator_ids = {row["candidate_id"] for row in evaluator_rows}
    model_visible_ids = {row["candidate_id"] for row in model_visible_rows}
    baseline_ids = {row["candidate_id"] for row in baseline_rows}
    leakage_hits = [hit for row in model_visible_rows for hit in forbidden_key_hits(row)]
    labels = Counter(str(row["normalized_label"]) for row in evaluator_rows)
    projects = Counter(str(row["project"]) for row in evaluator_rows)
    tasks = Counter(str(row["task_id"]) for row in evaluator_rows)
    baseline_decisions = Counter(str(row["decision"]) for row in baseline_rows)
    checks = [
        check("source_inventory_v0_4_phase1_ready", read_json(SOURCE_INVENTORY)["readiness"]["ready_for_phase1_candidate_curation"] is True, True),
        check("candidate_count_at_least_50", len(evaluator_rows) >= 50, len(evaluator_rows)),
        check("model_visible_count_matches_evaluator", model_visible_ids == evaluator_ids, len(model_visible_rows)),
        check("baseline_count_matches_evaluator", baseline_ids == evaluator_ids, len(baseline_rows)),
        check("model_visible_forbidden_fields_absent", not leakage_hits, leakage_hits[:20]),
        check("all_candidates_patch_applied", all(row["patch_application_status"]["patch_applied"] for row in evaluator_rows), True),
        check("rule_only_baseline_all_escalate_until_visible_tests_run", baseline_decisions == Counter({"escalate": len(baseline_rows)}), dict(baseline_decisions)),
    ]
    return {
        "analysis_id": "evp8_realistic_agent_cohort_manifest_v0_1",
        "date": datetime.now().date().isoformat(),
        "cohort_id": COHORT_ID,
        "scope": {
            "api_call_attempted": False,
            "verifier_api_authorized": False,
            "raw_model_outputs_read": False,
            "prompt_text_stored": False,
            "model_visible_evaluator_labels_stored": False,
            "visible_test_execution_performed": False,
        },
        "outputs": {
            "evaluator_manifest": display_path(DEFAULT_EVALUATOR_OUT),
            "model_visible_seed": display_path(DEFAULT_MODEL_VISIBLE_OUT),
            "rule_only_baseline": display_path(DEFAULT_BASELINE_OUT),
        },
        "candidate_summary": {
            "candidate_count": len(evaluator_rows),
            "normalized_label_counts": dict(sorted(labels.items())),
            "nontrivial_hard_negative_count": sum(1 for row in evaluator_rows if row["nontrivial_hard_negative"]),
            "project_counts": dict(sorted(projects.items())),
            "task_counts": dict(sorted(tasks.items())),
            "excluded_count": len(excluded),
            "excluded_reason_counts": dict(sorted(Counter(row["reason"] for row in excluded).items())),
        },
        "baseline_summary": {
            "condition": "rule_only_visible_apply_and_test_hint",
            "decision_counts": dict(sorted(baseline_decisions.items())),
            "headroom_gate_ready": False,
            "headroom_block_reason": "Visible tests have not been executed for the realistic cohort yet.",
        },
        "checks": checks,
        "status": "passed" if all(row["passed"] for row in checks) else "blocked",
        "next_required_step": "run declared visible tests for the realistic cohort and build the visible-tool headroom baseline",
    }


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    candidate = summary["candidate_summary"]
    baseline = summary["baseline_summary"]
    lines = [
        "# EVP-8 Realistic Agent Cohort Manifest v0.1",
        "",
        f"Date: {summary['date']}",
        "",
        f"- status: `{summary['status']}`",
        f"- cohort id: `{summary['cohort_id']}`",
        f"- candidate count: {candidate['candidate_count']}",
        f"- non-trivial hard negatives: {candidate['nontrivial_hard_negative_count']}",
        f"- baseline decisions: `{baseline['decision_counts']}`",
        f"- headroom gate ready: `{baseline['headroom_gate_ready']}`",
        f"- headroom block reason: {baseline['headroom_block_reason']}",
        "",
        "## Outputs",
        "",
    ]
    for name, output in summary["outputs"].items():
        lines.append(f"- {name}: `{output}`")
    lines += [
        "",
        "## Label Counts",
        "",
    ]
    for label, count in candidate["normalized_label_counts"].items():
        lines.append(f"- `{label}`: {count}")
    lines += [
        "",
        "## Project Counts",
        "",
    ]
    for project, count in candidate["project_counts"].items():
        lines.append(f"- `{project}`: {count}")
    lines += [
        "",
        "## Checks",
        "",
    ]
    for row in summary["checks"]:
        lines.append(f"- {row['check']}: {'passed' if row['passed'] else 'failed'} ({row['detail']})")
    lines += [
        "",
        "## Next Step",
        "",
        summary["next_required_step"],
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluator-out", type=Path, default=DEFAULT_EVALUATOR_OUT)
    parser.add_argument("--model-visible-out", type=Path, default=DEFAULT_MODEL_VISIBLE_OUT)
    parser.add_argument("--baseline-out", type=Path, default=DEFAULT_BASELINE_OUT)
    parser.add_argument("--summary-out", type=Path, default=DEFAULT_SUMMARY_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    selected, excluded = collect_candidates()
    evaluator_rows = [evaluator_row(index, item) for index, item in enumerate(selected, start=1)]
    model_visible_rows = [model_visible_row(index, item) for index, item in enumerate(selected, start=1)]
    baseline_rows = [baseline_row(seed) for seed in model_visible_rows]
    summary = build_summary(evaluator_rows, model_visible_rows, baseline_rows, excluded)
    write_jsonl(args.evaluator_out, evaluator_rows)
    write_jsonl(args.model_visible_out, model_visible_rows)
    write_jsonl(args.baseline_out, baseline_rows)
    write_json(args.summary_out, summary)
    write_markdown(args.md_out, summary)
    print(json.dumps(summary["candidate_summary"], ensure_ascii=False, indent=2, sort_keys=True))
    if args.check and summary["status"] != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
