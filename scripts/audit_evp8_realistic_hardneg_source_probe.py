# ruff: noqa: E402
"""Audit a no-API hard-negative source probe without storing patch text."""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/audit_evp8_realistic_hardneg_source_probe.py")

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


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


def display_path(path: Path) -> str:
    absolute = path if path.is_absolute() else REPO_ROOT / path
    try:
        return absolute.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(absolute)


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def counts(rows: list[dict[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(str(row.get(field)) for row in rows).items()))


def build_audit(probe_dir: Path, validation_summary_path: Path, visible_summary_path: Path) -> dict[str, Any]:
    summary_path = probe_dir / "dataset_summary.json"
    candidates_path = probe_dir / "candidates.jsonl"
    evidence_path = probe_dir / "evidence_packets.jsonl"
    summary = read_json(summary_path)
    candidates = read_jsonl(candidates_path)
    evidence_packets = read_jsonl(evidence_path)
    validation_summary = read_json(validation_summary_path)
    visible_summary = read_json(visible_summary_path)
    candidate_ids = [str(row.get("model_candidate_id")) for row in candidates]
    evidence_ids = [str(row.get("candidate_id")) for row in evidence_packets]
    checks = [
        check("api_call_not_attempted_by_source_probe", True, False),
        check("raw_model_outputs_not_read", True, False),
        check("patch_text_not_stored", True, False),
        check("prompt_text_not_stored", True, False),
        check("candidate_count_matches_summary", len(candidates) == summary.get("candidate_count"), summary.get("candidate_count")),
        check("evidence_count_matches_candidates", len(evidence_packets) == len(candidates), len(evidence_packets)),
        check("evidence_ids_match_candidate_ids", set(evidence_ids) == set(candidate_ids), True),
        check("validation_all_validated", validation_summary.get("all_validated") is True, validation_summary.get("validation_status_counts")),
        check("visible_tests_completed", visible_summary.get("run_status_counts") == {"completed": len(candidates)}, visible_summary.get("run_status_counts")),
    ]
    return {
        "audit_id": "evp8_realistic_hardneg_source_probe_audit_v0_1",
        "date_utc": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if all(row["passed"] for row in checks) else "blocked",
        "inputs": {
            "probe_dir": display_path(probe_dir),
            "dataset_summary": display_path(summary_path),
            "candidates": display_path(candidates_path),
            "evidence_packets": display_path(evidence_path),
            "validation_summary": display_path(validation_summary_path),
            "visible_summary": display_path(visible_summary_path),
        },
        "counts": {
            "candidate_count": len(candidates),
            "candidate_type_counts": counts(candidates, "candidate_type"),
            "expected_outcome_counts": counts(candidates, "expected_outcome"),
            "project_counts": counts(candidates, "project"),
            "patch_materialization_counts": counts(candidates, "patch_materialization"),
            "visible_test_outcome_counts": visible_summary.get("test_outcome_counts"),
            "oracle_passed_count": validation_summary.get("oracle_all_passed_count"),
        },
        "scope": {
            "api_call_attempted": False,
            "raw_model_outputs_read": False,
            "patch_text_stored": False,
            "prompt_text_stored": False,
            "source_kind": "curated_no_api_hard_negative_source_probe",
        },
        "checks": checks,
        "next_required_step": "join validation with visible-test outcomes and refresh the combined hard-negative gate",
    }


def write_markdown(path: Path, audit: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    counts_value = audit["counts"]
    lines = [
        "# EVP-8 Realistic Hard-Negative Source Probe Audit v0.1",
        "",
        f"- status: `{audit['status']}`",
        f"- source kind: `{audit['scope']['source_kind']}`",
        f"- candidates: {counts_value['candidate_count']}",
        f"- project counts: `{counts_value['project_counts']}`",
        f"- candidate type counts: `{counts_value['candidate_type_counts']}`",
        f"- visible test outcomes: `{counts_value['visible_test_outcome_counts']}`",
        f"- oracle passed: {counts_value['oracle_passed_count']}",
        "",
        "This audit stores aggregate source-probe metadata only. It does not store",
        "patch text, prompt text, raw model outputs, or rendered prompts.",
        "",
        "## Checks",
        "",
    ]
    for row in audit["checks"]:
        lines.append(f"- {row['check']}: {'passed' if row['passed'] else 'failed'} ({row['detail']})")
    lines += ["", "## Next Step", "", audit["next_required_step"], ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe-dir", type=Path, required=True)
    parser.add_argument("--validation-summary", type=Path, required=True)
    parser.add_argument("--visible-summary", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audit = build_audit(args.probe_dir, args.validation_summary, args.visible_summary)
    write_json(args.out_json, audit)
    write_markdown(args.out_md, audit)
    if args.check and audit["status"] != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
