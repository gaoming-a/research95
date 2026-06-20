"""Audit EVP-8 DeepSeek/Qwen smoke summaries without reading raw outputs.

Before real smoke execution this audit reports ``waiting_for_execution``. After
execution it validates tracked raw-output-free summaries, model order, parse
gates, usage/cost gates, and ignored raw-output paths.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = REPO_ROOT / "data" / "protocols" / "evp8_deepseek_qwen_smoke_execution_packet_v0_1.json"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "protocols" / "evp8_deepseek_qwen_smoke_result_audit_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_deepseek_qwen_smoke_result_audit_v0_1.md"
EXPECTED_REVIEW_COUNT = 35


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
    checks = [
        check("mode_executed", summary.get("mode") == "executed", summary.get("mode")),
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
        check("smoke_gate", summary.get("smoke_gate") == "passed", summary.get("smoke_gate")),
        check("usage_cost_gate", summary.get("usage_cost_gate") == "passed", summary.get("usage_cost_gate")),
        check("configured_model_id", summary.get("configured_model_id") == model_id, summary.get("configured_model_id")),
        check("raw_responses_out_matches_packet", summary.get("raw_responses_out") == raw_path, summary.get("raw_responses_out")),
        check("raw_response_text_not_stored_in_summary", summary.get("raw_response_text_stored_in_tracked_summary") is False, summary.get("raw_response_text_stored_in_tracked_summary")),
        check("prompt_text_not_stored_in_summary", summary.get("prompt_text_stored") is False, summary.get("prompt_text_stored")),
        check("raw_outputs_generated_flag", summary.get("raw_outputs_generated") is True, summary.get("raw_outputs_generated")),
        check("raw_path_under_outputs", raw_path_is_ignored_boundary(raw_path), raw_path),
    ]
    cost_summary = summary.get("cost_summary") or {}
    checks.append(check("unknown_cost_record_count", cost_summary.get("unknown_cost_record_count") == 0, cost_summary.get("unknown_cost_record_count")))
    return {
        "model_id": model_id,
        "summary_path": summary_path,
        "raw_response_path": raw_path,
        "summary_present": True,
        "status": "passed" if all(item["passed"] for item in checks) else "failed",
        "checks": checks,
    }


def build_audit(packet_path: Path) -> dict[str, Any]:
    packet = read_json(packet_path)
    if packet is None:
        raise FileNotFoundError(display_path(packet_path))
    command_records = packet.get("execute_commands_after_explicit_user_authorization") or []
    model_audits = []
    for command_record in command_records:
        summary = read_json(resolve(command_record["outputs"]["tracked_summary"]))
        model_audits.append(audit_summary(packet, command_record, summary))
    present = [item for item in model_audits if item["summary_present"]]
    qwen = next((item for item in model_audits if item["model_id"] == "qwen/qwen3.7-max"), None)
    deepseek = next((item for item in model_audits if item["model_id"] == "deepseek/deepseek-v4-pro"), None)
    order_checks = [
        check("packet_ready", packet.get("packet_status") == "ready", packet.get("packet_status")),
        check("packet_does_not_authorize_execution", packet.get("execution_authorized_by_packet") is False, packet.get("execution_authorized_by_packet")),
        check("packet_no_api", packet.get("api_call_attempted") is False, packet.get("api_call_attempted")),
        check("raw_outputs_not_read_by_audit", True, False),
        check(
            "qwen_requires_deepseek_passed",
            not (qwen and qwen["summary_present"]) or bool(deepseek and deepseek["status"] == "passed"),
            {"deepseek_status": deepseek and deepseek["status"], "qwen_present": qwen and qwen["summary_present"]},
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
        "audit_id": "evp8_deepseek_qwen_smoke_result_audit_v0_1",
        "cohort_id": "EVP-8",
        "protocol_id": packet.get("protocol_id"),
        "candidate_set_id": packet.get("candidate_set_id"),
        "audit_status": status,
        "api_call_attempted": False,
        "raw_outputs_read": False,
        "raw_outputs_generated_by_audit": False,
        "rendered_prompt_text_read": False,
        "model_audits": model_audits,
        "order_checks": order_checks,
        "claim_boundary": (
            "This audit validates tracked smoke summaries when they exist. "
            "It is not model-result evidence before execution and never reads raw responses."
        ),
    }


def write_markdown(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# EVP-8 DeepSeek/Qwen Smoke Result Audit v0.1",
        "",
        f"- Status: `{audit['audit_status']}`",
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
        raise SystemExit(f"EVP-8 smoke result audit failed: {audit['audit_status']}")
    if audit["api_call_attempted"] is not False:
        raise SystemExit("result audit must not call APIs")
    if audit["raw_outputs_read"] is not False:
        raise SystemExit("result audit must not read raw outputs")
    if not all(item["passed"] for item in audit["order_checks"]):
        raise SystemExit(f"EVP-8 smoke order checks failed: {audit['order_checks']}")


def self_test_packet(packet_path: Path, deepseek_summary_path: Path, qwen_summary_path: Path) -> None:
    packet = {
        "packet_id": "evp8_deepseek_qwen_smoke_execution_packet_v0_1_self_test",
        "cohort_id": "EVP-8",
        "protocol_id": "evp8_journal_full_ladder_v0_1",
        "candidate_set_id": "evp8_smoke_from_evp7_structural_98_v0_1",
        "packet_status": "ready",
        "api_call_attempted": False,
        "execution_authorized_by_packet": False,
        "execute_commands_after_explicit_user_authorization": [
            {
                "step": "deepseek_smoke_first",
                "model_id": "deepseek/deepseek-v4-pro",
                "request_model_id": "deepseek-v4-pro",
                "provider_route": "deepseek_official",
                "outputs": {
                    "tracked_summary": str(deepseek_summary_path),
                    "raw_responses": "outputs/evp8_phase1_deepseek_qwen_smoke/deepseek_deepseek-v4-pro/raw_responses.jsonl",
                },
            },
            {
                "step": "qwen_smoke_after_deepseek_gate",
                "model_id": "qwen/qwen3.7-max",
                "request_model_id": "qwen3.7-max",
                "provider_route": "qwen_official",
                "outputs": {
                    "tracked_summary": str(qwen_summary_path),
                    "raw_responses": "outputs/evp8_phase1_deepseek_qwen_smoke/qwen_qwen3.7-max/raw_responses.jsonl",
                },
            },
        ],
    }
    write_json(packet_path, packet)


def executed_summary(model_id: str, raw_responses_out: str, **overrides: Any) -> dict[str, Any]:
    request_model_id = "deepseek-v4-pro" if model_id == "deepseek/deepseek-v4-pro" else "qwen3.7-max"
    provider_route = "deepseek_official" if model_id == "deepseek/deepseek-v4-pro" else "qwen_official"
    summary: dict[str, Any] = {
        "mode": "executed",
        "protocol_id": "evp8_journal_full_ladder_v0_1",
        "candidate_set_id": "evp8_smoke_from_evp7_structural_98_v0_1",
        "api_call_attempted": True,
        "review_count": EXPECTED_REVIEW_COUNT,
        "parse_valid_count": EXPECTED_REVIEW_COUNT,
        "invalid_parse_count": 0,
        "smoke_gate": "passed",
        "usage_cost_gate": "passed",
        "configured_model_id": model_id,
        "request_model_id": request_model_id,
        "provider_route": provider_route,
        "request_model_id_counts": {request_model_id: EXPECTED_REVIEW_COUNT},
        "configured_model_id_counts": {model_id: EXPECTED_REVIEW_COUNT},
        "actual_model_id_counts": {request_model_id: EXPECTED_REVIEW_COUNT},
        "actual_model_id_missing_count": 0,
        "provider_route_counts": {provider_route: EXPECTED_REVIEW_COUNT},
        "raw_responses_out": raw_responses_out,
        "raw_response_text_stored_in_tracked_summary": False,
        "prompt_text_stored": False,
        "raw_outputs_generated": True,
        "cost_summary": {"unknown_cost_record_count": 0},
    }
    summary.update(overrides)
    return summary


def run_case(
    case_dir: Path,
    *,
    deepseek_summary: dict[str, Any] | None,
    qwen_summary: dict[str, Any] | None,
    expected_status: str,
    assert_check_passes: bool,
) -> dict[str, Any]:
    packet_path = case_dir / "packet.json"
    deepseek_path = case_dir / "deepseek_summary.json"
    qwen_path = case_dir / "qwen_summary.json"
    self_test_packet(packet_path, deepseek_path, qwen_path)
    if deepseek_summary is not None:
        write_json(deepseek_path, deepseek_summary)
    if qwen_summary is not None:
        write_json(qwen_path, qwen_summary)
    audit = build_audit(packet_path)
    if audit["audit_status"] != expected_status:
        raise SystemExit(
            f"self-test expected {expected_status} but got {audit['audit_status']} for {display_path(case_dir)}"
        )
    try:
        assert_audit(audit)
        assert_raised = False
    except SystemExit:
        assert_raised = True
    if assert_check_passes and assert_raised:
        raise SystemExit(f"self-test expected assert_audit to pass for {display_path(case_dir)}")
    if not assert_check_passes and not assert_raised:
        raise SystemExit(f"self-test expected assert_audit to fail for {display_path(case_dir)}")
    return {
        "case": case_dir.name,
        "audit_status": audit["audit_status"],
        "assert_check_passes": assert_check_passes,
        "raw_outputs_read": audit["raw_outputs_read"],
        "api_call_attempted": audit["api_call_attempted"],
    }


def run_self_test() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="evp8_smoke_audit_selftest_") as temp_dir:
        root = Path(temp_dir)
        deepseek_raw_path = "outputs/evp8_phase1_deepseek_qwen_smoke/deepseek_deepseek-v4-pro/raw_responses.jsonl"
        qwen_raw_path = "outputs/evp8_phase1_deepseek_qwen_smoke/qwen_qwen3.7-max/raw_responses.jsonl"
        deepseek_passed = executed_summary("deepseek/deepseek-v4-pro", deepseek_raw_path)
        qwen_passed = executed_summary("qwen/qwen3.7-max", qwen_raw_path)
        failed_cost = executed_summary(
            "deepseek/deepseek-v4-pro",
            deepseek_raw_path,
            parse_valid_count=EXPECTED_REVIEW_COUNT - 1,
            invalid_parse_count=1,
            smoke_gate="failed",
            usage_cost_gate="failed",
            cost_summary={"unknown_cost_record_count": 1},
        )
        raw_path_mismatch = executed_summary(
            "deepseek/deepseek-v4-pro",
            "outputs/evp8_phase1_deepseek_qwen_smoke/unexpected/raw_responses.jsonl",
        )
        missing_actual_model = executed_summary(
            "deepseek/deepseek-v4-pro",
            deepseek_raw_path,
            actual_model_id_counts={"missing": EXPECTED_REVIEW_COUNT},
            actual_model_id_missing_count=EXPECTED_REVIEW_COUNT,
        )
        request_model_drift = executed_summary(
            "deepseek/deepseek-v4-pro",
            deepseek_raw_path,
            request_model_id_counts={"unexpected-model": EXPECTED_REVIEW_COUNT},
        )
        cases = [
            run_case(
                root / "waiting_for_execution",
                deepseek_summary=None,
                qwen_summary=None,
                expected_status="waiting_for_execution",
                assert_check_passes=True,
            ),
            run_case(
                root / "deepseek_only_passed",
                deepseek_summary=deepseek_passed,
                qwen_summary=None,
                expected_status="partial_waiting_for_remaining_model",
                assert_check_passes=True,
            ),
            run_case(
                root / "both_models_passed",
                deepseek_summary=deepseek_passed,
                qwen_summary=qwen_passed,
                expected_status="passed",
                assert_check_passes=True,
            ),
            run_case(
                root / "qwen_without_deepseek",
                deepseek_summary=None,
                qwen_summary=qwen_passed,
                expected_status="failed",
                assert_check_passes=False,
            ),
            run_case(
                root / "deepseek_parse_cost_failed",
                deepseek_summary=failed_cost,
                qwen_summary=None,
                expected_status="failed",
                assert_check_passes=False,
            ),
            run_case(
                root / "deepseek_raw_path_mismatch",
                deepseek_summary=raw_path_mismatch,
                qwen_summary=None,
                expected_status="failed",
                assert_check_passes=False,
            ),
            run_case(
                root / "deepseek_actual_model_missing",
                deepseek_summary=missing_actual_model,
                qwen_summary=None,
                expected_status="failed",
                assert_check_passes=False,
            ),
            run_case(
                root / "deepseek_request_model_drift",
                deepseek_summary=request_model_drift,
                qwen_summary=None,
                expected_status="failed",
                assert_check_passes=False,
            ),
        ]
    return {
        "self_test_status": "passed",
        "case_count": len(cases),
        "cases": cases,
        "api_call_attempted": False,
        "raw_outputs_read": False,
        "raw_outputs_generated": False,
        "tracked_outputs_written": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=PACKET_PATH)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true", help="Run no-API synthetic state tests without writing tracked artifacts.")
    args = parser.parse_args()

    if args.self_test:
        result = run_self_test()
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0

    audit = build_audit(args.packet)
    write_json(args.json_out, audit)
    write_markdown(args.md_out, audit)
    if args.check:
        assert_audit(audit)
    print(json.dumps(audit, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
