"""Build EVP-8 cost-observability and deterministic-baseline dry-run summaries.

This Phase 0 check validates the planned model-call accounting surface and the
deterministic baseline output schema without reading local API configs, reading
credentials, generating raw outputs, or calling model APIs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_IN = REPO_ROOT / "data" / "protocols" / "evp8_protocol_v0_1.json"
CANDIDATE_SET_IN = REPO_ROOT / "data" / "protocols" / "evp8_candidate_set_v0_1.json"
COST_SUMMARY_OUT = REPO_ROOT / "data" / "protocols" / "evp8_cost_observability_dry_run_v0_1.json"
BASELINE_SUMMARY_OUT = REPO_ROOT / "data" / "protocols" / "evp8_deterministic_tool_baseline_dry_run_v0_1.json"

MODEL_VISIBLE_LEVELS = ("E0", "E1", "E2", "E3", "E4", "E5", "E6")
REQUIRED_USAGE_COST_FIELDS = (
    "record_prompt_tokens",
    "record_completion_tokens",
    "record_total_tokens",
    "record_provider_cost_usd",
    "record_cost_source",
)
FORBIDDEN_MARKERS = (
    "expected_outcome",
    "candidate_type",
    "failure_type_label",
    "label_with_p2p_broad",
    "label_retained_oracle",
    "hidden_oracles",
    "hidden_oracle_paths",
    "hidden_oracle_result",
    "hidden_oracle_results",
    "patch_materialization",
    "patch_source_label",
    "source_model_candidate_id",
    "validation_summary",
    "reference_patch_provenance",
    "reference_patch_label",
    "evaluator_merge_label",
    "correct_under_f2p_and_p2p_broad",
    "incorrect_issue_not_fixed",
    "incorrect_regression",
    "correct_reference",
    "irrelevant_patch",
    "buggy_noop",
    "partial_fix",
    "regression_patch",
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _counts(values: Any) -> dict[str, int]:
    result: dict[str, int] = {}
    for value in values:
        key = str(value)
        result[key] = result.get(key, 0) + 1
    return dict(sorted(result.items()))


def _level_map(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {level["level"]: level for level in spec.get("evidence_ladder", [])}


def _phase_models(spec: dict[str, Any], phase_key: str) -> list[str]:
    return [
        model["model_id"]
        for model in (spec.get("model_plan") or {}).get(phase_key, [])
    ]


def _planned_records(candidates: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "candidate_id": candidate["evp8_candidate_id"],
            "evidence_level": level,
        }
        for candidate in candidates
        for level in MODEL_VISIBLE_LEVELS
    ]


def _baseline_output(record: dict[str, str], levels: dict[str, dict[str, Any]]) -> dict[str, Any]:
    level = record["evidence_level"]
    field_groups = levels[level].get("model_visible_field_groups") or []
    return {
        "decision": "escalate",
        "confidence": 0.0,
        "primary_reason": (
            "Phase 0 deterministic baseline dry-run has only planned model-visible "
            "evidence slots, not observed evidence values."
        ),
        "evidence_used": [f"planned_field_group:{field_group}" for field_group in field_groups],
        "visible_contradictions": [],
        "risk_flags": ["insufficient_evidence"],
        "human_review_needed": True,
    }


def _validate_output_schema(output: dict[str, Any], output_schema: dict[str, Any]) -> str | None:
    required_keys = output_schema.get("required_keys") or []
    missing = [key for key in required_keys if key not in output]
    if missing:
        return "missing_keys:" + ",".join(missing)
    forbidden = [key for key in output_schema.get("forbidden_output_keys") or [] if key in output]
    if forbidden:
        return "forbidden_keys:" + ",".join(forbidden)
    if output["decision"] not in set(output_schema.get("decision_values") or []):
        return f"invalid_decision:{output['decision']}"
    if not isinstance(output["confidence"], (int, float)) or not 0 <= output["confidence"] <= 1:
        return "invalid_confidence"
    if not isinstance(output["primary_reason"], str) or not output["primary_reason"]:
        return "invalid_primary_reason"
    if not isinstance(output["evidence_used"], list):
        return "invalid_evidence_used"
    if not isinstance(output["visible_contradictions"], list):
        return "invalid_visible_contradictions"
    risk_values = set(output_schema.get("risk_flag_values") or [])
    if not isinstance(output["risk_flags"], list) or any(flag not in risk_values for flag in output["risk_flags"]):
        return "invalid_risk_flags"
    if not isinstance(output["human_review_needed"], bool):
        return "invalid_human_review_needed"
    return None


def _leakage_findings(value: Any) -> list[str]:
    serialized = json.dumps(value, ensure_ascii=False).lower()
    return [marker for marker in FORBIDDEN_MARKERS if marker.lower() in serialized]


def build_summaries(spec_path: Path, candidate_set_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    spec = _load_json(spec_path)
    candidate_set = _load_json(candidate_set_path)
    candidates = candidate_set.get("records") or []
    planned_records = _planned_records(candidates)
    phase1_models = _phase_models(spec, "phase1_first_batch")
    phase2_models = _phase_models(spec, "phase2_later_batch")
    all_models = phase1_models + phase2_models
    planned_calls_per_model = len(planned_records)
    planned_calls_by_level = _counts(record["evidence_level"] for record in planned_records)

    routing = spec.get("routing_policy") or {}
    cost_policy = spec.get("cost_observability") or {}
    missing_usage_cost_fields = [
        field for field in REQUIRED_USAGE_COST_FIELDS if cost_policy.get(field) is not True
    ]
    routing_failures = [
        key
        for key, expected in {
            "exact_model_id_required": True,
            "record_actual_model_id": True,
            "record_actual_provider": True,
            "allow_unrecorded_provider_fallback": False,
        }.items()
        if routing.get(key) is not expected
    ]
    retry_policy = routing.get("retry_policy") or {}
    retry_failures = [
        key
        for key, expected in {
            "retry_only_on_transport_or_rate_limit": True,
            "no_silent_retry_for_parse_invalid": True,
        }.items()
        if retry_policy.get(key) is not expected
    ]
    cost_summary = {
        "cohort_id": "EVP-8",
        "protocol_id": spec.get("protocol_id"),
        "candidate_set_id": candidate_set.get("candidate_set_id"),
        "candidate_count": len(candidates),
        "model_visible_levels": list(MODEL_VISIBLE_LEVELS),
        "planned_calls_per_model": planned_calls_per_model,
        "expected_planned_calls_per_model": len(candidates) * len(MODEL_VISIBLE_LEVELS),
        "planned_calls_by_level": planned_calls_by_level,
        "phase1_first_batch_models": phase1_models,
        "phase2_later_batch_models": phase2_models,
        "all_planned_model_count": len(all_models),
        "phase1_planned_call_count": planned_calls_per_model * len(phase1_models),
        "phase2_planned_call_count": planned_calls_per_model * len(phase2_models),
        "all_models_planned_call_count": planned_calls_per_model * len(all_models),
        "required_usage_cost_fields": list(REQUIRED_USAGE_COST_FIELDS),
        "missing_usage_cost_fields": missing_usage_cost_fields,
        "routing_policy_failures": routing_failures,
        "retry_policy_failures": retry_failures,
        "temperature": routing.get("temperature"),
        "max_output_tokens": routing.get("max_output_tokens"),
        "unknown_usage_blocks_api": True,
        "missing_provider_or_model_id_blocks_api": True,
        "deepseek_qwen_excluded_from_later_openrouter_budget_estimate": cost_policy.get(
            "exclude_deepseek_qwen_from_later_openrouter_budget_estimate"
        )
        is True,
        "cost_observability_dry_run_status": "passed"
        if planned_calls_per_model == len(candidates) * len(MODEL_VISIBLE_LEVELS)
        and not missing_usage_cost_fields
        and not routing_failures
        and not retry_failures
        and phase1_models == ["deepseek/deepseek-v4-pro", "qwen/qwen3.7-max"]
        else "failed",
        "api_call_attempted": False,
        "local_api_config_read": False,
        "raw_outputs_generated": False,
        "claim_boundary": "This validates planned usage/cost observability fields only; it is not a billing statement.",
    }

    levels = _level_map(spec)
    outputs = [_baseline_output(record, levels) for record in planned_records]
    invalid_reasons = [
        reason
        for reason in (_validate_output_schema(output, spec.get("output_schema") or {}) for output in outputs)
        if reason is not None
    ]
    leakage = _leakage_findings(outputs)
    baseline_summary = {
        "cohort_id": "EVP-8",
        "protocol_id": spec.get("protocol_id"),
        "candidate_set_id": candidate_set.get("candidate_set_id"),
        "candidate_count": len(candidates),
        "model_visible_levels": list(MODEL_VISIBLE_LEVELS),
        "planned_baseline_record_count": len(outputs),
        "expected_planned_baseline_record_count": len(candidates) * len(MODEL_VISIBLE_LEVELS),
        "baseline_counts_by_level": planned_calls_by_level,
        "decision_counts": _counts(output["decision"] for output in outputs),
        "valid_schema_count": len(outputs) - len(invalid_reasons),
        "invalid_schema_count": len(invalid_reasons),
        "invalid_reason_counts": _counts(invalid_reasons),
        "leakage_findings_count": len(leakage),
        "leakage_findings": leakage,
        "model_visible_evidence_slots_only": True,
        "candidate_labels_read": False,
        "evaluator_labels_read": False,
        "output_records_stored": False,
        "deterministic_tool_baseline_dry_run_status": "passed"
        if len(outputs) == len(candidates) * len(MODEL_VISIBLE_LEVELS)
        and not invalid_reasons
        and not leakage
        else "failed",
        "api_call_attempted": False,
        "local_api_config_read": False,
        "raw_outputs_generated": False,
        "claim_boundary": "This validates deterministic baseline schema shape only; it is not tool-baseline performance evidence.",
    }
    return cost_summary, baseline_summary


def _check(cost_summary: dict[str, Any], baseline_summary: dict[str, Any]) -> None:
    if cost_summary["cost_observability_dry_run_status"] != "passed":
        raise SystemExit(f"EVP-8 cost-observability dry-run failed: {cost_summary}")
    if baseline_summary["deterministic_tool_baseline_dry_run_status"] != "passed":
        raise SystemExit(f"EVP-8 deterministic baseline dry-run failed: {baseline_summary}")
    if cost_summary["planned_calls_per_model"] != 686:
        raise SystemExit("EVP-8 cost dry-run planned calls per model must be 686")
    if baseline_summary["planned_baseline_record_count"] != 686:
        raise SystemExit("EVP-8 deterministic baseline dry-run record count must be 686")
    if cost_summary["api_call_attempted"] or baseline_summary["api_call_attempted"]:
        raise SystemExit("EVP-8 dry-runs must not call APIs")
    if cost_summary["local_api_config_read"] or baseline_summary["local_api_config_read"]:
        raise SystemExit("EVP-8 dry-runs must not read local API configs")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-in", type=Path, default=SPEC_IN)
    parser.add_argument("--candidate-set-in", type=Path, default=CANDIDATE_SET_IN)
    parser.add_argument("--cost-summary-out", type=Path, default=COST_SUMMARY_OUT)
    parser.add_argument("--baseline-summary-out", type=Path, default=BASELINE_SUMMARY_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    cost_summary, baseline_summary = build_summaries(args.spec_in, args.candidate_set_in)
    _write_json(args.cost_summary_out, cost_summary)
    _write_json(args.baseline_summary_out, baseline_summary)
    if args.check:
        _check(cost_summary, baseline_summary)
    print(json.dumps({"cost_summary": cost_summary, "baseline_summary": baseline_summary}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
