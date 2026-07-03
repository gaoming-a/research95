from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
QWEN_LABEL_SUMMARY = (
    REPO_ROOT
    / "data"
    / "reviews"
    / "evp8_qwen_first_main_v0_3_prompt_v0_2_label_conditioned_summary.json"
)
NO_VERDICT_COMPARISON = (
    REPO_ROOT / "data" / "reviews" / "evp8_e6_no_verdict_ablation_comparison.json"
)
PHASE_A_ANALYSIS = (
    REPO_ROOT / "data" / "reviews" / "evp8_phase_a_paper_ready_analysis.json"
)
DEFAULT_JSON_OUT = (
    REPO_ROOT / "data" / "reviews" / "ccfc_baseline_feasibility_audit_v0_1.json"
)
DEFAULT_MD_OUT = (
    REPO_ROOT / "docs" / "paper" / "ccfc_baseline_feasibility_audit_v0_1.md"
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def pct(value: float | None) -> str:
    if value is None:
        return "NA"
    return f"{value * 100:.2f}%"


def metric_from_counts(
    *,
    true_accept: int,
    false_accept: int,
    false_reject: int,
    true_reject: int,
    escalated_correct: int,
    escalated_incorrect: int,
    correct_total: int,
    incorrect_total: int,
) -> dict[str, Any]:
    total = correct_total + incorrect_total
    accept = true_accept + false_accept
    reject = false_reject + true_reject
    escalate = escalated_correct + escalated_incorrect
    accepted_precision = true_accept / accept if accept else None
    return {
        "record_count": total,
        "decision_counts": {
            "accept": accept,
            "reject": reject,
            "escalate": escalate,
        },
        "confusion_counts": {
            "true_accept": true_accept,
            "false_accept": false_accept,
            "false_reject": false_reject,
            "true_reject": true_reject,
            "escalated_correct": escalated_correct,
            "escalated_incorrect": escalated_incorrect,
        },
        "accepted_precision": accepted_precision,
        "correct_recall": true_accept / correct_total if correct_total else None,
        "false_accept_rate": false_accept / incorrect_total if incorrect_total else None,
        "false_reject_rate": false_reject / correct_total if correct_total else None,
        "escalation_rate": escalate / total if total else None,
    }


def deterministic_reference_baselines(
    correct_total: int, incorrect_total: int
) -> dict[str, dict[str, Any]]:
    random_probability = 1 / 3
    return {
        "always_escalate": metric_from_counts(
            true_accept=0,
            false_accept=0,
            false_reject=0,
            true_reject=0,
            escalated_correct=correct_total,
            escalated_incorrect=incorrect_total,
            correct_total=correct_total,
            incorrect_total=incorrect_total,
        ),
        "always_reject": metric_from_counts(
            true_accept=0,
            false_accept=0,
            false_reject=correct_total,
            true_reject=incorrect_total,
            escalated_correct=0,
            escalated_incorrect=0,
            correct_total=correct_total,
            incorrect_total=incorrect_total,
        ),
        "always_accept": metric_from_counts(
            true_accept=correct_total,
            false_accept=incorrect_total,
            false_reject=0,
            true_reject=0,
            escalated_correct=0,
            escalated_incorrect=0,
            correct_total=correct_total,
            incorrect_total=incorrect_total,
        ),
        "uniform_random_three_way_expected": metric_from_counts(
            true_accept=correct_total * random_probability,
            false_accept=incorrect_total * random_probability,
            false_reject=correct_total * random_probability,
            true_reject=incorrect_total * random_probability,
            escalated_correct=correct_total * random_probability,
            escalated_incorrect=incorrect_total * random_probability,
            correct_total=correct_total,
            incorrect_total=incorrect_total,
        ),
    }


def all_checks_pass(checks: list[dict[str, Any]]) -> bool:
    return all(bool(check.get("passed")) for check in checks)


def build_audit() -> dict[str, Any]:
    qwen = read_json(QWEN_LABEL_SUMMARY)
    no_verdict = read_json(NO_VERDICT_COMPARISON)
    phase_a = read_json(PHASE_A_ANALYSIS)

    label_distribution = qwen["label_distribution"]
    correct_total = int(label_distribution["correct_count"])
    incorrect_total = int(label_distribution["incorrect_count"])
    record_count = int(label_distribution["selected_candidate_count"])

    reference_baselines = deterministic_reference_baselines(
        correct_total=correct_total,
        incorrect_total=incorrect_total,
    )
    rule_only = no_verdict["rule_only"]["metrics"]
    qwen_e6 = no_verdict["per_model"]["qwen/qwen3.7-max"]["conditions"]["E6-full"][
        "metrics"
    ]
    deepseek_e6 = no_verdict["per_model"]["deepseek/deepseek-v4-pro"]["conditions"][
        "E6-full"
    ]["metrics"]

    completed_or_calculable = {
        **reference_baselines,
        "rule_only_visible_tool": rule_only,
        "qwen_e6_full": qwen_e6,
        "deepseek_e6_full": deepseek_e6,
    }

    feasibility = {
        "always_escalate": {
            "status": "calculable_from_label_totals",
            "reason": "Uses only aggregate correct/incorrect counts; no candidate text, prompt text, raw model output, or API call is needed.",
            "paper_role": "conservative abstention reference, not a useful verifier.",
        },
        "always_reject": {
            "status": "calculable_from_label_totals",
            "reason": "Uses only aggregate correct/incorrect counts.",
            "paper_role": "safety-heavy lower-bound reference exposing recall collapse.",
        },
        "always_accept": {
            "status": "calculable_from_label_totals",
            "reason": "Uses only aggregate correct/incorrect counts.",
            "paper_role": "unsafe throughput reference exposing base-rate risk.",
        },
        "uniform_random_three_way_expected": {
            "status": "calculable_expected_reference_from_label_totals",
            "reason": "Uses the expected value of a uniform random accept/reject/escalate policy over aggregate correct/incorrect counts; no stochastic simulation or candidate-level decisions are required.",
            "paper_role": "sanity-check reference for the decision space, not a completed verifier or a reported stochastic experiment.",
        },
        "rule_only_visible_tool": {
            "status": "completed_existing_tracked_result",
            "source": str(NO_VERDICT_COMPARISON.relative_to(REPO_ROOT)),
            "paper_role": "main deterministic baseline for E6 full/no-verdict comparison.",
        },
        "qwen_e6_full": {
            "status": "completed_existing_tracked_result",
            "source": str(NO_VERDICT_COMPARISON.relative_to(REPO_ROOT)),
            "paper_role": "model condition to compare against rule-only and no-verdict ablations.",
        },
        "deepseek_e6_full": {
            "status": "completed_existing_tracked_result",
            "source": str(NO_VERDICT_COMPARISON.relative_to(REPO_ROOT)),
            "paper_role": "secondary model condition in the E6 ablation package.",
        },
        "majority_vote_across_models": {
            "status": "not_feasible_from_current_aggregate_boundary",
            "reason": "Requires candidate-level aligned decisions across models and hidden labels. The current paper-facing boundary for this audit uses aggregate summaries only.",
            "paper_role": "do not report as completed unless a separate candidate-level, raw-output-free audit is built.",
        },
        "separate_no_tool_e0_deterministic_verifier": {
            "status": "partial_only",
            "reason": "Qwen E0 behavior exists, and always-escalate is calculable as a no-evidence conservative reference. A separate non-LLM E0 verifier policy has not been implemented as a tracked result.",
            "paper_role": "report Qwen E0 and always-escalate separately; do not call this a completed deterministic E0 verifier.",
        },
    }

    checks = [
        {
            "check": "input_files_exist",
            "passed": all(
                path.exists()
                for path in [QWEN_LABEL_SUMMARY, NO_VERDICT_COMPARISON, PHASE_A_ANALYSIS]
            ),
        },
        {
            "check": "label_totals_match_record_count",
            "passed": correct_total + incorrect_total == record_count == 98,
            "detail": {
                "correct_total": correct_total,
                "incorrect_total": incorrect_total,
                "record_count": record_count,
            },
        },
        {
            "check": "no_verdict_comparison_checks_pass",
            "passed": all_checks_pass(no_verdict.get("checks", [])),
        },
        {
            "check": "phase_a_checks_pass",
            "passed": all_checks_pass(phase_a.get("checks", [])),
        },
        {
            "check": "rule_only_record_count_matches",
            "passed": rule_only.get("record_count") == record_count,
            "detail": rule_only.get("record_count"),
        },
        {
            "check": "audit_api_call_attempted",
            "passed": True,
            "detail": False,
        },
        {
            "check": "raw_outputs_read_by_this_audit",
            "passed": True,
            "detail": False,
        },
        {
            "check": "prompt_or_patch_text_read_by_this_audit",
            "passed": True,
            "detail": False,
        },
    ]

    return {
        "audit_id": "ccfc_baseline_feasibility_audit_v0_1",
        "status": "passed" if all(check["passed"] is True for check in checks) else "failed",
        "cohort_id": "EVP-8",
        "scope": {
            "purpose": "determine which baseline rows can be honestly reported in the current CCF-C manuscript route.",
            "api_call_attempted": False,
            "raw_outputs_read": False,
            "prompt_or_patch_text_read": False,
            "inputs": [
                str(QWEN_LABEL_SUMMARY.relative_to(REPO_ROOT)),
                str(NO_VERDICT_COMPARISON.relative_to(REPO_ROOT)),
                str(PHASE_A_ANALYSIS.relative_to(REPO_ROOT)),
            ],
        },
        "cohort_totals": {
            "record_count": record_count,
            "correct_total": correct_total,
            "incorrect_total": incorrect_total,
        },
        "feasibility": feasibility,
        "completed_or_calculable_metrics": completed_or_calculable,
        "uncertainty_available": {
            key: phase_a["confidence_intervals"].get(key)
            for key in [
                "rule-only",
                "qwen/qwen3.7-max E6-full",
                "deepseek/deepseek-v4-pro E6-full",
            ]
        },
        "claim_boundary": {
            "allowed": [
                "Report always-escalate/always-reject/always-accept as deterministic reference policies calculated from label totals.",
                "Report uniform-random three-way only as an expected reference policy, not as a completed stochastic baseline run.",
                "Report rule-only visible-tool as the completed deterministic E6 baseline.",
                "Use Phase A confidence intervals for rule-only and E6 model conditions.",
            ],
            "forbidden": [
                "Do not claim a completed majority-vote baseline from aggregate-only files.",
                "Do not call always-escalate a successful verifier.",
                "Do not present the uniform-random expected reference as a real randomized experiment.",
                "Do not claim LLM superiority over deterministic baselines as the paper's main result.",
            ],
        },
        "checks": checks,
    }


def render_md(audit: dict[str, Any]) -> str:
    rows = []
    metric_keys = [
        "always_escalate",
        "always_reject",
        "always_accept",
        "uniform_random_three_way_expected",
        "rule_only_visible_tool",
        "qwen_e6_full",
        "deepseek_e6_full",
    ]
    for key in metric_keys:
        metrics = audit["completed_or_calculable_metrics"][key]
        decisions = metrics["decision_counts"]
        rows.append(
            "| {key} | {status} | {accept} | {reject} | {escalate} | {precision} | {recall} | {far} | {escalation} |".format(
                key=key,
                status=audit["feasibility"][key]["status"],
                accept=decisions.get("accept", 0),
                reject=decisions.get("reject", 0),
                escalate=decisions.get("escalate", 0),
                precision=pct(metrics.get("accepted_precision")),
                recall=pct(metrics.get("correct_recall")),
                far=pct(metrics.get("false_accept_rate")),
                escalation=pct(metrics.get("escalation_rate")),
            )
        )

    feasibility_rows = []
    for key, item in audit["feasibility"].items():
        feasibility_rows.append(
            f"| `{key}` | {item['status']} | {item.get('paper_role', '')} | {item.get('reason', item.get('source', ''))} |"
        )

    return "\n".join(
        [
            "# CCF-C Baseline Feasibility Audit v0.1",
            "",
            "## Scope",
            "",
            f"- audit id: `{audit['audit_id']}`",
            f"- status: `{audit['status']}`",
            "- boundary: tracked aggregate summaries only; no API call, no raw output read, no prompt text or patch text read.",
            f"- cohort: {audit['cohort_totals']['record_count']} candidates, {audit['cohort_totals']['correct_total']} correct and {audit['cohort_totals']['incorrect_total']} incorrect.",
            "",
            "## Baseline Table Readiness",
            "",
            "| baseline | status | accept | reject | escalate | accepted precision | correct recall | false accept rate | escalation rate |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|",
            *rows,
            "",
            "## Feasibility Decisions",
            "",
            "| baseline or analysis | feasibility | paper role | reason/source |",
            "|---|---|---|---|",
            *feasibility_rows,
            "",
            "## Manuscript Boundary",
            "",
            "Allowed:",
            "",
            *[f"- {item}" for item in audit["claim_boundary"]["allowed"]],
            "",
            "Forbidden:",
            "",
            *[f"- {item}" for item in audit["claim_boundary"]["forbidden"]],
            "",
            "## Checks",
            "",
            "| check | passed | detail |",
            "|---|---:|---|",
            *[
                f"| `{check['check']}` | {check['passed']} | `{check.get('detail', '')}` |"
                for check in audit["checks"]
            ],
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-json", default=str(DEFAULT_JSON_OUT))
    parser.add_argument("--out-md", default=str(DEFAULT_MD_OUT))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    audit = build_audit()
    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    rendered_json = json.dumps(audit, indent=2, ensure_ascii=False) + "\n"
    rendered_md = render_md(audit)

    if args.check:
        existing_json = out_json.read_text(encoding="utf-8") if out_json.exists() else ""
        existing_md = out_md.read_text(encoding="utf-8") if out_md.exists() else ""
        if existing_json != rendered_json or existing_md != rendered_md:
            raise SystemExit("baseline feasibility audit outputs are stale")
        print("baseline feasibility audit outputs are current")
        return

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(rendered_json, encoding="utf-8")
    out_md.write_text(rendered_md, encoding="utf-8")
    print(f"wrote {out_json.relative_to(REPO_ROOT)}")
    print(f"wrote {out_md.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
