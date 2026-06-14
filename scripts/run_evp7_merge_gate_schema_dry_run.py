"""Generate EVP-7 merge-gate schema dry-run outputs.

This is a no-API schema stability check. It renders deterministic
accept/reject/escalate JSON objects from model-visible evidence packets only,
then parses and validates those objects as the future LLM merge-gate runner
would do.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKETS_IN = REPO_ROOT / "data" / "evidence" / "evp7_evidence_packets.jsonl"
REVIEWS_OUT = REPO_ROOT / "data" / "reviews" / "evp7_merge_gate_schema_dry_run.jsonl"
SUMMARY_OUT = REPO_ROOT / "data" / "reviews" / "evp7_merge_gate_schema_dry_run_summary.json"

REQUIRED_SCHEMA_KEYS = (
    "decision",
    "confidence",
    "primary_reason",
    "evidence_used",
    "risk_flags",
    "suspected_failure_type",
    "human_review_needed",
)
VALID_DECISIONS = {"accept", "reject", "escalate"}
VALID_FAILURE_TYPES = {
    "none",
    "partial_fix",
    "under_fix",
    "regression",
    "irrelevant",
    "non_applicable",
    "unknown",
}
EVIDENCE_LEVELS = ("E0", "E2", "E4", "E6")
EVALUATOR_MARKERS = (
    "label_with_p2p_broad",
    "label_retained_oracle",
    "candidate_type",
    "failure_type_label",
    "expected_outcome",
    "hidden_oracles",
    "patch_id",
    "correct_under_f2p_and_p2p_broad",
    "incorrect_issue_not_fixed",
    "retained_oracle",
    "hidden_oracle",
    "correct_reference",
    "partial_fix",
    "irrelevant_patch",
    "buggy_noop",
)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )


def _schema_output(packet: dict[str, Any]) -> dict[str, Any]:
    level = packet["evidence_level"]
    if level == "E0":
        return _decision(
            "escalate",
            0.5,
            "Issue and patch diff alone are insufficient for a merge decision.",
            ["issue_summary", "patch_diff"],
            ["insufficient_evidence"],
            "unknown",
        )
    if level == "E2":
        static = packet.get("visible_static_evidence") or {}
        if static.get("patch_applies") is False:
            return _decision(
                "reject",
                1.0,
                "Visible static evidence says the patch does not apply.",
                ["visible_static_evidence.patch_applies"],
                ["patch_apply_failed"],
                "non_applicable",
            )
        return _decision(
            "escalate",
            0.65,
            "Patch applies, but static evidence alone does not establish behavioral correctness.",
            ["visible_static_evidence.patch_applies"],
            ["insufficient_evidence"],
            "unknown",
        )
    if level == "E4":
        return _test_based_decision(packet)
    if level == "E6":
        return _tool_summary_decision(packet)
    return _decision(
        "escalate",
        0.0,
        "Unsupported evidence level in schema dry-run.",
        [],
        ["insufficient_evidence"],
        "unknown",
    )


def _test_based_decision(packet: dict[str, Any]) -> dict[str, Any]:
    evidence = packet.get("visible_test_evidence") or {}
    results = evidence.get("test_results") or []
    outcomes = [result.get("outcome") for result in results]
    if any(outcome in {"failed", "error", "timeout"} for outcome in outcomes):
        return _decision(
            "reject",
            1.0,
            "At least one visible test outcome is failed, error, or timeout.",
            ["visible_test_evidence.test_results"],
            ["visible_test_failure"],
            "unknown",
        )
    if outcomes and all(outcome == "passed" for outcome in outcomes):
        return _decision(
            "accept",
            0.9,
            "All visible tests passed and no visible failure was reported.",
            ["visible_test_evidence.test_results"],
            [],
            "none",
        )
    return _decision(
        "escalate",
        0.5,
        "Visible test evidence is missing or ambiguous.",
        ["visible_test_evidence.test_results"],
        ["insufficient_evidence"],
        "unknown",
    )


def _tool_summary_decision(packet: dict[str, Any]) -> dict[str, Any]:
    summary = ((packet.get("visible_tool_evidence") or {}).get("summary") or {})
    counts = summary.get("visible_test_outcome_counts") or {}
    if any(int(counts.get(key, 0)) > 0 for key in ("failed", "error", "timeout")):
        return _decision(
            "reject",
            1.0,
            "Visible tool summary reports failed, error, or timeout test outcomes.",
            ["visible_tool_evidence.summary.visible_test_outcome_counts"],
            ["visible_test_failure"],
            "unknown",
        )
    if int(counts.get("passed", 0)) > 0:
        return _decision(
            "accept",
            0.9,
            "Visible tool summary reports passing visible tests and no visible failures.",
            ["visible_tool_evidence.summary.visible_test_outcome_counts"],
            [],
            "none",
        )
    return _decision(
        "escalate",
        0.5,
        "Visible tool summary is missing decisive behavioral evidence.",
        ["visible_tool_evidence.summary"],
        ["insufficient_evidence"],
        "unknown",
    )


def _decision(
    decision: str,
    confidence: float,
    reason: str,
    evidence_used: list[str],
    risk_flags: list[str],
    suspected_failure_type: str,
) -> dict[str, Any]:
    return {
        "decision": decision,
        "confidence": confidence,
        "primary_reason": reason,
        "evidence_used": evidence_used,
        "risk_flags": risk_flags,
        "suspected_failure_type": suspected_failure_type,
        "human_review_needed": decision == "escalate",
    }


def _parse_schema(raw_response_text: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        parsed = json.loads(raw_response_text)
    except json.JSONDecodeError as exc:
        return None, f"invalid_json:{exc.msg}"
    error = _validate_schema(parsed)
    if error:
        return parsed, error
    return parsed, None


def _validate_schema(parsed: Any) -> str | None:
    if not isinstance(parsed, dict):
        return "schema_not_object"
    missing = [key for key in REQUIRED_SCHEMA_KEYS if key not in parsed]
    if missing:
        return f"missing_keys:{','.join(missing)}"
    if parsed["decision"] not in VALID_DECISIONS:
        return f"invalid_decision:{parsed['decision']}"
    confidence = parsed["confidence"]
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        return "invalid_confidence"
    if not isinstance(parsed["primary_reason"], str) or not parsed["primary_reason"]:
        return "invalid_primary_reason"
    if not isinstance(parsed["evidence_used"], list) or not all(isinstance(item, str) for item in parsed["evidence_used"]):
        return "invalid_evidence_used"
    if not isinstance(parsed["risk_flags"], list) or not all(isinstance(item, str) for item in parsed["risk_flags"]):
        return "invalid_risk_flags"
    if parsed["suspected_failure_type"] not in VALID_FAILURE_TYPES:
        return f"invalid_suspected_failure_type:{parsed['suspected_failure_type']}"
    if not isinstance(parsed["human_review_needed"], bool):
        return "invalid_human_review_needed"
    return None


def build_records(packets_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    packets = _read_jsonl(packets_path)
    records = []
    for packet in packets:
        schema = _schema_output(packet)
        raw_response_text = json.dumps(schema, ensure_ascii=False, sort_keys=True)
        parsed, invalid_reason = _parse_schema(raw_response_text)
        record = {
            "schema_dry_run_id": f"{packet['evidence_packet_id']}__schema_dry_run",
            "evidence_packet_id": packet["evidence_packet_id"],
            "candidate_id": packet["model_visible"]["candidate_id"],
            "cohort_id": packet["cohort_id"],
            "evidence_level": packet["evidence_level"],
            "verifier_id": "merge_gate_schema_dry_run",
            "condition": f"schema_dry_run_{packet['evidence_level']}",
            "dry_run": True,
            "model_call_attempted": False,
            "dry_run_policy": "schema_only_visible_rule",
            "raw_response_text": raw_response_text,
            "parsed_output": parsed,
            "parse_status": "valid" if invalid_reason is None else "invalid",
            "invalid_reason": invalid_reason,
            "cost_usd": 0.0,
        }
        records.append(record)
    summary = _summary(records)
    return records, summary


def _summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    invalid = [record for record in records if record["parse_status"] != "valid"]
    leakage_findings = leakage_audit(records)
    level_counts = _counts(record["evidence_level"] for record in records)
    decision_counts = _counts((record.get("parsed_output") or {}).get("decision", "invalid") for record in records)
    candidate_count = len({record["candidate_id"] for record in records})
    expected_level_counts = {level: candidate_count for level in EVIDENCE_LEVELS}
    expected_record_count = candidate_count * len(EVIDENCE_LEVELS)
    passed = (
        len(records) == expected_record_count
        and not invalid
        and not leakage_findings
        and level_counts == expected_level_counts
    )
    return {
        "cohort_id": "EVP-7",
        "record_count": len(records),
        "expected_record_count": expected_record_count,
        "level_counts": level_counts,
        "decision_counts": decision_counts,
        "valid_parse_count": len(records) - len(invalid),
        "invalid_parse_count": len(invalid),
        "leakage_findings_count": len(leakage_findings),
        "g4_schema_stability": "passed" if passed else "not_passed",
        "dry_run_boundary": "No model API calls; deterministic schema-only outputs generated from model-visible evidence packets.",
        "paper_claim_boundary": "These records validate parser/schema stability only and are not LLM verifier results.",
    }


def _counts(values: Any) -> dict[str, int]:
    result: dict[str, int] = {}
    for value in values:
        key = str(value)
        result[key] = result.get(key, 0) + 1
    return dict(sorted(result.items()))


def leakage_audit(records: list[dict[str, Any]]) -> list[str]:
    serialized = json.dumps(records, ensure_ascii=False)
    return [marker for marker in EVALUATOR_MARKERS if marker in serialized]


def _check(records: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    if summary["g4_schema_stability"] != "passed":
        raise SystemExit(f"G4 schema stability did not pass: {summary}")
    for record in records:
        parsed = record["parsed_output"]
        if parsed is None:
            raise SystemExit(f"missing parsed output: {record['schema_dry_run_id']}")
        error = _validate_schema(parsed)
        if error:
            raise SystemExit(f"invalid parsed schema: {record['schema_dry_run_id']} {error}")
    findings = leakage_audit(records)
    if findings:
        raise SystemExit(f"evaluator marker leaked into schema dry-run records: {findings}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packets-in", type=Path, default=PACKETS_IN)
    parser.add_argument("--reviews-out", type=Path, default=REVIEWS_OUT)
    parser.add_argument("--summary-out", type=Path, default=SUMMARY_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    records, summary = build_records(args.packets_in)
    _write_jsonl(args.reviews_out, records)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check:
        _check(records, summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
