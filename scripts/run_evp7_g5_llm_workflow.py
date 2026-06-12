"""Guarded EVP-7 G5 LLM workflow.

This workflow provides check-only and mock validation for the future G5 LLM
run. Real API execution is supported only behind strict preflight and an
explicit --execute flag; the tracked example config is intentionally not
API-ready.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from cross_review.env import load_env_file  # noqa: E402
from cross_review.openrouter import DeepSeekClient, OpenRouterClient, redact_sensitive_text  # noqa: E402
from cross_review.parsing import extract_json_object, response_text  # noqa: E402

import analyze_evp7_schema_dry_run_metrics as metrics_module  # noqa: E402
import build_evp7_g5_llm_prompt_manifest as prompt_module  # noqa: E402
import preflight_evp7_g5_llm_run as preflight_module  # noqa: E402
import run_evp7_merge_gate_schema_dry_run as schema_module  # noqa: E402


DEFAULT_CONFIG = Path("configs") / "evp7_g5_llm.example.json"
DEFAULT_CHECK_SUMMARY_OUT = REPO_ROOT / "data" / "reviews" / "evp7_g5_workflow_check_only_example.json"
DEFAULT_MOCK_REVIEWS_OUT = REPO_ROOT / "data" / "reviews" / "evp7_g5_workflow_mock_reviews.jsonl"
DEFAULT_MOCK_METRICS_OUT = REPO_ROOT / "data" / "reviews" / "evp7_g5_workflow_mock_metrics.json"
DEFAULT_MOCK_SUMMARY_OUT = REPO_ROOT / "data" / "reviews" / "evp7_g5_workflow_mock_summary.json"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )


def packets_for_run(config: dict[str, Any], limit: int | None) -> list[dict[str, Any]]:
    packets = read_jsonl(REPO_ROOT / str(config["evidence_packets"]))
    if limit is None or limit == 0:
        return packets
    return packets[:limit]


def normalize_provider_response(response: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None, str]:
    text = response_text(response)
    try:
        parsed = extract_json_object(text)
    except Exception as exc:  # noqa: BLE001
        return None, f"invalid_json:{exc}", text
    error = schema_module._validate_schema(parsed)
    return parsed, error, text


def mock_provider_response(packet: dict[str, Any], policy: str) -> dict[str, Any]:
    if policy == "schema_visible_rule":
        parsed = schema_module._schema_output(packet)
    elif policy == "escalate_all":
        parsed = {
            "decision": "escalate",
            "confidence": 0.5,
            "primary_reason": "Mock escalation for workflow validation only.",
            "evidence_used": ["mock_policy"],
            "risk_flags": ["insufficient_evidence"],
            "suspected_failure_type": "unknown",
            "human_review_needed": True,
        }
    else:
        raise ValueError(f"unsupported mock policy: {policy}")
    return {
        "choices": [{"message": {"content": json.dumps(parsed, ensure_ascii=False, sort_keys=True)}}],
        "usage": {"cost": 0.0, "mock": True},
        "mock_policy": policy,
    }


def review_record(
    *,
    packet: dict[str, Any],
    prompt: str,
    response: dict[str, Any],
    model: str,
    api_provider: str,
    mock_run: bool,
) -> dict[str, Any]:
    parsed, invalid_reason, raw_text = normalize_provider_response(response)
    return {
        "review_id": f"{packet['evidence_packet_id']}__evidence_visibility_merge_gate",
        "evidence_packet_id": packet["evidence_packet_id"],
        "candidate_id": packet["model_visible"]["candidate_id"],
        "cohort_id": packet["cohort_id"],
        "evidence_level": packet["evidence_level"],
        "verifier_id": f"evidence_visibility_merge_gate__{_safe(model)}",
        "condition": "evidence_visibility_merge_gate",
        "prompt_id": prompt_module.PROMPT_ID,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "prompt_chars": len(prompt),
        "model": model,
        "api_provider": api_provider,
        "mock_run": mock_run,
        "api_call_attempted": not mock_run,
        "raw_response_text": raw_text,
        "parsed_output": parsed,
        "parse_status": "valid" if invalid_reason is None else "invalid",
        "invalid_reason": invalid_reason,
        "cost_usd": _cost(response),
        "run_date_utc": datetime.now(timezone.utc).isoformat(),
    }


def _safe(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def _cost(response: dict[str, Any]) -> float:
    usage = response.get("usage", {})
    if not isinstance(usage, dict):
        return 0.0
    try:
        return float(usage.get("cost") or 0.0)
    except (TypeError, ValueError):
        return 0.0


def run_check_only(args: argparse.Namespace) -> dict[str, Any]:
    preflight = preflight_module.preflight(args.config)
    summary = {
        "mode": "check_only",
        "config": _display_path(args.config),
        "structural_ready": preflight["structural_ready"],
        "api_ready": preflight["api_ready"],
        "model_call_attempted": False,
        "api_call_attempted": False,
        "next_required_user_confirmation": preflight["next_required_user_confirmation"],
        "preflight": preflight,
    }
    write_json(_abs(args.summary_out or DEFAULT_CHECK_SUMMARY_OUT), summary)
    return summary


def run_mock(args: argparse.Namespace) -> dict[str, Any]:
    config = read_json(args.config)
    preflight = preflight_module.preflight(args.config)
    if not preflight["structural_ready"]:
        raise SystemExit("mock workflow requires structural preflight readiness")
    records = []
    for packet in packets_for_run(config, args.limit):
        prompt = prompt_module.render_prompt(packet)
        findings = prompt_module.boundary_findings(prompt)
        if findings:
            raise SystemExit(f"prompt boundary failed for {packet['evidence_packet_id']}: {findings}")
        records.append(
            review_record(
                packet=packet,
                prompt=prompt,
                response=mock_provider_response(packet, args.mock_policy),
                model=f"mock::{args.mock_policy}",
                api_provider="mock",
                mock_run=True,
            )
        )
    reviews_out = _abs(args.reviews_out or DEFAULT_MOCK_REVIEWS_OUT)
    metrics_out = _abs(args.metrics_out or DEFAULT_MOCK_METRICS_OUT)
    summary_out = _abs(args.summary_out or DEFAULT_MOCK_SUMMARY_OUT)
    write_jsonl(reviews_out, records)
    metrics = metrics_module.build_metrics(reviews_out, REPO_ROOT / str(config["candidates"]))
    write_json(metrics_out, metrics)
    summary = {
        "mode": "mock",
        "mock_run": True,
        "mock_policy": args.mock_policy,
        "config": _display_path(args.config),
        "review_count": len(records),
        "reviews_out": _display_path(reviews_out),
        "metrics_out": _display_path(metrics_out),
        "api_call_attempted": False,
        "model_call_attempted": False,
        "g5_metric_scaffold": metrics["g5_metric_scaffold"],
        "g5_signal_claim_status": metrics["g5_signal_claim_status"],
        "preflight_structural_ready": preflight["structural_ready"],
        "preflight_api_ready": preflight["api_ready"],
    }
    write_json(summary_out, summary)
    return summary


def run_execute(args: argparse.Namespace) -> dict[str, Any]:
    config = read_json(args.config)
    preflight = preflight_module.preflight(args.config)
    if not preflight["api_ready"]:
        raise SystemExit(
            "G5 workflow stopped before API call because strict API readiness is false:\n"
            + json.dumps(preflight["next_required_user_confirmation"], ensure_ascii=False, indent=2)
        )
    if not args.execute:
        raise SystemExit("Strict preflight passed, but --execute is required before model calls.")
    if args.config.name.endswith(".example.json"):
        raise SystemExit("Refusing to execute with tracked example config. Use an ignored local config.")
    if args.concurrency < 1:
        raise SystemExit("--concurrency must be >= 1")

    load_env_file(str(config.get("env", ".env")))
    packets = packets_for_run(config, args.limit)
    _validate_prompt_boundaries(packets)
    records = _execute_packets(packets, config, args.concurrency)
    max_total_cost = float(config["max_total_cost_usd"])
    if sum(float(item.get("cost_usd") or 0.0) for item in records) > max_total_cost:
        raise SystemExit("G5 workflow stopped because observed cost exceeded max_total_cost_usd.")

    reviews_out = _abs(args.reviews_out or Path(config["out_dir"]) / "reviews.jsonl")
    metrics_out = _abs(args.metrics_out or Path(config["out_dir"]) / "metrics.json")
    summary_out = _abs(args.summary_out or Path(config["out_dir"]) / "workflow_summary.json")
    write_jsonl(reviews_out, records)
    metrics = metrics_module.build_metrics(reviews_out, REPO_ROOT / str(config["candidates"]))
    write_json(metrics_out, metrics)
    summary = {
        "mode": "executed",
        "config": _display_path(args.config),
        "review_count": len(records),
        "reviews_out": _display_path(reviews_out),
        "metrics_out": _display_path(metrics_out),
        "api_call_attempted": True,
        "model_call_attempted": True,
        "concurrency": args.concurrency,
        "total_cost_usd": round(sum(float(item.get("cost_usd") or 0.0) for item in records), 6),
        "g5_signal_claim_status": metrics["g5_signal_claim_status"],
    }
    write_json(summary_out, summary)
    return summary


def _validate_prompt_boundaries(packets: list[dict[str, Any]]) -> None:
    for packet in packets:
        prompt = prompt_module.render_prompt(packet)
        findings = prompt_module.boundary_findings(prompt)
        if findings:
            raise SystemExit(f"prompt boundary failed for {packet['evidence_packet_id']}: {findings}")


def _execute_packets(packets: list[dict[str, Any]], config: dict[str, Any], concurrency: int) -> list[dict[str, Any]]:
    if concurrency == 1:
        return [_execute_one_packet(packet, config) for packet in packets]

    ordered_records: list[dict[str, Any] | None] = [None] * len(packets)
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {
            executor.submit(_execute_one_packet, packet, config): index
            for index, packet in enumerate(packets)
        }
        for future in as_completed(futures):
            index = futures[future]
            ordered_records[index] = future.result()
    return [record for record in ordered_records if record is not None]


def _execute_one_packet(packet: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    prompt = prompt_module.render_prompt(packet)
    client = _client(str(config["api_provider"]))
    response = client.chat_completion(
        model=str(config["model"]),
        prompt=prompt,
        temperature=float(config.get("temperature", 0.0)),
        max_tokens=int(config.get("max_tokens", 1024)),
    )
    return review_record(
        packet=packet,
        prompt=prompt,
        response=response,
        model=str(config["model"]),
        api_provider=str(config["api_provider"]),
        mock_run=False,
    )


def _client(api_provider: str) -> OpenRouterClient | DeepSeekClient:
    if api_provider == "openrouter":
        return OpenRouterClient()
    if api_provider == "deepseek_official":
        return DeepSeekClient()
    raise SystemExit(f"unsupported api provider for execution: {api_provider}")


def _abs(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def _display_path(path: Path) -> str:
    absolute = _abs(path)
    try:
        return str(absolute.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--mock-policy", choices=["schema_visible_rule", "escalate_all"])
    parser.add_argument("--limit", type=int, help="Optional packet limit. Use 0 or omit for all packets.")
    parser.add_argument("--reviews-out", type=Path)
    parser.add_argument("--metrics-out", type=Path)
    parser.add_argument("--summary-out", type=Path)
    parser.add_argument("--concurrency", type=int, default=1, help="Execute model calls with this bounded concurrency. Default: 1.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    modes = sum(bool(value) for value in (args.check_only, args.mock_policy, args.execute))
    if modes != 1:
        raise SystemExit("Choose exactly one mode: --check-only, --mock-policy, or --execute.")
    if args.check_only:
        summary = run_check_only(args)
    elif args.mock_policy:
        summary = run_mock(args)
    else:
        summary = run_execute(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
