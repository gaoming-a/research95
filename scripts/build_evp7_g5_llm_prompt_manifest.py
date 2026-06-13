"""Build the EVP-7 G5 LLM prompt manifest without calling model APIs.

The manifest records prompt hashes, lengths, prompt version, and leakage checks
for the future evidence-visibility merge-gate run. It intentionally does not
store full prompt text and does not read credentials or local API configs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKETS_IN = REPO_ROOT / "data" / "evidence" / "evp7_evidence_packets.jsonl"
PROMPT_MANIFEST_OUT = REPO_ROOT / "data" / "reviews" / "evp7_g5_llm_prompt_manifest.jsonl"
READINESS_OUT = REPO_ROOT / "data" / "reviews" / "evp7_g5_llm_run_readiness.json"

PROMPT_ID = "patch_verify_evidence_visibility_merge_gate_v1"
DEFAULT_MODEL_PLACEHOLDER = "user_confirmed_model_required"
DEFAULT_API_PROVIDER_PLACEHOLDER = "user_confirmed_provider_required"
DEFAULT_TEMPERATURE = 0.0
DEFAULT_MAX_TOKENS = 1024
EVIDENCE_LEVELS = ("E0", "E2", "E4", "E6")

FORBIDDEN_BOUNDARY_MARKERS = (
    "label_with_p2p_broad",
    "label_retained_oracle",
    "candidate_type",
    "expected_outcome",
    "failure_type_label",
    "patch_id",
    "patch_materialization",
    "patch_source_label",
    "source_model_candidate_id",
    "validation_summary",
    "hidden_oracles",
    "oracle_command",
    "oracle_workdir",
    "correct_under_f2p_and_p2p_broad",
    "incorrect_issue_not_fixed",
    "correct_reference",
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


def _visible_payload(packet: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "evidence_packet_id": packet["evidence_packet_id"],
        "cohort_id": packet["cohort_id"],
        "evidence_level": packet["evidence_level"],
        "evidence_level_name": packet["evidence_level_name"],
        "model_visible": packet["model_visible"],
        "packet_completeness": packet["packet_completeness"],
    }
    for key in ("visible_static_evidence", "visible_test_evidence", "visible_tool_evidence"):
        if key in packet:
            payload[key] = packet[key]
    return payload


def render_prompt(packet: dict[str, Any]) -> str:
    payload = _visible_payload(packet)
    return "\n".join(
        [
            "You are a software merge-gate verifier for candidate patches.",
            "",
            "Use only the visible evidence packet below. Do not infer hidden labels, hidden tests, oracle outcomes, reference-patch provenance, or evaluator notes.",
            "Decide whether the candidate patch should be accepted, rejected, or escalated for human or tool review.",
            "",
            "Return exactly one JSON object with this schema:",
            "{",
            '  "decision": "accept | reject | escalate",',
            '  "confidence": 0.0,',
            '  "primary_reason": "one concise reason grounded in visible evidence",',
            '  "evidence_used": ["names of visible evidence fields used"],',
            '  "risk_flags": ["partial_fix | under_fix | regression_risk | test_overfitting | insufficient_evidence"],',
            '  "suspected_failure_type": "none | partial_fix | under_fix | regression | irrelevant | non_applicable | unknown",',
            '  "human_review_needed": true',
            "}",
            "",
            "Decision policy:",
            "- Accept only when visible evidence directly supports the patch and no visible contradiction remains.",
            "- Reject when visible evidence contradicts the required behavior, the patch does not apply, visible tests fail/error/timeout, or the patch visibly fails to address the issue.",
            "- Escalate when visible evidence is incomplete, ambiguous, or insufficient for a safe merge decision.",
            "- If the evidence level is sparse, prefer escalation over unsupported acceptance.",
            "",
            "Visible evidence packet:",
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        ]
    )


def boundary_findings(prompt: str) -> list[str]:
    return [marker for marker in FORBIDDEN_BOUNDARY_MARKERS if marker in prompt]


def build_manifest(packets_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    packets = _read_jsonl(packets_path)
    records = []
    for packet in packets:
        prompt = render_prompt(packet)
        findings = boundary_findings(prompt)
        records.append(
            {
                "prompt_manifest_id": f"{packet['evidence_packet_id']}__{PROMPT_ID}",
                "evidence_packet_id": packet["evidence_packet_id"],
                "candidate_id": packet["model_visible"]["candidate_id"],
                "cohort_id": packet["cohort_id"],
                "evidence_level": packet["evidence_level"],
                "prompt_id": PROMPT_ID,
                "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                "prompt_chars": len(prompt),
                "prompt_text_stored": False,
                "label_leakage_check": "passed" if not findings else "failed",
                "boundary_findings": findings,
            }
        )
    return records, _summary(records)


def _summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    char_lengths = [record["prompt_chars"] for record in records]
    leakage_count = sum(1 for record in records if record["label_leakage_check"] != "passed")
    level_counts = _counts(record["evidence_level"] for record in records)
    prompt_count = len(records)
    expected_level_count = prompt_count // len(EVIDENCE_LEVELS) if records else 0
    expected_level_counts = {level: expected_level_count for level in EVIDENCE_LEVELS}
    expected_prompt_count = expected_level_count * len(EVIDENCE_LEVELS)
    estimated_prompt_tokens = round(sum(char_lengths) / 4) if char_lengths else 0
    readiness_passed = prompt_count == expected_prompt_count and level_counts == expected_level_counts and leakage_count == 0
    return {
        "cohort_id": "EVP-7",
        "prompt_id": PROMPT_ID,
        "prompt_record_count": prompt_count,
        "expected_prompt_record_count": expected_prompt_count,
        "level_counts": level_counts,
        "prompt_char_min": min(char_lengths) if char_lengths else None,
        "prompt_char_max": max(char_lengths) if char_lengths else None,
        "prompt_char_total": sum(char_lengths),
        "estimated_prompt_tokens_char_div_4": estimated_prompt_tokens,
        "label_leakage_failed_count": leakage_count,
        "prompt_text_stored": False,
        "default_api_provider": DEFAULT_API_PROVIDER_PLACEHOLDER,
        "default_model": DEFAULT_MODEL_PLACEHOLDER,
        "default_temperature": DEFAULT_TEMPERATURE,
        "default_max_tokens": DEFAULT_MAX_TOKENS,
        "planned_output_records": expected_prompt_count,
        "planned_conditions": ["evidence_visibility_merge_gate"],
        "planned_evidence_levels": list(EVIDENCE_LEVELS),
        "stop_conditions": [
            "any prompt boundary/leakage check fails",
            "invalid output rate exceeds 0.2 in an initial smoke slice",
            "API authentication/model/preflight fails",
            "unexpected cost growth exceeds user-confirmed budget",
            "run_error.json is produced",
        ],
        "requires_user_confirmation": [
            "api_provider",
            "model",
            "max_total_cost_usd",
            "smoke_scope",
            "full_run_permission",
        ],
        "g5_llm_run_readiness": "passed_without_api" if readiness_passed else "not_passed",
        "api_call_attempted": False,
        "claim_boundary": "This readiness artifact prepares a future LLM G5 run; it is not model-result evidence.",
    }


def _counts(values: Any) -> dict[str, int]:
    result: dict[str, int] = {}
    for value in values:
        key = str(value)
        result[key] = result.get(key, 0) + 1
    return dict(sorted(result.items()))


def _check(records: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    if summary["g5_llm_run_readiness"] != "passed_without_api":
        raise SystemExit(f"G5 LLM run readiness did not pass: {summary}")
    for record in records:
        if record["boundary_findings"]:
            raise SystemExit(f"prompt boundary failed: {record['prompt_manifest_id']} {record['boundary_findings']}")
    if len({record["prompt_sha256"] for record in records}) != len(records):
        raise SystemExit("prompt hashes are not unique across evidence packets")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packets-in", type=Path, default=PACKETS_IN)
    parser.add_argument("--prompt-manifest-out", type=Path, default=PROMPT_MANIFEST_OUT)
    parser.add_argument("--readiness-out", type=Path, default=READINESS_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    records, summary = build_manifest(args.packets_in)
    _write_jsonl(args.prompt_manifest_out, records)
    args.readiness_out.parent.mkdir(parents=True, exist_ok=True)
    args.readiness_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check:
        _check(records, summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
