from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_FULL_RUN_DIR = Path("outputs") / "patch_verification_api_pilot_002"


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def count_jsonl(path: Path) -> int | None:
    if not path.exists():
        return None
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def file_state(path: Path) -> dict[str, Any]:
    return {
        "path": path.as_posix(),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
    }


def review_state(run_dir: Path) -> dict[str, Any]:
    reviews_path = run_dir / "reviews.jsonl"
    metrics_path = run_dir / "metrics.json"
    reviews_count = count_jsonl(reviews_path)
    metrics = read_json(metrics_path)
    metric_count = metrics.get("verifier_output_count") if metrics else None
    return {
        "reviews_path": reviews_path.as_posix(),
        "reviews_count": reviews_count,
        "metrics_path": metrics_path.as_posix(),
        "metrics_count": metric_count,
        "counts_match": reviews_count is not None and reviews_count == metric_count,
    }


def failure_state(run_dir: Path) -> dict[str, Any]:
    failure_json = read_json(run_dir / "failure_examples.json")
    if failure_json is None:
        return {
            "exists": False,
            "mock_review_count": None,
            "bucket_counts": {},
            "usable_for_paper": False,
        }
    return {
        "exists": True,
        "mock_review_count": failure_json.get("mock_review_count"),
        "bucket_counts": failure_json.get("bucket_counts", {}),
        "usable_for_paper": failure_json.get("mock_review_count") == 0,
    }


def gate_state(run_dir: Path) -> dict[str, Any]:
    gate = read_json(run_dir / "gate_report.json")
    if gate is None:
        return {
            "exists": False,
            "verdict": None,
            "usable_for_positive_claim": False,
        }
    return {
        "exists": True,
        "verdict": gate.get("verdict"),
        "reason": gate.get("reason"),
        "mock_review_count": gate.get("mock_review_count"),
        "usable_for_positive_claim": gate.get("verdict") == "continue" and gate.get("mock_review_count") == 0,
    }


def completeness_state(run_dir: Path) -> dict[str, Any]:
    completeness = read_json(run_dir / "run_completeness.json")
    if completeness is None:
        return {
            "exists": False,
            "passed": False,
            "expected_records": None,
            "review_count": None,
            "mock_review_count": None,
            "usable_full_run": False,
        }
    return {
        "exists": True,
        "passed": completeness.get("passed") is True,
        "expected_records": completeness.get("expected_records"),
        "review_count": completeness.get("review_count"),
        "mock_review_count": completeness.get("mock_review_count"),
        "usable_full_run": (
            completeness.get("passed") is True
            and completeness.get("expected_records") == 60
            and completeness.get("review_count") == 60
            and completeness.get("mock_review_count") == 0
        ),
    }


