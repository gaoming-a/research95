from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


NO_API_REPRO_DIR = Path("outputs") / "patch_verification_pilot_repro_001"
SMOKE_API_DIR = Path("outputs") / "patch_verification_api_pilot_001_tokens4096"
FULL_API_DIR = Path("outputs") / "patch_verification_api_pilot_002"
TOOL_AUGMENTED_FULL_DIR = Path("outputs") / "patch_verification_tool_augmented_full_001"


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
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
            raise ValueError(f"{path}:{line_number} must contain a JSON object")
        rows.append(value)
    return rows


def count_jsonl(path: Path) -> int | None:
    if not path.exists():
        return None
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def paper_claim_allowed(value: bool) -> str:
    return "yes" if value else "no"


def first_model(reviews: list[dict[str, Any]]) -> str | None:
    for record in reviews:
        model = record.get("model")
        if model:
            return str(model)
    return None


def no_api_record() -> dict[str, Any]:
    readiness = read_json(Path("outputs/readiness_audit/latest.json")) or {}
    repro = read_json(Path("outputs/reproducibility/pilot_compare.json")) or {}
    validation = read_json(NO_API_REPRO_DIR / "validation_summary.json") or {}
    prompt_records = count_jsonl(NO_API_REPRO_DIR / "api_prompt_dry_run" / "prompt_manifest.jsonl")
    no_api = readiness.get("no_api") or {}
    counts = no_api.get("counts") or {}
    return {
        "run_id": "patch_verification_pilot_repro_001",
        "run_dir": NO_API_REPRO_DIR.as_posix(),
        "run_type": "no_api_repro",
        "date": modified_or_now(NO_API_REPRO_DIR),
        "model_slug": None,
        "conditions": ["deterministic_baselines", "prompt_dry_run"],
        "candidate_count": counts.get("candidates"),
        "review_record_count": counts.get("verifier_outputs"),
        "mock_review_count": 0,
        "command": "python scripts\\run_no_api_patch_pipeline.py --out-dir outputs\\patch_verification_pilot_repro_001",
        "key_outputs": [
            (NO_API_REPRO_DIR / "candidates.jsonl").as_posix(),
            (NO_API_REPRO_DIR / "validation_summary.json").as_posix(),
            "outputs/reproducibility/pilot_compare.json",
        ],
        "gate_verdict": "no_api_ready" if no_api.get("ready") and repro.get("matched") else "not_ready",
        "paper_claim_allowed": "no",
        "notes": {
            "validation_all_validated": validation.get("all_validated"),
            "prompt_dry_run_records": prompt_records,
            "deterministic_reproducibility_matched": repro.get("matched"),
            "boundary": "No model-review result; usable for methods, validation, and reproducibility evidence only.",
        },
    }


def api_record(run_dir: Path, run_id: str, run_type: str, expected_candidates: int) -> dict[str, Any]:
    reviews = read_jsonl(run_dir / "reviews.jsonl")
    metrics = read_json(run_dir / "metrics.json") or {}
    completeness = read_json(run_dir / "run_completeness.json") or {}
    gate = read_json(run_dir / "gate_report.json") or {}
    postprocess = read_json(run_dir / "postprocess_summary.json") or {}
    run_error_exists = (run_dir / "run_error.json").exists()
    mock_count = completeness.get("mock_review_count")
    if mock_count is None:
        mock_count = metrics.get("mock_review_count")
    gate_verdict = gate.get("verdict")
    positive_allowed = bool(
        run_type == "full_api"
        and reviews
        and not run_error_exists
        and completeness.get("passed") is True
        and completeness.get("expected_records") == expected_candidates * 2
        and mock_count == 0
        and gate_verdict == "continue"
    )
    return {
        "run_id": run_id,
        "run_dir": run_dir.as_posix(),
        "run_type": run_type,
        "date": modified_or_now(run_dir),
        "model_slug": first_model(reviews),
        "conditions": sorted({str(record.get("condition")) for record in reviews if record.get("condition")}),
        "candidate_count": completeness.get("unique_reviewed_candidates"),
        "review_record_count": len(reviews) if reviews else None,
        "mock_review_count": mock_count,
        "command": api_command(run_type),
        "key_outputs": existing_outputs(
            run_dir,
            [
                "reviews.jsonl",
                "metrics.json",
                "run_summary.md",
                "run_completeness.json",
                "api_pilot_report.md",
                "failure_examples.json",
                "gate_report.json",
                "postprocess_summary.json",
            ],
        ),
        "gate_verdict": gate_verdict or ("incomplete" if run_error_exists or not reviews else "missing_gate"),
        "paper_claim_allowed": paper_claim_allowed(positive_allowed),
        "notes": {
            "expected_candidates": expected_candidates,
            "expected_records": expected_candidates * 2,
            "run_error_exists": run_error_exists,
            "completeness_passed": completeness.get("passed"),
            "postprocess_gate_verdict": postprocess.get("gate_verdict"),
            "boundary": api_boundary(run_type, reviews, mock_count, positive_allowed),
        },
    }


