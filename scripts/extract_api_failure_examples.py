from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


CORRECT_OUTCOMES = {"correct"}
NEGATIVE_OUTCOMES = {"incorrect", "partial", "overfitted", "irrelevant_or_noop"}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number} must contain a JSON object")
        records.append(value)
    return records


def write_json(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def by_key(records: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for record in records:
        value = str(record[key])
        if value in indexed:
            raise ValueError(f"duplicate {key}: {value}")
        indexed[value] = record
    return indexed


def classify_review(candidate: dict[str, Any], review: dict[str, Any]) -> list[str]:
    outcome = str(candidate["expected_outcome"])
    decision = str(review["decision"])
    condition = str(review["condition"])
    buckets: list[str] = []

    if decision == "invalid_output":
        buckets.append("invalid_outputs")
    if outcome in NEGATIVE_OUTCOMES and decision == "accept":
        buckets.append("false_accepts")
        if condition == "llm_only":
            buckets.append("llm_only_false_accepts")
        if condition == "evidence_first":
            buckets.append("evidence_first_false_accepts")
    if outcome in CORRECT_OUTCOMES and decision == "reject":
        buckets.append("false_rejects")
    if outcome in CORRECT_OUTCOMES and decision in {"reject", "escalate"}:
        buckets.append("correct_patch_not_accepted")
    if condition == "evidence_first" and decision in {"reject", "escalate"}:
        buckets.append("evidence_first_reject_or_escalate")
    return buckets


def short_text(value: Any, max_chars: int) -> str:
    text = str(value or "").replace("\r\n", "\n").strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 15].rstrip() + "\n...[truncated]"


def summarize_claims(claims: Any, max_claims: int) -> list[dict[str, Any]]:
    if not isinstance(claims, list):
        return []
    summarized: list[dict[str, Any]] = []
    for claim in claims[:max_claims]:
        if not isinstance(claim, dict):
            continue
        summarized.append(
            {
                "claim": short_text(claim.get("claim", ""), 220),
                "evidence": claim.get("evidence", []),
                "evidence_status": claim.get("evidence_status", ""),
            }
        )
    return summarized


def make_example(
    bucket: str,
    review: dict[str, Any],
    candidate: dict[str, Any],
    evidence_packet: dict[str, Any] | None,
    max_patch_chars: int,
) -> dict[str, Any]:
    return {
        "bucket": bucket,
        "patch_id": candidate["patch_id"],
        "model_candidate_id": review.get("model_candidate_id") or candidate.get("model_candidate_id"),
        "task_id": candidate["task_id"],
        "project": candidate["project"],
        "candidate_type": candidate["candidate_type"],
        "expected_outcome": candidate["expected_outcome"],
        "condition": review["condition"],
        "decision": review["decision"],
        "confidence": review.get("confidence"),
        "model": review.get("model"),
        "prompt_version": review.get("prompt_version"),
        "mock_run": bool(review.get("mock_run")),
        "visible_tests": (evidence_packet or candidate).get("visible_tests", []),
        "task_summary": (evidence_packet or candidate).get("task_summary") or candidate.get("issue_summary"),
        "visible_context": short_text((evidence_packet or candidate).get("visible_context", ""), 700),
        "patch_excerpt": short_text((evidence_packet or candidate).get("patch_text", ""), max_patch_chars),
        "claims": summarize_claims(review.get("claims", []), max_claims=3),
        "invalid_reason": review.get("invalid_reason"),
    }


def collect_examples(
    candidates: list[dict[str, Any]],
    evidence_packets: list[dict[str, Any]],
    reviews: list[dict[str, Any]],
    limit_per_bucket: int,
    max_patch_chars: int,
) -> dict[str, Any]:
    candidates_by_patch_id = by_key(candidates, "patch_id")
    evidence_by_candidate_id = by_key(evidence_packets, "candidate_id")
    buckets: dict[str, list[dict[str, Any]]] = {}
    bucket_counts: Counter[str] = Counter()
    condition_counts = Counter(str(review.get("condition", "unknown")) for review in reviews)
    decision_counts = Counter(str(review.get("decision", "unknown")) for review in reviews)
    mock_count = sum(1 for review in reviews if review.get("mock_run"))

    for review in reviews:
        patch_id = str(review["patch_id"])
        if patch_id not in candidates_by_patch_id:
            raise ValueError(f"review references unknown patch_id: {patch_id}")
        candidate = candidates_by_patch_id[patch_id]
        evidence_packet = evidence_by_candidate_id.get(str(review.get("model_candidate_id", "")))
        for bucket in classify_review(candidate, review):
            bucket_counts[bucket] += 1
            examples = buckets.setdefault(bucket, [])
            if len(examples) < limit_per_bucket:
                examples.append(make_example(bucket, review, candidate, evidence_packet, max_patch_chars))

    return {
        "review_count": len(reviews),
        "mock_review_count": mock_count,
        "condition_counts": dict(sorted(condition_counts.items())),
        "decision_counts": dict(sorted(decision_counts.items())),
        "bucket_counts": dict(sorted(bucket_counts.items())),
        "examples": {key: value for key, value in sorted(buckets.items())},
    }


def markdown_example(example: dict[str, Any]) -> list[str]:
    claims = example.get("claims", [])
    lines = [
        f"### `{example['bucket']}`: `{example['patch_id']}`",
        "",
        f"- task: `{example['task_id']}` / `{example['project']}`",
        f"- anonymous candidate: `{example['model_candidate_id']}`",
        f"- candidate type: `{example['candidate_type']}`",
        f"- oracle label: `{example['expected_outcome']}`",
        f"- condition and decision: `{example['condition']}` -> `{example['decision']}`",
        f"- confidence: {example.get('confidence')}",
        f"- model: `{example.get('model')}`",
        f"- visible tests: `{example.get('visible_tests')}`",
        "",
        "Visible context:",
        "",
        "```text",
        example.get("visible_context", ""),
        "```",
        "",
        "Patch excerpt:",
        "",
        "```diff",
        example.get("patch_excerpt", ""),
        "```",
        "",
    ]
    if claims:
        lines.extend(["Claims:", ""])
        for index, claim in enumerate(claims, start=1):
            lines.append(
                f"{index}. {claim.get('claim', '')} "
                f"(status: `{claim.get('evidence_status', '')}`, evidence: `{claim.get('evidence', [])}`)"
            )
        lines.append("")
    if example.get("invalid_reason"):
        lines.extend(["Invalid reason:", "", f"`{example['invalid_reason']}`", ""])
    return lines


def build_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Patch Verification Failure Analysis Examples",
        "",
        "## Status",
        "",
        f"- reviewer records: {summary['review_count']}",
        f"- mock reviewer records: {summary['mock_review_count']}",
        f"- condition counts: `{summary['condition_counts']}`",
        f"- decision counts: `{summary['decision_counts']}`",
        f"- bucket counts: `{summary['bucket_counts']}`",
        "",
    ]
    if summary["mock_review_count"]:
        lines.extend(
            [
                "## Boundary",
                "",
                "This file was generated from mock reviewer outputs. It validates the failure-analysis extraction pipeline only and must not be used as paper evidence.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "## Boundary",
                "",
                "This file was generated from real reviewer outputs. Use it as a starting point for manual qualitative analysis; do not quote examples before checking raw responses and oracle labels.",
                "",
            ]
        )

    for bucket, examples in summary["examples"].items():
        lines.extend([f"## {bucket}", ""])
        for example in examples:
            lines.extend(markdown_example(example))
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract failure-analysis examples from API pilot reviews.")
    parser.add_argument("--candidates", required=True, help="Evaluator-facing patch candidates JSONL.")
    parser.add_argument("--evidence-packets", required=True, help="Model-visible evidence packets JSONL.")
    parser.add_argument("--reviews", required=True, help="API pilot reviews JSONL.")
    parser.add_argument("--out-json", required=True, help="Structured failure-analysis JSON output.")
    parser.add_argument("--out-md", required=True, help="Markdown failure-analysis report output.")
    parser.add_argument("--limit-per-bucket", type=int, default=3)
    parser.add_argument("--max-patch-chars", type=int, default=1600)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = collect_examples(
        candidates=read_jsonl(Path(args.candidates)),
        evidence_packets=read_jsonl(Path(args.evidence_packets)),
        reviews=read_jsonl(Path(args.reviews)),
        limit_per_bucket=args.limit_per_bucket,
        max_patch_chars=args.max_patch_chars,
    )
    write_json(Path(args.out_json), summary)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(summary), encoding="utf-8")
    print(
        json.dumps(
            {
                "out_json": args.out_json,
                "out_md": args.out_md,
                "review_count": summary["review_count"],
                "mock_review_count": summary["mock_review_count"],
                "bucket_counts": summary["bucket_counts"],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
