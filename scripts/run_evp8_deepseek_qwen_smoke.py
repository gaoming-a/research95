"""Guarded EVP-8 DeepSeek/Qwen smoke/full runner.

The default path is check-only and does not call model APIs. Real calls require
an ignored local config, an explicit --execute flag, a run scope, and a single
configured model id.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
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
DEFAULT_SMOKE_CHECK_SUMMARY_OUT = REPO_ROOT / "data" / "protocols" / "evp8_deepseek_qwen_smoke_check_only_v0_1.json"
DEFAULT_FULL_CHECK_SUMMARY_OUT = REPO_ROOT / "data" / "protocols" / "evp8_deepseek_qwen_first_batch_full_check_only_v0_1.json"
DEFAULT_EXEC_SUMMARY_DIR = REPO_ROOT / "data" / "reviews"
MODEL_VISIBLE_LEVELS = ("E0", "E1", "E2", "E3", "E4", "E5", "E6")
EVP7_CANDIDATES = REPO_ROOT / "data" / "patches" / "evp7_candidates.jsonl"
EVP7_VISIBLE_TEST_OUTCOMES = REPO_ROOT / "data" / "evidence" / "evp7_visible_test_outcomes.jsonl"
EVP7_VISIBLE_TOOL_SUMMARIES = REPO_ROOT / "data" / "evidence" / "evp7_visible_tool_summaries.jsonl"
EVP7_TOOL_ONLY_DECISIONS = REPO_ROOT / "data" / "baselines" / "evp7_tool_only_decisions.jsonl"
DEEPSEEK_PRICING_SOURCE_URL = "https://api-docs.deepseek.com/quick_start/pricing"
DEEPSEEK_V4_PRO_USD_PER_1M_TOKENS = {
    "input_cache_hit": 0.003625,
    "input_cache_miss": 0.435,
    "output": 0.87,
}
QWEN_PRICING_SOURCE_URL = "https://help.aliyun.com/zh/model-studio/model-pricing"
QWEN_3_7_MAX_CNY_PER_1M_TOKENS = {
    "input": 12.0,
    "output": 36.0,
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


def load_visible_artifact_indexes(config: dict[str, Any]) -> dict[str, Any]:
    mode = str(config.get("evidence_source_mode") or "placeholder_not_run")
    if mode == "placeholder_not_run":
        return {"mode": mode}
    if mode != "evp7_visible_artifacts":
        raise ValueError(f"unsupported evidence_source_mode: {mode}")
    sources = config.get("visible_artifact_sources") or {}
    visible_tests = read_jsonl(resolve(sources.get("visible_test_outcomes") or EVP7_VISIBLE_TEST_OUTCOMES))
    tool_summaries = read_jsonl(resolve(sources.get("visible_tool_summaries") or EVP7_VISIBLE_TOOL_SUMMARIES))
    tool_decisions = read_jsonl(resolve(sources.get("tool_only_decisions") or EVP7_TOOL_ONLY_DECISIONS))
    decisions_by_candidate: dict[str, dict[str, dict[str, Any]]] = {}
    for record in tool_decisions:
        candidate_id = str(record.get("candidate_id"))
        condition = str(record.get("condition"))
        decisions_by_candidate.setdefault(candidate_id, {})[condition] = record
    return {
        "mode": mode,
        "visible_test_outcomes": {str(record.get("candidate_id")): record for record in visible_tests},
        "visible_tool_summaries": {str(record.get("candidate_id")): record for record in tool_summaries},
        "tool_only_decisions": decisions_by_candidate,
    }


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


def build_packets(config: dict[str, Any], run_scope: str) -> list[dict[str, Any]]:
    spec = read_json(resolve(config["protocol_spec"]))
    candidate_set = read_json(resolve(config["candidate_set"]))
    source_index = load_source_candidate_index()
    visible_artifacts = load_visible_artifact_indexes(config)
    levels = {level["level"]: level for level in spec.get("evidence_ladder", [])}
    scope_config = config.get(run_scope) or {}
    if run_scope == "smoke":
        selected = select_smoke_candidates(candidate_set, int(scope_config.get("candidate_count") or 5))
        packet_suffix = str(scope_config.get("packet_suffix") or "evp8_smoke_v0_1")
    elif run_scope == "full":
        selected = list(candidate_set.get("records") or [])
        packet_suffix = str(scope_config.get("packet_suffix") or "evp8_first_batch_full_v0_1")
    else:
        raise ValueError(f"unsupported EVP-8 run scope: {run_scope}")
    packets: list[dict[str, Any]] = []
    for candidate in selected:
        source_id = str(candidate["source_candidate_id"])
        source = source_index.get(source_id)
        if source is None:
            raise ValueError(f"missing EVP-7 source candidate: {source_id}")
        all_fields = _visible_field_groups(candidate, source, run_scope, visible_artifacts)
        for level_name in scope_config.get("levels") or MODEL_VISIBLE_LEVELS:
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
                "evidence_source_mode": visible_artifacts["mode"],
                "model_visible_field_groups": field_groups,
                "visible_fields": visible_fields,
            }
            packet["evidence_packet_id"] = (
                f"{packet['anonymous_candidate_id']}__{packet['evidence_level']}__{packet_suffix}"
            )
            findings = leakage_findings(packet)
            if findings:
                raise ValueError(f"leakage findings for {packet['evidence_packet_id']}: {findings}")
            packets.append(packet)
    return packets


def build_smoke_packets(config: dict[str, Any]) -> list[dict[str, Any]]:
    return build_packets(config, "smoke")


def _visible_field_groups(
    candidate: dict[str, Any],
    source: dict[str, Any],
    run_scope: str,
    visible_artifacts: dict[str, Any],
) -> dict[str, Any]:
    scope_tag = "phase0_smoke" if run_scope == "smoke" else "first_batch_full"
    seed = source.get("model_visible_seed") or {}
    patch_text = str(seed.get("patch_text") or "")
    touched_files = list(seed.get("touched_files") or candidate.get("touched_files") or [])
    visible_tests = list(source.get("visible_tests") or [])
    patch_applied = (source.get("validation_summary") or {}).get("patch_applied")
    patch_apply_status = "applied" if patch_applied is True else "failed" if patch_applied is False else "not_recorded"
    source_candidate_id = str(source["evp7_candidate_id"])
    visible_record = (visible_artifacts.get("visible_test_outcomes") or {}).get(source_candidate_id)
    tool_summary_record = (visible_artifacts.get("visible_tool_summaries") or {}).get(source_candidate_id)
    tool_decisions = (visible_artifacts.get("tool_only_decisions") or {}).get(source_candidate_id) or {}
    if visible_artifacts["mode"] == "evp7_visible_artifacts" and visible_record:
        visible_tests = list(visible_record.get("visible_tests") or visible_tests)
        test_results = _sanitized_visible_test_results(visible_record)
        f2p_outcomes = [str(item.get("outcome") or "unknown") for item in test_results]
        visible_run_summary = _sanitized_visible_run_summary(visible_record, test_results)
    else:
        test_results = [
            {"test_name": test_name, "outcome": f"not_run_in_{scope_tag}"}
            for test_name in visible_tests
        ]
        f2p_outcomes = [str(item["outcome"]) for item in test_results]
        visible_run_summary = {
            "run_status": f"not_run_in_{scope_tag}",
            "timeout": False,
            "test_count": len(test_results),
            "outcome_counts": _counts(item["outcome"] for item in test_results),
        }
    tool_summary = _sanitized_visible_tool_summary(tool_summary_record)
    visible_tests_decision = _sanitized_tool_decision(tool_decisions.get("tool_only_visible_tests"))
    visible_tool_decision = _sanitized_tool_decision(tool_decisions.get("tool_only_visible_tool_summary"))
    merge_gate = _deterministic_visible_merge_gate(
        patch_apply_status,
        f2p_outcomes,
        scope_tag,
        tool_decision=visible_tool_decision,
    )
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
            "syntax_check_status": f"not_run_in_{scope_tag}",
            "import_smoke_status": f"not_run_in_{scope_tag}",
            "configured_static_check_status": f"not_run_in_{scope_tag}",
        },
        "visible_fail_to_pass_test_evidence": {
            "visible_fail_to_pass_scope_id": f"{candidate['task_id']}::{scope_tag}_visible_f2p",
            "visible_fail_to_pass_test_names": visible_tests,
            "visible_fail_to_pass_outcomes": test_results,
            "visible_fail_to_pass_run_summary": visible_run_summary,
            "sanitized_fail_to_pass_stdout_tail": "not_included_in_tracked_visible_summary",
            "fail_to_pass_command_fingerprint": sha256_text("\n".join(visible_tests)),
        },
        "visible_pass_to_pass_regression_evidence": {
            "visible_pass_to_pass_scope_id": f"{candidate['task_id']}::{scope_tag}_visible_p2p_not_materialized",
            "visible_pass_to_pass_test_names": [],
            "visible_pass_to_pass_outcomes": [],
            "sanitized_pass_to_pass_stdout_tail": "not_included_in_tracked_visible_summary",
            "pass_to_pass_scope_summary": (
                "not_separately_materialized; visible test outcome evidence is reported in "
                "visible_fail_to_pass_test_evidence"
            ),
            "visible_tests_rule_decision": visible_tests_decision,
        },
        "broader_visible_tool_diagnostics": {
            "lint_or_static_diagnostic_summary": tool_summary.get("static_analysis", f"not_run_in_{scope_tag}"),
            "syntax_import_check": tool_summary.get("syntax_import_check", f"not_run_in_{scope_tag}"),
            "sanitized_test_log_observations": [tool_summary],
            "environment_diagnostic_summary": f"not_recorded_in_{scope_tag}",
            "diagnostic_tool_versions": {},
        },
        "deterministic_visible_merge_gate_summary": merge_gate,
    }


def _sanitized_visible_test_results(record: dict[str, Any]) -> list[dict[str, str]]:
    results = []
    for item in record.get("test_results") or []:
        results.append({
            "test_name": str(item.get("test_name") or "unknown_test"),
            "outcome": str(item.get("outcome") or "unknown"),
        })
    if results:
        return results
    summary = record.get("visible_run_summary") or {}
    outcome = str(summary.get("outcome") or record.get("run_status") or "unknown")
    return [{"test_name": "visible_test_summary", "outcome": outcome}]


def _sanitized_visible_run_summary(record: dict[str, Any], test_results: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "run_status": str(record.get("run_status") or "unknown"),
        "timeout": bool(record.get("timeout")),
        "exit_code": record.get("exit_code"),
        "elapsed_seconds": record.get("elapsed_seconds"),
        "test_count": len(test_results),
        "outcome_counts": _counts(item["outcome"] for item in test_results),
    }


def _sanitized_visible_tool_summary(record: dict[str, Any] | None) -> dict[str, Any]:
    if not record:
        return {}
    summary = record.get("visible_tool_summary") or {}
    return {
        "patch_applies": summary.get("patch_applies"),
        "static_analysis": summary.get("static_analysis"),
        "syntax_import_check": summary.get("syntax_import_check"),
        "visible_test_outcome_counts": summary.get("visible_test_outcome_counts") or {},
        "visible_test_run_status": summary.get("visible_test_run_status"),
        "summary_status": record.get("summary_status"),
    }


def _sanitized_tool_decision(record: dict[str, Any] | None) -> dict[str, Any]:
    if not record:
        return {}
    return {
        "condition": record.get("condition"),
        "decision": record.get("decision"),
        "confidence": record.get("confidence"),
        "primary_reason": record.get("primary_reason"),
        "evidence_used": record.get("evidence_used") or [],
        "risk_flags": record.get("risk_flags") or [],
        "human_review_needed": record.get("human_review_needed"),
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


def _deterministic_visible_merge_gate(
    patch_apply_status: str,
    f2p_outcomes: list[str],
    scope_tag: str,
    *,
    tool_decision: dict[str, Any] | None = None,
) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for outcome in f2p_outcomes:
        counts[outcome] = counts.get(outcome, 0) + 1
    contradictions: list[str] = []
    decision = "escalate"
    reasons = [f"{scope_tag}_visible_evidence_is_incomplete"]
    if patch_apply_status == "failed":
        contradictions.append("patch_apply_failed")
        decision = "reject"
        reasons = ["visible_patch_apply_status_failed"]
    elif tool_decision and tool_decision.get("decision") in {"accept", "reject", "escalate"}:
        decision = str(tool_decision["decision"])
        reasons = [str(tool_decision.get("primary_reason") or "visible_tool_only_decision")]
        if decision == "reject":
            contradictions.append("visible_tool_summary_rejected")
    elif f2p_outcomes and all(outcome == "passed" for outcome in f2p_outcomes):
        decision = "accept"
        reasons = ["all_visible_tests_passed_and_no_visible_contradiction"]
    elif any(outcome in {"failed", "error", "timeout"} for outcome in f2p_outcomes):
        decision = "reject"
        contradictions.append("visible_test_failure")
        reasons = ["visible_test_outcomes_include_failure"]
    return {
        "visible_tool_summary_counts": counts,
        "visible_tool_summary_contradictions": contradictions,
        "rule_based_visible_merge_gate_decision": decision,
        "rule_based_visible_merge_gate_reasons": reasons,
        "source_decision": tool_decision or {},
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
    if summary.get("rule_based_visible_merge_gate_decision") == "accept":
        return _decision(
            "accept",
            0.9,
            "Visible deterministic merge-gate summary accepted the candidate.",
            ["deterministic_visible_merge_gate_summary.rule_based_visible_merge_gate_decision"],
            [],
            [],
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
        raise SystemExit("EVP-8 DeepSeek/Qwen check-only requires structural preflight readiness.")
    if not args.allow_missing_credentials and not preflight["ready_for_user_execute_command"]:
        raise SystemExit("EVP-8 DeepSeek/Qwen check-only requires strict local preflight unless --allow-missing-credentials is set.")
    spec = read_json(resolve(config["protocol_spec"]))
    template = resolve(config["prompt_template"]).read_text(encoding="utf-8")
    scope_config = config.get(args.run_scope) or {}
    expected_packet_count = int(scope_config.get("planned_calls_per_model") or 0)
    expected_candidate_count = int(scope_config.get("candidate_count") or 0)
    packets = build_packets(config, args.run_scope)
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
    schema_outputs = [schema_visible_rule_output(packet) for packet in packets]
    check_only_status = (
        "passed"
        if len(packets) == expected_packet_count
        and len({packet["anonymous_candidate_id"] for packet in packets}) == expected_candidate_count
        and not boundary_errors
        and not schema_errors
        else "failed"
    )
    summary = {
        "mode": "check_only",
        "cohort_id": "EVP-8",
        "protocol_id": spec.get("protocol_id"),
        "candidate_set_id": preflight.get("candidate_set_id"),
        "config": display_path(args.config),
        "run_scope": args.run_scope,
        "evidence_source_mode": config.get("evidence_source_mode", "placeholder_not_run"),
        "selected_candidate_ids": sorted({packet["anonymous_candidate_id"] for packet in packets}),
        "candidate_count": len({packet["anonymous_candidate_id"] for packet in packets}),
        "selection_policy": (
            "deterministic_project_frequency_stratified_first_candidate_per_top_project"
            if args.run_scope == "smoke"
            else "all_frozen_evp8_candidate_set_records"
        ),
        "model_visible_levels": list(MODEL_VISIBLE_LEVELS),
        "expected_packet_count": expected_packet_count,
        "packet_count": len(packets),
        "prompt_count": len(prompt_hashes),
        "prompt_hashes_unique_count": len(set(prompt_hashes)),
        "prompt_chars_min": min(prompt_chars) if prompt_chars else 0,
        "prompt_chars_max": max(prompt_chars) if prompt_chars else 0,
        "prompt_text_stored": False,
        "raw_outputs_generated": False,
        "api_call_attempted": False,
        "local_api_config_read": False,
        "api_key_values_printed": False,
        "local_config_content_stored_in_tracked_summary": False,
        "packet_dry_run_status": check_only_status,
        "schema_dry_run_status": check_only_status,
        "deterministic_tool_baseline_dry_run_status": check_only_status,
        "planned_packet_skeleton_count": len(packets),
        "schema_dry_run_record_count": len(packets),
        "planned_baseline_record_count": len(packets),
        "valid_schema_count": len(packets) - len(schema_errors),
        "invalid_schema_count": len(schema_errors),
        "boundary_error_count": len(boundary_errors),
        "boundary_errors": sorted(set(boundary_errors)),
        "schema_error_count": len(schema_errors),
        "schema_error_counts": _counts(schema_errors),
        "schema_rule_decision_counts": _counts(output["decision"] for output in schema_outputs),
        "schema_rule_decision_counts_by_evidence_level": _schema_rule_counts_by_level(packets, schema_outputs),
        "deterministic_visible_merge_gate_counts": _deterministic_merge_gate_counts(packets),
        "check_only_status": check_only_status,
        "preflight_structural_ready": preflight["structural_ready"],
        "preflight_ready_for_user_execute_command": preflight["ready_for_user_execute_command"],
        "next_step": f"Wait for explicit user command before running --execute {args.run_scope}.",
    }
    default_summary_out = (
        DEFAULT_SMOKE_CHECK_SUMMARY_OUT if args.run_scope == "smoke" else DEFAULT_FULL_CHECK_SUMMARY_OUT
    )
    write_json(args.summary_out or default_summary_out, summary)
    if summary["check_only_status"] != "passed":
        raise SystemExit(f"EVP-8 {args.run_scope} check-only failed: {summary}")
    return summary


def execute(args: argparse.Namespace) -> dict[str, Any]:
    if args.config.name.endswith(".example.json"):
        raise SystemExit("Refusing to execute with tracked example config. Use ignored local config.")
    config = read_json(args.config)
    preflight = preflight_module.preflight(args.config)
    if not preflight["ready_for_user_execute_command"]:
        raise SystemExit("EVP-8 DeepSeek/Qwen execute requires strict preflight readiness.")
    model_config = _model_config(config, args.model_id)
    if model_config is None:
        raise SystemExit(f"--model-id must match one configured model: {args.model_id}")
    scope_config = config.get(args.run_scope) or {}
    output_dir = resolve(scope_config["output_dir"]) / safe_name(str(model_config["model_id"]))
    raw_out = args.raw_out or output_dir / "raw_responses.jsonl"
    summary_out = args.summary_out or DEFAULT_EXEC_SUMMARY_DIR / f"evp8_{safe_name(str(model_config['model_id']))}_{args.run_scope}_summary.json"
    if config.get("overwrite_policy") == "refuse_if_output_exists":
        if summary_out.exists():
            raise SystemExit(f"Refusing to overwrite existing {args.run_scope} summary: {display_path(summary_out)}")
        if raw_out.exists() and not args.resume:
            raise SystemExit(
                f"Refusing to overwrite existing {args.run_scope} raw output: {display_path(raw_out)}. "
                "Use --resume only when this is an interrupted run without a tracked summary."
            )

    load_env_file(str(resolve(config.get("env", ".env"))))
    spec = read_json(resolve(config["protocol_spec"]))
    template = resolve(config["prompt_template"]).read_text(encoding="utf-8")
    packets = build_packets(config, args.run_scope)
    completed_packet_ids, parsed_records = load_resume_state(
        raw_out=raw_out,
        packets=packets,
        spec=spec,
        model_config=model_config,
        resume=args.resume,
    )
    resumed_raw_record_count = len(completed_packet_ids)
    raw_out.parent.mkdir(parents=True, exist_ok=True)
    raw_mode = "a" if args.resume and raw_out.exists() else "x"
    with raw_out.open(raw_mode, encoding="utf-8") as raw_handle:
        remaining_packets = [
            packet for packet in packets if packet["evidence_packet_id"] not in completed_packet_ids
        ]
        if args.concurrency == 1:
            for packet in remaining_packets:
                raw_record = fetch_raw_record(packet, template, config, model_config)
                append_jsonl_record(raw_handle, raw_record)
                parsed_records.append(parsed_record_from_raw(raw_record, spec, model_config))
        else:
            for batch_start in range(0, len(remaining_packets), args.concurrency):
                batch = remaining_packets[batch_start : batch_start + args.concurrency]
                with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
                    raw_records = list(
                        executor.map(
                            lambda packet: fetch_raw_record(packet, template, config, model_config),
                            batch,
                        )
                    )
                for raw_record in raw_records:
                    append_jsonl_record(raw_handle, raw_record)
                    parsed_records.append(parsed_record_from_raw(raw_record, spec, model_config))

    cost = aggregate_cost(parsed_records)
    parse_valid_count = sum(1 for record in parsed_records if record["parse_status"] == "valid")
    summary = {
        "mode": "executed",
        "cohort_id": "EVP-8",
        "protocol_id": spec.get("protocol_id"),
        "candidate_set_id": preflight.get("candidate_set_id"),
        "config": display_path(args.config),
        "run_scope": args.run_scope,
        "evidence_source_mode": config.get("evidence_source_mode", "placeholder_not_run"),
        "configured_model_id": model_config["model_id"],
        "request_model_id": model_config["request_model_id"],
        "provider_route": model_config["provider_route"],
        "request_reasoning": model_config.get("reasoning"),
        "request_include_reasoning": model_config.get("include_reasoning"),
        "request_thinking": model_config.get("thinking"),
        "request_response_format": model_config.get("response_format"),
        "raw_responses_out": display_path(raw_out),
        "raw_response_text_stored_in_tracked_summary": False,
        "review_count": len(parsed_records),
        "concurrency": args.concurrency,
        "resume_enabled": bool(args.resume),
        "resumed_raw_record_count": resumed_raw_record_count,
        "new_api_call_count": len(parsed_records) - resumed_raw_record_count,
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
        "run_gate": "passed"
        if parse_valid_count == len(parsed_records) and cost["unknown_cost_record_count"] == 0
        else "blocked",
    }
    if args.run_scope == "smoke":
        summary["smoke_gate"] = summary["run_gate"]
    else:
        summary["first_batch_full_gate"] = summary["run_gate"]
    write_json(summary_out, summary)
    if summary["run_gate"] != "passed":
        raise SystemExit(f"EVP-8 {args.run_scope} gate blocked after writing outputs: {summary['run_gate']}")
    return summary


def fetch_raw_record(
    packet: dict[str, Any],
    template: str,
    config: dict[str, Any],
    model_config: dict[str, Any],
) -> dict[str, Any]:
    prompt = render_prompt(template, packet)
    findings = prompt_module._boundary_findings(prompt)  # noqa: SLF001
    if findings:
        raise RuntimeError(f"prompt boundary failed for {packet['evidence_packet_id']}: {findings}")
    response = _client(str(model_config["provider_route"])).chat_completion(
        model=str(model_config["request_model_id"]),
        prompt=prompt,
        temperature=float(config.get("temperature", 0.0)),
        max_tokens=int(config.get("max_output_tokens", 1024)),
        reasoning=model_config.get("reasoning"),
        include_reasoning=model_config.get("include_reasoning"),
        thinking=model_config.get("thinking"),
        response_format=model_config.get("response_format"),
    )
    return {
        "evidence_packet_id": packet["evidence_packet_id"],
        "anonymous_candidate_id": packet["anonymous_candidate_id"],
        "evidence_level": packet["evidence_level"],
        "requested_model_id": model_config["request_model_id"],
        "configured_model_id": model_config["model_id"],
        "actual_model_id": response.get("model"),
        "provider_route": model_config["provider_route"],
        "request_reasoning": model_config.get("reasoning"),
        "request_include_reasoning": model_config.get("include_reasoning"),
        "request_thinking": model_config.get("thinking"),
        "request_response_format": model_config.get("response_format"),
        "raw_response_text": response_text(response),
        "response": response,
        "run_date_utc": datetime.now(timezone.utc).isoformat(),
    }


def load_resume_state(
    *,
    raw_out: Path,
    packets: list[dict[str, Any]],
    spec: dict[str, Any],
    model_config: dict[str, Any],
    resume: bool,
) -> tuple[set[str], list[dict[str, Any]]]:
    if not raw_out.exists():
        return set(), []
    if not resume:
        return set(), []
    raw_records = read_jsonl(raw_out)
    expected_ids = [str(packet["evidence_packet_id"]) for packet in packets]
    existing_ids = [str(record.get("evidence_packet_id")) for record in raw_records]
    if existing_ids != expected_ids[: len(existing_ids)]:
        raise SystemExit(
            f"Cannot resume {display_path(raw_out)}: existing raw records are not a prefix of the planned packet order."
        )
    packet_by_id = {str(packet["evidence_packet_id"]): packet for packet in packets}
    parsed_records: list[dict[str, Any]] = []
    completed: set[str] = set()
    for raw_record in raw_records:
        packet_id = str(raw_record["evidence_packet_id"])
        if packet_id in completed:
            raise SystemExit(f"Cannot resume {display_path(raw_out)}: duplicate raw record {packet_id}.")
        packet = packet_by_id[packet_id]
        if raw_record.get("configured_model_id") != model_config["model_id"]:
            raise SystemExit(f"Cannot resume {display_path(raw_out)}: configured model mismatch for {packet_id}.")
        if raw_record.get("provider_route") != model_config["provider_route"]:
            raise SystemExit(f"Cannot resume {display_path(raw_out)}: provider route mismatch for {packet_id}.")
        if raw_record.get("anonymous_candidate_id") != packet["anonymous_candidate_id"]:
            raise SystemExit(f"Cannot resume {display_path(raw_out)}: candidate mismatch for {packet_id}.")
        if raw_record.get("evidence_level") != packet["evidence_level"]:
            raise SystemExit(f"Cannot resume {display_path(raw_out)}: evidence-level mismatch for {packet_id}.")
        completed.add(packet_id)
        parsed_records.append(parsed_record_from_raw(raw_record, spec, model_config))
    return completed, parsed_records


def parsed_record_from_raw(
    raw_record: dict[str, Any],
    spec: dict[str, Any],
    model_config: dict[str, Any],
) -> dict[str, Any]:
    response = raw_record.get("response") if isinstance(raw_record.get("response"), dict) else {}
    raw_text = str(raw_record.get("raw_response_text") or "")
    parsed, invalid_reason = _parse_response(raw_text, spec)
    cost = cost_summary(response=response, model_config=model_config)
    return {
        "evidence_packet_id": raw_record["evidence_packet_id"],
        "anonymous_candidate_id": raw_record["anonymous_candidate_id"],
        "evidence_level": raw_record["evidence_level"],
        "parse_status": "valid" if invalid_reason is None else "invalid",
        "invalid_reason": invalid_reason,
        "decision": parsed.get("decision") if parsed else None,
        "risk_flags": parsed.get("risk_flags") if parsed else [],
        "human_review_needed": parsed.get("human_review_needed") if parsed else None,
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
            "cost_cny": None,
            "cost_currency": "USD",
            "cost_source": "provider_reported_usage_cost",
            "cost_observability": "provider_reported_cost",
        }
    if model_config.get("provider_route") == "deepseek_official" and model_config.get("request_model_id") == "deepseek-v4-pro":
        estimated = _estimate_deepseek_v4_pro_cost(usage)
        if estimated is not None:
            return {
                "usage": normalized_usage,
                "cost_usd": round(estimated["cost_usd"], 9),
                "cost_cny": None,
                "cost_currency": "USD",
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
    if model_config.get("provider_route") == "qwen_official" and model_config.get("request_model_id") == "qwen3.7-max":
        estimated = _estimate_qwen_3_7_max_cost_cny(usage)
        if estimated is not None:
            return {
                "usage": normalized_usage,
                "cost_usd": None,
                "cost_cny": round(estimated["cost_cny"], 9),
                "cost_currency": "CNY",
                "cost_source": "estimated_from_tokens_official_qwen_cny_pricing",
                "cost_observability": "estimated_from_provider_token_usage_and_official_cny_pricing",
                "cost_pricing": {
                    "source": QWEN_PRICING_SOURCE_URL,
                    "unit": "CNY per 1M tokens",
                    "model": "qwen3.7-max",
                    "rates": QWEN_3_7_MAX_CNY_PER_1M_TOKENS,
                    "pricing_tier": "0<Token<=1M",
                },
            }
    if normalized_usage:
        return {
            "usage": normalized_usage,
            "cost_usd": None,
            "cost_cny": None,
            "cost_currency": None,
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


def _estimate_qwen_3_7_max_cost_cny(usage: dict[str, Any]) -> dict[str, Any] | None:
    completion_tokens = _token_count(usage.get("completion_tokens"), usage.get("output_tokens"))
    prompt_tokens = _token_count(usage.get("prompt_tokens"), usage.get("input_tokens"))
    if completion_tokens is None and prompt_tokens is None:
        return None
    prompt_cost = 0.0
    if prompt_tokens is not None:
        prompt_cost = prompt_tokens * QWEN_3_7_MAX_CNY_PER_1M_TOKENS["input"] / 1_000_000
    completion_cost = 0.0
    if completion_tokens is not None:
        completion_cost = completion_tokens * QWEN_3_7_MAX_CNY_PER_1M_TOKENS["output"] / 1_000_000
    return {
        "cost_cny": prompt_cost + completion_cost,
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
        "cost_cny": None,
        "cost_currency": None,
        "cost_source": "unknown",
        "cost_observability": reason,
    }


def aggregate_cost(records: list[dict[str, Any]]) -> dict[str, Any]:
    total_usd = 0.0
    total_cny = 0.0
    unknown = 0
    sources: list[str] = []
    observability: list[str] = []
    currencies: list[str] = []
    for record in records:
        sources.append(str(record.get("cost_source") or "unknown"))
        observability.append(str(record.get("cost_observability") or "unknown"))
        currency = record.get("cost_currency")
        if currency:
            currencies.append(str(currency))
        cost_usd = record.get("cost_usd")
        cost_cny = record.get("cost_cny")
        if cost_usd is None and cost_cny is None:
            unknown += 1
        else:
            if cost_usd is not None:
                total_usd += float(cost_usd)
            if cost_cny is not None:
                total_cny += float(cost_cny)
    return {
        "total_cost_usd": round(total_usd, 9),
        "total_cost_cny": round(total_cny, 9),
        "unknown_cost_record_count": unknown,
        "cost_source_counts": _counts(sources),
        "cost_observability_counts": _counts(observability),
        "cost_currency_counts": _counts(currencies),
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


def _schema_rule_counts_by_level(
    packets: list[dict[str, Any]],
    outputs: list[dict[str, Any]],
) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {level: {} for level in MODEL_VISIBLE_LEVELS}
    for packet, output in zip(packets, outputs):
        level = str(packet["evidence_level"])
        decision = str(output.get("decision") or "missing")
        bucket = result.setdefault(level, {})
        bucket[decision] = bucket.get(decision, 0) + 1
    return {level: dict(sorted(counts.items())) for level, counts in sorted(result.items())}


def _deterministic_merge_gate_counts(packets: list[dict[str, Any]]) -> dict[str, int]:
    decisions: list[str] = []
    for packet in packets:
        fields = packet.get("visible_fields") or {}
        summary = fields.get("deterministic_visible_merge_gate_summary") or {}
        decisions.append(str(summary.get("rule_based_visible_merge_gate_decision") or "missing"))
    return _counts(decisions)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--run-scope", choices=("smoke", "full"), default="smoke")
    parser.add_argument("--model-id", help="Configured model id to execute, e.g. deepseek/deepseek-v4-pro.")
    parser.add_argument("--allow-missing-credentials", action="store_true")
    parser.add_argument("--summary-out", type=Path)
    parser.add_argument("--raw-out", type=Path)
    parser.add_argument("--resume", action="store_true", help="Resume an interrupted execute run from an existing raw JSONL prefix.")
    parser.add_argument("--concurrency", type=int, default=1, help="Ordered batch concurrency for execute mode.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    modes = sum(bool(value) for value in (args.check_only, args.execute))
    if modes != 1:
        raise SystemExit("Choose exactly one mode: --check-only or --execute.")
    if args.execute and not args.model_id:
        raise SystemExit("--execute requires --model-id.")
    if args.concurrency < 1:
        raise SystemExit("--concurrency must be >= 1.")
    summary = execute(args) if args.execute else check_only(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
