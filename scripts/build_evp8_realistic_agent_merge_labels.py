"""Build merge-correct labels for the EVP-8 realistic agent cohort.

The merge label requires both hidden oracle success and declared visible-test
success. Hidden oracle success alone is not enough for a merge-gate label if the
candidate still fails the declared visible fail-to-pass tests.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVALUATOR_IN = REPO_ROOT / "data" / "patches" / "evp8_realistic_agent_evaluator_manifest_v0_2.jsonl"
DEFAULT_ORACLE_RECORDS_IN = REPO_ROOT / "data" / "patches" / "evp8_realistic_agent_oracle_revalidation_v0_1.jsonl"
DEFAULT_VISIBLE_OUTCOMES_IN = REPO_ROOT / "data" / "evidence" / "evp8_realistic_agent_visible_test_outcomes_v0_1.jsonl"
DEFAULT_EVALUATOR_OUT = REPO_ROOT / "data" / "patches" / "evp8_realistic_agent_evaluator_manifest_v0_3.jsonl"
DEFAULT_SUMMARY_OUT = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_merge_label_manifest_v0_3.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_realistic_agent_merge_label_manifest_v0_3.md"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def index(rows: list[dict[str, Any]], field: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = str(row[field])
        if key in result:
            raise ValueError(f"duplicate {field}: {key}")
        result[key] = row
    return result


def visible_passed(outcome: dict[str, Any]) -> bool:
    summary = outcome.get("visible_run_summary") or {}
    counts = Counter(str(result.get("outcome")) for result in outcome.get("test_results", []))
    return outcome.get("run_status") == "completed" and summary.get("passed") is True and set(counts) == {"passed"}


def merge_label(oracle_record: dict[str, Any], visible_outcome: dict[str, Any]) -> str:
    if not oracle_record.get("patch_applied"):
        return "patch_apply_failed"
    if oracle_record.get("dependency_error_count"):
        return "environment_invalid"
    if not visible_passed(visible_outcome):
        return "visible_test_failing_wrong"
    if oracle_record.get("oracle_passed"):
        return "correct"
    return "test_passing_wrong"


def build(
    evaluator_rows: list[dict[str, Any]],
    oracle_records: list[dict[str, Any]],
    visible_outcomes: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    oracle = index(oracle_records, "candidate_id")
    visible = index(visible_outcomes, "candidate_id")
    rows: list[dict[str, Any]] = []
    transitions = Counter()
    for row in evaluator_rows:
        candidate_id = row["candidate_id"]
        label = merge_label(oracle[candidate_id], visible[candidate_id])
        transitions[f"{row['normalized_label']}->{label}"] += 1
        corrected = row | {
            "normalized_label": label,
            "expected_outcome": "correct" if label == "correct" else "incorrect",
            "label_confidence": "high" if label in {"correct", "test_passing_wrong", "visible_test_failing_wrong"} else label,
            "nontrivial_hard_negative": label != "correct",
            "hidden_validation_summary": (row.get("hidden_validation_summary") or {}) | {
                "merge_label_manifest_id": "evp8_realistic_agent_merge_label_manifest_v0_3",
                "visible_tests_passed": visible_passed(visible[candidate_id]),
                "merge_correct_requires_visible_and_hidden_pass": True,
            },
        }
        rows.append(corrected)
    summary = {
        "analysis_id": "evp8_realistic_agent_merge_label_manifest_v0_3",
        "candidate_count": len(rows),
        "label_counts": dict(sorted(Counter(row["normalized_label"] for row in rows).items())),
        "transition_counts": dict(sorted(transitions.items())),
        "visible_passed_count": sum(1 for row in visible_outcomes if visible_passed(row)),
        "oracle_passed_count": sum(1 for row in oracle_records if row.get("oracle_passed")),
        "merge_correct_count": sum(1 for row in rows if row["normalized_label"] == "correct"),
        "environment_invalid_count": sum(1 for row in rows if row["normalized_label"] == "environment_invalid"),
        "label_policy": "correct iff patch applies, declared visible tests pass, and hidden oracle passes",
    }
    return rows, summary


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# EVP-8 Realistic Agent Merge Label Manifest v0.3",
        "",
        "Date: 2026-06-30",
        "",
        "This evaluator-side manifest defines merge-correct labels. A candidate",
        "is `correct` only when it applies, passes declared visible tests, and",
        "passes the hidden oracle.",
        "",
        f"- candidates: {summary['candidate_count']}",
        f"- labels: `{summary['label_counts']}`",
        f"- transitions: `{summary['transition_counts']}`",
        f"- visible passed: {summary['visible_passed_count']}",
        f"- oracle passed: {summary['oracle_passed_count']}",
        f"- merge correct: {summary['merge_correct_count']}",
        f"- environment invalid: {summary['environment_invalid_count']}",
        "",
        f"Policy: {summary['label_policy']}.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluator-in", type=Path, default=DEFAULT_EVALUATOR_IN)
    parser.add_argument("--oracle-records-in", type=Path, default=DEFAULT_ORACLE_RECORDS_IN)
    parser.add_argument("--visible-outcomes-in", type=Path, default=DEFAULT_VISIBLE_OUTCOMES_IN)
    parser.add_argument("--evaluator-out", type=Path, default=DEFAULT_EVALUATOR_OUT)
    parser.add_argument("--summary-out", type=Path, default=DEFAULT_SUMMARY_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows, summary = build(
        evaluator_rows=read_jsonl(args.evaluator_in),
        oracle_records=read_jsonl(args.oracle_records_in),
        visible_outcomes=read_jsonl(args.visible_outcomes_in),
    )
    write_jsonl(args.evaluator_out, rows)
    write_json(args.summary_out, summary)
    write_markdown(args.md_out, summary)
    if args.check:
        if summary["candidate_count"] != 53:
            raise SystemExit(f"expected 53 candidates, got {summary['candidate_count']}")
        if summary["environment_invalid_count"] != 0:
            raise SystemExit(f"environment invalid labels remain: {summary['environment_invalid_count']}")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
