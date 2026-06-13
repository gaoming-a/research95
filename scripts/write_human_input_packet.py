from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ENV_PATH = Path(".env")
MODEL_SELECTION_PATH = Path("configs") / "model_selection.local.json"
API_CONFIG_PATH = Path("configs") / "api_pilot.local.json"
READINESS_PATH = Path("outputs") / "readiness_audit" / "latest.json"
PLAN_PROGRESS_PATH = Path("outputs") / "plan_progress" / "latest.json"
YOUTUBEDL_DECISION_PATH = Path("outputs") / "youtubedl_p2p_decision_audit" / "latest.json"
YOUTUBEDL_ATTEMPT_PATH = Path("docs") / "experiments" / "evp7_youtubedl_p2p_execution_attempt_20260613.md"
YOUTUBEDL_MANIFEST_PATH = Path("data") / "p2p_scopes" / "bugsinpy_youtube-dl_7_p2p_broad.json"


BOOTSTRAP_DRY_RUN_COMMAND = (
    "python scripts\\bootstrap_api_prereqs.py --model deepseek-v4-pro "
    "--api-provider deepseek_official --provider DeepSeek "
    '--selection-source "DeepSeek official API docs and user-confirmed primary model" '
    "--selection-source-url https://api-docs.deepseek.com/ "
    '--capability-source "DeepSeek official V4 model family" '
    '--capability-band "single-model-pilot/strong-reviewer" '
    '--reason "Use DeepSeek V4 Pro through the official DeepSeek API for a within-model llm_only versus evidence_first comparison, controlling base-model capability." '
    "--dry-run --allow-missing-credentials"
)

