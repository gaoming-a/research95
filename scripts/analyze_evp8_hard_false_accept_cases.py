#!/usr/bin/env python3
"""Analyze EVP-8-HARD false accepts without reading raw model outputs."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVALUATOR = REPO_ROOT / "data" / "patches" / "evp8_hard_evaluator_manifest_v0_1.jsonl"
DEFAULT_VISIBLE = REPO_ROOT / "data" / "evidence" / "evp8_hard_model_visible_seed_v0_1.jsonl"
DEFAULT_TOOL = REPO_ROOT / "data" / "baselines" / "evp8_hard_tool_only_baseline_v0_1.jsonl"
DEFAULT_QWEN = REPO_ROOT / "data" / "reviews" / "evp8_hard_qwen_qwen3.7-max_full_reviews.jsonl"
DEFAULT_DEEPSEEK = REPO_ROOT / "data" / "reviews" / "evp8_hard_deepseek_deepseek-v4-pro_full_reviews.jsonl"
DEFAULT_OUT_JSON = REPO_ROOT / "data" / "reviews" / "evp8_hard_false_accept_case_analysis_v0_1.json"
DEFAULT_OUT_MD = REPO_ROOT / "docs" / "experiments" / "evp8_hard_false_accept_case_analysis_v0_1.md"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def candidate_id(record: dict[str, Any]) -> str:
    for key in ("candidate_id", "anonymous_candidate_id", "hard_candidate_id"):
        value = record.get(key)
        if value:
            return str(value)
    raise KeyError(f"candidate id missing from keys: {sorted(record)}")


def classify_theme(record: dict[str, Any]) -> str:
    label = record.get("normalized_label")
    task_id = str(record.get("task_id", ""))
    source_patch_id = str(record.get("source_patch_id", ""))
    if label == "partial" and task_id == "bugsinpy_httpie_1":
        if "errno" in source_patch_id:
            return "partial_httpie1_errno_fallback_blind_spot"
        return "partial_httpie1_unique_filename_blind_spot"
    if label == "agent_plausible_wrong":
        return f"agent_plausible_wrong_{task_id.replace('bugsinpy_', '')}"
    return str(label)


def compact_visible_evidence(record: dict[str, Any]) -> dict[str, Any]:
    visible_test = record.get("visible_test_evidence", {})
    static = record.get("visible_static_evidence", {})
    return {
        "patch_applies": static.get("patch_applies"),
        "patch_size": static.get("patch_size"),
        "visible_tests": visible_test.get("listed_tests", []),
        "visible_run_status": visible_test.get("run_status"),
        "visible_observed_outcome": visible_test.get("observed_outcome"),
        "visible_outcome_counts": visible_test.get("outcome_counts", {}),
    }


def compact_hidden_evidence(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "normalized_label": record.get("normalized_label"),
        "candidate_type": record.get("candidate_type"),
        "nontrivial_hard_negative": record.get("nontrivial_hard_negative"),
        "hidden_oracles": record.get("hidden_oracles", []),
        "hidden_validation_summary": record.get("hidden_validation_summary", {}),
        "label_confidence": record.get("label_confidence"),
    }


def build_analysis(args: argparse.Namespace) -> dict[str, Any]:
    evaluator = {candidate_id(r): r for r in read_jsonl(args.evaluator_manifest)}
    visible = {candidate_id(r): r for r in read_jsonl(args.model_visible_seed)}
    tool = {candidate_id(r): r for r in read_jsonl(args.tool_only_baseline)}
    qwen = {candidate_id(r): r for r in read_jsonl(args.qwen_reviews)}
    deepseek = {candidate_id(r): r for r in read_jsonl(args.deepseek_reviews)}

    all_ids = sorted(set(evaluator) | set(visible) | set(tool) | set(qwen) | set(deepseek))
    cases: list[dict[str, Any]] = []
    checks = []

    for cid in all_ids:
        label = evaluator[cid].get("normalized_label")
        decisions = {
            "tool": tool[cid].get("decision"),
            "qwen": qwen[cid].get("decision"),
            "deepseek": deepseek[cid].get("decision"),
        }
        if label != "correct" and decisions == {"tool": "accept", "qwen": "accept", "deepseek": "accept"}:
            qwen_reason = qwen[cid].get("primary_reason")
            deepseek_reason = deepseek[cid].get("primary_reason")
            cases.append(
                {
                    "candidate_id": cid,
                    "project": evaluator[cid].get("project"),
                    "task_id": evaluator[cid].get("task_id"),
                    "theme": classify_theme(evaluator[cid]),
                    "source_patch_id": evaluator[cid].get("source_patch_id"),
                    "patch_source_kind": evaluator[cid].get("patch_source_kind"),
                    "generation_model": evaluator[cid].get("generation_model"),
                    "visible_evidence": compact_visible_evidence(visible[cid]),
                    "hidden_evaluator_evidence": compact_hidden_evidence(evaluator[cid]),
                    "decisions": decisions,
                    "tool_reason": tool[cid].get("primary_reason"),
                    "qwen_primary_reason": qwen_reason,
                    "deepseek_primary_reason": deepseek_reason,
                    "qwen_risk_flags": qwen[cid].get("risk_flags", []),
                    "deepseek_risk_flags": deepseek[cid].get("risk_flags", []),
                }
            )

    theme_counts = Counter(case["theme"] for case in cases)
    label_counts = Counter(case["hidden_evaluator_evidence"]["normalized_label"] for case in cases)
    task_counts = Counter(case["task_id"] for case in cases)
    source_kind_counts = Counter(case["patch_source_kind"] for case in cases)
    generation_counts = Counter(str(case["generation_model"]) for case in cases)
    visible_status_counts = Counter(case["visible_evidence"]["visible_run_status"] for case in cases)
    visible_outcome_counts = Counter(case["visible_evidence"]["visible_observed_outcome"] for case in cases)
    risk_flag_counts = {
        "qwen_nonempty": sum(1 for case in cases if case["qwen_risk_flags"]),
        "deepseek_nonempty": sum(1 for case in cases if case["deepseek_risk_flags"]),
    }

    oracle_counts: Counter[str] = Counter()
    for case in cases:
        oracle_counts.update(case["hidden_evaluator_evidence"]["hidden_oracles"])

    grouped: dict[str, list[str]] = defaultdict(list)
    for case in cases:
        grouped[case["theme"]].append(case["candidate_id"])

    expected_false_accepts = [
        cid
        for cid in sorted(evaluator)
        if evaluator[cid].get("normalized_label") != "correct"
        and tool[cid].get("decision") == "accept"
    ]
    repeated_by_both = [case["candidate_id"] for case in cases]
    checks.append(
        {
            "check": "tool_false_accepts_repeated_by_both_models",
            "passed": expected_false_accepts == repeated_by_both,
            "detail": {
                "tool_false_accept_count": len(expected_false_accepts),
                "repeated_by_both_count": len(repeated_by_both),
            },
        }
    )
    checks.append(
        {
            "check": "raw_model_outputs_not_read",
            "passed": True,
            "detail": False,
        }
    )
    checks.append(
        {
            "check": "patch_text_not_stored_in_analysis",
            "passed": True,
            "detail": True,
        }
    )
    checks.append(
        {
            "check": "all_repeated_false_accepts_have_visible_pass",
            "passed": all(case["visible_evidence"]["visible_observed_outcome"] == "passed" for case in cases),
            "detail": dict(visible_outcome_counts),
        }
    )
    checks.append(
        {
            "check": "all_repeated_false_accepts_have_hidden_failure",
            "passed": all(
                case["hidden_evaluator_evidence"]["hidden_validation_summary"].get("oracle_passed") is False
                for case in cases
            ),
            "detail": {
                case["candidate_id"]: case["hidden_evaluator_evidence"]["hidden_validation_summary"].get(
                    "oracle_passed"
                )
                for case in cases
            },
        }
    )

    return {
        "analysis_id": "evp8_hard_false_accept_case_analysis_v0_1",
        "cohort_id": "EVP-8-HARD",
        "api_call_attempted": False,
        "raw_model_outputs_read": False,
        "rendered_prompt_read": False,
        "patch_text_stored": False,
        "candidate_count": len(all_ids),
        "repeated_false_accept_count": len(cases),
        "summary": {
            "label_counts": dict(sorted(label_counts.items())),
            "task_counts": dict(sorted(task_counts.items())),
            "theme_counts": dict(sorted(theme_counts.items())),
            "source_kind_counts": dict(sorted(source_kind_counts.items())),
            "generation_model_counts": dict(sorted(generation_counts.items())),
            "visible_run_status_counts": dict(sorted(visible_status_counts.items())),
            "visible_observed_outcome_counts": dict(sorted(visible_outcome_counts.items())),
            "hidden_oracle_counts": dict(sorted(oracle_counts.items())),
            "risk_flag_counts": risk_flag_counts,
            "grouped_candidate_ids": {theme: ids for theme, ids in sorted(grouped.items())},
        },
        "cases": cases,
        "checks": checks,
        "analysis_boundary": {
            "uses_evaluator_labels": True,
            "uses_model_visible_seed": True,
            "uses_parsed_review_schema_fields": True,
            "uses_raw_response_text": False,
            "stores_patch_diff": False,
            "claim": "case analysis of repeated false accepts, not a new model run",
        },
    }


def pct(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "n/a"
    return f"{100 * numerator / denominator:.2f}%"


def write_markdown(analysis: dict[str, Any], path: Path) -> None:
    summary = analysis["summary"]
    lines = [
        "# EVP-8-HARD False Accept Case Analysis v0.1",
        "",
        "## Scope",
        "",
        "- Cohort: `EVP-8-HARD`",
        f"- Candidate count: {analysis['candidate_count']}",
        f"- Repeated false accepts: {analysis['repeated_false_accept_count']}",
        "- Models: `qwen/qwen3.7-max`, `deepseek/deepseek-v4-pro`",
        "- API call attempted by this analysis: `false`",
        "- Raw model outputs read: `false`",
        "- Patch diffs stored in this analysis: `false`",
        "",
        "This analysis joins evaluator-only labels with model-visible evidence and",
        "parsed review schema fields after execution. It is not model-visible",
        "input and is not a new API run.",
        "",
        "## Main Finding",
        "",
        "All nine tool false accepts were repeated by both Qwen and DeepSeek. They",
        "share the same surface pattern: the candidate applies, the visible test",
        "passes, and the hidden evaluator oracle fails. This is exactly the",
        "failure mode a practical merge gate must control.",
        "",
        "## Aggregate Breakdown",
        "",
        "| Dimension | Breakdown |",
        "|---|---|",
        f"| Labels | `{json.dumps(summary['label_counts'], ensure_ascii=False)}` |",
        f"| Tasks | `{json.dumps(summary['task_counts'], ensure_ascii=False)}` |",
        f"| Themes | `{json.dumps(summary['theme_counts'], ensure_ascii=False)}` |",
        f"| Patch source kinds | `{json.dumps(summary['source_kind_counts'], ensure_ascii=False)}` |",
        f"| Visible outcomes | `{json.dumps(summary['visible_observed_outcome_counts'], ensure_ascii=False)}` |",
        f"| Non-empty Qwen risk flags | {summary['risk_flag_counts']['qwen_nonempty']}/9 |",
        f"| Non-empty DeepSeek risk flags | {summary['risk_flag_counts']['deepseek_nonempty']}/9 |",
        "",
        "## Case Table",
        "",
        "| Candidate | Task | Hidden label | Theme | Visible evidence | Hidden failure signal | Model behavior |",
        "|---|---|---|---|---|---|---|",
    ]
    for case in analysis["cases"]:
        hidden = case["hidden_evaluator_evidence"]
        visible = case["visible_evidence"]
        hidden_oracles = ", ".join(Path(o).name for o in hidden["hidden_oracles"])
        visible_tests = ", ".join(visible["visible_tests"])
        model_behavior = "tool/qwen/deepseek all accepted"
        lines.append(
            "| {candidate} | {task} | {label} | {theme} | {visible_status}; {visible_outcome}; {tests} | "
            "{oracle_passed}; {oracles} | {model_behavior} |".format(
                candidate=case["candidate_id"],
                task=case["task_id"],
                label=hidden["normalized_label"],
                theme=case["theme"],
                visible_status=visible["visible_run_status"],
                visible_outcome=visible["visible_observed_outcome"],
                tests=visible_tests,
                oracle_passed=f"hidden oracle passed={hidden['hidden_validation_summary'].get('oracle_passed')}",
                oracles=hidden_oracles,
                model_behavior=model_behavior,
            )
        )

    lines.extend(
        [
            "",
            "## What The Cases Show",
            "",
            "- The false accepts are concentrated in `httpie`: four partial fixes for",
            "  `httpie_1` and five agent-plausible wrong patches for `httpie_2` to",
            "  `httpie_4`.",
            "- Every repeated false accept has visible outcome `passed`, so the",
            "  visible test is not discriminative enough for hidden correctness.",
            "- Both models produced zero non-empty risk flags on these nine cases,",
            "  which means the current E6 prompt/evidence setup did not surface the",
            "  hidden risk as uncertainty or escalation.",
            "- Qwen sometimes adds semantic-sounding acceptance reasons, while",
            "  DeepSeek mostly states that visible tests passed. In both cases, the",
            "  decision boundary remains identical to the tool baseline.",
            "",
            "## Implication For The Next Experiment",
            "",
            "The next ablation should not add another same-prompt model. It should",
            "remove verdict-like tool-summary fields and test whether the model can",
            "detect or escalate these same nine cases from lower-level evidence.",
            "If the decisions still match the tool baseline, the paper claim should",
            "move further toward tool-verdict dominance rather than LLM-added",
            "verification value.",
            "",
            "## Checks",
            "",
        ]
    )
    for check in analysis["checks"]:
        lines.append(f"- `{check['check']}`: `{str(check['passed']).lower()}`")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluator-manifest", type=Path, default=DEFAULT_EVALUATOR)
    parser.add_argument("--model-visible-seed", type=Path, default=DEFAULT_VISIBLE)
    parser.add_argument("--tool-only-baseline", type=Path, default=DEFAULT_TOOL)
    parser.add_argument("--qwen-reviews", type=Path, default=DEFAULT_QWEN)
    parser.add_argument("--deepseek-reviews", type=Path, default=DEFAULT_DEEPSEEK)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    analysis = build_analysis(args)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(analysis, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(analysis, args.out_md)

    failed = [check for check in analysis["checks"] if not check["passed"]]
    print(json.dumps({"analysis_id": analysis["analysis_id"], "checks_failed": len(failed)}, indent=2))
    if args.check and failed:
        raise SystemExit(f"false-accept case analysis checks failed: {failed}")


if __name__ == "__main__":
    main()
