"""Audit EVP-8 DeepSeek/Qwen smoke summaries without reading raw outputs.

Before real smoke execution this audit reports ``waiting_for_execution``. After
execution it validates tracked raw-output-free summaries, model order, parse
gates, usage/cost gates, and ignored raw-output paths.
"""

from __future__ import annotations

import argparse
import json
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


def audit_summary(command_record: dict[str, Any], summary: dict[str, Any] | None) -> dict[str, Any]:
    model_id = command_record["model_id"]
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
    checks = [
        check("mode_executed", summary.get("mode") == "executed", summary.get("mode")),
        check("api_call_attempted_true_for_executed_summary", summary.get("api_call_attempted") is True, summary.get("api_call_attempted")),
        check("review_count", summary.get("review_count") == EXPECTED_REVIEW_COUNT, summary.get("review_count")),
        check("parse_valid_count", summary.get("parse_valid_count") == EXPECTED_REVIEW_COUNT, summary.get("parse_valid_count")),
        check("invalid_parse_count", summary.get("invalid_parse_count") == 0, summary.get("invalid_parse_count")),
        check("smoke_gate", summary.get("smoke_gate") == "passed", summary.get("smoke_gate")),
        check("usage_cost_gate", summary.get("usage_cost_gate") == "passed", summary.get("usage_cost_gate")),
        check("configured_model_id", summary.get("configured_model_id") == model_id, summary.get("configured_model_id")),
        check("raw_response_text_not_stored_in_summary", summary.get("raw_response_text_stored_in_tracked_summary") is False, summary.get("raw_response_text_stored_in_tracked_summary")),
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
        model_audits.append(audit_summary(command_record, summary))
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
