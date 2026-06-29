"""Audit the EVP-8 realistic agent-patch generation output without storing raw content."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_DIR = REPO_ROOT / "outputs" / "evp8_realistic_agent_generation_qwen_primary_001"
TARGET_MATRIX = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_source_target_matrix_v0_1.json"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_generation_result_audit_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_realistic_agent_generation_result_audit_v0_1.md"
EXPECTED_RUN_ID = "evp8_realistic_agent_generation_qwen_primary_001"
EXPECTED_MODEL = "qwen3.7-max"
EXPECTED_PROVIDER = "qwen_official"
PLANNED_SLOTS = 54
PATCHES_PER_TASK = 9

PROMPT_MANIFEST_ALLOWED_FIELDS = {
    "api_provider",
    "label_leakage_check",
    "model",
    "prompt_chars",
    "prompt_sha256",
    "prompt_version",
    "resumed_prompt_record",
    "task_id",
    "variant_index",
}
EVIDENCE_PACKET_FORBIDDEN_FIELDS = {
    "agent_applied_edits",
    "candidate_type",
    "construction_notes",
    "expected_outcome",
    "generation_rationale",
    "hidden_oracles",
    "label_confidence",
    "oracle_command",
    "oracle_workdir",
    "raw_generation_response_path",
    "raw_generation_response_sha256",
    "source",
}


def display_path(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{display_path(path)} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
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


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def counter_dict(values: list[str]) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def field_union(rows: list[dict[str, Any]]) -> set[str]:
    fields: set[str] = set()
    for row in rows:
        fields.update(row)
    return fields


def build_audit(run_dir: Path) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    summary_path = run_dir / "generation_summary.json"
    candidate_path = run_dir / "candidates.pending.jsonl"
    evidence_path = run_dir / "evidence_packets.pending.jsonl"
    manifest_path = run_dir / "prompt_manifest.jsonl"
    error_path = run_dir / "generation_error.json"
    raw_dir = run_dir / "raw"

    target_matrix = read_json(TARGET_MATRIX)
    planned_tasks = [target["task_id"] for target in target_matrix["targets"]]
    planned_task_counts = {task_id: PATCHES_PER_TASK for task_id in planned_tasks}

    missing_required_files = [
        display_path(path)
        for path in (summary_path, candidate_path, evidence_path, manifest_path)
        if not path.exists()
    ]
    if missing_required_files:
        status = "waiting_for_generation_results" if not run_dir.exists() else "partial_or_blocked"
        audit = {
            "audit_id": "evp8_realistic_agent_generation_result_audit_v0_1",
            "date_utc": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "run_dir": display_path(run_dir),
            "missing_required_files": missing_required_files,
            "raw_output_content_stored": False,
            "patch_text_stored": False,
            "prompt_text_stored": False,
            "checks": [
                check("generation_required_files_present", False, missing_required_files),
                check("generation_error_absent", not error_path.exists(), error_path.exists()),
            ],
            "next_required_step": "finish generation before validation/relabel",
        }
        return audit

    summary = read_json(summary_path)
    candidates = read_jsonl(candidate_path)
    evidence_packets = read_jsonl(evidence_path)
    prompt_manifest = read_jsonl(manifest_path)
    raw_response_file_count = len(list(raw_dir.rglob("*.json"))) if raw_dir.exists() else 0
    candidate_raw_ref_count = sum(1 for candidate in candidates if candidate.get("raw_generation_response_sha256"))
    candidate_patch_ids = [str(candidate.get("patch_id", "")) for candidate in candidates]
    model_candidate_ids = [str(candidate.get("model_candidate_id", "")) for candidate in candidates]
    evidence_candidate_ids = [str(packet.get("candidate_id", "")) for packet in evidence_packets]
    prompt_task_counts = counter_dict([str(record.get("task_id", "")) for record in prompt_manifest])
    candidate_task_counts = counter_dict([str(candidate.get("task_id", "")) for candidate in candidates])
    project_counts = counter_dict([str(candidate.get("project", "")) for candidate in candidates])
    label_confidence_counts = counter_dict([str(candidate.get("label_confidence", "")) for candidate in candidates])
    patch_hashes = {
        hashlib.sha256(str(candidate.get("patch_text", "")).encode("utf-8")).hexdigest()
        for candidate in candidates
    }
    prompt_fields = field_union(prompt_manifest)
    evidence_fields = field_union(evidence_packets)
    unexpected_prompt_fields = sorted(prompt_fields - PROMPT_MANIFEST_ALLOWED_FIELDS)
    evidence_forbidden_fields_present = sorted(evidence_fields & EVIDENCE_PACKET_FORBIDDEN_FIELDS)

    checks = [
        check("generation_error_absent", not error_path.exists(), error_path.exists()),
        check("summary_run_id_expected", summary.get("run_id") == EXPECTED_RUN_ID, summary.get("run_id")),
        check("summary_model_expected", summary.get("model") == EXPECTED_MODEL, summary.get("model")),
        check("summary_provider_expected", summary.get("api_provider") == EXPECTED_PROVIDER, summary.get("api_provider")),
        check("summary_not_dry_run", summary.get("dry_run") is False, summary.get("dry_run")),
        check("summary_prompt_count_54", summary.get("prompt_count") == PLANNED_SLOTS, summary.get("prompt_count")),
        check("summary_candidate_count_54", summary.get("candidate_count") == PLANNED_SLOTS, summary.get("candidate_count")),
        check("prompt_manifest_count_54", len(prompt_manifest) == PLANNED_SLOTS, len(prompt_manifest)),
        check("candidate_count_54", len(candidates) == PLANNED_SLOTS, len(candidates)),
        check("evidence_packet_count_54", len(evidence_packets) == PLANNED_SLOTS, len(evidence_packets)),
        check("unique_patch_ids_54", len(set(candidate_patch_ids)) == PLANNED_SLOTS, len(set(candidate_patch_ids))),
        check("unique_model_candidate_ids_54", len(set(model_candidate_ids)) == PLANNED_SLOTS, len(set(model_candidate_ids))),
        check(
            "evidence_candidate_ids_match_model_candidate_ids",
            set(evidence_candidate_ids) == set(model_candidate_ids),
            True,
        ),
        check("candidate_task_counts_match_plan", candidate_task_counts == planned_task_counts, candidate_task_counts),
        check("prompt_task_counts_match_plan", prompt_task_counts == planned_task_counts, prompt_task_counts),
        check("all_labels_pending_validation", label_confidence_counts == {"pending_validation": PLANNED_SLOTS}, label_confidence_counts),
        check("raw_response_files_at_least_candidates", raw_response_file_count >= len(candidates), raw_response_file_count),
        check("candidate_raw_hashes_present", candidate_raw_ref_count == len(candidates), candidate_raw_ref_count),
        check("prompt_manifest_has_no_payload_fields", not unexpected_prompt_fields, unexpected_prompt_fields),
        check("evidence_packets_hide_evaluator_fields", not evidence_forbidden_fields_present, evidence_forbidden_fields_present),
    ]
    status = "passed" if all(item["passed"] for item in checks) else "blocked"
    return {
        "audit_id": "evp8_realistic_agent_generation_result_audit_v0_1",
        "date_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "run_dir": display_path(run_dir),
        "generation_summary": {
            "run_id": summary.get("run_id"),
            "model": summary.get("model"),
            "api_provider": summary.get("api_provider"),
            "prompt_version": summary.get("prompt_version"),
            "dry_run": summary.get("dry_run"),
            "prompt_count": summary.get("prompt_count"),
            "candidate_count": summary.get("candidate_count"),
            "generation_date_utc": summary.get("generation_date_utc"),
        },
        "counts": {
            "planned_slots": PLANNED_SLOTS,
            "prompt_manifest_records": len(prompt_manifest),
            "candidate_records": len(candidates),
            "evidence_packet_records": len(evidence_packets),
            "unique_patch_ids": len(set(candidate_patch_ids)),
            "unique_model_candidate_ids": len(set(model_candidate_ids)),
            "unique_patch_text_hashes": len(patch_hashes),
            "raw_response_file_count": raw_response_file_count,
            "candidate_raw_hash_count": candidate_raw_ref_count,
            "extra_raw_response_files_from_failed_attempts": max(0, raw_response_file_count - candidate_raw_ref_count),
        },
        "task_counts": candidate_task_counts,
        "project_counts": project_counts,
        "label_confidence_counts": label_confidence_counts,
        "field_boundary": {
            "prompt_manifest_unexpected_fields": unexpected_prompt_fields,
            "evidence_packet_forbidden_fields_present": evidence_forbidden_fields_present,
            "pending_candidates_contain_evaluator_only_fields": True,
            "pending_candidates_are_not_model_visible_inputs": True,
        },
        "raw_output_content_stored": False,
        "patch_text_stored": False,
        "prompt_text_stored": False,
        "checks": checks,
        "next_required_step": "validate generated candidates and relabel with evaluator-only outcomes before cohort construction",
    }


def write_markdown(path: Path, audit: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# EVP-8 Realistic Agent Generation Result Audit v0.1",
        "",
        f"- status: `{audit['status']}`",
        f"- run dir: `{audit['run_dir']}`",
        f"- raw output content stored in this audit: `{str(audit.get('raw_output_content_stored')).lower()}`",
        f"- patch text stored in this audit: `{str(audit.get('patch_text_stored')).lower()}`",
        f"- prompt text stored in this audit: `{str(audit.get('prompt_text_stored')).lower()}`",
        "",
    ]
    if "generation_summary" in audit:
        summary = audit["generation_summary"]
        counts = audit["counts"]
        lines += [
            "## Summary",
            "",
            f"- model/provider: `{summary['model']}` / `{summary['api_provider']}`",
            f"- prompt version: `{summary['prompt_version']}`",
            f"- prompts/candidates/evidence packets: {counts['prompt_manifest_records']} / {counts['candidate_records']} / {counts['evidence_packet_records']}",
            f"- unique patch ids: {counts['unique_patch_ids']}",
            f"- unique patch-text hashes: {counts['unique_patch_text_hashes']}",
            f"- raw response files: {counts['raw_response_file_count']}",
            f"- extra raw files from failed attempts: {counts['extra_raw_response_files_from_failed_attempts']}",
            "",
            "## Task Counts",
            "",
        ]
        for task_id, count in audit["task_counts"].items():
            lines.append(f"- `{task_id}`: {count}")
        lines += [
            "",
            "## Project Counts",
            "",
        ]
        for project, count in audit["project_counts"].items():
            lines.append(f"- `{project}`: {count}")
        lines += [
            "",
            "## Boundary",
            "",
            f"- pending candidates contain evaluator-only fields: `{str(audit['field_boundary']['pending_candidates_contain_evaluator_only_fields']).lower()}`",
            f"- pending candidates are model-visible inputs: `{str(not audit['field_boundary']['pending_candidates_are_not_model_visible_inputs']).lower()}`",
            f"- prompt manifest unexpected fields: `{audit['field_boundary']['prompt_manifest_unexpected_fields']}`",
            f"- evidence packet forbidden fields present: `{audit['field_boundary']['evidence_packet_forbidden_fields_present']}`",
            "",
        ]
    if audit.get("missing_required_files"):
        lines += ["## Missing Files", ""]
        for missing in audit["missing_required_files"]:
            lines.append(f"- `{missing}`")
        lines.append("")
    lines += ["## Checks", ""]
    for row in audit["checks"]:
        lines.append(f"- {row['check']}: {'passed' if row['passed'] else 'failed'} ({row['detail']})")
    lines += [
        "",
        "## Next Step",
        "",
        audit["next_required_step"],
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audit = build_audit(args.run_dir)
    write_json(args.out_json, audit)
    write_markdown(args.out_md, audit)
    if args.check and audit["status"] != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
