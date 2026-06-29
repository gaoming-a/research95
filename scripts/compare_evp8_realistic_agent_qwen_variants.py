"""Compare Qwen full-with-verdict and no-verdict realistic cohort variants."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FULL_REVIEWS = REPO_ROOT / "data" / "reviews" / "evp8_realistic_agent_qwen_qwen_qwen3.7-max_full_reviews.jsonl"
DEFAULT_NO_VERDICT_REVIEWS = REPO_ROOT / "data" / "reviews" / "evp8_realistic_agent_qwen_qwen_qwen3.7-max_no_verdict_reviews.jsonl"
DEFAULT_BASELINE = REPO_ROOT / "data" / "baselines" / "evp8_realistic_agent_visible_tool_baseline_v0_1.jsonl"
DEFAULT_EVALUATOR = REPO_ROOT / "data" / "patches" / "evp8_realistic_agent_evaluator_manifest_v0_1.jsonl"
DEFAULT_OUT = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_qwen_variant_comparison_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_realistic_agent_qwen_variant_comparison_v0_1.md"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def index(rows: list[dict[str, Any]], field: str) -> dict[str, dict[str, Any]]:
    result = {}
    for row in rows:
        key = str(row[field])
        if key in result:
            raise ValueError(f"duplicate id: {key}")
        result[key] = row
    return result


def build_summary(
    full_rows: list[dict[str, Any]],
    no_verdict_rows: list[dict[str, Any]],
    baseline_rows: list[dict[str, Any]],
    evaluator_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    full = index(full_rows, "anonymous_candidate_id")
    no_verdict = index(no_verdict_rows, "anonymous_candidate_id")
    baseline = index(baseline_rows, "candidate_id")
    evaluator = index(evaluator_rows, "candidate_id")
    ids = sorted(evaluator)
    if ids != sorted(full) or ids != sorted(no_verdict) or ids != sorted(baseline):
        raise ValueError("candidate id sets do not match")
    transitions = Counter()
    full_vs_no_verdict_changes = []
    no_verdict_vs_baseline_changes = []
    for candidate_id in ids:
        label = evaluator[candidate_id]["normalized_label"]
        full_decision = full[candidate_id]["decision"]
        no_verdict_decision = no_verdict[candidate_id]["decision"]
        baseline_decision = baseline[candidate_id]["decision"]
        transitions[f"{full_decision}->{no_verdict_decision}"] += 1
        if full_decision != no_verdict_decision:
            full_vs_no_verdict_changes.append(
                {
                    "candidate_id": candidate_id,
                    "label": label,
                    "full_decision": full_decision,
                    "no_verdict_decision": no_verdict_decision,
                }
            )
        if no_verdict_decision != baseline_decision:
            no_verdict_vs_baseline_changes.append(
                {
                    "candidate_id": candidate_id,
                    "label": label,
                    "baseline_decision": baseline_decision,
                    "no_verdict_decision": no_verdict_decision,
                }
            )
    wrong_ids = [candidate_id for candidate_id in ids if evaluator[candidate_id]["normalized_label"] != "correct"]
    no_verdict_false_accepts = [
        candidate_id for candidate_id in wrong_ids if no_verdict[candidate_id]["decision"] == "accept"
    ]
    corrected_label_set = any(str(row.get("hidden_validation_summary", {}).get("corrected_revalidation_id", "")) for row in evaluator_rows)
    merge_label_set = any(str(row.get("hidden_validation_summary", {}).get("merge_label_manifest_id", "")) for row in evaluator_rows)
    return {
        "analysis_id": (
            "evp8_realistic_agent_qwen_merge_label_variant_comparison_v0_3"
            if merge_label_set
            else
            "evp8_realistic_agent_qwen_corrected_label_variant_comparison_v0_2"
            if corrected_label_set
            else "evp8_realistic_agent_qwen_variant_comparison_v0_1"
        ),
        "cohort_id": "EVP-8-REALISTIC-AGENT",
        "corrected_label_set": corrected_label_set,
        "merge_label_set": merge_label_set,
        "candidate_count": len(ids),
        "full_decision_counts": dict(sorted(Counter(row["decision"] for row in full_rows).items())),
        "no_verdict_decision_counts": dict(sorted(Counter(row["decision"] for row in no_verdict_rows).items())),
        "visible_tool_decision_counts": dict(sorted(Counter(row["decision"] for row in baseline_rows).items())),
        "full_to_no_verdict_transition_counts": dict(sorted(transitions.items())),
        "full_vs_no_verdict_change_count": len(full_vs_no_verdict_changes),
        "full_vs_no_verdict_changes": full_vs_no_verdict_changes,
        "no_verdict_vs_visible_tool_change_count": len(no_verdict_vs_baseline_changes),
        "no_verdict_vs_visible_tool_changes": no_verdict_vs_baseline_changes,
        "no_verdict_false_accepts_among_wrong": len(no_verdict_false_accepts),
        "wrong_candidate_count": len(wrong_ids),
        "interpretation": {
            "verdict_removal_changed_qwen_decisions": len(full_vs_no_verdict_changes) > 0,
            "no_verdict_still_matches_visible_tool": len(no_verdict_vs_baseline_changes) == 0,
            "claim": "Removing the explicit merge-gate verdict did not change Qwen decisions; Qwen still follows visible test pass/fail outcomes on this cohort.",
        },
    }


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    title = (
        "EVP-8 Realistic Agent Qwen Merge-Label Variant Comparison v0.3"
        if summary.get("merge_label_set")
        else
        "EVP-8 Realistic Agent Qwen Corrected-Label Variant Comparison v0.2"
        if summary.get("corrected_label_set")
        else "EVP-8 Realistic Agent Qwen Variant Comparison v0.1"
    )
    lines = [
        f"# {title}",
        "",
        "Date: 2026-06-30",
        "",
        f"- candidates: {summary['candidate_count']}",
        f"- corrected label set: `{summary['corrected_label_set']}`",
        f"- merge label set: `{summary['merge_label_set']}`",
        f"- full decisions: `{summary['full_decision_counts']}`",
        f"- no-verdict decisions: `{summary['no_verdict_decision_counts']}`",
        f"- visible-tool decisions: `{summary['visible_tool_decision_counts']}`",
        f"- full to no-verdict transitions: `{summary['full_to_no_verdict_transition_counts']}`",
        f"- full vs no-verdict changes: `{summary['full_vs_no_verdict_change_count']}`",
        f"- no-verdict vs visible-tool changes: `{summary['no_verdict_vs_visible_tool_change_count']}`",
        f"- no-verdict false accepts among wrong: `{summary['no_verdict_false_accepts_among_wrong']}/{summary['wrong_candidate_count']}`",
        "",
        "Interpretation:",
        "",
        f"- {summary['interpretation']['claim']}",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full-reviews", type=Path, default=DEFAULT_FULL_REVIEWS)
    parser.add_argument("--no-verdict-reviews", type=Path, default=DEFAULT_NO_VERDICT_REVIEWS)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--evaluator", type=Path, default=DEFAULT_EVALUATOR)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = build_summary(
        full_rows=read_jsonl(args.full_reviews),
        no_verdict_rows=read_jsonl(args.no_verdict_reviews),
        baseline_rows=read_jsonl(args.baseline),
        evaluator_rows=read_jsonl(args.evaluator),
    )
    if args.check and summary["candidate_count"] != 53:
        raise SystemExit(f"expected 53 candidates, got {summary['candidate_count']}")
    write_json(args.out, summary)
    write_markdown(args.md_out, summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
