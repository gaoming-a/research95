"""Guarded EVP-8 DeepSeek/Qwen smoke runner.

The default path is check-only and does not call model APIs. Real smoke calls
require an ignored local config, an explicit --execute flag, and a single
configured model id.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
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

from cross_review.env import load_env_file  # noqa: E402
from cross_review.openrouter import DeepSeekClient, QwenClient  # noqa: E402
from cross_review.parsing import extract_json_object, response_text  # noqa: E402

import build_evp8_prompt_manifest as prompt_module  # noqa: E402
import preflight_evp8_deepseek_qwen as preflight_module  # noqa: E402


DEFAULT_CONFIG = REPO_ROOT / "configs" / "evp8_deepseek_qwen.local.json"
DEFAULT_CHECK_SUMMARY_OUT = REPO_ROOT / "data" / "protocols" / "evp8_deepseek_qwen_smoke_check_only_v0_1.json"
DEFAULT_EXEC_SUMMARY_DIR = REPO_ROOT / "data" / "reviews"
MODEL_VISIBLE_LEVELS = ("E0", "E1", "E2", "E3", "E4", "E5", "E6")
EVP7_CANDIDATES = REPO_ROOT / "data" / "patches" / "evp7_candidates.jsonl"
DEEPSEEK_PRICING_SOURCE_URL = "https://api-docs.deepseek.com/quick_start/pricing"
DEEPSEEK_V4_PRO_USD_PER_1M_TOKENS = {
    "input_cache_hit": 0.003625,
    "input_cache_miss": 0.435,
    "output": 0.87,
}
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


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )


def resolve(path_value: Any) -> Path:
    path = Path(str(path_value))
    return path if path.is_absolute() else REPO_ROOT / path


def display_path(path: Path) -> str:
    absolute = path if path.is_absolute() else REPO_ROOT / path
    try:
        return absolute.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(absolute)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def leakage_findings(value: Any) -> list[str]:
    serialized = json.dumps(value, ensure_ascii=False).lower()
    return sorted({marker for marker in FORBIDDEN_MARKERS if marker.lower() in serialized})


def load_source_candidate_index() -> dict[str, dict[str, Any]]:
    records = read_jsonl(EVP7_CANDIDATES)
    return {str(record["evp7_candidate_id"]): record for record in records}


def select_smoke_candidates(candidate_set: dict[str, Any], count: int) -> list[dict[str, Any]]:
    records = list(candidate_set.get("records") or [])
    project_counts: dict[str, int] = {}
    project_first_index: dict[str, int] = {}
    project_first_record: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records):
        project = str(record.get("project"))
        project_counts[project] = project_counts.get(project, 0) + 1
        project_first_index.setdefault(project, index)
        project_first_record.setdefault(project, record)
    ordered_projects = sorted(
        project_counts,
        key=lambda project: (-project_counts[project], project_first_index[project]),
    )
    selected = [project_first_record[project] for project in ordered_projects[:count]]
    selected_ids = {record["evp8_candidate_id"] for record in selected}
    if len(selected) == count:
        return selected
    for record in records:
        if record["evp8_candidate_id"] not in selected_ids:
            selected.append(record)
            selected_ids.add(record["evp8_candidate_id"])
        if len(selected) == count:
            return selected
    return selected


def build_smoke_packets(config: dict[str, Any]) -> list[dict[str, Any]]:
    spec = read_json(resolve(config["protocol_spec"]))
    candidate_set = read_json(resolve(config["candidate_set"]))
    source_index = load_source_candidate_index()
    levels = {level["level"]: level for level in spec.get("evidence_ladder", [])}
    smoke = config.get("smoke") or {}
    selected = select_smoke_candidates(candidate_set, int(smoke.get("candidate_count") or 5))
    packets: list[dict[str, Any]] = []
    for candidate in selected:
        source_id = str(candidate["source_candidate_id"])
        source = source_index.get(source_id)
        if source is None:
            raise ValueError(f"missing EVP-7 source candidate: {source_id}")
        all_fields = _visible_field_groups(candidate, source)
        for level_name in smoke.get("levels") or MODEL_VISIBLE_LEVELS:
            level = levels[level_name]
            field_groups = list(level.get("model_visible_field_groups") or [])
            visible_fields = {group: all_fields[group] for group in field_groups if group in all_fields}
            packet = {
                "cohort_id": "EVP-8",
                "protocol_id": spec["protocol_id"],
                "candidate_set_id": candidate["candidate_set_id"],
                "evidence_level": level_name,
                "evidence_level_name": level["level_name"],
                "anonymous_candidate_id": candidate["evp8_candidate_id"],
                "source_candidate_id": source_id,
                "task_id": candidate["task_id"],
                "project": candidate["project"],
                "patch_sha256": candidate["patch_sha256"],
                "model_visible_field_groups": field_groups,
                "visible_fields": visible_fields,
            }
            packet["evidence_packet_id"] = (
                f"{packet['anonymous_candidate_id']}__{packet['evidence_level']}__evp8_smoke_v0_1"
            )
            findings = leakage_findings(packet)
            if findings:
                raise ValueError(f"leakage findings for {packet['evidence_packet_id']}: {findings}")
            packets.append(packet)
    return packets


def _visible_field_groups(candidate: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    seed = source.get("model_visible_seed") or {}
    patch_text = str(seed.get("patch_text") or "")
    touched_files = list(seed.get("touched_files") or candidate.get("touched_files") or [])
    visible_tests = list(source.get("visible_tests") or [])
    patch_applied = (source.get("validation_summary") or {}).get("patch_applied")
    patch_apply_status = "applied" if patch_applied is True else "failed" if patch_applied is False else "not_recorded"
    f2p_outcomes = ["not_run_in_phase0_smoke" for _ in visible_tests]
    merge_gate = _deterministic_visible_merge_gate(patch_apply_status, f2p_outcomes)
    return {
        "issue_patch_seed": {
            "anonymous_candidate_id": candidate["evp8_candidate_id"],
            "task_id": candidate["task_id"],
            "project": candidate["project"],
            "issue_summary": seed.get("issue_summary"),
            "candidate_patch_diff": patch_text,
            "touched_filenames": touched_files,
        },
        "patch_surface_map": _patch_surface_map(patch_text, touched_files),
        "patch_application_static_status": {
            "patch_apply_status": patch_apply_status,
            "syntax_check_status": "not_run_in_phase0_smoke",
            "import_smoke_status": "not_run_in_phase0_smoke",
            "configured_static_check_status": "not_run_in_phase0_smoke",
        },
        "visible_fail_to_pass_test_evidence": {
            "visible_fail_to_pass_scope_id": f"{candidate['task_id']}::phase0_smoke_visible_f2p",
            "visible_fail_to_pass_test_names": visible_tests,
            "visible_fail_to_pass_outcomes": f2p_outcomes,
            "sanitized_fail_to_pass_stdout_tail": "not_generated_in_phase0_smoke",
            "fail_to_pass_command_fingerprint": sha256_text("\n".join(visible_tests)),
        },
        "visible_pass_to_pass_regression_evidence": {
            "visible_pass_to_pass_scope_id": f"{candidate['task_id']}::phase0_smoke_visible_p2p_not_materialized",
            "visible_pass_to_pass_test_names": [],
            "visible_pass_to_pass_outcomes": [],
            "sanitized_pass_to_pass_stdout_tail": "not_generated_in_phase0_smoke",
            "pass_to_pass_scope_summary": "not_materialized_in_phase0_smoke",
        },
        "broader_visible_tool_diagnostics": {
            "lint_or_static_diagnostic_summary": "not_run_in_phase0_smoke",
            "sanitized_test_log_observations": [],
            "environment_diagnostic_summary": "not_recorded_in_phase0_smoke",
            "diagnostic_tool_versions": {},
        },
        "deterministic_visible_merge_gate_summary": merge_gate,
    }


def _patch_surface_map(patch_text: str, touched_files: list[str]) -> dict[str, Any]:
    current_file = ""
    hunk_locations: list[str] = []
    neighboring_symbols: list[str] = []
    related_imports: list[str] = []
    changed_functions: list[str] = []
    changed_classes: list[str] = []
    for line in patch_text.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[6:]
        elif line.startswith("+++ "):
            current_file = line[4:]
        elif line.startswith("@@"):
            hunk_locations.append(_hunk_location(current_file, line))
            symbol = _hunk_symbol(line)
            if symbol:
                neighboring_symbols.append(symbol)
                if symbol.lstrip().startswith("def "):
                    changed_functions.append(_symbol_name(symbol, "def"))
                elif symbol.lstrip().startswith("class "):
                    changed_classes.append(_symbol_name(symbol, "class"))
        elif line.startswith(("+def ", "-def ", "+    def ", "-    def ")):
            changed_functions.append(_symbol_name(line[1:].strip(), "def"))
        elif line.startswith(("+class ", "-class ", "+    class ", "-    class ")):
            changed_classes.append(_symbol_name(line[1:].strip(), "class"))
        elif line.startswith(("+import ", "+from ")):
            related_imports.append(line[1:].strip())
    return {
        "changed_files": sorted(set(touched_files)),
        "changed_functions": sorted({name for name in changed_functions if name}),
        "changed_classes": sorted({name for name in changed_classes if name}),
        "hunk_locations": hunk_locations,
        "neighboring_symbols": sorted({symbol for symbol in neighboring_symbols if symbol}),
        "related_imports": sorted(set(related_imports)),
        "related_module_paths": sorted(set(touched_files)),
    }


def _hunk_location(current_file: str, line: str) -> str:
    match = re.search(r"\+(\d+)(?:,(\d+))?", line)
    if not match:
        return f"{current_file}:unknown"
    return f"{current_file}:{match.group(1)}"


def _hunk_symbol(line: str) -> str:
    parts = line.split("@@")
    return parts[-1].strip() if len(parts) >= 3 else ""


def _symbol_name(symbol: str, keyword: str) -> str:
    prefix = f"{keyword} "
    text = symbol.strip()
    if not text.startswith(prefix):
        return ""
    tail = text[len(prefix) :]
    return re.split(r"[\(:\s]", tail, maxsplit=1)[0]


def _deterministic_visible_merge_gate(patch_apply_status: str, f2p_outcomes: list[str]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for outcome in f2p_outcomes:
        counts[outcome] = counts.get(outcome, 0) + 1
    contradictions: list[str] = []
    decision = "escalate"
    reasons = ["phase0_smoke_visible_evidence_is_incomplete"]
    if patch_apply_status == "failed":
        contradictions.append("patch_apply_failed")
        decision = "reject"
        reasons = ["visible_patch_apply_status_failed"]
    return {
        "visible_tool_summary_counts": counts,
        "visible_tool_summary_contradictions": contradictions,
        "rule_based_visible_merge_gate_decision": decision,
        "rule_based_visible_merge_gate_reasons": reasons,
    }


def render_prompt(template: str, packet: dict[str, Any]) -> str:
    return prompt_module.render_prompt(template, packet)


def validate_output_schema(parsed: Any, output_schema: dict[str, Any]) -> str | None:
    if not isinstance(parsed, dict):
        return "schema_not_object"
    required = output_schema.get("required_keys") or []
    missing = [key for key in required if key not in parsed]
    if missing:
        return "missing_keys:" + ",".join(missing)
    forbidden = [key for key in output_schema.get("forbidden_output_keys") or [] if key in parsed]
    if forbidden:
        return "forbidden_keys:" + ",".join(forbidden)
    if parsed["decision"] not in set(output_schema.get("decision_values") or []):
        return f"invalid_decision:{parsed['decision']}"
    confidence = parsed["confidence"]
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        return "invalid_confidence"
    if not isinstance(parsed["primary_reason"], str) or not parsed["primary_reason"]:
        return "invalid_primary_reason"
    if not isinstance(parsed["evidence_used"], list):
        return "invalid_evidence_used"
    if not isinstance(parsed["visible_contradictions"], list):
        return "invalid_visible_contradictions"
    risk_values = set(output_schema.get("risk_flag_values") or [])
    risk_flags = parsed["risk_flags"]
    if not isinstance(risk_flags, list) or any(flag not in risk_values for flag in risk_flags):
        return "invalid_risk_flags"
    if not isinstance(parsed["human_review_needed"], bool):
        return "invalid_human_review_needed"
    if leakage_findings(parsed):
        return "forbidden_marker_in_output"
    return None


def schema_visible_rule_output(packet: dict[str, Any]) -> dict[str, Any]:
    fields = packet.get("visible_fields") or {}
    static = fields.get("patch_application_static_status") or {}
    summary = fields.get("deterministic_visible_merge_gate_summary") or {}
    if static.get("patch_apply_status") == "failed":
        return _decision(
            "reject",
            1.0,
            "Visible patch-apply status failed.",
            ["patch_application_static_status.patch_apply_status"],
            ["patch_apply_failed"],
            ["patch_apply_failed"],
        )
    if summary.get("rule_based_visible_merge_gate_decision") == "reject":
        return _decision(
            "reject",
            1.0,
            "Visible deterministic merge-gate summary rejected the candidate.",
            ["deterministic_visible_merge_gate_summary.rule_based_visible_merge_gate_decision"],
            ["visible_test_failure"],
            list(summary.get("visible_tool_summary_contradictions") or []),
        )
    return _decision(
        "escalate",
        0.0,
        "Phase 0 smoke packet contains incomplete visible evidence slots.",
        list(fields.keys()),
        ["insufficient_evidence"],
        ["phase0_smoke_packet_incomplete"],
    )


def _decision(
    decision: str,
    confidence: float,
    reason: str,
    evidence_used: list[str],
    risk_flags: list[str],
    contradictions: list[str],
) -> dict[str, Any]:
    return {
        "decision": decision,
        "confidence": confidence,
        "primary_reason": reason,
        "evidence_used": evidence_used,
        "visible_contradictions": contradictions,
        "risk_flags": risk_flags,
        "human_review_needed": decision == "escalate",
    }


def check_only(args: argparse.Namespace) -> dict[str, Any]:
    config = read_json(args.config)
    preflight = preflight_module.preflight(args.config, allow_missing_credentials=args.allow_missing_credentials)
    if not preflight["structural_ready"]:
        raise SystemExit("EVP-8 smoke check-only requires structural preflight readiness.")
    if not args.allow_missing_credentials and not preflight["ready_for_user_execute_command"]:
        raise SystemExit("EVP-8 smoke check-only requires strict local preflight unless --allow-missing-credentials is set.")
    spec = read_json(resolve(config["protocol_spec"]))
    template = resolve(config["prompt_template"]).read_text(encoding="utf-8")
    packets = build_smoke_packets(config)
    prompt_hashes: list[str] = []
    prompt_chars: list[int] = []
    schema_errors: list[str] = []
    boundary_errors: list[str] = []
    for packet in packets:
        prompt = render_prompt(template, packet)
        prompt_hashes.append(sha256_text(prompt))
        prompt_chars.append(len(prompt))
        findings = prompt_module._boundary_findings(prompt)  # noqa: SLF001
        if findings:
            boundary_errors.extend(findings)
        error = validate_output_schema(schema_visible_rule_output(packet), spec.get("output_schema") or {})
        if error:
            schema_errors.append(error)
    summary = {
        "mode": "check_only",
        "cohort_id": "EVP-8",
        "protocol_id": spec.get("protocol_id"),
        "candidate_set_id": preflight.get("candidate_set_id"),
        "config": display_path(args.config),
        "selected_candidate_ids": sorted({packet["anonymous_candidate_id"] for packet in packets}),
        "selection_policy": "deterministic_project_frequency_stratified_first_candidate_per_top_project",
        "model_visible_levels": list(MODEL_VISIBLE_LEVELS),
        "expected_packet_count": 35,
        "packet_count": len(packets),
        "prompt_count": len(prompt_hashes),
        "prompt_hashes_unique_count": len(set(prompt_hashes)),
        "prompt_chars_min": min(prompt_chars) if prompt_chars else 0,
        "prompt_chars_max": max(prompt_chars) if prompt_chars else 0,
        "prompt_text_stored": False,
        "raw_outputs_generated": False,
        "api_call_attempted": False,
        "api_key_values_printed": False,
        "local_config_content_stored_in_tracked_summary": False,
        "boundary_error_count": len(boundary_errors),
        "boundary_errors": sorted(set(boundary_errors)),
        "schema_error_count": len(schema_errors),
        "schema_error_counts": _counts(schema_errors),
        "check_only_status": "passed"
        if len(packets) == 35 and not boundary_errors and not schema_errors
        else "failed",
        "preflight_structural_ready": preflight["structural_ready"],
        "preflight_ready_for_user_execute_command": preflight["ready_for_user_execute_command"],
        "next_step": "Wait for explicit user command before running --execute smoke.",
    }
    write_json(args.summary_out or DEFAULT_CHECK_SUMMARY_OUT, summary)
    if summary["check_only_status"] != "passed":
        raise SystemExit(f"EVP-8 smoke check-only failed: {summary}")
    return summary


def execute(args: argparse.Namespace) -> dict[str, Any]:
    if args.config.name.endswith(".example.json"):
        raise SystemExit("Refusing to execute with tracked example config. Use ignored local config.")
    config = read_json(args.config)
    preflight = preflight_module.preflight(args.config)
    if not preflight["ready_for_user_execute_command"]:
        raise SystemExit("EVP-8 smoke execute requires strict DeepSeek/Qwen preflight readiness.")
    model_config = _model_config(config, args.model_id)
    if model_config is None:
        raise SystemExit(f"--model-id must match one configured model: {args.model_id}")
    output_dir = resolve((config.get("smoke") or {})["output_dir"]) / safe_name(str(model_config["model_id"]))
    raw_out = args.raw_out or output_dir / "raw_responses.jsonl"
    summary_out = args.summary_out or DEFAULT_EXEC_SUMMARY_DIR / f"evp8_{safe_name(str(model_config['model_id']))}_smoke_summary.json"
    if config.get("overwrite_policy") == "refuse_if_output_exists" and (raw_out.exists() or summary_out.exists()):
        raise SystemExit(f"Refusing to overwrite existing smoke outputs: {display_path(raw_out)} or {display_path(summary_out)}")

    load_env_file(str(resolve(config.get("env", ".env"))))
    spec = read_json(resolve(config["protocol_spec"]))
    template = resolve(config["prompt_template"]).read_text(encoding="utf-8")
    packets = build_smoke_packets(config)
    raw_records: list[dict[str, Any]] = []
    parsed_records: list[dict[str, Any]] = []
    for packet in packets:
        prompt = render_prompt(template, packet)
        findings = prompt_module._boundary_findings(prompt)  # noqa: SLF001
        if findings:
            raise SystemExit(f"prompt boundary failed for {packet['evidence_packet_id']}: {findings}")
        response = _client(str(model_config["provider_route"])).chat_completion(
            model=str(model_config["request_model_id"]),
            prompt=prompt,
            temperature=float(config.get("temperature", 0.0)),
            max_tokens=int(config.get("max_output_tokens", 1024)),
        )
        raw_text = response_text(response)
        parsed, invalid_reason = _parse_response(raw_text, spec)
        cost = cost_summary(response=response, model_config=model_config)
        raw_records.append(
            {
                "evidence_packet_id": packet["evidence_packet_id"],
                "anonymous_candidate_id": packet["anonymous_candidate_id"],
                "evidence_level": packet["evidence_level"],
                "requested_model_id": model_config["request_model_id"],
                "configured_model_id": model_config["model_id"],
                "actual_model_id": response.get("model"),
                "provider_route": model_config["provider_route"],
                "raw_response_text": raw_text,
                "response": response,
                "run_date_utc": datetime.now(timezone.utc).isoformat(),
            }
        )
        parsed_records.append(
            {
                "evidence_packet_id": packet["evidence_packet_id"],
                "anonymous_candidate_id": packet["anonymous_candidate_id"],
                "evidence_level": packet["evidence_level"],
                "parse_status": "valid" if invalid_reason is None else "invalid",
                "invalid_reason": invalid_reason,
                "decision": parsed.get("decision") if parsed else None,
                "risk_flags": parsed.get("risk_flags") if parsed else [],
                "human_review_needed": parsed.get("human_review_needed") if parsed else None,
                "request_model_id": model_config["request_model_id"],
                "configured_model_id": model_config["model_id"],
                "actual_model_id": response.get("model"),
                "provider_route": model_config["provider_route"],
                "usage": cost["usage"],
                "cost_usd": cost["cost_usd"],
                "cost_source": cost["cost_source"],
                "cost_observability": cost["cost_observability"],
            }
        )

    write_jsonl(raw_out, raw_records)
    cost = aggregate_cost(parsed_records)
    parse_valid_count = sum(1 for record in parsed_records if record["parse_status"] == "valid")
    summary = {
        "mode": "executed",
        "cohort_id": "EVP-8",
        "protocol_id": spec.get("protocol_id"),
        "candidate_set_id": preflight.get("candidate_set_id"),
        "config": display_path(args.config),
        "configured_model_id": model_config["model_id"],
        "request_model_id": model_config["request_model_id"],
        "provider_route": model_config["provider_route"],
        "raw_responses_out": display_path(raw_out),
        "raw_response_text_stored_in_tracked_summary": False,
        "review_count": len(parsed_records),
        "parse_valid_count": parse_valid_count,
        "invalid_parse_count": len(parsed_records) - parse_valid_count,
        "decision_counts": _counts(record["decision"] for record in parsed_records),
        "review_count_by_evidence_level": _level_counts(parsed_records),
        "parse_valid_count_by_evidence_level": _level_counts(
            record for record in parsed_records if record["parse_status"] == "valid"
        ),
        "invalid_parse_count_by_evidence_level": _level_counts(
            record for record in parsed_records if record["parse_status"] != "valid"
        ),
        "decision_counts_by_evidence_level": _counts_by_evidence_level(parsed_records, "decision"),
        "request_model_id_counts": _counts(record["request_model_id"] for record in parsed_records),
        "configured_model_id_counts": _counts(record["configured_model_id"] for record in parsed_records),
        "actual_model_id_counts": _counts(record["actual_model_id"] or "missing" for record in parsed_records),
        "actual_model_id_missing_count": sum(1 for record in parsed_records if not record["actual_model_id"]),
        "provider_route_counts": _counts(record["provider_route"] for record in parsed_records),
        "api_call_attempted": True,
        "raw_outputs_generated": True,
        "prompt_text_stored": False,
        "cost_summary": cost,
        "usage_cost_gate": "passed" if cost["unknown_cost_record_count"] == 0 else "blocked",
        "smoke_gate": "passed"
        if parse_valid_count == len(parsed_records) and cost["unknown_cost_record_count"] == 0
        else "blocked",
    }
    write_json(summary_out, summary)
    if summary["smoke_gate"] != "passed":
        raise SystemExit(f"EVP-8 smoke gate blocked after writing outputs: {summary['smoke_gate']}")
    return summary


def _parse_response(raw_text: str, spec: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    try:
        parsed = extract_json_object(raw_text)
    except Exception as exc:  # noqa: BLE001
        return None, f"invalid_json:{exc}"
    error = validate_output_schema(parsed, spec.get("output_schema") or {})
    return parsed, error


def _model_config(config: dict[str, Any], model_id: str | None) -> dict[str, Any] | None:
    models = config.get("models") or []
    if model_id is None:
        return None
    for model in models:
        if model.get("model_id") == model_id:
            return model
    return None


def _client(provider_route: str) -> DeepSeekClient | QwenClient:
    if provider_route == "deepseek_official":
        return DeepSeekClient()
    if provider_route == "qwen_official":
        return QwenClient()
    raise SystemExit(f"unsupported provider route for EVP-8 smoke: {provider_route}")


def cost_summary(*, response: dict[str, Any], model_config: dict[str, Any]) -> dict[str, Any]:
    usage = response.get("usage")
    if not isinstance(usage, dict):
        return _unknown_cost("missing_usage")
    normalized_usage = _usage_summary(usage)
    provider_cost = _float_or_none(usage.get("cost"))
    if provider_cost is not None:
        return {
            "usage": normalized_usage,
            "cost_usd": round(provider_cost, 9),
            "cost_source": "provider_reported_usage_cost",
            "cost_observability": "provider_reported_cost",
        }
    if model_config.get("provider_route") == "deepseek_official" and model_config.get("request_model_id") == "deepseek-v4-pro":
        estimated = _estimate_deepseek_v4_pro_cost(usage)
        if estimated is not None:
            return {
                "usage": normalized_usage,
                "cost_usd": round(estimated["cost_usd"], 9),
                "cost_source": "estimated_from_tokens",
                "cost_observability": "estimated_from_provider_token_usage",
                "cost_pricing": {
                    "source": DEEPSEEK_PRICING_SOURCE_URL,
                    "unit": "USD per 1M tokens",
                    "model": "deepseek-v4-pro",
                    "rates": DEEPSEEK_V4_PRO_USD_PER_1M_TOKENS,
                    "input_cache_miss_fallback": estimated["input_cache_miss_fallback"],
                },
            }
    if normalized_usage:
        return {
            "usage": normalized_usage,
            "cost_usd": None,
            "cost_source": "provider_token_usage_without_usd_cost",
            "cost_observability": "token_usage_present_cost_unknown",
        }
    return _unknown_cost("missing_provider_cost_or_token_usage", usage=normalized_usage)


def _usage_summary(usage: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "input_tokens",
        "output_tokens",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "prompt_cache_hit_tokens",
        "prompt_cache_miss_tokens",
        "cache_hit_tokens",
        "cache_miss_tokens",
    }
    summary: dict[str, Any] = {}
    for key in sorted(allowed):
        value = _token_count(usage.get(key))
        if value is not None:
            summary[key] = value
    return summary


def _estimate_deepseek_v4_pro_cost(usage: dict[str, Any]) -> dict[str, Any] | None:
    completion_tokens = _token_count(usage.get("completion_tokens"), usage.get("output_tokens"))
    prompt_tokens = _token_count(usage.get("prompt_tokens"), usage.get("input_tokens"))
    cache_hit_tokens = _token_count(usage.get("prompt_cache_hit_tokens"), usage.get("cache_hit_tokens"))
    cache_miss_tokens = _token_count(usage.get("prompt_cache_miss_tokens"), usage.get("cache_miss_tokens"))
    input_cache_miss_fallback = False
    if cache_hit_tokens is None and cache_miss_tokens is None and prompt_tokens is not None:
        cache_hit_tokens = 0
        cache_miss_tokens = prompt_tokens
        input_cache_miss_fallback = True
    if completion_tokens is None and prompt_tokens is None and cache_hit_tokens is None and cache_miss_tokens is None:
        return None
    prompt_cost = 0.0
    if cache_hit_tokens is not None:
        prompt_cost += cache_hit_tokens * DEEPSEEK_V4_PRO_USD_PER_1M_TOKENS["input_cache_hit"] / 1_000_000
    if cache_miss_tokens is not None:
        prompt_cost += cache_miss_tokens * DEEPSEEK_V4_PRO_USD_PER_1M_TOKENS["input_cache_miss"] / 1_000_000
    completion_cost = 0.0
    if completion_tokens is not None:
        completion_cost = completion_tokens * DEEPSEEK_V4_PRO_USD_PER_1M_TOKENS["output"] / 1_000_000
    return {
        "cost_usd": prompt_cost + completion_cost,
        "input_cache_miss_fallback": input_cache_miss_fallback,
    }


def _token_count(*values: Any) -> int | None:
    for value in values:
        if value is None:
            continue
        try:
            count = int(value)
        except (TypeError, ValueError):
            continue
        if count >= 0:
            return count
    return None


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _unknown_cost(reason: str, usage: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "usage": usage or {},
        "cost_usd": None,
        "cost_source": "unknown",
        "cost_observability": reason,
    }


def aggregate_cost(records: list[dict[str, Any]]) -> dict[str, Any]:
    total = 0.0
    unknown = 0
    sources: list[str] = []
    observability: list[str] = []
    for record in records:
        sources.append(str(record.get("cost_source") or "unknown"))
        observability.append(str(record.get("cost_observability") or "unknown"))
        cost = record.get("cost_usd")
        if cost is None:
            unknown += 1
        else:
            total += float(cost)
    return {
        "total_cost_usd": round(total, 9),
        "unknown_cost_record_count": unknown,
        "cost_source_counts": _counts(sources),
        "cost_observability_counts": _counts(observability),
    }


def _counts(values: Any) -> dict[str, int]:
    result: dict[str, int] = {}
    for value in values:
        key = str(value)
        result[key] = result.get(key, 0) + 1
    return dict(sorted(result.items()))


def _level_counts(records: Any) -> dict[str, int]:
    result = {level: 0 for level in MODEL_VISIBLE_LEVELS}
    for record in records:
        level = str(record["evidence_level"])
        result[level] = result.get(level, 0) + 1
    return dict(sorted(result.items()))


def _counts_by_evidence_level(records: list[dict[str, Any]], field: str) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {level: {} for level in MODEL_VISIBLE_LEVELS}
    for record in records:
        level = str(record["evidence_level"])
        value = record.get(field)
        key = str(value) if value is not None else "missing"
        bucket = result.setdefault(level, {})
        bucket[key] = bucket.get(key, 0) + 1
    return {level: dict(sorted(counts.items())) for level, counts in sorted(result.items())}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--model-id", help="Configured model id to execute, e.g. deepseek/deepseek-v4-pro.")
    parser.add_argument("--allow-missing-credentials", action="store_true")
    parser.add_argument("--summary-out", type=Path)
    parser.add_argument("--raw-out", type=Path)
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
