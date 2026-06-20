"""Write the no-API EVP-8 DeepSeek/Qwen smoke execution packet.

The packet records exact guard and execute commands for a future user-confirmed
smoke run. It does not authorize execution, read API key values, call APIs, or
generate raw outputs.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "evp8_deepseek_qwen.local.json"
PROTOCOL_AUDIT_PATH = REPO_ROOT / "data" / "protocols" / "evp8_protocol_v0_1_audit_summary.json"
PREFLIGHT_PATH = REPO_ROOT / "data" / "protocols" / "evp8_deepseek_qwen_preflight_summary_v0_1.json"
CHECK_ONLY_PATH = REPO_ROOT / "data" / "protocols" / "evp8_deepseek_qwen_smoke_check_only_v0_1.json"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "protocols" / "evp8_deepseek_qwen_smoke_execution_packet_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_deepseek_qwen_smoke_execution_packet_v0_1.md"


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


def output_paths(config: dict[str, Any], model_id: str) -> dict[str, str]:
    output_dir = Path(str((config.get("smoke") or {}).get("output_dir"))) / safe_name(model_id)
    return {
        "raw_responses": (output_dir / "raw_responses.jsonl").as_posix(),
        "tracked_summary": (Path("data") / "reviews" / f"evp8_{safe_name(model_id)}_smoke_summary.json").as_posix(),
    }


def build_packet() -> dict[str, Any]:
    config = read_json(CONFIG_PATH)
    protocol_audit = read_json(PROTOCOL_AUDIT_PATH)
    preflight = read_json(PREFLIGHT_PATH)
    check_only = read_json(CHECK_ONLY_PATH)
    model_ids = [model["model_id"] for model in config.get("models") or []]
    checks = [
        check("local_config_path_boundary", local_config_is_ignored_boundary(CONFIG_PATH), display_path(CONFIG_PATH)),
        check("protocol_audit_passed", protocol_audit.get("protocol_spec_audit_status") == "passed", protocol_audit.get("protocol_spec_audit_status")),
        check("protocol_ready_for_preflight", protocol_audit.get("phase0_api_readiness") == "ready_for_api_preflight", protocol_audit.get("phase0_api_readiness")),
        check("protocol_audit_no_api", protocol_audit.get("api_call_attempted") is False, protocol_audit.get("api_call_attempted")),
        check("preflight_passed", preflight.get("preflight_status") == "passed", preflight.get("preflight_status")),
        check("preflight_ready_for_user_execute_command", preflight.get("ready_for_user_execute_command") is True, preflight.get("ready_for_user_execute_command")),
        check("preflight_no_api", preflight.get("api_call_attempted") is False, preflight.get("api_call_attempted")),
        check("preflight_no_key_values_printed", preflight.get("api_key_values_printed") is False, preflight.get("api_key_values_printed")),
        check("check_only_passed", check_only.get("check_only_status") == "passed", check_only.get("check_only_status")),
        check("check_only_packet_count", check_only.get("packet_count") == 35, check_only.get("packet_count")),
        check("check_only_no_api", check_only.get("api_call_attempted") is False, check_only.get("api_call_attempted")),
        check("check_only_no_raw_outputs", check_only.get("raw_outputs_generated") is False, check_only.get("raw_outputs_generated")),
        check(
            "check_only_selection_includes_youtube_dl",
            "evp8_smoke_candidate_0047" in set(check_only.get("selected_candidate_ids") or []),
            check_only.get("selected_candidate_ids"),
        ),
        check("phase1_model_ids", model_ids == ["deepseek/deepseek-v4-pro", "qwen/qwen3.7-max"], model_ids),
    ]
    guard_commands = [
        "git status --short --branch --untracked-files=all",
        "python scripts\\audit_evp8_protocol_spec.py --check",
        "python scripts\\preflight_evp8_deepseek_qwen.py --config configs\\evp8_deepseek_qwen.local.json --strict-api-ready",
        "python scripts\\run_evp8_deepseek_qwen_smoke.py --check-only --config configs\\evp8_deepseek_qwen.local.json",
        "python scripts\\audit_evp8_smoke_results.py --self-test",
        "git status --short --ignored configs\\evp8_deepseek_qwen.local.json outputs artifacts .env",
    ]
    execute_commands = [
        {
            "step": "deepseek_smoke_first",
            "model_id": "deepseek/deepseek-v4-pro",
            "command": "python scripts\\run_evp8_deepseek_qwen_smoke.py --execute --config configs\\evp8_deepseek_qwen.local.json --model-id deepseek/deepseek-v4-pro",
            "outputs": output_paths(config, "deepseek/deepseek-v4-pro"),
            "proceed_if": "tracked_summary.smoke_gate == passed and tracked_summary.usage_cost_gate == passed",
        },
        {
            "step": "qwen_smoke_after_deepseek_gate",
            "model_id": "qwen/qwen3.7-max",
            "command": "python scripts\\run_evp8_deepseek_qwen_smoke.py --execute --config configs\\evp8_deepseek_qwen.local.json --model-id qwen/qwen3.7-max",
            "outputs": output_paths(config, "qwen/qwen3.7-max"),
            "proceed_if": "DeepSeek smoke gate passed first; this Qwen summary must also pass parse and usage/cost gates.",
        },
    ]
    packet_status = "ready" if all(item["passed"] for item in checks) else "blocked"
    return {
        "packet_id": "evp8_deepseek_qwen_smoke_execution_packet_v0_1",
        "cohort_id": "EVP-8",
        "protocol_id": protocol_audit.get("protocol_id"),
        "candidate_set_id": check_only.get("candidate_set_id"),
        "packet_status": packet_status,
        "api_call_attempted": False,
        "raw_outputs_generated": False,
        "api_key_values_printed": False,
        "rendered_prompt_text_stored": False,
        "execution_authorized_by_packet": False,
        "requires_explicit_user_command": True,
        "local_config": display_path(CONFIG_PATH),
        "guard_commands": guard_commands,
        "execute_commands_after_explicit_user_authorization": execute_commands,
        "checks": checks,
        "stop_gates": [
            "Any guard command fails.",
            "Local config is not ignored under configs/*.local.json.",
            "Rendered prompt text or raw model response would be written to tracked files.",
            "DeepSeek smoke does not pass parse/schema/usage-cost gates.",
            "Qwen smoke is attempted before DeepSeek smoke passes.",
            "Any smoke summary has unknown_cost_record_count > 0.",
            "Any executed run changes protocol id, candidate set id, prompt hash policy, evidence levels, provider route, or model id.",
            "Any hidden evaluator label becomes model-visible.",
        ],
        "claim_boundary": (
            "This packet is a no-API execution handoff. It is not LLM verifier "
            "evidence and does not authorize API calls without an explicit user command."
        ),
    }


def write_markdown(path: Path, packet: dict[str, Any]) -> None:
    lines = [
        "# EVP-8 DeepSeek/Qwen Smoke Execution Packet v0.1",
        "",
        f"- Status: `{packet['packet_status']}`",
        f"- API call attempted: `{str(packet['api_call_attempted']).lower()}`",
        f"- Raw outputs generated: `{str(packet['raw_outputs_generated']).lower()}`",
        f"- Execution authorized by this packet: `{str(packet['execution_authorized_by_packet']).lower()}`",
        f"- Local config: `{packet['local_config']}`",
        "",
        "## Guard Commands",
        "",
    ]
    lines.extend(f"1. `{command}`" for command in packet["guard_commands"])
    lines.extend(["", "## Execute Commands After Explicit User Authorization", ""])
    for command in packet["execute_commands_after_explicit_user_authorization"]:
        lines.append(f"- `{command['step']}`: `{command['command']}`")
        lines.append(f"  - outputs: `{command['outputs']['tracked_summary']}`, `{command['outputs']['raw_responses']}`")
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
        raise SystemExit(f"EVP-8 smoke execution packet is blocked: {packet['checks']}")
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
    print(json.dumps(packet, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
