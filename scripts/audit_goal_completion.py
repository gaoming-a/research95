from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


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


def git_state() -> dict[str, Any]:
    status = subprocess.run(["git", "status", "--short"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    remote = subprocess.run(["git", "remote", "-v"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {
        "is_repo": status.returncode == 0,
        "status_short": status.stdout.strip().splitlines() if status.returncode == 0 else [],
        "remote_exists": remote.returncode == 0 and bool(remote.stdout.strip()),
        "remote_stdout": remote.stdout.strip() if remote.returncode == 0 else "",
        "status_error": status.stderr.strip() if status.returncode != 0 else "",
    }


def file_exists(path: str) -> bool:
    return Path(path).exists()


def check(name: str, passed: bool, evidence: dict[str, Any], required: bool = True) -> dict[str, Any]:
    return {
        "name": name,
        "passed": bool(passed),
        "required": required,
        "evidence": evidence,
    }


def build_audit() -> dict[str, Any]:
    readiness = read_json(Path("outputs/readiness_audit/latest.json")) or {}
    plan_progress = read_json(Path("outputs/plan_progress/latest.json")) or {}
    paper = read_json(Path("outputs/paper_readiness/latest.json")) or {}
    local_quality = read_json(Path("outputs/local_quality_gate/latest.json")) or {}
    run_records = read_json(Path("outputs/experiment_run_records/latest.json")) or {}
    youtubedl_decision = read_json(Path("outputs/youtubedl_p2p_decision_audit/latest.json")) or {}
    youtubedl_attempt_path = "docs/experiments/evp7_youtubedl_p2p_execution_attempt_20260613.md"
    youtubedl_manifest_path = "data/p2p_scopes/bugsinpy_youtube-dl_7_p2p_broad.json"
    artifact_audit = read_json(Path("artifacts/research95_anonymous_artifact_audit.json")) or {}
    repro = read_json(Path("outputs/reproducibility/pilot_compare.json")) or {}
    full_dir = Path("outputs/patch_verification_api_pilot_002")
    fallback_full_dir = Path("outputs/patch_verification_api_pilot_001")
    if not (full_dir / "reviews.jsonl").exists() and (fallback_full_dir / "reviews.jsonl").exists():
        full_dir = fallback_full_dir
    tool_augmented_dir = Path("outputs/patch_verification_tool_augmented_full_001")

    full_reviews = count_jsonl(full_dir / "reviews.jsonl")
    full_metrics = read_json(full_dir / "metrics.json")
    full_gate = read_json(full_dir / "gate_report.json")
    full_failures = read_json(full_dir / "failure_examples.json")
    full_completeness = read_json(full_dir / "run_completeness.json")
    tool_reviews = count_jsonl(tool_augmented_dir / "reviews.jsonl")
    tool_metrics = read_json(tool_augmented_dir / "metrics.json")
    tool_completeness = read_json(tool_augmented_dir / "run_completeness.json")
    tool_gate = read_json(tool_augmented_dir / "tool_augmented_full_gate.json")
    git = git_state()
    stage_counts = plan_progress.get("stage_counts", {}) if isinstance(plan_progress, dict) else {}
    ledger_records = run_records.get("records", []) if isinstance(run_records.get("records"), list) else []
    ledger_run_types = sorted({str(record.get("run_type")) for record in ledger_records if isinstance(record, dict)})
    required_ledger_types = ["full_api", "no_api_repro", "quality_gate", "smoke_api", "tool_augmented_full_api"]

    requirements = [
        check(
            "no_api_pipeline_ready",
            bool((readiness.get("no_api") or {}).get("ready")),
            {
                "source": "outputs/readiness_audit/latest.json",
                "no_api": readiness.get("no_api"),
            },
        ),
        check(
            "deterministic_reproducibility_matched",
            repro.get("matched") is True,
            {
                "source": "outputs/reproducibility/pilot_compare.json",
                "matched": repro.get("matched"),
                "checked_file_count": repro.get("checked_file_count"),
            },
        ),
        check(
            "api_prerequisites_ready",
            readiness.get("overall_ready_for_real_api") is True,
            {
                "source": "outputs/readiness_audit/latest.json",
                "overall_ready_for_real_api": readiness.get("overall_ready_for_real_api"),
                "api": readiness.get("api"),
            },
        ),
        check(
            "all_execution_plan_stages_complete",
            bool(stage_counts) and set(stage_counts.keys()) == {"complete"},
            {
                "source": "outputs/plan_progress/latest.json",
                "stage_counts": stage_counts,
            },
        ),
        check(
            "prompt_only_full_api_reviews_present",
            full_reviews == 60
            and full_metrics is not None
            and full_metrics.get("mock_review_count", 0) == 0
            and full_completeness is not None
            and full_completeness.get("passed") is True
            and full_completeness.get("expected_records") == 60
            and full_completeness.get("mock_review_count") == 0,
            {
                "run_dir": full_dir.as_posix(),
                "reviews_count": full_reviews,
                "mock_review_count": full_metrics.get("mock_review_count") if full_metrics else None,
                "run_completeness_passed": full_completeness.get("passed") if full_completeness else None,
                "expected_records": full_completeness.get("expected_records") if full_completeness else None,
            },
        ),
        check(
            "tool_augmented_full_api_reviews_present",
            tool_reviews == 30
            and tool_metrics is not None
            and tool_metrics.get("mock_review_count", 0) == 0
            and tool_completeness is not None
            and tool_completeness.get("passed") is True
            and tool_completeness.get("expected_records") == 30
            and tool_completeness.get("mock_review_count") == 0,
            {
                "run_dir": tool_augmented_dir.as_posix(),
                "reviews_count": tool_reviews,
                "mock_review_count": tool_metrics.get("mock_review_count") if tool_metrics else None,
                "run_completeness_passed": tool_completeness.get("passed") if tool_completeness else None,
                "expected_records": tool_completeness.get("expected_records") if tool_completeness else None,
            },
        ),
        check(
            "postprocess_reports_present",
            all(
                (full_dir / name).exists()
                for name in [
                    "api_pilot_report.md",
                    "failure_examples.md",
                    "gate_report.md",
                    "postprocess_summary.json",
                ]
            ),
            {
                "run_dir": full_dir.as_posix(),
                "required_files": [
                    "api_pilot_report.md",
                    "failure_examples.md",
                    "gate_report.md",
                    "postprocess_summary.json",
                ],
            },
        ),
        check(
            "failure_examples_are_real",
            bool(full_failures and full_failures.get("mock_review_count") == 0),
            {
                "run_dir": full_dir.as_posix(),
                "mock_review_count": full_failures.get("mock_review_count") if full_failures else None,
                "bucket_counts": full_failures.get("bucket_counts") if full_failures else None,
            },
        ),
        check(
            "prompt_only_positive_claim_preserved_as_negative",
            paper.get("prompt_only_positive_claim_ready") is False or paper.get("positive_claim_ready") is False,
            {
                "source": "outputs/paper_readiness/latest.json",
                "prompt_only_positive_claim_ready": paper.get("prompt_only_positive_claim_ready"),
                "positive_claim_ready": paper.get("positive_claim_ready"),
                "blockers": paper.get("blockers"),
            },
        ),
        check(
            "tool_augmented_paper_claim_ready",
            paper.get("tool_augmented_claim_ready") is True,
            {
                "source": "outputs/paper_readiness/latest.json",
                "tool_augmented_claim_ready": paper.get("tool_augmented_claim_ready"),
                "claim_boundary": paper.get("claim_boundary"),
                "tool_augmented_blockers": paper.get("tool_augmented_blockers"),
            },
        ),
        check(
            "prompt_only_gate_preserved_as_redesign_signal",
            bool(full_gate and full_gate.get("verdict") != "continue" and full_gate.get("mock_review_count", 0) == 0),
            {
                "run_dir": full_dir.as_posix(),
                "verdict": full_gate.get("verdict") if full_gate else None,
                "mock_review_count": full_gate.get("mock_review_count") if full_gate else None,
            },
        ),
        check(
            "tool_augmented_gate_supports_conditional_claim",
            bool(
                tool_gate
                and tool_gate.get("passed") is True
                and tool_gate.get("mock_review_count", 0) == 0
                and (tool_gate.get("condition_counts") or {}) == {"tool_augmented_evidence": 30}
                and (tool_gate.get("metrics") or {}).get("false_accept_rate") == 0.0
                and (tool_gate.get("metrics") or {}).get("correct_patch_recall") == 1.0
                and (tool_gate.get("metrics") or {}).get("invalid_output_rate") == 0.0
            ),
            {
                "run_dir": tool_augmented_dir.as_posix(),
                "passed": tool_gate.get("passed") if tool_gate else None,
                "mock_review_count": tool_gate.get("mock_review_count") if tool_gate else None,
                "condition_counts": tool_gate.get("condition_counts") if tool_gate else None,
                "metrics": tool_gate.get("metrics") if tool_gate else None,
            },
        ),
        check(
            "ieee_preapi_draft_exists",
            file_exists("docs/paper/ieee_preapi_draft.tex"),
            {"path": "docs/paper/ieee_preapi_draft.tex"},
        ),
        check(
            "anonymous_artifact_safe",
            artifact_audit.get("safe") is True,
            {
                "source": "artifacts/research95_anonymous_artifact_audit.json",
                "safe": artifact_audit.get("safe"),
                "forbidden_entries": artifact_audit.get("forbidden_entries"),
            },
        ),
        check(
            "local_quality_gate_passed",
            local_quality.get("passed") is True,
            {
                "source": "outputs/local_quality_gate/latest.json",
                "passed": local_quality.get("passed"),
            },
        ),
        check(
            "experiment_run_records_present",
            bool(
                run_records
                and run_records.get("summary", {}).get("record_count") == len(ledger_records)
                and all(item in ledger_run_types for item in required_ledger_types)
            ),
            {
                "source": "outputs/experiment_run_records/latest.json",
                "record_count": run_records.get("summary", {}).get("record_count") if run_records else None,
                "actual_record_count": len(ledger_records),
                "run_types": ledger_run_types,
                "required_run_types": required_ledger_types,
                "records_allowing_paper_claim": run_records.get("summary", {}).get("records_allowing_paper_claim")
                if run_records
                else None,
            },
        ),
        check(
            "git_repository_and_remote_present",
            git["is_repo"] and git["remote_exists"],
            {
                "is_repo": git["is_repo"],
                "remote_exists": git["remote_exists"],
                "status_error": git["status_error"],
            },
        ),
        check(
            "youtube_dl_p2p_decision_resolved",
            bool(
                youtubedl_decision
                and youtubedl_decision.get("passed") is True
                and file_exists(youtubedl_attempt_path)
                and file_exists(youtubedl_manifest_path)
            ),
            {
                "source": "outputs/youtubedl_p2p_decision_audit/latest.json",
                "attempt_record": youtubedl_attempt_path,
                "attempt_record_exists": file_exists(youtubedl_attempt_path),
                "decision_audit_passed": youtubedl_decision.get("passed"),
                "approval_required": (youtubedl_decision.get("command_packet") or {}).get("approval_required"),
                "proposed_manifest": youtubedl_manifest_path,
                "proposed_manifest_exists": file_exists(youtubedl_manifest_path),
                "recommended_task": (youtubedl_decision.get("decision_packet") or {}).get("recommended_task_id"),
                "boundary": (
                    "Goal remains incomplete until the approved youtube-dl_7 P2P path either produces "
                    "a manifest or is explicitly stopped. The first approved attempt timed out in dynamic "
                    "test_download tests, so rerun requires a separate nodeid-level scope-policy decision."
                ),
            },
        ),
    ]

    missing = [item for item in requirements if item["required"] and not item["passed"]]
    return {
        "complete": not missing,
        "requirements": requirements,
        "missing_required": [item["name"] for item in missing],
        "summary": {
            "required_count": len([item for item in requirements if item["required"]]),
            "passed_required_count": len([item for item in requirements if item["required"] and item["passed"]]),
            "missing_required_count": len(missing),
        },
    }


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# Goal Completion Audit",
        "",
        "## Summary",
        "",
        f"- complete: {bool_mark(audit['complete'])}",
        f"- required checks: {audit['summary']['required_count']}",
        f"- passed required checks: {audit['summary']['passed_required_count']}",
        f"- missing required checks: {audit['summary']['missing_required_count']}",
        "",
        "## Requirements",
        "",
        "| requirement | passed | evidence |",
        "|---|---:|---|",
    ]
    for item in audit["requirements"]:
        evidence = json.dumps(item["evidence"], ensure_ascii=False, sort_keys=True)
        lines.append(f"| `{item['name']}` | {bool_mark(item['passed'])} | `{evidence}` |")
    lines.extend(["", "## Missing Required", ""])
    if audit["missing_required"]:
        for name in audit["missing_required"]:
            lines.append(f"- `{name}`")
    else:
        lines.append("- None.")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit whether the full user goal has actually been completed.")
    parser.add_argument("--out-json", default="outputs/goal_completion/latest.json")
    parser.add_argument("--out-md", default="outputs/goal_completion/latest.md")
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Exit non-zero if any required completion condition is missing.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = build_audit()
    write_json(Path(args.out_json), audit)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(audit), encoding="utf-8")
    print(json.dumps({"out_json": args.out_json, "out_md": args.out_md, "complete": audit["complete"]}, indent=2))
    if args.require_complete and not audit["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
