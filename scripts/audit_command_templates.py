from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from write_human_input_packet import build_packet


DOCS_TO_CHECK = [
    Path("README.md"),
    Path("docs/plans/current_plan.md"),
    Path("docs/plans/current_plan_zh.md"),
    Path("docs/plans/ai_agent_experiment_execution_plan_zh.md"),
    Path("docs/plans/agent_execution_plan_zh.md"),
]

SCRIPT_OUTPUT_SOURCES = [
    Path("scripts/audit_execution_readiness.py"),
    Path("scripts/audit_ai_plan_progress.py"),
]
HELPER_CONFIG_OUT = Path("outputs") / "command_templates" / "api_pilot.helper.local.json"


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check_human_packet_commands() -> dict[str, Any]:
    packet = build_packet()
    preferred = packet.get("preferred_command_order", [])
    full_run_command = packet.get("full_run_command_after_smoke", "")
    postprocess_commands = packet.get("postprocess_commands", [])
    fallback = packet.get("fallback_command_order", [])
    forbidden = packet.get("forbidden", [])

    dry_run = preferred[0] if len(preferred) > 0 else ""
    write = preferred[1] if len(preferred) > 1 else ""
    preflight = preferred[2] if len(preferred) > 2 else ""
    check_only = preferred[3] if len(preferred) > 3 else ""
    execute = preferred[4] if len(preferred) > 4 else ""

    checks = {
        "preferred_command_count": len(preferred) == 5,
        "dry_run_uses_bootstrap": "bootstrap_api_prereqs.py" in dry_run,
        "dry_run_has_dry_run": "--dry-run" in dry_run,
        "dry_run_allows_missing_credentials": "--allow-missing-credentials" in dry_run,
        "write_uses_bootstrap": "bootstrap_api_prereqs.py" in write,
        "write_is_strict": "--dry-run" not in write and "--allow-missing-credentials" not in write,
        "preflight_before_check_only": "preflight_api_pilot.py" in preflight,
        "check_only_before_execute": "--check-only" in check_only and "--execute" not in check_only,
        "execute_is_last": "--execute" in execute and "--check-only" not in execute,
        "full_run_command_overrides_limit": "--limit 0" in full_run_command,
        "full_run_command_uses_new_run_dir": "--run-dir" in full_run_command and "patch_verification_api_pilot_002" in full_run_command,
        "smoke_postprocess_expected_candidates": any(
            "postprocess_api_pilot_run.py" in command
            and "patch_verification_api_pilot_001" in command
            and "--expected-candidates 2" in command
            for command in postprocess_commands
        ),
        "full_postprocess_expected_candidates": any(
            "postprocess_api_pilot_run.py" in command
            and "patch_verification_api_pilot_002" in command
            and "--expected-candidates 30" in command
            for command in postprocess_commands
        ),
        "fallback_kept_for_debugging": len(fallback) >= 7,
        "forbidden_mentions_execute_gate": any("--execute" in item and "preflight" in item for item in forbidden),
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "preferred_command_order": preferred,
    }


def check_docs() -> dict[str, Any]:
    checks: dict[str, dict[str, Any]] = {}
    for path in DOCS_TO_CHECK:
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        mentions_bootstrap = "bootstrap_api_prereqs.py" in text
        if mentions_bootstrap:
            passed = "--dry-run --allow-missing-credentials" in text
            detail = "bootstrap dry-run command mentions allow-missing-credentials"
        else:
            passed = True
            detail = "bootstrap command not documented here"
        checks[path.as_posix()] = {
            "passed": passed,
            "exists": path.exists(),
            "mentions_bootstrap": mentions_bootstrap,
            "detail": detail,
        }
    return {
        "passed": all(item["passed"] for item in checks.values()),
        "checks": checks,
    }


def check_script_next_actions() -> dict[str, Any]:
    checks: dict[str, dict[str, Any]] = {}
    for path in SCRIPT_OUTPUT_SOURCES:
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        checks[path.as_posix()] = {
            "passed": "bootstrap_api_prereqs.py" in text and "--allow-missing-credentials" in text,
            "exists": path.exists(),
            "mentions_bootstrap": "bootstrap_api_prereqs.py" in text,
            "mentions_safe_dry_run": "--allow-missing-credentials" in text,
        }
    return {
        "passed": all(item["passed"] for item in checks.values()),
        "checks": checks,
    }