def quality_record() -> dict[str, Any]:
    quality = read_json(Path("outputs/local_quality_gate/latest.json")) or {}
    handoff = read_json(Path("outputs/handoff/pre_api_handoff.json")) or {}
    return {
        "run_id": "local_quality_gate_latest",
        "run_dir": "outputs/local_quality_gate",
        "run_type": "quality_gate",
        "date": modified_or_now(Path("outputs/local_quality_gate")),
        "model_slug": None,
        "conditions": ["local_no_api_gates"],
        "candidate_count": None,
        "review_record_count": None,
        "mock_review_count": None,
        "command": "python scripts\\run_local_quality_gate.py --out-json outputs\\local_quality_gate\\latest.json --out-md outputs\\local_quality_gate\\latest.md",
        "key_outputs": [
            "outputs/local_quality_gate/latest.json",
            "outputs/local_quality_gate/latest.md",
            "outputs/handoff/pre_api_handoff.json",
        ],
        "gate_verdict": "passed" if quality.get("passed") else "failed_or_missing",
        "paper_claim_allowed": "no",
        "notes": {
            "ready_for_real_api": quality.get("readiness", {}).get("overall_ready_for_real_api"),
            "pre_api_handoff_ready_for_real_api": handoff.get("ready_for_real_api"),
            "full_goal_complete": quality.get("goal_completion", {}).get("complete"),
            "boundary": "Local quality gate reports readiness; it is not a model experiment result.",
        },
    }


def tool_augmented_record() -> dict[str, Any]:
    run_dir = TOOL_AUGMENTED_FULL_DIR
    reviews = read_jsonl(run_dir / "reviews.jsonl")
    metrics = read_json(run_dir / "metrics.json") or {}
    completeness = read_json(run_dir / "run_completeness.json") or {}
    gate = read_json(run_dir / "tool_augmented_full_gate.json") or {}
    run_error_exists = (run_dir / "run_error.json").exists()
    mock_count = completeness.get("mock_review_count")
    if mock_count is None:
        mock_count = metrics.get("mock_review_count")
    positive_allowed = bool(
        reviews
        and not run_error_exists
        and completeness.get("passed") is True
        and completeness.get("expected_records") == 30
        and completeness.get("unique_reviewed_candidates") == 30
        and mock_count == 0
        and gate.get("passed") is True
    )
    return {
        "run_id": "patch_verification_tool_augmented_full_001",
        "run_dir": run_dir.as_posix(),
        "run_type": "tool_augmented_full_api",
        "date": modified_or_now(run_dir),
        "model_slug": first_model(reviews),
        "conditions": sorted({str(record.get("condition")) for record in reviews if record.get("condition")}),
        "candidate_count": completeness.get("unique_reviewed_candidates"),
        "review_record_count": len(reviews) if reviews else None,
        "mock_review_count": mock_count,
        "command": (
            "python scripts\\run_redesign_smoke_workflow.py "
            "--config outputs\\patch_verification_tool_augmented_full_001\\api_config.local.json "
            "--run-dir outputs\\patch_verification_tool_augmented_full_001 "
            "--gate-mode full --execute"
        ),
        "key_outputs": existing_outputs(
            run_dir,
            [
                "reviews.jsonl",
                "metrics.json",
                "run_summary.md",
                "run_completeness.json",
                "api_pilot_report.md",
                "failure_examples.json",
                "tool_augmented_full_gate.json",
            ],
        ),
        "gate_verdict": "passed" if gate.get("passed") is True else "failed_or_missing",
        "paper_claim_allowed": paper_claim_allowed(positive_allowed),
        "notes": {
            "expected_candidates": 30,
            "expected_records": 30,
            "run_error_exists": run_error_exists,
            "completeness_passed": completeness.get("passed"),
            "tool_augmented_gate_passed": gate.get("passed"),
            "boundary": (
                "Full non-mock tool-augmented run; eligible only for the conditional "
                "tool-assisted verification claim, not for the prompt-only evidence-first claim."
            )
            if positive_allowed
            else "Tool-augmented full run is not currently eligible for a positive conditional claim.",
        },
    }


