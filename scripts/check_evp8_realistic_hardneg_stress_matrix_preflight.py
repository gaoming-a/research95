"""No-API preflight for the EVP-8 hard-negative stress verifier matrix.

The stress cohort's model-visible packets contain patch diffs and therefore
remain under ignored outputs. This preflight renders prompts only in memory and
writes tracked summaries without patch text, rendered prompts, raw responses,
or credentials.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_evp8_prompt_manifest as prompt_module  # noqa: E402


SUMMARY_IN = REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_stress_cohort_v0_1.json"
PACKETS_IN = (
    REPO_ROOT
    / "outputs"
    / "evp8_realistic_hardneg_stress_cohort_v0_1"
    / "model_visible_packets.jsonl"
)
JSON_OUT = (
    REPO_ROOT
    / "data"
    / "protocols"
    / "evp8_realistic_hardneg_stress_matrix_preflight_v0_1.json"
)
MD_OUT = (
    REPO_ROOT
    / "docs"
    / "experiments"
    / "evp8_realistic_hardneg_stress_matrix_preflight_v0_1.md"
)
CALL_MANIFEST_OUT = (
    REPO_ROOT
    / "outputs"
    / "evp8_realistic_hardneg_stress_matrix_preflight_v0_1"
    / "call_manifest.jsonl"
)

PLACEHOLDER = "{visible_evidence_packet_json}"
VERDICT_FIELDS = (
    "rule_based_visible_merge_gate_decision",
    "rule_based_visible_merge_gate_reasons",
    "source_decision",
)
SANITIZED_METADATA_FIELDS = (
    "has_hidden_oracle",
    "label_leakage_guard",
    "stress_source_boundary",
)
TRACKED_FORBIDDEN_SUBSTRINGS = (
    "diff --git",
    "\n@@ ",
    "sk-",
    "Bearer ",
)
PACKET_FORBIDDEN_KEYS = (
    "normalized_label",
    "oracle_result",
    "oracle_passed",
    "hidden_validation_summary",
    "hidden_oracle_result",
    "hidden_oracle_results",
    "expected_outcome",
    "candidate_type",
    "source_patch_id",
)
MODELS = (
    {
        "model_id": "qwen/qwen3.7-max",
        "request_model_id": "qwen3.7-max",
        "provider_route": "qwen_official",
    },
    {
        "model_id": "deepseek/deepseek-v4-pro",
        "request_model_id": "deepseek-v4-pro",
        "provider_route": "deepseek_official",
    },
    {
        "model_id": "google/gemini-2.5-flash",
        "request_model_id": "google/gemini-2.5-flash",
        "provider_route": "openrouter_pinned_exact_model_id",
    },
)
CONDITIONS = (
    {
        "condition_id": "current_merge_gate",
        "prompt_template": "prompts/evp8_visible_evidence_merge_gate_v0_2.md",
        "packet_transform": "sanitized_stress_packet",
    },
    {
        "condition_id": "e6_no_verdict",
        "prompt_template": "prompts/evp8_visible_evidence_merge_gate_v0_2.md",
        "packet_transform": "sanitized_stress_packet_minus_verdict_fields",
    },
    {
        "condition_id": "coverage_contestation",
        "prompt_template": "prompts/evp8_coverage_contestation_merge_gate_v0_1.md",
        "packet_transform": "sanitized_stress_packet",
    },
)


def display_path(path: Path) -> str:
    absolute = path if path.is_absolute() else REPO_ROOT / path
    try:
        return absolute.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(absolute)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{display_path(path)} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{display_path(path)}:{line_number} must contain a JSON object")
        rows.append(value)
    return rows


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def nested_key_hits(value: Any, forbidden: tuple[str, ...]) -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in forbidden:
                hits.append(key)
            hits.extend(nested_key_hits(child, forbidden))
    elif isinstance(value, list):
        for child in value:
            hits.extend(nested_key_hits(child, forbidden))
    return hits


def remove_keys_recursive(value: Any, keys: tuple[str, ...]) -> tuple[Any, int]:
    removed = 0
    if isinstance(value, dict):
        cleaned: dict[str, Any] = {}
        for key, child in value.items():
            if key in keys:
                removed += 1
                continue
            new_child, child_removed = remove_keys_recursive(child, keys)
            removed += child_removed
            cleaned[key] = new_child
        return cleaned, removed
    if isinstance(value, list):
        cleaned_list = []
        for child in value:
            new_child, child_removed = remove_keys_recursive(child, keys)
            removed += child_removed
            cleaned_list.append(new_child)
        return cleaned_list, removed
    return value, 0


def sanitize_packet(packet: dict[str, Any]) -> tuple[dict[str, Any], int]:
    sanitized, removed = remove_keys_recursive(copy.deepcopy(packet), SANITIZED_METADATA_FIELDS)
    if not isinstance(sanitized, dict):
        raise ValueError("sanitized packet must remain an object")
    return sanitized, removed


def no_verdict_packet(packet: dict[str, Any]) -> tuple[dict[str, Any], int]:
    sanitized, removed_meta = sanitize_packet(packet)
    stripped, removed_verdict = remove_keys_recursive(sanitized, VERDICT_FIELDS)
    if not isinstance(stripped, dict):
        raise ValueError("no-verdict packet must remain an object")
    return stripped, removed_meta + removed_verdict


def render_prompt(template: str, packet: dict[str, Any]) -> str:
    return prompt_module.render_prompt(template, packet)


def prompt_boundary_findings(prompt: str) -> list[str]:
    findings = set(prompt_module._boundary_findings(prompt))  # noqa: SLF001
    return sorted(findings)


def packet_visible_pass(packet: dict[str, Any]) -> bool:
    visible_tests = packet.get("visible_test_evidence")
    if not isinstance(visible_tests, dict):
        return False
    tool = packet.get("visible_tool_evidence")
    if not isinstance(tool, dict):
        return False
    return (
        visible_tests.get("run_status") == "completed"
        and visible_tests.get("observed_outcome") == "passed"
        and tool.get("tool_summary_available") is True
        and tool.get("visible_test_observed_outcome") == "passed"
    )


def condition_packet(condition_id: str, packet: dict[str, Any]) -> tuple[dict[str, Any], int]:
    if condition_id == "e6_no_verdict":
        return no_verdict_packet(packet)
    return sanitize_packet(packet)


def condition_status(condition: dict[str, str], packets: list[dict[str, Any]]) -> dict[str, Any]:
    condition_id = condition["condition_id"]
    total_removed = 0
    verdict_removed = 0
    rendered_hashes: list[str] = []
    rendered_chars: list[int] = []
    boundary_findings: list[str] = []
    template_path = REPO_ROOT / condition["prompt_template"]
    template = template_path.read_text(encoding="utf-8")
    for packet in packets:
        transformed, removed = condition_packet(condition_id, packet)
        total_removed += removed
        if condition_id == "e6_no_verdict":
            _, sanitized_removed = sanitize_packet(packet)
            verdict_removed += max(0, removed - sanitized_removed)
        prompt = render_prompt(template, transformed)
        rendered_hashes.append(sha256_text(prompt))
        rendered_chars.append(len(prompt))
        boundary_findings.extend(prompt_boundary_findings(prompt))

    is_no_verdict = condition_id == "e6_no_verdict"
    ready = not boundary_findings and (not is_no_verdict or verdict_removed > 0)
    reason = "ready"
    if boundary_findings:
        reason = "prompt_boundary_findings_present"
    elif is_no_verdict and verdict_removed == 0:
        reason = "blocked_no_verdict_transform_is_degenerate_for_stress_packets"
    return {
        "condition_id": condition_id,
        "prompt_template": condition["prompt_template"],
        "prompt_template_sha256": sha256_text(template),
        "packet_transform": condition["packet_transform"],
        "ready_for_api": ready,
        "readiness_reason": reason,
        "packet_count": len(packets),
        "metadata_fields_removed_total": total_removed,
        "verdict_fields_removed_total": verdict_removed,
        "rendered_prompt_text_stored": False,
        "rendered_prompt_hashes_unique_count": len(set(rendered_hashes)),
        "rendered_prompt_chars_min": min(rendered_chars) if rendered_chars else 0,
        "rendered_prompt_chars_max": max(rendered_chars) if rendered_chars else 0,
        "boundary_findings": sorted(set(boundary_findings)),
    }


def call_manifest_records(
    packets: list[dict[str, Any]],
    conditions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    ready_conditions = {row["condition_id"]: row for row in conditions if row["ready_for_api"]}
    records: list[dict[str, Any]] = []
    template_cache = {
        condition["condition_id"]: (REPO_ROOT / condition["prompt_template"]).read_text(encoding="utf-8")
        for condition in CONDITIONS
        if condition["condition_id"] in ready_conditions
    }
    for packet in packets:
        for condition_id, condition in ready_conditions.items():
            transformed, removed = condition_packet(condition_id, packet)
            prompt = render_prompt(template_cache[condition_id], transformed)
            for model in MODELS:
                records.append(
                    {
                        "candidate_id": packet.get("candidate_id"),
                        "condition_id": condition_id,
                        "model_id": model["model_id"],
                        "request_model_id": model["request_model_id"],
                        "provider_route": model["provider_route"],
                        "packet_sha256": sha256_text(stable_json(transformed)),
                        "rendered_prompt_sha256": sha256_text(prompt),
                        "rendered_prompt_chars": len(prompt),
                        "sanitized_or_removed_field_count": removed,
                        "prompt_template": condition["prompt_template"],
                        "prompt_template_sha256": condition["prompt_template_sha256"],
                        "raw_response_text_stored": False,
                        "rendered_prompt_text_stored": False,
                        "patch_text_stored_in_manifest": False,
                    }
                )
    return records


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def tracked_text_leaks(*paths: Path) -> dict[str, list[str]]:
    leaks: dict[str, list[str]] = {}
    for path in paths:
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        found = [needle for needle in TRACKED_FORBIDDEN_SUBSTRINGS if needle in text]
        if found:
            leaks[display_path(path)] = found
    return leaks


def build_summary() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    cohort_summary = read_json(SUMMARY_IN)
    packets = read_jsonl(PACKETS_IN)
    candidate_ids = [str(packet.get("candidate_id")) for packet in packets]
    tracked_cases = cohort_summary.get("case_records") or []
    source_counts = Counter(str(row.get("source_kind")) for row in tracked_cases if isinstance(row, dict))
    project_counts = Counter(str(row.get("project")) for row in tracked_cases if isinstance(row, dict))
    task_counts = Counter(str(row.get("task_id")) for row in tracked_cases if isinstance(row, dict))
    forbidden_hits = Counter()
    visible_pass_count = 0
    metadata_removed_counts = []
    for packet in packets:
        forbidden_hits.update(nested_key_hits(packet, PACKET_FORBIDDEN_KEYS))
        if packet_visible_pass(packet):
            visible_pass_count += 1
        _, removed = sanitize_packet(packet)
        metadata_removed_counts.append(removed)

    condition_rows = [condition_status(condition, packets) for condition in CONDITIONS]
    ready_conditions = [row for row in condition_rows if row["ready_for_api"]]
    blocked_conditions = [row for row in condition_rows if not row["ready_for_api"]]
    records = call_manifest_records(packets, condition_rows)
    requested_call_count = len(packets) * len(CONDITIONS) * len(MODELS)
    effective_call_count = len(records)
    checks = [
        check("api_call_not_attempted", True, False),
        check("raw_outputs_not_generated", True, False),
        check("rendered_prompt_text_not_stored", True, False),
        check("stress_cohort_summary_exists", SUMMARY_IN.exists(), display_path(SUMMARY_IN)),
        check("model_visible_packets_exists", PACKETS_IN.exists(), display_path(PACKETS_IN)),
        check("candidate_count_is_31", len(packets) == 31, len(packets)),
        check("candidate_ids_unique", len(set(candidate_ids)) == len(candidate_ids), len(set(candidate_ids))),
        check(
            "tracked_summary_candidate_count_matches_packets",
            cohort_summary.get("candidate_count") == len(packets),
            {"summary": cohort_summary.get("candidate_count"), "packets": len(packets)},
        ),
        check("visible_pass_all_packets", visible_pass_count == len(packets), visible_pass_count),
        check("forbidden_label_keys_absent_from_packets", not forbidden_hits, dict(forbidden_hits)),
        check(
            "sanitizer_removed_hidden_metadata",
            all(count > 0 for count in metadata_removed_counts),
            {"min": min(metadata_removed_counts), "max": max(metadata_removed_counts)},
        ),
        check(
            "ready_conditions_are_nonempty",
            len(ready_conditions) >= 1,
            [row["condition_id"] for row in ready_conditions],
        ),
        check(
            "no_verdict_degenerate_condition_blocked",
            any(
                row["condition_id"] == "e6_no_verdict"
                and not row["ready_for_api"]
                and row["readiness_reason"] == "blocked_no_verdict_transform_is_degenerate_for_stress_packets"
                for row in condition_rows
            ),
            [row for row in condition_rows if row["condition_id"] == "e6_no_verdict"],
        ),
        check(
            "effective_call_count_matches_ready_conditions",
            effective_call_count == len(packets) * len(ready_conditions) * len(MODELS),
            effective_call_count,
        ),
    ]
    hard_checks_pass = all(row["passed"] for row in checks)
    status = "passed_with_no_verdict_blocked" if hard_checks_pass and blocked_conditions else "passed"
    if not hard_checks_pass:
        status = "blocked"
    summary = {
        "analysis_id": "evp8_realistic_hardneg_stress_matrix_preflight_v0_1",
        "status": status,
        "mode": "no_api_preflight",
        "cohort_id": "EVP-8-REALISTIC-HARDNEG-STRESS",
        "input_summary": display_path(SUMMARY_IN),
        "input_model_visible_packets": display_path(PACKETS_IN),
        "call_manifest_out": display_path(CALL_MANIFEST_OUT),
        "candidate_count": len(packets),
        "project_counts": dict(sorted(project_counts.items())),
        "task_counts": dict(sorted(task_counts.items())),
        "source_kind_counts": dict(sorted(source_counts.items())),
        "models": list(MODELS),
        "prompt_conditions_requested": [row["condition_id"] for row in condition_rows],
        "prompt_conditions_ready": [row["condition_id"] for row in ready_conditions],
        "prompt_conditions_blocked": [
            {"condition_id": row["condition_id"], "reason": row["readiness_reason"]}
            for row in blocked_conditions
        ],
        "condition_summaries": condition_rows,
        "requested_matrix_call_count_if_all_conditions_ready": requested_call_count,
        "effective_ready_matrix_call_count": effective_call_count,
        "calls_per_ready_condition": len(packets) * len(MODELS),
        "api_call_attempted": False,
        "raw_outputs_generated": False,
        "rendered_prompt_text_stored": False,
        "patch_text_stored_in_tracked_outputs": False,
        "claim_boundary": (
            "This preflight prepares a hard-negative stress-test verifier matrix. "
            "It is not model-result evidence, and the blocked no-verdict condition "
            "must not be reported as an executed independent ablation."
        ),
        "next_step": (
            "Run only the ready current_merge_gate and coverage_contestation conditions "
            "for Qwen, DeepSeek, and Gemini unless a separate verdict-field packet "
            "variant is built and preflighted for no-verdict."
        ),
        "checks": checks,
    }
    return summary, records


def write_md(summary: dict[str, Any], path: Path) -> None:
    model_list = ", ".join(f"`{model['model_id']}`" for model in summary["models"])
    requested_conditions = ", ".join(f"`{condition}`" for condition in summary["prompt_conditions_requested"])
    ready_conditions = ", ".join(f"`{condition}`" for condition in summary["prompt_conditions_ready"])
    lines = [
        "# EVP-8 hard-negative stress matrix preflight v0.1",
        "",
        f"Status: `{summary['status']}`",
        "",
        "## Boundary",
        "",
        "- No verifier API call was attempted.",
        "- Raw model outputs were not generated.",
        "- Rendered prompt text was not stored.",
        "- Patch-bearing packets remain in ignored `outputs/**`; tracked files contain only counts, hashes, and boundary checks.",
        "- The matrix is hard-negative stress-test evidence, not a pure agent-generated realistic cohort.",
        "",
        "## Scope",
        "",
        f"- candidates: `{summary['candidate_count']}`",
        f"- models: {model_list}",
        f"- requested conditions: {requested_conditions}",
        f"- ready conditions: {ready_conditions}",
        f"- requested calls if all conditions were ready: `{summary['requested_matrix_call_count_if_all_conditions_ready']}`",
        f"- effective ready calls: `{summary['effective_ready_matrix_call_count']}`",
        "",
        "## Condition Gates",
        "",
        "| condition | ready | reason | prompt |",
        "| --- | --- | --- | --- |",
    ]
    for row in summary["condition_summaries"]:
        lines.append(
            f"| `{row['condition_id']}` | {str(row['ready_for_api']).lower()} | "
            f"`{row['readiness_reason']}` | `{row['prompt_template']}` |"
        )
    lines.extend(
        [
            "",
            "## Composition",
            "",
            f"- project counts: `{json.dumps(summary['project_counts'], ensure_ascii=False, sort_keys=True)}`",
            f"- source kind counts: `{json.dumps(summary['source_kind_counts'], ensure_ascii=False, sort_keys=True)}`",
            "",
            "## Checks",
            "",
            "| check | passed | detail |",
            "| --- | --- | --- |",
        ]
    )
    for row in summary["checks"]:
        lines.append(
            f"| `{row['check']}` | {str(row['passed']).lower()} | "
            f"`{json.dumps(row['detail'], ensure_ascii=False, sort_keys=True)}` |"
        )
    lines.extend(["", "## Next Step", "", summary["next_step"], ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=MD_OUT)
    parser.add_argument("--call-manifest-out", type=Path, default=CALL_MANIFEST_OUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    existing_json = args.json_out.read_text(encoding="utf-8") if args.json_out.exists() else None
    existing_md = args.md_out.read_text(encoding="utf-8") if args.md_out.exists() else None
    existing_manifest = args.call_manifest_out.read_text(encoding="utf-8") if args.call_manifest_out.exists() else None
    summary, records = build_summary()
    write_json(args.json_out, summary)
    write_md(summary, args.md_out)
    write_jsonl(args.call_manifest_out, records)
    leaks = tracked_text_leaks(args.json_out, args.md_out)
    if leaks:
        raise SystemExit(f"tracked output leakage detected: {json.dumps(leaks, ensure_ascii=False)}")
    if args.check:
        json_text = args.json_out.read_text(encoding="utf-8")
        md_text = args.md_out.read_text(encoding="utf-8")
        manifest_text = args.call_manifest_out.read_text(encoding="utf-8")
        if existing_json is not None and existing_json != json_text:
            raise SystemExit(f"{display_path(args.json_out)} is not current")
        if existing_md is not None and existing_md != md_text:
            raise SystemExit(f"{display_path(args.md_out)} is not current")
        if existing_manifest is not None and existing_manifest != manifest_text:
            raise SystemExit(f"{display_path(args.call_manifest_out)} is not current")
        if existing_json is None or existing_md is None or existing_manifest is None:
            raise SystemExit("preflight outputs were missing before --check")
        if summary["status"] == "blocked":
            raise SystemExit("preflight status is blocked")
        print("hard-negative stress matrix preflight outputs are current")
    else:
        print(f"wrote {display_path(args.json_out)}")
        print(f"wrote {display_path(args.md_out)}")
        print(f"wrote {display_path(args.call_manifest_out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
