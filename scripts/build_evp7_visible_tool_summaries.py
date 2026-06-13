"""Build deterministic EVP-7 visible tool summaries.

These summaries aggregate only model-visible tool evidence: patch-apply/static
status already present in evidence packets and independently rerun visible-test
outcomes. They do not read evaluator labels or hidden validation outcomes.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKETS_IN = REPO_ROOT / "data" / "evidence" / "evp7_evidence_packets.jsonl"
VISIBLE_OUTCOMES_IN = REPO_ROOT / "data" / "evidence" / "evp7_visible_test_outcomes.jsonl"
SUMMARIES_OUT = REPO_ROOT / "data" / "evidence" / "evp7_visible_tool_summaries.jsonl"
SUMMARY_OUT = REPO_ROOT / "data" / "evidence" / "evp7_visible_tool_summary_summary.json"

FORBIDDEN_MARKERS = (
    "label_with_p2p_broad",
    "label_retained_oracle",
    "candidate_type",
    "failure_type_label",
    "expected_outcome",
    "hidden_oracles",
    "patch_id",
    "correct_under_f2p_and_p2p_broad",
    "incorrect_issue_not_fixed",
    "correct_reference",
    "partial_fix",
    "irrelevant_patch",
    "buggy_noop",
)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )


def _counts(values: Any) -> dict[str, int]:
    result: dict[str, int] = {}
    for value in values:
        key = str(value)
        result[key] = result.get(key, 0) + 1
    return dict(sorted(result.items()))


def _packets_by_candidate(packets: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    result: dict[str, dict[str, dict[str, Any]]] = {}
    for packet in packets:
        candidate_id = packet["model_visible"]["candidate_id"]
        result.setdefault(candidate_id, {})[packet["evidence_level"]] = packet
    return result


def _outcomes_by_candidate(path: Path) -> dict[str, dict[str, Any]]:
    return {record["candidate_id"]: record for record in _read_jsonl(path)}


def _summary_record(candidate_id: str, packets: dict[str, dict[str, Any]], outcome: dict[str, Any] | None) -> dict[str, Any]:
    e2 = packets.get("E2", {})
    model_visible = e2.get("model_visible", {})
    static_evidence = e2.get("visible_static_evidence", {})
    test_results = outcome.get("test_results", []) if outcome else []
    test_counts = _counts(result.get("outcome") for result in test_results)
    run_status = outcome.get("run_status") if outcome else "missing"
    summary_status = "complete" if run_status in {"completed", "error", "timeout"} else "incomplete"
    return {
        "cohort_id": "EVP-7",
        "candidate_id": candidate_id,
        "task_id": model_visible.get("task_id"),
        "project": model_visible.get("project"),
        "summary_status": summary_status,
        "visible_tool_summary": {
            "patch_applies": static_evidence.get("patch_applies"),
            "syntax_import_check": static_evidence.get("syntax_import_check"),
            "static_analysis": static_evidence.get("static_analysis"),
            "visible_test_run_status": run_status,
            "visible_test_outcome_counts": test_counts,
        },
        "evidence_sources": {
            "static_packet_level": "E2",
            "visible_test_outcomes": "data/evidence/evp7_visible_test_outcomes.jsonl",
        },
    }


def build_summaries(packets_path: Path, visible_outcomes_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    packets = _packets_by_candidate(_read_jsonl(packets_path))
    outcomes = _outcomes_by_candidate(visible_outcomes_path)
    records = [
        _summary_record(candidate_id, level_packets, outcomes.get(candidate_id))
        for candidate_id, level_packets in sorted(packets.items())
    ]
    summary = {
        "cohort_id": "EVP-7",
        "record_count": len(records),
        "summary_status_counts": _counts(record["summary_status"] for record in records),
        "visible_test_run_status_counts": _counts(
            record["visible_tool_summary"]["visible_test_run_status"]
            for record in records
        ),
        "leakage_audit": "passed",
        "leakage_findings_count": 0,
    }
    findings = leakage_audit(records)
    summary["leakage_audit"] = "passed" if not findings else "failed"
    summary["leakage_findings_count"] = len(findings)
    return records, summary


def leakage_audit(records: list[dict[str, Any]]) -> list[str]:
    serialized = json.dumps(records, ensure_ascii=False)
    return [marker for marker in FORBIDDEN_MARKERS if marker in serialized]


def _check(records: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    if summary["record_count"] != 46:
        raise SystemExit(f"tool summary count changed: {summary['record_count']} != 46")
    if summary["leakage_audit"] != "passed":
        raise SystemExit("visible tool summary leakage audit failed")
    if summary["summary_status_counts"].get("complete") != 46:
        raise SystemExit("expected 46 complete visible tool summaries")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packets-in", type=Path, default=PACKETS_IN)
    parser.add_argument("--visible-outcomes-in", type=Path, default=VISIBLE_OUTCOMES_IN)
    parser.add_argument("--summaries-out", type=Path, default=SUMMARIES_OUT)
    parser.add_argument("--summary-out", type=Path, default=SUMMARY_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    records, summary = build_summaries(args.packets_in, args.visible_outcomes_in)
    _write_jsonl(args.summaries_out, records)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.check:
        _check(records, summary)

    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
