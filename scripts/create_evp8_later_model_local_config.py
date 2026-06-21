"""Create or dry-run the ignored EVP-8 later-model local config.

The config contains OpenRouter model routes, expected call counts, and output
boundaries. It contains no API keys. Write mode copies the tracked example into
`configs/evp8_later_models.local.json`, which is ignored by git.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_CONFIG = REPO_ROOT / "configs" / "evp8_later_models.example.json"
DEFAULT_LOCAL_CONFIG = REPO_ROOT / "configs" / "evp8_later_models.local.json"
DEFAULT_DRY_RUN_OUT = REPO_ROOT / "data" / "protocols" / "evp8_later_model_local_config_plan_v0_1.json"


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _display(path: Path) -> str:
    absolute = path if path.is_absolute() else REPO_ROOT / path
    try:
        return absolute.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def _gitignore_allows_local_config(path: Path) -> bool:
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    absolute = path if path.is_absolute() else REPO_ROOT / path
    return absolute.parent == REPO_ROOT / "configs" and absolute.name.endswith(".local.json") and "configs/*.local.json" in gitignore


def _summarize_config(config: dict[str, Any], target: Path, write_attempted: bool) -> dict[str, Any]:
    full = config.get("full") or {}
    models = config.get("models") or []
    return {
        "cohort_id": "EVP-8",
        "config_id": config.get("config_id"),
        "target_local_config": _display(target),
        "local_config_write_attempted": write_attempted,
        "api_call_attempted": False,
        "raw_outputs_generated": False,
        "contains_api_key_values": False,
        "target_is_ignored_local_config": _gitignore_allows_local_config(target),
        "phase2_models": [model.get("model_id") for model in models],
        "provider_routes": [model.get("provider_route") for model in models],
        "api_key_env_names": sorted({model.get("api_key_env") for model in models}),
        "full_planned_calls_per_model": full.get("planned_calls_per_model"),
        "planned_later_model_count": len(models),
        "planned_total_later_model_calls": int(full.get("planned_calls_per_model") or 0) * len(models),
        "planning_cost_ceiling_usd": config.get("planning_cost_ceiling_usd"),
        "execution_requires_explicit_execute_flag": config.get("execution_requires_explicit_execute_flag") is True,
        "api_execution_authorized_in_config": config.get("api_execution_authorized") is True,
        "safe_next_command": (
            "python scripts\\preflight_evp8_later_models.py "
            "--config configs\\evp8_later_models.local.json --allow-missing-credentials"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--example-config", type=Path, default=EXAMPLE_CONFIG)
    parser.add_argument("--out", type=Path, default=DEFAULT_LOCAL_CONFIG)
    parser.add_argument("--dry-run-out", type=Path, default=DEFAULT_DRY_RUN_OUT)
    parser.add_argument("--write", action="store_true", help="Write the ignored local config.")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing local config.")
    args = parser.parse_args()

    config = _load_json(args.example_config)
    summary = _summarize_config(config, args.out, write_attempted=args.write)
    if not summary["target_is_ignored_local_config"]:
        raise SystemExit(f"Refusing to use non-ignored local config target: {_display(args.out)}")

    if args.write:
        target = args.out if args.out.is_absolute() else REPO_ROOT / args.out
        if target.exists() and not args.force:
            raise SystemExit(f"{_display(args.out)} already exists; pass --force to overwrite")
        _write_json(target, config)
    _write_json(args.dry_run_out, summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
