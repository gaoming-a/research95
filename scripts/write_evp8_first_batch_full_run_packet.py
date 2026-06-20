"""Write the no-API EVP-8 DeepSeek/Qwen first-batch full-run packet."""

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
FULL_CHECK_ONLY_PATH = REPO_ROOT / "data" / "protocols" / "evp8_deepseek_qwen_first_batch_full_check_only_v0_1.json"
SMOKE_AUDIT_PATH = REPO_ROOT / "data" / "protocols" / "evp8_deepseek_qwen_smoke_result_audit_v0_1.json"
SMOKE_SYNTHESIS_PATH = REPO_ROOT / "data" / "protocols" / "evp8_deepseek_qwen_smoke_synthesis_v0_1.json"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "protocols" / "evp8_deepseek_qwen_first_batch_full_run_packet_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_deepseek_qwen_first_batch_full_run_packet_v0_1.md"


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
    output_dir = Path(str((config.get("full") or {}).get("output_dir"))) / safe_name(model_id)
    return {
        "raw_responses": (output_dir / "raw_responses.jsonl").as_posix(),
        "tracked_summary": (Path("data") / "reviews" / f"evp8_{safe_name(model_id)}_full_summary.json").as_posix(),
    }


def configured_model(config: dict[str, Any], model_id: str) -> dict[str, Any]:
    for model in config.get("models") or []:
        if model.get("model_id") == model_id:
            return model
    raise ValueError(f"missing configured model: {model_id}")


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


