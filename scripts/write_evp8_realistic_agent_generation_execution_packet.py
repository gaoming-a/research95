"""Write the no-API execution packet for realistic agent-patch generation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET_MATRIX = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_source_target_matrix_v0_1.json"
DRY_RUN_AUDIT = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_generation_dry_run_audit_v0_1.json"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_generation_execution_packet_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_realistic_agent_generation_execution_packet_v0_1.md"
DEFAULT_ENV = REPO_ROOT / ".env"
EXECUTION_OUT_DIR = REPO_ROOT / "outputs" / "evp8_realistic_agent_generation_qwen_primary_001"
RUN_ID = "evp8_realistic_agent_generation_qwen_primary_001"
MODEL = "qwen3.7-max"
API_PROVIDER = "qwen_official"
ENV_KEY = "QWEN_API_KEY"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{display_path(path)} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def display_path(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def env_key_present(env_path: Path, key: str) -> bool:
    if not env_path.exists():
        return False
    prefix = f"{key}="
    for line in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith(prefix) and stripped[len(prefix) :].strip():
            return True
    return False


def build_execute_command(targets: list[dict[str, Any]]) -> list[str]:
    command = [
        "python",
        "scripts\\generate_agent_patch_candidates.py",
        "--execute",
        "--out-dir",
        str(EXECUTION_OUT_DIR.relative_to(REPO_ROOT)),
        "--run-id",
        RUN_ID,
        "--api-provider",
        API_PROVIDER,
        "--model",
        MODEL,
        "--patches-per-task",
        "9",
    ]
    for target in targets:
        command.extend(["--task-id", str(target["task_id"])])
    return command


def build_packet(env_path: Path) -> dict[str, Any]:
    matrix = read_json(TARGET_MATRIX)
    dry_run = read_json(DRY_RUN_AUDIT)
    targets = matrix["targets"]
    planned_slots = int(matrix["target_summary"]["planned_generation_slots"])
    command = build_execute_command(targets)
    expected_outputs = {
        "output_dir": display_path(EXECUTION_OUT_DIR),
        "prompt_manifest": display_path(EXECUTION_OUT_DIR / "prompt_manifest.jsonl"),
        "candidates_pending": display_path(EXECUTION_OUT_DIR / "candidates.pending.jsonl"),
        "evidence_packets_pending": display_path(EXECUTION_OUT_DIR / "evidence_packets.pending.jsonl"),
        "generation_summary": display_path(EXECUTION_OUT_DIR / "generation_summary.json"),
        "raw_response_dir": display_path(EXECUTION_OUT_DIR / "raw"),
        "generation_error": display_path(EXECUTION_OUT_DIR / "generation_error.json"),
    }
    credential_ready = env_key_present(env_path, ENV_KEY)
    checks = [
        check("api_call_not_attempted_by_packet", True, False),
        check("execution_authorized_by_packet_false", True, False),
        check("target_matrix_passed", matrix.get("target_matrix_status") == "passed", matrix.get("target_matrix_status")),
        check("dry_run_audit_passed", dry_run.get("audit_status") == "passed", dry_run.get("audit_status")),
        check("planned_generation_slots_54", planned_slots == 54, planned_slots),
        check("execute_command_uses_execute", "--execute" in command and "--dry-run" not in command, command),
        check("execution_output_dir_absent", not EXECUTION_OUT_DIR.exists(), display_path(EXECUTION_OUT_DIR)),
        check("credential_presence_ready", credential_ready, ENV_KEY),
    ]
    status = "ready" if all(item["passed"] for item in checks) else "blocked"
    return {
        "packet_id": "evp8_realistic_agent_generation_execution_packet_v0_1",
        "date": "2026-06-29",
        "status": status,
        "scope": {
            "api_call_attempted": False,
            "execution_authorized_by_packet": False,
            "patch_generation_attempted": False,
            "verifier_api_authorized": False,
            "raw_model_outputs_read": False,
            "prompt_text_stored": False,
        },
        "inputs": {
            "target_matrix": display_path(TARGET_MATRIX),
            "dry_run_audit": display_path(DRY_RUN_AUDIT),
            "env_path": display_path(env_path),
            "env_key_checked": ENV_KEY,
            "api_key_value_printed": False,
        },
        "generation_request": {
            "run_id": RUN_ID,
            "model": MODEL,
            "api_provider": API_PROVIDER,
            "planned_generation_slots": planned_slots,
            "target_tasks": [target["task_id"] for target in targets],
            "execute_command": command,
        },
        "expected_outputs": expected_outputs,
        "stop_gates": [
            "Do not run this command unless the user explicitly authorizes realistic agent-patch generation API execution.",
            "If generation_error.json is created, stop and diagnose generation failure before retrying.",
            "Do not commit raw responses or ignored output directories.",
            "After generation, validate and relabel candidates before constructing any realistic verifier cohort.",
            "Do not run Qwen/DeepSeek verifier APIs from this generation packet.",
        ],
        "post_generation_required_steps": [
            "validate generated candidates",
            "relabel with evaluator-only hidden outcomes",
            "rerun realistic source inventory",
            "construct separated evaluator/model-visible cohort only if fresh gates pass",
            "build visible-tool baseline before verifier APIs",
        ],
        "checks": checks,
    }


def write_markdown(path: Path, packet: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    request = packet["generation_request"]
    lines = [
        "# EVP-8 Realistic Agent Generation Execution Packet v0.1",
        "",
        "Date: 2026-06-29",
        "",
        "This is a no-API execution packet. It freezes the future patch-generation",
        "command and gates, but it does not authorize API execution.",
        "",
        f"- status: `{packet['status']}`",
        f"- execution authorized by packet: `{packet['scope']['execution_authorized_by_packet']}`",
        f"- verifier API authorized: `{packet['scope']['verifier_api_authorized']}`",
        f"- model: `{request['model']}`",
        f"- provider: `{request['api_provider']}`",
        f"- planned generation slots: {request['planned_generation_slots']}",
        "",
        "## Checks",
        "",
    ]
    for row in packet["checks"]:
        detail = row["detail"]
        if row["check"] == "execute_command_uses_execute":
            detail = "command redacted to separate section"
        lines.append(f"- {row['check']}: {'passed' if row['passed'] else 'failed'} ({detail})")
    lines += [
        "",
        "## Execute Command",
        "",
        "```powershell",
        " ".join(request["execute_command"]),
        "```",
        "",
        "## Target Tasks",
        "",
    ]
    for task_id in request["target_tasks"]:
        lines.append(f"- `{task_id}`")
    lines += [
        "",
        "## Stop Gates",
        "",
    ]
    for gate in packet["stop_gates"]:
        lines.append(f"- {gate}")
    lines += [
        "",
        "## Required After Generation",
        "",
    ]
    for step in packet["post_generation_required_steps"]:
        lines.append(f"- {step}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", type=Path, default=DEFAULT_ENV)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    packet = build_packet(args.env)
    write_json(args.out_json, packet)
    write_markdown(args.out_md, packet)
    if args.check and packet["status"] != "ready":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
