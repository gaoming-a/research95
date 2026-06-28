"""Run EVP-8 E6-no-verdict ablation for DeepSeek and Qwen.

This runner reuses the existing EVP-8 visible-evidence packet construction,
keeps only E6 packets, and removes the rule verdict fields from
``deterministic_visible_merge_gate_summary`` before rendering prompts.

The default mode is check-only. Real API calls require ``--execute`` and a
configured model id.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_evp8_prompt_manifest as prompt_module  # noqa: E402
import run_evp8_deepseek_qwen_smoke as base_runner  # noqa: E402
from cross_review.env import load_env_file  # noqa: E402


DEFAULT_CONFIG = REPO_ROOT / "configs" / "evp8_e6_no_verdict_ablation.local.json"
DEFAULT_CHECK_ONLY_OUT = REPO_ROOT / "data" / "protocols" / "evp8_e6_no_verdict_ablation_check_only_v0_1.json"
DEFAULT_EXEC_SUMMARY_DIR = REPO_ROOT / "data" / "reviews"
NO_VERDICT_LEVEL = "E6"
REMOVED_VERDICT_FIELDS = (
    "rule_based_visible_merge_gate_decision",
    "rule_based_visible_merge_gate_reasons",
    "source_decision",
)
FORBIDDEN_PACKET_MARKERS = base_runner.FORBIDDEN_MARKERS + REMOVED_VERDICT_FIELDS


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{base_runner.display_path(path)} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ablation_packets(config: dict[str, Any], run_scope: str) -> list[dict[str, Any]]:
    packets = [
        strip_verdict_fields(packet)
        for packet in base_runner.build_packets(config, run_scope)
        if packet.get("evidence_level") == NO_VERDICT_LEVEL
    ]
    packet_suffix = str((config.get(run_scope) or {}).get("packet_suffix") or "evp8_e6_no_verdict")
    for packet in packets:
        packet["ablation_condition"] = "E6-no-verdict"
        packet["evidence_level_name"] = "deterministic_visible_tool_summary_without_verdict"
        packet["evidence_packet_id"] = (
            f"{packet['anonymous_candidate_id']}__E6_NO_VERDICT__{packet_suffix}"
        )
    return packets


def strip_verdict_fields(packet: dict[str, Any]) -> dict[str, Any]:
    stripped = copy.deepcopy(packet)
    fields = stripped.get("visible_fields") or {}
    summary = fields.get("deterministic_visible_merge_gate_summary")
    if isinstance(summary, dict):
        for key in REMOVED_VERDICT_FIELDS:
            summary.pop(key, None)
    findings = packet_leakage_findings(stripped)
    if findings:
        raise ValueError(f"forbidden no-verdict fields in {stripped.get('evidence_packet_id')}: {findings}")
    return stripped


def packet_leakage_findings(value: Any) -> list[str]:
    serialized = json.dumps(value, ensure_ascii=False).lower()
    return sorted({marker for marker in FORBIDDEN_PACKET_MARKERS if marker.lower() in serialized})


def schema_rule_output(packet: dict[str, Any]) -> dict[str, Any]:
    fields = packet.get("visible_fields") or {}
    static = fields.get("patch_application_static_status") or {}
    summary = fields.get("deterministic_visible_merge_gate_summary") or {}
    contradictions = list(summary.get("visible_tool_summary_contradictions") or [])
    counts = summary.get("visible_tool_summary_counts") or {}
    if static.get("patch_apply_status") == "failed":
        return base_runner._decision(
            "reject",
            1.0,
            "Visible patch-apply status failed.",
            ["patch_application_static_status.patch_apply_status"],
            ["patch_apply_failed"],
            ["patch_apply_failed"],
        )
    if contradictions:
        return base_runner._decision(
            "reject",
            0.8,
            "Visible no-verdict summary contains contradictions.",
            ["deterministic_visible_merge_gate_summary.visible_tool_summary_contradictions"],
            ["visible_test_failure"],
            contradictions,
        )
    if counts and set(counts) == {"passed"}:
        return base_runner._decision(
            "accept",
            0.7,
            "Visible no-verdict summary reports only passed visible tests.",
            ["deterministic_visible_merge_gate_summary.visible_tool_summary_counts"],
            [],
            [],
        )
    return base_runner._decision(
        "escalate",
        0.0,
        "No-verdict E6 packet does not provide enough direct evidence for a safe decision.",
        list(fields.keys()),
        ["insufficient_evidence"],
        ["rule_verdict_removed"],
    )


def check_only(args: argparse.Namespace) -> dict[str, Any]:
    config = read_json(args.config)
    spec = read_json(base_runner.resolve(config["protocol_spec"]))
    template = base_runner.resolve(config["prompt_template"]).read_text(encoding="utf-8")
    scope_config = config.get(args.run_scope) or {}
    expected_candidate_count = int(scope_config.get("candidate_count") or 0)
    expected_packet_count = int(scope_config.get("planned_calls_per_model") or 0)
    packets = ablation_packets(config, args.run_scope)
    prompt_hashes: list[str] = []
    prompt_chars: list[int] = []
    boundary_errors: list[str] = []
    schema_errors: list[str] = []
    packet_leakages: list[str] = []
    for packet in packets:
        packet_leakages.extend(packet_leakage_findings(packet))
        prompt = base_runner.render_prompt(template, packet)
        prompt_hashes.append(base_runner.sha256_text(prompt))
        prompt_chars.append(len(prompt))
        boundary_errors.extend(prompt_module._boundary_findings(prompt))  # noqa: SLF001
        schema_error = base_runner.validate_output_schema(schema_rule_output(packet), spec.get("output_schema") or {})
        if schema_error:
            schema_errors.append(schema_error)
    candidate_count = len({packet["anonymous_candidate_id"] for packet in packets})
    checks = [
        _check("candidate_count", candidate_count == expected_candidate_count, candidate_count),
        _check("packet_count", len(packets) == expected_packet_count, len(packets)),
        _check("only_e6_packets", {packet["evidence_level"] for packet in packets} == {NO_VERDICT_LEVEL}, sorted({packet["evidence_level"] for packet in packets})),
        _check("removed_rule_based_visible_merge_gate_decision", not any("rule_based_visible_merge_gate_decision" in json.dumps(packet) for packet in packets), True),
        _check("removed_rule_based_visible_merge_gate_reasons", not any("rule_based_visible_merge_gate_reasons" in json.dumps(packet) for packet in packets), True),
        _check("removed_source_decision", not any("source_decision" in json.dumps(packet) for packet in packets), True),
        _check("packet_forbidden_marker_count", not packet_leakages, sorted(set(packet_leakages))),
        _check("prompt_boundary_error_count", not boundary_errors, sorted(set(boundary_errors))),
        _check("schema_error_count", not schema_errors, base_runner._counts(schema_errors)),
        _check("api_call_not_attempted", True, False),
        _check("raw_outputs_not_generated", True, False),
        _check("prompt_text_not_stored", True, False),
    ]
    status = "passed" if all(check["passed"] for check in checks) else "failed"
    summary = {
        "mode": "check_only",
        "analysis_id": "evp8_e6_no_verdict_ablation_check_only_v0_1",
        "cohort_id": "EVP-8",
        "ablation_condition": "E6-no-verdict",
        "config": base_runner.display_path(args.config),
        "run_scope": args.run_scope,
        "candidate_count": candidate_count,
        "packet_count": len(packets),
        "expected_packet_count": expected_packet_count,
        "model_visible_levels": [NO_VERDICT_LEVEL],
        "removed_verdict_fields": list(REMOVED_VERDICT_FIELDS),
        "prompt_count": len(prompt_hashes),
        "prompt_hashes_unique_count": len(set(prompt_hashes)),
        "prompt_chars_min": min(prompt_chars) if prompt_chars else 0,
        "prompt_chars_max": max(prompt_chars) if prompt_chars else 0,
        "schema_rule_decision_counts": base_runner._counts(schema_rule_output(packet)["decision"] for packet in packets),
        "api_call_attempted": False,
        "raw_outputs_generated": False,
        "prompt_text_stored": False,
        "api_key_values_printed": False,
        "check_only_status": status,
        "checks": checks,
    }
    write_json(args.summary_out or DEFAULT_CHECK_ONLY_OUT, summary)
    if status != "passed":
        raise SystemExit(f"E6-no-verdict check-only failed: {summary}")
    return summary


def execute(args: argparse.Namespace) -> dict[str, Any]:
    if args.config.name.endswith(".example.json"):
        raise SystemExit("Refusing to execute with tracked example config. Use ignored local config.")
    config = read_json(args.config)
    model_config = base_runner._model_config(config, args.model_id)
    if model_config is None:
        raise SystemExit(f"--model-id must match one configured model: {args.model_id}")
    load_env_file(str(base_runner.resolve(config.get("env", ".env"))))
    spec = read_json(base_runner.resolve(config["protocol_spec"]))
    template = base_runner.resolve(config["prompt_template"]).read_text(encoding="utf-8")
    packets = ablation_packets(config, args.run_scope)
    scope_config = config.get(args.run_scope) or {}
    output_dir = base_runner.resolve(scope_config["output_dir"]) / base_runner.safe_name(str(model_config["model_id"]))
    raw_out = args.raw_out or output_dir / "raw_responses.jsonl"
    summary_out = (
        args.summary_out
        or DEFAULT_EXEC_SUMMARY_DIR
        / f"evp8_e6_no_verdict_{base_runner.safe_name(str(model_config['model_id']))}_{args.run_scope}_summary.json"
    )
    if config.get("overwrite_policy") == "refuse_if_output_exists":
        if summary_out.exists():
            raise SystemExit(f"Refusing to overwrite summary: {base_runner.display_path(summary_out)}")
        if raw_out.exists() and not args.resume:
            raise SystemExit(
                f"Refusing to overwrite raw output: {base_runner.display_path(raw_out)}. "
                "Use --resume only for interrupted runs."
            )
    completed_packet_ids, parsed_records = base_runner.load_resume_state(
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
        if args.concurrency != 1:
            raise SystemExit("E6-no-verdict runner currently requires --concurrency 1 for ordered guarded execution.")
        for packet in remaining_packets:
            raw_record = base_runner.fetch_raw_record(packet, template, config, model_config)
            base_runner.append_jsonl_record(raw_handle, raw_record)
            parsed_records.append(base_runner.parsed_record_from_raw(raw_record, spec, model_config))
    cost = base_runner.aggregate_cost(parsed_records)
    parse_valid_count = sum(1 for record in parsed_records if record["parse_status"] == "valid")
    summary = {
        "mode": "executed",
        "cohort_id": "EVP-8",
        "ablation_condition": "E6-no-verdict",
        "config": base_runner.display_path(args.config),
        "run_scope": args.run_scope,
        "configured_model_id": model_config["model_id"],
        "request_model_id": model_config["request_model_id"],
        "provider_route": model_config["provider_route"],
        "request_response_format": model_config.get("response_format"),
        "request_thinking": model_config.get("thinking"),
        "raw_responses_out": base_runner.display_path(raw_out),
        "raw_response_text_stored_in_tracked_summary": False,
        "review_count": len(parsed_records),
        "new_api_call_count": len(parsed_records) - resumed_raw_record_count,
        "resume_enabled": bool(args.resume),
        "resumed_raw_record_count": resumed_raw_record_count,
        "parse_valid_count": parse_valid_count,
        "invalid_parse_count": len(parsed_records) - parse_valid_count,
        "decision_counts": base_runner._counts(record["decision"] for record in parsed_records),
        "review_count_by_evidence_level": base_runner._level_counts(parsed_records),
        "decision_counts_by_evidence_level": base_runner._counts_by_evidence_level(parsed_records, "decision"),
        "actual_model_id_counts": base_runner._counts(record["actual_model_id"] or "missing" for record in parsed_records),
        "provider_route_counts": base_runner._counts(record["provider_route"] for record in parsed_records),
        "api_call_attempted": True,
        "raw_outputs_generated": True,
        "prompt_text_stored": False,
        "api_key_values_printed": False,
        "removed_verdict_fields": list(REMOVED_VERDICT_FIELDS),
        "cost_summary": cost,
        "usage_cost_gate": "passed" if cost["unknown_cost_record_count"] == 0 else "blocked",
        "run_gate": "passed"
        if parse_valid_count == len(parsed_records) and cost["unknown_cost_record_count"] == 0
        else "blocked",
    }
    if args.run_scope == "smoke":
        summary["smoke_gate"] = summary["run_gate"]
    else:
        summary["full_gate"] = summary["run_gate"]
    write_json(summary_out, summary)
    if summary["run_gate"] != "passed":
        raise SystemExit(f"E6-no-verdict run gate blocked: {summary['run_gate']}")
    return summary


def _check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--run-scope", choices=("smoke", "full"), default="full")
    parser.add_argument("--model-id")
    parser.add_argument("--summary-out", type=Path)
    parser.add_argument("--raw-out", type=Path)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--concurrency", type=int, default=1)
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
