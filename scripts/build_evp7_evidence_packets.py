"""Build leakage-audited EVP-7 evidence packet records.

The packets are model-visible inputs for verifier runs. They intentionally do
not copy evaluator-only labels, retained-oracle outcomes, hidden oracle paths,
or candidate construction taxonomy from the candidate manifest.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CANDIDATES_IN = REPO_ROOT / "data" / "patches" / "evp7_candidates.jsonl"
VISIBLE_OUTCOMES_IN = REPO_ROOT / "data" / "evidence" / "evp7_visible_test_outcomes.jsonl"
TOOL_SUMMARIES_IN = REPO_ROOT / "data" / "evidence" / "evp7_visible_tool_summaries.jsonl"
PACKETS_OUT = REPO_ROOT / "data" / "evidence" / "evp7_evidence_packets.jsonl"
SUMMARY_OUT = REPO_ROOT / "data" / "evidence" / "evp7_evidence_packet_summary.json"

EVIDENCE_LEVELS = ("E0", "E2", "E4", "E6")
EVIDENCE_LEVEL_NAMES = {
    "E0": "issue_and_patch",
    "E2": "issue_patch_static",
    "E4": "visible_tests",
    "E6": "visible_tool_summary",
}

FORBIDDEN_KEYS = {
    "candidate_type",
    "expected_outcome",
    "failure_type_label",
    "hidden_oracles",
    "label_retained_oracle",
    "label_with_p2p_broad",
    "patch_id",
    "patch_materialization",
    "patch_source_label",
    "source_model_candidate_id",
    "validation_summary",
}
FORBIDDEN_VALUE_MARKERS = (
    "correct_under_f2p_and_p2p_broad",
    "incorrect_issue_not_fixed",
    "correct_reference",
    "partial_fix",
    "irrelevant_patch",
    "buggy_noop",
    "retained_oracle",
    "hidden_oracle",
    "label_with_p2p_broad",
    "label_retained_oracle",
    "failure_type_label",
)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )


def _candidate_seed(candidate: dict[str, Any]) -> dict[str, Any]:
    seed = candidate.get("model_visible_seed") or {}
    return {
        "candidate_id": candidate["evp7_candidate_id"],
        "project": seed.get("project") or candidate.get("project"),
        "task_id": seed.get("task_id") or candidate.get("task_id"),
        "issue_summary": seed.get("issue_summary") or candidate.get("issue_summary"),
        "touched_files": seed.get("touched_files") or candidate.get("touched_files", []),
        "patch_diff": seed.get("patch_text") or candidate.get("patch_text", ""),
    }


def _static_evidence(candidate: dict[str, Any]) -> dict[str, Any]:
    validation_summary = candidate.get("validation_summary") or {}
    return {
        "patch_applies": validation_summary.get("patch_applied"),
        "syntax_import_check": "not_run",
        "static_analysis": "not_run",
        "source": "candidate_validation_patch_apply_only",
    }


def _visible_tests(candidate: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "test_name": test_name,
            "outcome": "not_included_missing_visible_outcome_source",
        }
        for test_name in candidate.get("visible_tests", [])
    ]


def _has_visible_outcomes(visible_outcome: dict[str, Any] | None) -> bool:
    if not visible_outcome:
        return False
    if visible_outcome.get("run_status") not in {"completed", "error", "timeout"}:
        return False
    outcomes = [result.get("outcome") for result in visible_outcome.get("test_results", [])]
    return bool(outcomes) and all(outcome not in {"planned", "not_run_blocked"} for outcome in outcomes)


def _has_tool_summary(tool_summary: dict[str, Any] | None) -> bool:
    return bool(tool_summary) and tool_summary.get("summary_status") == "complete"


def _completeness(
    level: str,
    candidate: dict[str, Any],
    visible_outcome: dict[str, Any] | None,
    tool_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    seed = _candidate_seed(candidate)
    missing = []
    if not seed["issue_summary"]:
        missing.append("issue_summary")
    if not seed["patch_diff"]:
        missing.append("patch_diff")
    if level in {"E4", "E6"} and not _has_visible_outcomes(visible_outcome):
        missing.append("independent_visible_test_outcomes")
    if level == "E6" and not _has_tool_summary(tool_summary):
        missing.append("realistic_visible_tool_summary")
    return {
        "status": "complete" if not missing else "incomplete",
        "missing": missing,
    }


def _visible_test_evidence(candidate: dict[str, Any], visible_outcome: dict[str, Any] | None) -> dict[str, Any]:
    if not _has_visible_outcomes(visible_outcome):
        return {
            "status": "incomplete_missing_independent_visible_outcomes",
            "test_results": _visible_tests(candidate),
        }
    return {
        "status": "complete",
        "run_status": visible_outcome.get("run_status"),
        "test_results": [
            {
                "test_name": result.get("test_name"),
                "outcome": result.get("outcome"),
            }
            for result in visible_outcome.get("test_results", [])
        ],
    }


def _tool_evidence(tool_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not _has_tool_summary(tool_summary):
        return {
            "status": "not_generated_or_incomplete",
            "summary": None,
        }
    return {
        "status": "complete",
        "summary": tool_summary.get("visible_tool_summary"),
    }


def _packet(
    candidate: dict[str, Any],
    level: str,
    visible_outcome: dict[str, Any] | None,
    tool_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    seed = _candidate_seed(candidate)
    packet: dict[str, Any] = {
        "evidence_packet_id": f"{candidate['evp7_candidate_id']}__{level}",
        "cohort_id": "EVP-7",
        "evidence_level": level,
        "evidence_level_name": EVIDENCE_LEVEL_NAMES[level],
        "model_visible": seed,
        "packet_completeness": _completeness(level, candidate, visible_outcome, tool_summary),
        "label_leakage_guard": (
            "no evaluator labels, retained-oracle outcome, hidden tests, "
            "reference provenance, or failure taxonomy included"
        ),
    }
    if level in {"E2", "E4", "E6"}:
        packet["visible_static_evidence"] = _static_evidence(candidate)
    if level in {"E4", "E6"}:
        packet["visible_test_evidence"] = _visible_test_evidence(candidate, visible_outcome)
    if level == "E6":
        packet["visible_tool_evidence"] = _tool_evidence(tool_summary)
    return packet


def _visible_outcomes_by_candidate(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    return {record["candidate_id"]: record for record in _read_jsonl(path)}


def _tool_summaries_by_candidate(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    return {record["candidate_id"]: record for record in _read_jsonl(path)}


def _counts(values: Any) -> dict[str, int]:
    result: dict[str, int] = {}
    for value in values:
        key = str(value)
        result[key] = result.get(key, 0) + 1
    return dict(sorted(result.items()))


def build_packets(
    candidates_path: Path,
    visible_outcomes_path: Path,
    tool_summaries_path: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    candidates = _read_jsonl(candidates_path)
    visible_outcomes = _visible_outcomes_by_candidate(visible_outcomes_path)
    tool_summaries = _tool_summaries_by_candidate(tool_summaries_path)
    visible_outcome_status_counts = _counts(record.get("run_status", "missing") for record in visible_outcomes.values())
    tool_summary_status_counts = _counts(record.get("summary_status", "missing") for record in tool_summaries.values())
    packets = [
        _packet(
            candidate,
            level,
            visible_outcomes.get(candidate["evp7_candidate_id"]),
            tool_summaries.get(candidate["evp7_candidate_id"]),
        )
        for candidate in candidates
        for level in EVIDENCE_LEVELS
    ]
    summary = {
        "cohort_id": "EVP-7",
        "candidate_count": len(candidates),
        "packet_count": len(packets),
        "evidence_levels": list(EVIDENCE_LEVELS),
        "packet_counts_by_level": {
            level: sum(1 for packet in packets if packet["evidence_level"] == level)
            for level in EVIDENCE_LEVELS
        },
        "complete_packet_counts_by_level": {
            level: sum(
                1
                for packet in packets
                if packet["evidence_level"] == level
                and packet["packet_completeness"]["status"] == "complete"
            )
            for level in EVIDENCE_LEVELS
        },
        "g1_packet_completeness": "pending",
        "g1_blocker": None,
        "g2_leakage_audit": "pending",
        "visible_outcome_source": str(visible_outcomes_path.relative_to(REPO_ROOT)) if visible_outcomes else None,
        "visible_outcome_status_counts": visible_outcome_status_counts,
        "visible_tool_summary_source": str(tool_summaries_path.relative_to(REPO_ROOT)) if tool_summaries else None,
        "visible_tool_summary_status_counts": tool_summary_status_counts,
        "next_step": "Run tool-only baselines and merge-gate schema dry-run before any real LLM API calls.",
    }
    leakage_findings = leakage_audit(packets)
    summary["g2_leakage_audit"] = "passed" if not leakage_findings else "failed"
    summary["leakage_findings_count"] = len(leakage_findings)
    all_complete = all(
        summary["complete_packet_counts_by_level"].get(level) == len(candidates)
        for level in EVIDENCE_LEVELS
    )
    summary["g1_packet_completeness"] = "passed" if all_complete else "not_passed"
    if not all_complete:
        summary["g1_blocker"] = "At least one evidence level has incomplete packet records."
    return packets, summary


def _walk(value: Any, path: str = "") -> list[tuple[str, Any]]:
    if isinstance(value, dict):
        items: list[tuple[str, Any]] = []
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            items.append((child_path, key))
            items.extend(_walk(child, child_path))
        return items
    if isinstance(value, list):
        items = []
        for index, child in enumerate(value):
            items.extend(_walk(child, f"{path}[{index}]"))
        return items
    return [(path, value)]


def leakage_audit(packets: list[dict[str, Any]]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for packet in packets:
        packet_id = packet["evidence_packet_id"]
        for path, value in _walk(packet):
            if isinstance(value, str):
                if path.split(".")[-1] in FORBIDDEN_KEYS:
                    findings.append({"packet_id": packet_id, "path": path, "reason": "forbidden_key"})
                lowered = value.lower()
                for marker in FORBIDDEN_VALUE_MARKERS:
                    if marker in lowered:
                        findings.append(
                            {
                                "packet_id": packet_id,
                                "path": path,
                                "reason": f"forbidden_marker:{marker}",
                            }
                        )
            elif isinstance(value, str) and value in FORBIDDEN_KEYS:
                findings.append({"packet_id": packet_id, "path": path, "reason": "forbidden_key"})
    return findings


def _check_packets(packets: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    if summary["candidate_count"] != 50:
        raise SystemExit(f"EVP-7 candidate count changed: {summary['candidate_count']} != 50")
    expected_packets = summary["candidate_count"] * len(EVIDENCE_LEVELS)
    if summary["packet_count"] != expected_packets:
        raise SystemExit(f"packet count {summary['packet_count']} != {expected_packets}")
    by_candidate: dict[str, set[str]] = {}
    for packet in packets:
        candidate_id = packet["model_visible"]["candidate_id"]
        by_candidate.setdefault(candidate_id, set()).add(packet["evidence_level"])
    missing = {
        candidate_id: sorted(set(EVIDENCE_LEVELS) - levels)
        for candidate_id, levels in by_candidate.items()
        if set(EVIDENCE_LEVELS) != levels
    }
    if missing:
        raise SystemExit(f"missing evidence levels: {missing}")
    findings = leakage_audit(packets)
    if findings:
        raise SystemExit(f"leakage audit failed: {findings[:5]}")
    if summary["complete_packet_counts_by_level"]["E0"] != 50:
        raise SystemExit("E0 packet completeness should cover all 50 candidates")
    expected_e4_complete = summary.get("visible_outcome_status_counts", {}).get("completed", 0)
    expected_e4_complete += summary.get("visible_outcome_status_counts", {}).get("error", 0)
    expected_e4_complete += summary.get("visible_outcome_status_counts", {}).get("timeout", 0)
    if summary["complete_packet_counts_by_level"]["E4"] != expected_e4_complete:
        raise SystemExit("E4 packet completeness must match complete visible outcome count")
    expected_e6_complete = summary.get("visible_tool_summary_status_counts", {}).get("complete", 0)
    if summary["complete_packet_counts_by_level"]["E6"] != expected_e6_complete:
        raise SystemExit("E6 packet completeness must match complete visible tool summary count")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates-in", type=Path, default=CANDIDATES_IN)
    parser.add_argument("--visible-outcomes-in", type=Path, default=VISIBLE_OUTCOMES_IN)
    parser.add_argument("--tool-summaries-in", type=Path, default=TOOL_SUMMARIES_IN)
    parser.add_argument("--packets-out", type=Path, default=PACKETS_OUT)
    parser.add_argument("--summary-out", type=Path, default=SUMMARY_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    packets, summary = build_packets(args.candidates_in, args.visible_outcomes_in, args.tool_summaries_in)
    _write_jsonl(args.packets_out, packets)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.check:
        _check_packets(packets, summary)

    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