def build_audit(args: argparse.Namespace) -> dict[str, Any]:
    run_dir = Path(args.full_run_dir)
    required_docs = {
        "pilot_report": file_state(Path("docs") / "experiments" / "patch_verification_pilot_report.md"),
        "paper_draft": file_state(Path("docs") / "paper" / "patch_verification_draft.md"),
        "paper_outline": file_state(Path("docs") / "paper" / "patch_verification_outline.md"),
        "generated_tables_md": file_state(Path("docs") / "paper" / "generated_tables.md"),
        "generated_tables_tex": file_state(Path("docs") / "paper" / "generated_tables.tex"),
        "ieee_preapi_draft": file_state(Path("docs") / "paper" / "ieee_preapi_draft.tex"),
        "model_selection_shortlist": file_state(Path("docs") / "experiments" / "model_selection_shortlist.md"),
        "model_selection_protocol": file_state(Path("docs") / "experiments" / "model_selection_protocol.md"),
    }
    pre_api_evidence = {
        "reproducibility_compare": file_state(Path("outputs") / "reproducibility" / "pilot_compare.json"),
        "model_catalog_audit": file_state(Path("outputs") / "model_selection" / "openrouter_catalog_audit.json"),
        "pre_api_handoff": file_state(Path("outputs") / "handoff" / "pre_api_handoff.json"),
    }
    run_files = {
        "api_pilot_report": file_state(run_dir / "api_pilot_report.md"),
        "run_summary": file_state(run_dir / "run_summary.md"),
        "failure_examples_md": file_state(run_dir / "failure_examples.md"),
        "gate_report_md": file_state(run_dir / "gate_report.md"),
    }
    reviews = review_state(run_dir)
    failures = failure_state(run_dir)
    gate = gate_state(run_dir)
    completeness = completeness_state(run_dir)

    minimum_inputs_ready = all(doc["exists"] for doc in required_docs.values()) and all(
        state["exists"] for state in run_files.values()
    ) and reviews["counts_match"] and completeness["usable_full_run"] and failures["usable_for_paper"] and gate["exists"]
    positive_claim_ready = bool(minimum_inputs_ready and gate["usable_for_positive_claim"])
    negative_or_methods_draft_ready = bool(
        all(state["exists"] for state in required_docs.values())
        and all(state["exists"] for state in pre_api_evidence.values())
    )

    blockers: list[str] = []
    if not reviews["counts_match"]:
        blockers.append("Missing real API reviews/metrics or counts do not match.")
    if not completeness["usable_full_run"]:
        blockers.append("Missing run completeness evidence for a 60-record non-mock full run.")
    if not run_files["api_pilot_report"]["exists"]:
        blockers.append("Missing API pilot report.")
    if not failures["usable_for_paper"]:
        blockers.append("Missing non-mock failure examples.")
    if not gate["exists"]:
        blockers.append("Missing stop/continue gate report.")
    elif gate["verdict"] != "continue":
        blockers.append(f"Gate verdict is `{gate['verdict']}`, so positive claims are not ready.")

    return {
        "full_run_dir": run_dir.as_posix(),
        "minimum_inputs_ready": minimum_inputs_ready,
        "positive_claim_ready": positive_claim_ready,
        "negative_or_methods_draft_ready": negative_or_methods_draft_ready,
        "required_docs": required_docs,
        "pre_api_evidence": pre_api_evidence,
        "run_files": run_files,
        "reviews": reviews,
        "completeness": completeness,
        "failures": failures,
        "gate": gate,
        "blockers": blockers,
    }


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# Paper Draft Readiness Audit",
        "",
        "## Summary",
        "",
        f"- full run dir: `{audit['full_run_dir']}`",
        f"- minimum inputs ready: {bool_mark(audit['minimum_inputs_ready'])}",
        f"- positive claim ready: {bool_mark(audit['positive_claim_ready'])}",
        f"- methods/negative draft ready: {bool_mark(audit['negative_or_methods_draft_ready'])}",
        "",
        "## Required Docs",
        "",
    ]
    for name, state in audit["required_docs"].items():
        lines.append(f"- `{name}`: {bool_mark(state['exists'])} (`{state['path']}`)")
    lines.extend(["", "## Pre-API Evidence", ""])
    for name, state in audit["pre_api_evidence"].items():
        lines.append(f"- `{name}`: {bool_mark(state['exists'])} (`{state['path']}`)")
    lines.extend(["", "## Full-Run Files", ""])
    for name, state in audit["run_files"].items():
        lines.append(f"- `{name}`: {bool_mark(state['exists'])} (`{state['path']}`)")
    lines.extend(
        [
            "",
            "## Reviews",
            "",
            f"- reviews count: {audit['reviews']['reviews_count']}",
            f"- metrics count: {audit['reviews']['metrics_count']}",
            f"- counts match: {bool_mark(audit['reviews']['counts_match'])}",
            "",
            "## Run Completeness",
            "",
            f"- exists: {bool_mark(audit['completeness']['exists'])}",
            f"- passed: {bool_mark(audit['completeness']['passed'])}",
            f"- expected records: {audit['completeness']['expected_records']}",
            f"- review count: {audit['completeness']['review_count']}",
            f"- mock review count: {audit['completeness']['mock_review_count']}",
            f"- usable full run: {bool_mark(audit['completeness']['usable_full_run'])}",
            "",
            "## Failure Examples",
            "",
            f"- exists: {bool_mark(audit['failures']['exists'])}",
            f"- mock review count: {audit['failures']['mock_review_count']}",
            f"- bucket counts: `{audit['failures']['bucket_counts']}`",
            "",
            "## Gate",
            "",
            f"- exists: {bool_mark(audit['gate']['exists'])}",
            f"- verdict: `{audit['gate']['verdict']}`",
            f"- usable for positive claim: {bool_mark(audit['gate']['usable_for_positive_claim'])}",
            "",
            "## Blockers",
            "",
        ]
    )
    if audit["blockers"]:
        for blocker in audit["blockers"]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit whether the paper draft can move beyond pre-API methods.")
    parser.add_argument("--full-run-dir", default=str(DEFAULT_FULL_RUN_DIR))
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = build_audit(args)
    write_json(Path(args.out_json), audit)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(audit), encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
