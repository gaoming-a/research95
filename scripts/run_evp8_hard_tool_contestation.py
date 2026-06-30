"""Guarded EVP-8-HARD tool-contestation runner.

The default mode is check-only and does not call model APIs. Real API calls
require an ignored local config, --execute, and a single configured model id.
"""

from __future__ import annotations

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

from cross_review.env import is_placeholder_secret, load_env_file  # noqa: E402
from cross_review.openrouter import DeepSeekClient, QwenClient  # noqa: E402
from cross_review.parsing import extract_json_object, response_text  # noqa: E402

import build_evp8_prompt_manifest as prompt_module  # noqa: E402
import run_evp8_deepseek_qwen_smoke as evp8_core  # noqa: E402
import run_evp8_hard_qwen_deepseek as hard_runner  # noqa: E402


DEFAULT_CONFIG = REPO_ROOT / "configs" / "evp8_hard_tool_contestation.example.json"
DEFAULT_CHECK_SUMMARY_OUT = REPO_ROOT / "data" / "protocols" / "evp8_hard_tool_contestation_check_only_v0_1.json"
DEFAULT_EXEC_SUMMARY_DIR = REPO_ROOT / "data" / "reviews"
DEFAULT_REVIEW_RECORD_DIR = REPO_ROOT / "data" / "reviews"
COHORT_ID = "EVP-8-HARD"
EVIDENCE_LEVEL = "E6"
PACKET_VARIANT = "e6_tool_contestation_no_verdict"
QWEN_MODEL_ID = "qwen/qwen3.7-max"
DEEPSEEK_MODEL_ID = "deepseek/deepseek-v4-pro"
QWEN_SUMMARY = REPO_ROOT / "data" / "reviews" / "evp8_hard_tool_contestation_qwen_qwen3.7-max_full_summary.json"
QWEN_REVIEWS = REPO_ROOT / "data" / "reviews" / "evp8_hard_tool_contestation_qwen_qwen3.7-max_full_reviews.jsonl"
REMOVED_VERDICT_FIELDS = (
    "rule_based_visible_merge_gate_decision",
    "rule_based_visible_merge_gate_reasons",
    "source_decision",
)
RISK_FLAG_VALUES = {
    "patch_apply_failed",
    "visible_test_failure",
    "visible_regression_risk",
    "tool_diagnostic_concern",
    "insufficient_evidence",
    "ambiguous_evidence",
    "test_coverage_concern",
}
COVERAGE_VALUES = {"none", "low", "medium", "high"}
TOOL_RELIABILITY_VALUES = {
    "sufficient_for_accept",
    "insufficient_for_accept",
    "contradicts_accept",
    "no_visible_tool_evidence",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{display_path(path)} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


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


def resolve(path_value: Any) -> Path:
    path = Path(str(path_value))
    return path if path.is_absolute() else REPO_ROOT / path


def display_path(path: Path) -> str:
    absolute = path if path.is_absolute() else REPO_ROOT / path
    try:
        return absolute.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(absolute)


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def env_key_states(env_path: Path, keys: list[str]) -> tuple[dict[str, str], bool]:
    if not env_path.exists():
        return {key: "missing" for key in keys}, False
    states = {key: "missing" for key in keys}
    for line_number, line in enumerate(env_path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            raise ValueError(f"invalid env line at {display_path(env_path)}:{line_number}")
        key, value = stripped.split("=", 1)
        key = key.strip()
        if key in states:
            secret = value.strip().strip("\"'")
            states[key] = "missing_or_placeholder" if is_placeholder_secret(secret) else "set"
    return states, True


def model_config_by_id(config: dict[str, Any], model_id: str | None) -> dict[str, Any] | None:
    if not model_id:
        return None
    for model in config.get("models") or []:
        if model.get("model_id") == model_id:
            return model
    return None


def build_packets(config: dict[str, Any]) -> list[dict[str, Any]]:
    spec = read_json(resolve(config["protocol_spec"]))
    seeds = read_jsonl(resolve(config["model_visible_seed_manifest"]))
    baseline = {
        str(record["candidate_id"]): record
        for record in read_jsonl(resolve(config["tool_only_baseline"]))
    }
    packet_suffix = str((config.get("full") or {}).get("packet_suffix") or "evp8_hard_tool_contestation_full_v0_1")
    packets: list[dict[str, Any]] = []
    for seed in seeds:
        candidate_id = str(seed["candidate_id"])
        baseline_row = baseline[candidate_id]
        packet = {
            "cohort_id": COHORT_ID,
            "protocol_id": spec.get("protocol_id"),
            "evidence_level": EVIDENCE_LEVEL,
            "evidence_level_name": "visible_tool_contestation_no_verdict",
            "anonymous_candidate_id": candidate_id,
            "task_id": seed.get("task_id"),
            "project": seed.get("project"),
            "model_visible_field_groups": [
                "issue_patch_seed",
                "patch_surface_map",
                "patch_application_static_status",
                "visible_fail_to_pass_test_evidence",
                "visible_pass_to_pass_regression_evidence",
                "broader_visible_tool_diagnostics",
                "deterministic_visible_merge_gate_summary",
            ],
            "visible_fields": hard_runner.visible_fields(seed, baseline_row),
        }
        remove_verdict_fields(packet)
        packet["evidence_packet_id"] = f"{candidate_id}__{EVIDENCE_LEVEL}__{packet_suffix}"
        findings = hard_runner.packet_leakage_findings(packet, REMOVED_VERDICT_FIELDS)
        if findings:
            raise ValueError(f"forbidden packet markers for {packet['evidence_packet_id']}: {findings}")
        packets.append(packet)
    return packets


def remove_verdict_fields(packet: dict[str, Any]) -> None:
    summary = ((packet.get("visible_fields") or {}).get("deterministic_visible_merge_gate_summary") or {})
    if isinstance(summary, dict):
        for field in REMOVED_VERDICT_FIELDS:
            summary.pop(field, None)


def verdict_field_check(name: str, packets: list[dict[str, Any]]) -> dict[str, Any]:
    present = name in json.dumps(packets)
    return check(f"{name}_absent", not present, {"present": present})


def schema_sample_output() -> dict[str, Any]:
    return {
        "decision": "escalate",
        "confidence": 0.4,
        "primary_reason": "Visible evidence is too sparse for a safe merge decision.",
        "evidence_used": ["visible_fail_to_pass_test_evidence"],
        "visible_contradictions": ["No visible regression tests were run."],
        "risk_flags": ["insufficient_evidence", "test_coverage_concern"],
        "coverage_concern": "high",
        "visible_tests_sufficient": False,
        "tool_evidence_reliability": "insufficient_for_accept",
        "would_challenge_visible_test_only_accept": True,
        "challenge_reason": "Visible tests are too narrow to justify acceptance.",
        "human_review_needed": True,
    }


def validate_tool_contestation_output(parsed: Any) -> str | None:
    if not isinstance(parsed, dict):
        return "output_not_object"
    required = {
        "decision",
        "confidence",
        "primary_reason",
        "evidence_used",
        "visible_contradictions",
        "risk_flags",
        "coverage_concern",
        "visible_tests_sufficient",
        "tool_evidence_reliability",
        "would_challenge_visible_test_only_accept",
        "challenge_reason",
        "human_review_needed",
    }
    missing = sorted(required - set(parsed))
    if missing:
        return f"missing_required_keys:{','.join(missing)}"
    if parsed.get("decision") not in {"accept", "reject", "escalate"}:
        return "invalid_decision"
    try:
        confidence = float(parsed.get("confidence"))
    except (TypeError, ValueError):
        return "invalid_confidence"
    if confidence < 0.0 or confidence > 1.0:
        return "confidence_out_of_range"
    if not isinstance(parsed.get("primary_reason"), str):
        return "invalid_primary_reason"
    if not isinstance(parsed.get("evidence_used"), list) or not all(isinstance(item, str) for item in parsed["evidence_used"]):
        return "invalid_evidence_used"
    if not isinstance(parsed.get("visible_contradictions"), list) or not all(isinstance(item, str) for item in parsed["visible_contradictions"]):
        return "invalid_visible_contradictions"
    risk_flags = parsed.get("risk_flags")
    if not isinstance(risk_flags, list) or not all(isinstance(item, str) for item in risk_flags):
        return "invalid_risk_flags"
    invalid_risks = sorted(set(risk_flags) - RISK_FLAG_VALUES)
    if invalid_risks:
        return f"invalid_risk_flag_values:{','.join(invalid_risks)}"
    if parsed.get("coverage_concern") not in COVERAGE_VALUES:
        return "invalid_coverage_concern"
    if not isinstance(parsed.get("visible_tests_sufficient"), bool):
        return "invalid_visible_tests_sufficient"
    if parsed.get("tool_evidence_reliability") not in TOOL_RELIABILITY_VALUES:
        return "invalid_tool_evidence_reliability"
    if not isinstance(parsed.get("would_challenge_visible_test_only_accept"), bool):
        return "invalid_would_challenge_visible_test_only_accept"
    if not isinstance(parsed.get("challenge_reason"), str):
        return "invalid_challenge_reason"
    if not isinstance(parsed.get("human_review_needed"), bool):
        return "invalid_human_review_needed"
    if parsed["decision"] == "escalate" and parsed["human_review_needed"] is not True:
        return "escalate_requires_human_review"
    if parsed["decision"] in {"accept", "reject"} and parsed["human_review_needed"] is not False:
        return "supported_decision_requires_no_human_review"
    return None


def check_only(args: argparse.Namespace) -> dict[str, Any]:
    config = read_json(args.config)
    if config.get("packet_variant") != PACKET_VARIANT:
        raise SystemExit(f"unsupported packet_variant: {config.get('packet_variant')}")
    template = resolve(config["prompt_template"]).read_text(encoding="utf-8")
    packets = build_packets(config)
    prompt_hashes: list[str] = []
    prompt_chars: list[int] = []
    boundary_errors: list[str] = []
    packet_leakages: list[str] = []
    for packet in packets:
        prompt = evp8_core.render_prompt(template, packet)
        prompt_hashes.append(evp8_core.sha256_text(prompt))
        prompt_chars.append(len(prompt))
        boundary_errors.extend(prompt_module._boundary_findings(prompt))  # noqa: SLF001
        packet_leakages.extend(hard_runner.packet_leakage_findings(packet, REMOVED_VERDICT_FIELDS))
    schema_error = validate_tool_contestation_output(schema_sample_output())
    model_ids = [str(model.get("model_id")) for model in config.get("models") or []]
    key_names = [str(model.get("api_key_env")) for model in config.get("models") or [] if model.get("api_key_env")]
    key_states, env_exists = env_key_states(resolve(config.get("env", ".env")), key_names)
    credentials_ready = env_exists and all(state == "set" for state in key_states.values())
    full_config = config.get("full") or {}
    candidate_ids = {packet["anonymous_candidate_id"] for packet in packets}
    checks = [
        check("candidate_count", len(candidate_ids) == full_config.get("candidate_count"), len(candidate_ids)),
        check("packet_count", len(packets) == full_config.get("planned_calls_per_model"), len(packets)),
        check("only_e6_packets", {packet["evidence_level"] for packet in packets} == {EVIDENCE_LEVEL}, sorted({packet["evidence_level"] for packet in packets})),
        check("packet_forbidden_marker_count", not packet_leakages, sorted(set(packet_leakages))),
        verdict_field_check("rule_based_visible_merge_gate_decision", packets),
        verdict_field_check("rule_based_visible_merge_gate_reasons", packets),
        verdict_field_check("source_decision", packets),
        check("prompt_boundary_error_count", not boundary_errors, sorted(set(boundary_errors))),
        check("tool_contestation_schema_sample", schema_error is None, schema_error),
        check("credential_key_presence", credentials_ready, {"env_file_exists": env_exists, "key_states": key_states, "values_printed": False}),
        check("api_call_not_attempted", True, False),
        check("raw_outputs_not_generated", True, False),
        check("prompt_text_not_stored", True, False),
    ]
    status = "passed" if all(item["passed"] for item in checks) else "blocked"
    summary = {
        "analysis_id": "evp8_hard_tool_contestation_check_only_v0_1",
        "mode": "check_only",
        "cohort_id": COHORT_ID,
        "config": display_path(args.config),
        "packet_variant": PACKET_VARIANT,
        "removed_verdict_fields": list(REMOVED_VERDICT_FIELDS),
        "planned_model_ids": model_ids,
        "candidate_count": len(candidate_ids),
        "packet_count_per_model": len(packets),
        "model_visible_levels": [EVIDENCE_LEVEL],
        "prompt_count_per_model": len(prompt_hashes),
        "prompt_hashes_unique_count": len(set(prompt_hashes)),
        "prompt_chars_min": min(prompt_chars) if prompt_chars else 0,
        "prompt_chars_max": max(prompt_chars) if prompt_chars else 0,
        "credential_presence_ready": credentials_ready,
        "api_call_attempted": False,
        "raw_outputs_generated": False,
        "prompt_text_stored": False,
        "api_key_values_printed": False,
        "check_only_status": status,
        "checks": checks,
        "next_step": "Run Qwen first with --execute, audit, then run DeepSeek if Qwen coverage passes.",
    }
    write_json(args.summary_out or DEFAULT_CHECK_SUMMARY_OUT, summary)
    if status != "passed":
        raise SystemExit(f"EVP-8-HARD tool-contestation check-only blocked: {status}")
    return summary


def enforce_model_order(config: dict[str, Any], model_id: str) -> None:
    if model_id != DEEPSEEK_MODEL_ID:
        return
    if not QWEN_SUMMARY.exists() or not QWEN_REVIEWS.exists():
        raise SystemExit(
            "Tool-contestation DeepSeek execution requires completed Qwen summary and parsed reviews first."
        )
    summary = read_json(QWEN_SUMMARY)
    reviews = read_jsonl(QWEN_REVIEWS)
    candidate_ids = {str(record.get("anonymous_candidate_id")) for record in reviews}
    checks = {
        "qwen_run_gate": summary.get("run_gate") == "passed",
        "qwen_review_count": summary.get("review_count") == 47 and len(reviews) == 47,
        "qwen_parse_valid_count": summary.get("parse_valid_count") == 47,
        "qwen_unique_candidate_count": len(candidate_ids) == 47,
        "qwen_configured_model_id": summary.get("configured_model_id") == QWEN_MODEL_ID,
        "qwen_packet_variant": summary.get("packet_variant") == PACKET_VARIANT,
        "qwen_parsed_records_valid": all(record.get("parse_status") == "valid" for record in reviews),
    }
    if not all(checks.values()):
        raise SystemExit(f"Tool-contestation DeepSeek execution blocked by Qwen precondition: {checks}")


def output_prefix(model_id: str) -> str:
    return f"evp8_hard_tool_contestation_{evp8_core.safe_name(model_id)}_full"


def execute(args: argparse.Namespace) -> dict[str, Any]:
    if args.config.name.endswith(".example.json"):
        raise SystemExit("Refusing to execute with tracked example config. Use ignored local config.")
    config = read_json(args.config)
    if config.get("packet_variant") != PACKET_VARIANT:
        raise SystemExit(f"unsupported packet_variant: {config.get('packet_variant')}")
    model_config = model_config_by_id(config, args.model_id)
    if model_config is None:
        raise SystemExit(f"--model-id must match one configured model: {args.model_id}")
    enforce_model_order(config, str(model_config["model_id"]))
    load_env_file(str(resolve(config.get("env", ".env"))))
    template = resolve(config["prompt_template"]).read_text(encoding="utf-8")
    packets = build_packets(config)
    output_dir = resolve((config.get("full") or {})["output_dir"]) / evp8_core.safe_name(str(model_config["model_id"]))
    raw_out = args.raw_out or output_dir / "raw_responses.jsonl"
    prefix = output_prefix(str(model_config["model_id"]))
    summary_out = args.summary_out or DEFAULT_EXEC_SUMMARY_DIR / f"{prefix}_summary.json"
    parsed_reviews_out = args.parsed_reviews_out or DEFAULT_REVIEW_RECORD_DIR / f"{prefix}_reviews.jsonl"
    if config.get("overwrite_policy") == "refuse_if_output_exists":
        for path in (summary_out, raw_out, parsed_reviews_out):
            if path.exists():
                raise SystemExit(f"Refusing to overwrite output: {display_path(path)}")
    client = client_for(str(model_config["provider_route"]))
    parsed_records: list[dict[str, Any]] = []
    raw_out.parent.mkdir(parents=True, exist_ok=True)
    with raw_out.open("x", encoding="utf-8") as raw_handle:
        for packet in packets:
            prompt = evp8_core.render_prompt(template, packet)
            findings = prompt_module._boundary_findings(prompt)  # noqa: SLF001
            if findings:
                raise RuntimeError(f"prompt boundary failed for {packet['evidence_packet_id']}: {findings}")
            response = client.chat_completion(
                model=str(model_config["request_model_id"]),
                prompt=prompt,
                temperature=float(config.get("temperature", 0.0)),
                max_tokens=int(config.get("max_output_tokens", 4096)),
                thinking=model_config.get("thinking"),
                response_format=model_config.get("response_format"),
            )
            raw_record = {
                "evidence_packet_id": packet["evidence_packet_id"],
                "anonymous_candidate_id": packet["anonymous_candidate_id"],
                "evidence_level": packet["evidence_level"],
                "requested_model_id": model_config["request_model_id"],
                "configured_model_id": model_config["model_id"],
                "actual_model_id": response.get("model"),
                "provider_route": model_config["provider_route"],
                "request_response_format": model_config.get("response_format"),
                "request_thinking": model_config.get("thinking"),
                "raw_response_text": response_text(response),
                "response": response,
                "run_date_utc": datetime.now(timezone.utc).isoformat(),
            }
            append_jsonl_record(raw_handle, raw_record)
            parsed_records.append(parsed_record_from_raw(raw_record, model_config))
    cost = evp8_core.aggregate_cost(parsed_records)
    parse_valid_count = sum(1 for record in parsed_records if record["parse_status"] == "valid")
    write_jsonl(parsed_reviews_out, parsed_records)
    summary = {
        "analysis_id": "evp8_hard_tool_contestation_full_summary_v0_1",
        "mode": "executed",
        "cohort_id": COHORT_ID,
        "packet_variant": PACKET_VARIANT,
        "removed_verdict_fields": list(REMOVED_VERDICT_FIELDS),
        "configured_model_id": model_config["model_id"],
        "request_model_id": model_config["request_model_id"],
        "provider_route": model_config["provider_route"],
        "raw_responses_out": display_path(raw_out),
        "parsed_reviews_out": display_path(parsed_reviews_out),
        "raw_response_text_stored_in_tracked_summary": False,
        "raw_response_text_stored_in_parsed_reviews": False,
        "review_count": len(parsed_records),
        "parse_valid_count": parse_valid_count,
        "invalid_parse_count": len(parsed_records) - parse_valid_count,
        "decision_counts": evp8_core._counts(record["decision"] for record in parsed_records),  # noqa: SLF001
        "coverage_concern_counts": evp8_core._counts(record.get("coverage_concern") for record in parsed_records),  # noqa: SLF001
        "tool_evidence_reliability_counts": evp8_core._counts(record.get("tool_evidence_reliability") for record in parsed_records),  # noqa: SLF001
        "challenge_visible_test_only_accept_counts": evp8_core._counts(record.get("would_challenge_visible_test_only_accept") for record in parsed_records),  # noqa: SLF001
        "api_call_attempted": True,
        "raw_outputs_generated": True,
        "prompt_text_stored": False,
        "cost_summary": cost,
        "usage_cost_gate": "passed" if cost["unknown_cost_record_count"] == 0 else "blocked",
        "run_gate": "passed" if parse_valid_count == len(parsed_records) and cost["unknown_cost_record_count"] == 0 else "blocked",
    }
    write_json(summary_out, summary)
    if summary["run_gate"] != "passed":
        raise SystemExit(f"EVP-8-HARD tool-contestation run gate blocked: {summary['run_gate']}")
    return summary


def parsed_record_from_raw(raw_record: dict[str, Any], model_config: dict[str, Any]) -> dict[str, Any]:
    response = raw_record.get("response") if isinstance(raw_record.get("response"), dict) else {}
    raw_text = str(raw_record.get("raw_response_text") or "")
    try:
        parsed = extract_json_object(raw_text)
        invalid_reason = validate_tool_contestation_output(parsed)
    except Exception as exc:  # noqa: BLE001
        parsed = {}
        invalid_reason = f"invalid_json:{exc}"
    cost = evp8_core.cost_summary(response=response, model_config=model_config)
    return {
        "evidence_packet_id": raw_record["evidence_packet_id"],
        "anonymous_candidate_id": raw_record["anonymous_candidate_id"],
        "evidence_level": raw_record["evidence_level"],
        "parse_status": "valid" if invalid_reason is None else "invalid",
        "invalid_reason": invalid_reason,
        "decision": parsed.get("decision"),
        "risk_flags": parsed.get("risk_flags") or [],
        "human_review_needed": parsed.get("human_review_needed"),
        "confidence": parsed.get("confidence"),
        "primary_reason": parsed.get("primary_reason"),
        "evidence_used": parsed.get("evidence_used") or [],
        "visible_contradictions": parsed.get("visible_contradictions") or [],
        "coverage_concern": parsed.get("coverage_concern"),
        "visible_tests_sufficient": parsed.get("visible_tests_sufficient"),
        "tool_evidence_reliability": parsed.get("tool_evidence_reliability"),
        "would_challenge_visible_test_only_accept": parsed.get("would_challenge_visible_test_only_accept"),
        "challenge_reason": parsed.get("challenge_reason"),
        "request_model_id": model_config["request_model_id"],
        "configured_model_id": model_config["model_id"],
        "actual_model_id": raw_record.get("actual_model_id") or response.get("model"),
        "provider_route": model_config["provider_route"],
        "usage": cost["usage"],
        "cost_usd": cost.get("cost_usd"),
        "cost_cny": cost.get("cost_cny"),
        "cost_currency": cost.get("cost_currency"),
        "cost_source": cost["cost_source"],
        "cost_observability": cost["cost_observability"],
    }


def client_for(provider_route: str) -> DeepSeekClient | QwenClient:
    if provider_route == "deepseek_official":
        return DeepSeekClient()
    if provider_route == "qwen_official":
        return QwenClient()
    raise SystemExit(f"unsupported provider route: {provider_route}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--model-id")
    parser.add_argument("--summary-out", type=Path)
    parser.add_argument("--raw-out", type=Path)
    parser.add_argument("--parsed-reviews-out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    modes = sum(bool(value) for value in (args.check_only, args.execute))
    if modes != 1:
        raise SystemExit("Choose exactly one mode: --check-only or --execute.")
    if args.execute and not args.model_id:
        raise SystemExit("--execute requires --model-id.")
    summary = execute(args) if args.execute else check_only(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
