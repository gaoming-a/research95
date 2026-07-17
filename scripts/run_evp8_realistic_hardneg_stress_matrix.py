# ruff: noqa: E402
"""Run the ready EVP-8 hard-negative stress verifier matrix.

Raw provider responses are written only under ignored outputs. Tracked review
files contain normalized decisions and cost metadata, never rendered prompts,
patch diffs, raw response text, or credentials.
"""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/run_evp8_realistic_hardneg_stress_matrix.py")

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_evp8_realistic_hardneg_stress_matrix_preflight as preflight_module  # noqa: E402
import run_evp8_deepseek_qwen_smoke as evp8_core  # noqa: E402
from check_evp8_coverage_contestation_current98 import validate_output as validate_coverage_output  # noqa: E402
from cross_review.env import load_env_file  # noqa: E402
from cross_review.parsing import extract_json_object  # noqa: E402


DEFAULT_PRELIGHT = (
    REPO_ROOT
    / "data"
    / "protocols"
    / "evp8_realistic_hardneg_stress_matrix_preflight_v0_1.json"
)
DEFAULT_RAW_ROOT = REPO_ROOT / "outputs" / "evp8_realistic_hardneg_stress_matrix_v0_1"
DEFAULT_REVIEW_ROOT = REPO_ROOT / "data" / "reviews"
CONDITION_PROMPTS = {
    "current_merge_gate": REPO_ROOT / "prompts" / "evp8_visible_evidence_merge_gate_v0_2.md",
    "coverage_contestation": REPO_ROOT / "prompts" / "evp8_coverage_contestation_merge_gate_v0_1.md",
}
BASE_SCHEMA = {
    "required_keys": [
        "decision",
        "confidence",
        "primary_reason",
        "evidence_used",
        "visible_contradictions",
        "risk_flags",
        "human_review_needed",
    ],
    "decision_values": ["accept", "reject", "escalate"],
    "risk_flag_values": [
        "patch_apply_failed",
        "visible_test_failure",
        "visible_regression_risk",
        "tool_diagnostic_concern",
        "insufficient_evidence",
        "ambiguous_evidence",
    ],
    "forbidden_output_keys": [],
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{preflight_module.display_path(path)} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{preflight_module.display_path(path)}:{line_number} must contain a JSON object")
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


def append_jsonl_record(handle: Any, record: dict[str, Any]) -> None:
    handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    handle.flush()


def model_config(preflight: dict[str, Any], model_id: str) -> dict[str, Any]:
    for model in preflight.get("models") or []:
        if model.get("model_id") == model_id:
            result = dict(model)
            if model_id == "qwen/qwen3.7-max":
                result["api_key_env"] = "QWEN_API_KEY"
                result["response_format"] = {"type": "json_object"}
            elif model_id == "deepseek/deepseek-v4-pro":
                result["api_key_env"] = "DEEPSEEK_API_KEY"
                result["response_format"] = {"type": "json_object"}
                result["thinking"] = {"type": "disabled"}
            elif model_id == "google/gemini-2.5-flash":
                result["api_key_env"] = "OPENROUTER_API_KEY"
                result["provider_preferences"] = {
                    "allow_fallbacks": False,
                    "require_parameters": True,
                }
            return result
    raise SystemExit(f"--model-id must be one of the preflight models: {model_id}")


def ready_conditions(preflight: dict[str, Any]) -> list[str]:
    return [str(condition) for condition in preflight.get("prompt_conditions_ready") or []]


def build_packets(condition_id: str) -> list[dict[str, Any]]:
    if condition_id not in CONDITION_PROMPTS:
        raise SystemExit(f"unsupported or blocked condition for execution: {condition_id}")
    source_packets = read_jsonl(preflight_module.PACKETS_IN)
    packets: list[dict[str, Any]] = []
    for packet in source_packets:
        transformed, _ = preflight_module.condition_packet(condition_id, packet)
        transformed["evidence_packet_id"] = (
            f"{packet['candidate_id']}__{condition_id}__hardneg_stress_v0_1"
        )
        transformed["anonymous_candidate_id"] = packet["candidate_id"]
        transformed["evidence_level"] = "HARDNEG_STRESS_VISIBLE_PASS"
        transformed["evidence_level_name"] = condition_id
        transformed["condition_id"] = condition_id
        packets.append(transformed)
    return packets


def validate_parsed(condition_id: str, parsed: Any) -> str | None:
    if condition_id == "coverage_contestation":
        return validate_coverage_output(parsed)
    return evp8_core.validate_output_schema(parsed, BASE_SCHEMA)


def parsed_from_raw(raw_record: dict[str, Any], model: dict[str, Any], condition_id: str) -> dict[str, Any]:
    response = raw_record.get("response") if isinstance(raw_record.get("response"), dict) else {}
    raw_text = str(raw_record.get("raw_response_text") or "")
    parsed: dict[str, Any] | None
    invalid_reason: str | None
    try:
        parsed = extract_json_object(raw_text)
        invalid_reason = validate_parsed(condition_id, parsed)
    except Exception as exc:  # noqa: BLE001
        parsed = None
        invalid_reason = f"invalid_json:{exc}"
    cost = evp8_core.cost_summary(response=response, model_config=model)
    return {
        "analysis_id": "evp8_realistic_hardneg_stress_matrix_v0_1",
        "condition_id": condition_id,
        "evidence_packet_id": raw_record["evidence_packet_id"],
        "anonymous_candidate_id": raw_record["anonymous_candidate_id"],
        "parse_status": "valid" if invalid_reason is None else "invalid",
        "invalid_reason": invalid_reason,
        "decision": parsed.get("decision") if parsed else None,
        "confidence": parsed.get("confidence") if parsed else None,
        "risk_flags": parsed.get("risk_flags") if parsed else [],
        "coverage_concern": parsed.get("coverage_concern") if parsed else None,
        "visible_tests_sufficient": parsed.get("visible_tests_sufficient") if parsed else None,
        "tool_evidence_reliability": parsed.get("tool_evidence_reliability") if parsed else None,
        "would_challenge_visible_test_only_accept": (
            parsed.get("would_challenge_visible_test_only_accept") if parsed else None
        ),
        "human_review_needed": parsed.get("human_review_needed") if parsed else None,
        "request_model_id": model["request_model_id"],
        "configured_model_id": model["model_id"],
        "actual_model_id": raw_record.get("actual_model_id") or response.get("model"),
        "provider_route": model["provider_route"],
        "usage": cost["usage"],
        "cost_usd": cost.get("cost_usd"),
        "cost_cny": cost.get("cost_cny"),
        "cost_currency": cost.get("cost_currency"),
        "cost_source": cost["cost_source"],
        "cost_observability": cost["cost_observability"],
        "raw_response_text_stored": False,
        "rendered_prompt_text_stored": False,
        "patch_text_stored": False,
    }


def load_resume_state(
    *,
    raw_out: Path,
    packets: list[dict[str, Any]],
    model: dict[str, Any],
    condition_id: str,
    resume: bool,
) -> tuple[set[str], list[dict[str, Any]]]:
    if not raw_out.exists() or not resume:
        return set(), []
    raw_records = read_jsonl(raw_out)
    expected_ids = [str(packet["evidence_packet_id"]) for packet in packets]
    existing_ids = [str(record.get("evidence_packet_id")) for record in raw_records]
    if existing_ids != expected_ids[: len(existing_ids)]:
        raise SystemExit(
            f"Cannot resume {preflight_module.display_path(raw_out)}: raw records are not a planned prefix."
        )
    completed: set[str] = set()
    parsed_records: list[dict[str, Any]] = []
    packet_by_id = {str(packet["evidence_packet_id"]): packet for packet in packets}
    for raw_record in raw_records:
        packet_id = str(raw_record["evidence_packet_id"])
        packet = packet_by_id[packet_id]
        if raw_record.get("configured_model_id") != model["model_id"]:
            raise SystemExit(f"Cannot resume {preflight_module.display_path(raw_out)}: model mismatch.")
        if raw_record.get("provider_route") != model["provider_route"]:
            raise SystemExit(f"Cannot resume {preflight_module.display_path(raw_out)}: provider mismatch.")
        if raw_record.get("anonymous_candidate_id") != packet["anonymous_candidate_id"]:
            raise SystemExit(f"Cannot resume {preflight_module.display_path(raw_out)}: candidate mismatch.")
        completed.add(packet_id)
        parsed_records.append(parsed_from_raw(raw_record, model, condition_id))
    return completed, parsed_records


def retry_invalid_raw_records(
    *,
    raw_out: Path,
    packets: list[dict[str, Any]],
    model: dict[str, Any],
    condition_id: str,
    template: str,
    config: dict[str, Any],
) -> int:
    if not raw_out.exists():
        return 0
    raw_records = read_jsonl(raw_out)
    expected_ids = [str(packet["evidence_packet_id"]) for packet in packets]
    existing_ids = [str(record.get("evidence_packet_id")) for record in raw_records]
    if existing_ids != expected_ids[: len(existing_ids)]:
        raise SystemExit(
            f"Cannot retry invalid records in {preflight_module.display_path(raw_out)}: "
            "raw records are not a planned prefix."
        )
    packet_by_id = {str(packet["evidence_packet_id"]): packet for packet in packets}
    updated_records: list[dict[str, Any]] = []
    retry_count = 0
    for raw_record in raw_records:
        parsed = parsed_from_raw(raw_record, model, condition_id)
        if parsed["parse_status"] == "valid":
            updated_records.append(raw_record)
            continue
        packet = packet_by_id[str(raw_record["evidence_packet_id"])]
        replacement = evp8_core.fetch_raw_record(packet, template, config, model)
        replacement["condition_id"] = condition_id
        replacement["retry_of_invalid_raw_record"] = True
        replacement["previous_invalid_reason"] = parsed["invalid_reason"]
        updated_records.append(replacement)
        retry_count += 1
    if retry_count:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = raw_out.with_name(f"{raw_out.stem}.before_invalid_retry_{stamp}{raw_out.suffix}")
        backup.write_text(
            "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in raw_records),
            encoding="utf-8",
        )
        raw_out.write_text(
            "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in updated_records),
            encoding="utf-8",
        )
    return retry_count


def default_paths(model_id: str, condition_id: str) -> tuple[Path, Path, Path]:
    safe_model = evp8_core.safe_name(model_id)
    raw_out = DEFAULT_RAW_ROOT / condition_id / safe_model / "raw_responses.jsonl"
    reviews_out = DEFAULT_REVIEW_ROOT / (
        f"evp8_realistic_hardneg_stress_matrix_{condition_id}_{safe_model}_reviews.jsonl"
    )
    summary_out = DEFAULT_REVIEW_ROOT / (
        f"evp8_realistic_hardneg_stress_matrix_{condition_id}_{safe_model}_summary.json"
    )
    return raw_out, reviews_out, summary_out


def run_gate_summary(
    *,
    records: list[dict[str, Any]],
    condition_id: str,
    model: dict[str, Any],
    raw_out: Path,
    reviews_out: Path,
    resumed_count: int,
    args: argparse.Namespace,
) -> dict[str, Any]:
    cost = evp8_core.aggregate_cost(records)
    parse_valid_count = sum(1 for row in records if row["parse_status"] == "valid")
    return {
        "analysis_id": "evp8_realistic_hardneg_stress_matrix_v0_1",
        "mode": "executed",
        "cohort_id": "EVP-8-REALISTIC-HARDNEG-STRESS",
        "condition_id": condition_id,
        "configured_model_id": model["model_id"],
        "request_model_id": model["request_model_id"],
        "provider_route": model["provider_route"],
        "provider_preferences": model.get("provider_preferences"),
        "request_response_format": model.get("response_format"),
        "request_thinking": model.get("thinking"),
        "max_output_tokens": args.max_output_tokens,
        "raw_responses_out": preflight_module.display_path(raw_out),
        "tracked_reviews_out": preflight_module.display_path(reviews_out),
        "api_call_attempted": True,
        "raw_outputs_generated": True,
        "raw_response_text_stored_in_tracked_reviews": False,
        "rendered_prompt_text_stored": False,
        "patch_text_stored_in_tracked_reviews": False,
        "review_count": len(records),
        "new_api_call_count": len(records) - resumed_count,
        "resume_enabled": bool(args.resume),
        "resumed_raw_record_count": resumed_count,
        "parse_valid_count": parse_valid_count,
        "invalid_parse_count": len(records) - parse_valid_count,
        "decision_counts": evp8_core._counts(row["decision"] for row in records),
        "coverage_concern_counts": evp8_core._counts(row["coverage_concern"] for row in records),
        "challenge_visible_test_only_accept_counts": evp8_core._counts(
            row["would_challenge_visible_test_only_accept"] for row in records
        ),
        "actual_model_id_counts": evp8_core._counts(row["actual_model_id"] or "missing" for row in records),
        "cost_summary": cost,
        "usage_cost_gate": "passed" if cost["unknown_cost_record_count"] == 0 else "blocked",
        "run_gate": (
            "passed"
            if parse_valid_count == len(records) and cost["unknown_cost_record_count"] == 0
            else "blocked"
        ),
    }


def execute(args: argparse.Namespace) -> dict[str, Any]:
    if not args.execute_authorized:
        raise SystemExit("--execute-authorized is required for API execution.")
    preflight = read_json(args.preflight)
    if preflight.get("status") not in {"passed", "passed_with_no_verdict_blocked"}:
        raise SystemExit(f"preflight status is not executable: {preflight.get('status')}")
    if args.condition_id not in ready_conditions(preflight):
        raise SystemExit(f"condition is not ready in preflight: {args.condition_id}")
    if args.condition_id not in CONDITION_PROMPTS:
        raise SystemExit(f"condition has no runner prompt mapping: {args.condition_id}")
    model = model_config(preflight, args.model_id)
    load_env_file(str(args.env))
    template = CONDITION_PROMPTS[args.condition_id].read_text(encoding="utf-8")
    packets = build_packets(args.condition_id)
    raw_out, reviews_out, summary_out = default_paths(args.model_id, args.condition_id)
    if raw_out.exists() and not args.resume:
        raise SystemExit(f"Refusing to overwrite raw output: {preflight_module.display_path(raw_out)}. Use --resume.")
    if summary_out.exists() and not args.resume:
        raise SystemExit(
            f"Refusing to overwrite tracked summary: {preflight_module.display_path(summary_out)}. Use --resume."
        )
    config = {
        "temperature": args.temperature,
        "max_output_tokens": args.max_output_tokens,
        "openrouter_metadata_header": "enabled",
    }
    invalid_retry_count = 0
    if args.retry_invalid:
        if not args.resume:
            raise SystemExit("--retry-invalid requires --resume.")
        invalid_retry_count = retry_invalid_raw_records(
            raw_out=raw_out,
            packets=packets,
            model=model,
            condition_id=args.condition_id,
            template=template,
            config=config,
        )
    completed_ids, records = load_resume_state(
        raw_out=raw_out,
        packets=packets,
        model=model,
        condition_id=args.condition_id,
        resume=args.resume,
    )
    resumed_count = len(completed_ids)
    raw_out.parent.mkdir(parents=True, exist_ok=True)
    raw_mode = "a" if args.resume and raw_out.exists() else "x"
    with raw_out.open(raw_mode, encoding="utf-8") as raw_handle:
        for packet in packets:
            if packet["evidence_packet_id"] in completed_ids:
                continue
            raw_record = evp8_core.fetch_raw_record(packet, template, config, model)
            raw_record["condition_id"] = args.condition_id
            append_jsonl_record(raw_handle, raw_record)
            records.append(parsed_from_raw(raw_record, model, args.condition_id))
    write_jsonl(reviews_out, records)
    summary = run_gate_summary(
        records=records,
        condition_id=args.condition_id,
        model=model,
        raw_out=raw_out,
        reviews_out=reviews_out,
        resumed_count=resumed_count,
        args=args,
    )
    summary["invalid_raw_retry_count"] = invalid_retry_count
    write_json(summary_out, summary)
    if summary["run_gate"] != "passed":
        raise SystemExit(f"stress matrix run gate blocked: {summary['run_gate']}")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight", type=Path, default=DEFAULT_PRELIGHT)
    parser.add_argument("--condition-id", required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--env", type=Path, default=REPO_ROOT / ".env")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-output-tokens", type=int, default=4096)
    parser.add_argument("--execute-authorized", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--retry-invalid", action="store_true")
    return parser.parse_args()


def main() -> int:
    summary = execute(parse_args())
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
