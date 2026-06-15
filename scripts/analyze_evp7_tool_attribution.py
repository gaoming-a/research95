from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REVIEWS = REPO_ROOT / "outputs" / "evp7_g5_llm_376_full_001" / "reviews.jsonl"
DEFAULT_TOOL_DECISIONS = REPO_ROOT / "data" / "baselines" / "evp7_tool_only_decisions.jsonl"
DEFAULT_CANDIDATES = REPO_ROOT / "data" / "patches" / "evp7_candidates.jsonl"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "reviews" / "evp7_g5_376_tool_attribution.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp7_g5_376_tool_attribution.md"

CORRECT_LABEL = "correct_under_f2p_and_p2p_broad"
COMPARISONS = {
    "E4": "tool_only_visible_tests",
    "E6": "tool_only_visible_tool_summary",
}
RAW_FIELD_MARKERS = ("raw_" + "response_text", "prompt_" + "text")


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


def load_candidates(path: Path) -> dict[str, dict[str, Any]]:
    candidates: dict[str, dict[str, Any]] = {}
    for record in read_jsonl(path):
        candidates[record["evp7_candidate_id"]] = {
            "is_correct": record["label_with_p2p_broad"] == CORRECT_LABEL,
            "patch_source_label": record["patch_source_label"],
            "project": record["project"],
        }
    return candidates


def load_llm_decisions(path: Path) -> dict[tuple[str, str], str]:
    decisions: dict[tuple[str, str], str] = {}
    for record in read_jsonl(path):
        parsed = record.get("parsed_output") if record.get("parse_status") == "valid" else {}
        decision = parsed.get("decision") if isinstance(parsed, dict) else None
        decisions[(record["candidate_id"], record["evidence_level"])] = str(decision or "invalid_output")
    return decisions


def load_tool_decisions(path: Path) -> dict[tuple[str, str], str]:
    decisions: dict[tuple[str, str], str] = {}
    for record in read_jsonl(path):
        if record["condition"] in COMPARISONS.values():
            decisions[(record["candidate_id"], record["evidence_level"])] = record["decision"]
    return decisions


def analyze(reviews_path: Path, tool_decisions_path: Path, candidates_path: Path) -> dict[str, Any]:
    candidates = load_candidates(candidates_path)
    llm_decisions = load_llm_decisions(reviews_path)
    tool_decisions = load_tool_decisions(tool_decisions_path)
    candidate_ids = sorted(candidates)
    check_matrix(candidate_ids, llm_decisions, tool_decisions)
    comparisons = {
        level: compare_level(level, tool_condition, candidate_ids, candidates, llm_decisions, tool_decisions)
        for level, tool_condition in COMPARISONS.items()
    }
    analysis = {
        "analysis_id": "evp7_g5_376_tool_attribution",
        "boundary": (
            "This artifact compares deterministic tool-only decisions with LLM decisions at matching "
            "EVP-7 evidence levels. It reads ignored review records structurally but writes only "
            "candidate-level decision aggregates and raw-output-free summaries. It does not support "
            "a claim that the LLM outperforms deterministic tool evidence."
        ),
        "inputs": {
            "llm_reviews": repo_relative(reviews_path),
            "tool_only_decisions": repo_relative(tool_decisions_path),
            "candidates": repo_relative(candidates_path),
        },
        "cohort": {
            "candidate_count": len(candidate_ids),
            "comparison_levels": list(COMPARISONS),
        },
        "comparisons": comparisons,
    }
    analysis["raw_output_free_check"] = {
        "passed": not contains_raw_markers(analysis),
        "checked_for_raw_response_fields": True,
    }
    if not analysis["raw_output_free_check"]["passed"]:
        raise SystemExit("tool-attribution output contains raw-output field markers")
    return analysis


def check_matrix(
    candidate_ids: list[str],
    llm_decisions: dict[tuple[str, str], str],
    tool_decisions: dict[tuple[str, str], str],
) -> None:
    expected = {(candidate_id, level) for candidate_id in candidate_ids for level in COMPARISONS}
    missing_llm = sorted(expected - set(llm_decisions))
    missing_tool = sorted(expected - set(tool_decisions))
    if missing_llm or missing_tool:
        raise SystemExit(
            "tool attribution matrix mismatch: "
            f"missing_llm={len(missing_llm)} missing_tool={len(missing_tool)}"
        )


