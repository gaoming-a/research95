"""Write the no-API EVP-8-HARD DeepSeek-after-Qwen execution packet."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "evp8_hard_qwen_deepseek.local.json"
CHECK_ONLY_PATH = REPO_ROOT / "data" / "protocols" / "evp8_hard_qwen_deepseek_check_only_v0_1.json"
RESULT_AUDIT_PATH = REPO_ROOT / "data" / "protocols" / "evp8_hard_qwen_deepseek_result_audit_v0_1.json"
QWEN_SUMMARY_PATH = REPO_ROOT / "data" / "reviews" / "evp8_hard_qwen_qwen3.7-max_full_summary.json"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "protocols" / "evp8_hard_deepseek_after_qwen_packet_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_hard_deepseek_after_qwen_packet_v0_1.md"


def read_json(path: Path) -> dict[str, Any]:
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


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def local_config_is_ignored_boundary(path: Path) -> bool:
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    return path.parent == REPO_ROOT / "configs" and path.name.endswith(".local.json") and "configs/*.local.json" in gitignore


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def output_paths(model_id: str) -> dict[str, str]:
    safe_model = safe_name(model_id)
    raw_dir = Path("outputs") / "evp8_hard_qwen_deepseek_full" / safe_model
    return {
        "ignored_raw_responses": (raw_dir / "raw_responses.jsonl").as_posix(),
        "tracked_summary": (Path("data") / "reviews" / f"evp8_hard_{safe_model}_full_summary.json").as_posix(),
        "tracked_parsed_reviews": (Path("data") / "reviews" / f"evp8_hard_{safe_model}_full_reviews.jsonl").as_posix(),
    }


def expected_output_absence(outputs: dict[str, str]) -> list[dict[str, Any]]:
    checks = []
    for output_kind, path_value in outputs.items():
        path = REPO_ROOT / path_value
        checks.append({"output_kind": output_kind, "path": path_value, "exists": path.exists(), "passed": not path.exists()})
    return checks


def build_packet() -> dict[str, Any]:
    config = read_json(CONFIG_PATH)
    check_only = read_json(CHECK_ONLY_PATH)
    result_audit = read_json(RESULT_AUDIT_PATH)
    qwen_summary = read_json(QWEN_SUMMARY_PATH)
    deepseek_outputs = output_paths("deepseek/deepseek-v4-pro")
    output_absence = expected_output_absence(deepseek_outputs)
    qwen_model = result_audit.get("models", {}).get("qwen/qwen3.7-max") or {}
    checks = [
        check("local_config_path_boundary", local_config_is_ignored_boundary(CONFIG_PATH), display_path(CONFIG_PATH)),
        check("local_config_execution_not_pre_authorized", config.get("api_execution_authorized") is False, config.get("api_execution_authorized")),
        check("check_only_passed", check_only.get("check_only_status") == "passed", check_only.get("check_only_status")),
        check("credential_presence_ready", check_only.get("credential_presence_ready") is True, check_only.get("credential_presence_ready")),
        check("qwen_summary_passed", qwen_summary.get("run_gate") == "passed", qwen_summary.get("run_gate")),
        check("qwen_parse_complete", qwen_summary.get("parse_valid_count") == 47 and qwen_summary.get("review_count") == 47, {"parse_valid_count": qwen_summary.get("parse_valid_count"), "review_count": qwen_summary.get("review_count")}),
        check("qwen_audit_passed", result_audit.get("audit_status") == "passed", result_audit.get("audit_status")),
        check("qwen_audit_complete", qwen_model.get("complete_candidate_coverage") is True, qwen_model.get("complete_candidate_coverage")),
        check("deepseek_outputs_absent", all(item["passed"] for item in output_absence), output_absence),
    ]
    packet_status = "ready" if all(item["passed"] for item in checks) else "blocked"
    return {
        "packet_id": "evp8_hard_deepseek_after_qwen_packet_v0_1",
        "cohort_id": "EVP-8-HARD",
        "packet_status": packet_status,
        "api_call_attempted": False,
        "raw_outputs_generated": False,
        "api_key_values_printed": False,
        "rendered_prompt_text_stored": False,
        "execution_authorized_by_packet": False,
        "requires_explicit_user_command": True,
        "precondition_qwen_result": {
            "summary": display_path(QWEN_SUMMARY_PATH),
            "audit": display_path(RESULT_AUDIT_PATH),
            "qwen_decision_counts": qwen_summary.get("decision_counts"),
            "qwen_run_gate": qwen_summary.get("run_gate"),
        },
        "planned_deepseek_calls": 47,
        "model_visible_levels": ["E6"],
        "deepseek_execute_command_after_explicit_user_authorization": {
            "command": "python scripts\\run_evp8_hard_qwen_deepseek.py --execute --config configs\\evp8_hard_qwen_deepseek.local.json --model-id deepseek/deepseek-v4-pro",
            "model_id": "deepseek/deepseek-v4-pro",
            "request_model_id": "deepseek-v4-pro",
            "provider_route": "deepseek_official",
            "outputs": deepseek_outputs,
            "proceed_if": "summary.run_gate == passed and parsed reviews contain exactly 47 candidate decisions",
        },
        "post_deepseek_audit_command": "python scripts\\audit_evp8_hard_qwen_deepseek_results.py --out data\\protocols\\evp8_hard_qwen_deepseek_result_audit_v0_1.json",
        "expected_deepseek_output_absence": output_absence,
        "checks": checks,
        "stop_gates": [
            "User has not explicitly authorized EVP-8-HARD DeepSeek API execution.",
            "Any DeepSeek expected output path already exists before execution.",
            "Qwen summary or Qwen audit is not passed.",
            "Local config is not ignored under configs/*.local.json.",
            "Tracked example config is used for --execute.",
            "DeepSeek run_gate or usage_cost_gate is not passed.",
            "DeepSeek parsed reviews do not contain exactly 47 unique candidate decisions.",
            "Tracked DeepSeek parsed reviews contain raw response text or provider response objects.",
        ],
        "claim_boundary": (
            "This is a no-API DeepSeek-after-Qwen handoff. It records that Qwen "
            "has passed and DeepSeek outputs are absent; it does not authorize "
            "DeepSeek API execution."
        ),
    }


def write_markdown(path: Path, packet: dict[str, Any]) -> None:
    command = packet["deepseek_execute_command_after_explicit_user_authorization"]
    lines = [
        "# EVP-8-HARD DeepSeek After Qwen Packet v0.1",
        "",
        f"- Status: `{packet['packet_status']}`",
        f"- API call attempted: `{str(packet['api_call_attempted']).lower()}`",
        f"- Execution authorized by this packet: `{str(packet['execution_authorized_by_packet']).lower()}`",
        f"- Planned DeepSeek calls: `{packet['planned_deepseek_calls']}`",
        "",
        "## Precondition",
        "",
        f"- Qwen summary: `{packet['precondition_qwen_result']['summary']}`",
        f"- Qwen audit: `{packet['precondition_qwen_result']['audit']}`",
        f"- Qwen run gate: `{packet['precondition_qwen_result']['qwen_run_gate']}`",
        f"- Qwen decisions: `{packet['precondition_qwen_result']['qwen_decision_counts']}`",
        "",
        "## Execute Command After Explicit User Authorization",
        "",
        f"- `{command['command']}`",
        f"  - outputs: `{command['outputs']['tracked_summary']}`, `{command['outputs']['tracked_parsed_reviews']}`, `{command['outputs']['ignored_raw_responses']}`",
        f"  - proceed if: {command['proceed_if']}",
        "",
        "## Post-Run Audit",
        "",
        f"- `{packet['post_deepseek_audit_command']}`",
        "",
        "## Stop Gates",
        "",
    ]
    lines.extend(f"- {gate}" for gate in packet["stop_gates"])
    lines.extend(["", "## Checks", ""])
    lines.extend(f"- {item['check']}: `{str(item['passed']).lower()}`" for item in packet["checks"])
    lines.extend(["", "## Claim Boundary", "", packet["claim_boundary"], ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def assert_packet(packet: dict[str, Any]) -> None:
    if packet["packet_status"] != "ready":
        raise SystemExit(f"EVP-8-HARD DeepSeek-after-Qwen packet is blocked: {packet['checks']}")
    if packet["execution_authorized_by_packet"] is not False:
        raise SystemExit("execution_authorized_by_packet must be false")
    if packet["requires_explicit_user_command"] is not True:
        raise SystemExit("requires_explicit_user_command must be true")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    packet = build_packet()
    write_json(args.json_out, packet)
    write_markdown(args.md_out, packet)
    if args.check:
        assert_packet(packet)
    print(json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
