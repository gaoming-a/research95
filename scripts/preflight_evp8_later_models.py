"""Preflight EVP-8 later-model OpenRouter local config without model calls.

The checker reads the ignored local config and `.env` only to determine whether
the required OpenRouter key name is present. It never prints key values, never
calls a model API, and never generates raw outputs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "evp8_later_models.local.json"
DEFAULT_OUT = REPO_ROOT / "data" / "protocols" / "evp8_later_model_preflight_summary_v0_1.json"
EXPECTED_API_KEY_ENVS = ["OPENROUTER_API_KEY"]
EXPECTED_MODELS = ["moonshotai/kimi-k2.6", "mistralai/devstral-2512", "google/gemini-2.5-flash"]
MODEL_VISIBLE_LEVELS = ["E0", "E1", "E2", "E3", "E4", "E5", "E6"]


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _resolve(path_value: Any) -> Path:
    path = Path(str(path_value))
    return path if path.is_absolute() else REPO_ROOT / path


def _display(path: Path) -> str:
    absolute = path if path.is_absolute() else REPO_ROOT / path
    try:
        return absolute.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(absolute)


def _is_placeholder(value: Any) -> bool:
    text = str(value).strip()
    return not text or text.startswith("<") or text.endswith(">") or "your-" in text.lower()


def _load_env_key_states(path: Path, keys: list[str]) -> tuple[dict[str, str], bool]:
    if not path.exists():
        return {key: "missing" for key in keys}, False
    present: dict[str, str] = {key: "missing" for key in keys}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            raise ValueError(f"invalid env line at {_display(path)}:{line_number}")
        key, value = stripped.split("=", 1)
        key = key.strip()
        if key in present:
            value = value.strip().strip("\"'")
            present[key] = "set" if value and not _is_placeholder(value) else "missing_or_placeholder"
    return present, True


def _gitignore_allows_local_config(path: Path) -> bool:
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    absolute = path if path.is_absolute() else REPO_ROOT / path
    return absolute.parent == REPO_ROOT / "configs" and absolute.name.endswith(".local.json") and "configs/*.local.json" in gitignore


def _check(name: str, passed: bool, detail: Any, category: str = "structural") -> dict[str, Any]:
    return {
        "check": name,
        "passed": bool(passed),
        "detail": detail,
        "category": category,
    }


def _file_check(config: dict[str, Any], key: str) -> dict[str, Any]:
    path = _resolve(config.get(key, ""))
    return _check(f"{key}_exists", path.exists(), _display(path))


def _output_path_check(config: dict[str, Any], key: str) -> dict[str, Any]:
    value = (config.get(key) or {}).get("output_dir")
    path = Path(str(value))
    return _check(
        f"{key}_output_dir_ignored_boundary",
        bool(value) and not path.is_absolute() and path.parts and path.parts[0] == "outputs",
        value,
    )


def _protocol_later_model_ids(protocol: dict[str, Any]) -> list[str]:
    phase2 = ((protocol.get("model_plan") or {}).get("phase2_later_batch")) or []
    return [str(item.get("model_id")) for item in phase2]


def _catalog_ids(catalog: dict[str, Any]) -> list[str]:
    return [str(item.get("slug")) for item in catalog.get("results") or []]


def _provider_pref_checks(models: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for model in models:
        model_id = model.get("model_id")
        prefs = model.get("provider_preferences") or {}
        checks.append(
            _check(
                f"{model_id}_provider_allow_fallbacks_false",
                prefs.get("allow_fallbacks") is False,
                prefs.get("allow_fallbacks"),
            )
        )
        checks.append(
            _check(
                f"{model_id}_provider_require_parameters_true",
                prefs.get("require_parameters") is True,
                prefs.get("require_parameters"),
            )
        )
    return checks


def preflight(config_path: Path, allow_missing_credentials: bool = False) -> dict[str, Any]:
    config_path = config_path if config_path.is_absolute() else REPO_ROOT / config_path
    config = _load_json(config_path)
    spec = _load_json(_resolve(config["protocol_spec"]))
    audit = _load_json(_resolve(config["protocol_audit_summary"]))
    candidate_set = _load_json(_resolve(config["candidate_set"]))
    prompt_manifest = _load_json(_resolve(config["prompt_manifest"]))
    cost_summary = _load_json(_resolve(config["cost_observability_dry_run"]))
    baseline_summary = _load_json(_resolve(config["deterministic_tool_baseline_dry_run"]))
    catalog_audit = _load_json(_resolve(config["openrouter_catalog_audit"]))

    models = config.get("models") or []
    model_ids = [str(model.get("model_id")) for model in models]
    request_model_ids = [str(model.get("request_model_id")) for model in models]
    provider_routes = [str(model.get("provider_route")) for model in models]
    api_key_envs = sorted({str(model.get("api_key_env")) for model in models})
    protocol_later_models = _protocol_later_model_ids(spec)

    checks: list[dict[str, Any]] = []
    checks.append(_check("config_path_is_ignored_local", _gitignore_allows_local_config(config_path), _display(config_path)))
    for key in (
        "protocol_spec",
        "protocol_audit_summary",
        "candidate_set",
        "prompt_template",
        "prompt_manifest",
        "prompt_boundary_audit",
        "packet_dry_run_summary",
        "schema_dry_run_summary",
        "cost_observability_dry_run",
        "deterministic_tool_baseline_dry_run",
        "openrouter_catalog_audit",
    ):
        checks.append(_file_check(config, key))
    checks.extend(
        [
            _check("protocol_audit_ready_for_preflight", audit.get("phase0_api_readiness") == "ready_for_api_preflight", audit.get("phase0_api_readiness")),
            _check("protocol_audit_no_api", audit.get("api_call_attempted") is False, audit.get("api_call_attempted")),
            _check("phase2_model_ids", model_ids == EXPECTED_MODELS, model_ids),
            _check("request_model_ids_match_model_ids", request_model_ids == model_ids, request_model_ids),
            _check("protocol_phase2_model_ids", protocol_later_models == EXPECTED_MODELS, protocol_later_models),
            _check("provider_routes", provider_routes == ["openrouter_pinned_exact_model_id"] * 3, provider_routes),
            _check("api_key_env_names", api_key_envs == EXPECTED_API_KEY_ENVS, api_key_envs),
            _check("openrouter_catalog_available", catalog_audit.get("all_available") is True, catalog_audit.get("all_available")),
            _check("openrouter_catalog_ids", _catalog_ids(catalog_audit) == EXPECTED_MODELS, _catalog_ids(catalog_audit)),
            _check("openrouter_metadata_header", config.get("openrouter_metadata_header") == "enabled", config.get("openrouter_metadata_header")),
            _check("prompt_id", prompt_manifest.get("prompt_id") == spec.get("prompt_policy", {}).get("prompt_id"), prompt_manifest.get("prompt_id")),
            _check(
                "prompt_template_hash",
                prompt_manifest.get("prompt_template_sha256") == spec.get("prompt_policy", {}).get("prompt_template_sha256"),
                prompt_manifest.get("prompt_template_sha256"),
            ),
            _check("candidate_count", candidate_set.get("records") and len(candidate_set["records"]) == 98, len(candidate_set.get("records") or [])),
            _check("temperature", config.get("temperature") == spec.get("routing_policy", {}).get("temperature"), config.get("temperature")),
            _check("max_output_tokens", config.get("max_output_tokens") == spec.get("routing_policy", {}).get("max_output_tokens"), config.get("max_output_tokens")),
            _check("execution_requires_explicit_execute_flag", config.get("execution_requires_explicit_execute_flag") is True, config.get("execution_requires_explicit_execute_flag")),
            _check("api_execution_not_authorized_by_config", config.get("api_execution_authorized") is False, config.get("api_execution_authorized")),
            _check("raw_output_policy", config.get("raw_output_policy") == "ignored_outputs_only", config.get("raw_output_policy")),
            _check("overwrite_policy", config.get("overwrite_policy") == "refuse_if_output_exists", config.get("overwrite_policy")),
            _check("record_actual_model_id", config.get("record_actual_model_id") is True, config.get("record_actual_model_id")),
            _check("record_actual_provider", config.get("record_actual_provider") is True, config.get("record_actual_provider")),
            _check("record_openrouter_metadata", config.get("record_openrouter_metadata") is True, config.get("record_openrouter_metadata")),
            _check("record_cost_source", config.get("record_cost_source") is True, config.get("record_cost_source")),
            _check("record_cost_currency", config.get("record_cost_currency") is True, config.get("record_cost_currency")),
            _check("record_provider_cost_usd", config.get("record_provider_cost_usd") is True, config.get("record_provider_cost_usd")),
            _check("planning_cost_ceiling_usd", config.get("planning_cost_ceiling_usd") == 30.0, config.get("planning_cost_ceiling_usd")),
        ]
    )
    checks.extend(_provider_pref_checks(models))
    checks.append(_output_path_check(config, "full"))

    full = config.get("full") or {}
    checks.extend(
        [
            _check("full_levels", full.get("levels") == MODEL_VISIBLE_LEVELS, full.get("levels")),
            _check("full_candidate_count", full.get("candidate_count") == 98, full.get("candidate_count")),
            _check("full_planned_calls_per_model", full.get("planned_calls_per_model") == 686, full.get("planned_calls_per_model")),
            _check("cost_dry_run_status", cost_summary.get("cost_observability_dry_run_status") == "passed", cost_summary.get("cost_observability_dry_run_status")),
            _check("cost_planned_calls_per_model", cost_summary.get("planned_calls_per_model") == 686, cost_summary.get("planned_calls_per_model")),
            _check("baseline_dry_run_status", baseline_summary.get("deterministic_tool_baseline_dry_run_status") == "passed", baseline_summary.get("deterministic_tool_baseline_dry_run_status")),
            _check("baseline_planned_record_count", baseline_summary.get("planned_baseline_record_count") == 686, baseline_summary.get("planned_baseline_record_count")),
        ]
    )

    retry = config.get("retry_policy") or {}
    expected_retry = spec.get("routing_policy", {}).get("retry_policy") or {}
    checks.extend(
        _check(f"retry_policy_{key}", retry.get(key) == expected_retry.get(key), retry.get(key))
        for key in ("max_retries_per_record", "retry_only_on_transport_or_rate_limit", "no_silent_retry_for_parse_invalid")
    )

    env_key_states, env_file_exists = _load_env_key_states(_resolve(config.get("env", ".env")), EXPECTED_API_KEY_ENVS)
    credentials_ready = env_file_exists and all(state == "set" for state in env_key_states.values())
    checks.append(
        _check(
            "credential_key_presence",
            credentials_ready or allow_missing_credentials,
            {
                "env_file_exists": env_file_exists,
                "key_states": env_key_states,
                "values_printed": False,
            },
            category="credential_presence",
        )
    )

    structural_ready = all(check["passed"] for check in checks if check["category"] == "structural")
    strict_preflight_ready = structural_ready and credentials_ready
    result = {
        "cohort_id": "EVP-8",
        "config": _display(config_path),
        "config_id": config.get("config_id"),
        "protocol_id": spec.get("protocol_id"),
        "candidate_set_id": candidate_set.get("candidate_set_id"),
        "preflight_status": "passed" if strict_preflight_ready else "structural_only" if structural_ready else "blocked",
        "structural_ready": structural_ready,
        "credential_presence_ready": credentials_ready,
        "ready_for_user_execute_command": strict_preflight_ready,
        "api_call_attempted": False,
        "raw_outputs_generated": False,
        "api_key_values_printed": False,
        "local_config_content_stored_in_tracked_summary": False,
        "planned_later_model_ids": model_ids,
        "planned_calls_per_later_model": full.get("planned_calls_per_model"),
        "planned_total_later_model_calls": int(full.get("planned_calls_per_model") or 0) * len(models),
        "checks": checks,
        "next_step": (
            "Wait for explicit per-model execution command after strict preflight."
            if strict_preflight_ready
            else "Use structural check-only until OPENROUTER_API_KEY is available; do not call model APIs."
            if structural_ready
            else "Fix blocked preflight checks before any model call."
        ),
        "boundary": "Passing this preflight does not call or authorize API execution by itself.",
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--allow-missing-credentials", action="store_true")
    parser.add_argument("--strict-api-ready", action="store_true")
    args = parser.parse_args()

    result = preflight(args.config, allow_missing_credentials=args.allow_missing_credentials)
    _write_json(args.out, result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    if not result["structural_ready"]:
        return 1
    if args.strict_api_ready and not result["ready_for_user_execute_command"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