def check_create_api_helper_next_commands() -> dict[str, Any]:
    command = [
        sys.executable,
        "scripts/create_api_pilot_local_config.py",
        "--model",
        "example/provider-model",
        "--out",
        str(HELPER_CONFIG_OUT),
        "--force",
    ]
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    parsed: dict[str, Any] = {}
    if completed.returncode == 0:
        parsed = json.loads(completed.stdout)
    next_commands = parsed.get("next_commands", []) if isinstance(parsed, dict) else []
    checks = {
        "helper_command_succeeded": completed.returncode == 0,
        "preflight_listed": any("preflight_api_pilot.py" in command for command in next_commands),
        "workflow_check_only_listed": any("run_api_pilot_workflow.py" in command and "--check-only" in command for command in next_commands),
        "workflow_smoke_execute_listed": any(
            "run_api_pilot_workflow.py" in command and "--execute" in command and "--limit 0" not in command
            for command in next_commands
        ),
        "workflow_full_execute_listed": any("run_api_pilot_workflow.py" in command and "--limit 0" in command for command in next_commands),
        "no_low_level_real_runner_listed": not any("run_patch_verification_api_pilot.py" in command for command in next_commands),
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "next_commands": next_commands,
        "stdout_tail": completed.stdout[-1000:],
        "stderr_tail": completed.stderr[-1000:],
    }


def build_audit() -> dict[str, Any]:
    human_packet = check_human_packet_commands()
    docs = check_docs()
    script_next_actions = check_script_next_actions()
    create_api_helper = check_create_api_helper_next_commands()
    return {
        "passed": bool(
            human_packet["passed"]
            and docs["passed"]
            and script_next_actions["passed"]
            and create_api_helper["passed"]
        ),
        "human_packet": human_packet,
        "docs": docs,
        "script_next_actions": script_next_actions,
        "create_api_helper": create_api_helper,
    }


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# Command Template Audit",
        "",
        "## Summary",
        "",
        f"- passed: {bool_mark(audit['passed'])}",
        f"- human input packet commands passed: {bool_mark(audit['human_packet']['passed'])}",
        f"- documented bootstrap commands passed: {bool_mark(audit['docs']['passed'])}",
        f"- script next actions passed: {bool_mark(audit['script_next_actions']['passed'])}",
        f"- create API helper commands passed: {bool_mark(audit['create_api_helper']['passed'])}",
        "",
        "## Human Packet Checks",
        "",
        "| check | passed |",
        "|---|---:|",
    ]
    for name, passed in audit["human_packet"]["checks"].items():
        lines.append(f"| `{name}` | {bool_mark(passed)} |")
    lines.extend(["", "## Documentation Checks", "", "| path | passed | detail |", "|---|---:|---|"])
    for path, result in audit["docs"]["checks"].items():
        lines.append(f"| `{path}` | {bool_mark(result['passed'])} | {result['detail']} |")
    lines.extend(["", "## Script Next-Action Checks", "", "| path | passed | mentions bootstrap | safe dry-run |", "|---|---:|---:|---:|"])
    for path, result in audit["script_next_actions"]["checks"].items():
        lines.append(
            f"| `{path}` | {bool_mark(result['passed'])} | "
            f"{bool_mark(result['mentions_bootstrap'])} | {bool_mark(result['mentions_safe_dry_run'])} |"
        )
    lines.extend(["", "## Create API Helper Checks", "", "| check | passed |", "|---|---:|"])
    for name, passed in audit["create_api_helper"]["checks"].items():
        lines.append(f"| `{name}` | {bool_mark(passed)} |")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit API command-template consistency.")
    parser.add_argument("--out-json", default="outputs/command_templates/latest.json")
    parser.add_argument("--out-md", default="outputs/command_templates/latest.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = build_audit()
    write_json(Path(args.out_json), audit)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(audit), encoding="utf-8")
    print(json.dumps({"out_json": args.out_json, "out_md": args.out_md, "passed": audit["passed"]}, ensure_ascii=False, indent=2))
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
