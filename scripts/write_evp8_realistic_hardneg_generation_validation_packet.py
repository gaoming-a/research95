"""Write a no-API packet for fresh realistic hard-negative generation.

The packet freezes a future Qwen generation command and the mandatory
generation-audit, validation, relabel, and hard-negative filtering gates. It
does not authorize or call any model API.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

OPPORTUNITY_INVENTORY = (
    REPO_ROOT / "data" / "protocols" / "evp8_realistic_hard_negative_opportunity_inventory_v0_1.json"
)
TARGET_MATRIX = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_source_target_matrix_v0_1.json"
DRY_RUN_AUDIT = REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_generation_dry_run_audit_v0_1.json"

DEFAULT_JSON_OUT = (
    REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_generation_validation_packet_v0_1.json"
)
DEFAULT_MD_OUT = (
    REPO_ROOT / "docs" / "experiments" / "evp8_realistic_hardneg_generation_validation_packet_v0_1.md"
)
DEFAULT_ENV = REPO_ROOT / ".env"

RUN_ID = "evp8_realistic_hardneg_generation_qwen_001"
DRY_RUN_ID = "evp8_realistic_hardneg_generation_dryrun_qwen_001"
MODEL = "qwen3.7-max"
API_PROVIDER = "qwen_official"
ENV_KEY = "QWEN_API_KEY"
PATCHES_PER_TASK = 9
VARIANT_START_INDEX = 13
MODEL_CANDIDATE_START_INDEX = 3001
EXPECTED_SLOTS = 54
MIN_VISIBLE_PASS_HIDDEN_FAIL = 30
MIN_PROJECTS = 3

EXECUTION_OUT_DIR = REPO_ROOT / "outputs" / RUN_ID
VALIDATION_DIR = REPO_ROOT / "outputs" / "evp8_realistic_hardneg_validation_qwen_001"


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


def task_ids(target_matrix: dict[str, Any]) -> list[str]:
    targets = target_matrix.get("targets")
    if not isinstance(targets, list):
        raise ValueError("target matrix must contain targets list")
    return [str(target["task_id"]) for target in targets]


def expected_task_count_args(tasks: list[str]) -> list[str]:
    args: list[str] = []
    for task_id in tasks:
        args.extend(["--expected-task-count", f"{task_id}={PATCHES_PER_TASK}"])
    return args


def task_id_args(tasks: list[str]) -> list[str]:
    args: list[str] = []
    for task_id in tasks:
        args.extend(["--task-id", task_id])
    return args


def generation_execute_command(tasks: list[str]) -> list[str]:
    return [
        "python",
        "scripts\\generate_agent_patch_candidates.py",
        "--execute",
        "--out-dir",
        display_path(EXECUTION_OUT_DIR),
        "--run-id",
        RUN_ID,
        "--api-provider",
        API_PROVIDER,
        "--model",
        MODEL,
        "--patches-per-task",
        str(PATCHES_PER_TASK),
        "--variant-start-index",
        str(VARIANT_START_INDEX),
        "--model-candidate-start-index",
        str(MODEL_CANDIDATE_START_INDEX),
        *task_id_args(tasks),
    ]


def generation_result_audit_command(tasks: list[str]) -> list[str]:
    return [
        "python",
        "scripts\\audit_evp8_realistic_agent_generation_results.py",
        "--run-dir",
        display_path(EXECUTION_OUT_DIR),
        "--out-json",
        "data\\protocols\\evp8_realistic_hardneg_generation_result_audit_v0_1.json",
        "--out-md",
        "docs\\experiments\\evp8_realistic_hardneg_generation_result_audit_v0_1.md",
        "--expected-run-id",
        RUN_ID,
        "--expected-model",
        MODEL,
        "--expected-provider",
        API_PROVIDER,
        "--expected-slots",
        str(EXPECTED_SLOTS),
        *expected_task_count_args(tasks),
        "--check",
    ]


def validation_command() -> list[str]:
    return [
        "python",
        "scripts\\validate_patch_candidates.py",
        "--candidates",
        display_path(EXECUTION_OUT_DIR / "candidates.pending.jsonl"),
        "--workdir-root",
        display_path(VALIDATION_DIR / "workdirs"),
        "--out",
        display_path(VALIDATION_DIR / "validation.jsonl"),
        "--summary-out",
        display_path(VALIDATION_DIR / "validation_summary.json"),
    ]


def relabel_command() -> list[str]:
    return [
        "python",
        "scripts\\relabel_ai_patch_candidates.py",
        "--pending-candidates",
        display_path(EXECUTION_OUT_DIR / "candidates.pending.jsonl"),
        "--validation",
        display_path(VALIDATION_DIR / "validation.jsonl"),
        "--out-candidates",
        display_path(VALIDATION_DIR / "candidates.relabeled.jsonl"),
        "--out-evidence-packets",
        display_path(VALIDATION_DIR / "evidence_packets.relabeled.jsonl"),
        "--summary-out",
        display_path(VALIDATION_DIR / "relabel_summary.json"),
    ]


def source_inventory_command() -> list[str]:
    return [
        "python",
        "scripts\\inventory_evp8_realistic_agent_sources.py",
        "--out-json",
        "data\\protocols\\evp8_realistic_hardneg_source_inventory_after_generation_v0_1.json",
        "--out-md",
        "docs\\experiments\\evp8_realistic_hardneg_source_inventory_after_generation_v0_1.md",
        "--check",
    ]


def build_packet(env_path: Path) -> dict[str, Any]:
    opportunity = read_json(OPPORTUNITY_INVENTORY)
    target_matrix = read_json(TARGET_MATRIX)
    dry_run = read_json(DRY_RUN_AUDIT)
    tasks = task_ids(target_matrix)
    credential_ready = env_key_present(env_path, ENV_KEY)
    current_ready_for_verifier = bool(opportunity.get("readiness", {}).get("ready_for_verifier_api"))
    dry_run_summary = dry_run.get("summary") if isinstance(dry_run.get("summary"), dict) else {}
    checks = [
        check("api_call_not_attempted_by_packet", True, False),
        check("execution_authorized_by_packet_false", True, False),
        check("opportunity_inventory_passed", opportunity.get("inventory_status") == "passed", opportunity.get("inventory_status")),
        check("current_verifier_api_not_ready", not current_ready_for_verifier, current_ready_for_verifier),
        check("target_matrix_passed", target_matrix.get("target_matrix_status") == "passed", target_matrix.get("target_matrix_status")),
        check("dry_run_audit_passed", dry_run.get("audit_status") == "passed", dry_run.get("audit_status")),
        check("dry_run_uses_expected_run_id", dry_run_summary.get("run_id") == DRY_RUN_ID, dry_run_summary.get("run_id")),
        check("dry_run_prompt_count_expected", dry_run_summary.get("prompt_count") == EXPECTED_SLOTS, dry_run_summary.get("prompt_count")),
        check("dry_run_candidate_count_zero", dry_run_summary.get("candidate_count") == 0, dry_run_summary.get("candidate_count")),
        check("generation_execution_output_dir_absent", not EXECUTION_OUT_DIR.exists(), display_path(EXECUTION_OUT_DIR)),
        check("validation_output_dir_absent", not VALIDATION_DIR.exists(), display_path(VALIDATION_DIR)),
        check("credential_presence_ready", credential_ready, ENV_KEY),
    ]
    generation_ready = all(item["passed"] for item in checks)
    return {
        "packet_id": "evp8_realistic_hardneg_generation_validation_packet_v0_1",
        "date": datetime.now().date().isoformat(),
        "status": "ready_for_generation_api" if generation_ready else "blocked",
        "scope": {
            "api_call_attempted": False,
            "generation_api_authorized_by_packet": False,
            "user_broad_api_authorization_recorded": True,
            "verifier_api_ready": False,
            "verifier_api_authorized_by_packet": False,
            "raw_model_outputs_read": False,
            "rendered_prompt_text_stored": False,
            "patch_text_stored_in_packet": False,
        },
        "inputs": {
            "opportunity_inventory": display_path(OPPORTUNITY_INVENTORY),
            "target_matrix": display_path(TARGET_MATRIX),
            "dry_run_audit": display_path(DRY_RUN_AUDIT),
            "env_path": display_path(env_path),
            "env_key_checked": ENV_KEY,
            "api_key_value_printed": False,
        },
        "generation_plan": {
            "run_id": RUN_ID,
            "model": MODEL,
            "api_provider": API_PROVIDER,
            "planned_slots": EXPECTED_SLOTS,
            "target_tasks": tasks,
            "patches_per_task": PATCHES_PER_TASK,
            "variant_start_index": VARIANT_START_INDEX,
            "model_candidate_start_index": MODEL_CANDIDATE_START_INDEX,
            "execute_command": generation_execute_command(tasks),
        },
        "post_generation_commands": {
            "generation_result_audit": generation_result_audit_command(tasks),
            "validate_generated_candidates": validation_command(),
            "relabel_generated_candidates": relabel_command(),
            "source_inventory_after_generation": source_inventory_command(),
        },
        "expected_output_paths": {
            "generation_dir": display_path(EXECUTION_OUT_DIR),
            "generation_summary": display_path(EXECUTION_OUT_DIR / "generation_summary.json"),
            "pending_candidates": display_path(EXECUTION_OUT_DIR / "candidates.pending.jsonl"),
            "raw_response_dir": display_path(EXECUTION_OUT_DIR / "raw"),
            "generation_error": display_path(EXECUTION_OUT_DIR / "generation_error.json"),
            "validation_dir": display_path(VALIDATION_DIR),
            "validation_jsonl": display_path(VALIDATION_DIR / "validation.jsonl"),
            "validation_summary": display_path(VALIDATION_DIR / "validation_summary.json"),
            "relabeled_candidates": display_path(VALIDATION_DIR / "candidates.relabeled.jsonl"),
            "relabel_summary": display_path(VALIDATION_DIR / "relabel_summary.json"),
        },
        "hard_negative_filter_gate": {
            "required_candidate_property": "patch_applies && declared_visible_tests_pass && hidden_oracle_fails",
            "minimum_visible_pass_hidden_fail_candidates": MIN_VISIBLE_PASS_HIDDEN_FAIL,
            "minimum_projects": MIN_PROJECTS,
            "verifier_api_blocked_until_gate_passes": True,
        },
        "stop_gates": [
            "This packet does not authorize API execution by itself.",
            "If generation_error.json appears, stop and diagnose before retrying or resuming.",
            "Do not commit outputs/ raw responses, workdirs, pending candidates, or relabeled local candidate files.",
            "Do not construct a verifier cohort from relabel output until corrected oracle and visible-test consistency are audited.",
            "Do not run Qwen/DeepSeek verifier APIs until the hard-negative filter gate passes.",
        ],
        "checks": checks,
    }


def write_markdown(path: Path, packet: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    generation = packet["generation_plan"]
    commands = packet["post_generation_commands"]
    gate = packet["hard_negative_filter_gate"]
    lines = [
        "# EVP-8 Realistic Hard-Negative Generation/Validation Packet v0.1",
        "",
        f"Date: {packet['date']}",
        "",
        "This is a no-API packet. It records the broad API authorization but does",
        "not use it. The packet is for future patch generation only; verifier API",
        "execution remains blocked until a fresh visible-pass/hidden-fail gate passes.",
        "",
        f"- status: `{packet['status']}`",
        f"- generation API authorized by packet: `{packet['scope']['generation_api_authorized_by_packet']}`",
        f"- verifier API ready: `{packet['scope']['verifier_api_ready']}`",
        f"- model/provider: `{generation['model']}` / `{generation['api_provider']}`",
        f"- planned slots: {generation['planned_slots']}",
        f"- variant start index: {generation['variant_start_index']}",
        f"- model candidate start index: {generation['model_candidate_start_index']}",
        "",
        "## Checks",
        "",
    ]
    for row in packet["checks"]:
        lines.append(f"- {row['check']}: {'passed' if row['passed'] else 'failed'} ({row['detail']})")
    lines += [
        "",
        "## Generation Command",
        "",
        "```powershell",
        " ".join(generation["execute_command"]),
        "```",
        "",
        "## Post-Generation Commands",
        "",
    ]
    for name, command in commands.items():
        lines += [
            f"### {name}",
            "",
            "```powershell",
            " ".join(command),
            "```",
            "",
        ]
    lines += [
        "## Hard-Negative Filter Gate",
        "",
        f"- required property: `{gate['required_candidate_property']}`",
        f"- minimum visible-pass/hidden-fail candidates: {gate['minimum_visible_pass_hidden_fail_candidates']}",
        f"- minimum projects: {gate['minimum_projects']}",
        f"- verifier API blocked until gate passes: `{gate['verifier_api_blocked_until_gate_passes']}`",
        "",
        "## Stop Gates",
        "",
    ]
    for stop_gate in packet["stop_gates"]:
        lines.append(f"- {stop_gate}")
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
    if args.check and packet["status"] != "ready_for_generation_api":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