def compare_level(
    level: str,
    tool_condition: str,
    candidate_ids: list[str],
    candidates: dict[str, dict[str, Any]],
    llm_decisions: dict[tuple[str, str], str],
    tool_decisions: dict[tuple[str, str], str],
) -> dict[str, Any]:
    decision_pairs: Counter[str] = Counter()
    counts: Counter[str] = Counter()
    patch_source_pairs: dict[str, Counter[str]] = {}

    for candidate_id in candidate_ids:
        candidate = candidates[candidate_id]
        is_correct = bool(candidate["is_correct"])
        tool_decision = tool_decisions[(candidate_id, level)]
        llm_decision = llm_decisions[(candidate_id, level)]
        pair_key = f"tool_{tool_decision}__llm_{llm_decision}"
        decision_pairs[pair_key] += 1
        patch_source = str(candidate["patch_source_label"])
        patch_source_pairs.setdefault(patch_source, Counter())[pair_key] += 1

        counts["agreement" if tool_decision == llm_decision else "disagreement"] += 1
        if tool_decision == "accept":
            counts["tool_accept"] += 1
        if llm_decision == "accept":
            counts["llm_accept"] += 1
        if llm_decision == "accept" and tool_decision != "accept":
            counts["llm_accept_not_tool_accept"] += 1
        if tool_decision == "accept" and not is_correct and llm_decision != "accept":
            counts["tool_false_accept_recovered_by_llm"] += 1
        if tool_decision == "accept" and not is_correct and llm_decision == "accept":
            counts["shared_false_accept"] += 1
        if tool_decision == "accept" and is_correct and llm_decision == "accept":
            counts["tool_true_accept_kept_by_llm"] += 1
        if tool_decision == "accept" and is_correct and llm_decision != "accept":
            counts["tool_true_accept_downgraded_by_llm"] += 1

    record_count = len(candidate_ids)
    false_accept_total = counts["tool_false_accept_recovered_by_llm"] + counts["shared_false_accept"]
    true_accept_total = counts["tool_true_accept_kept_by_llm"] + counts["tool_true_accept_downgraded_by_llm"]
    return {
        "evidence_level": level,
        "tool_condition": tool_condition,
        "record_count": record_count,
        "agreement_count": counts["agreement"],
        "agreement_rate": round(counts["agreement"] / record_count, 6),
        "disagreement_count": counts["disagreement"],
        "decision_pair_counts": dict(sorted(decision_pairs.items())),
        "label_interaction_counts": dict(sorted(counts.items())),
        "tool_false_accept_recovery": {
            "recovered": counts["tool_false_accept_recovered_by_llm"],
            "total_tool_false_accepts": false_accept_total,
            "rate": round(counts["tool_false_accept_recovered_by_llm"] / false_accept_total, 6)
            if false_accept_total
            else None,
        },
        "tool_true_accept_retention": {
            "kept": counts["tool_true_accept_kept_by_llm"],
            "downgraded": counts["tool_true_accept_downgraded_by_llm"],
            "total_tool_true_accepts": true_accept_total,
            "retention_rate": round(counts["tool_true_accept_kept_by_llm"] / true_accept_total, 6)
            if true_accept_total
            else None,
        },
        "llm_accept_subset_of_tool_accepts": counts["llm_accept_not_tool_accept"] == 0,
        "per_patch_source_pair_counts": {
            key: dict(sorted(counter.items())) for key, counter in sorted(patch_source_pairs.items())
        },
    }


def contains_raw_markers(value: Any) -> bool:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return any(marker in text for marker in RAW_FIELD_MARKERS)


def fmt(value: Any) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def build_markdown(analysis: dict[str, Any]) -> str:
    lines = [
        "# EVP-7 G5 Tool-Only Attribution Analysis",
        "",
        analysis["boundary"],
        "",
        "## Summary",
        "",
        f"- candidate count: {analysis['cohort']['candidate_count']}",
        f"- comparison levels: `{', '.join(analysis['cohort']['comparison_levels'])}`",
        f"- raw-output-free check passed: {str(analysis['raw_output_free_check']['passed']).lower()}",
        "",
        "## Matched Decision Overlap",
        "",
        "| evidence | tool condition | agreement | LLM accepts outside tool accepts | recovered tool false accepts | downgraded tool true accepts |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for level in COMPARISONS:
        item = analysis["comparisons"][level]
        counts = item["label_interaction_counts"]
        recovery = item["tool_false_accept_recovery"]
        retention = item["tool_true_accept_retention"]
        lines.append(
            f"| {level} | `{item['tool_condition']}` | "
            f"{item['agreement_count']}/{item['record_count']} ({fmt(item['agreement_rate'])}) | "
            f"{counts.get('llm_accept_not_tool_accept', 0)} | "
            f"{recovery['recovered']}/{recovery['total_tool_false_accepts']} | "
            f"{retention['downgraded']}/{retention['total_tool_true_accepts']} |"
        )
    lines.extend(["", "## Decision Pair Counts", ""])
    for level in COMPARISONS:
        item = analysis["comparisons"][level]
        lines.extend([f"### {level}", "", "| pair | count |", "|---|---:|"])
        for pair, count in item["decision_pair_counts"].items():
            lines.append(f"| `{pair}` | {count} |")
        lines.append("")
    lines.extend(
        [
            "## Interpretation Boundary",
            "",
            "- The LLM accepted no candidate that the matched deterministic tool-only baseline rejected.",
            "- The LLM recovered the observed tool-only false accepts at E4 and E6, but this came with lower correct-patch recall because many tool-only true accepts were downgraded to reject or escalate.",
            "- The result supports a bounded safety/recall attribution claim, not LLM superiority over deterministic tool evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze EVP-7 LLM decisions against deterministic tool-only baselines.")
    parser.add_argument("--reviews", default=str(DEFAULT_REVIEWS))
    parser.add_argument("--tool-decisions", default=str(DEFAULT_TOOL_DECISIONS))
    parser.add_argument("--candidates", default=str(DEFAULT_CANDIDATES))
    parser.add_argument("--out-json", default=str(DEFAULT_JSON_OUT))
    parser.add_argument("--out-md", default=str(DEFAULT_MD_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    analysis = analyze(Path(args.reviews), Path(args.tool_decisions), Path(args.candidates))
    write_json(Path(args.out_json), analysis)
    write_text(Path(args.out_md), build_markdown(analysis))
    print(
        json.dumps(
            {
                "out_json": args.out_json,
                "out_md": args.out_md,
                "raw_output_free": analysis["raw_output_free_check"]["passed"],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
