"""Guarded Qwen verifier runner for the EVP-8 realistic agent-patch cohort."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
SCRIPT_ROOT = REPO_ROOT / "scripts"
for path in (SRC_ROOT, SCRIPT_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from cross_review.env import is_placeholder_secret, load_env_file  # noqa: E402
from cross_review.openrouter import QwenClient  # noqa: E402
from cross_review.parsing import extract_json_object, response_text  # noqa: E402

import build_evp8_prompt_manifest as prompt_module  # noqa: E402
import run_evp8_deepseek_qwen_smoke as evp8_core  # noqa: E402


COHORT_ID = "EVP-8-REALISTIC-AGENT"
EVIDENCE_LEVEL = "E6"
DEFAULT_CONFIG = REPO_ROOT / "configs" / "evp8_realistic_agent_qwen.example.json"
DEFAULT_CHECK_SUMMARY_OUT = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_qwen_check_only_v0_1.json"
DEFAULT_EXEC_SUMMARY_DIR = REPO_ROOT / "data" / "reviews"
DEFAULT_REVIEW_RECORD_DIR = REPO_ROOT / "data" / "reviews"
DEFAULT_PACKET_VARIANT = "e6_full_with_verdict"
NO_VERDICT_PACKET_VARIANT = "e6_no_verdict"
REMOVED_VERDICT_FIELDS = (
    "rule_based_visible_merge_gate_decision",
    "rule_based_visible_merge_gate_reasons",
    "source_decision",
)
FORBIDDEN_PACKET_MARKERS = evp8_core.FORBIDDEN_MARKERS + (
    "expected_outcome",
    "hidden_oracles",
    "oracle_passed",
    "oracle_result",
    "oracle_ran",
    "candidate_type",
    "source_patch_id",
    "source_model_candidate_id",
    "model_candidate_id",
    "validation_status",
    "normalized_label",
    "raw_generation_response",
    "generation_rationale",
)


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


def safe_model_name(model_id: str) -> str:
    return evp8_core.safe_name(model_id)


def packet_variant(config: dict[str, Any]) -> str:
    return str(config.get("packet_variant") or DEFAULT_PACKET_VARIANT)


def variant_removed_fields(config: dict[str, Any]) -> tuple[str, ...]:
    variant = packet_variant(config)
    if variant == DEFAULT_PACKET_VARIANT:
        return ()
    if variant == NO_VERDICT_PACKET_VARIANT:
        return REMOVED_VERDICT_FIELDS
    raise ValueError(f"unsupported packet_variant: {variant}")


def output_prefix(config: dict[str, Any], model_id: str) -> str:
    suffix = "no_verdict" if packet_variant(config) == NO_VERDICT_PACKET_VARIANT else "full"
    return f"evp8_realistic_agent_qwen_{safe_model_name(model_id)}_{suffix}"


def model_config_by_id(config: dict[str, Any], model_id: str | None) -> dict[str, Any] | None:
    if not model_id:
        return None
    for model in config.get("models") or []:
        if model.get("model_id") == model_id:
            return model
    return None


def packet_leakage_findings(value: Any) -> list[str]:
    serialized = json.dumps(value, ensure_ascii=False).lower()
    return sorted({marker for marker in FORBIDDEN_PACKET_MARKERS if marker.lower() in serialized})


def remove_verdict_fields(packet: dict[str, Any], removed_fields: tuple[str, ...]) -> None:
    if not removed_fields:
        return
    summary = ((packet.get("visible_fields") or {}).get("deterministic_visible_merge_gate_summary"))
    if not isinstance(summary, dict):
        return
    for field in removed_fields:
        summary.pop(field, None)


def verdict_field_check(name: str, packets: list[dict[str, Any]], removed_fields: tuple[str, ...]) -> dict[str, Any]:
    present = name in json.dumps(packets)
    expected_present = name not in removed_fields
    return check(
        f"{name}_presence_matches_packet_variant",
        present == expected_present,
        {"present": present, "expected_present": expected_present},
    )


def build_packets(config: dict[str, Any]) -> list[dict[str, Any]]:
    spec = read_json(resolve(config["protocol_spec"]))
    seeds = read_jsonl(resolve(config["model_visible_seed_manifest"]))
    baseline = {
        str(record["candidate_id"]): record
        for record in read_jsonl(resolve(config["tool_only_baseline"]))
    }
    packet_suffix = str((config.get("full") or {}).get("packet_suffix") or "realistic_agent_visible_tool_v0_1")
    packets: list[dict[str, Any]] = []
    for seed in seeds:
        candidate_id = str(seed["candidate_id"])
        baseline_row = baseline[candidate_id]
        packet = {
            "cohort_id": COHORT_ID,
            "protocol_id": spec.get("protocol_id"),
            "evidence_level": EVIDENCE_LEVEL,
            "evidence_level_name": "realistic_agent_visible_tool_summary",
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
            "visible_fields": visible_fields(seed, baseline_row),
        }
        remove_verdict_fields(packet, variant_removed_fields(config))
        packet["evidence_packet_id"] = f"{candidate_id}__{EVIDENCE_LEVEL}__{packet_suffix}"
        findings = packet_leakage_findings(packet)
        if findings:
            raise ValueError(f"forbidden packet markers for {packet['evidence_packet_id']}: {findings}")
        packets.append(packet)
    return packets


def visible_fields(seed: dict[str, Any], baseline_row: dict[str, Any]) -> dict[str, Any]:
    patch_text = str(seed.get("patch_text") or "")
    touched_files = list(seed.get("touched_files") or [])
    static = seed.get("visible_static_evidence") or {}
    test_evidence = seed.get("visible_test_evidence") or {}
    tool_evidence = seed.get("visible_tool_evidence") or {}
    test_results = [
        {"test_name": item.get("test_name"), "outcome": item.get("outcome")}
        for item in test_evidence.get("test_results") or []
    ]
    outcome_counts = test_evidence.get("outcome_counts") or evp8_core._counts(  # noqa: SLF001
        item.get("outcome") for item in test_results
    )
    decision = str(baseline_row.get("decision") or "escalate")
    reason = baseline_row.get("reason") or baseline_row.get("primary_reason")
    contradictions = []
    if decision == "reject":
        contradictions.append("visible_test_failure")
    return {
        "issue_patch_seed": {
            "anonymous_candidate_id": seed.get("candidate_id"),
            "task_id": seed.get("task_id"),
            "project": seed.get("project"),
            "issue_summary": seed.get("issue_summary"),
            "candidate_patch_diff": patch_text,
            "touched_filenames": touched_files,
        },
        "patch_surface_map": evp8_core._patch_surface_map(patch_text, touched_files),  # noqa: SLF001
        "patch_application_static_status": {
            "patch_apply_status": "applied" if static.get("patch_applies") is True else "failed",
            "syntax_check_status": "not_run_for_realistic_agent_cohort",
            "import_smoke_status": "not_run_for_realistic_agent_cohort",
            "configured_static_check_status": "not_run_for_realistic_agent_cohort",
        },
        "visible_fail_to_pass_test_evidence": {
            "visible_fail_to_pass_scope_id": f"{seed.get('task_id')}::realistic_agent_declared_visible_tests",
            "visible_fail_to_pass_test_names": test_evidence.get("listed_tests") or [],
            "visible_fail_to_pass_outcomes": test_results,
            "visible_fail_to_pass_run_summary": {
                "run_status": test_evidence.get("run_status"),
                "observed_outcome": test_evidence.get("observed_outcome"),
                "outcome_counts": outcome_counts,
                "test_count": len(test_results),
            },
            "sanitized_fail_to_pass_stdout_tail": "not_included_in_tracked_visible_summary",
            "fail_to_pass_command_fingerprint": evp8_core.sha256_text("\n".join(test_evidence.get("listed_tests") or [])),
        },
        "visible_pass_to_pass_regression_evidence": {
            "visible_pass_to_pass_scope_id": f"{seed.get('task_id')}::realistic_agent_visible_p2p_not_materialized",
            "visible_pass_to_pass_test_names": [],
            "visible_pass_to_pass_outcomes": [],
            "sanitized_pass_to_pass_stdout_tail": "not_included_in_tracked_visible_summary",
            "pass_to_pass_scope_summary": "not_separately_materialized_for_realistic_agent_cohort",
        },
        "broader_visible_tool_diagnostics": {
            "lint_or_static_diagnostic_summary": "not_run_for_realistic_agent_cohort",
            "syntax_import_check": "not_run_for_realistic_agent_cohort",
            "sanitized_test_log_observations": [tool_evidence],
            "environment_diagnostic_summary": "recorded_only_as_visible_test_status",
            "diagnostic_tool_versions": {},
        },
        "deterministic_visible_merge_gate_summary": {
            "visible_tool_summary_counts": outcome_counts,
            "visible_tool_summary_contradictions": contradictions,
            "rule_based_visible_merge_gate_decision": decision,
            "rule_based_visible_merge_gate_reasons": [reason],
            "source_decision": {
                "condition": "realistic_agent_visible_tool_baseline_v0_1",
                "decision": decision,
                "confidence": 1.0,
                "human_review_needed": decision == "escalate",
                "risk_flags": ["visible_test_failure"] if decision == "reject" else [],
                "primary_reason": reason,
            },
        },
    }


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def check_only(args: argparse.Namespace) -> dict[str, Any]:
    config = read_json(args.config)
    spec = read_json(resolve(config["protocol_spec"]))
    template = resolve(config["prompt_template"]).read_text(encoding="utf-8")
    packets = build_packets(config)
    prompt_hashes: list[str] = []
    prompt_chars: list[int] = []
    boundary_errors: list[str] = []
    schema_errors: list[str] = []
    for packet in packets:
        prompt = evp8_core.render_prompt(template, packet)
        prompt_hashes.append(evp8_core.sha256_text(prompt))
        prompt_chars.append(len(prompt))
        boundary_errors.extend(prompt_module._boundary_findings(prompt))  # noqa: SLF001
        schema_error = evp8_core.validate_output_schema(
            evp8_core.schema_visible_rule_output(packet),
            spec.get("output_schema") or {},
        )
        if schema_error:
            schema_errors.append(schema_error)
    full_config = config.get("full") or {}
    model_ids = [str(model.get("model_id")) for model in config.get("models") or []]
    key_names = [str(model.get("api_key_env")) for model in config.get("models") or [] if model.get("api_key_env")]
    key_states, env_exists = env_key_states(resolve(config.get("env", ".env")), key_names)
    credentials_ready = env_exists and all(state == "set" for state in key_states.values())
    packet_leakages = [marker for packet in packets for marker in packet_leakage_findings(packet)]
    removed_fields = variant_removed_fields(config)
    checks = [
        check("candidate_count", len({packet["anonymous_candidate_id"] for packet in packets}) == full_config.get("candidate_count"), len({packet["anonymous_candidate_id"] for packet in packets})),
        check("packet_count", len(packets) == full_config.get("planned_calls_per_model"), len(packets)),
        check("only_e6_packets", {packet["evidence_level"] for packet in packets} == {EVIDENCE_LEVEL}, sorted({packet["evidence_level"] for packet in packets})),
        check("packet_forbidden_marker_count", not packet_leakages, sorted(set(packet_leakages))),
        verdict_field_check("rule_based_visible_merge_gate_decision", packets, removed_fields),
        verdict_field_check("rule_based_visible_merge_gate_reasons", packets, removed_fields),
        verdict_field_check("source_decision", packets, removed_fields),
        check("prompt_boundary_error_count", not boundary_errors, sorted(set(boundary_errors))),
        check("schema_error_count", not schema_errors, evp8_core._counts(schema_errors)),  # noqa: SLF001
        check("credential_key_presence", credentials_ready, {"env_file_exists": env_exists, "key_states": key_states, "values_printed": False}),
        check("api_call_not_attempted", True, False),
        check("raw_outputs_not_generated", True, False),
        check("prompt_text_not_stored", True, False),
    ]
    status = "passed" if all(item["passed"] for item in checks) else "blocked"
    summary = {
        "analysis_id": "evp8_realistic_agent_qwen_check_only_v0_1",
        "mode": "check_only",
        "cohort_id": COHORT_ID,
        "config": display_path(args.config),
        "packet_variant": packet_variant(config),
        "removed_verdict_fields": list(removed_fields),
        "planned_model_ids": model_ids,
        "candidate_count": len({packet["anonymous_candidate_id"] for packet in packets}),
        "packet_count_per_model": len(packets),
        "model_visible_levels": [EVIDENCE_LEVEL],
        "prompt_count_per_model": len(prompt_hashes),
        "prompt_hashes_unique_count": len(set(prompt_hashes)),
        "prompt_chars_min": min(prompt_chars) if prompt_chars else 0,
        "prompt_chars_max": max(prompt_chars) if prompt_chars else 0,
        "schema_rule_decision_counts": evp8_core._counts(evp8_core.schema_visible_rule_output(packet)["decision"] for packet in packets),  # noqa: SLF001
        "credential_presence_ready": credentials_ready,
        "api_call_attempted": False,
        "raw_outputs_generated": False,
        "prompt_text_stored": False,
        "api_key_values_printed": False,
        "check_only_status": status,
        "checks": checks,
        "next_step": "Run Qwen with --execute after this check-only gate passes.",
    }
    write_json(args.summary_out or DEFAULT_CHECK_SUMMARY_OUT, summary)
    if status != "passed":
        raise SystemExit(f"EVP-8 realistic Qwen check-only blocked: {status}")
    return summary


def execute(args: argparse.Namespace) -> dict[str, Any]:
    if args.config.name.endswith(".example.json"):
        raise SystemExit("Refusing to execute with tracked example config. Use ignored local config.")
    config = read_json(args.config)
    model_config = model_config_by_id(config, args.model_id)
    if model_config is None:
        raise SystemExit(f"--model-id must match one configured model: {args.model_id}")
    if model_config.get("provider_route") != "qwen_official":
        raise SystemExit("This runner only supports qwen_official.")
    load_env_file(str(resolve(config.get("env", ".env"))))
    spec = read_json(resolve(config["protocol_spec"]))
    template = resolve(config["prompt_template"]).read_text(encoding="utf-8")
    packets = build_packets(config)
    output_dir = resolve((config.get("full") or {})["output_dir"]) / safe_model_name(str(model_config["model_id"]))
    raw_out = args.raw_out or output_dir / "raw_responses.jsonl"
    default_output_prefix = output_prefix(config, str(model_config["model_id"]))
    summary_out = args.summary_out or DEFAULT_EXEC_SUMMARY_DIR / f"{default_output_prefix}_summary.json"
    parsed_reviews_out = args.parsed_reviews_out or DEFAULT_REVIEW_RECORD_DIR / f"{default_output_prefix}_reviews.jsonl"
    if config.get("overwrite_policy") == "refuse_if_output_exists":
        for path in (summary_out, raw_out, parsed_reviews_out):
            if path.exists():
                raise SystemExit(f"Refusing to overwrite output: {display_path(path)}")
    client = QwenClient()
    parsed_records: list[dict[str, Any]] = []
    raw_out.parent.mkdir(parents=True, exist_ok=True)
    with raw_out.open("x", encoding="utf-8") as raw_handle:
        for index, packet in enumerate(packets, start=1):
            prompt = evp8_core.render_prompt(template, packet)
            findings = prompt_module._boundary_findings(prompt)  # noqa: SLF001
            if findings:
                raise RuntimeError(f"prompt boundary failed for {packet['evidence_packet_id']}: {findings}")
            response = client.chat_completion(
                model=str(model_config["request_model_id"]),
                prompt=prompt,
                temperature=float(config.get("temperature", 0.0)),
                max_tokens=int(config.get("max_output_tokens", 4096)),
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
                "raw_response_text": response_text(response),
                "response": response,
                "run_date_utc": datetime.now(timezone.utc).isoformat(),
            }
            append_jsonl_record(raw_handle, raw_record)
            parsed_records.append(parsed_record_from_raw(raw_record, spec, model_config))
            print(f"[{index}/{len(packets)}] {packet['anonymous_candidate_id']} parsed={parsed_records[-1]['parse_status']} decision={parsed_records[-1]['decision']}")
    cost = evp8_core.aggregate_cost(parsed_records)
    parse_valid_count = sum(1 for record in parsed_records if record["parse_status"] == "valid")
    write_jsonl(parsed_reviews_out, parsed_records)
    summary = {
        "analysis_id": "evp8_realistic_agent_qwen_full_summary_v0_1",
        "mode": "executed",
        "cohort_id": COHORT_ID,
        "packet_variant": packet_variant(config),
        "removed_verdict_fields": list(variant_removed_fields(config)),
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
        "review_count_by_evidence_level": evp8_core._level_counts(parsed_records),  # noqa: SLF001
        "api_call_attempted": True,
        "raw_outputs_generated": True,
        "prompt_text_stored": False,
        "cost_summary": cost,
        "usage_cost_gate": "passed" if cost["unknown_cost_record_count"] == 0 else "blocked",
        "run_gate": "passed" if parse_valid_count == len(parsed_records) and cost["unknown_cost_record_count"] == 0 else "blocked",
    }
    write_json(summary_out, summary)
    if summary["run_gate"] != "passed":
        raise SystemExit(f"EVP-8 realistic Qwen run gate blocked: {summary['run_gate']}")
    return summary


def parsed_record_from_raw(raw_record: dict[str, Any], spec: dict[str, Any], model_config: dict[str, Any]) -> dict[str, Any]:
    response = raw_record.get("response") if isinstance(raw_record.get("response"), dict) else {}
    raw_text = str(raw_record.get("raw_response_text") or "")
    try:
        parsed = extract_json_object(raw_text)
        invalid_reason = evp8_core.validate_output_schema(parsed, spec.get("output_schema") or {})
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
