from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PLACEHOLDER_MARKERS = ("<", ">", "YYYY", "example.org", "model-ranking-or-catalog")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def is_placeholder(value: Any) -> bool:
    if value is None:
        return True
    text = str(value).strip()
    if not text:
        return True
    return any(marker in text for marker in PLACEHOLDER_MARKERS)


def check_required_string(record: dict[str, Any], field: str, allow_placeholders: bool) -> dict[str, Any]:
    value = record.get(field)
    placeholder = is_placeholder(value)
    return {
        "check": field,
        "passed": bool(value) and (allow_placeholders or not placeholder),
        "placeholder": placeholder,
        "value": value,
    }


def validate(selection: dict[str, Any], api_config: dict[str, Any] | None, allow_placeholders: bool) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for field in ["selection_date", "selection_source", "selection_source_url"]:
        checks.append(check_required_string(selection, field, allow_placeholders))

    policy = selection.get("selection_policy", {})
    checks.append(
        {
            "check": "selection_policy",
            "passed": isinstance(policy, dict) and bool(policy.get("primary_goal")),
            "detail": "present" if isinstance(policy, dict) else "missing_or_invalid",
        }
    )

    primary = selection.get("primary_pilot_model", {})
    if not isinstance(primary, dict):
        primary = {}
    for field in [
        "alias",
        "api_provider",
        "provider",
        "capability_source",
        "capability_band",
        "reason_for_selection",
    ]:
        checks.append(check_required_string(primary, f"primary_pilot_model.{field}", allow_placeholders))
        checks[-1]["value"] = primary.get(field)
        checks[-1]["placeholder"] = is_placeholder(primary.get(field))
        checks[-1]["passed"] = bool(primary.get(field)) and (allow_placeholders or not checks[-1]["placeholder"])
    model_identifier = primary.get("model_id") or primary.get("openrouter_slug")
    checks.append(
        {
            "check": "primary_pilot_model.model_identifier",
            "passed": bool(model_identifier) and (allow_placeholders or not is_placeholder(model_identifier)),
            "value": model_identifier,
            "placeholder": is_placeholder(model_identifier),
        }
    )

    limitations = primary.get("known_limitations", [])
    checks.append(
        {
            "check": "primary_pilot_model.known_limitations",
            "passed": isinstance(limitations, list) and len(limitations) > 0,
            "detail": limitations,
        }
    )

    api_model = api_config.get("model") if api_config else None
    selected_model = model_identifier
    if api_config:
        api_provider = api_config.get("api_provider", "openrouter")
        selected_provider = primary.get("api_provider", "openrouter")
        checks.append(
            {
                "check": "api_config_model_matches_selection",
                "passed": api_model == selected_model,
                "api_config_model": api_model,
                "selected_model": selected_model,
            }
        )
        checks.append(
            {
                "check": "api_provider_matches_selection",
                "passed": api_provider == selected_provider,
                "api_config_provider": api_provider,
                "selected_provider": selected_provider,
            }
        )

    passed = all(check["passed"] for check in checks)
    return {
        "passed": passed,
        "allow_placeholders": allow_placeholders,
        "selected_model": selected_model,
        "api_config_model": api_model,
        "checks": checks,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate documented model selection for API pilot runs.")
    parser.add_argument("--selection", required=True, help="Model selection JSON.")
    parser.add_argument("--api-config", help="Optional API pilot local config to cross-check model slug.")
    parser.add_argument("--out", help="Optional validation JSON output.")
    parser.add_argument("--allow-placeholders", action="store_true", help="Allow placeholders when validating example files.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not Path(args.selection).exists():
        result = {
            "passed": False,
            "allow_placeholders": args.allow_placeholders,
            "selected_model": None,
            "api_config_model": None,
            "checks": [
                {
                    "check": "selection_file_exists",
                    "passed": False,
                    "path": args.selection,
                }
            ],
        }
        if args.out:
            write_json(Path(args.out), result)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        raise SystemExit(1)
    selection = read_json(Path(args.selection))
    api_config = read_json(Path(args.api_config)) if args.api_config else None
    result = validate(selection, api_config, args.allow_placeholders)
    if args.out:
        write_json(Path(args.out), result)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
