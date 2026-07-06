"""Run EVP-8 current-98 coverage-contestation prompt-sensitivity condition.

This runner executes the independent E6/no-verdict coverage-contestation
prompt on the frozen current-98 cohort. Raw provider responses are written only
under ignored outputs. Tracked review files contain normalized structured
fields, never rendered prompts or raw response text.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

import run_evp8_deepseek_qwen_smoke as evp8_core  # noqa: E402
from check_evp8_coverage_contestation_current98 import (  # noqa: E402
    build_coverage_packets,
    display_path,
    read_json,
    validate_output,
    write_json,
)
from cross_review.env import load_env_file  # noqa: E402
from cross_review.parsing import extract_json_object  # noqa: E402


DEFAULT_CONFIG = REPO_ROOT / "configs" / "evp8_coverage_contestation_current98.local.json"
DEFAULT_SUMMARY_DIR = REPO_ROOT / "data" / "reviews"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "outputs" / "evp8_coverage_contestation_current98_v0_1"
CONDITION = "coverage-contestation-current98-e6-no-verdict"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{display_path(path)}:{line_number} must contain a JSON object")
        records.append(value)
    return records


def append_jsonl_record(handle: Any, record: dict[str, Any]) -> None:
    handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    handle.flush()


def model_config(config: dict[str, Any], model_id: str | None) -> dict[str, Any]:
    for model in config.get("models") or []:
        if model.get("model_id") == model_id:
            return model
    raise SystemExit(f"--model-id must match a configured model: {model_id}")


def default_paths(model_id: str, run_scope: str) -> tuple[Path, Path, Path]:
    safe_model = evp8_core.safe_name(model_id)
    raw_out = DEFAULT_OUTPUT_DIR / safe_model / "raw_responses.jsonl"
    reviews_out = (
        DEFAULT_SUMMARY_DIR
        / f"evp8_coverage_contestation_current98_{safe_model}_{run_scope}_reviews.jsonl"
    )
    summary_out = (
        DEFAULT_SUMMARY_DIR
        / f"evp8_coverage_contestation_current98_{safe_model}_{run_scope}_summary.json"
    )
    return raw_out, reviews_out, summary_out


def parsed_from_raw(raw_record: dict[str, Any], model: dict[str, Any]) -> dict[str, Any]:
    raw_text = str(raw_record.get("raw_response_text") or "")
    parsed: dict[str, Any] | None
    invalid_reason: str | None
    try:
        parsed = extract_json_object(raw_text)
        invalid_reason = validate_output(parsed)
    except Exception as exc:  # noqa: BLE001
        parsed = None
        invalid_reason = f"invalid_json:{exc}"
    response = raw_record.get("response") if isinstance(raw_record.get("response"), dict) else {}
    cost = evp8_core.cost_summary(response=response, model_config=model)
    return {
        "condition": CONDITION,
        "evidence_packet_id": raw_record["evidence_packet_id"],
        "anonymous_candidate_id": raw_record["anonymous_candidate_id"],
        "evidence_level": raw_record["evidence_level"],
        "parse_status": "valid" if invalid_reason is None else "invalid",
        "invalid_reason": invalid_reason,
        "decision": parsed.get("decision") if parsed else None,
        "confidence": parsed.get("confidence") if parsed else None,
        "risk_flags": parsed.get("risk_flags") if parsed else [],
        "coverage_concern": parsed.get("coverage_concern") if parsed else None,
        "visible_tests_sufficient": parsed.get("visible_tests_sufficient") if parsed else None,
        "tool_evidence_reliability": parsed.get("tool_evidence_reliability") if parsed else None,
        "would_challenge_visible_test_only_accept": (
            parsed.get("would_challenge_visible_test_only_accept") if parsed else None
        ),
        "human_review_needed": parsed.get("human_review_needed") if parsed else None,
        "request_model_id": model["request_model_id"],
        "configured_model_id": model["model_id"],
        "actual_model_id": raw_record.get("actual_model_id") or response.get("model"),
        "provider_route": model["provider_route"],
        "usage": cost["usage"],
        "cost_usd": cost.get("cost_usd"),
        "cost_cny": cost.get("cost_cny"),
        "cost_currency": cost.get("cost_currency"),
        "cost_source": cost["cost_source"],
        "cost_observability": cost["cost_observability"],
        "raw_response_text_stored": False,
        "rendered_prompt_text_stored": False,
    }


def load_resume_state(
    *,
    raw_out: Path,
    packets: list[dict[str, Any]],
    model: dict[str, Any],
    resume: bool,
) -> tuple[set[str], list[dict[str, Any]]]:
    if not raw_out.exists() or not resume:
        return set(), []
    raw_records = read_jsonl(raw_out)
    expected_ids = [str(packet["evidence_packet_id"]) for packet in packets]
    existing_ids = [str(record.get("evidence_packet_id")) for record in raw_records]
    if existing_ids != expected_ids[: len(existing_ids)]:
        raise SystemExit(
            f"Cannot resume {display_path(raw_out)}: existing raw records are not a prefix of planned packet order."
        )
    completed: set[str] = set()
    parsed_records: list[dict[str, Any]] = []
    packet_by_id = {str(packet["evidence_packet_id"]): packet for packet in packets}
    for raw_record in raw_records:
        packet_id = str(raw_record["evidence_packet_id"])
        packet = packet_by_id[packet_id]
        if raw_record.get("configured_model_id") != model["model_id"]:
            raise SystemExit(f"Cannot resume {display_path(raw_out)}: model mismatch at {packet_id}.")
        if raw_record.get("provider_route") != model["provider_route"]:
            raise SystemExit(f"Cannot resume {display_path(raw_out)}: provider route mismatch at {packet_id}.")
        if raw_record.get("anonymous_candidate_id") != packet["anonymous_candidate_id"]:
            raise SystemExit(f"Cannot resume {display_path(raw_out)}: candidate mismatch at {packet_id}.")
        completed.add(packet_id)
        parsed_records.append(parsed_from_raw(raw_record, model))
    return completed, parsed_records


def write_reviews(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )


def summary_for(
    *,
    args: argparse.Namespace,
    config: dict[str, Any],
    model: dict[str, Any],
    raw_out: Path,
    reviews_out: Path,
    records: list[dict[str, Any]],
    resumed_count: int,
) -> dict[str, Any]:
    cost = evp8_core.aggregate_cost(records)
    parse_valid_count = sum(1 for record in records if record["parse_status"] == "valid")
    run_gate = (
        "passed"
        if parse_valid_count == len(records) and cost["unknown_cost_record_count"] == 0
        else "blocked"
    )
    return {
        "mode": "executed",
        "analysis_id": "evp8_coverage_contestation_current98_v0_1",
        "condition": CONDITION,
        "cohort_id": "EVP-8",
        "config": display_path(args.config),
        "run_scope": args.run_scope,
        "packet_variant": config["packet_variant"],
        "configured_model_id": model["model_id"],
        "request_model_id": model["request_model_id"],
        "provider_route": model["provider_route"],
        "provider_preferences": model.get("provider_preferences"),
        "request_response_format": model.get("response_format"),
        "request_thinking": model.get("thinking"),
        "raw_responses_out": display_path(raw_out),
        "tracked_reviews_out": display_path(reviews_out),
        "raw_response_text_stored_in_tracked_summary": False,
        "raw_response_text_stored_in_tracked_reviews": False,
        "rendered_prompt_text_stored": False,
        "api_key_values_printed": False,
        "api_call_attempted": True,
        "raw_outputs_generated": True,
        "review_count": len(records),
        "new_api_call_count": len(records) - resumed_count,
        "resume_enabled": bool(args.resume),
        "resumed_raw_record_count": resumed_count,
        "parse_valid_count": parse_valid_count,
        "invalid_parse_count": len(records) - parse_valid_count,
        "decision_counts": evp8_core._counts(record["decision"] for record in records),
        "coverage_concern_counts": evp8_core._counts(record["coverage_concern"] for record in records),
        "visible_tests_sufficient_counts": evp8_core._counts(
            record["visible_tests_sufficient"] for record in records
        ),
        "tool_evidence_reliability_counts": evp8_core._counts(
            record["tool_evidence_reliability"] for record in records
        ),
        "challenge_visible_test_only_accept_counts": evp8_core._counts(
            record["would_challenge_visible_test_only_accept"] for record in records
        ),
        "actual_model_id_counts": evp8_core._counts(record["actual_model_id"] or "missing" for record in records),
        "provider_route_counts": evp8_core._counts(record["provider_route"] for record in records),
        "cost_summary": cost,
        "usage_cost_gate": "passed" if cost["unknown_cost_record_count"] == 0 else "blocked",
        "run_gate": run_gate,
    }


def execute(args: argparse.Namespace) -> dict[str, Any]:
    if args.config.name.endswith(".example.json"):
        raise SystemExit("Refusing to execute with tracked example config. Use ignored local config.")
    config = read_json(args.config)
    if config.get("api_execution_authorized") is not True:
        raise SystemExit("api_execution_authorized must be true in ignored local config for execution.")
    model = model_config(config, args.model_id)
    load_env_file(str(evp8_core.resolve(config.get("env", ".env"))))
    template = evp8_core.resolve(config["prompt_template"]).read_text(encoding="utf-8")
    packets = build_coverage_packets(config, args.run_scope)
    default_raw, default_reviews, default_summary = default_paths(str(model["model_id"]), args.run_scope)
    raw_out = args.raw_out or default_raw
    reviews_out = args.reviews_out or default_reviews
    summary_out = args.summary_out or default_summary
    if raw_out.exists() and not args.resume:
        raise SystemExit(f"Refusing to overwrite raw output: {display_path(raw_out)}. Use --resume.")
    completed_ids, parsed_records = load_resume_state(
        raw_out=raw_out,
        packets=packets,
        model=model,
        resume=args.resume,
    )
    resumed_count = len(completed_ids)
    raw_out.parent.mkdir(parents=True, exist_ok=True)
    raw_mode = "a" if args.resume and raw_out.exists() else "x"
    with raw_out.open(raw_mode, encoding="utf-8") as raw_handle:
        for packet in packets:
            if packet["evidence_packet_id"] in completed_ids:
                continue
            raw_record = evp8_core.fetch_raw_record(packet, template, config, model)
            append_jsonl_record(raw_handle, raw_record)
            parsed_records.append(parsed_from_raw(raw_record, model))
    write_reviews(reviews_out, parsed_records)
    summary = summary_for(
        args=args,
        config=config,
        model=model,
        raw_out=raw_out,
        reviews_out=reviews_out,
        records=parsed_records,
        resumed_count=resumed_count,
    )
    write_json(summary_out, summary)
    if summary["run_gate"] != "passed":
        raise SystemExit(f"Coverage-contestation run gate blocked: {summary['run_gate']}")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--run-scope", choices=("smoke", "full"), default="full")
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--raw-out", type=Path)
    parser.add_argument("--reviews-out", type=Path)
    parser.add_argument("--summary-out", type=Path)
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


def main() -> int:
    summary = execute(parse_args())
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
