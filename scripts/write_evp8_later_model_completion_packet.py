"""Write the no-API EVP-8 later-model completion packet."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = REPO_ROOT / "data" / "protocols" / "evp8_protocol_v0_1.json"
PROTOCOL_AUDIT_PATH = REPO_ROOT / "data" / "protocols" / "evp8_protocol_v0_1_audit_summary.json"
FULL_CHECK_ONLY_PATH = REPO_ROOT / "data" / "protocols" / "evp8_deepseek_qwen_first_batch_full_check_only_v0_1.json"
FIRST_BATCH_AUDIT_PATH = REPO_ROOT / "data" / "protocols" / "evp8_deepseek_qwen_first_batch_full_result_audit_v0_1.json"
FIRST_BATCH_SYNTHESIS_PATH = REPO_ROOT / "data" / "protocols" / "evp8_deepseek_qwen_first_batch_full_synthesis_v0_1.json"
CATALOG_AUDIT_PATH = REPO_ROOT / "data" / "protocols" / "evp8_later_model_openrouter_catalog_audit_v0_1.json"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "protocols" / "evp8_later_model_completion_packet_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_later_model_completion_packet_v0_1.md"

EXPECTED_LATER_MODELS = [
    "moonshotai/kimi-k2.6",
    "mistralai/devstral-2512",
    "google/gemini-2.5-flash",
]
MODEL_VISIBLE_LEVELS = ["E0", "E1", "E2", "E3", "E4", "E5", "E6"]
PLANNING_COST_CEILING_USD = 30.0


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{display_path(path)} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def display_path(path: Path) -> str:
    absolute = path if path.is_absolute() else REPO_ROOT / path
    try:
        return absolute.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(absolute)


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def later_model_ids(protocol: dict[str, Any]) -> list[str]:
    phase2 = ((protocol.get("model_plan") or {}).get("phase2_later_batch")) or []
    return [str(item.get("model_id")) for item in phase2]


def catalog_result_ids(catalog_audit: dict[str, Any]) -> list[str]:
    results = catalog_audit.get("results") or []
    return [str(item.get("slug")) for item in results]


def output_paths(model_id: str) -> dict[str, str]:
    safe_model = safe_name(model_id)
    output_dir = Path("outputs") / "evp8_phase2_later_models_full" / safe_model
    return {
        "raw_responses": (output_dir / "raw_responses.jsonl").as_posix(),
        "tracked_summary": (Path("data") / "reviews" / f"evp8_{safe_model}_full_summary.json").as_posix(),
    }


def expected_output_absence(model_ids: list[str]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for model_id in model_ids:
        for output_kind, path_value in output_paths(model_id).items():
            path = REPO_ROOT / path_value
            checks.append(
                {
                    "model_id": model_id,
                    "output_kind": output_kind,
                    "path": path_value,
                    "exists": path.exists(),
                    "passed": not path.exists(),
                }
            )
    return checks


def build_model_records(model_ids: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for index, model_id in enumerate(model_ids, start=1):
        records.append(
            {
                "step": f"later_model_{index}",
                "model_id": model_id,
                "request_model_id": model_id,
                "provider_route": "openrouter_pinned_exact_model_id",
                "api_key_env": "OPENROUTER_API_KEY",
                "outputs": output_paths(model_id),
                "planned_execute_command_template": (
                    "python scripts\\run_evp8_later_model_full.py "
                    "--execute --run-scope full --config configs\\evp8_later_models.local.json "
                    f"--model-id {model_id}"
                ),
                "proceed_if": (
                    "G7 packet passed, later-model runner/preflight are implemented and checked, "
                    "OPENROUTER_API_KEY is present in ignored local env, and user explicitly authorizes this model."
                ),
            }
        )
    return records


def build_packet() -> dict[str, Any]:
    protocol = read_json(PROTOCOL_PATH)
    protocol_audit = read_json(PROTOCOL_AUDIT_PATH)
    full_check = read_json(FULL_CHECK_ONLY_PATH)
    first_batch_audit = read_json(FIRST_BATCH_AUDIT_PATH)
    first_batch_synthesis = read_json(FIRST_BATCH_SYNTHESIS_PATH)
    catalog_audit = read_json(CATALOG_AUDIT_PATH)

    model_ids = later_model_ids(protocol)
    catalog_ids = catalog_result_ids(catalog_audit)
    output_absence = expected_output_absence(model_ids)
    planned_calls = int(full_check.get("packet_count") or 0)
    total_planned_calls = planned_calls * len(model_ids)
    checks = [
        check("protocol_audit_passed", protocol_audit.get("protocol_spec_audit_status") == "passed", protocol_audit.get("protocol_spec_audit_status")),
        check("protocol_ready_for_preflight", protocol_audit.get("phase0_api_readiness") == "ready_for_api_preflight", protocol_audit.get("phase0_api_readiness")),
        check("full_check_only_passed", full_check.get("check_only_status") == "passed", full_check.get("check_only_status")),
        check("full_packet_count", planned_calls == 686, planned_calls),
        check("full_candidate_count", full_check.get("candidate_count") == 98, full_check.get("candidate_count")),
        check("full_prompt_hashes_unique", full_check.get("prompt_hashes_unique_count") == 686, full_check.get("prompt_hashes_unique_count")),
        check("first_batch_audit_passed", first_batch_audit.get("audit_status") == "passed", first_batch_audit.get("audit_status")),
        check("first_batch_audit_no_raw_outputs_read", first_batch_audit.get("raw_outputs_read") is False, first_batch_audit.get("raw_outputs_read")),
        check("first_batch_synthesis_passed", first_batch_synthesis.get("synthesis_status") == "passed", first_batch_synthesis.get("synthesis_status")),
        check("first_batch_synthesis_no_raw_outputs_read", first_batch_synthesis.get("raw_outputs_read") is False, first_batch_synthesis.get("raw_outputs_read")),
        check("later_model_ids_match_protocol", model_ids == EXPECTED_LATER_MODELS, model_ids),
        check("openrouter_catalog_all_available", catalog_audit.get("all_available") is True, catalog_audit.get("all_available")),
        check("openrouter_catalog_ids_match_protocol", catalog_ids == EXPECTED_LATER_MODELS, catalog_ids),
        check("expected_later_outputs_absent", all(item["passed"] for item in output_absence), output_absence),
    ]
    packet_status = "ready" if all(item["passed"] for item in checks) else "blocked"
    return {
        "packet_id": "evp8_later_model_completion_packet_v0_1",
        "cohort_id": "EVP-8",
        "protocol_id": protocol.get("protocol_id"),
        "candidate_set_id": full_check.get("candidate_set_id"),
        "packet_status": packet_status,
        "api_call_attempted": False,
        "raw_outputs_generated": False,
        "raw_outputs_read": False,
        "api_key_values_printed": False,
        "rendered_prompt_text_stored": False,
        "execution_authorized_by_packet": False,
        "requires_explicit_user_command": True,
        "runner_implementation_required_before_execution": True,
        "later_model_preflight_required_before_execution": True,
        "run_scope": "full",
        "planned_calls_per_later_model": planned_calls,
        "planned_later_model_count": len(model_ids),
        "planned_total_later_model_calls": total_planned_calls,
        "candidate_count": full_check.get("candidate_count"),
        "model_visible_levels": MODEL_VISIBLE_LEVELS,
        "temperature": ((protocol.get("routing_policy") or {}).get("temperature")),
        "max_output_tokens": ((protocol.get("routing_policy") or {}).get("max_output_tokens")),
        "retry_policy": (protocol.get("routing_policy") or {}).get("retry_policy"),
        "provider_route_policy": {
            "preferred_route": "openrouter_pinned_exact_model_id",
            "api_key_env": "OPENROUTER_API_KEY",
            "exact_model_id_required": True,
            "allow_unrecorded_provider_fallback": False,
            "record_actual_model_id": True,
            "record_actual_provider": True,
        },
        "cost_policy": {
            "planning_cost_ceiling_usd": PLANNING_COST_CEILING_USD,
            "ceiling_scope": "Kimi/Devstral/Gemini later-model batch only; excludes DeepSeek and Qwen already run.",
            "required_fields": [
                "usage.prompt_tokens",
                "usage.completion_tokens",
                "usage.total_tokens",
                "cost_usd",
                "cost_cny",
                "cost_currency",
                "cost_source",
                "cost_observability",
            ],
            "unknown_cost_record_count_must_equal": 0,
        },
        "openrouter_catalog_audit": {
            "path": display_path(CATALOG_AUDIT_PATH),
            "audit_date": catalog_audit.get("audit_date"),
            "all_available": catalog_audit.get("all_available"),
            "model_ids": catalog_ids,
        },
        "models": build_model_records(model_ids),
        "expected_output_absence": output_absence,
        "checks": checks,
        "guard_commands": [
            "git status --short --branch --untracked-files=all",
            "python scripts\\audit_evp8_protocol_spec.py --check",
            "python scripts\\audit_openrouter_model_catalog.py --model moonshotai/kimi-k2.6 --model mistralai/devstral-2512 --model google/gemini-2.5-flash --out-json data\\protocols\\evp8_later_model_openrouter_catalog_audit_v0_1.json --out-md docs\\experiments\\evp8_later_model_openrouter_catalog_audit_v0_1.md",
            "python scripts\\run_evp8_deepseek_qwen_smoke.py --check-only --run-scope full --config configs\\evp8_deepseek_qwen.local.json",
            "python scripts\\audit_evp8_first_batch_full_results.py --check",
            "python scripts\\summarize_evp8_first_batch_full_synthesis.py --check",
            "python scripts\\write_evp8_later_model_completion_packet.py --check",
        ],
        "post_later_model_requirements": [
            "Implement and verify later-model runner/preflight before any model call.",
            "Run each later model only after explicit user authorization.",
            "Write raw responses only under ignored outputs/evp8_phase2_later_models_full/.",
            "Write tracked raw-output-free summaries under data/reviews/.",
            "Audit each summary without reading raw outputs.",
            "Only after all later model audits pass, run five-model synthesis and claim-boundary audit.",
        ],
        "stop_gates": [
            "Any G7 packet check fails.",
            "OpenRouter public catalog no longer contains one of the pinned model IDs.",
            "OPENROUTER_API_KEY is missing from ignored local environment before execution.",
            "Later-model runner or local preflight is missing or unaudited.",
            "Any expected later-model output already exists before execution without an explicit resume path.",
            "Any raw response or rendered prompt text would be written to tracked files.",
            "Any model silently changes model ID or provider route without being recorded.",
            "Any summary has invalid parse, unknown cost, missing usage, or missing per-level aggregate.",
            "Any protocol, prompt, schema, candidate-set, or evaluator-join bug requires a protocol version bump and affected-model rerun.",
        ],
        "claim_boundary": (
            "This packet is a no-API later-model completion handoff. It does not "
            "authorize Kimi, Devstral, or Gemini API calls and does not support "
            "five-model journal conclusions until the later-model runs and audits pass."
        ),
    }


def write_markdown(path: Path, packet: dict[str, Any]) -> None:
    lines = [
        "# EVP-8 Later-Model Completion Packet v0.1",
        "",
        f"- Status: `{packet['packet_status']}`",
        f"- API call attempted: `{str(packet['api_call_attempted']).lower()}`",
        f"- Raw outputs generated/read: `{str(packet['raw_outputs_generated']).lower()}` / `{str(packet['raw_outputs_read']).lower()}`",
        f"- Execution authorized by this packet: `{str(packet['execution_authorized_by_packet']).lower()}`",
        f"- Planned calls per later model: `{packet['planned_calls_per_later_model']}`",
        f"- Planned total later-model calls: `{packet['planned_total_later_model_calls']}`",
        f"- Planning cost ceiling: `USD {packet['cost_policy']['planning_cost_ceiling_usd']}`",
        "",
        "## Models",
        "",
        "| model id | provider route | tracked summary | raw responses |",
        "|---|---|---|---|",
    ]
    for model in packet["models"]:
        lines.append(
            f"| `{model['model_id']}` | `{model['provider_route']}` | "
            f"`{model['outputs']['tracked_summary']}` | `{model['outputs']['raw_responses']}` |"
        )
    lines.extend(["", "## Guard Commands", ""])
    lines.extend(f"1. `{command}`" for command in packet["guard_commands"])
    lines.extend(["", "## Planned Execute Command Templates", ""])
    for model in packet["models"]:
        lines.append(f"- `{model['model_id']}`: `{model['planned_execute_command_template']}`")
        lines.append(f"  - proceed if: {model['proceed_if']}")
    lines.extend(["", "## Stop Gates", ""])
    lines.extend(f"- {gate}" for gate in packet["stop_gates"])
    lines.extend(["", "## Checks", ""])
    lines.extend(f"- {item['check']}: `{str(item['passed']).lower()}`" for item in packet["checks"])
    lines.extend(["", "## Claim Boundary", "", packet["claim_boundary"], ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def assert_packet(packet: dict[str, Any]) -> None:
    if packet["packet_status"] != "ready":
        raise SystemExit(f"EVP-8 later-model completion packet is blocked: {packet['checks']}")
    for key in (
        "api_call_attempted",
        "raw_outputs_generated",
        "raw_outputs_read",
        "api_key_values_printed",
        "rendered_prompt_text_stored",
        "execution_authorized_by_packet",
    ):
        if packet.get(key) is not False:
            raise SystemExit(f"{key} must be false")
    if packet.get("requires_explicit_user_command") is not True:
        raise SystemExit("requires_explicit_user_command must be true")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    packet = build_packet()
    write_json(args.json_out, packet)
    write_markdown(args.md_out, packet)
    if args.check:
        assert_packet(packet)
    print(json.dumps(packet, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
