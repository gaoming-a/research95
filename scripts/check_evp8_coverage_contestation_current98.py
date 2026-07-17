# ruff: noqa: E402
"""No-API check-only gate for EVP-8 current-98 coverage-contestation packets.

This script freezes the current prompt-sensitivity condition without calling
model APIs. It builds E6 packets from the existing EVP-8 packet builder,
removes final deterministic verdict fields, renders the coverage-contestation
prompt, and validates schema/leakage boundaries.
"""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/check_evp8_coverage_contestation_current98.py")

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

from cross_review.env import is_placeholder_secret  # noqa: E402

import build_evp8_prompt_manifest as prompt_module  # noqa: E402
import run_evp8_deepseek_qwen_smoke as evp8_core  # noqa: E402


DEFAULT_CONFIG = REPO_ROOT / "configs" / "evp8_coverage_contestation_current98.example.json"
DEFAULT_JSON_OUT = (
    REPO_ROOT / "data" / "protocols" / "evp8_coverage_contestation_current98_check_only_v0_1.json"
)
DEFAULT_MD_OUT = (
    REPO_ROOT / "docs" / "experiments" / "evp8_coverage_contestation_current98_check_only_v0_1.md"
)
REMOVED_VERDICT_FIELDS = (
    "rule_based_visible_merge_gate_decision",
    "rule_based_visible_merge_gate_reasons",
    "source_decision",
)
RISK_FLAG_VALUES = {
    "patch_apply_failed",
    "visible_test_failure",
    "visible_regression_risk",
    "tool_diagnostic_concern",
    "insufficient_evidence",
    "ambiguous_evidence",
    "test_coverage_concern",
}
COVERAGE_VALUES = {"none", "low", "medium", "high"}
TOOL_RELIABILITY_VALUES = {
    "sufficient_for_accept",
    "insufficient_for_accept",
    "contradicts_accept",
    "no_visible_tool_evidence",
}


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


def resolve(path_value: Any) -> Path:
    path = Path(str(path_value))
    return path if path.is_absolute() else REPO_ROOT / path


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def remove_verdict_fields(packet: dict[str, Any]) -> None:
    summary = ((packet.get("visible_fields") or {}).get("deterministic_visible_merge_gate_summary") or {})
    if isinstance(summary, dict):
        for field in REMOVED_VERDICT_FIELDS:
            summary.pop(field, None)


def build_coverage_packets(config: dict[str, Any], run_scope: str) -> list[dict[str, Any]]:
    packets = evp8_core.build_packets(config, run_scope)
    filtered = [packet for packet in packets if packet.get("evidence_level") == "E6"]
    suffix = str((config.get(run_scope) or {}).get("packet_suffix") or "coverage_contestation")
    for packet in filtered:
        remove_verdict_fields(packet)
        packet["packet_variant"] = config["packet_variant"]
        packet["evidence_level_name"] = "coverage_contestation_no_verdict"
        packet["evidence_packet_id"] = f"{packet['anonymous_candidate_id']}__E6__{suffix}"
        findings = evp8_core.leakage_findings(packet)
        if findings:
            raise ValueError(f"leakage findings for {packet['evidence_packet_id']}: {findings}")
    return filtered


def schema_sample_output() -> dict[str, Any]:
    return {
        "decision": "escalate",
        "confidence": 0.4,
        "primary_reason": "Visible tests pass but do not cover enough behavior for a safe merge decision.",
        "evidence_used": ["visible_fail_to_pass_test_evidence", "visible_pass_to_pass_regression_evidence"],
        "visible_contradictions": ["No visible regression tests were materialized."],
        "risk_flags": ["insufficient_evidence", "test_coverage_concern"],
        "coverage_concern": "high",
        "visible_tests_sufficient": False,
        "tool_evidence_reliability": "insufficient_for_accept",
        "would_challenge_visible_test_only_accept": True,
        "challenge_reason": "Visible pass evidence is too narrow relative to the changed surface.",
        "human_review_needed": True,
    }


