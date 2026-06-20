"""Build EVP-8 packet and schema dry-run summaries without API calls.

The dry-run validates planned packet structure for the frozen EVP-8 candidate
set and protocol ladder. It intentionally does not write full evidence packet
JSONL records and does not call model APIs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_IN = REPO_ROOT / "data" / "protocols" / "evp8_protocol_v0_1.json"
CANDIDATE_SET_IN = REPO_ROOT / "data" / "protocols" / "evp8_candidate_set_v0_1.json"
PACKET_SUMMARY_OUT = REPO_ROOT / "data" / "protocols" / "evp8_evidence_packet_dry_run_summary_v0_1.json"
SCHEMA_SUMMARY_OUT = REPO_ROOT / "data" / "protocols" / "evp8_schema_dry_run_summary_v0_1.json"

MODEL_VISIBLE_LEVELS = ("E0", "E1", "E2", "E3", "E4", "E5", "E6")
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


def _packet_skeleton(candidate: dict[str, Any], level: dict[str, Any]) -> dict[str, Any]:
    field_groups = level.get("model_visible_field_groups") or []
    required_fields = level.get("required_fields") or []
    return {
        "packet_id": f"{candidate['evp8_candidate_id']}__{level['level']}__dry_run",
        "cohort_id": "EVP-8",
        "protocol_id": "evp8_journal_full_ladder_v0_1",
        "candidate_set_id": candidate["candidate_set_id"],
        "candidate_id": candidate["evp8_candidate_id"],
        "source_candidate_id": candidate["source_candidate_id"],
        "task_id": candidate["task_id"],
        "project": candidate["project"],
        "evidence_level": level["level"],
        "evidence_level_name": level["level_name"],
        "model_visible_field_groups": field_groups,
        "required_fields": required_fields,
        "field_group_count": len(field_groups),
        "required_field_count": len(required_fields),
        "packet_materialization": "skeleton_only_no_evidence_values",
        "model_visible_record": True,
    }


def _schema_output() -> dict[str, Any]:
    return {
        "decision": "escalate",
        "confidence": 0.0,
        "primary_reason": "Phase 0 packet skeletons contain no behavioral evidence values.",
        "evidence_used": [],
        "visible_contradictions": ["dry_run_packet_skeleton_only"],
        "risk_flags": ["insufficient_evidence"],
        "human_review_needed": True,
    }


def _validate_output_schema(output: dict[str, Any], output_schema: dict[str, Any]) -> str | None:
    required_keys = output_schema.get("required_keys") or []
    missing = [key for key in required_keys if key not in output]
    if missing:
        return "missing_keys:" + ",".join(missing)
    extra_forbidden = [key for key in output_schema.get("forbidden_output_keys") or [] if key in output]
    if extra_forbidden:
        return "forbidden_keys:" + ",".join(extra_forbidden)
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
    levels = _level_map(spec)
    skeletons = [
        _packet_skeleton(candidate, levels[level])
        for candidate in candidates
        for level in MODEL_VISIBLE_LEVELS
    ]
    level_counts = _counts(skeleton["evidence_level"] for skeleton in skeletons)
    expected_level_counts = {level: len(candidates) for level in MODEL_VISIBLE_LEVELS}
    missing_levels = [level for level in MODEL_VISIBLE_LEVELS if level not in levels]
    leakage = _leakage_findings(skeletons)
    field_group_count_errors = [
        skeleton["packet_id"]
        for skeleton in skeletons
        if skeleton["field_group_count"] != MODEL_VISIBLE_LEVELS.index(skeleton["evidence_level"]) + 1
    ]
    packet_summary = {
        "cohort_id": "EVP-8",
        "protocol_id": spec.get("protocol_id"),
        "candidate_set_id": candidate_set.get("candidate_set_id"),
        "candidate_count": len(candidates),
        "model_visible_levels": list(MODEL_VISIBLE_LEVELS),
        "planned_packet_skeleton_count": len(skeletons),
        "expected_packet_skeleton_count": len(candidates) * len(MODEL_VISIBLE_LEVELS),
        "packet_skeleton_counts_by_level": level_counts,
        "expected_packet_skeleton_counts_by_level": expected_level_counts,
        "missing_model_visible_levels": missing_levels,
        "field_group_count_error_count": len(field_group_count_errors),
        "field_group_count_error_sample": field_group_count_errors[:20],
        "leakage_findings_count": len(leakage),
        "leakage_findings": leakage,
        "packet_dry_run_status": "passed" if not missing_levels and level_counts == expected_level_counts and not leakage and not field_group_count_errors else "failed",
        "api_call_attempted": False,
        "full_evidence_packets_generated": False,
        "raw_prompt_text_stored": False,
        "claim_boundary": "This validates planned EVP-8 packet skeleton structure only; it is not final evidence-packet generation.",
    }

    outputs = [_schema_output() for _ in skeletons]
    invalid_reasons = [
        reason
        for reason in (_validate_output_schema(output, spec.get("output_schema") or {}) for output in outputs)
        if reason is not None
    ]
    output_leakage = _leakage_findings(outputs)
    schema_summary = {
        "cohort_id": "EVP-8",
        "protocol_id": spec.get("protocol_id"),
        "candidate_set_id": candidate_set.get("candidate_set_id"),
        "schema_dry_run_record_count": len(outputs),
        "expected_schema_dry_run_record_count": len(candidates) * len(MODEL_VISIBLE_LEVELS),
        "schema_dry_run_counts_by_level": level_counts,
        "valid_parse_count": len(outputs) - len(invalid_reasons),
        "invalid_parse_count": len(invalid_reasons),
        "invalid_reason_counts": _counts(invalid_reasons),
        "leakage_findings_count": len(output_leakage),
        "leakage_findings": output_leakage,
        "schema_dry_run_status": "passed" if not invalid_reasons and not output_leakage else "failed",
        "output_records_stored": False,
        "api_call_attempted": False,
        "full_evidence_packets_generated": False,
        "claim_boundary": "This validates output parser/schema shape only; it is not LLM verifier evidence.",
    }
    return packet_summary, schema_summary


def _check(packet_summary: dict[str, Any], schema_summary: dict[str, Any]) -> None:
    if packet_summary["packet_dry_run_status"] != "passed":
        raise SystemExit(f"EVP-8 packet dry-run failed: {packet_summary}")
    if schema_summary["schema_dry_run_status"] != "passed":
        raise SystemExit(f"EVP-8 schema dry-run failed: {schema_summary}")
    if packet_summary["planned_packet_skeleton_count"] != 686:
        raise SystemExit("EVP-8 packet skeleton count must be 686 for 98 candidates x 7 levels")
    if schema_summary["valid_parse_count"] != 686:
        raise SystemExit("EVP-8 schema dry-run valid parse count must be 686")
    if packet_summary["full_evidence_packets_generated"] is not False:
        raise SystemExit("packet dry-run must not generate full evidence packets")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-in", type=Path, default=SPEC_IN)
    parser.add_argument("--candidate-set-in", type=Path, default=CANDIDATE_SET_IN)
    parser.add_argument("--packet-summary-out", type=Path, default=PACKET_SUMMARY_OUT)
    parser.add_argument("--schema-summary-out", type=Path, default=SCHEMA_SUMMARY_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    packet_summary, schema_summary = build_summaries(args.spec_in, args.candidate_set_in)
    _write_json(args.packet_summary_out, packet_summary)
    _write_json(args.schema_summary_out, schema_summary)
    if args.check:
        _check(packet_summary, schema_summary)
    print(json.dumps({"packet_summary": packet_summary, "schema_summary": schema_summary}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
