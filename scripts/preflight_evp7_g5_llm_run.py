"""Preflight the EVP-7 G5 LLM run configuration without API calls.

This checker validates structural readiness for the future G5 LLM verifier run.
It does not read credentials, does not load .env, and never calls a model API.
Strict API readiness remains false until the user fills provider/model/cost,
smoke scope, and full-run permission in an ignored local config.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EXPECTED_PROMPT_ID = "patch_verify_evidence_visibility_merge_gate_v1"
EXPECTED_LEVEL_COUNTS = {"E0": 42, "E2": 42, "E4": 42, "E6": 42}
EXPECTED_RECORD_COUNT = 168
ALLOWED_CONDITIONS = {"evidence_visibility_merge_gate"}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def is_placeholder(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, bool):
        return not value
    text = str(value).strip()
    return not text or text.startswith("<") or text.endswith(">") or "user-confirmed" in text


def check_file(config: dict[str, Any], key: str) -> dict[str, Any]:
    path = Path(str(config.get(key, "")))
    exists = path.exists()
    return {
        "check": f"{key}_exists",
        "passed": exists,
        "path": str(path),
        "detail": "exists" if exists else "missing",
        "category": "structural",
    }


def counts(values: Any) -> dict[str, int]:
    result: dict[str, int] = {}
    for value in values:
        key = str(value)
        result[key] = result.get(key, 0) + 1
    return dict(sorted(result.items()))


def preflight(config_path: Path) -> dict[str, Any]:
    config = read_json(config_path)
    checks: list[dict[str, Any]] = []

    for key in ("evidence_packets", "prompt_manifest", "run_readiness", "metrics_scaffold", "candidates"):
        checks.append(check_file(config, key))

    checks.extend(config_checks(config))
    checks.extend(artifact_checks(config))

    structural_ready = all(check["passed"] for check in checks if check["category"] == "structural")
    api_ready = structural_ready and all(check["passed"] for check in checks)
    return {
        "config": str(config_path),
        "structural_ready": structural_ready,
        "api_ready": api_ready,
        "api_call_attempted": False,
        "checks": checks,
        "next_required_user_confirmation": [
            "api_provider",
            "model",
            "max_total_cost_usd",
            "smoke_scope",
            "full_run_permission",
        ],
    }


def config_checks(config: dict[str, Any]) -> list[dict[str, Any]]:
    conditions = config.get("conditions")
    valid_conditions = (
        isinstance(conditions, list)
        and bool(conditions)
        and all(isinstance(condition, str) and condition in ALLOWED_CONDITIONS for condition in conditions)
    )
    return [
        {
            "check": "prompt_id",
            "passed": config.get("prompt_id") == EXPECTED_PROMPT_ID,
            "detail": config.get("prompt_id"),
            "category": "structural",
        },
        {
            "check": "conditions",
            "passed": valid_conditions,
            "detail": {
                "conditions": conditions,
                "allowed_conditions": sorted(ALLOWED_CONDITIONS),
            },
            "category": "structural",
        },
        {
            "check": "decoding_temperature",
            "passed": config.get("temperature") == 0.0,
            "detail": config.get("temperature"),
            "category": "structural",
        },
        {
            "check": "decoding_max_tokens",
            "passed": isinstance(config.get("max_tokens"), int) and int(config["max_tokens"]) > 0,
            "detail": config.get("max_tokens"),
            "category": "structural",
        },
        {
            "check": "api_provider_confirmed",
            "passed": not is_placeholder(config.get("api_provider")),
            "detail": config.get("api_provider"),
            "category": "user_confirmation",
        },
        {
            "check": "model_confirmed",
            "passed": not is_placeholder(config.get("model")),
            "detail": config.get("model"),
            "category": "user_confirmation",
        },
        {
            "check": "max_total_cost_usd_confirmed",
            "passed": _positive_number(config.get("max_total_cost_usd")),
            "detail": config.get("max_total_cost_usd"),
            "category": "user_confirmation",
        },
        {
            "check": "smoke_scope_confirmed",
            "passed": not is_placeholder(config.get("smoke_scope")),
            "detail": config.get("smoke_scope"),
            "category": "user_confirmation",
        },
        {
            "check": "full_run_permission_confirmed",
            "passed": config.get("full_run_permission") is True,
            "detail": config.get("full_run_permission"),
            "category": "user_confirmation",
        },
    ]


def artifact_checks(config: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    prompt_manifest_path = Path(str(config.get("prompt_manifest", "")))
    readiness_path = Path(str(config.get("run_readiness", "")))
    metrics_path = Path(str(config.get("metrics_scaffold", "")))
    evidence_path = Path(str(config.get("evidence_packets", "")))
    candidates_path = Path(str(config.get("candidates", "")))

    if prompt_manifest_path.exists():
        records = read_jsonl(prompt_manifest_path)
        level_counts = counts(record.get("evidence_level") for record in records)
        leakage_failed = sum(1 for record in records if record.get("label_leakage_check") != "passed")
        prompt_ids = sorted({record.get("prompt_id") for record in records})
        prompt_text_stored = any(record.get("prompt_text_stored") is not False for record in records)
        checks.extend(
            [
                _structural_check("prompt_manifest_record_count", len(records) == EXPECTED_RECORD_COUNT, len(records)),
                _structural_check("prompt_manifest_level_counts", level_counts == EXPECTED_LEVEL_COUNTS, level_counts),
                _structural_check("prompt_manifest_prompt_id", prompt_ids == [EXPECTED_PROMPT_ID], prompt_ids),
                _structural_check("prompt_manifest_leakage", leakage_failed == 0, {"failed": leakage_failed}),
                _structural_check("prompt_text_not_stored", not prompt_text_stored, {"prompt_text_stored_any": prompt_text_stored}),
            ]
        )

    if readiness_path.exists():
        readiness = read_json(readiness_path)
        checks.extend(
            [
                _structural_check("run_readiness_status", readiness.get("g5_llm_run_readiness") == "passed_without_api", readiness.get("g5_llm_run_readiness")),
                _structural_check("run_readiness_api_not_attempted", readiness.get("api_call_attempted") is False, readiness.get("api_call_attempted")),
                _structural_check("run_readiness_prompt_count", readiness.get("prompt_record_count") == EXPECTED_RECORD_COUNT, readiness.get("prompt_record_count")),
                _structural_check("run_readiness_level_counts", readiness.get("level_counts") == EXPECTED_LEVEL_COUNTS, readiness.get("level_counts")),
            ]
        )

    if metrics_path.exists():
        metrics = read_json(metrics_path)
        checks.extend(
            [
                _structural_check("metric_scaffold_status", metrics.get("g5_metric_scaffold") == "passed", metrics.get("g5_metric_scaffold")),
                _structural_check(
                    "metric_signal_boundary",
                    metrics.get("g5_signal_claim_status") == "requires_real_llm_verifier_outputs",
                    metrics.get("g5_signal_claim_status"),
                ),
            ]
        )

    if evidence_path.exists() and candidates_path.exists():
        evidence_count = len(read_jsonl(evidence_path))
        candidate_count = len(read_jsonl(candidates_path))
        checks.extend(
            [
                _structural_check("evidence_packet_count", evidence_count == EXPECTED_RECORD_COUNT, evidence_count),
                _structural_check("candidate_count", candidate_count == 42, candidate_count),
            ]
        )

    return checks


def _structural_check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {
        "check": name,
        "passed": passed,
        "detail": detail,
        "category": "structural",
    }


def _positive_number(value: Any) -> bool:
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/evp7_g5_llm.example.json"))
    parser.add_argument("--out", type=Path, help="Optional JSON output path.")
    parser.add_argument("--strict-api-ready", action="store_true", help="Fail if user-confirmation checks are still pending.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = preflight(args.config)
    if args.out:
        write_json(args.out, result)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if not result["structural_ready"]:
        return 1
    if args.strict_api_ready and not result["api_ready"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
