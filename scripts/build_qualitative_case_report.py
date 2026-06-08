from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


CASE_CANDIDATE_IDS = [
    "candidate_0005",
    "candidate_0001",
    "candidate_0023",
    "candidate_0006",
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            value = json.loads(stripped)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number} is not a JSON object")
            records.append(value)
    return records


def write_json(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def by_key(records: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        value = str(record.get(key, ""))
        if value:
            result[value] = record
    return result


def index_reviews(records: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    indexed: dict[tuple[str, str], dict[str, Any]] = {}
    for record in records:
        key = (str(record.get("model_candidate_id") or ""), str(record.get("condition") or ""))
        if key[0] and key[1]:
            indexed[key] = record
    return indexed


def short(value: Any, max_chars: int = 900) -> str:
    text = str(value or "").replace("\r\n", "\n").strip()
    if len(text) <= max_chars:
        return "\n".join(line.rstrip() for line in text.splitlines())
    truncated = text[: max_chars - 18].rstrip() + "\n...[truncated]"
    return "\n".join(line.rstrip() for line in truncated.splitlines())


def decision_line(review: dict[str, Any] | None) -> str:
    if not review:
        return "missing"
    return f"{review.get('decision')} (confidence={review.get('confidence')}, verifier={review.get('verifier_id')})"


def build_cases(
    candidates: list[dict[str, Any]],
    prompt_reviews: list[dict[str, Any]],
    tool_augmented_reviews: list[dict[str, Any]],
    tool_only_reviews: list[dict[str, Any]],
) -> dict[str, Any]:
    candidates_by_model_id = by_key(candidates, "model_candidate_id")
    prompt_index = index_reviews(prompt_reviews)
    tool_aug_index = index_reviews(tool_augmented_reviews)
    tool_only_index = index_reviews(tool_only_reviews)
    case_records: list[dict[str, Any]] = []
    for candidate_id in CASE_CANDIDATE_IDS:
        candidate = candidates_by_model_id[candidate_id]
        case_records.append(
            {
                "model_candidate_id": candidate_id,
                "patch_id": candidate["patch_id"],
                "task_id": candidate["task_id"],
                "project": candidate["project"],
                "candidate_type": candidate["candidate_type"],
                "expected_outcome": candidate["expected_outcome"],
                "issue_summary": candidate["issue_summary"],
                "visible_tests": candidate.get("visible_tests", []),
                "patch_excerpt": short(candidate.get("patch_text"), 1200),
                "decisions": {
                    "llm_only": prompt_index.get((candidate_id, "llm_only")),
                    "evidence_first": prompt_index.get((candidate_id, "evidence_first")),
                    "tool_only_apply_only": tool_only_index.get((candidate_id, "no_api_tool_only_apply_only")),
                    "tool_only_validation_summary": tool_only_index.get(
                        (candidate_id, "no_api_tool_only_validation_summary")
                    ),
                    "tool_augmented_evidence": tool_aug_index.get((candidate_id, "tool_augmented_evidence")),
                },
            }
        )
    return {
        "case_count": len(case_records),
        "case_candidate_ids": CASE_CANDIDATE_IDS,
        "boundary": (
            "Cases are selected from existing audited pilot outputs. The tool-only validation-summary "
            "condition uses retained executable validation and is not a hidden-evaluator-free final baseline."
        ),
        "cases": case_records,
    }


def build_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Qualitative Case Report",
        "",
        "## Boundary",
        "",
        summary["boundary"],
        "",
        "These cases are for middle-report explanation and paper diagnosis. They should not be quoted as final expanded-study evidence before raw responses, visible/hidden evidence separation, and oracle labels are manually checked.",
        "",
    ]
    for case in summary["cases"]:
        decisions = case["decisions"]
        lines.extend(
            [
                f"## `{case['model_candidate_id']}` / `{case['patch_id']}`",
                "",
                f"- task: `{case['task_id']}` / `{case['project']}`",
                f"- candidate type: `{case['candidate_type']}`",
                f"- evaluator outcome: `{case['expected_outcome']}`",
                f"- issue: {case['issue_summary']}",
                f"- visible tests: `{case['visible_tests']}`",
                "",
                "| condition | decision |",
                "| --- | --- |",
                f"| LLM-only | {decision_line(decisions.get('llm_only'))} |",
                f"| Evidence-first | {decision_line(decisions.get('evidence_first'))} |",
                f"| Tool-only apply-only | {decision_line(decisions.get('tool_only_apply_only'))} |",
                f"| Tool-only validation-summary | {decision_line(decisions.get('tool_only_validation_summary'))} |",
                f"| Tool-augmented evidence | {decision_line(decisions.get('tool_augmented_evidence'))} |",
                "",
                "Patch excerpt:",
                "",
                "```diff",
                case["patch_excerpt"],
                "```",
                "",
            ]
        )
    return "\n".join(line.rstrip() for line in lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a tracked qualitative case report from existing pilot outputs.")
    parser.add_argument("--candidates", default="outputs/patch_verification_pilot_001/candidates.jsonl")
    parser.add_argument("--prompt-reviews", default="outputs/patch_verification_api_pilot_002/reviews.jsonl")
    parser.add_argument("--tool-augmented-reviews", default="outputs/patch_verification_tool_augmented_full_001/reviews.jsonl")
    parser.add_argument("--tool-only-reviews", default="outputs/tool_only_baseline/tool_only_verifier_outputs.jsonl")
    parser.add_argument("--out-json", default="outputs/qualitative_cases/qualitative_cases.json")
    parser.add_argument("--out-md", default="docs/experiments/qualitative_case_report.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = build_cases(
        candidates=read_jsonl(Path(args.candidates)),
        prompt_reviews=read_jsonl(Path(args.prompt_reviews)),
        tool_augmented_reviews=read_jsonl(Path(args.tool_augmented_reviews)),
        tool_only_reviews=read_jsonl(Path(args.tool_only_reviews)),
    )
    write_json(Path(args.out_json), summary)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(summary), encoding="utf-8")
    print(json.dumps({"case_count": summary["case_count"], "out_md": args.out_md}, indent=2))


if __name__ == "__main__":
    main()
