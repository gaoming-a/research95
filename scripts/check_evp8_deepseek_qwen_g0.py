"""Run the no-API EVP-8 DeepSeek/Qwen G0 guard sequence.

This script is a convenience gate for the commands that must pass immediately
before any user-authorized EVP-8 Phase 1 smoke execution. It does not call
model APIs, read raw responses, or store rendered prompts.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "evp8_deepseek_qwen.local.json"
EXECUTION_PACKET = REPO_ROOT / "data" / "protocols" / "evp8_deepseek_qwen_smoke_execution_packet_v0_1.json"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "protocols" / "evp8_deepseek_qwen_g0_guard_summary_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_deepseek_qwen_g0_guard_summary_v0_1.md"


def display_path(path: Path) -> str:
    absolute = path if path.is_absolute() else REPO_ROOT / path
    try:
        return absolute.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(absolute)


def display_command(command: list[str]) -> str:
    display = list(command)
    if display and display[0] == sys.executable:
        display[0] = "python"
    return " ".join(display)


def run_command(name: str, command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    parsed_json: dict[str, Any] | None = None
    try:
        value = json.loads(completed.stdout)
        if isinstance(value, dict):
            parsed_json = value
    except json.JSONDecodeError:
        parsed_json = None
    stdout_preview = "" if completed.returncode == 0 and parsed_json is not None else preview(completed.stdout)
    return {
        "name": name,
        "command": display_command(command),
        "exit_code": completed.returncode,
        "passed": completed.returncode == 0,
        "parsed": summarize_parsed(name, parsed_json),
        "stdout_preview": stdout_preview,
        "stderr_preview": preview(completed.stderr),
    }


def preview(text: str, limit: int = 700) -> str:
    cleaned = text.strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit] + "...<truncated>"


def summarize_parsed(name: str, value: dict[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {}
    if name == "protocol_audit":
        return {
            "protocol_spec_audit_status": value.get("protocol_spec_audit_status"),
            "phase0_api_readiness": value.get("phase0_api_readiness"),
            "api_call_attempted": value.get("api_call_attempted"),
        }
    if name == "strict_preflight":
        return {
            "preflight_status": value.get("preflight_status"),
            "ready_for_user_execute_command": value.get("ready_for_user_execute_command"),
            "api_call_attempted": value.get("api_call_attempted"),
            "api_key_values_printed": value.get("api_key_values_printed"),
        }
    if name == "smoke_check_only":
        return {
            "check_only_status": value.get("check_only_status"),
            "packet_count": value.get("packet_count"),
            "prompt_hashes_unique_count": value.get("prompt_hashes_unique_count"),
            "api_call_attempted": value.get("api_call_attempted"),
            "raw_outputs_generated": value.get("raw_outputs_generated"),
        }
    if name == "execution_packet":
        return {
            "packet_status": value.get("packet_status"),
            "execution_authorized_by_packet": value.get("execution_authorized_by_packet"),
            "api_call_attempted": value.get("api_call_attempted"),
            "raw_outputs_generated": value.get("raw_outputs_generated"),
        }
    if name == "post_smoke_audit_self_test":
        return {
            "self_test_status": value.get("self_test_status"),
            "case_count": value.get("case_count"),
            "api_call_attempted": value.get("api_call_attempted"),
            "raw_outputs_read": value.get("raw_outputs_read"),
            "raw_outputs_generated": value.get("raw_outputs_generated"),
            "tracked_outputs_written": value.get("tracked_outputs_written"),
        }
    if name == "post_smoke_audit_check":
        return {
            "audit_status": value.get("audit_status"),
            "api_call_attempted": value.get("api_call_attempted"),
            "raw_outputs_read": value.get("raw_outputs_read"),
            "raw_outputs_generated_by_audit": value.get("raw_outputs_generated_by_audit"),
            "rendered_prompt_text_read": value.get("rendered_prompt_text_read"),
        }
    if name == "smoke_synthesis_self_test":
        return {
            "self_test_status": value.get("self_test_status"),
            "case_count": value.get("case_count"),
            "api_call_attempted": value.get("api_call_attempted"),
            "raw_outputs_read": value.get("raw_outputs_read"),
            "raw_outputs_generated": value.get("raw_outputs_generated"),
            "tracked_outputs_written": value.get("tracked_outputs_written"),
        }
    if name == "smoke_synthesis_check":
        return {
            "synthesis_status": value.get("synthesis_status"),
            "audit_status": value.get("audit_status"),
            "api_call_attempted": value.get("api_call_attempted"),
            "raw_outputs_read": value.get("raw_outputs_read"),
            "raw_outputs_generated_by_synthesis": value.get("raw_outputs_generated_by_synthesis"),
        }
    return {}


def ignored_boundary_result(command: list[str]) -> dict[str, Any]:
    result = run_command("ignored_boundary_status", command)
    stdout = result["stdout_preview"]
    expected = ["!! .env", "!! artifacts/", "!! configs/evp8_deepseek_qwen.local.json", "!! outputs/"]
    result["ignored_boundary"] = {
        "expected_ignored_entries": expected,
        "missing_ignored_entries": [entry for entry in expected if entry not in stdout],
    }
    result["passed"] = result["passed"] and not result["ignored_boundary"]["missing_ignored_entries"]
    return result


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{display_path(path)} must contain a JSON object")
    return value


def resolve_repo_path(path_value: str) -> Path:
    path = Path(path_value)
    return path if path.is_absolute() else REPO_ROOT / path


def expected_output_absence_result(packet_path: Path = EXECUTION_PACKET) -> dict[str, Any]:
    packet = read_json(packet_path)
    checks: list[dict[str, Any]] = []
    for command_record in packet.get("execute_commands_after_explicit_user_authorization") or []:
        outputs = command_record.get("outputs") or {}
        for output_kind in ("raw_responses", "tracked_summary"):
            output_path = str(outputs.get(output_kind) or "")
            exists = resolve_repo_path(output_path).exists()
            checks.append(
                {
                    "step": command_record.get("step"),
                    "output_kind": output_kind,
                    "path": output_path,
                    "exists": exists,
                    "passed": not exists,
                }
            )
    return {
        "name": "expected_output_absence",
        "command": f"read {display_path(packet_path)}",
        "exit_code": 0,
        "passed": all(item["passed"] for item in checks),
        "parsed": {
            "checked_output_count": len(checks),
            "existing_output_count": sum(1 for item in checks if item["exists"]),
        },
        "expected_output_absence": checks,
        "stdout_preview": "",
        "stderr_preview": "",
    }


def build_summary(config: Path) -> dict[str, Any]:
    config_display = display_path(config)
    py = sys.executable
    commands: list[tuple[str, list[str]]] = [
        ("protocol_audit", [py, "scripts\\audit_evp8_protocol_spec.py", "--check"]),
        (
            "strict_preflight",
            [
                py,
                "scripts\\preflight_evp8_deepseek_qwen.py",
                "--config",
                config_display,
                "--strict-api-ready",
            ],
        ),
        (
            "smoke_check_only",
            [
                py,
                "scripts\\run_evp8_deepseek_qwen_smoke.py",
                "--check-only",
                "--config",
                config_display,
            ],
        ),
        ("execution_packet", [py, "scripts\\write_evp8_smoke_execution_packet.py", "--check"]),
        ("post_smoke_audit_self_test", [py, "scripts\\audit_evp8_smoke_results.py", "--self-test"]),
        ("post_smoke_audit_check", [py, "scripts\\audit_evp8_smoke_results.py", "--check"]),
        ("smoke_synthesis_self_test", [py, "scripts\\summarize_evp8_smoke_synthesis.py", "--self-test"]),
        ("smoke_synthesis_check", [py, "scripts\\summarize_evp8_smoke_synthesis.py", "--check"]),
    ]
    command_results = [run_command(name, command) for name, command in commands]
    command_results.append(expected_output_absence_result())
    command_results.append(
        ignored_boundary_result(
            [
                "git",
                "status",
                "--short",
                "--branch",
                "--ignored",
                config_display,
                "outputs",
                "artifacts",
                ".env",
            ]
        )
    )
    parsed_by_name = {item["name"]: item["parsed"] for item in command_results}
    status = "passed" if all(item["passed"] for item in command_results) else "failed"
    post_smoke_status = parsed_by_name.get("post_smoke_audit_check", {}).get("audit_status")
    if post_smoke_status != "waiting_for_execution":
        status = "failed"
    return {
        "guard_id": "evp8_deepseek_qwen_g0_guard_v0_1",
        "cohort_id": "EVP-8",
        "config": config_display,
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "guard_status": status,
        "api_call_attempted": False,
        "raw_outputs_read": False,
        "raw_outputs_generated": False,
        "expected_outputs_exist": bool(
            parsed_by_name.get("expected_output_absence", {}).get("existing_output_count")
        ),
        "rendered_prompt_text_read": False,
        "local_config_content_stored": False,
        "post_smoke_expected_status_before_execution": "waiting_for_execution",
        "post_smoke_observed_status": post_smoke_status,
        "command_results": command_results,
        "next_step": "Only after explicit user authorization, execute DeepSeek smoke first.",
    }


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# EVP-8 DeepSeek/Qwen G0 Guard Summary v0.1",
        "",
        f"- Status: `{summary['guard_status']}`",
        f"- API call attempted: `{str(summary['api_call_attempted']).lower()}`",
        f"- Raw outputs read: `{str(summary['raw_outputs_read']).lower()}`",
        f"- Raw outputs generated: `{str(summary['raw_outputs_generated']).lower()}`",
        f"- Rendered prompt text read: `{str(summary['rendered_prompt_text_read']).lower()}`",
        f"- Post-smoke status before execution: `{summary['post_smoke_observed_status']}`",
        "",
        "## Commands",
        "",
    ]
    for item in summary["command_results"]:
        lines.append(f"- `{item['name']}`: `{str(item['passed']).lower()}`")
        lines.append(f"  - command: `{item['command']}`")
        if item["parsed"]:
            lines.append(f"  - parsed: `{json.dumps(item['parsed'], ensure_ascii=False, sort_keys=True)}`")
        if item["name"] == "expected_output_absence":
            for output in item.get("expected_output_absence", []):
                lines.append(f"  - `{output['output_kind']}` `{output['path']}` exists: `{str(output['exists']).lower()}`")
    lines.extend(["", "## Boundary", "", summary["next_step"], ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    summary = build_summary(args.config)
    write_json(args.json_out, summary)
    write_markdown(args.md_out, summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    if args.check and summary["guard_status"] != "passed":
        raise SystemExit(f"EVP-8 G0 guard failed: {summary['guard_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
