from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

from create_api_pilot_local_config import build_config
from create_model_selection_local import build_selection, require_catalog_model, write_json
from preflight_api_pilot import is_placeholder, load_env_keys, preflight
from validate_model_selection import validate as validate_model_selection


DEFAULT_MODEL_SELECTION_OUT = Path("configs") / "model_selection.local.json"
DEFAULT_API_CONFIG_OUT = Path("configs") / "api_pilot.local.json"
DEFAULT_API_EXAMPLE = Path("configs") / "api_pilot.example.json"
DEFAULT_CATALOG_AUDIT_JSON = Path("outputs") / "model_selection" / "selected_model_catalog_audit.json"
DEFAULT_CATALOG_AUDIT_MD = Path("outputs") / "model_selection" / "selected_model_catalog_audit.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Bootstrap ignored local API prerequisites from explicit human-provided "
            "model-selection inputs, then run validation and preflight."
        )
    )
    parser.add_argument("--model", required=True, help="Concrete model id or provider slug.")
    parser.add_argument("--api-provider", choices=["openrouter", "deepseek_official"], default="openrouter")
    parser.add_argument("--provider", required=True, help="Model provider name.")
    parser.add_argument("--selection-source", required=True, help="Source used to justify model selection.")
    parser.add_argument("--selection-source-url", required=True)
    parser.add_argument("--capability-source", required=True, help="Ranking/catalog/source name.")
    parser.add_argument("--capability-band", required=True, help="Single-model pilot or near-peer capability band.")
    parser.add_argument("--reason", required=True, help="Concrete reason for selecting this model.")
    parser.add_argument("--capability-score", help="Optional numeric score from the source.")
    parser.add_argument("--selection-date", default=date.today().isoformat())
    parser.add_argument("--alias", default="primary")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=1200)
    parser.add_argument("--limitation", action="append", help="Known limitation. Can be repeated.")
    parser.add_argument("--model-selection-out", default=str(DEFAULT_MODEL_SELECTION_OUT))
    parser.add_argument("--api-config-out", default=str(DEFAULT_API_CONFIG_OUT))
    parser.add_argument("--api-example", default=str(DEFAULT_API_EXAMPLE))
    parser.add_argument("--run-id")
    parser.add_argument("--out-dir")
    parser.add_argument("--candidates")
    parser.add_argument("--evidence-packets")
    parser.add_argument("--validation-summary")
    parser.add_argument("--env", help="Env file path. Defaults to the API example config value.")
    parser.add_argument("--smoke-limit", type=int, default=2, help="2 for smoke run; 0 for full run config.")
    parser.add_argument(
        "--require-openrouter-catalog",
        action="store_true",
        help="Verify the selected model against the public OpenRouter catalog before writing.",
    )
    parser.add_argument("--catalog-audit-json", default=str(DEFAULT_CATALOG_AUDIT_JSON))
    parser.add_argument("--catalog-audit-md", default=str(DEFAULT_CATALOG_AUDIT_MD))
    parser.add_argument(
        "--allow-missing-credentials",
        action="store_true",
        help="Allow missing provider API key for local config validation only.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing local config files.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned local configs without writing files.")
    return parser.parse_args()


def model_selection_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        model=args.model,
        api_provider=args.api_provider,
        provider=args.provider,
        selection_source=args.selection_source,
        selection_source_url=args.selection_source_url,
        capability_source=args.capability_source,
        capability_band=args.capability_band,
        reason=args.reason,
        capability_score=args.capability_score,
        selection_date=args.selection_date,
        alias=args.alias,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        limitation=args.limitation,
    )


def api_config_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        model=args.model,
        api_provider=args.api_provider,
        example=args.api_example,
        run_id=args.run_id,
        out_dir=args.out_dir,
        candidates=args.candidates,
        evidence_packets=args.evidence_packets,
        validation_summary=args.validation_summary,
        model_selection=args.model_selection_out,
        env=args.env,
        smoke_limit=args.smoke_limit,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )


def require_can_write(path: Path, force: bool) -> None:
    if path.exists() and not force:
        raise SystemExit(f"{path} already exists; pass --force to overwrite")


def require_credentials_before_write(api_config: dict[str, Any], allow_missing_credentials: bool) -> None:
    if allow_missing_credentials:
        return
    env_path = Path(str(api_config.get("env", ".env")))
    env_values = load_env_keys(env_path)
    api_provider = str(api_config.get("api_provider", "openrouter"))
    api_key_env = "DEEPSEEK_API_KEY" if api_provider == "deepseek_official" else "OPENROUTER_API_KEY"
    if is_placeholder(env_values.get(api_key_env)):
        raise SystemExit(
            f"{api_key_env} is missing or placeholder. No local config files were written. "
            "Create .env first, or pass --allow-missing-credentials only for local config validation."
        )


def main() -> None:
    args = parse_args()
    selection_path = Path(args.model_selection_out)
    api_config_path = Path(args.api_config_out)

    selection = build_selection(model_selection_args(args))
    api_config = build_config(api_config_args(args))

    selection_validation = validate_model_selection(selection, api_config, allow_placeholders=False)
    if not selection_validation["passed"]:
        print(json.dumps({"selection_validation": selection_validation}, ensure_ascii=False, indent=2, sort_keys=True))
        raise SystemExit(1)

    if args.require_openrouter_catalog:
        if args.api_provider != "openrouter":
            raise SystemExit("--require-openrouter-catalog is only valid with --api-provider openrouter")
        require_catalog_model(args.model, Path(args.catalog_audit_json), Path(args.catalog_audit_md))

    if args.dry_run:
        print(
            json.dumps(
                {
                    "dry_run": True,
                    "would_write": {
                        str(selection_path): selection,
                        str(api_config_path): api_config,
                    },
                    "selection_validation": selection_validation,
                    "preflight": "skipped in dry-run because local files are not written",
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
        return

    require_can_write(selection_path, args.force)
    require_can_write(api_config_path, args.force)
    require_credentials_before_write(api_config, args.allow_missing_credentials)
    write_json(selection_path, selection)
    write_json(api_config_path, api_config)

    preflight_result = preflight(api_config_path, allow_missing_credentials=args.allow_missing_credentials)
    result: dict[str, Any] = {
        "api_config": str(api_config_path),
        "api_ready": preflight_result["api_ready"],
        "model_selection": str(selection_path),
        "next_commands": [
            f"python scripts/preflight_api_pilot.py --config {api_config_path.as_posix()}",
            f"python scripts/run_api_pilot_workflow.py --config {api_config_path.as_posix()} --check-only --summary-out outputs/api_workflow_check/latest.json",
            f"python scripts/run_api_pilot_workflow.py --config {api_config_path.as_posix()} --execute",
            f"python scripts/run_api_pilot_workflow.py --config {api_config_path.as_posix()} --run-dir outputs/patch_verification_api_pilot_002 --limit 0 --execute",
        ],
        "preflight": preflight_result,
        "selection_validation": selection_validation,
        "selected_model": args.model,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))

    if not selection_validation["passed"]:
        raise SystemExit(1)
    if args.allow_missing_credentials:
        if not preflight_result["dry_run_ready"]:
            raise SystemExit(1)
    elif not preflight_result["api_ready"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
