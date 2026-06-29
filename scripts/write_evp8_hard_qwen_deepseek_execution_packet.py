"""Write the no-API EVP-8-HARD Qwen/DeepSeek execution packet.

The packet records exact commands and stop gates for a future user-authorized
hard-case run. It does not authorize execution, call model APIs, or read raw
responses.
"""

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
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "protocols" / "evp8_hard_qwen_deepseek_execution_packet_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_hard_qwen_deepseek_execution_packet_v0_1.md"


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


def configured_model(config: dict[str, Any], model_id: str) -> dict[str, Any]:
    for model in config.get("models") or []:
        if model.get("model_id") == model_id:
            return model
    raise ValueError(f"missing configured model: {model_id}")


def output_paths(config: dict[str, Any], model_id: str) -> dict[str, str]:
    safe_model = safe_name(model_id)
    raw_dir = Path(str((config.get("full") or {}).get("output_dir"))) / safe_model
    return {
        "ignored_raw_responses": (raw_dir / "raw_responses.jsonl").as_posix(),
        "tracked_summary": (Path("data") / "reviews" / f"evp8_hard_{safe_model}_full_summary.json").as_posix(),
        "tracked_parsed_reviews": (Path("data") / "reviews" / f"evp8_hard_{safe_model}_full_reviews.jsonl").as_posix(),
    }


