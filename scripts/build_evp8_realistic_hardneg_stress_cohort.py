"""Build the separated EVP-8 realistic hard-negative stress cohort.

This is a no-API step. Patch-bearing model-visible packets are written only to
ignored outputs; tracked artifacts contain aggregate and hash metadata only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
COHORT_ID = "EVP-8-REALISTIC-HARDNEG-STRESS"

DEFAULT_GATE_PATHS = [
    REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_generation_gate_v0_1.json",
    REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_generation_supplement_001_gate_v0_1.json",
    REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_generation_deepseek_supplement_001_gate_v0_1.json",
    REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_generation_thefuck_supplement_003_gate_v0_1.json",
    REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_full_file_generation_gate_v0_1.json",
    REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_scrapy_source_probe_gate_v0_1.json",
]
DEFAULT_OUT_DIR = REPO_ROOT / "outputs" / "evp8_realistic_hardneg_stress_cohort_v0_1"
DEFAULT_SUMMARY_OUT = REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_stress_cohort_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_realistic_hardneg_stress_cohort_v0_1.md"
MIN_CASES = 30
MIN_PROJECTS = 3


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


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def display_path(path: Path) -> str:
    absolute = path if path.is_absolute() else REPO_ROOT / path
    try:
        return absolute.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(absolute)


def repo_path(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else REPO_ROOT / path


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def index_by(rows: list[dict[str, Any]], field: str) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = str(row.get(field) or "")
        if not key:
            raise ValueError(f"row missing {field}")
        if key in index:
            raise ValueError(f"duplicate {field}: {key}")
        index[key] = row
    return index


def visible_passed(row: dict[str, Any]) -> bool:
    return ((row.get("visible_run_summary") or {}).get("passed") is True)


def outcome_counts(outcome: dict[str, Any]) -> dict[str, int]:
    return dict(sorted(Counter(str(result.get("outcome")) for result in outcome.get("test_results", [])).items()))


def classify(validation: dict[str, Any], visible: dict[str, Any]) -> str:
    if validation.get("patch_applied") is not True:
        return "patch_apply_failed"
    oracle_passed = validation.get("oracle_passed")
    if visible_passed(visible) and oracle_passed is False:
        return "visible_pass_hidden_fail"
    if visible_passed(visible) and oracle_passed is True:
        return "visible_pass_hidden_pass"
    if not visible_passed(visible) and oracle_passed is False:
        return "visible_fail_hidden_fail"
    if not visible_passed(visible) and oracle_passed is True:
        return "visible_fail_hidden_pass"
    return "inconclusive"


def candidate_source_path(gate: dict[str, Any], generation_audit: dict[str, Any]) -> Path:
    inputs = generation_audit.get("inputs")
    if isinstance(inputs, dict) and inputs.get("candidates"):
        return repo_path(str(inputs["candidates"]))
    run_dir = generation_audit.get("run_dir")
    if isinstance(run_dir, str) and run_dir:
        return repo_path(run_dir) / "candidates.pending.jsonl"
    gate_inputs = gate.get("inputs") if isinstance(gate.get("inputs"), dict) else {}
    validation = str(gate_inputs.get("validation") or "")
    if "full_file" in validation:
        return REPO_ROOT / "outputs" / "evp8_realistic_hardneg_full_file_generation_qwen_001" / "candidates.pending.jsonl"
    raise ValueError(f"cannot infer candidate source for gate {gate.get('analysis_id')}")


def evidence_source_path(gate: dict[str, Any], generation_audit: dict[str, Any], candidates_path: Path) -> Path:
    inputs = generation_audit.get("inputs")
    if isinstance(inputs, dict) and inputs.get("evidence_packets"):
        return repo_path(str(inputs["evidence_packets"]))
    candidate_name = candidates_path.name
    if candidate_name == "candidates.pending.jsonl":
        return candidates_path.with_name("evidence_packets.pending.jsonl")
    if candidate_name == "candidates.jsonl":
        return candidates_path.with_name("evidence_packets.jsonl")
    return candidates_path.with_name("evidence_packets.jsonl")


def patch_size(patch_text: str) -> dict[str, int]:
    added = 0
    deleted = 0
    files: set[str] = set()
    for line in patch_text.splitlines():
        if line.startswith("+++ b/"):
            files.add(line[6:])
        elif line.startswith("+") and not line.startswith("+++"):
            added += 1
        elif line.startswith("-") and not line.startswith("---"):
            deleted += 1
    return {"added_lines": added, "deleted_lines": deleted, "files_changed": len(files)}


def load_gate_cases(gate_path: Path) -> list[dict[str, Any]]:
    gate = read_json(gate_path)
    inputs = gate.get("inputs")
    if not isinstance(inputs, dict):
        return []
    validation_path = repo_path(str(inputs["validation"]))
    visible_path = repo_path(str(inputs["visible_test_outcomes"]))
    generation_audit_path = repo_path(str(inputs["generation_audit"]))
    generation_audit = read_json(generation_audit_path)
    candidates_path = candidate_source_path(gate, generation_audit)
    evidence_path = evidence_source_path(gate, generation_audit, candidates_path)

    validations = index_by(read_jsonl(validation_path), "model_candidate_id")
    visible_rows = index_by(read_jsonl(visible_path), "candidate_id")
    candidates = index_by(read_jsonl(candidates_path), "model_candidate_id")
    evidence_packets = index_by(read_jsonl(evidence_path), "candidate_id")
    cases = []
    for candidate_id, validation in sorted(validations.items()):
        visible = visible_rows.get(candidate_id)
        candidate = candidates.get(candidate_id)
        evidence = evidence_packets.get(candidate_id)
        if visible is None or candidate is None or evidence is None:
            raise ValueError(f"{display_path(gate_path)} missing joined row for {candidate_id}")
        if classify(validation, visible) != "visible_pass_hidden_fail":
            continue
        cases.append(
            {
                "gate_path": gate_path,
                "generation_audit_path": generation_audit_path,
                "validation": validation,
                "visible": visible,
                "candidate": candidate,
                "evidence": evidence,
                "source_kind": (
                    "curated_no_api_stress_source"
                    if "source_probe" in display_path(gate_path)
                    else "model_generated_source"
                ),
            }
        )
    return cases


def evaluator_row(index: int, case: dict[str, Any]) -> dict[str, Any]:
    candidate = case["candidate"]
    validation = case["validation"]
    visible = case["visible"]
    patch_text = str(candidate["patch_text"])
    return {
        "cohort_id": COHORT_ID,
        "candidate_id": f"evp8_hardneg_stress_candidate_{index:04d}",
        "source_candidate_id": candidate.get("model_candidate_id"),
        "source_patch_id": candidate.get("patch_id"),
        "source_gate": display_path(case["gate_path"]),
        "source_kind": case["source_kind"],
        "task_id": candidate.get("task_id"),
        "project": candidate.get("project"),
        "candidate_type": candidate.get("candidate_type"),
        "patch_materialization": candidate.get("patch_materialization"),
        "generation_model": candidate.get("generation_model"),
        "generation_run_id": candidate.get("generation_run_id"),
        "normalized_label": "test_passing_wrong",
        "hard_negative_class": "visible_pass_hidden_fail",
        "patch_sha256": hashlib.sha256(patch_text.encode("utf-8")).hexdigest(),
        "patch_size": patch_size(patch_text),
        "hidden_validation_summary": {
            "patch_applied": validation.get("patch_applied"),
            "oracle_ran": validation.get("oracle_ran"),
            "oracle_passed": validation.get("oracle_passed"),
            "validation_status": validation.get("validation_status"),
        },
        "visible_test_summary": {
            "run_status": visible.get("run_status"),
            "observed_outcome": (visible.get("visible_run_summary") or {}).get("outcome"),
            "passed": visible_passed(visible),
            "outcome_counts": outcome_counts(visible),
        },
    }


def model_visible_row(index: int, case: dict[str, Any]) -> dict[str, Any]:
    candidate = case["candidate"]
    visible = case["visible"]
    evidence = dict(case["evidence"])
    stress_id = f"evp8_hardneg_stress_candidate_{index:04d}"
    evidence["candidate_id"] = stress_id
    evidence["cohort_id"] = COHORT_ID
    visible_evidence = {
        "listed_tests": visible.get("visible_tests", []),
        "run_status": visible.get("run_status"),
        "observed_outcome": (visible.get("visible_run_summary") or {}).get("outcome"),
        "outcome_counts": outcome_counts(visible),
        "patch_apply_summary": visible.get("patch_apply_summary"),
        "test_results": visible.get("test_results", []),
    }
    return evidence | {
        "task_id": candidate.get("task_id"),
        "project": candidate.get("project"),
        "issue_summary": candidate.get("issue_summary"),
        "visible_test_evidence": visible_evidence,
        "visible_tool_evidence": {
            "tool_summary_available": True,
            "visible_test_run_status": visible_evidence["run_status"],
            "visible_test_observed_outcome": visible_evidence["observed_outcome"],
            "visible_test_outcome_counts": visible_evidence["outcome_counts"],
            "patch_apply_summary": visible_evidence["patch_apply_summary"],
            "reason": "Declared visible tests passed, but hidden evaluator labels are omitted from this packet.",
        },
        "stress_source_boundary": (
            "This packet is part of a hard-negative stress-test cohort. Some cases are curated "
            "no-API stress-source partials rather than pure agent-generated patches."
        ),
    }


def baseline_row(evaluator: dict[str, Any]) -> dict[str, Any]:
    return {
        "baseline_id": "evp8_realistic_hardneg_stress_visible_tool_baseline_v0_1",
        "cohort_id": COHORT_ID,
        "candidate_id": evaluator["candidate_id"],
        "task_id": evaluator["task_id"],
        "project": evaluator["project"],
        "decision": "accept",
        "reason": "all_declared_visible_tests_passed",
        "visible_test_run_status": evaluator["visible_test_summary"]["run_status"],
        "visible_test_observed_outcome": evaluator["visible_test_summary"]["observed_outcome"],
        "api_call_attempted": False,
        "is_false_accept_under_hidden_label": True,
    }


def forbidden_key_hits(value: Any, path: str = "$") -> list[str]:
    forbidden = {
        "candidate_type",
        "expected_outcome",
        "generation_rationale",
        "hidden_oracles",
        "hidden_validation_summary",
        "label_confidence",
        "model_candidate_id",
        "normalized_label",
        "oracle_command",
        "oracle_passed",
        "oracle_result",
        "oracle_ran",
        "oracle_workdir",
        "raw_generation_response_path",
        "raw_generation_response_sha256",
        "source_patch_id",
        "source_model_candidate_id",
    }
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in forbidden:
                hits.append(child_path)
            hits.extend(forbidden_key_hits(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(forbidden_key_hits(child, f"{path}[{index}]"))
    return hits


def build_summary(
    evaluator_rows: list[dict[str, Any]],
    model_visible_rows: list[dict[str, Any]],
    baseline_rows: list[dict[str, Any]],
    out_dir: Path,
    min_cases: int,
    min_projects: int,
) -> dict[str, Any]:
    projects = sorted({str(row["project"]) for row in evaluator_rows})
    task_counts = Counter(str(row["task_id"]) for row in evaluator_rows)
    project_counts = Counter(str(row["project"]) for row in evaluator_rows)
    source_kind_counts = Counter(str(row["source_kind"]) for row in evaluator_rows)
    baseline_decisions = Counter(str(row["decision"]) for row in baseline_rows)
    false_accepts = sum(1 for row in baseline_rows if row["is_false_accept_under_hidden_label"])
    leakage_hits = [hit for row in model_visible_rows for hit in forbidden_key_hits(row)]
    checks = [
        check("api_call_not_attempted", True, False),
        check("case_count_minimum_met", len(evaluator_rows) >= min_cases, len(evaluator_rows)),
        check("project_minimum_met", len(projects) >= min_projects, projects),
        check("all_cases_are_visible_pass_hidden_fail", all(row["hard_negative_class"] == "visible_pass_hidden_fail" for row in evaluator_rows), True),
        check("model_visible_count_matches_evaluator", len(model_visible_rows) == len(evaluator_rows), len(model_visible_rows)),
        check("baseline_count_matches_evaluator", len(baseline_rows) == len(evaluator_rows), len(baseline_rows)),
        check("visible_tool_baseline_all_accepts", baseline_decisions == Counter({"accept": len(baseline_rows)}), dict(baseline_decisions)),
        check("visible_tool_false_accepts_all_cases", false_accepts == len(baseline_rows), false_accepts),
        check("model_visible_forbidden_fields_absent", not leakage_hits, leakage_hits[:20]),
    ]
    return {
        "analysis_id": "evp8_realistic_hardneg_stress_cohort_v0_1",
        "date_utc": datetime.now(timezone.utc).isoformat(),
        "cohort_id": COHORT_ID,
        "status": "passed" if all(row["passed"] for row in checks) else "blocked",
        "scope": {
            "api_call_attempted": False,
            "raw_model_outputs_read": False,
            "tracked_patch_text_stored": False,
            "tracked_prompt_text_stored": False,
            "model_visible_packets_path_is_ignored_outputs": True,
            "cohort_boundary": "hard-negative stress test; not a pure agent-generated realistic cohort",
        },
        "outputs": {
            "ignored_evaluator_manifest": display_path(out_dir / "evaluator_manifest.jsonl"),
            "ignored_model_visible_packets": display_path(out_dir / "model_visible_packets.jsonl"),
            "ignored_visible_tool_baseline": display_path(out_dir / "visible_tool_baseline.jsonl"),
        },
        "candidate_count": len(evaluator_rows),
        "project_counts": dict(sorted(project_counts.items())),
        "task_counts": dict(sorted(task_counts.items())),
        "source_kind_counts": dict(sorted(source_kind_counts.items())),
        "visible_tool_baseline": {
            "decision_counts": dict(sorted(baseline_decisions.items())),
            "false_accepts": false_accepts,
            "false_accept_rate": None if not baseline_rows else round(false_accepts / len(baseline_rows), 4),
            "headroom_exists": false_accepts == len(baseline_rows) and len(baseline_rows) >= min_cases,
            "interpretation": "A visible-tool-only merge rule accepts every stress case; this creates direct headroom for verifier prompts to reduce false accepts.",
        },
        "case_records": [
            {
                "candidate_id": row["candidate_id"],
                "source_candidate_id": row["source_candidate_id"],
                "source_gate": row["source_gate"],
                "source_kind": row["source_kind"],
                "project": row["project"],
                "task_id": row["task_id"],
                "candidate_type": row["candidate_type"],
                "patch_materialization": row["patch_materialization"],
                "patch_sha256": row["patch_sha256"],
                "patch_size": row["patch_size"],
                "normalized_label": row["normalized_label"],
                "hard_negative_class": row["hard_negative_class"],
                "baseline_decision": "accept",
            }
            for row in evaluator_rows
        ],
        "checks": checks,
        "next_required_step": "Run verifier preflight/matrix only as hard-negative stress-test evidence.",
    }


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    baseline = summary["visible_tool_baseline"]
    lines = [
        "# EVP-8 Realistic Hard-Negative Stress Cohort v0.1",
        "",
        f"- status: `{summary['status']}`",
        f"- candidates: {summary['candidate_count']}",
        f"- projects: `{summary['project_counts']}`",
        f"- source kinds: `{summary['source_kind_counts']}`",
        f"- visible-tool decisions: `{baseline['decision_counts']}`",
        f"- visible-tool false accepts: {baseline['false_accepts']}",
        f"- visible-tool false accept rate: `{baseline['false_accept_rate']}`",
        f"- headroom exists: `{baseline['headroom_exists']}`",
        "",
        "Boundary: this is a hard-negative stress-test cohort, not a pure",
        "agent-generated realistic cohort. Patch-bearing packets are written only",
        "under ignored `outputs/**`; this tracked report stores hashes and",
        "aggregate/case metadata only.",
        "",
        "## Tasks",
        "",
    ]
    for task_id, count in summary["task_counts"].items():
        lines.append(f"- `{task_id}`: {count}")
    lines += ["", "## Checks", ""]
    for row in summary["checks"]:
        lines.append(f"- {row['check']}: {'passed' if row['passed'] else 'failed'} ({row['detail']})")
    lines += ["", "## Next Step", "", summary["next_required_step"], ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate", type=Path, action="append", default=None)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--summary-out", type=Path, default=DEFAULT_SUMMARY_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--min-cases", type=int, default=MIN_CASES)
    parser.add_argument("--min-projects", type=int, default=MIN_PROJECTS)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cases: list[dict[str, Any]] = []
    for gate_path in args.gate or DEFAULT_GATE_PATHS:
        cases.extend(load_gate_cases(gate_path))
    evaluator_rows = [evaluator_row(index, case) for index, case in enumerate(cases, start=1)]
    model_visible_rows = [model_visible_row(index, case) for index, case in enumerate(cases, start=1)]
    baseline_rows = [baseline_row(row) for row in evaluator_rows]
    write_jsonl(args.out_dir / "evaluator_manifest.jsonl", evaluator_rows)
    write_jsonl(args.out_dir / "model_visible_packets.jsonl", model_visible_rows)
    write_jsonl(args.out_dir / "visible_tool_baseline.jsonl", baseline_rows)
    summary = build_summary(
        evaluator_rows=evaluator_rows,
        model_visible_rows=model_visible_rows,
        baseline_rows=baseline_rows,
        out_dir=args.out_dir,
        min_cases=args.min_cases,
        min_projects=args.min_projects,
    )
    write_json(args.summary_out, summary)
    write_markdown(args.md_out, summary)
    print(json.dumps(summary["visible_tool_baseline"], ensure_ascii=False, indent=2, sort_keys=True))
    if args.check and summary["status"] != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
