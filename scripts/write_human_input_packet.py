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
        "positive_paper_claim_ready": bool(progress.get("positive_paper_claim_ready")),
        "git_repo": bool(progress.get("git_repo")),
        "stage_counts": progress.get("stage_counts", {}),
        "required_inputs": required_inputs,
        "missing_required_input_ids": [item["id"] for item in missing],
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
        ],
        "decision_aids": [
            "docs/experiments/model_selection_shortlist.md",
            "docs/experiments/model_selection_protocol.md",
        ],
    }


def build_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Human Input Packet",
        "",
        "## Status",
        "",
        f"- ready for real API: {bool_mark(packet['ready_for_real_api'])}",
        f"- positive paper claim ready: {bool_mark(packet['positive_paper_claim_ready'])}",
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
