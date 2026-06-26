"""Audit EVP-8 DeepSeek/Qwen first-batch full-run summaries without raw outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = REPO_ROOT / "data" / "protocols" / "evp8_deepseek_qwen_first_batch_full_run_packet_v0_1.json"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "protocols" / "evp8_deepseek_qwen_first_batch_full_result_audit_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_deepseek_qwen_first_batch_full_result_audit_v0_1.md"
EXPECTED_REVIEW_COUNT = 686
EXPECTED_LEVELS = ("E0", "E1", "E2", "E3", "E4", "E5", "E6")
EXPECTED_REVIEW_COUNT_PER_LEVEL = 98


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{display_path(path)} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def display_path(path: Path) -> str:
    absolute = path if path.is_absolute() else REPO_ROOT / path
    try:
        return absolute.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(absolute)


def resolve(path_value: str) -> Path:
    path = Path(path_value)
    return path if path.is_absolute() else REPO_ROOT / path


def raw_path_is_ignored_boundary(path_value: str) -> bool:
    path = Path(path_value)
    return bool(path.parts) and path.parts[0] == "outputs"


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def audit_summary(packet: dict[str, Any], command_record: dict[str, Any], summary: dict[str, Any] | None) -> dict[str, Any]:
    model_id = command_record["model_id"]
    request_model_id = command_record.get("request_model_id")
    provider_route = command_record.get("provider_route")
    outputs = command_record["outputs"]
    summary_path = outputs["tracked_summary"]
    raw_path = outputs["raw_responses"]
    if summary is None:
        return {
            "model_id": model_id,
            "summary_path": summary_path,
            "raw_response_path": raw_path,
            "summary_present": False,
            "status": "waiting_for_execution",
            "checks": [
                check("raw_path_under_outputs", raw_path_is_ignored_boundary(raw_path), raw_path),
            ],
        }
    expected_request_counts = {str(request_model_id): EXPECTED_REVIEW_COUNT}
    expected_provider_counts = {str(provider_route): EXPECTED_REVIEW_COUNT}
    request_counts = summary.get("request_model_id_counts") or {}
    actual_counts = summary.get("actual_model_id_counts") or {}
    provider_counts = summary.get("provider_route_counts") or {}
    expected_level_counts = {level: EXPECTED_REVIEW_COUNT_PER_LEVEL for level in EXPECTED_LEVELS}
    expected_invalid_level_counts = {level: 0 for level in EXPECTED_LEVELS}
    review_counts_by_level = summary.get("review_count_by_evidence_level") or {}
    parse_valid_counts_by_level = summary.get("parse_valid_count_by_evidence_level") or {}
    invalid_parse_counts_by_level = summary.get("invalid_parse_count_by_evidence_level") or {}
    decision_counts_by_level = summary.get("decision_counts_by_evidence_level") or {}
    decision_count_totals_by_level = {
        level: _sum_count_values(decision_counts_by_level.get(level) or {}) for level in EXPECTED_LEVELS
    }
    cost_summary = summary.get("cost_summary") or {}
    checks = [
        check("mode_executed", summary.get("mode") == "executed", summary.get("mode")),
        check("run_scope_full", summary.get("run_scope") == "full", summary.get("run_scope")),
        check("api_call_attempted_true_for_executed_summary", summary.get("api_call_attempted") is True, summary.get("api_call_attempted")),
        check("protocol_id", summary.get("protocol_id") == packet.get("protocol_id"), summary.get("protocol_id")),
        check("candidate_set_id", summary.get("candidate_set_id") == packet.get("candidate_set_id"), summary.get("candidate_set_id")),
        check("request_model_id", summary.get("request_model_id") == request_model_id, summary.get("request_model_id")),
        check("provider_route", summary.get("provider_route") == provider_route, summary.get("provider_route")),
        check("request_model_id_counts", request_counts == expected_request_counts, request_counts),
        check("provider_route_counts", provider_counts == expected_provider_counts, provider_counts),
        check("actual_model_id_count_total", sum(int(value) for value in actual_counts.values()) == EXPECTED_REVIEW_COUNT, actual_counts),
        check("actual_model_id_missing_count", summary.get("actual_model_id_missing_count") == 0, summary.get("actual_model_id_missing_count")),
        check("actual_model_id_counts_no_missing", "missing" not in actual_counts, actual_counts),
        check("review_count", summary.get("review_count") == EXPECTED_REVIEW_COUNT, summary.get("review_count")),
        check("parse_valid_count", summary.get("parse_valid_count") == EXPECTED_REVIEW_COUNT, summary.get("parse_valid_count")),
        check("invalid_parse_count", summary.get("invalid_parse_count") == 0, summary.get("invalid_parse_count")),
        check("review_count_by_evidence_level", review_counts_by_level == expected_level_counts, review_counts_by_level),
        check("parse_valid_count_by_evidence_level", parse_valid_counts_by_level == expected_level_counts, parse_valid_counts_by_level),
        check("invalid_parse_count_by_evidence_level", invalid_parse_counts_by_level == expected_invalid_level_counts, invalid_parse_counts_by_level),
        check("decision_counts_by_evidence_level_levels", sorted(decision_counts_by_level) == list(EXPECTED_LEVELS), sorted(decision_counts_by_level)),
        check("decision_counts_by_evidence_level_totals", decision_count_totals_by_level == expected_level_counts, decision_count_totals_by_level),
        check("run_gate", summary.get("run_gate") == "passed", summary.get("run_gate")),
        check("first_batch_full_gate", summary.get("first_batch_full_gate") == "passed", summary.get("first_batch_full_gate")),
        check("usage_cost_gate", summary.get("usage_cost_gate") == "passed", summary.get("usage_cost_gate")),
        check("unknown_cost_record_count", cost_summary.get("unknown_cost_record_count") == 0, cost_summary.get("unknown_cost_record_count")),
        check("configured_model_id", summary.get("configured_model_id") == model_id, summary.get("configured_model_id")),
        check("raw_responses_out_matches_packet", summary.get("raw_responses_out") == raw_path, summary.get("raw_responses_out")),
        check("raw_response_text_not_stored_in_summary", summary.get("raw_response_text_stored_in_tracked_summary") is False, summary.get("raw_response_text_stored_in_tracked_summary")),
        check("prompt_text_not_stored_in_summary", summary.get("prompt_text_stored") is False, summary.get("prompt_text_stored")),
        check("raw_outputs_generated_flag", summary.get("raw_outputs_generated") is True, summary.get("raw_outputs_generated")),
        check("raw_path_under_outputs", raw_path_is_ignored_boundary(raw_path), raw_path),
    ]
    return {
        "model_id": model_id,
        "summary_path": summary_path,
        "raw_response_path": raw_path,
        "summary_present": True,
        "status": "passed" if all(item["passed"] for item in checks) else "failed",
        "decision_counts_by_evidence_level": decision_counts_by_level,
        "checks": checks,
    }


def _sum_count_values(counts: dict[str, Any]) -> int:
    total = 0
    for value in counts.values():
        try:
            total += int(value)
        except (TypeError, ValueError):
            continue
    return total


def build_audit(packet_path: Path) -> dict[str, Any]:
    packet = read_json(packet_path)
    if packet is None:
        raise FileNotFoundError(display_path(packet_path))
    command_records = packet.get("execute_commands_after_explicit_user_authorization") or []
    model_audits = [
        audit_summary(packet, command_record, read_json(resolve(command_record["outputs"]["tracked_summary"])))
        for command_record in command_records
    ]
    present = [item for item in model_audits if item["summary_present"]]
    qwen = next((item for item in model_audits if item["model_id"] == "qwen/qwen3.7-max"), None)
    deepseek = next((item for item in model_audits if item["model_id"] == "deepseek/deepseek-v4-pro"), None)
    qwen_first_allowed = packet.get("execution_order_policy") == "qwen_first_no_deepseek_dependency"
    order_checks = [
        check("packet_ready", packet.get("packet_status") == "ready", packet.get("packet_status")),
        check("packet_does_not_authorize_execution", packet.get("execution_authorized_by_packet") is False, packet.get("execution_authorized_by_packet")),
        check("packet_no_api", packet.get("api_call_attempted") is False, packet.get("api_call_attempted")),
        check("raw_outputs_not_read_by_audit", True, False),
        check(
            "qwen_requires_deepseek_passed",
            qwen_first_allowed or not (qwen and qwen["summary_present"]) or bool(deepseek and deepseek["status"] == "passed"),
            {
                "deepseek_status": deepseek and deepseek["status"],
                "qwen_present": qwen and qwen["summary_present"],
                "execution_order_policy": packet.get("execution_order_policy"),
            },
        ),
    ]
    if not present:
        status = "waiting_for_execution"
    elif all(item["status"] == "passed" for item in model_audits):
        status = "passed"
    elif any(item["status"] == "failed" for item in model_audits) or not all(item["passed"] for item in order_checks):
        status = "failed"
    else:
        status = "partial_waiting_for_remaining_model"
    return {
        "audit_id": packet.get("result_audit_id") or "evp8_deepseek_qwen_first_batch_full_result_audit_v0_1",
        "cohort_id": "EVP-8",
        "protocol_id": packet.get("protocol_id"),
        "candidate_set_id": packet.get("candidate_set_id"),
        "packet_id": packet.get("packet_id"),
        "evidence_source_mode": packet.get("evidence_source_mode"),
        "execution_order_policy": packet.get("execution_order_policy"),
        "audit_status": status,
        "api_call_attempted": False,
        "raw_outputs_read": False,
        "raw_outputs_generated_by_audit": False,
        "rendered_prompt_text_read": False,
        "model_audits": model_audits,
        "order_checks": order_checks,
        "claim_boundary": (
            "This audit validates tracked first-batch full-run summaries when they exist. "
            "It is not model-result evidence before execution and never reads raw responses."
        ),
    }


def write_markdown(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        f"# {audit.get('audit_id', 'EVP-8 DeepSeek/Qwen First-Batch Full-Run Result Audit')}",
        "",
        f"- Status: `{audit['audit_status']}`",
        f"- Packet: `{audit.get('packet_id')}`",
        f"- Evidence source mode: `{audit.get('evidence_source_mode')}`",
        f"- Execution order policy: `{audit.get('execution_order_policy')}`",
        f"- API call attempted by audit: `{str(audit['api_call_attempted']).lower()}`",
        f"- Raw outputs read: `{str(audit['raw_outputs_read']).lower()}`",
        f"- Raw outputs generated by audit: `{str(audit['raw_outputs_generated_by_audit']).lower()}`",
        "",
        "## Model Summaries",
        "",
    ]
    for item in audit["model_audits"]:
        lines.append(f"- `{item['model_id']}`: `{item['status']}`")
        lines.append(f"  - summary: `{item['summary_path']}`")
        lines.append(f"  - raw responses: `{item['raw_response_path']}`")
    lines.extend(["", "## Order Checks", ""])
    lines.extend(f"- {item['check']}: `{str(item['passed']).lower()}`" for item in audit["order_checks"])
    lines.extend(["", "## Claim Boundary", "", audit["claim_boundary"], ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def assert_audit(audit: dict[str, Any]) -> None:
    if audit["audit_status"] not in {"waiting_for_execution", "partial_waiting_for_remaining_model", "passed"}:
        raise SystemExit(f"EVP-8 first-batch full result audit failed: {audit['audit_status']}")
    if audit["api_call_attempted"] is not False:
        raise SystemExit("result audit must not call APIs")
    if audit["raw_outputs_read"] is not False:
        raise SystemExit("result audit must not read raw outputs")
    if not all(item["passed"] for item in audit["order_checks"]):
        raise SystemExit(f"EVP-8 first-batch full order checks failed: {audit['order_checks']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=PACKET_PATH)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    audit = build_audit(args.packet)
    write_json(args.json_out, audit)
    write_markdown(args.md_out, audit)
    if args.check:
        assert_audit(audit)
    print(json.dumps(audit, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
