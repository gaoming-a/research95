from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_CANDIDATES = Path("outputs") / "patch_verification_pilot_001" / "candidates.jsonl"
DEFAULT_EVIDENCE = Path("outputs") / "patch_verification_pilot_001" / "evidence_packets.jsonl"


def run_step(command: list[str]) -> None:
    print(f"\n$ {' '.join(command)}", flush=True)
    subprocess.run(command, check=True)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def count_jsonl(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def require_file(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"missing {label}: {path}")


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_summary(run_dir: Path) -> dict[str, Any]:
    reviews = run_dir / "reviews.jsonl"
    metrics = run_dir / "metrics.json"
    api_report = run_dir / "api_pilot_report.md"
    failure_examples = run_dir / "failure_examples.json"
    gate_report = run_dir / "gate_report.json"
    paper_readiness = run_dir / "paper_readiness.json"
    run_completeness = run_dir / "run_completeness.json"
    gate = read_json(gate_report)
    paper = read_json(paper_readiness)
    completeness = read_json(run_completeness)
    return {
        "run_dir": run_dir.as_posix(),
        "reviews_count": count_jsonl(reviews),
        "metrics_verifier_output_count": read_json(metrics).get("verifier_output_count"),
        "api_report": api_report.as_posix(),
        "failure_examples": failure_examples.as_posix(),
        "gate_report": gate_report.as_posix(),
        "paper_readiness": paper_readiness.as_posix(),
        "gate_verdict": gate.get("verdict"),
        "gate_reason": gate.get("reason"),
        "mock_review_count": gate.get("mock_review_count"),
        "run_completeness": run_completeness.as_posix(),
        "run_completeness_passed": completeness.get("passed"),
        "expected_records": completeness.get("expected_records"),
        "positive_claim_ready": paper.get("positive_claim_ready"),
        "minimum_paper_inputs_ready": paper.get("minimum_inputs_ready"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run all post-processing steps for an API pilot run directory.")
    parser.add_argument("--run-dir", required=True, help="Directory containing reviews.jsonl and metrics.json.")
    parser.add_argument("--candidates", default=str(DEFAULT_CANDIDATES))
    parser.add_argument("--evidence-packets", default=str(DEFAULT_EVIDENCE))
    parser.add_argument("--summary-out", help="Defaults to <run-dir>/postprocess_summary.json.")
    parser.add_argument("--expected-candidates", type=int, help="Expected reviewed candidate count for this smoke/full run.")
    parser.add_argument("--expected-records", type=int, help="Expected review record count for this smoke/full run.")
    parser.add_argument("--allow-mock", action="store_true", help="Allow mock reviewer records for pipeline smoke tests.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir)
    candidates = Path(args.candidates)
    evidence_packets = Path(args.evidence_packets)
    summary_out = Path(args.summary_out) if args.summary_out else run_dir / "postprocess_summary.json"

    for label, path in [
        ("run directory", run_dir),
        ("reviews", run_dir / "reviews.jsonl"),
        ("metrics", run_dir / "metrics.json"),
        ("candidates", candidates),
        ("evidence packets", evidence_packets),
    ]:
        require_file(path, label)

    run_summary = run_dir / "run_summary.md"
    run_completeness_command = [
        sys.executable,
        "scripts/audit_api_run_completeness.py",
        "--run-dir",
        str(run_dir),
        "--candidates",
        str(candidates),
        "--out-json",
        str(run_dir / "run_completeness.json"),
        "--out-md",
        str(run_dir / "run_completeness.md"),
        "--require-complete",
    ]
    if args.expected_candidates is not None:
        run_completeness_command.extend(["--expected-candidates", str(args.expected_candidates)])
    if args.expected_records is not None:
        run_completeness_command.extend(["--expected-records", str(args.expected_records)])
    if args.allow_mock:
        run_completeness_command.append("--allow-mock")
    run_step(run_completeness_command)
    run_step(
        [
            sys.executable,
            "scripts/summarize_api_pilot_results.py",
            "--reviews",
            str(run_dir / "reviews.jsonl"),
            "--metrics",
            str(run_dir / "metrics.json"),
            "--out",
            str(run_dir / "api_pilot_report.md"),
            *(
                [
                    "--run-summary",
                    str(run_summary),
                ]
                if run_summary.exists()
                else []
            ),
        ]
    )
    run_step(
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
    run_step(
        [
            sys.executable,
            "scripts/evaluate_api_pilot_gate.py",
            "--metrics",
            str(run_dir / "metrics.json"),
            "--reviews",
            str(run_dir / "reviews.jsonl"),
            "--out-json",
            str(run_dir / "gate_report.json"),
            "--out-md",
            str(run_dir / "gate_report.md"),
        ]
    )
    run_step(
        [
            sys.executable,
            "scripts/audit_paper_readiness.py",
            "--full-run-dir",
            str(run_dir),
            "--out-json",
            str(run_dir / "paper_readiness.json"),
            "--out-md",
            str(run_dir / "paper_readiness.md"),
        ]
    )

    summary = build_summary(run_dir)
    write_json(summary_out, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
