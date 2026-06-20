"""Audit the EVP-8 no-API protocol specification.

This script validates the machine-readable protocol boundary before any EVP-8
packet generation or model call. It reads only tracked protocol data and does
not read credentials, local API configs, raw model outputs, or ignored outputs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_IN = REPO_ROOT / "data" / "protocols" / "evp8_protocol_v0_1.json"
SUMMARY_OUT = REPO_ROOT / "data" / "protocols" / "evp8_protocol_v0_1_audit_summary.json"

MODEL_VISIBLE_LEVELS = ("E0", "E1", "E2", "E3", "E4", "E5", "E6")
EVALUATOR_ONLY_LEVEL = "E7"
EXPECTED_PHASE1_MODELS = ("deepseek/deepseek-v4-pro", "qwen/qwen3.7-max")
EXPECTED_PHASE2_MODELS = (
    "moonshotai/kimi-k2.6",
    "mistralai/devstral-2512",
    "google/gemini-2.5-flash",
)
FORBIDDEN_MODEL_VISIBLE_FIELDS = {
    "expected_outcome",
    "candidate_type",
    "failure_type_label",
    "hidden_oracle_paths",
    "hidden_oracle_results",
    "hidden_oracle_result",
    "reference_patch_provenance",
    "reference_patch_label",
    "evaluator_merge_label",
}
REQUIRED_STOP_GATE_MARKERS = (
    "leakage",
    "schema",
    "prompt",
    "cost",
    "model",
    "hidden",
)
REQUIRED_COST_FIELDS = (
    "record_prompt_tokens",
    "record_completion_tokens",
    "record_total_tokens",
    "record_provider_cost_usd",
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _level_map(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {level["level"]: level for level in spec.get("evidence_ladder", [])}


def _as_bool(value: Any) -> bool:
    return value is True


def audit_protocol(spec: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    api_blockers: list[str] = []

    if spec.get("protocol_id") != "evp8_journal_full_ladder_v0_1":
        errors.append("unexpected_protocol_id")
    if spec.get("cohort_id") != "EVP-8":
        errors.append("unexpected_cohort_id")
    if spec.get("api_call_attempted") is not False:
        errors.append("api_call_attempted_must_be_false")

    scope_boundary = spec.get("scope_boundary") or {}
    if scope_boundary.get("packet_generation_authorized") is not False:
        errors.append("packet_generation_must_not_be_authorized_by_protocol_spec")
    if scope_boundary.get("model_run_authorized") is not False:
        errors.append("model_run_must_not_be_authorized_by_protocol_spec")

    levels = _level_map(spec)
    _audit_ladder(levels, errors)
    _audit_prompt_and_output_schema(spec, errors, warnings)
    _audit_model_plan(spec, errors)
    _audit_routing_policy(spec, errors)
    _audit_cost_observability(spec, errors)
    _audit_stop_gates(spec, errors)
    _audit_phase0_api_blockers(spec, api_blockers)

    model_visible_levels = [levels[level] for level in MODEL_VISIBLE_LEVELS if level in levels]
    phase1_models = [
        model.get("model_id")
        for model in (spec.get("model_plan") or {}).get("phase1_first_batch", [])
    ]
    phase2_models = [
        model.get("model_id")
        for model in (spec.get("model_plan") or {}).get("phase2_later_batch", [])
    ]
    summary = {
        "protocol_id": spec.get("protocol_id"),
        "cohort_id": spec.get("cohort_id"),
        "candidate_set_version": (spec.get("candidate_set_policy") or {}).get("current_candidate_set_version"),
        "candidate_set_manifest": (spec.get("candidate_set_policy") or {}).get("candidate_set_manifest"),
        "api_call_attempted": spec.get("api_call_attempted"),
        "protocol_spec_audit_status": "passed" if not errors else "failed",
        "phase0_api_readiness": "ready" if not errors and not api_blockers else "not_ready",
        "error_count": len(errors),
        "errors": errors,
        "warning_count": len(warnings),
        "warnings": warnings,
        "api_blocker_count": len(api_blockers),
        "api_blockers": api_blockers,
        "model_visible_levels": list(MODEL_VISIBLE_LEVELS),
        "evaluator_only_levels": [EVALUATOR_ONLY_LEVEL] if EVALUATOR_ONLY_LEVEL in levels else [],
        "model_visible_level_count": len(model_visible_levels),
        "adjacent_delta_count": max(len(model_visible_levels) - 1, 0),
        "field_group_counts_by_level": {
            level["level"]: len(level.get("model_visible_field_groups") or [])
            for level in model_visible_levels
        },
        "adds_evidence_class_by_level": {
            level["level"]: level.get("adds_evidence_class")
            for level in model_visible_levels
        },
        "phase1_models": phase1_models,
        "phase2_models": phase2_models,
        "no_api_boundary": "This audit reads only the tracked EVP-8 protocol spec and does not read credentials or call models.",
        "next_step": (
            "Freeze candidate set, prompt text, packet dry-run, schema dry-run, "
            "prompt-boundary audit, cost-observability dry-run, and deterministic baseline before API."
        ),
    }
    return summary


def _audit_ladder(levels: dict[str, dict[str, Any]], errors: list[str]) -> None:
    expected_levels = set(MODEL_VISIBLE_LEVELS) | {EVALUATOR_ONLY_LEVEL}
    if set(levels) != expected_levels:
        errors.append(f"evidence_levels_mismatch:{sorted(levels)}")
        return

    cumulative_groups: list[str] = []
    seen_added_classes: set[str] = set()
    for level_name in MODEL_VISIBLE_LEVELS:
        level = levels[level_name]
        if level.get("visibility") != "model_visible":
            errors.append(f"{level_name}:visibility_not_model_visible")
        added_class = level.get("adds_evidence_class")
        if not isinstance(added_class, str) or not added_class:
            errors.append(f"{level_name}:missing_added_evidence_class")
            continue
        if added_class in seen_added_classes:
            errors.append(f"{level_name}:duplicate_added_evidence_class:{added_class}")
        seen_added_classes.add(added_class)
        cumulative_groups.append(added_class)
        if level.get("model_visible_field_groups") != cumulative_groups:
            errors.append(
                f"{level_name}:field_groups_not_adjacent_cumulative:"
                f"{level.get('model_visible_field_groups')} != {cumulative_groups}"
            )
        required_fields = set(level.get("required_fields") or [])
        forbidden_visible = sorted(required_fields & FORBIDDEN_MODEL_VISIBLE_FIELDS)
        if forbidden_visible:
            errors.append(f"{level_name}:forbidden_required_fields:{forbidden_visible}")
        must_not_include = set(level.get("must_not_include") or [])
        missing_forbidden = sorted(FORBIDDEN_MODEL_VISIBLE_FIELDS - must_not_include)
        if missing_forbidden:
            errors.append(f"{level_name}:missing_must_not_include:{missing_forbidden}")

    e7 = levels[EVALUATOR_ONLY_LEVEL]
    if e7.get("visibility") != "evaluator_only":
        errors.append("E7:visibility_not_evaluator_only")
    if e7.get("model_visible_field_groups") != []:
        errors.append("E7:model_visible_field_groups_must_be_empty")
    e7_required = set(e7.get("required_fields") or [])
    missing_e7_fields = sorted(FORBIDDEN_MODEL_VISIBLE_FIELDS - e7_required)
    if missing_e7_fields:
        errors.append(f"E7:missing_evaluator_only_fields:{missing_e7_fields}")


def _audit_prompt_and_output_schema(
    spec: dict[str, Any],
    errors: list[str],
    warnings: list[str],
) -> None:
    prompt_policy = spec.get("prompt_policy") or {}
    if prompt_policy.get("prompt_id") != "evp8_visible_evidence_merge_gate_v0_1":
        errors.append("unexpected_prompt_id")
    if prompt_policy.get("visible_payload_only") is not True:
        errors.append("prompt_policy_must_be_visible_payload_only")
    if prompt_policy.get("prompt_text_frozen") is not True:
        warnings.append("prompt_text_not_yet_frozen")
    template_path = prompt_policy.get("prompt_template_path")
    if prompt_policy.get("prompt_text_frozen") is True:
        if not isinstance(template_path, str) or not (REPO_ROOT / template_path).exists():
            errors.append("prompt_template_missing")
        if not prompt_policy.get("prompt_template_sha256"):
            errors.append("prompt_template_sha256_missing")
        for key in ("prompt_manifest", "prompt_boundary_audit"):
            value = prompt_policy.get(key)
            if not isinstance(value, str) or not (REPO_ROOT / value).exists():
                errors.append(f"{key}_missing")

    output_schema = spec.get("output_schema") or {}
    required_keys = set(output_schema.get("required_keys") or [])
    required_output = {
        "decision",
        "confidence",
        "primary_reason",
        "evidence_used",
        "visible_contradictions",
        "risk_flags",
        "human_review_needed",
    }
    if required_keys != required_output:
        errors.append(f"output_required_keys_mismatch:{sorted(required_keys)}")
    if set(output_schema.get("decision_values") or []) != {"accept", "reject", "escalate"}:
        errors.append("output_decision_values_mismatch")
    forbidden_required = sorted(required_keys & FORBIDDEN_MODEL_VISIBLE_FIELDS)
    if forbidden_required:
        errors.append(f"output_schema_forbidden_required_keys:{forbidden_required}")


def _audit_model_plan(spec: dict[str, Any], errors: list[str]) -> None:
    model_plan = spec.get("model_plan") or {}
    phase1 = model_plan.get("phase1_first_batch") or []
    phase2 = model_plan.get("phase2_later_batch") or []
    phase1_models = tuple(model.get("model_id") for model in phase1)
    phase2_models = tuple(model.get("model_id") for model in phase2)
    if phase1_models != EXPECTED_PHASE1_MODELS:
        errors.append(f"phase1_models_mismatch:{phase1_models}")
    if phase2_models != EXPECTED_PHASE2_MODELS:
        errors.append(f"phase2_models_mismatch:{phase2_models}")
    all_models = list(phase1) + list(phase2)
    for model in all_models:
        model_id = model.get("model_id")
        if not isinstance(model_id, str) or "/" not in model_id:
            errors.append(f"model_id_not_fixed_provider_form:{model_id}")
    counted = {
        model.get("model_id"): model.get("cost_counted_in_openrouter_later_model_budget")
        for model in all_models
    }
    if counted.get("deepseek/deepseek-v4-pro") is not False:
        errors.append("deepseek_should_be_excluded_from_later_openrouter_budget")
    if counted.get("qwen/qwen3.7-max") is not False:
        errors.append("qwen_should_be_excluded_from_later_openrouter_budget")
    for model_id in EXPECTED_PHASE2_MODELS:
        if counted.get(model_id) is not True:
            errors.append(f"later_model_should_be_counted:{model_id}")


def _audit_routing_policy(spec: dict[str, Any], errors: list[str]) -> None:
    routing = spec.get("routing_policy") or {}
    expected_true = (
        "exact_model_id_required",
        "record_actual_model_id",
        "record_actual_provider",
    )
    for key in expected_true:
        if not _as_bool(routing.get(key)):
            errors.append(f"routing_policy_{key}_must_be_true")
    if routing.get("allow_unrecorded_provider_fallback") is not False:
        errors.append("unrecorded_provider_fallback_must_be_false")
    if routing.get("temperature") != 0.0:
        errors.append("temperature_must_be_zero")
    if not isinstance(routing.get("max_output_tokens"), int) or routing["max_output_tokens"] <= 0:
        errors.append("max_output_tokens_must_be_positive_int")
    retry_policy = routing.get("retry_policy") or {}
    if retry_policy.get("no_silent_retry_for_parse_invalid") is not True:
        errors.append("parse_invalid_must_not_be_silently_retried")


def _audit_cost_observability(spec: dict[str, Any], errors: list[str]) -> None:
    cost = spec.get("cost_observability") or {}
    for key in REQUIRED_COST_FIELDS:
        if cost.get(key) is not True:
            errors.append(f"cost_observability_missing:{key}")
    if cost.get("exclude_deepseek_qwen_from_later_openrouter_budget_estimate") is not True:
        errors.append("deepseek_qwen_budget_exclusion_not_recorded")


def _audit_stop_gates(spec: dict[str, Any], errors: list[str]) -> None:
    stop_gates = [str(gate).lower() for gate in spec.get("stop_gates") or []]
    joined = "\n".join(stop_gates)
    for marker in REQUIRED_STOP_GATE_MARKERS:
        if marker not in joined:
            errors.append(f"stop_gate_missing_marker:{marker}")


def _audit_phase0_api_blockers(spec: dict[str, Any], api_blockers: list[str]) -> None:
    candidate_policy = spec.get("candidate_set_policy") or {}
    if candidate_policy.get("current_candidate_set_version") == "not_frozen":
        api_blockers.append("candidate_set_not_frozen")
    candidate_manifest = candidate_policy.get("candidate_set_manifest")
    candidate_manifest_ready = False
    if isinstance(candidate_manifest, str) and candidate_manifest:
        candidate_manifest_ready = (REPO_ROOT / candidate_manifest).exists()
    if not candidate_manifest_ready:
        api_blockers.append("candidate_set_manifest_missing")
    prompt_policy = spec.get("prompt_policy") or {}
    if prompt_policy.get("prompt_text_frozen") is not True:
        api_blockers.append("prompt_text_not_frozen")
    prompt_manifest_ready = _tracked_path_exists(prompt_policy.get("prompt_manifest"))
    prompt_boundary_audit_ready = _tracked_path_exists(prompt_policy.get("prompt_boundary_audit"))
    dry_run_artifacts = spec.get("phase0_dry_run_artifacts") or {}
    packet_dry_run_ready = _tracked_path_exists(dry_run_artifacts.get("evidence_packet_dry_run_summary"))
    schema_dry_run_ready = _tracked_path_exists(dry_run_artifacts.get("schema_dry_run_summary"))
    required_outputs = set(spec.get("required_phase0_outputs_before_api") or [])
    already_satisfied = {"tracked_protocol_spec", "protocol_audit_summary"}
    if candidate_manifest_ready:
        already_satisfied.add("candidate_set_manifest")
    if prompt_manifest_ready:
        already_satisfied.add("prompt_manifest")
    if prompt_boundary_audit_ready:
        already_satisfied.add("prompt_boundary_audit")
    if packet_dry_run_ready:
        already_satisfied.add("evidence_packet_dry_run_summary")
    if schema_dry_run_ready:
        already_satisfied.add("schema_dry_run_summary")
    missing_outputs = sorted(required_outputs - already_satisfied)
    if missing_outputs:
        api_blockers.append("missing_phase0_outputs_before_api:" + ",".join(missing_outputs))


def _tracked_path_exists(value: Any) -> bool:
    return isinstance(value, str) and bool(value) and (REPO_ROOT / value).exists()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-in", type=Path, default=SPEC_IN)
    parser.add_argument("--summary-out", type=Path, default=SUMMARY_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    spec = _load_json(args.spec_in)
    summary = audit_protocol(spec)
    _write_json(args.summary_out, summary)

    if args.check and summary["protocol_spec_audit_status"] != "passed":
        raise SystemExit(f"EVP-8 protocol spec audit failed: {summary['errors']}")
    if args.check and summary["api_call_attempted"] is not False:
        raise SystemExit("EVP-8 protocol audit must be no-API")

    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
