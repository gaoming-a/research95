from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REVIEWS = REPO_ROOT / "outputs" / "evp7_g5_llm_376_full_001" / "reviews.jsonl"
DEFAULT_CANDIDATES = REPO_ROOT / "data" / "patches" / "evp7_candidates.jsonl"
DEFAULT_TOOL_DECISIONS = REPO_ROOT / "data" / "baselines" / "evp7_tool_only_decisions.jsonl"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "reviews" / "evp7_g5_376_qualitative_cases.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp7_g5_376_qualitative_cases.md"

EVIDENCE_LEVELS = ("E0", "E2", "E4", "E6")
CORRECT_LABEL = "correct_under_f2p_and_p2p_broad"
RAW_FIELD_MARKERS = ("raw_" + "response_text", "prompt_" + "text")

CASE_SPECS = [
    {
        "case_id": "QC1",
        "candidate_id": "evp7_candidate_0007",
        "role": "evidence_enabled_accept",
        "expected_sequence": ["escalate", "escalate", "accept", "accept"],
        "interpretation": (
            "Visible test evidence changed a cautious model-visible sequence into an accept decision. "
            "This case illustrates the intended value of evidence visibility when the evaluator-only label "
            "marks the patch as correct."
        ),
    },
    {
        "case_id": "QC2",
        "candidate_id": "evp7_candidate_0078",
        "role": "tool_false_accept_recovered_by_llm",
        "expected_sequence": ["escalate", "reject", "escalate", "reject"],
        "interpretation": (
            "The deterministic visible-test and visible-tool-summary baselines accepted this partial patch, "
            "whereas the LLM did not accept it at E4 or E6. This is one of the recovered tool-only false accepts."
        ),
    },
    {
        "case_id": "QC3",
        "candidate_id": "evp7_candidate_0001",
        "role": "correct_patch_downgraded_by_llm",
        "expected_sequence": ["escalate", "escalate", "escalate", "escalate"],
        "interpretation": (
            "The tool-only baselines accepted this correct reference patch at E4 and E6, but the LLM kept "
            "escalating. This case shows the recall cost behind the safety-oriented interpretation."
        ),
    },
    {
        "case_id": "QC4",
        "candidate_id": "evp7_candidate_0051",
        "role": "tool_summary_late_accept",
        "expected_sequence": ["reject", "escalate", "escalate", "accept"],
        "interpretation": (
            "The model rejected or escalated before the full visible tool summary, then accepted at E6. "
            "This case illustrates that the strongest evidence level can recover some correct-patch recall."
        ),
    },
    {
        "case_id": "QC5",
        "candidate_id": "evp7_candidate_0031",
        "role": "no_op_rejected_after_evidence",
        "expected_sequence": ["escalate", "escalate", "reject", "reject"],
        "interpretation": (
            "A no-op control moved from escalation to rejection once visible test evidence was available. "
            "This supports the paper's merge-gate framing for non-fixing patches."
        ),
    },
    {
        "case_id": "QC6",
        "candidate_id": "evp7_candidate_0005",
        "role": "partial_patch_rejected_after_evidence",
        "expected_sequence": ["escalate", "escalate", "reject", "reject"],
        "interpretation": (
            "A partial patch remained non-accepted after visible evidence was added. This case represents "
            "the common E4/E6 reject path rather than the smaller set of tool-only false accepts."
        ),
    },
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def analyze(reviews_path: Path, candidates_path: Path, tool_decisions_path: Path) -> dict[str, Any]:
    candidates = {record["evp7_candidate_id"]: record for record in read_jsonl(candidates_path)}
    reviews = load_reviews_by_candidate(reviews_path)
    tool_decisions = load_tool_decisions(tool_decisions_path)
    cases = [
        build_case(spec, candidates, reviews, tool_decisions)
        for spec in CASE_SPECS
    ]
    role_counts = {case["role"]: 1 for case in cases}
    analysis = {
        "analysis_id": "evp7_g5_376_qualitative_cases",
        "boundary": (
            "This artifact selects representative EVP-7 decision cases from existing parse-valid review records. "
            "It writes only structured decision sequences, model-visible evidence categories, deterministic "
            "tool-only decisions, and separated evaluator-only interpretations. It does not include raw responses, "
            "prompt text, or reviewer-facing truth labels."
        ),
        "inputs": {
            "llm_reviews": repo_relative(reviews_path),
            "candidates": repo_relative(candidates_path),
            "tool_only_decisions": repo_relative(tool_decisions_path),
        },
        "case_count": len(cases),
        "case_roles": [case["role"] for case in cases],
        "role_counts": role_counts,
        "cases": cases,
    }
    analysis["raw_output_free_check"] = {
        "passed": not contains_raw_markers(analysis),
        "checked_for_raw_response_fields": True,
        "reviewer_facing_truth_label_separated": all(
            "evaluator_outcome" not in json.dumps(case["model_visible"], sort_keys=True)
            and "patch_source_label" not in json.dumps(case["model_visible"], sort_keys=True)
            for case in cases
        ),
    }
    if not analysis["raw_output_free_check"]["passed"]:
        raise SystemExit("qualitative-case output contains raw-output field markers")
    if not analysis["raw_output_free_check"]["reviewer_facing_truth_label_separated"]:
        raise SystemExit("qualitative-case model-visible section contains evaluator-only labels")
    return analysis


def load_reviews_by_candidate(path: Path) -> dict[str, dict[str, dict[str, Any]]]:
    reviews: dict[str, dict[str, dict[str, Any]]] = {}
    for record in read_jsonl(path):
        if record.get("parse_status") != "valid":
            raise SystemExit(f"invalid review record in qualitative source: {record.get('review_id')}")
        parsed = record.get("parsed_output")
        if not isinstance(parsed, dict):
            raise SystemExit(f"missing parsed output in review record: {record.get('review_id')}")
        candidate_id = str(record["candidate_id"])
        level = str(record["evidence_level"])
        reviews.setdefault(candidate_id, {})[level] = {
            "decision": parsed.get("decision"),
            "confidence": parsed.get("confidence"),
            "evidence_used": parsed.get("evidence_used", []),
            "human_review_needed": parsed.get("human_review_needed"),
            "risk_flags": parsed.get("risk_flags", []),
            "suspected_failure_type": parsed.get("suspected_failure_type"),
        }
    return reviews


def load_tool_decisions(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    decisions: dict[tuple[str, str], dict[str, Any]] = {}
    for record in read_jsonl(path):
        if record.get("evidence_level") in {"E4", "E6"}:
            decisions[(record["candidate_id"], record["evidence_level"])] = {
                "condition": record["condition"],
                "decision": record["decision"],
                "human_review_needed": record.get("human_review_needed"),
                "evidence_used": record.get("evidence_used", []),
            }
    return decisions


def build_case(
    spec: dict[str, Any],
    candidates: dict[str, dict[str, Any]],
    reviews: dict[str, dict[str, dict[str, Any]]],
    tool_decisions: dict[tuple[str, str], dict[str, Any]],
) -> dict[str, Any]:
    candidate_id = spec["candidate_id"]
    if candidate_id not in candidates:
        raise SystemExit(f"missing qualitative candidate: {candidate_id}")
    if candidate_id not in reviews:
        raise SystemExit(f"missing qualitative reviews: {candidate_id}")
    candidate = candidates[candidate_id]
    sequence = [str(reviews[candidate_id][level]["decision"]) for level in EVIDENCE_LEVELS]
    if sequence != spec["expected_sequence"]:
        raise SystemExit(f"{candidate_id} sequence changed: observed={sequence} expected={spec['expected_sequence']}")

    model_visible = {
        "candidate_id": candidate_id,
        "project": candidate["project"],
        "task_id": candidate["task_id"],
        "issue_summary": candidate["issue_summary"],
        "touched_files": candidate.get("touched_files", []),
        "patch_size": candidate.get("patch_size", {}),
        "visible_tests_count": len(candidate.get("visible_tests", [])),
        "decision_sequence": dict(zip(EVIDENCE_LEVELS, sequence)),
        "level_records": [
            {
                "evidence_level": level,
                **reviews[candidate_id][level],
            }
            for level in EVIDENCE_LEVELS
        ],
        "tool_only_decisions": {
            level: tool_decisions.get((candidate_id, level), {})
            for level in ("E4", "E6")
        },
    }
    evaluator_only = {
        "patch_source_label": candidate["patch_source_label"],
        "label_with_p2p_broad": candidate["label_with_p2p_broad"],
        "failure_type_label": candidate["failure_type_label"],
        "expected_outcome": candidate["expected_outcome"],
        "interpretation": spec["interpretation"],
    }
    validate_role(spec["role"], sequence, model_visible["tool_only_decisions"], evaluator_only)
    return {
        "case_id": spec["case_id"],
        "candidate_id": candidate_id,
        "role": spec["role"],
        "model_visible": model_visible,
        "evaluator_only_interpretation": evaluator_only,
    }


def validate_role(
    role: str,
    sequence: list[str],
    tool_by_level: dict[str, dict[str, Any]],
    evaluator_only: dict[str, Any],
) -> None:
    is_correct = evaluator_only["label_with_p2p_broad"] == CORRECT_LABEL
    e4_tool = (tool_by_level.get("E4") or {}).get("decision")
    e6_tool = (tool_by_level.get("E6") or {}).get("decision")
    if role == "evidence_enabled_accept" and not (is_correct and sequence[:2] == ["escalate", "escalate"] and sequence[2:] == ["accept", "accept"]):
        raise SystemExit("evidence_enabled_accept role validation failed")
    if role == "tool_false_accept_recovered_by_llm" and not (
        not is_correct and e4_tool == "accept" and e6_tool == "accept" and sequence[2] != "accept" and sequence[3] != "accept"
    ):
        raise SystemExit("tool_false_accept_recovered_by_llm role validation failed")
    if role == "correct_patch_downgraded_by_llm" and not (
        is_correct and e4_tool == "accept" and e6_tool == "accept" and sequence[2] != "accept" and sequence[3] != "accept"
    ):
        raise SystemExit("correct_patch_downgraded_by_llm role validation failed")
    if role == "tool_summary_late_accept" and not (is_correct and sequence[3] == "accept" and sequence[2] != "accept"):
        raise SystemExit("tool_summary_late_accept role validation failed")
    if role == "no_op_rejected_after_evidence" and not (
        evaluator_only["patch_source_label"] == "buggy_noop" and sequence[2:] == ["reject", "reject"]
    ):
        raise SystemExit("no_op_rejected_after_evidence role validation failed")
    if role == "partial_patch_rejected_after_evidence" and not (
        evaluator_only["patch_source_label"] == "partial_fix" and sequence[2:] == ["reject", "reject"]
    ):
        raise SystemExit("partial_patch_rejected_after_evidence role validation failed")


def contains_raw_markers(value: Any) -> bool:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return any(marker in text for marker in RAW_FIELD_MARKERS)


def build_markdown(analysis: dict[str, Any]) -> str:
    lines = [
        "# EVP-7 G5 Qualitative Decision Cases",
        "",
        analysis["boundary"],
        "",
        "## Summary",
        "",
        f"- case count: {analysis['case_count']}",
        f"- case roles: `{', '.join(analysis['case_roles'])}`",
        f"- raw-output-free check passed: {str(analysis['raw_output_free_check']['passed']).lower()}",
        f"- reviewer-facing truth labels separated: {str(analysis['raw_output_free_check']['reviewer_facing_truth_label_separated']).lower()}",
        "",
        "## Terminology Ledger",
        "",
        "| Canonical term | Meaning in this report | Boundary |",
        "|---|---|---|",
        "| model-visible sequence | The E0/E2/E4/E6 decisions and structured evidence categories visible in the review record | Does not include evaluator-only labels |",
        "| evaluator-only interpretation | The hidden label, patch source, and validation outcome used after review to interpret the case | Not part of the model-visible prompt |",
        "| tool-only decision | Deterministic E4/E6 baseline decision from visible tests or visible tool summaries | Used for attribution, not as an oracle |",
        "",
        "## Case Overview",
        "",
        "| case | candidate | role | project | task | E0 | E2 | E4 | E6 | evaluator-only outcome |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for case in analysis["cases"]:
        visible = case["model_visible"]
        evaluator = case["evaluator_only_interpretation"]
        seq = visible["decision_sequence"]
        lines.append(
            f"| {case['case_id']} | `{case['candidate_id']}` | `{case['role']}` | "
            f"{visible['project']} | `{visible['task_id']}` | {seq['E0']} | {seq['E2']} | "
            f"{seq['E4']} | {seq['E6']} | `{evaluator['label_with_p2p_broad']}` |"
        )
    lines.extend(["", "## Case Details", ""])
    for case in analysis["cases"]:
        visible = case["model_visible"]
        evaluator = case["evaluator_only_interpretation"]
        lines.extend(
            [
                f"### {case['case_id']} - {case['role']}",
                "",
                f"- candidate: `{case['candidate_id']}`",
                f"- project/task: {visible['project']} / `{visible['task_id']}`",
                f"- issue summary: {visible['issue_summary']}",
                f"- touched files: `{', '.join(visible['touched_files'])}`",
                f"- patch size: `{visible['patch_size']}`",
                f"- visible tests count: {visible['visible_tests_count']}",
                "",
                "| level | LLM decision | confidence | human review | risk flags | evidence used | tool-only decision |",
                "|---|---|---:|---|---|---|---|",
            ]
        )
        tool_by_level = visible["tool_only_decisions"]
        for level_record in visible["level_records"]:
            level = level_record["evidence_level"]
            tool_decision = (tool_by_level.get(level) or {}).get("decision", "--")
            lines.append(
                f"| {level} | {level_record['decision']} | {fmt(level_record['confidence'])} | "
                f"{str(level_record['human_review_needed']).lower()} | "
                f"`{', '.join(level_record['risk_flags'])}` | "
                f"`{', '.join(level_record['evidence_used'])}` | {tool_decision} |"
            )
        lines.extend(
            [
                "",
                "Evaluator-only interpretation:",
                "",
                f"- patch source label: `{evaluator['patch_source_label']}`",
                f"- outcome label: `{evaluator['label_with_p2p_broad']}`",
                f"- failure type: `{evaluator['failure_type_label']}`",
                f"- interpretation: {evaluator['interpretation']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Paper-Use Boundary",
            "",
            "- Use these cases to explain decision mechanics, not to make scale-generalized claims.",
            "- Keep the model-visible decision sequence separate from evaluator-only labels in prose.",
            "- The cases support the bounded interpretation that evidence visibility changes merge-gate behavior while preserving a safety/recall tradeoff.",
            "",
        ]
    )
    return "\n".join(lines)


def fmt(value: Any) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build raw-output-free EVP-7 qualitative decision cases.")
    parser.add_argument("--reviews", default=str(DEFAULT_REVIEWS))
    parser.add_argument("--candidates", default=str(DEFAULT_CANDIDATES))
    parser.add_argument("--tool-decisions", default=str(DEFAULT_TOOL_DECISIONS))
    parser.add_argument("--out-json", default=str(DEFAULT_JSON_OUT))
    parser.add_argument("--out-md", default=str(DEFAULT_MD_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    analysis = analyze(Path(args.reviews), Path(args.candidates), Path(args.tool_decisions))
    write_json(Path(args.out_json), analysis)
    write_text(Path(args.out_md), build_markdown(analysis))
    print(
        json.dumps(
            {
                "out_json": args.out_json,
                "out_md": args.out_md,
                "case_count": analysis["case_count"],
                "raw_output_free": analysis["raw_output_free_check"]["passed"],
                "reviewer_facing_truth_label_separated": analysis["raw_output_free_check"][
                    "reviewer_facing_truth_label_separated"
                ],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
