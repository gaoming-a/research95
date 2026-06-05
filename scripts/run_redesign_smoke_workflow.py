from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


EXPECTED_ACCEPT_IDS = {"candidate_0001", "candidate_0023"}
EXPECTED_NOT_ACCEPT_IDS = {"candidate_0005", "candidate_0006", "candidate_0020"}
EXPECTED_CONDITION = "tool_augmented_evidence"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number} must contain a JSON object")
        rows.append(value)
    return rows


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_command(command: list[str], allow_failure: bool = False) -> subprocess.CompletedProcess[str]:
    print(f"\n$ {' '.join(command)}", flush=True)
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    if completed.returncode != 0 and not allow_failure:
        raise subprocess.CalledProcessError(completed.returncode, command)
    return completed


def count_jsonl(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def load_preflight(config: Path, allow_missing_credentials: bool) -> dict[str, Any]:
    command = [sys.executable, "scripts/preflight_api_pilot.py", "--config", str(config)]
    if allow_missing_credentials:
        command.append("--allow-missing-credentials")
    completed = run_command(command, allow_failure=True)
    return json.loads(completed.stdout)


def require_ready(preflight: dict[str, Any]) -> None:
    if not preflight.get("api_ready"):
        failed = [
            {"check": check.get("check"), "detail": check.get("detail"), "path": check.get("path")}
            for check in preflight.get("checks", [])
            if not check.get("passed")
        ]
        raise SystemExit(
            "Redesign smoke stopped before any model call because preflight failed:\n"
            + json.dumps(failed, ensure_ascii=False, indent=2, sort_keys=True)
        )


def evaluate_smoke(reviews: list[dict[str, Any]]) -> dict[str, Any]:
    decisions = {str(record["model_candidate_id"]): str(record["decision"]) for record in reviews}
    invalid_count = sum(1 for record in reviews if record.get("decision") == "invalid_output")
    mock_count = sum(1 for record in reviews if record.get("mock_run"))
    accept_ids = {candidate_id for candidate_id, decision in decisions.items() if decision == "accept"}
    rejected_required_accepts = sorted(EXPECTED_ACCEPT_IDS - accept_ids)
    false_accept_ids = sorted(candidate_id for candidate_id in EXPECTED_NOT_ACCEPT_IDS if decisions.get(candidate_id) == "accept")
    missing_ids = sorted((EXPECTED_ACCEPT_IDS | EXPECTED_NOT_ACCEPT_IDS) - set(decisions))
    passed = not invalid_count and not mock_count and not rejected_required_accepts and not false_accept_ids and not missing_ids
    return {
        "passed": passed,
        "condition": EXPECTED_CONDITION,
        "review_count": len(reviews),
        "mock_review_count": mock_count,
        "invalid_output_count": invalid_count,
        "decisions": dict(sorted(decisions.items())),
        "accept_required_candidate_ids": sorted(EXPECTED_ACCEPT_IDS),
        "not_accept_required_candidate_ids": sorted(EXPECTED_NOT_ACCEPT_IDS),
        "rejected_or_escalated_required_accepts": rejected_required_accepts,
        "false_accept_ids": false_accept_ids,
        "missing_candidate_ids": missing_ids,
        "interpretation": (
            "This is a failure-case redesign smoke gate. Passing it only justifies a larger "
            "tool-augmented experiment; it does not rescue the original prompt-only positive claim."
        ),
    }


def write_smoke_report(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Tool-Augmented Redesign Smoke Gate",
        "",
        f"- passed: `{report['passed']}`",
        f"- condition: `{report['condition']}`",
        f"- reviewer records: {report['review_count']}",
        f"- mock reviewer records: {report['mock_review_count']}",
        f"- invalid outputs: {report['invalid_output_count']}",
        f"- decisions: `{report['decisions']}`",
        f"- required accepts not accepted: `{report['rejected_or_escalated_required_accepts']}`",
        f"- false accepts: `{report['false_accept_ids']}`",
        f"- missing candidates: `{report['missing_candidate_ids']}`",
        "",
        "## Boundary",
        "",
        report["interpretation"],
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def workflow(args: argparse.Namespace) -> dict[str, Any]:
    config_path = Path(args.config)
    config = read_json(config_path)
    run_dir = Path(args.run_dir or config["out_dir"])
    candidates = Path(config["candidates"])
    evidence_packets = Path(config["evidence_packets"])
    conditions = list(config.get("conditions") or [])
    expected_candidates = count_jsonl(evidence_packets)
    expected_records = expected_candidates * len(conditions)

    if conditions != [EXPECTED_CONDITION]:
        raise SystemExit(f"redesign smoke requires conditions={[EXPECTED_CONDITION]}, got {conditions}")

    preflight = load_preflight(config_path, allow_missing_credentials=args.check_only)
    if args.check_only:
        summary = {
            "mode": "check_only",
            "config": config_path.as_posix(),
            "run_dir": run_dir.as_posix(),
            "api_ready": preflight.get("api_ready"),
            "dry_run_ready": preflight.get("dry_run_ready"),
            "model_call_attempted": False,
        }
        if args.summary_out:
            write_json(Path(args.summary_out), summary)
        print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
        return summary

    require_ready(preflight)
    if not args.execute:
        raise SystemExit("Preflight passed, but --execute is required before making real API calls.")
    if (run_dir / "reviews.jsonl").exists() and not args.allow_existing_output:
        raise SystemExit(f"Refusing to overwrite existing redesign smoke outputs in {run_dir}.")

    run_command(
        [
            sys.executable,
            "scripts/run_patch_verification_api_pilot.py",
            "--config",
            str(config_path),
            "--allow-direct-api-run",
        ]
    )
    run_command(
        [
            sys.executable,
            "scripts/audit_api_run_completeness.py",
            "--run-dir",
            str(run_dir),
            "--candidates",
            str(candidates),
            "--conditions",
            *conditions,
            "--expected-candidates",
            str(expected_candidates),
            "--expected-records",
            str(expected_records),
            "--out-json",
            str(run_dir / "run_completeness.json"),
            "--out-md",
            str(run_dir / "run_completeness.md"),
            "--require-complete",
        ]
    )
    run_command(
        [
            sys.executable,
            "scripts/summarize_api_pilot_results.py",
            "--reviews",
            str(run_dir / "reviews.jsonl"),
            "--metrics",
            str(run_dir / "metrics.json"),
            "--run-summary",
            str(run_dir / "run_summary.md"),
            "--out",
            str(run_dir / "api_pilot_report.md"),
        ]
    )
    run_command(
        [
            sys.executable,
            "scripts/extract_api_failure_examples.py",
            "--candidates",
            str(candidates),
            "--evidence-packets",
            str(evidence_packets),
            "--reviews",
            str(run_dir / "reviews.jsonl"),
            "--out-json",
            str(run_dir / "failure_examples.json"),
            "--out-md",
            str(run_dir / "failure_examples.md"),
        ]
    )
    smoke_report = evaluate_smoke(read_jsonl(run_dir / "reviews.jsonl"))
    write_json(run_dir / "redesign_smoke_gate.json", smoke_report)
    write_smoke_report(run_dir / "redesign_smoke_gate.md", smoke_report)
    summary = {
        "mode": "executed",
        "config": config_path.as_posix(),
        "run_dir": run_dir.as_posix(),
        "expected_candidates": expected_candidates,
        "expected_records": expected_records,
        "model_call_attempted": True,
        "redesign_smoke_gate": smoke_report,
    }
    if args.summary_out:
        write_json(Path(args.summary_out), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the guarded tool-augmented redesign smoke workflow.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--run-dir")
    parser.add_argument("--summary-out")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--allow-existing-output", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    workflow(args)


if __name__ == "__main__":
    main()