def build_packet() -> dict[str, Any]:
    config = read_json(CONFIG_PATH)
    protocol_audit = read_json(PROTOCOL_AUDIT_PATH)
    preflight = read_json(PREFLIGHT_PATH)
    full_check = read_json(FULL_CHECK_ONLY_PATH)
    smoke_audit = read_json(SMOKE_AUDIT_PATH)
    smoke_synthesis = read_json(SMOKE_SYNTHESIS_PATH)
    model_ids = [model["model_id"] for model in config.get("models") or []]
    deepseek_model = configured_model(config, "deepseek/deepseek-v4-pro")
    qwen_model = configured_model(config, "qwen/qwen3.7-max")
    execute_commands = [
        {
            "step": "deepseek_first_batch_full_first",
            "model_id": "deepseek/deepseek-v4-pro",
            "request_model_id": deepseek_model.get("request_model_id"),
            "provider_route": deepseek_model.get("provider_route"),
            "command": "python scripts\\run_evp8_deepseek_qwen_smoke.py --execute --run-scope full --config configs\\evp8_deepseek_qwen.local.json --model-id deepseek/deepseek-v4-pro",
            "outputs": output_paths(config, "deepseek/deepseek-v4-pro"),
            "proceed_if": "tracked_summary.first_batch_full_gate == passed and tracked_summary.usage_cost_gate == passed",
        },
        {
            "step": "qwen_first_batch_full_after_deepseek_gate",
            "model_id": "qwen/qwen3.7-max",
            "request_model_id": qwen_model.get("request_model_id"),
            "provider_route": qwen_model.get("provider_route"),
            "command": "python scripts\\run_evp8_deepseek_qwen_smoke.py --execute --run-scope full --config configs\\evp8_deepseek_qwen.local.json --model-id qwen/qwen3.7-max",
            "outputs": output_paths(config, "qwen/qwen3.7-max"),
            "proceed_if": "DeepSeek first-batch full audit passed first; this Qwen summary must also pass parse and usage/cost gates.",
        },
    ]
    output_absence = expected_output_absence(execute_commands)
    checks = [
        check("local_config_path_boundary", local_config_is_ignored_boundary(CONFIG_PATH), display_path(CONFIG_PATH)),
        check("protocol_audit_passed", protocol_audit.get("protocol_spec_audit_status") == "passed", protocol_audit.get("protocol_spec_audit_status")),
        check("protocol_ready_for_preflight", protocol_audit.get("phase0_api_readiness") == "ready_for_api_preflight", protocol_audit.get("phase0_api_readiness")),
        check("preflight_passed", preflight.get("preflight_status") == "passed", preflight.get("preflight_status")),
        check("preflight_ready_for_user_execute_command", preflight.get("ready_for_user_execute_command") is True, preflight.get("ready_for_user_execute_command")),
        check("preflight_no_key_values_printed", preflight.get("api_key_values_printed") is False, preflight.get("api_key_values_printed")),
        check("full_check_only_passed", full_check.get("check_only_status") == "passed", full_check.get("check_only_status")),
        check("full_check_only_scope", full_check.get("run_scope") == "full", full_check.get("run_scope")),
        check("full_packet_count", full_check.get("packet_count") == 686, full_check.get("packet_count")),
        check("full_candidate_count", full_check.get("candidate_count") == 98, full_check.get("candidate_count")),
        check("full_prompt_count", full_check.get("prompt_count") == 686, full_check.get("prompt_count")),
        check("full_prompt_hashes_unique", full_check.get("prompt_hashes_unique_count") == 686, full_check.get("prompt_hashes_unique_count")),
        check("full_check_no_api", full_check.get("api_call_attempted") is False, full_check.get("api_call_attempted")),
        check("full_check_no_raw_outputs", full_check.get("raw_outputs_generated") is False, full_check.get("raw_outputs_generated")),
        check("smoke_audit_passed", smoke_audit.get("audit_status") == "passed", smoke_audit.get("audit_status")),
        check("smoke_synthesis_passed", smoke_synthesis.get("synthesis_status") == "passed", smoke_synthesis.get("synthesis_status")),
        check("phase1_model_ids", model_ids == ["deepseek/deepseek-v4-pro", "qwen/qwen3.7-max"], model_ids),
        check("expected_full_outputs_absent", all(item["passed"] for item in output_absence), output_absence),
    ]
    guard_commands = [
        "git status --short --branch --untracked-files=all",
        "python scripts\\audit_evp8_protocol_spec.py --check",
        "python scripts\\preflight_evp8_deepseek_qwen.py --config configs\\evp8_deepseek_qwen.local.json --strict-api-ready",
        "python scripts\\run_evp8_deepseek_qwen_smoke.py --check-only --run-scope full --config configs\\evp8_deepseek_qwen.local.json",
        "python scripts\\write_evp8_first_batch_full_run_packet.py --check",
        "python scripts\\audit_evp8_first_batch_full_results.py --check",
        "python scripts\\summarize_evp8_first_batch_full_synthesis.py --check",
        "git status --short --ignored configs\\evp8_deepseek_qwen.local.json outputs artifacts .env data\\reviews",
    ]
    packet_status = "ready" if all(item["passed"] for item in checks) else "blocked"
    return {
        "packet_id": "evp8_deepseek_qwen_first_batch_full_run_packet_v0_1",
        "cohort_id": "EVP-8",
        "protocol_id": protocol_audit.get("protocol_id"),
        "candidate_set_id": full_check.get("candidate_set_id"),
        "packet_status": packet_status,
        "api_call_attempted": False,
        "raw_outputs_generated": False,
        "api_key_values_printed": False,
        "rendered_prompt_text_stored": False,
        "execution_authorized_by_packet": False,
        "requires_explicit_user_command": True,
        "local_config": display_path(CONFIG_PATH),
        "run_scope": "full",
        "planned_calls_per_model": 686,
        "candidate_count": 98,
        "model_visible_levels": ["E0", "E1", "E2", "E3", "E4", "E5", "E6"],
        "max_output_tokens": config.get("max_output_tokens"),
        "temperature": config.get("temperature"),
        "cost_observability_fields": [
            "usage.prompt_tokens",
            "usage.completion_tokens",
            "usage.total_tokens",
            "cost_usd",
            "cost_cny",
            "cost_currency",
            "cost_source",
            "cost_observability",
        ],
        "guard_commands": guard_commands,
        "execute_commands_after_explicit_user_authorization": execute_commands,
        "post_full_run_commands": [
            "python scripts\\audit_evp8_first_batch_full_results.py --check",
            "python scripts\\summarize_evp8_first_batch_full_synthesis.py --check",
        ],
        "expected_output_absence": output_absence,
        "checks": checks,
        "stop_gates": [
            "Any guard command fails.",
            "Any expected first-batch full output path already exists before execution.",
            "Local config is not ignored under configs/*.local.json.",
            "Rendered prompt text or raw model response would be written to tracked files.",
            "DeepSeek first-batch full run does not pass parse/schema/usage-cost gates.",
            "Qwen first-batch full run is attempted before DeepSeek first-batch full audit passes.",
            "Any first-batch full summary has unknown_cost_record_count > 0.",
            "Any executed run changes protocol id, candidate set id, prompt hash policy, evidence levels, provider route, model id, temperature, or max output tokens.",
            "Any hidden evaluator label becomes model-visible.",
            "Any protocol, prompt, schema, candidate-set, or evaluator-join bug requires a protocol version bump and affected-model rerun.",
        ],
        "claim_boundary": (
            "This packet is a no-API first-batch full-run handoff. It is not "
            "LLM verifier evidence and does not authorize 686-call model runs "
            "without a separate explicit user command."
        ),
    }


def write_markdown(path: Path, packet: dict[str, Any]) -> None:
    lines = [
        "# EVP-8 DeepSeek/Qwen First-Batch Full-Run Packet v0.1",
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
        lines.append(f"  - request model: `{command['request_model_id']}`")
        lines.append(f"  - provider route: `{command['provider_route']}`")
        lines.append(f"  - outputs: `{command['outputs']['tracked_summary']}`, `{command['outputs']['raw_responses']}`")
        lines.append(f"  - proceed if: {command['proceed_if']}")
    lines.extend(["", "## Post-Full-Run Commands", ""])
    lines.extend(f"1. `{command}`" for command in packet["post_full_run_commands"])
    lines.extend(["", "## Stop Gates", ""])
    lines.extend(f"- {gate}" for gate in packet["stop_gates"])
    lines.extend(["", "## Checks", ""])
    lines.extend(f"- {item['check']}: `{str(item['passed']).lower()}`" for item in packet["checks"])
    lines.extend(["", "## Claim Boundary", "", packet["claim_boundary"], ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def assert_packet(packet: dict[str, Any]) -> None:
    if packet["packet_status"] != "ready":
        raise SystemExit(f"EVP-8 first-batch full-run packet is blocked: {packet['checks']}")
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