def validate_output(parsed: Any) -> str | None:
    if not isinstance(parsed, dict):
        return "output_not_object"
    required = {
        "decision",
        "confidence",
        "primary_reason",
        "evidence_used",
        "visible_contradictions",
        "risk_flags",
        "coverage_concern",
        "visible_tests_sufficient",
        "tool_evidence_reliability",
        "would_challenge_visible_test_only_accept",
        "challenge_reason",
        "human_review_needed",
    }
    missing = sorted(required - set(parsed))
    if missing:
        return f"missing_required_keys:{','.join(missing)}"
    if parsed["decision"] not in {"accept", "reject", "escalate"}:
        return "invalid_decision"
    try:
        confidence = float(parsed["confidence"])
    except (TypeError, ValueError):
        return "invalid_confidence"
    if not 0.0 <= confidence <= 1.0:
        return "confidence_out_of_range"
    if not isinstance(parsed["primary_reason"], str) or not parsed["primary_reason"]:
        return "invalid_primary_reason"
    for key in ("evidence_used", "visible_contradictions", "risk_flags"):
        if not isinstance(parsed[key], list) or not all(isinstance(item, str) for item in parsed[key]):
            return f"invalid_{key}"
    invalid_flags = sorted(set(parsed["risk_flags"]) - RISK_FLAG_VALUES)
    if invalid_flags:
        return f"invalid_risk_flags:{','.join(invalid_flags)}"
    if parsed["coverage_concern"] not in COVERAGE_VALUES:
        return "invalid_coverage_concern"
    if parsed["tool_evidence_reliability"] not in TOOL_RELIABILITY_VALUES:
        return "invalid_tool_evidence_reliability"
    for key in ("visible_tests_sufficient", "would_challenge_visible_test_only_accept", "human_review_needed"):
        if not isinstance(parsed[key], bool):
            return f"invalid_{key}"
    if not isinstance(parsed["challenge_reason"], str):
        return "invalid_challenge_reason"
    if parsed["decision"] == "escalate" and parsed["human_review_needed"] is not True:
        return "escalate_requires_human_review"
    if parsed["decision"] in {"accept", "reject"} and parsed["human_review_needed"] is not False:
        return "supported_decision_requires_no_human_review"
    return None


