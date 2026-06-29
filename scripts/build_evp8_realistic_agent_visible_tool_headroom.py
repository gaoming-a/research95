"""Build visible-tool baseline and headroom analysis for EVP-8 realistic agents."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
COHORT_ID = "EVP-8-REALISTIC-AGENT"

DEFAULT_EVALUATOR_IN = REPO_ROOT / "data" / "patches" / "evp8_realistic_agent_evaluator_manifest_v0_1.jsonl"
DEFAULT_MODEL_VISIBLE_IN = REPO_ROOT / "data" / "evidence" / "evp8_realistic_agent_model_visible_seed_v0_1.jsonl"
DEFAULT_VISIBLE_OUTCOMES_IN = REPO_ROOT / "data" / "evidence" / "evp8_realistic_agent_visible_test_outcomes_v0_1.jsonl"
DEFAULT_MODEL_VISIBLE_OUT = REPO_ROOT / "data" / "evidence" / "evp8_realistic_agent_model_visible_seed_v0_2.jsonl"
DEFAULT_BASELINE_OUT = REPO_ROOT / "data" / "baselines" / "evp8_realistic_agent_visible_tool_baseline_v0_1.jsonl"
DEFAULT_SUMMARY_OUT = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_visible_tool_headroom_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_realistic_agent_visible_tool_headroom_v0_1.md"

FORBIDDEN_MODEL_VISIBLE_KEYS = {
    "candidate_type",
    "expected_outcome",
    "generation_rationale",
    "hidden_oracles",
    "hidden_validation_summary",
    "label_confidence",
    "model_candidate_id",
    "normalized_label",
    "oracle_command",
    "oracle_passed",
    "oracle_result",
    "oracle_ran",
    "oracle_workdir",
    "raw_generation_response_path",
    "raw_generation_response_sha256",
    "source_patch_id",
    "source_model_candidate_id",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{display_path(path)}:{line_number} must contain a JSON object")
        rows.append(value)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def display_path(path: Path) -> str:
    absolute = path if path.is_absolute() else REPO_ROOT / path
    try:
        return absolute.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(absolute)


def index_by_candidate_id(rows: list[dict[str, Any]], name: str) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for row in rows:
        candidate_id = str(row.get("candidate_id") or "")
        if not candidate_id:
            raise ValueError(f"{name} row missing candidate_id")
        if candidate_id in index:
            raise ValueError(f"{name} duplicate candidate_id: {candidate_id}")
        index[candidate_id] = row
    return index


def outcome_counts(outcome: dict[str, Any]) -> dict[str, int]:
    counter = Counter(str(result.get("outcome")) for result in outcome.get("test_results", []))
    return dict(sorted(counter.items()))


def baseline_decision(outcome: dict[str, Any]) -> tuple[str, str]:
    patch_apply = outcome.get("patch_apply_summary") or {}
    run_summary = outcome.get("visible_run_summary") or {}
    counts = outcome_counts(outcome)
    if patch_apply.get("applied") is not True:
        return "reject", "patch_apply_failed"
    if outcome.get("run_status") != "completed":
        return "escalate", f"visible_test_{outcome.get('run_status')}"
    if counts and set(counts) == {"passed"} and run_summary.get("passed") is True:
        return "accept", "all_declared_visible_tests_passed"
    if "failed" in counts:
        return "reject", "declared_visible_test_failed"
    return "escalate", "visible_test_inconclusive"


def visible_test_evidence(outcome: dict[str, Any]) -> dict[str, Any]:
    counts = outcome_counts(outcome)
    run_summary = outcome.get("visible_run_summary") or {}
    return {
        "listed_tests": outcome.get("visible_tests", []),
        "run_status": outcome.get("run_status"),
        "observed_outcome": run_summary.get("outcome"),
        "outcome_counts": counts,
        "patch_apply_summary": outcome.get("patch_apply_summary"),
        "test_results": outcome.get("test_results", []),
    }


def model_visible_v2(seed: dict[str, Any], outcome: dict[str, Any]) -> dict[str, Any]:
    evidence = visible_test_evidence(outcome)
    return seed | {
        "visible_test_evidence": evidence,
        "visible_tool_evidence": {
            "tool_summary_available": True,
            "visible_test_run_status": evidence["run_status"],
            "visible_test_observed_outcome": evidence["observed_outcome"],
            "visible_test_outcome_counts": evidence["outcome_counts"],
            "patch_apply_summary": evidence["patch_apply_summary"],
            "reason": "Declared visible tests were executed against the candidate patch in a recreated buggy checkout.",
        },
    }


def wilson_interval(successes: int, total: int, z: float = 1.96) -> dict[str, float | None]:
    if total == 0:
        return {"low": None, "high": None}
    phat = successes / total
    denominator = 1 + z * z / total
    centre = phat + z * z / (2 * total)
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total)
    return {
        "low": round((centre - margin) / denominator, 4),
        "high": round((centre + margin) / denominator, 4),
    }


def metric(successes: int, total: int) -> dict[str, Any]:
    return {
        "successes": successes,
        "total": total,
        "value": None if total == 0 else round(successes / total, 4),
        "wilson_95": wilson_interval(successes, total),
    }


def build(
    evaluator_rows: list[dict[str, Any]],
    model_visible_rows: list[dict[str, Any]],
    outcome_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    evaluator = index_by_candidate_id(evaluator_rows, "evaluator")
    visible = index_by_candidate_id(model_visible_rows, "model_visible")
    outcomes = index_by_candidate_id(outcome_rows, "visible_outcomes")
    ids = sorted(evaluator)
    if ids != sorted(visible) or ids != sorted(outcomes):
        raise ValueError("candidate_id sets do not match across evaluator, model-visible, and outcomes")

    baseline_rows: list[dict[str, Any]] = []
    model_visible_v2_rows: list[dict[str, Any]] = []
    matrix: dict[str, Counter[str]] = defaultdict(Counter)
    accepted_correct = 0
    accepted_wrong = 0
    rejected_wrong = 0
    rejected_correct = 0
    escalated = 0
    correct_total = 0
    wrong_total = 0

    for candidate_id in ids:
        eval_row = evaluator[candidate_id]
        outcome = outcomes[candidate_id]
        decision, reason = baseline_decision(outcome)
        label = str(eval_row["normalized_label"])
        is_correct = label == "correct"
        correct_total += int(is_correct)
        wrong_total += int(not is_correct)
        accepted_correct += int(decision == "accept" and is_correct)
        accepted_wrong += int(decision == "accept" and not is_correct)
        rejected_correct += int(decision == "reject" and is_correct)
        rejected_wrong += int(decision == "reject" and not is_correct)
        escalated += int(decision == "escalate")
        matrix[label][decision] += 1
        counts = outcome_counts(outcome)
        baseline_rows.append(
            {
                "baseline_id": "evp8_realistic_agent_visible_tool_baseline_v0_1",
                "cohort_id": COHORT_ID,
                "candidate_id": candidate_id,
                "task_id": outcome.get("task_id"),
                "project": outcome.get("project"),
                "decision": decision,
                "reason": reason,
                "visible_test_run_status": outcome.get("run_status"),
                "visible_test_observed_outcome": (outcome.get("visible_run_summary") or {}).get("outcome"),
                "visible_test_outcome_counts": counts,
                "patch_apply_summary": outcome.get("patch_apply_summary"),
                "api_call_attempted": False,
            }
        )
        model_visible_v2_rows.append(model_visible_v2(visible[candidate_id], outcome))

    accepted_total = accepted_correct + accepted_wrong
    summary = {
        "analysis_id": "evp8_realistic_agent_visible_tool_headroom_v0_1",
        "cohort_id": COHORT_ID,
        "candidate_count": len(ids),
        "api_call_attempted": False,
        "baseline_rule": "accept iff patch applies and all declared visible tests pass; reject on visible test failure or patch apply failure; escalate on tool error/timeout/inconclusive",
        "label_counts": dict(sorted(Counter(str(row["normalized_label"]) for row in evaluator_rows).items())),
        "decision_counts": dict(sorted(Counter(row["decision"] for row in baseline_rows).items())),
        "decision_by_label": {label: dict(sorted(counter.items())) for label, counter in sorted(matrix.items())},
        "metrics": {
            "accepted_precision": metric(accepted_correct, accepted_total),
            "correct_recall": metric(accepted_correct, correct_total),
            "false_accept_rate_among_wrong": metric(accepted_wrong, wrong_total),
            "wrong_reject_rate": metric(rejected_wrong, wrong_total),
            "correct_reject_rate": metric(rejected_correct, correct_total),
            "escalation_rate": metric(escalated, len(ids)),
        },
        "counts": {
            "accepted_correct": accepted_correct,
            "accepted_wrong": accepted_wrong,
            "rejected_correct": rejected_correct,
            "rejected_wrong": rejected_wrong,
            "escalated": escalated,
        },
        "headroom_assessment": {
            "visible_tool_is_not_sufficient_merge_gate": accepted_wrong > 0,
            "llm_false_accept_reduction_headroom_exists": accepted_wrong >= 10,
            "correct_patch_acceptance_power_is_undermeasured": correct_total < 10,
            "recommended_next_step": "Run Qwen/DeepSeek verifier on model-visible v0.2 only if the paper frames this cohort primarily as false-accept reduction/headroom, not correct-patch recall.",
        },
    }
    return baseline_rows, model_visible_v2_rows, summary


def forbidden_key_hits(value: Any, path: str = "$") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in FORBIDDEN_MODEL_VISIBLE_KEYS:
                hits.append(child_path)
            hits.extend(forbidden_key_hits(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(forbidden_key_hits(child, f"{path}[{index}]"))
    return hits


def check_outputs(
    baseline_rows: list[dict[str, Any]],
    model_visible_rows: list[dict[str, Any]],
    summary: dict[str, Any],
    expected_count: int | None,
) -> None:
    if expected_count is not None and summary["candidate_count"] != expected_count:
        raise SystemExit(f"expected {expected_count} candidates, got {summary['candidate_count']}")
    if len(baseline_rows) != summary["candidate_count"]:
        raise SystemExit("baseline row count mismatch")
    if len(model_visible_rows) != summary["candidate_count"]:
        raise SystemExit("model-visible row count mismatch")
    hits = forbidden_key_hits(model_visible_rows)
    if hits:
        raise SystemExit(f"forbidden evaluator fields leaked into model-visible v0.2: {hits[:10]}")


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    metrics = summary["metrics"]
    lines = [
        "# EVP-8 Realistic Agent Visible-Tool Headroom v0.1",
        "",
        "Date: 2026-06-30",
        "",
        "This analysis compares a deterministic visible-tool baseline against",
        "evaluator-only labels for the realistic agent-patch cohort. The baseline",
        "itself contains no labels; labels are used only in this headroom summary.",
        "",
        f"- candidates: {summary['candidate_count']}",
        f"- labels: `{summary['label_counts']}`",
        f"- decisions: `{summary['decision_counts']}`",
        f"- decision by label: `{summary['decision_by_label']}`",
        "",
        "Metrics:",
        "",
        f"- accepted precision: `{metrics['accepted_precision']['successes']}/{metrics['accepted_precision']['total']}` = `{metrics['accepted_precision']['value']}`",
        f"- correct recall: `{metrics['correct_recall']['successes']}/{metrics['correct_recall']['total']}` = `{metrics['correct_recall']['value']}`",
        f"- false accept rate among wrong: `{metrics['false_accept_rate_among_wrong']['successes']}/{metrics['false_accept_rate_among_wrong']['total']}` = `{metrics['false_accept_rate_among_wrong']['value']}`",
        f"- wrong reject rate: `{metrics['wrong_reject_rate']['successes']}/{metrics['wrong_reject_rate']['total']}` = `{metrics['wrong_reject_rate']['value']}`",
        f"- escalation rate: `{metrics['escalation_rate']['successes']}/{metrics['escalation_rate']['total']}` = `{metrics['escalation_rate']['value']}`",
        "",
        "Interpretation:",
        "",
        "- Visible tests alone are not a sufficient merge gate on this cohort.",
        "- The baseline accepts many test-passing wrong patches, so there is real",
        "  headroom for an LLM verifier to reduce false accepts.",
        "- Correct-patch recall is undermeasured because this separated realistic",
        "  cohort currently contains only one correct patch.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluator-in", type=Path, default=DEFAULT_EVALUATOR_IN)
    parser.add_argument("--model-visible-in", type=Path, default=DEFAULT_MODEL_VISIBLE_IN)
    parser.add_argument("--visible-outcomes-in", type=Path, default=DEFAULT_VISIBLE_OUTCOMES_IN)
    parser.add_argument("--model-visible-out", type=Path, default=DEFAULT_MODEL_VISIBLE_OUT)
    parser.add_argument("--baseline-out", type=Path, default=DEFAULT_BASELINE_OUT)
    parser.add_argument("--summary-out", type=Path, default=DEFAULT_SUMMARY_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--expected-count", type=int, default=53)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    baseline_rows, model_visible_rows, summary = build(
        evaluator_rows=read_jsonl(args.evaluator_in),
        model_visible_rows=read_jsonl(args.model_visible_in),
        outcome_rows=read_jsonl(args.visible_outcomes_in),
    )
    write_jsonl(args.baseline_out, baseline_rows)
    write_jsonl(args.model_visible_out, model_visible_rows)
    write_json(args.summary_out, summary)
    write_markdown(args.md_out, summary)
    if args.check:
        check_outputs(baseline_rows, model_visible_rows, summary, args.expected_count)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
