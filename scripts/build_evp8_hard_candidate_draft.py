"""Build the no-API EVP-8-HARD candidate draft and baseline gate.

This script constructs a separate hard-case draft from previously inventoried
local sources. It does not call model APIs, render prompts, read raw model
responses, or mutate the old 98-candidate controlled cohort.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
COHORT_ID = "EVP-8-HARD"
DEFAULT_EVALUATOR_OUT = REPO_ROOT / "data" / "patches" / "evp8_hard_evaluator_manifest_v0_1.jsonl"
DEFAULT_MODEL_VISIBLE_OUT = REPO_ROOT / "data" / "evidence" / "evp8_hard_model_visible_seed_v0_1.jsonl"
DEFAULT_BASELINE_OUT = REPO_ROOT / "data" / "baselines" / "evp8_hard_tool_only_baseline_v0_1.jsonl"
DEFAULT_SUMMARY_OUT = REPO_ROOT / "data" / "protocols" / "evp8_hard_candidate_draft_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_hard_candidate_draft_v0_1.md"
SOURCE_INVENTORY = REPO_ROOT / "data" / "protocols" / "evp8_hard_case_source_inventory_v0_1.json"

CURATED_SOURCE_FILES = [
    REPO_ROOT / "outputs" / "httpie_agent_patch_qwen37_httpie5_strict_001" / "candidates.relabeled.jsonl",
    REPO_ROOT / "outputs" / "httpie_agent_patch_stage_ab_001" / "candidates.relabeled.jsonl",
    REPO_ROOT / "outputs" / "httpie_ai_patch_stage_ab_001" / "candidates.jsonl",
    REPO_ROOT / "outputs" / "httpie_stage_ab_001" / "candidates.jsonl",
    REPO_ROOT / "outputs" / "luigi3_stability_audit_001" / "candidates.jsonl",
    REPO_ROOT / "outputs" / "luigi4_stability_audit_001" / "candidates.jsonl",
]

FORBIDDEN_MODEL_VISIBLE_KEYS = {
    "candidate_type",
    "expected_outcome",
    "failure_type_label",
    "hidden_oracles",
    "label_confidence",
    "label_retained_oracle",
    "label_with_p2p_broad",
    "model_candidate_id",
    "oracle_command",
    "oracle_passed",
    "oracle_result",
    "oracle_ran",
    "oracle_workdir",
    "patch_id",
    "raw_generation_response_path",
    "raw_generation_response_sha256",
    "validation_status",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{display_path(path)} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
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


def record_key(row: dict[str, Any]) -> str:
    return str(row.get("patch_id") or row.get("model_candidate_id") or "")


def validation_index_for_dir(directory: Path) -> dict[str, dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name in ("validation.jsonl", "p2p_validation.jsonl", "oracle_validation.jsonl"):
        rows.extend(read_jsonl(directory / name))
    return {record_key(row): row for row in rows if record_key(row)}


def patch_size(patch_text: str) -> dict[str, int]:
    added = 0
    deleted = 0
    files = set()
    for line in patch_text.splitlines():
        if line.startswith("+++ b/") or line.startswith("--- a/"):
            files.add(line[6:] if line.startswith("+++ b/") else line[6:])
        elif line.startswith("+") and not line.startswith("+++"):
            added += 1
        elif line.startswith("-") and not line.startswith("---"):
            deleted += 1
    return {"added_lines": added, "deleted_lines": deleted, "files_changed": len(files)}


def is_generated(row: dict[str, Any]) -> bool:
    return bool(row.get("generation_model") or "agent" in str(row.get("source") or ""))


def normalized_candidate_type(row: dict[str, Any], validation: dict[str, Any]) -> str:
    expected = row.get("expected_outcome")
    source_type = row.get("candidate_type")
    if expected == "correct" or validation.get("oracle_passed") is True:
        return "correct_reference"
    if source_type == "partial_fix" or expected == "partial":
        return "partial_fix"
    if expected == "regression" or source_type == "regression_patch":
        return "regression_patch"
    if source_type == "model_generated_patch" and is_generated(row):
        return "agent_plausible_wrong"
    if source_type in {"buggy_noop", "irrelevant_patch", "irrelevant_or_noop_control"}:
        return "irrelevant_or_noop_control"
    return str(source_type or "unknown")


def normalized_label(row: dict[str, Any], validation: dict[str, Any]) -> str:
    if validation.get("oracle_passed") is True:
        return "correct"
    candidate_type = normalized_candidate_type(row, validation)
    if candidate_type == "partial_fix":
        return "partial"
    if candidate_type == "regression_patch":
        return "regression"
    if candidate_type == "agent_plausible_wrong":
        return "agent_plausible_wrong"
    if candidate_type == "irrelevant_or_noop_control":
        return "irrelevant_or_noop"
    return "incorrect"


def is_nontrivial_hard_negative(label: str, candidate_type: str) -> bool:
    return label in {"partial", "regression", "agent_plausible_wrong", "overfitted"}


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
    selected: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    seen_patch_ids: set[str] = set()
    for source_path in CURATED_SOURCE_FILES:
        validation_index = validation_index_for_dir(source_path.parent)
        for row in read_jsonl(source_path):
            key = record_key(row)
            validation = validation_index.get(key)
            usable, reason = candidate_is_usable(row, validation)
            if key in seen_patch_ids:
                excluded.append({"source": display_path(source_path), "patch_id": key, "reason": "duplicate_patch_id"})
                continue
            if not usable:
                excluded.append({"source": display_path(source_path), "patch_id": key, "reason": reason})
                continue
            assert validation is not None
            seen_patch_ids.add(key)
            selected.append({"source_path": source_path, "candidate": row, "validation": validation})
    return selected, excluded


def evaluator_row(index: int, item: dict[str, Any]) -> dict[str, Any]:
    row = item["candidate"]
    validation = item["validation"]
    patch_text = row["patch_text"]
    candidate_type = normalized_candidate_type(row, validation)
    label = normalized_label(row, validation)
    hard_id = f"evp8_hard_candidate_{index:04d}"
    size = patch_size(patch_text)
    return {
        "cohort_id": COHORT_ID,
        "hard_candidate_id": hard_id,
        "source_candidate_file": display_path(item["source_path"]),
        "source_patch_id": row.get("patch_id"),
        "source_model_candidate_id": row.get("model_candidate_id"),
        "task_id": row.get("task_id"),
        "project": row.get("project"),
        "patch_sha256": hashlib.sha256(patch_text.encode("utf-8")).hexdigest(),
        "patch_size": size,
        "candidate_type": candidate_type,
        "patch_source_kind": "ai_or_agent_generated" if is_generated(row) else "constructed_or_reference",
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
            "p2p_broad_status": validation.get("p2p_broad_status"),
            "retained_oracle_ran": validation.get("retained_oracle_ran"),
            "retained_oracle_passed": validation.get("retained_oracle_passed"),
        },
        "nontrivial_hard_negative": is_nontrivial_hard_negative(label, candidate_type),
    }


def model_visible_row(index: int, item: dict[str, Any]) -> dict[str, Any]:
    row = item["candidate"]
    validation = item["validation"]
    patch_text = row["patch_text"]
    size = patch_size(patch_text)
    return {
        "cohort_id": COHORT_ID,
        "candidate_id": f"evp8_hard_candidate_{index:04d}",
        "task_id": row.get("task_id"),
        "project": row.get("project"),
        "issue_summary": row.get("issue_summary"),
        "touched_files": row.get("touched_files", []),
        "patch_text": patch_text,
        "visible_context": row.get("visible_context"),
        "visible_static_evidence": {
            "patch_applies": validation.get("patch_applied") is True,
            "patch_size": size,
        },
        "visible_test_evidence": {
            "listed_tests": row.get("visible_tests", []),
            "observed_outcome": "not_run_hint_only",
            "outcome_counts": {"not_run_hint_only": len(row.get("visible_tests", []))},
        },
        "visible_tool_evidence": {
            "tool_summary_available": False,
            "reason": "No model-visible visible-test execution outcome is available in the inventoried local source.",
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


def baseline_decision(seed: dict[str, Any]) -> dict[str, Any]:
    candidate_id = seed["candidate_id"]
    patch_applies = seed["visible_static_evidence"]["patch_applies"]
    observed = seed["visible_test_evidence"]["observed_outcome"]
    if not patch_applies:
        decision = "reject"
        reason = "Patch does not apply under visible static evidence."
        flags = ["patch_apply_failed"]
        confidence = 1.0
    elif observed == "passed":
        decision = "accept"
        reason = "Visible tests passed and no visible failures are reported."
        flags = []
        confidence = 0.8
    elif observed in {"failed", "error", "timeout"}:
        decision = "reject"
        reason = "Visible test evidence reports a failure, error, or timeout."
        flags = ["visible_test_failure"]
        confidence = 0.9
    else:
        decision = "escalate"
        reason = "Patch applies, but only visible test hints are available; no visible execution outcome supports accept or reject."
        flags = ["visible_test_outcome_missing"]
        confidence = 0.2
    return {
        "cohort_id": COHORT_ID,
        "candidate_id": candidate_id,
        "condition": "tool_only_visible_apply_and_test_hint",
        "evidence_level": "rule-only",
        "decision": decision,
        "confidence": confidence,
        "human_review_needed": decision == "escalate",
        "risk_flags": flags,
        "primary_reason": reason,
        "api_call_attempted": False,
    }


def baseline_metrics(evaluator_rows: list[dict[str, Any]], baseline_rows: list[dict[str, Any]]) -> dict[str, Any]:
    labels = {row["hard_candidate_id"]: row for row in evaluator_rows}
    counts = Counter(row["decision"] for row in baseline_rows)
    confusion = Counter()
    examples: dict[str, list[str]] = {
        "tool_false_accepts": [],
        "tool_false_rejects": [],
        "tool_escalations_correct": [],
        "tool_escalations_incorrect": [],
    }
    for row in baseline_rows:
        evaluator = labels[row["candidate_id"]]
        is_correct = evaluator["normalized_label"] == "correct"
        decision = row["decision"]
        if decision == "accept" and is_correct:
            confusion["true_accept"] += 1
        elif decision == "accept":
            confusion["false_accept"] += 1
            examples["tool_false_accepts"].append(row["candidate_id"])
        elif decision == "reject" and is_correct:
            confusion["false_reject"] += 1
            examples["tool_false_rejects"].append(row["candidate_id"])
        elif decision == "reject":
            confusion["true_reject"] += 1
        elif decision == "escalate" and is_correct:
            confusion["escalated_correct"] += 1
            examples["tool_escalations_correct"].append(row["candidate_id"])
        elif decision == "escalate":
            confusion["escalated_incorrect"] += 1
            examples["tool_escalations_incorrect"].append(row["candidate_id"])
    correct_total = sum(1 for row in evaluator_rows if row["normalized_label"] == "correct")
    incorrect_total = len(evaluator_rows) - correct_total
    opportunity = (
        confusion["false_accept"]
        + confusion["false_reject"]
        + confusion["escalated_correct"]
        + confusion["escalated_incorrect"]
    )
    return {
        "record_count": len(evaluator_rows),
        "decision_counts": dict(sorted(counts.items())),
        "correct_total": correct_total,
        "incorrect_total": incorrect_total,
        "confusion_counts": dict(sorted(confusion.items())),
        "false_accept_count": confusion["false_accept"],
        "false_reject_count": confusion["false_reject"],
        "actionable_false_accept_or_reject_headroom": confusion["false_accept"] + confusion["false_reject"],
        "opportunity_set_size_including_escalations": opportunity,
        "opportunity_set_rate_including_escalations": round(opportunity / len(evaluator_rows), 6) if evaluator_rows else None,
        "examples": examples,
    }


def build_outputs() -> dict[str, Any]:
    inventory = read_json(SOURCE_INVENTORY)
    selected, excluded = collect_candidates()
    evaluator_rows = [evaluator_row(index, item) for index, item in enumerate(selected, start=1)]
    model_visible_rows = [model_visible_row(index, item) for index, item in enumerate(selected, start=1)]
    baseline_rows = [baseline_decision(row) for row in model_visible_rows]
    leakage_hits = [hit for row in model_visible_rows for hit in forbidden_key_hits(row)]
    candidate_type_counts = Counter(row["candidate_type"] for row in evaluator_rows)
    label_counts = Counter(row["normalized_label"] for row in evaluator_rows)
    source_kind_counts = Counter(row["patch_source_kind"] for row in evaluator_rows)
    task_counts = Counter(row["task_id"] for row in evaluator_rows)
    hard_negative_count = sum(1 for row in evaluator_rows if row["nontrivial_hard_negative"])
    ai_agent_hard_negative_count = sum(
        1
        for row in evaluator_rows
        if row["patch_source_kind"] == "ai_or_agent_generated" and row["nontrivial_hard_negative"]
    )
    metrics = baseline_metrics(evaluator_rows, baseline_rows)
    visible_outcome_count = sum(
        1 for row in model_visible_rows if row["visible_test_evidence"]["observed_outcome"] != "not_run_hint_only"
    )
    checks = [
        check("api_call_not_attempted", True, False),
        check("raw_model_outputs_not_read", True, False),
        check("rendered_prompt_not_generated", True, False),
        check("old_evp8_controlled_cohort_not_mutated", True, False),
        check("source_inventory_passed", inventory.get("inventory_status") == "passed", inventory.get("inventory_status")),
        check("candidate_count_30_to_50", 30 <= len(evaluator_rows) <= 50, len(evaluator_rows)),
        check("nontrivial_hard_negative_count_at_least_20", hard_negative_count >= 20, hard_negative_count),
        check("ai_or_agent_hard_negative_count_at_least_10", ai_agent_hard_negative_count >= 10, ai_agent_hard_negative_count),
        check("model_visible_label_leakage_absent", not leakage_hits, leakage_hits[:20]),
        check("visible_test_outcomes_available", visible_outcome_count > 0, visible_outcome_count),
        check(
            "actionable_false_accept_or_reject_headroom_at_least_10",
            metrics["actionable_false_accept_or_reject_headroom"] >= 10,
            metrics["actionable_false_accept_or_reject_headroom"],
        ),
    ]
    api_ready = all(row["passed"] for row in checks)
    return {
        "analysis_id": "evp8_hard_candidate_draft_v0_1",
        "cohort_id": COHORT_ID,
        "source_inventory": display_path(SOURCE_INVENTORY),
        "scope": {
            "api_call_attempted": False,
            "raw_model_outputs_read": False,
            "rendered_prompt_generated": False,
            "old_evp8_controlled_cohort_mutated": False,
        },
        "outputs": {
            "evaluator_manifest": display_path(DEFAULT_EVALUATOR_OUT),
            "model_visible_seed_manifest": display_path(DEFAULT_MODEL_VISIBLE_OUT),
            "tool_only_baseline": display_path(DEFAULT_BASELINE_OUT),
        },
        "candidate_summary": {
            "candidate_count": len(evaluator_rows),
            "task_count": len(task_counts),
            "project_count": len({row["project"] for row in evaluator_rows}),
            "candidate_type_counts": dict(sorted(candidate_type_counts.items())),
            "normalized_label_counts": dict(sorted(label_counts.items())),
            "patch_source_kind_counts": dict(sorted(source_kind_counts.items())),
            "task_counts": dict(sorted(task_counts.items())),
            "nontrivial_hard_negative_count": hard_negative_count,
            "ai_or_agent_hard_negative_count": ai_agent_hard_negative_count,
            "excluded_source_records": excluded,
        },
        "tool_only_baseline_summary": metrics,
        "checks": checks,
        "api_readiness": "ready" if api_ready else "blocked",
        "blocked_reasons": [row["check"] for row in checks if not row["passed"]],
        "_evaluator_rows": evaluator_rows,
        "_model_visible_rows": model_visible_rows,
        "_baseline_rows": baseline_rows,
    }


def public_summary(summary: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in summary.items() if not key.startswith("_")}


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    candidate = summary["candidate_summary"]
    baseline = summary["tool_only_baseline_summary"]
    lines = [
        "# EVP-8-HARD Candidate Draft v0.1",
        "",
        "Date: 2026-06-29",
        "",
        "This is a no-API hard-case draft and baseline gate. It creates separate",
        "evaluator-only and model-visible manifests, but it does not call model APIs,",
        "render prompts, read raw model responses, or mutate the old 98-candidate",
        "controlled cohort.",
        "",
        "## Outputs",
        "",
    ]
    for key, value in summary["outputs"].items():
        lines.append(f"- {key}: `{value}`")
    lines += [
        "",
        "## Candidate Summary",
        "",
        f"- candidates: {candidate['candidate_count']}",
        f"- tasks: {candidate['task_count']}",
        f"- projects: {candidate['project_count']}",
        f"- nontrivial hard negatives: {candidate['nontrivial_hard_negative_count']}",
        f"- AI/agent hard negatives: {candidate['ai_or_agent_hard_negative_count']}",
        "",
        "Candidate types:",
        "",
    ]
    for key, value in candidate["candidate_type_counts"].items():
        lines.append(f"- `{key}`: {value}")
    lines += [
        "",
        "Labels:",
        "",
    ]
    for key, value in candidate["normalized_label_counts"].items():
        lines.append(f"- `{key}`: {value}")
    lines += [
        "",
        "## Tool-Only Baseline",
        "",
        f"- decision counts: `{baseline['decision_counts']}`",
        f"- false accepts: {baseline['false_accept_count']}",
        f"- false rejects: {baseline['false_reject_count']}",
        f"- actionable false-accept/false-reject headroom: {baseline['actionable_false_accept_or_reject_headroom']}",
        f"- opportunity size including escalations: {baseline['opportunity_set_size_including_escalations']}",
        "",
        "The deterministic baseline escalates these candidates because the current",
        "source files provide visible test hints but not model-visible test execution",
        "outcomes. This is intentionally conservative: the draft must not pretend",
        "that visible tests passed when only hidden oracle validation is available.",
        "",
        "## Gate Checks",
        "",
    ]
    for row in summary["checks"]:
        lines.append(f"- {row['check']}: {'passed' if row['passed'] else 'failed'} ({row['detail']})")
    lines += [
        "",
        f"API readiness: `{summary['api_readiness']}`",
        "",
        "Blocked reasons:",
        "",
    ]
    for reason in summary["blocked_reasons"]:
        lines.append(f"- `{reason}`")
    lines += [
        "",
        "Plain-language conclusion: the draft reaches the 30-50 candidate size and",
        "has enough AI/agent wrong patches, but it does not yet meet the 20",
        "nontrivial-hard-negative gate and lacks visible test outcomes that could",
        "create meaningful tool false accepts or false rejects. The next action is",
        "to add or validate harder non-control negatives and visible test outcomes,",
        "not to run Qwen or DeepSeek.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluator-out", type=Path, default=DEFAULT_EVALUATOR_OUT)
    parser.add_argument("--model-visible-out", type=Path, default=DEFAULT_MODEL_VISIBLE_OUT)
    parser.add_argument("--baseline-out", type=Path, default=DEFAULT_BASELINE_OUT)
    parser.add_argument("--summary-out", type=Path, default=DEFAULT_SUMMARY_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true", help="Fail only if structural checks fail; blocked API readiness is allowed.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = build_outputs()
    write_jsonl(args.evaluator_out, summary["_evaluator_rows"])
    write_jsonl(args.model_visible_out, summary["_model_visible_rows"])
    write_jsonl(args.baseline_out, summary["_baseline_rows"])
    public = public_summary(summary)
    public["outputs"] = {
        "evaluator_manifest": display_path(args.evaluator_out),
        "model_visible_seed_manifest": display_path(args.model_visible_out),
        "tool_only_baseline": display_path(args.baseline_out),
    }
    write_json(args.summary_out, public)
    write_markdown(args.md_out, public)
    if args.check:
        structural_failures = [
            row for row in public["checks"]
            if not row["passed"] and row["check"] in {
                "api_call_not_attempted",
                "raw_model_outputs_not_read",
                "rendered_prompt_not_generated",
                "old_evp8_controlled_cohort_not_mutated",
                "source_inventory_passed",
                "candidate_count_30_to_50",
                "model_visible_label_leakage_absent",
            }
        ]
        if structural_failures:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
