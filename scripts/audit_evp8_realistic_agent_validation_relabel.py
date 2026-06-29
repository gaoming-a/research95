"""Audit realistic agent-patch validation/relabel outputs without storing patch text."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATION_AUDIT = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_generation_result_audit_v0_1.json"
VALIDATION_DIR = REPO_ROOT / "outputs" / "evp8_realistic_agent_validation_qwen_primary_001"
VALIDATION_SUMMARY = VALIDATION_DIR / "validation_summary.json"
RELABEL_SUMMARY = VALIDATION_DIR / "relabel_summary.json"
SOURCE_INVENTORY = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_source_inventory_v0_2.json"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_validation_relabel_audit_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_realistic_agent_validation_relabel_audit_v0_1.md"
EXPECTED_COUNT = 54


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


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def build_audit() -> dict[str, Any]:
    missing = [
        display_path(path)
        for path in (GENERATION_AUDIT, VALIDATION_SUMMARY, RELABEL_SUMMARY, SOURCE_INVENTORY)
        if not path.exists()
    ]
    if missing:
        return {
            "audit_id": "evp8_realistic_agent_validation_relabel_audit_v0_1",
            "date_utc": datetime.now(timezone.utc).isoformat(),
            "status": "waiting_for_validation_relabel_outputs",
            "missing_required_files": missing,
            "raw_output_content_stored": False,
            "patch_text_stored": False,
            "prompt_text_stored": False,
            "checks": [check("required_files_present", False, missing)],
            "next_required_step": "finish validation and relabel before source inventory rerun",
        }

    generation_audit = read_json(GENERATION_AUDIT)
    validation = read_json(VALIDATION_SUMMARY)
    relabel = read_json(RELABEL_SUMMARY)
    inventory = read_json(SOURCE_INVENTORY)
    readiness = inventory["readiness"]
    current_counts = readiness["current_counts"]
    checks = [
        check("generation_audit_passed", generation_audit.get("status") == "passed", generation_audit.get("status")),
        check("validation_record_count_54", validation.get("record_count") == EXPECTED_COUNT, validation.get("record_count")),
        check("validation_all_patches_applied", validation.get("patch_applied_count") == EXPECTED_COUNT, validation.get("patch_applied_count")),
        check("validation_all_oracles_ran", validation.get("oracle_ran_count") == EXPECTED_COUNT, validation.get("oracle_ran_count")),
        check("relabel_candidate_count_54", relabel.get("candidate_count") == EXPECTED_COUNT, relabel.get("candidate_count")),
        check("relabel_no_environment_invalid", relabel.get("environment_invalid_count") == 0, relabel.get("environment_invalid_count")),
        check("relabel_ready_for_revalidation", relabel.get("ready_for_revalidation") is True, relabel.get("ready_for_revalidation")),
        check("source_inventory_v0_2_passed", inventory.get("inventory_status") == "passed", inventory.get("inventory_status")),
        check("fresh_agent_like_at_least_30", current_counts.get("fresh_agent_like_candidates", 0) >= 30, current_counts),
        check("fresh_hard_negatives_at_least_25", current_counts.get("fresh_nontrivial_hard_negatives", 0) >= 25, current_counts),
        check("fresh_projects_at_least_3", current_counts.get("fresh_project_count", 0) >= 3, current_counts),
    ]
    validation_relabel_complete = all(item["passed"] for item in checks)
    ready_for_phase1 = bool(readiness.get("ready_for_phase1_candidate_curation"))
    status = "passed" if validation_relabel_complete and ready_for_phase1 else "passed_needs_more_sources"
    if not validation_relabel_complete:
        status = "blocked"
    return {
        "audit_id": "evp8_realistic_agent_validation_relabel_audit_v0_1",
        "date_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "inputs": {
            "generation_audit": display_path(GENERATION_AUDIT),
            "validation_summary": display_path(VALIDATION_SUMMARY),
            "relabel_summary": display_path(RELABEL_SUMMARY),
            "source_inventory": display_path(SOURCE_INVENTORY),
        },
        "validation_summary": {
            "record_count": validation.get("record_count"),
            "validation_status_counts": validation.get("validation_status_counts"),
            "patch_applied_count": validation.get("patch_applied_count"),
            "oracle_ran_count": validation.get("oracle_ran_count"),
            "oracle_all_passed_count": validation.get("oracle_all_passed_count"),
            "all_validated_against_initial_label": validation.get("all_validated"),
        },
        "relabel_summary": {
            "candidate_count": relabel.get("candidate_count"),
            "expected_outcome_counts": relabel.get("expected_outcome_counts"),
            "patch_applied_count": relabel.get("patch_applied_count"),
            "oracle_ran_count": relabel.get("oracle_ran_count"),
            "oracle_passed_count": relabel.get("oracle_passed_count"),
            "environment_invalid_count": relabel.get("environment_invalid_count"),
            "ready_for_revalidation": relabel.get("ready_for_revalidation"),
        },
        "source_readiness_after_relabel": {
            "fresh_usable_candidates": current_counts.get("fresh_usable_candidates"),
            "fresh_agent_like_candidates": current_counts.get("fresh_agent_like_candidates"),
            "fresh_nontrivial_hard_negatives": current_counts.get("fresh_nontrivial_hard_negatives"),
            "fresh_project_count": current_counts.get("fresh_project_count"),
            "ready_for_phase1_candidate_curation": ready_for_phase1,
            "ready_for_api": readiness.get("ready_for_api"),
            "phase1_count_gate": readiness.get("phase1_count_gate"),
        },
        "raw_output_content_stored": False,
        "patch_text_stored": False,
        "prompt_text_stored": False,
        "checks": checks,
        "next_required_step": (
            "add at least four fresh usable realistic candidates or revise the predeclared Phase 1 count gate "
            "before constructing the verifier cohort"
        ),
    }


def write_markdown(path: Path, audit: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# EVP-8 Realistic Agent Validation/Relabel Audit v0.1",
        "",
        f"- status: `{audit['status']}`",
        f"- raw output content stored: `{str(audit.get('raw_output_content_stored')).lower()}`",
        f"- patch text stored: `{str(audit.get('patch_text_stored')).lower()}`",
        f"- prompt text stored: `{str(audit.get('prompt_text_stored')).lower()}`",
        "",
    ]
    if "validation_summary" in audit:
        validation = audit["validation_summary"]
        relabel = audit["relabel_summary"]
        readiness = audit["source_readiness_after_relabel"]
        lines += [
            "## Validation",
            "",
            f"- records: {validation['record_count']}",
            f"- patch applied: {validation['patch_applied_count']}",
            f"- oracle ran: {validation['oracle_ran_count']}",
            f"- oracle passed: {validation['oracle_all_passed_count']}",
            f"- initial-label status counts: `{validation['validation_status_counts']}`",
            "",
            "## Relabel",
            "",
            f"- expected outcome counts: `{relabel['expected_outcome_counts']}`",
            f"- environment invalid: {relabel['environment_invalid_count']}",
            f"- ready for revalidation: `{relabel['ready_for_revalidation']}`",
            "",
            "## Source Readiness",
            "",
            f"- fresh usable candidates: {readiness['fresh_usable_candidates']}",
            f"- fresh agent-like candidates: {readiness['fresh_agent_like_candidates']}",
            f"- fresh non-trivial hard negatives: {readiness['fresh_nontrivial_hard_negatives']}",
            f"- fresh projects: {readiness['fresh_project_count']}",
            f"- ready for Phase 1 curation: `{readiness['ready_for_phase1_candidate_curation']}`",
            f"- ready for API: `{readiness['ready_for_api']}`",
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
    parser.add_argument("--out-json", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audit = build_audit()
    write_json(args.out_json, audit)
    write_markdown(args.out_md, audit)
    if args.check and audit["status"] not in {"passed", "passed_needs_more_sources"}:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
