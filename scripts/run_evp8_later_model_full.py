"""Guarded EVP-8 later-model full runner.

The default path is check-only and does not call model APIs. Real calls require
an ignored local config, strict preflight, an explicit --execute flag, and a
single configured OpenRouter model id.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
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
from cross_review.openrouter import OpenRouterClient  # noqa: E402
from cross_review.parsing import extract_json_object, response_text  # noqa: E402

import build_evp8_prompt_manifest as prompt_module  # noqa: E402
import preflight_evp8_later_models as preflight_module  # noqa: E402
import run_evp8_deepseek_qwen_smoke as evp8_core  # noqa: E402


DEFAULT_CONFIG = REPO_ROOT / "configs" / "evp8_later_models.local.json"
DEFAULT_CHECK_SUMMARY_OUT = REPO_ROOT / "data" / "protocols" / "evp8_later_model_full_check_only_v0_1.json"
DEFAULT_EXEC_SUMMARY_DIR = REPO_ROOT / "data" / "reviews"
MODEL_VISIBLE_LEVELS = ("E0", "E1", "E2", "E3", "E4", "E5", "E6")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{display_path(path)} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_jsonl_record(handle: Any, record: dict[str, Any]) -> None:
    handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    handle.flush()


def resolve(path_value: Any) -> Path:
    path = Path(str(path_value))
    return path if path.is_absolute() else REPO_ROOT / path


def display_path(path: Path) -> str:
    absolute = path if path.is_absolute() else REPO_ROOT / path
    try:
        return absolute.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(absolute)


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def check_only(args: argparse.Namespace) -> dict[str, Any]:
    config = read_json(args.config)
    preflight = preflight_module.preflight(args.config, allow_missing_credentials=args.allow_missing_credentials)
    if not preflight["structural_ready"]:
        raise SystemExit("EVP-8 later-model check-only requires structural preflight readiness.")
    if not args.allow_missing_credentials and not preflight["ready_for_user_execute_command"]:
        raise SystemExit("EVP-8 later-model check-only requires strict local preflight unless --allow-missing-credentials is set.")

    spec = read_json(resolve(config["protocol_spec"]))
    template = resolve(config["prompt_template"]).read_text(encoding="utf-8")
    full_config = config.get("full") or {}
    model_ids = [str(model.get("model_id")) for model in config.get("models") or []]
    expected_packet_count = int(full_config.get("planned_calls_per_model") or 0)
    expected_candidate_count = int(full_config.get("candidate_count") or 0)
    packets = evp8_core.build_packets(config, "full")
    prompt_hashes: list[str] = []
    prompt_chars: list[int] = []
    schema_errors: list[str] = []
    boundary_errors: list[str] = []
    for packet in packets:
        prompt = evp8_core.render_prompt(template, packet)
        prompt_hashes.append(evp8_core.sha256_text(prompt))
        prompt_chars.append(len(prompt))
        findings = prompt_module._boundary_findings(prompt)  # noqa: SLF001
        if findings:
            boundary_errors.extend(findings)
        error = evp8_core.validate_output_schema(evp8_core.schema_visible_rule_output(packet), spec.get("output_schema") or {})
        if error:
            schema_errors.append(error)
    summary = {
        "mode": "check_only",
        "cohort_id": "EVP-8",
        "protocol_id": spec.get("protocol_id"),
        "candidate_set_id": preflight.get("candidate_set_id"),
        "config": display_path(args.config),
        "run_scope": "full",
        "selected_candidate_ids": sorted({packet["anonymous_candidate_id"] for packet in packets}),
        "candidate_count": len({packet["anonymous_candidate_id"] for packet in packets}),
        "selection_policy": "all_frozen_evp8_candidate_set_records",
        "model_visible_levels": list(MODEL_VISIBLE_LEVELS),
        "planned_later_model_ids": model_ids,
        "planned_later_model_count": len(model_ids),
        "expected_packet_count_per_model": expected_packet_count,
        "packet_count_per_model": len(packets),
        "expected_total_later_model_calls": expected_packet_count * len(model_ids),
        "prompt_count_per_model": len(prompt_hashes),
        "prompt_hashes_unique_count": len(set(prompt_hashes)),
        "prompt_chars_min": min(prompt_chars) if prompt_chars else 0,
        "prompt_chars_max": max(prompt_chars) if prompt_chars else 0,
        "prompt_text_stored": False,
        "raw_outputs_generated": False,
        "api_call_attempted": False,
        "api_key_values_printed": False,
        "local_config_content_stored_in_tracked_summary": False,
        "boundary_error_count": len(boundary_errors),
        "boundary_errors": sorted(set(boundary_errors)),
        "schema_error_count": len(schema_errors),
        "schema_error_counts": counts(schema_errors),
        "check_only_status": "passed"
        if len(packets) == expected_packet_count
        and len({packet["anonymous_candidate_id"] for packet in packets}) == expected_candidate_count
        and len(model_ids) == 3
        and not boundary_errors
        and not schema_errors
        else "failed",
        "preflight_structural_ready": preflight["structural_ready"],
        "preflight_ready_for_user_execute_command": preflight["ready_for_user_execute_command"],
        "next_step": "Wait for explicit per-model --execute command after strict preflight.",
    }
    write_json(args.summary_out or DEFAULT_CHECK_SUMMARY_OUT, summary)
    if summary["check_only_status"] != "passed":
        raise SystemExit(f"EVP-8 later-model full check-only failed: {summary}")
    return summary


def execute(args: argparse.Namespace) -> dict[str, Any]:
    if args.config.name.endswith(".example.json"):
        raise SystemExit("Refusing to execute with tracked example config. Use ignored local config.")
    config = read_json(args.config)
    preflight = preflight_module.preflight(args.config)
    if not preflight["ready_for_user_execute_command"]:
        raise SystemExit("EVP-8 later-model execute requires strict preflight readiness.")
    model_config = model_config_by_id(config, args.model_id)
    if model_config is None:
        raise SystemExit(f"--model-id must match one configured later model: {args.model_id}")

    full_config = config.get("full") or {}
    output_dir = resolve(full_config["output_dir"]) / safe_name(str(model_config["model_id"]))
    raw_out = args.raw_out or output_dir / "raw_responses.jsonl"
    summary_out = args.summary_out or DEFAULT_EXEC_SUMMARY_DIR / f"evp8_{safe_name(str(model_config['model_id']))}_full_summary.json"
    if config.get("overwrite_policy") == "refuse_if_output_exists":
        if summary_out.exists():
            raise SystemExit(f"Refusing to overwrite existing later-model summary: {display_path(summary_out)}")
        if raw_out.exists() and not args.resume:
            raise SystemExit(
                f"Refusing to overwrite existing later-model raw output: {display_path(raw_out)}. "
                "Use --resume only when this is an interrupted run without a tracked summary."
            )

    load_env_file(str(resolve(config.get("env", ".env"))))
    spec = read_json(resolve(config["protocol_spec"]))
    template = resolve(config["prompt_template"]).read_text(encoding="utf-8")
    packets = evp8_core.build_packets(config, "full")
    completed_packet_ids, parsed_records = load_resume_state(
        raw_out=raw_out,
        packets=packets,
        spec=spec,
        model_config=model_config,
        resume=args.resume,
    )
    resumed_raw_record_count = len(completed_packet_ids)
    metadata_enabled = config.get("openrouter_metadata_header") == "enabled"
    raw_out.parent.mkdir(parents=True, exist_ok=True)
    raw_mode = "a" if args.resume and raw_out.exists() else "x"
    with raw_out.open(raw_mode, encoding="utf-8") as raw_handle:
        remaining_packets = [
            packet for packet in packets if packet["evidence_packet_id"] not in completed_packet_ids
        ]
        if args.concurrency == 1:
            client = OpenRouterClient()
            for packet in remaining_packets:
                raw_record = fetch_raw_record(
                    packet=packet,
                    template=template,
                    config=config,
                    model_config=model_config,
                    metadata_enabled=metadata_enabled,
                    client=client,
                )
                append_jsonl_record(raw_handle, raw_record)
                parsed_records.append(parsed_record_from_raw(raw_record, spec, model_config))
        else:
            execute_concurrent(
                raw_handle=raw_handle,
                packets=remaining_packets,
                template=template,
                config=config,
                spec=spec,
                model_config=model_config,
                metadata_enabled=metadata_enabled,
                parsed_records=parsed_records,
                concurrency=args.concurrency,
            )

    cost = aggregate_cost(parsed_records)
    parse_valid_count = sum(1 for record in parsed_records if record["parse_status"] == "valid")
    actual_provider_missing_count = sum(1 for record in parsed_records if not record["actual_provider"])
    summary = {
        "mode": "executed",
        "cohort_id": "EVP-8",
        "protocol_id": spec.get("protocol_id"),
        "candidate_set_id": preflight.get("candidate_set_id"),
        "config": display_path(args.config),
        "run_scope": "full",
        "configured_model_id": model_config["model_id"],
        "request_model_id": model_config["request_model_id"],
        "provider_route": model_config["provider_route"],
        "provider_preferences": model_config.get("provider_preferences"),
        "raw_responses_out": display_path(raw_out),
        "raw_response_text_stored_in_tracked_summary": False,
        "review_count": len(parsed_records),
        "concurrency": args.concurrency,
        "resume_enabled": bool(args.resume),
        "resumed_raw_record_count": resumed_raw_record_count,
        "new_api_call_count": len(parsed_records) - resumed_raw_record_count,
        "parse_valid_count": parse_valid_count,
        "invalid_parse_count": len(parsed_records) - parse_valid_count,
        "decision_counts": counts(record["decision"] for record in parsed_records),
        "review_count_by_evidence_level": level_counts(parsed_records),
        "parse_valid_count_by_evidence_level": level_counts(
            record for record in parsed_records if record["parse_status"] == "valid"
        ),
        "invalid_parse_count_by_evidence_level": level_counts(
            record for record in parsed_records if record["parse_status"] != "valid"
        ),
        "decision_counts_by_evidence_level": counts_by_evidence_level(parsed_records, "decision"),
        "request_model_id_counts": counts(record["request_model_id"] for record in parsed_records),
        "configured_model_id_counts": counts(record["configured_model_id"] for record in parsed_records),
        "actual_model_id_counts": counts(record["actual_model_id"] or "missing" for record in parsed_records),
        "actual_model_id_missing_count": sum(1 for record in parsed_records if not record["actual_model_id"]),
        "actual_provider_counts": counts(record["actual_provider"] or "missing" for record in parsed_records),
        "actual_provider_missing_count": actual_provider_missing_count,
        "openrouter_metadata_present_count": sum(1 for record in parsed_records if record["openrouter_metadata_present"]),
        "provider_route_counts": counts(record["provider_route"] for record in parsed_records),
        "api_call_attempted": True,
        "raw_outputs_generated": True,
        "prompt_text_stored": False,
        "cost_summary": cost,
        "usage_cost_gate": "passed" if cost["unknown_cost_record_count"] == 0 else "blocked",
        "provider_metadata_gate": "passed" if actual_provider_missing_count == 0 else "blocked",
        "run_gate": "passed"
        if parse_valid_count == len(parsed_records)
        and cost["unknown_cost_record_count"] == 0
        and actual_provider_missing_count == 0
        else "blocked",
    }
    summary["later_model_full_gate"] = summary["run_gate"]
    write_json(summary_out, summary)
    if summary["run_gate"] != "passed":
        raise SystemExit(f"EVP-8 later-model full gate blocked after writing outputs: {summary['run_gate']}")
    return summary


def fetch_raw_record(
    *,
    packet: dict[str, Any],
    template: str,
    config: dict[str, Any],
    model_config: dict[str, Any],
    metadata_enabled: bool,
    client: OpenRouterClient | None = None,
) -> dict[str, Any]:
    prompt = evp8_core.render_prompt(template, packet)
    findings = prompt_module._boundary_findings(prompt)  # noqa: SLF001
    if findings:
        raise RuntimeError(f"prompt boundary failed for {packet['evidence_packet_id']}: {findings}")
    active_client = client or OpenRouterClient()
    response = active_client.chat_completion(
        model=str(model_config["request_model_id"]),
        prompt=prompt,
        temperature=float(config.get("temperature", 0.0)),
        max_tokens=int(config.get("max_output_tokens", 4096)),
        provider=model_config.get("provider_preferences"),
        metadata_enabled=metadata_enabled,
    )
    return {
        "evidence_packet_id": packet["evidence_packet_id"],
        "anonymous_candidate_id": packet["anonymous_candidate_id"],
        "evidence_level": packet["evidence_level"],
        "requested_model_id": model_config["request_model_id"],
        "configured_model_id": model_config["model_id"],
        "actual_model_id": response.get("model"),
        "actual_provider": actual_provider(response),
        "openrouter_metadata": openrouter_metadata(response),
        "provider_route": model_config["provider_route"],
        "raw_response_text": response_text(response),
        "response": response,
        "run_date_utc": datetime.now(timezone.utc).isoformat(),
    }


def execute_concurrent(
    *,
    raw_handle: Any,
    packets: list[dict[str, Any]],
    template: str,
    config: dict[str, Any],
    spec: dict[str, Any],
    model_config: dict[str, Any],
    metadata_enabled: bool,
    parsed_records: list[dict[str, Any]],
    concurrency: int,
) -> None:
    pending: dict[Future[dict[str, Any]], int] = {}
    completed: dict[int, dict[str, Any]] = {}
    next_submit = 0
    next_write = 0

    def submit_available(executor: ThreadPoolExecutor) -> None:
        nonlocal next_submit
        while next_submit < len(packets) and len(pending) < concurrency:
            packet = packets[next_submit]
            future = executor.submit(
                fetch_raw_record,
                packet=packet,
                template=template,
                config=config,
                model_config=model_config,
                metadata_enabled=metadata_enabled,
            )
            pending[future] = next_submit
            next_submit += 1

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        submit_available(executor)
        while pending:
            done, _ = wait(pending, return_when=FIRST_COMPLETED)
            for future in done:
                index = pending.pop(future)
                completed[index] = future.result()
            while next_write in completed:
                raw_record = completed.pop(next_write)
                append_jsonl_record(raw_handle, raw_record)
                parsed_records.append(parsed_record_from_raw(raw_record, spec, model_config))
                next_write += 1
            submit_available(executor)


def load_resume_state(
    *,
    raw_out: Path,
    packets: list[dict[str, Any]],
    spec: dict[str, Any],
    model_config: dict[str, Any],
    resume: bool,
) -> tuple[set[str], list[dict[str, Any]]]:
    if not raw_out.exists():
        return set(), []
    if not resume:
        return set(), []
    raw_records = read_jsonl(raw_out)
    expected_ids = [str(packet["evidence_packet_id"]) for packet in packets]
    existing_ids = [str(record.get("evidence_packet_id")) for record in raw_records]
    if existing_ids != expected_ids[: len(existing_ids)]:
        raise SystemExit(
            f"Cannot resume {display_path(raw_out)}: existing raw records are not a prefix of the planned packet order."
        )
    packet_by_id = {str(packet["evidence_packet_id"]): packet for packet in packets}
    parsed_records: list[dict[str, Any]] = []
    completed: set[str] = set()
    for raw_record in raw_records:
        packet_id = str(raw_record["evidence_packet_id"])
        if packet_id in completed:
            raise SystemExit(f"Cannot resume {display_path(raw_out)}: duplicate raw record {packet_id}.")
        packet = packet_by_id[packet_id]
        if raw_record.get("configured_model_id") != model_config["model_id"]:
            raise SystemExit(f"Cannot resume {display_path(raw_out)}: configured model mismatch for {packet_id}.")
        if raw_record.get("provider_route") != model_config["provider_route"]:
            raise SystemExit(f"Cannot resume {display_path(raw_out)}: provider route mismatch for {packet_id}.")
        if raw_record.get("anonymous_candidate_id") != packet["anonymous_candidate_id"]:
            raise SystemExit(f"Cannot resume {display_path(raw_out)}: candidate mismatch for {packet_id}.")
        if raw_record.get("evidence_level") != packet["evidence_level"]:
            raise SystemExit(f"Cannot resume {display_path(raw_out)}: evidence-level mismatch for {packet_id}.")
        completed.add(packet_id)
        parsed_records.append(parsed_record_from_raw(raw_record, spec, model_config))
    return completed, parsed_records


def parsed_record_from_raw(
    raw_record: dict[str, Any],
    spec: dict[str, Any],
    model_config: dict[str, Any],
) -> dict[str, Any]:
    response = raw_record.get("response") if isinstance(raw_record.get("response"), dict) else {}
    raw_text = str(raw_record.get("raw_response_text") or "")
    parsed, invalid_reason = parse_response(raw_text, spec)
    cost = cost_summary(response=response)
    return {
        "evidence_packet_id": raw_record["evidence_packet_id"],
        "anonymous_candidate_id": raw_record["anonymous_candidate_id"],
        "evidence_level": raw_record["evidence_level"],
        "parse_status": "valid" if invalid_reason is None else "invalid",
        "invalid_reason": invalid_reason,
        "decision": parsed.get("decision") if parsed else None,
        "risk_flags": parsed.get("risk_flags") if parsed else [],
        "human_review_needed": parsed.get("human_review_needed") if parsed else None,
        "request_model_id": model_config["request_model_id"],
        "configured_model_id": model_config["model_id"],
        "actual_model_id": raw_record.get("actual_model_id") or response.get("model"),
        "actual_provider": raw_record.get("actual_provider") or actual_provider(response),
        "openrouter_metadata_present": bool(raw_record.get("openrouter_metadata") or openrouter_metadata(response)),
        "provider_route": model_config["provider_route"],
        "usage": cost["usage"],
        "cost_usd": cost.get("cost_usd"),
        "cost_cny": cost.get("cost_cny"),
        "cost_currency": cost.get("cost_currency"),
        "cost_source": cost["cost_source"],
        "cost_observability": cost["cost_observability"],
    }


def parse_response(raw_text: str, spec: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    try:
        parsed = extract_json_object(raw_text)
    except Exception as exc:  # noqa: BLE001
        return None, f"invalid_json:{exc}"
    error = evp8_core.validate_output_schema(parsed, spec.get("output_schema") or {})
    return parsed, error


def model_config_by_id(config: dict[str, Any], model_id: str | None) -> dict[str, Any] | None:
    if model_id is None:
        return None
    for model in config.get("models") or []:
        if model.get("model_id") == model_id:
            return model
    return None


def openrouter_metadata(response: dict[str, Any]) -> dict[str, Any]:
    metadata = response.get("openrouter_metadata")
    if isinstance(metadata, dict):
        return metadata
    usage = response.get("usage")
    if isinstance(usage, dict) and isinstance(usage.get("openrouter_metadata"), dict):
        return usage["openrouter_metadata"]
    return {}


def actual_provider(response: dict[str, Any]) -> str | None:
    metadata = openrouter_metadata(response)
    for source in (metadata, response):
        for key in (
            "provider_name",
            "provider",
            "provider_id",
            "provider_slug",
            "upstream_provider",
            "upstream_provider_name",
        ):
            value = source.get(key)
            if value:
                return str(value)
    return None


def cost_summary(*, response: dict[str, Any]) -> dict[str, Any]:
    usage = response.get("usage")
    if not isinstance(usage, dict):
        return unknown_cost("missing_usage")
    normalized_usage = usage_summary(usage)
    provider_cost = first_float(usage, ("cost", "cost_usd", "total_cost", "total_cost_usd"))
    if provider_cost is None:
        provider_cost = first_float(response, ("cost", "cost_usd", "total_cost", "total_cost_usd"))
    if provider_cost is not None:
        return {
            "usage": normalized_usage,
            "cost_usd": round(provider_cost, 9),
            "cost_cny": None,
            "cost_currency": "USD",
            "cost_source": "provider_reported_openrouter_cost",
            "cost_observability": "provider_reported_cost",
        }
    if normalized_usage:
        return {
            "usage": normalized_usage,
            "cost_usd": None,
            "cost_cny": None,
            "cost_currency": None,
            "cost_source": "provider_token_usage_without_usd_cost",
            "cost_observability": "token_usage_present_cost_unknown",
        }
    return unknown_cost("missing_provider_cost_or_token_usage", usage=normalized_usage)


def usage_summary(usage: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "input_tokens",
        "output_tokens",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "prompt_cache_hit_tokens",
        "prompt_cache_miss_tokens",
        "cache_hit_tokens",
        "cache_miss_tokens",
    }
    summary: dict[str, Any] = {}
    for key in sorted(allowed):
        value = token_count(usage.get(key))
        if value is not None:
            summary[key] = value
    return summary


def token_count(value: Any) -> int | None:
    if value is None:
        return None
    try:
        count = int(value)
    except (TypeError, ValueError):
        return None
    return count if count >= 0 else None


def first_float(source: dict[str, Any], keys: tuple[str, ...]) -> float | None:
    for key in keys:
        try:
            return float(source[key])
        except (KeyError, TypeError, ValueError):
            continue
    return None


def unknown_cost(reason: str, usage: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "usage": usage or {},
        "cost_usd": None,
        "cost_cny": None,
        "cost_currency": None,
        "cost_source": "unknown",
        "cost_observability": reason,
    }


def aggregate_cost(records: list[dict[str, Any]]) -> dict[str, Any]:
    total_usd = 0.0
    total_cny = 0.0
    unknown = 0
    sources: list[str] = []
    observability: list[str] = []
    currencies: list[str] = []
    for record in records:
        sources.append(str(record.get("cost_source") or "unknown"))
        observability.append(str(record.get("cost_observability") or "unknown"))
        currency = record.get("cost_currency")
        if currency:
            currencies.append(str(currency))
        cost_usd = record.get("cost_usd")
        cost_cny = record.get("cost_cny")
        if cost_usd is None and cost_cny is None:
            unknown += 1
        else:
            if cost_usd is not None:
                total_usd += float(cost_usd)
            if cost_cny is not None:
                total_cny += float(cost_cny)
    return {
        "total_cost_usd": round(total_usd, 9),
        "total_cost_cny": round(total_cny, 9),
        "unknown_cost_record_count": unknown,
        "cost_source_counts": counts(sources),
        "cost_observability_counts": counts(observability),
        "cost_currency_counts": counts(currencies),
    }


def counts(values: Any) -> dict[str, int]:
    result: dict[str, int] = {}
    for value in values:
        key = str(value)
        result[key] = result.get(key, 0) + 1
    return dict(sorted(result.items()))


def level_counts(records: Any) -> dict[str, int]:
    result = {level: 0 for level in MODEL_VISIBLE_LEVELS}
    for record in records:
        level = str(record["evidence_level"])
        result[level] = result.get(level, 0) + 1
    return dict(sorted(result.items()))


def counts_by_evidence_level(records: list[dict[str, Any]], field: str) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {level: {} for level in MODEL_VISIBLE_LEVELS}
    for record in records:
        level = str(record["evidence_level"])
        value = record.get(field)
        key = str(value) if value is not None else "missing"
        bucket = result.setdefault(level, {})
        bucket[key] = bucket.get(key, 0) + 1
    return {level: dict(sorted(level_counts.items())) for level, level_counts in sorted(result.items())}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--run-scope", choices=("full",), default="full")
    parser.add_argument("--model-id", help="Configured OpenRouter model id to execute.")
    parser.add_argument("--allow-missing-credentials", action="store_true")
    parser.add_argument("--summary-out", type=Path)
    parser.add_argument("--raw-out", type=Path)
    parser.add_argument("--resume", action="store_true", help="Resume an interrupted execute run from an existing raw JSONL prefix.")
    parser.add_argument("--concurrency", type=int, default=1, help="Bounded execute concurrency. Raw JSONL is still written in packet order.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    modes = sum(bool(value) for value in (args.check_only, args.execute))
    if modes != 1:
        raise SystemExit("Choose exactly one mode: --check-only or --execute.")
    if args.execute and not args.model_id:
        raise SystemExit("--execute requires --model-id.")
    if args.concurrency < 1:
        raise SystemExit("--concurrency must be >= 1.")
    if args.check_only and args.concurrency != 1:
        raise SystemExit("--concurrency is only valid with --execute.")
    summary = execute(args) if args.execute else check_only(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
