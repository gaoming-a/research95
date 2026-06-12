"""Create or dry-run an ignored EVP-7 G5 LLM local config.

Dry-run mode is safe for tracked handoff artifacts: it does not write the local
config and can be used before the user has confirmed provider/model/cost/scope.
Write mode requires every execution parameter explicitly.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_CONFIG = REPO_ROOT / "configs" / "evp7_g5_llm.example.json"
DEFAULT_LOCAL_CONFIG = REPO_ROOT / "configs" / "evp7_g5_llm.local.json"
DEFAULT_DRY_RUN_OUT = REPO_ROOT / "data" / "reviews" / "evp7_g5_local_config_dry_run.json"
DEFAULT_PACKET_MD = REPO_ROOT / "docs" / "experiments" / "evp7_g5_execution_confirmation_packet.md"
VALID_PROVIDERS = {"deepseek_official", "openrouter"}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def is_placeholder(value: Any) -> bool:
    if value is None:
        return True
    text = str(value).strip()
    return not text or text.startswith("<") or text.endswith(">") or "user-confirmed" in text


def build_config(args: argparse.Namespace) -> dict[str, Any]:
    config = read_json(args.example_config)
    config["api_provider"] = args.api_provider
    config["model"] = args.model
    config["max_total_cost_usd"] = args.max_total_cost_usd
    config["smoke_scope"] = args.smoke_scope
    config["full_run_permission"] = bool(args.full_run_permission)
    config["out_dir"] = args.out_dir
    config["env"] = args.env
    return config


def missing_confirmations(args: argparse.Namespace) -> list[str]:
    missing = []
    if args.api_provider not in VALID_PROVIDERS:
        missing.append("api_provider")
    if is_placeholder(args.model):
        missing.append("model")
    if not _positive_number(args.max_total_cost_usd):
        missing.append("max_total_cost_usd")
    if is_placeholder(args.smoke_scope):
        missing.append("smoke_scope")
    if not args.full_run_permission:
        missing.append("full_run_permission")
    return missing


def dry_run_packet(args: argparse.Namespace, missing: list[str]) -> dict[str, Any]:
    return {
        "mode": "dry_run",
        "local_config_write_attempted": False,
        "api_call_attempted": False,
        "example_config": _display(args.example_config),
        "target_local_config": _display(args.out),
        "provided_values": {
            "api_provider": args.api_provider,
            "model": args.model,
            "max_total_cost_usd": args.max_total_cost_usd,
            "smoke_scope": args.smoke_scope,
            "full_run_permission": args.full_run_permission,
        },
        "missing_or_unconfirmed": missing,
        "ready_to_write_local_config": not missing,
        "safe_command_order_after_user_confirmation": [
            "python scripts\\create_evp7_g5_llm_local_config.py --api-provider <provider> --model <model> --max-total-cost-usd <usd> --smoke-scope <scope> --full-run-permission",
            "python scripts\\preflight_evp7_g5_llm_run.py --config configs\\evp7_g5_llm.local.json --strict-api-ready",
            "python scripts\\run_evp7_g5_llm_workflow.py --config configs\\evp7_g5_llm.local.json --check-only",
            "python scripts\\run_evp7_g5_llm_workflow.py --config configs\\evp7_g5_llm.local.json --execute --limit <smoke-packet-count>",
            "inspect smoke invalid-output rate, cost, and run summary before any full run",
            "python scripts\\run_evp7_g5_llm_workflow.py --config configs\\evp7_g5_llm.local.json --execute --limit 0",
        ],
        "forbidden_actions": [
            "do not edit tracked example config with real provider/model/cost decisions",
            "do not run --execute with configs/evp7_g5_llm.example.json",
            "do not skip strict preflight and check-only workflow",
            "do not treat mock or dry-run outputs as LLM signal evidence",
        ],
    }


def render_markdown(packet: dict[str, Any]) -> str:
    missing = packet["missing_or_unconfirmed"]
    lines = [
        "# EVP-7 G5 Execution Confirmation Packet",
        "",
        "This packet is generated without reading credentials and without calling APIs.",
        "",
        "## Current Status",
        "",
        f"- local config write attempted: {str(packet['local_config_write_attempted']).lower()}",
        f"- API call attempted: {str(packet['api_call_attempted']).lower()}",
        f"- ready to write local config: {str(packet['ready_to_write_local_config']).lower()}",
        f"- missing or unconfirmed: {', '.join(missing) if missing else 'none'}",
        "",
        "## Required User Confirmations",
        "",
        "- API provider: `deepseek_official` or `openrouter`",
        "- model id",
        "- maximum total cost in USD",
        "- smoke scope, such as an explicit packet count",
        "- whether full-run permission is granted after smoke passes",
        "",
        "## Safe Command Order",
        "",
    ]
    for index, command in enumerate(packet["safe_command_order_after_user_confirmation"], start=1):
        lines.append(f"{index}. `{command}`")
    lines.extend(["", "## Forbidden Actions", ""])
    for item in packet["forbidden_actions"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def _positive_number(value: Any) -> bool:
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def _display(path: Path) -> str:
    absolute = path if path.is_absolute() else REPO_ROOT / path
    try:
        return str(absolute.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--example-config", type=Path, default=EXAMPLE_CONFIG)
    parser.add_argument("--out", type=Path, default=DEFAULT_LOCAL_CONFIG)
    parser.add_argument("--dry-run-out", type=Path, default=DEFAULT_DRY_RUN_OUT)
    parser.add_argument("--packet-md", type=Path, default=DEFAULT_PACKET_MD)
    parser.add_argument("--api-provider", default="<user-confirmed-provider>")
    parser.add_argument("--model", default="<user-confirmed-model>")
    parser.add_argument("--max-total-cost-usd", default="<user-confirmed-cost-ceiling>")
    parser.add_argument("--smoke-scope", default="<user-confirmed-smoke-scope>")
    parser.add_argument("--full-run-permission", action="store_true")
    parser.add_argument("--env", default=".env")
    parser.add_argument("--out-dir", default="outputs/evp7_g5_llm_001")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    missing = missing_confirmations(args)
    if args.dry_run:
        packet = dry_run_packet(args, missing)
        write_json(args.dry_run_out, packet)
        write_text(args.packet_md, render_markdown(packet))
        print(json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if missing:
        raise SystemExit(f"missing or unconfirmed values: {', '.join(missing)}")
    config = build_config(args)
    write_json(args.out, config)
    print(json.dumps({"local_config_written": _display(args.out), "api_call_attempted": False}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