def env_key_states(env_path: Path, keys: list[str]) -> tuple[dict[str, str], bool]:
    if not env_path.exists():
        return {key: "missing" for key in keys}, False
    states = {key: "missing" for key in keys}
    for line_number, line in enumerate(env_path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            raise ValueError(f"invalid env line at {display_path(env_path)}:{line_number}")
        key, value = stripped.split("=", 1)
        key = key.strip()
        if key in states:
            secret = value.strip().strip("\"'")
            states[key] = "missing_or_placeholder" if is_placeholder_secret(secret) else "set"
    return states, True


def verdict_field_count(packets: list[dict[str, Any]], field: str) -> int:
    return sum(1 for packet in packets if field in json.dumps(packet, ensure_ascii=False))


def build_summary(config: dict[str, Any], run_scope: str) -> dict[str, Any]:
    if config.get("packet_variant") != "current98_e6_coverage_contestation_no_verdict":
        raise ValueError(f"unsupported packet_variant: {config.get('packet_variant')}")
    template_path = resolve(config["prompt_template"])
    template = template_path.read_text(encoding="utf-8")
    packets = build_coverage_packets(config, run_scope)
    prompt_hashes: list[str] = []
    prompt_chars: list[int] = []
    boundary_errors: list[str] = []
    for packet in packets:
        prompt = evp8_core.render_prompt(template, packet)
        prompt_hashes.append(evp8_core.sha256_text(prompt))
        prompt_chars.append(len(prompt))
        boundary_errors.extend(prompt_module._boundary_findings(prompt))  # noqa: SLF001

    key_names = sorted(
        {
            str(model.get("api_key_env"))
            for model in config.get("models") or []
            if model.get("api_key_env")
        }
    )
    key_states, env_exists = env_key_states(resolve(config.get("env", ".env")), key_names)
    schema_error = validate_output(schema_sample_output())
    model_ids = [str(model.get("model_id")) for model in config.get("models") or []]
    expected_candidates = int((config.get(run_scope) or {}).get("candidate_count") or 0)
    expected_packets = int((config.get(run_scope) or {}).get("planned_calls_per_model") or 0)
    candidate_ids = {packet["anonymous_candidate_id"] for packet in packets}
    checks = [
        check("api_call_not_attempted", True, False),
        check("raw_outputs_not_generated", True, False),
        check("prompt_text_not_stored", True, False),
        check("prompt_template_exists", template_path.exists(), display_path(template_path)),
        check("candidate_count", len(candidate_ids) == expected_candidates, len(candidate_ids)),
        check("packet_count", len(packets) == expected_packets, len(packets)),
        check("only_e6_packets", {packet.get("evidence_level") for packet in packets} == {"E6"}, sorted({packet.get("evidence_level") for packet in packets})),
        check("rule_based_visible_merge_gate_decision_removed", verdict_field_count(packets, "rule_based_visible_merge_gate_decision") == 0, verdict_field_count(packets, "rule_based_visible_merge_gate_decision")),
        check("rule_based_visible_merge_gate_reasons_removed", verdict_field_count(packets, "rule_based_visible_merge_gate_reasons") == 0, verdict_field_count(packets, "rule_based_visible_merge_gate_reasons")),
        check("source_decision_removed", verdict_field_count(packets, "source_decision") == 0, verdict_field_count(packets, "source_decision")),
        check("prompt_boundary_error_count", not boundary_errors, sorted(set(boundary_errors))),
        check("schema_sample_valid", schema_error is None, schema_error),
        check("main_prompt_unchanged_by_this_check", True, "evp8_visible_evidence_merge_gate_v0_2 is not modified or used as this condition"),
    ]
    status = "passed" if all(item["passed"] for item in checks) else "blocked"
    return {
        "analysis_id": "evp8_coverage_contestation_current98_check_only_v0_1",
        "status": status,
        "mode": "check_only",
        "cohort_id": "EVP-8",
        "run_scope": run_scope,
        "config": display_path(DEFAULT_CONFIG),
        "prompt_template": display_path(template_path),
        "prompt_sha256": evp8_core.sha256_text(template),
        "packet_variant": config["packet_variant"],
        "removed_verdict_fields": list(REMOVED_VERDICT_FIELDS),
        "planned_model_ids": model_ids,
        "candidate_count": len(candidate_ids),
        "packet_count_per_model": len(packets),
        "planned_total_model_calls": len(packets) * len(model_ids),
        "prompt_count_per_model": len(prompt_hashes),
        "prompt_hashes_unique_count": len(set(prompt_hashes)),
        "prompt_chars_min": min(prompt_chars) if prompt_chars else 0,
        "prompt_chars_max": max(prompt_chars) if prompt_chars else 0,
        "credential_presence_observed": {
            "env_file_exists": env_exists,
            "key_states": key_states,
            "values_printed": False,
        },
        "api_call_attempted": False,
        "raw_outputs_generated": False,
        "prompt_text_stored": False,
        "checks": checks,
        "next_step": "If the user authorizes execution after this check-only gate, run the three planned models as a separate prompt-sensitivity condition and keep outputs separate from the main E0-E6 table.",
        "claim_boundary": "This check-only artifact freezes a coverage-contestation prompt condition; it is not model-result evidence.",
    }


def write_md(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# EVP-8 current-98 coverage-contestation check-only v0.1",
        "",
        f"Status: `{summary['status']}`",
        "",
        "## Boundary",
        "",
        "- No API call was attempted.",
        "- Raw model outputs were not generated.",
        "- Rendered prompts were not stored.",
        "- The main prompt `evp8_visible_evidence_merge_gate_v0_2` remains unchanged.",
        "- This condition removes final deterministic verdict fields from E6 packets.",
        "",
        "## Planned Scope",
        "",
        f"- candidate count: `{summary['candidate_count']}`",
        f"- packet count per model: `{summary['packet_count_per_model']}`",
        f"- planned models: {', '.join(f'`{model}`' for model in summary['planned_model_ids'])}",
        f"- planned total model calls: `{summary['planned_total_model_calls']}`",
        "",
        "## Checks",
        "",
        "| check | passed | detail |",
        "| --- | --- | --- |",
    ]
    for row in summary["checks"]:
        lines.append(
            f"| `{row['check']}` | {str(row['passed']).lower()} | `{json.dumps(row['detail'], ensure_ascii=False)}` |"
        )
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            summary["next_step"],
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--run-scope", choices=["smoke", "full"], default="full")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = read_json(args.config)
    summary = build_summary(config, args.run_scope)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    existing_json = args.json_out.read_text(encoding="utf-8") if args.json_out.exists() else None
    existing_md = args.md_out.read_text(encoding="utf-8") if args.md_out.exists() else None
    json_text = json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    args.json_out.write_text(json_text, encoding="utf-8")
    write_md(summary, args.md_out)
    if args.check:
        current_md = args.md_out.read_text(encoding="utf-8")
        if existing_json is not None and existing_json != json_text:
            raise SystemExit(f"{display_path(args.json_out)} is not current")
        if existing_md is not None and existing_md != current_md:
            raise SystemExit(f"{display_path(args.md_out)} is not current")
        if existing_json is None or existing_md is None:
            raise SystemExit("coverage-contestation check-only outputs were missing before --check")
        if summary["status"] != "passed":
            raise SystemExit(f"coverage-contestation check-only status is {summary['status']}")
        print("coverage-contestation current-98 check-only outputs are current")
    else:
        print(f"wrote {display_path(args.json_out)}")
        print(f"wrote {display_path(args.md_out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
