from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from audit_openrouter_model_catalog import audit_models, build_markdown as build_catalog_markdown


DEFAULT_EXAMPLE_CONFIG = Path("configs") / "api_pilot.example.json"
DEFAULT_LOCAL_CONFIG = Path("configs") / "api_pilot.local.json"
DEFAULT_CATALOG_AUDIT_JSON = Path("outputs") / "model_selection" / "selected_model_catalog_audit.json"
DEFAULT_CATALOG_AUDIT_MD = Path("outputs") / "model_selection" / "selected_model_catalog_audit.md"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require_catalog_model(model: str, out_json: Path, out_md: Path) -> None:
    audit = audit_models([model])
    write_json(out_json, audit)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_catalog_markdown(audit), encoding="utf-8")
    if not audit["all_available"]:
        raise SystemExit(f"--model is not visible in the public OpenRouter catalog: {model}")


def is_placeholder(value: str) -> bool:
    stripped = value.strip()
    return (
        not stripped
        or stripped.startswith("<")
        or stripped.endswith(">")
        or "model-slug" in stripped.lower()
        or "your-" in stripped.lower()
    )


def require_existing(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{label} does not exist: {path}")


def build_config(args: argparse.Namespace) -> dict[str, Any]:
    example = read_json(Path(args.example))
    model = str(args.model).strip()
    if is_placeholder(model):
        raise SystemExit("--model must be a concrete provider model id, not a placeholder")

    candidates = Path(args.candidates or example["candidates"])
    evidence_packets = Path(args.evidence_packets or example["evidence_packets"])
    validation_summary = Path(args.validation_summary or example["validation_summary"])
    model_selection = args.model_selection or example.get("model_selection", "configs/model_selection.local.json")
    env_path = args.env or example.get("env", ".env")

    require_existing(candidates, "candidates")
    require_existing(evidence_packets, "evidence packets")
    require_existing(validation_summary, "validation summary")

    run_id = args.run_id or str(example.get("run_id", "patch_verification_api_pilot_001"))
    out_dir = args.out_dir or str(example.get("out_dir", f"outputs/{run_id}"))

    return {
        "run_id": run_id,
        "api_provider": args.api_provider,
        "model": model,
        "conditions": example.get("conditions", ["llm_only", "evidence_first"]),
        "temperature": float(args.temperature if args.temperature is not None else example.get("temperature", 0.0)),
        "max_tokens": int(args.max_tokens if args.max_tokens is not None else example.get("max_tokens", 1200)),
        "smoke_limit": int(args.smoke_limit),
        "candidates": candidates.as_posix(),
        "evidence_packets": evidence_packets.as_posix(),
        "validation_summary": validation_summary.as_posix(),
        "model_selection": model_selection,
        "out_dir": out_dir,
        "env": env_path,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create an ignored local config for the API pilot.")
    parser.add_argument("--model", required=True, help="Concrete model id or provider slug.")
    parser.add_argument("--api-provider", choices=["openrouter", "deepseek_official"], default="openrouter")
    parser.add_argument("--example", default=str(DEFAULT_EXAMPLE_CONFIG), help="Example config to copy defaults from.")
    parser.add_argument("--out", default=str(DEFAULT_LOCAL_CONFIG), help="Local config output path.")
    parser.add_argument("--run-id", help="Run id for the API pilot.")
    parser.add_argument("--out-dir", help="API pilot output directory.")
    parser.add_argument("--candidates", help="Candidate JSONL path.")
    parser.add_argument("--evidence-packets", help="Evidence packet JSONL path.")
    parser.add_argument("--validation-summary", help="Validation summary JSON path.")
    parser.add_argument("--model-selection", help="Model selection JSON path.")
    parser.add_argument("--env", help="Env file path. Defaults to the example config value.")
    parser.add_argument("--smoke-limit", type=int, default=2, help="2 for smoke run; 0 for full run.")
    parser.add_argument("--temperature", type=float)
    parser.add_argument("--max-tokens", type=int)
    parser.add_argument("--require-openrouter-catalog", action="store_true", help="Verify an OpenRouter model slug against the public OpenRouter catalog before writing.")
    parser.add_argument("--catalog-audit-json", default=str(DEFAULT_CATALOG_AUDIT_JSON))
    parser.add_argument("--catalog-audit-md", default=str(DEFAULT_CATALOG_AUDIT_MD))
    parser.add_argument("--force", action="store_true", help="Overwrite an existing local config.")
    parser.add_argument("--dry-run", action="store_true", help="Print config without writing it.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = build_config(args)
    if args.require_openrouter_catalog:
        if config["api_provider"] != "openrouter":
            raise SystemExit("--require-openrouter-catalog is only valid with --api-provider openrouter")
        require_catalog_model(config["model"], Path(args.catalog_audit_json), Path(args.catalog_audit_md))
    out = Path(args.out)
    if args.dry_run:
        print(json.dumps(config, ensure_ascii=False, indent=2, sort_keys=True))
        return
    if out.exists() and not args.force:
        raise SystemExit(f"{out} already exists; pass --force to overwrite")
    write_json(out, config)
    print(
        json.dumps(
            {
                "out": str(out),
                "api_provider": config["api_provider"],
                "model": config["model"],
                "smoke_limit": config["smoke_limit"],
                "next_commands": [
                    f"python scripts/preflight_api_pilot.py --config {out.as_posix()}",
                    f"python scripts/run_api_pilot_workflow.py --config {out.as_posix()} --check-only --summary-out outputs/api_workflow_check/latest.json",
                    f"python scripts/run_api_pilot_workflow.py --config {out.as_posix()} --execute",
                    f"python scripts/run_api_pilot_workflow.py --config {out.as_posix()} --run-dir outputs/patch_verification_api_pilot_002 --limit 0 --execute",
                ],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