def api_command(run_type: str) -> str:
    if run_type == "smoke_api":
        return (
            "python scripts\\run_api_pilot_workflow.py --config configs\\api_pilot.local.json "
            "--run-dir outputs\\patch_verification_api_pilot_001_tokens4096 --execute"
        )
    return (
        "python scripts\\run_api_pilot_workflow.py --config configs\\api_pilot.local.json "
        "--run-dir outputs\\patch_verification_api_pilot_002 --limit 0 --execute"
    )


def api_boundary(run_type: str, reviews: list[dict[str, Any]], mock_count: Any, positive_allowed: bool) -> str:
    if not reviews:
        return "No real API reviews are present for this run directory."
    if mock_count:
        return "Mock output; pipeline validation only."
    if run_type == "smoke_api":
        return "Smoke output; validates real API chain but is not the full paper result."
    if positive_allowed:
        return "Full non-mock run with continue gate; eligible for positive paper claim subject to manual qualitative review."
    return "Full run is not currently eligible for positive paper claim."


def existing_outputs(run_dir: Path, names: list[str]) -> list[str]:
    return [(run_dir / name).as_posix() for name in names if (run_dir / name).exists()]


def modified_or_now(path: Path) -> str:
    if path.exists():
        timestamp = path.stat().st_mtime
        return datetime.fromtimestamp(timestamp, timezone.utc).isoformat()
    return datetime.now(timezone.utc).isoformat()


def build_ledger() -> dict[str, Any]:
    records = [
        no_api_record(),
        api_record(SMOKE_API_DIR, "patch_verification_api_pilot_001_tokens4096", "smoke_api", 2),
        api_record(FULL_API_DIR, "patch_verification_api_pilot_002", "full_api", 30),
        tool_augmented_record(),
        quality_record(),
    ]
    readiness = read_json(Path("outputs/readiness_audit/latest.json")) or {}
    paper = read_json(Path("outputs/paper_readiness/latest.json")) or {}
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "records": records,
        "summary": {
            "record_count": len(records),
            "real_api_ready": readiness.get("overall_ready_for_real_api"),
            "prompt_only_positive_paper_claim_ready": paper.get("positive_claim_ready"),
            "tool_augmented_claim_ready": paper.get("tool_augmented_claim_ready"),
            "records_allowing_paper_claim": [
                record["run_id"] for record in records if record.get("paper_claim_allowed") == "yes"
            ],
        },
    }


def build_markdown(ledger: dict[str, Any]) -> str:
    lines = [
        "# Experiment Run Records",
        "",
        "## Summary",
        "",
        f"- generated at UTC: `{ledger['generated_at_utc']}`",
        f"- record count: {ledger['summary']['record_count']}",
        f"- real API ready: {bool_mark(ledger['summary'].get('real_api_ready'))}",
        f"- prompt-only positive paper claim ready: {bool_mark(ledger['summary'].get('prompt_only_positive_paper_claim_ready'))}",
        f"- tool-augmented claim ready: {bool_mark(ledger['summary'].get('tool_augmented_claim_ready'))}",
        f"- records allowing paper claim: `{ledger['summary']['records_allowing_paper_claim']}`",
        "",
        "## Records",
        "",
        "| run id | type | model | candidates | review records | mock records | gate | paper claim |",
        "|---|---|---|---:|---:|---:|---|---:|",
    ]
    for record in ledger["records"]:
        lines.append(
            "| {run_id} | {run_type} | {model} | {candidates} | {reviews} | {mock} | {gate} | {claim} |".format(
                run_id=f"`{record['run_id']}`",
                run_type=f"`{record['run_type']}`",
                model=f"`{record['model_slug']}`" if record.get("model_slug") else "",
                candidates=record.get("candidate_count"),
                reviews=record.get("review_record_count"),
                mock=record.get("mock_review_count"),
                gate=f"`{record.get('gate_verdict')}`",
                claim=record.get("paper_claim_allowed"),
            )
        )
    lines.extend(["", "## Notes", ""])
    for record in ledger["records"]:
        lines.append(f"- `{record['run_id']}`: {record['notes'].get('boundary')}")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write the experiment run-record ledger required by the AI execution plan.")
    parser.add_argument("--out-json", default="outputs/experiment_run_records/latest.json")
    parser.add_argument("--out-md", default="outputs/experiment_run_records/latest.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ledger = build_ledger()
    write_json(Path(args.out_json), ledger)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(ledger), encoding="utf-8")
    print(json.dumps({"out_json": args.out_json, "out_md": args.out_md, "record_count": len(ledger["records"])}, indent=2))


if __name__ == "__main__":
    main()