BOOTSTRAP_WRITE_COMMAND = (
    "python scripts\\bootstrap_api_prereqs.py --model deepseek-v4-pro "
    "--api-provider deepseek_official --provider DeepSeek "
    '--selection-source "DeepSeek official API docs and user-confirmed primary model" '
    "--selection-source-url https://api-docs.deepseek.com/ "
    '--capability-source "DeepSeek official V4 model family" '
    '--capability-band "single-model-pilot/strong-reviewer" '
    '--reason "Use DeepSeek V4 Pro through the official DeepSeek API for a within-model llm_only versus evidence_first comparison, controlling base-model capability."'
)


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def env_has_provider_key(path: Path, key_name: str) -> bool:
    if not path.exists():
        return False
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        if key.strip() == key_name and len(value.strip().strip("\"'")) > 20:
            return True
    return False


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def build_packet() -> dict[str, Any]:
    readiness = read_json(READINESS_PATH) or {}
    progress = read_json(PLAN_PROGRESS_PATH) or {}
    youtubedl_decision = read_json(YOUTUBEDL_DECISION_PATH) or {}
    youtubedl_attempt_exists = YOUTUBEDL_ATTEMPT_PATH.exists()
    youtubedl_manifest_exists = YOUTUBEDL_MANIFEST_PATH.exists()
    api = readiness.get("api", {}) if isinstance(readiness, dict) else {}
    local_config = api.get("local_config", {}) if isinstance(api, dict) else {}
    model_selection = api.get("model_selection", {}) if isinstance(api, dict) else {}
    api_provider = api.get("api_provider", "deepseek_official")
    api_key_env = api.get("api_key_env", "DEEPSEEK_API_KEY")

    required_inputs = [
        {
            "id": "provider_api_key",
            "required": True,
            "present": env_has_provider_key(ENV_PATH, api_key_env),
            "target": ".env",
            "instruction": f"Create .env with {api_key_env}. Do not paste the key into tracked docs or command output.",
        },
        {
            "id": "model_id",
            "required": True,
            "present": bool(model_selection.get("selected_model")),
            "target": "configs/model_selection.local.json and configs/api_pilot.local.json",
            "instruction": f"Provide one concrete model id for provider {api_provider}; current primary model is deepseek-v4-pro.",
        },
        {
            "id": "model_selection_rationale",
            "required": True,
            "present": bool(model_selection.get("ready")),
            "target": "configs/model_selection.local.json",
            "instruction": "Document provider, selection source, capability source, capability band, and known limitations.",
        },
        {
            "id": "api_local_config",
            "required": True,
            "present": bool(local_config.get("exists") and local_config.get("model_set")),
            "target": "configs/api_pilot.local.json",
            "instruction": "Generate local API config from the selected model id and keep smoke_limit=2 for the first real run.",
        },
        {
            "id": "youtube_dl_p2p_decision",
            "required": True,
            "present": bool(youtubedl_attempt_exists or youtubedl_manifest_exists),
            "target": "docs/experiments/evp7_youtubedl_p2p_execution_attempt_20260613.md",
            "instruction": (
                "Original bounded project-level P2P-broad approval has been recorded and attempted once. "
                "Keep the execution-attempt record tracked."
            ),
        },
        {
            "id": "youtube_dl_dynamic_download_scope_policy",
            "required": bool(youtubedl_attempt_exists and not youtubedl_manifest_exists),
            "present": youtubedl_manifest_exists,
            "target": "docs/experiments/evp7_youtubedl_p2p_execution_attempt_20260613.md",
            "instruction": (
                "Decide whether to allow an explicit nodeid-level exclusion for dynamically generated "
                "test.test_download.TestDownload.* tests before rerunning youtube-dl_7 P2P, or stop the "
                "youtube-dl expansion path."
            ),
        },
        {
            "id": "github_repository_decision",
            "required": False,
            "present": bool((readiness.get("git") or {}).get("is_git_repo")) if isinstance(readiness, dict) else False,
            "target": "<repo_root>",
            "instruction": "Decide whether this clean workspace should become its own Git repository and which remote to use.",
        },
    ]

    missing = [item for item in required_inputs if item["required"] and not item["present"]]
    return {
        "ready_for_real_api": bool(readiness.get("overall_ready_for_real_api")),
        "positive_paper_claim_ready": bool(progress.get("prompt_only_positive_paper_claim_ready")),
        "prompt_only_positive_paper_claim_ready": bool(progress.get("prompt_only_positive_paper_claim_ready")),
        "tool_augmented_paper_claim_ready": bool(
            progress.get("tool_augmented_paper_claim_ready", progress.get("positive_paper_claim_ready"))
        ),
        "git_repo": bool(progress.get("git_repo")),
        "stage_counts": progress.get("stage_counts", {}),
        "required_inputs": required_inputs,
        "missing_required_input_ids": [item["id"] for item in missing],
        "youtube_dl_p2p_decision": {
            "audit_path": YOUTUBEDL_DECISION_PATH.as_posix(),
            "attempt_path": YOUTUBEDL_ATTEMPT_PATH.as_posix(),
            "attempt_record_exists": youtubedl_attempt_exists,
            "audit_passed": youtubedl_decision.get("passed"),
            "approval_required": (youtubedl_decision.get("command_packet") or {}).get("approval_required"),
            "manifest_exists": youtubedl_manifest_exists,
            "manifest_path": YOUTUBEDL_MANIFEST_PATH.as_posix(),
            "recommended_task": (youtubedl_decision.get("decision_packet") or {}).get("recommended_task_id"),
            "command_packet": youtubedl_decision.get("command_packet"),
            "builder_dry_run_checks": {
                key: value
                for key, value in (youtubedl_decision.get("checks") or {}).items()
                if str(key).startswith("builder_dry_run")
            },
        },
        "preferred_command_order": [
            BOOTSTRAP_DRY_RUN_COMMAND,
            BOOTSTRAP_WRITE_COMMAND,
            "python scripts\\preflight_api_pilot.py --config configs\\api_pilot.local.json",
            "python scripts\\run_api_pilot_workflow.py --config configs\\api_pilot.local.json --check-only --summary-out outputs\\api_workflow_check\\latest.json",
            "python scripts\\run_api_pilot_workflow.py --config configs\\api_pilot.local.json --execute",
        ],
        "full_run_command_after_smoke": (
            "python scripts\\run_api_pilot_workflow.py --config configs\\api_pilot.local.json "
            "--run-dir outputs\\patch_verification_api_pilot_002 --limit 0 --execute"
        ),
        "postprocess_commands": [
            (
                "python scripts\\postprocess_api_pilot_run.py "
                "--run-dir outputs\\patch_verification_api_pilot_001 --expected-candidates 2"
            ),
            (
                "python scripts\\postprocess_api_pilot_run.py "
                "--run-dir outputs\\patch_verification_api_pilot_002 --expected-candidates 30"
            ),
        ],
        "fallback_command_order": [
            "python scripts\\create_model_selection_local.py --model deepseek-v4-pro --api-provider deepseek_official --provider DeepSeek --selection-source <source-name> --selection-source-url <source-url> --capability-source <source-name> --capability-band <single-model-pilot-band> --reason <selection-rationale>",
            "python scripts\\validate_model_selection.py --selection configs\\model_selection.local.json --out outputs\\model_selection\\latest.json",
            "python scripts\\create_api_pilot_local_config.py --model deepseek-v4-pro --api-provider deepseek_official --out configs\\api_pilot.local.json --smoke-limit 2",
            "python scripts\\validate_model_selection.py --selection configs\\model_selection.local.json --api-config configs\\api_pilot.local.json --out outputs\\model_selection\\api_config_check.json",
            "python scripts\\preflight_api_pilot.py --config configs\\api_pilot.local.json",
            "python scripts\\run_api_pilot_workflow.py --config configs\\api_pilot.local.json --check-only --summary-out outputs\\api_workflow_check\\latest.json",
            "python scripts\\run_api_pilot_workflow.py --config configs\\api_pilot.local.json --execute",
        ],
        "forbidden": [
            "Do not commit .env or configs/*.local.json.",
            "Do not print the API key in logs, reports, or tracked docs.",
            "Do not run --execute before strict preflight and check-only pass.",
            "Do not treat mock or dry-run outputs as model experiment results.",
            "Do not run youtube-dl_7 P2P unless youtube_dl_p2p_decision is explicitly approved.",
            "Do not rerun youtube-dl_7 P2P with nodeid-level exclusions unless youtube_dl_dynamic_download_scope_policy is explicitly approved.",
        ],
        "decision_aids": [
            "docs/experiments/model_selection_shortlist.md",
            "docs/experiments/model_selection_protocol.md",
            "docs/experiments/evp7_youtubedl_p2p_decision_packet_20260613.md",
            "docs/experiments/evp7_youtubedl_p2p_execution_attempt_20260613.md",
            "outputs/youtubedl_p2p_decision_audit/latest.md",
        ],
    }