def expected_output_absence(commands: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for command_record in commands:
        for output_kind, path_value in command_record["outputs"].items():
            path = REPO_ROOT / path_value
            checks.append(
                {
                    "step": command_record["step"],
                    "output_kind": output_kind,
                    "path": path_value,
                    "exists": path.exists(),
                    "passed": not path.exists(),
                }
            )
    return checks


def build_execute_commands(config: dict[str, Any]) -> list[dict[str, Any]]:
    qwen = configured_model(config, "qwen/qwen3.7-max")
    deepseek = configured_model(config, "deepseek/deepseek-v4-pro")
    return [
        {
            "step": "qwen_hard_full_first",
            "model_id": "qwen/qwen3.7-max",
            "request_model_id": qwen.get("request_model_id"),
            "provider_route": qwen.get("provider_route"),
            "command": (
                "python scripts\\run_evp8_hard_qwen_deepseek.py --execute "
                "--config configs\\evp8_hard_qwen_deepseek.local.json "
                "--model-id qwen/qwen3.7-max"
            ),
            "outputs": output_paths(config, "qwen/qwen3.7-max"),
            "proceed_if": "summary.run_gate == passed and parsed reviews contain exactly 47 candidate decisions",
        },
        {
            "step": "audit_after_qwen",
            "model_id": "qwen/qwen3.7-max",
            "command": (
                "python scripts\\audit_evp8_hard_qwen_deepseek_results.py "
                "--out data\\protocols\\evp8_hard_qwen_deepseek_result_audit_v0_1.json"
            ),
            "outputs": {
                "tracked_result_audit": "data/protocols/evp8_hard_qwen_deepseek_result_audit_v0_1.json",
            },
            "proceed_if": "audit_status == passed and qwen model coverage is complete",
        },
        {
            "step": "deepseek_hard_full_second",
            "model_id": "deepseek/deepseek-v4-pro",
            "request_model_id": deepseek.get("request_model_id"),
            "provider_route": deepseek.get("provider_route"),
            "command": (
                "python scripts\\run_evp8_hard_qwen_deepseek.py --execute "
                "--config configs\\evp8_hard_qwen_deepseek.local.json "
                "--model-id deepseek/deepseek-v4-pro"
            ),
            "outputs": output_paths(config, "deepseek/deepseek-v4-pro"),
            "proceed_if": "Qwen audit passed first; DeepSeek summary.run_gate == passed",
        },
        {
            "step": "audit_after_deepseek",
            "model_id": "deepseek/deepseek-v4-pro",
            "command": (
                "python scripts\\audit_evp8_hard_qwen_deepseek_results.py "
                "--out data\\protocols\\evp8_hard_qwen_deepseek_result_audit_v0_1.json"
            ),
            "outputs": {
                "tracked_result_audit": "data/protocols/evp8_hard_qwen_deepseek_result_audit_v0_1.json",
            },
            "proceed_if": "audit_status == passed and both model coverages are complete",
        },
    ]


def build_packet() -> dict[str, Any]:
    config = read_json(CONFIG_PATH)
    check_only = read_json(CHECK_ONLY_PATH)
    result_audit = read_json(RESULT_AUDIT_PATH)
    execute_commands = build_execute_commands(config)
    model_execute_commands = [command for command in execute_commands if "provider_route" in command]
    output_absence = expected_output_absence(model_execute_commands)
    model_ids = [model["model_id"] for model in config.get("models") or []]
    checks = [
        check("local_config_path_boundary", local_config_is_ignored_boundary(CONFIG_PATH), display_path(CONFIG_PATH)),
        check("local_config_execution_not_pre_authorized", config.get("api_execution_authorized") is False, config.get("api_execution_authorized")),
        check("check_only_passed", check_only.get("check_only_status") == "passed", check_only.get("check_only_status")),
        check("check_only_candidate_count", check_only.get("candidate_count") == 47, check_only.get("candidate_count")),
        check("check_only_packet_count_per_model", check_only.get("packet_count_per_model") == 47, check_only.get("packet_count_per_model")),
        check("check_only_only_e6", check_only.get("model_visible_levels") == ["E6"], check_only.get("model_visible_levels")),
        check("check_only_no_api", check_only.get("api_call_attempted") is False, check_only.get("api_call_attempted")),
        check("check_only_no_raw_outputs", check_only.get("raw_outputs_generated") is False, check_only.get("raw_outputs_generated")),
        check("check_only_no_prompt_text_stored", check_only.get("prompt_text_stored") is False, check_only.get("prompt_text_stored")),
        check("qwen_deepseek_credentials_present", check_only.get("credential_presence_ready") is True, check_only.get("credential_presence_ready")),
        check("result_audit_waiting_or_passed", result_audit.get("audit_status") in {"waiting_for_model_results", "passed"}, result_audit.get("audit_status")),
        check("result_audit_no_raw_read", result_audit.get("scope", {}).get("raw_model_outputs_read") is False, result_audit.get("scope", {}).get("raw_model_outputs_read")),
        check("model_ids_qwen_first_configured", model_ids == ["qwen/qwen3.7-max", "deepseek/deepseek-v4-pro"], model_ids),
        check("expected_model_outputs_absent", all(item["passed"] for item in output_absence), output_absence),
    ]
    packet_status = "ready" if all(item["passed"] for item in checks) else "blocked"
    return {
        "packet_id": "evp8_hard_qwen_deepseek_execution_packet_v0_1",
        "cohort_id": "EVP-8-HARD",
        "packet_status": packet_status,
        "api_call_attempted": False,
        "raw_outputs_generated": False,
        "api_key_values_printed": False,
        "rendered_prompt_text_stored": False,
        "execution_authorized_by_packet": False,
        "requires_explicit_user_command": True,
        "local_config": display_path(CONFIG_PATH),
        "run_scope": "full_hard_case_e6_only",
        "planned_calls_per_model": 47,
        "candidate_count": 47,
        "model_visible_levels": ["E6"],
        "qwen_first_execution_order": True,
        "guard_commands": [
            "git status --short --branch --untracked-files=all",
            "python -m py_compile scripts\\run_evp8_hard_qwen_deepseek.py scripts\\audit_evp8_hard_qwen_deepseek_results.py scripts\\write_evp8_hard_qwen_deepseek_execution_packet.py",
            "python scripts\\run_evp8_hard_qwen_deepseek.py --check-only --config configs\\evp8_hard_qwen_deepseek.local.json --summary-out data\\protocols\\evp8_hard_qwen_deepseek_check_only_v0_1.json",
            "python scripts\\audit_evp8_hard_qwen_deepseek_results.py --out data\\protocols\\evp8_hard_qwen_deepseek_result_audit_v0_1.json",
            "python scripts\\write_evp8_hard_qwen_deepseek_execution_packet.py --check",
            "git status --short --ignored configs\\evp8_hard_qwen_deepseek.local.json outputs .env data\\reviews",
        ],
        "execute_commands_after_explicit_user_authorization": execute_commands,
        "expected_output_absence": output_absence,
        "checks": checks,
        "stop_gates": [
            "Any guard command fails.",
            "Any expected model output path already exists before execution.",
            "User has not explicitly authorized API execution in this thread.",
            "Local config is not ignored under configs/*.local.json.",
            "Tracked example config is used for --execute.",
            "Rendered prompt text or raw model response would be written to tracked files.",
            "A model summary has run_gate != passed.",
            "Parsed review JSONL contains raw_response_text, provider response object, rendered prompt, or prompt text.",
            "Parsed review JSONL does not contain exactly 47 unique hard-case candidate decisions per executed model.",
            "Qwen audit does not pass before starting DeepSeek.",
            "Any hidden evaluator label or hidden oracle outcome becomes model-visible.",
        ],
        "claim_boundary": (
            "This packet is a no-API execution handoff for the EVP-8-HARD "
            "hard-case cohort. It is not an experiment result and does not "
            "authorize API calls without a separate explicit user command."
        ),
    }


def write_markdown(path: Path, packet: dict[str, Any]) -> None:
    lines = [
        "# EVP-8-HARD Qwen/DeepSeek Execution Packet v0.1",
        "",
        f"- Status: `{packet['packet_status']}`",
        f"- API call attempted: `{str(packet['api_call_attempted']).lower()}`",
        f"- Raw outputs generated: `{str(packet['raw_outputs_generated']).lower()}`",
        f"- Execution authorized by this packet: `{str(packet['execution_authorized_by_packet']).lower()}`",
        f"- Planned calls per model: `{packet['planned_calls_per_model']}`",
        f"- Local config: `{packet['local_config']}`",
        "",
        "## Guard Commands",
        "",
    ]
    lines.extend(f"1. `{command}`" for command in packet["guard_commands"])
    lines.extend(["", "## Execute Commands After Explicit User Authorization", ""])
    for command in packet["execute_commands_after_explicit_user_authorization"]:
        lines.append(f"- `{command['step']}`: `{command['command']}`")
        if command.get("request_model_id"):
            lines.append(f"  - request model: `{command['request_model_id']}`")
        if command.get("provider_route"):
            lines.append(f"  - provider route: `{command['provider_route']}`")
        lines.append("  - outputs:")
        for output_kind, output_path in command["outputs"].items():
            lines.append(f"    - `{output_kind}`: `{output_path}`")
        lines.append(f"  - proceed if: {command['proceed_if']}")
    lines.extend(["", "## Stop Gates", ""])
    lines.extend(f"- {gate}" for gate in packet["stop_gates"])
    lines.extend(["", "## Checks", ""])
    lines.extend(f"- {item['check']}: `{str(item['passed']).lower()}`" for item in packet["checks"])
    lines.extend(["", "## Claim Boundary", "", packet["claim_boundary"], ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def assert_packet(packet: dict[str, Any]) -> None:
    if packet["packet_status"] != "ready":
        raise SystemExit(f"EVP-8-HARD execution packet is blocked: {packet['checks']}")
    for key in ("api_call_attempted", "raw_outputs_generated", "api_key_values_printed", "rendered_prompt_text_stored", "execution_authorized_by_packet"):
        if packet.get(key) is not False:
            raise SystemExit(f"{key} must be false")
    if packet.get("requires_explicit_user_command") is not True:
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
