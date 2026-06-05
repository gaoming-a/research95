from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PLACEHOLDER_PREFIX = "<"
PLACEHOLDER_SUFFIX = ">"
PROVIDER_CREDENTIALS = {
    "openrouter": {
        "api_key_env": "OPENROUTER_API_KEY",
        "base_url_env": "OPENROUTER_BASE_URL",
    },
    "deepseek_official": {
        "api_key_env": "DEEPSEEK_API_KEY",
        "base_url_env": "DEEPSEEK_BASE_URL",
    },
}
ALLOWED_CONDITIONS = {
    "llm_only",
    "evidence_first",
    "tool_augmented_evidence",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def read_jsonl_count(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def load_env_keys(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            raise ValueError(f"invalid env line at {path}:{line_number}")
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def is_placeholder(value: str | None) -> bool:
    if not value:
        return True
    stripped = value.strip()
    return (
        stripped.startswith(PLACEHOLDER_PREFIX)
        or stripped.endswith(PLACEHOLDER_SUFFIX)
        or "your-" in stripped.lower()
        or "model-slug" in stripped.lower()
    )


def check_file(path: Path, label: str) -> dict[str, Any]:
    exists = path.exists()
    return {
        "check": label,
        "passed": exists,
        "path": str(path),
        "detail": "exists" if exists else "missing",
    }


def preflight(config_path: Path, allow_missing_credentials: bool) -> dict[str, Any]:
    config = read_json(config_path)
    checks: list[dict[str, Any]] = []

    candidates = Path(config["candidates"])
    evidence_packets = Path(config["evidence_packets"])
    validation_summary_path = Path(config["validation_summary"])
    env_path = Path(config.get("env", ".env"))
    model_selection_path = Path(config["model_selection"]) if config.get("model_selection") else None

    for label, path in [
        ("candidates", candidates),
        ("evidence_packets", evidence_packets),
        ("validation_summary", validation_summary_path),
    ]:
        checks.append(check_file(path, label))

    api_provider = str(config.get("api_provider", "openrouter"))
    provider = PROVIDER_CREDENTIALS.get(api_provider)
    checks.append(
        {
            "check": "api_provider",
            "passed": provider is not None,
            "detail": api_provider,
        }
    )

    model = str(config.get("model", ""))
    model_ok = not is_placeholder(model)
    checks.append(
        {
            "check": "model_identifier",
            "passed": model_ok,
            "detail": "set" if model_ok else "missing_or_placeholder",
        }
    )

    if model_selection_path:
        checks.append(check_file(model_selection_path, "model_selection"))
        if model_selection_path.exists():
            model_selection = read_json(model_selection_path)
            primary = model_selection.get("primary_pilot_model", {})
            selected_model = selected_model_id(primary) if isinstance(primary, dict) else None
            checks.append(
                {
                    "check": "model_selection_matches_config",
                    "passed": selected_model == model and model_ok,
                    "detail": {
                        "selected_model": selected_model,
                        "config_model": model,
                    },
                }
            )
        else:
            checks.append(
                {
                    "check": "model_selection_matches_config",
                    "passed": False,
                    "detail": "missing model selection file",
                }
            )

    env_values = load_env_keys(env_path)
    api_key_env = provider["api_key_env"] if provider else "UNKNOWN_API_KEY"
    base_url_env = provider["base_url_env"] if provider else "UNKNOWN_BASE_URL"
    key_ok = not is_placeholder(env_values.get(api_key_env))
    checks.append(
        {
            "check": "api_key",
            "passed": key_ok or allow_missing_credentials,
            "path": str(env_path),
            "detail": {
                "api_provider": api_provider,
                "api_key_env": api_key_env,
                "base_url_env": base_url_env,
                "state": "set" if key_ok else "missing_or_placeholder",
            },
            "required_for_api_call": True,
        }
    )

    if validation_summary_path.exists():
        validation_summary = read_json(validation_summary_path)
        all_validated = bool(validation_summary.get("all_validated"))
        checks.append(
            {
                "check": "candidate_validation",
                "passed": all_validated,
                "detail": validation_summary,
            }
        )
    else:
        checks.append({"check": "candidate_validation", "passed": False, "detail": "missing summary"})

    if candidates.exists() and evidence_packets.exists():
        candidate_count = read_jsonl_count(candidates)
        evidence_count = read_jsonl_count(evidence_packets)
        checks.append(
            {
                "check": "candidate_evidence_count_match",
                "passed": candidate_count == evidence_count and candidate_count > 0,
                "detail": {
                    "candidate_count": candidate_count,
                    "evidence_packet_count": evidence_count,
                },
            }
        )

    conditions = config.get("conditions", [])
    valid_conditions = (
        isinstance(conditions, list)
        and bool(conditions)
        and all(isinstance(condition, str) and condition in ALLOWED_CONDITIONS for condition in conditions)
    )
    checks.append(
        {
            "check": "conditions",
            "passed": valid_conditions,
            "detail": {
                "conditions": conditions,
                "allowed_conditions": sorted(ALLOWED_CONDITIONS),
            },
        }
    )

    api_ready = all(check["passed"] for check in checks)
    dry_run_ready = all(
        check["passed"]
        for check in checks
        if check["check"] not in {"api_key", "model_slug"}
    )
    return {
        "config": str(config_path),
        "api_ready": api_ready,
        "dry_run_ready": dry_run_ready,
        "checks": checks,
    }


def selected_model_id(primary: dict[str, Any]) -> Any:
    return primary.get("model_id") or primary.get("openrouter_slug")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check readiness for the patch-verification API pilot.")
    parser.add_argument("--config", required=True, help="API pilot config JSON.")
    parser.add_argument(
        "--allow-missing-credentials",
        action="store_true",
        help="Allow missing API key for dry-run readiness checks.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = preflight(Path(args.config), args.allow_missing_credentials)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if not result["api_ready"] and not args.allow_missing_credentials:
        raise SystemExit(1)
    if not result["dry_run_ready"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