def build_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Human Input Packet",
        "",
        "## Status",
        "",
        f"- ready for real API: {bool_mark(packet['ready_for_real_api'])}",
        f"- prompt-only positive paper claim ready: {bool_mark(packet['prompt_only_positive_paper_claim_ready'])}",
        f"- tool-augmented conditional claim ready: {bool_mark(packet['tool_augmented_paper_claim_ready'])}",
        f"- git repository: {bool_mark(packet['git_repo'])}",
        f"- stage counts: `{packet['stage_counts']}`",
        "",
        "## Required Inputs",
        "",
        "| id | required | present | target | instruction |",
        "|---|---|---|---|---|",
    ]
    for item in packet["required_inputs"]:
        lines.append(
            f"| `{item['id']}` | {bool_mark(item['required'])} | {bool_mark(item['present'])} | "
            f"`{item['target']}` | {item['instruction']} |"
        )
    lines.extend(["", "## Missing Required Inputs", ""])
    if packet["missing_required_input_ids"]:
        for item_id in packet["missing_required_input_ids"]:
            lines.append(f"- `{item_id}`")
    else:
        lines.append("- None.")
    youtubedl_decision = packet["youtube_dl_p2p_decision"]
    lines.extend(
        [
            "",
            "## youtube-dl P2P Decision",
            "",
            f"- audit path: `{youtubedl_decision['audit_path']}`",
            f"- attempt path: `{youtubedl_decision['attempt_path']}`",
            f"- attempt record exists: {bool_mark(youtubedl_decision['attempt_record_exists'])}",
            f"- audit passed: {bool_mark(youtubedl_decision['audit_passed'])}",
            f"- approval required: {bool_mark(youtubedl_decision['approval_required'])}",
            f"- manifest path: `{youtubedl_decision['manifest_path']}`",
            f"- manifest exists: {bool_mark(youtubedl_decision['manifest_exists'])}",
            f"- recommended task: `{youtubedl_decision['recommended_task']}`",
            f"- builder dry-run checks: `{youtubedl_decision['builder_dry_run_checks']}`",
            "",
        ]
    )
    command_packet = youtubedl_decision.get("command_packet") or {}
    full_command = command_packet.get("full_command") or command_packet.get("command")
    if full_command:
        lines.extend(
            [
                "Approval-gated command packet:",
                "",
                "```powershell",
                full_command,
                "```",
                "",
            ]
        )
    lines.extend(["", "## Preferred Command Order After Inputs Are Available", ""])
    for command in packet["preferred_command_order"]:
        lines.extend(["```powershell", command, "```", ""])
    lines.extend(
        [
            "## Full Run Command After Smoke Passes",
            "",
            "Use this only after the 2-candidate real API smoke run has passed and prompts, candidates, and model are unchanged.",
            "",
            "```powershell",
            packet["full_run_command_after_smoke"],
            "```",
            "",
        ]
    )
    lines.extend(
        [
            "## Postprocess Commands",
            "",
            "Run the smoke postprocess command after the 2-candidate real API smoke run. Run the full postprocess command after the 30-candidate full run.",
            "",
        ]
    )
    for command in packet["postprocess_commands"]:
        lines.extend(["```powershell", command, "```", ""])
    lines.extend(
        [
            "## Fallback Command Order",
            "",
            "Use this only if the bootstrap wrapper needs step-by-step debugging.",
            "",
        ]
    )
    for command in packet["fallback_command_order"]:
        lines.extend(["```powershell", command, "```", ""])
    lines.extend(["## Forbidden", ""])
    for item in packet["forbidden"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Decision Aids", ""])
    for item in packet["decision_aids"]:
        lines.append(f"- `{item}`")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write the human-input packet required before real API execution.")
    parser.add_argument("--out-json", default="outputs/handoff/human_input_packet.json")
    parser.add_argument("--out-md", default="outputs/handoff/human_input_packet.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    packet = build_packet()
    write_json(Path(args.out_json), packet)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(packet), encoding="utf-8")
    print(json.dumps({"out_json": args.out_json, "out_md": args.out_md, "missing": packet["missing_required_input_ids"]}, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
