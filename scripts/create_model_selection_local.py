from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

from audit_openrouter_model_catalog import audit_models, build_markdown as build_catalog_markdown


DEFAULT_OUT = Path("configs") / "model_selection.local.json"
DEFAULT_CATALOG_AUDIT_JSON = Path("outputs") / "model_selection" / "selected_model_catalog_audit.json"
DEFAULT_CATALOG_AUDIT_MD = Path("outputs") / "model_selection" / "selected_model_catalog_audit.md"


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def is_placeholder(value: str) -> bool:
    stripped = value.strip()
    return (
        not stripped
        or stripped.startswith("<")
        or stripped.endswith(">")
        or "example.org" in stripped
        or "model-slug" in stripped.lower()
        or "your-" in stripped.lower()
    )


def parse_score(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def require_catalog_model(model: str, out_json: Path, out_md: Path) -> None:
    audit = audit_models([model])
    write_json(out_json, audit)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_catalog_markdown(audit), encoding="utf-8")
    if not audit["all_available"]:
        raise SystemExit(f"--model is not visible in the public OpenRouter catalog: {model}")


def build_selection(args: argparse.Namespace) -> dict[str, Any]:
    for field in [
        "model",
        "provider",
        "selection_source",
        "selection_source_url",
        "capability_source",
        "capability_band",
        "reason",
    ]:
        value = str(getattr(args, field)).strip()
        if is_placeholder(value):
            raise SystemExit(f"--{field.replace('_', '-')} must be concrete, not a placeholder")

    limitations = list(args.limitation or [])
    if not limitations:
        limitations = [
            "The first pilot compares conditions within the same model; it does not support cross-model superiority claims.",
            "Capability rankings may drift after the recorded selection date.",
        ]

    return {
        "selection_date": args.selection_date,
        "selection_source": args.selection_source,
        "selection_source_url": args.selection_source_url,
        "selection_policy": {
            "primary_goal": "Use one documented model endpoint for the first within-model condition comparison.",
            "matching_rule": "If expanding to multiple models, use models from a documented similar capability band and record source date.",
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
        },
        "primary_pilot_model": {
            "alias": args.alias,
            "model_id": args.model,
            "api_provider": args.api_provider,
            "openrouter_slug": args.model if args.api_provider == "openrouter" else None,
            "provider": args.provider,
            "capability_source": args.capability_source,
            "capability_score": parse_score(args.capability_score),
            "capability_band": args.capability_band,
            "reason_for_selection": args.reason,
            "known_limitations": limitations,
        },
        "optional_expansion_models": [],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create an ignored local model-selection record.")
    parser.add_argument("--model", required=True, help="Concrete model id or provider slug.")
    parser.add_argument("--api-provider", choices=["openrouter", "deepseek_official"], default="openrouter")
    parser.add_argument("--provider", required=True)
    parser.add_argument("--selection-source", required=True, help="Source used to justify model selection.")
    parser.add_argument("--selection-source-url", required=True)
    parser.add_argument("--capability-source", required=True, help="Ranking/catalog name or documented source.")
    parser.add_argument("--capability-band", required=True, help="Single-model pilot or near-peer capability band.")
    parser.add_argument("--reason", required=True, help="Concrete reason for selecting this model.")
    parser.add_argument("--capability-score", help="Optional numeric score from the source.")
    parser.add_argument("--selection-date", default=date.today().isoformat())
    parser.add_argument("--alias", default="primary")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=1200)
    parser.add_argument("--limitation", action="append", help="Known limitation. Can be repeated.")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--require-openrouter-catalog", action="store_true", help="Verify an OpenRouter model slug against the public OpenRouter catalog before writing.")
    parser.add_argument("--catalog-audit-json", default=str(DEFAULT_CATALOG_AUDIT_JSON))
    parser.add_argument("--catalog-audit-md", default=str(DEFAULT_CATALOG_AUDIT_MD))
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    selection = build_selection(args)
    if args.require_openrouter_catalog:
        if args.api_provider != "openrouter":
            raise SystemExit("--require-openrouter-catalog is only valid with --api-provider openrouter")
        require_catalog_model(args.model, Path(args.catalog_audit_json), Path(args.catalog_audit_md))
    out = Path(args.out)
    if args.dry_run:
        print(json.dumps(selection, ensure_ascii=False, indent=2, sort_keys=True))
        return
    if out.exists() and not args.force:
        raise SystemExit(f"{out} already exists; pass --force to overwrite")
    write_json(out, selection)
    print(
        json.dumps(
            {
                "out": str(out),
                "selected_model": selection["primary_pilot_model"]["model_id"],
                "next_commands": [
                    f"python scripts/validate_model_selection.py --selection {out.as_posix()}",
                    "python scripts/create_api_pilot_local_config.py --model "
                    + selection["primary_pilot_model"]["model_id"]
                    + " --api-provider "
                    + selection["primary_pilot_model"]["api_provider"],
                ],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
