"""Write the final manuscript claim map and stable CCF-C manuscript draft.

This script is no-API and raw-output-free. It uses tracked aggregate audits and
the final experiment-setting validity packet to produce a paper-facing claim
map plus a rewritten manuscript source for the stable CCF-C route.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDITY_AUDIT = REPO_ROOT / "data" / "reviews" / "final_experiment_setting_validity_audit_v0_1.json"
FIVE_MODEL_SYNTHESIS = REPO_ROOT / "data" / "protocols" / "evp8_five_model_synthesis_v0_1.json"
NO_VERDICT_COMPARISON = REPO_ROOT / "data" / "reviews" / "evp8_e6_no_verdict_ablation_comparison.json"
HARD_TOOL_CONTESTATION = REPO_ROOT / "data" / "protocols" / "evp8_hard_tool_contestation_result_audit_v0_1.json"
REALISTIC_GATE = REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_combined_generation_gate_with_full_file_v0_1.json"

DEFAULT_JSON_OUT = REPO_ROOT / "data" / "reviews" / "final_manuscript_claim_map_v0_1.json"
DEFAULT_CLAIM_MD_OUT = REPO_ROOT / "docs" / "paper" / "final_manuscript_claim_map_v0_1.md"
DEFAULT_MANUSCRIPT_MD_OUT = REPO_ROOT / "docs" / "paper" / "ccfc_manuscript_rewrite_v0_1.md"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def decision_totals_by_level(five: dict[str, Any]) -> dict[str, dict[str, int]]:
    totals: dict[str, dict[str, int]] = {}
    for level, by_model in (five.get("per_level_decision_counts_by_model") or {}).items():
        level_total: dict[str, int] = {}
        if not isinstance(by_model, dict):
            continue
        for counts in by_model.values():
            if not isinstance(counts, dict):
                continue
            for decision, count in counts.items():
                level_total[decision] = level_total.get(decision, 0) + int(count)
        totals[level] = dict(sorted(level_total.items()))
    return dict(sorted(totals.items()))


def compact_level_counts(five: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for level, by_model in (five.get("per_level_decision_counts_by_model") or {}).items():
        if not isinstance(by_model, dict):
            continue
        row = {"level": level}
        for model, counts in by_model.items():
            row[model] = counts
        rows.append(row)
    return rows


def build_claim_map() -> dict[str, Any]:
    validity = read_json(VALIDITY_AUDIT)
    five = read_json(FIVE_MODEL_SYNTHESIS)
    no_verdict = read_json(NO_VERDICT_COMPARISON)
    hard = read_json(HARD_TOOL_CONTESTATION)
    realistic = read_json(REALISTIC_GATE)

    hard_gate = realistic.get("hard_negative_gate") or {}
    hard_models = hard.get("models") or {}
    deepseek_contest = hard_models.get("deepseek/deepseek-v4-pro", {})
    qwen_contest = hard_models.get("qwen/qwen3.7-max", {})

    manuscript_argument = (
        "In candidate patch verification, we show that evidence visibility shapes LLM merge-gate "
        "risk behavior using frozen hidden-evaluator evidence packets, supported by five-model "
        "decision-pattern synthesis, no-verdict and tool-contestation ablations, and a realistic "
        "source-acquisition gate audit, with claims bounded away from autonomous correctness verification."
    )

    terminology = [
        {
            "term": "candidate patch verification",
            "definition": "the task of deciding accept/reject/escalate for a proposed patch under visible evidence",
            "decision": "Use as the manuscript's central task name.",
        },
        {
            "term": "evidence visibility",
            "definition": "the evidence fields available to the verifier at review time",
            "decision": "Use as the main explanatory variable.",
        },
        {
            "term": "hidden evaluator",
            "definition": "the evaluator-only label and oracle layer joined after model decisions",
            "decision": "Spell out on first use; emphasize non-visibility to models.",
        },
        {
            "term": "merge-gate decision",
            "definition": "one of accept, reject, or escalate",
            "decision": "Use instead of generic review decision when discussing outputs.",
        },
        {
            "term": "strict correction",
            "definition": "rejecting a known tool false accept",
            "decision": "Keep separate from escalation.",
        },
        {
            "term": "safe handling",
            "definition": "rejecting or escalating a known tool false accept",
            "decision": "Use only when escalation is explicitly treated as human-review routing.",
        },
    ]

    claims = [
        {
            "id": "C1",
            "claim": "Evidence visibility changes LLM merge-gate behavior on a frozen candidate-patch packet set.",
            "status": "supported",
            "evidence": ["evp8_five_model_synthesis_v0_1", "final_experiment_setting_validity_audit_v0_1"],
            "paper_location": "Results: Evidence visibility changes merge-gate decisions",
            "allowed_wording": "Evidence visibility changed verifier behavior across models and levels.",
            "boundary": "Descriptive decision-pattern result, not a claim of better correctness.",
        },
        {
            "id": "C2",
            "claim": "The observed evidence effect is model-dependent and non-monotonic.",
            "status": "supported",
            "evidence": ["per-level five-model decision counts"],
            "paper_location": "Results: Model-dependent, non-monotonic patterns",
            "allowed_wording": "The five-model synthesis showed model-dependent and non-monotonic escalation/rejection patterns.",
            "boundary": "Do not rank evidence levels as universally better.",
        },
        {
            "id": "C3",
            "claim": "Accept-aware protocol repairs are necessary to avoid over-interpreting earlier zero-accept artifacts.",
            "status": "supported_as_setting_repair",
            "evidence": ["v0_2_accept_aware_synthesis", "v0_3_qwen_label_conditioned_summary"],
            "paper_location": "Methods/Validity: Protocol repair and label-conditioned analysis",
            "allowed_wording": "Accept-aware analyses repair a protocol artifact and allow bounded recall/false-accept analysis.",
            "boundary": "Historical v0.1 zero-accept behavior should remain protocol history.",
        },
        {
            "id": "C4",
            "claim": "Verdict-like tool summaries can anchor model decisions; removing or contesting them changes behavior.",
            "status": "supported_qualified",
            "evidence": ["evp8_e6_no_verdict_ablation_comparison", "evp8_hard_tool_contestation_result_audit"],
            "paper_location": "Results: Verdict dependence and contestation",
            "allowed_wording": "Verdict removal and tool-contestation produced model-dependent risk-control tradeoffs.",
            "boundary": "Measured as policy behavior, not semantic proof.",
        },
        {
            "id": "C5",
            "claim": "Tool-contestation primarily improves safe handling through escalation rather than strict correction.",
            "status": "supported",
            "evidence": ["EVP-8-HARD tool-contestation audit"],
            "paper_location": "Results: Tool-contestation as risk triage",
            "allowed_wording": "Known false accepts were mostly shifted to escalation, so the supported contribution is risk triage.",
            "boundary": "Strict correction remains separate and limited.",
        },
        {
            "id": "C6",
            "claim": "The fresh realistic hard-negative branch is a source-acquisition negative result, not a verifier-ready main experiment.",
            "status": "supported_negative_boundary",
            "evidence": ["evp8_realistic_hardneg_combined_generation_gate_with_full_file_v0_1"],
            "paper_location": "Threats/Discussion: Realistic hard-negative acquisition",
            "allowed_wording": "The branch yielded a two-project hard-negative opportunity set but failed the three-project readiness gate.",
            "boundary": "Do not use it as three-project verifier evidence.",
        },
    ]

    figures = [
        {
            "id": "Fig. 1",
            "title": "Hidden-evaluator evidence-visibility protocol",
            "conclusion": "Model-visible evidence and evaluator-only labels are separated until post-decision analysis.",
            "panels": ["workflow from candidate patch to evidence packet", "model decision", "post-execution label join"],
            "status": "planned_requires_backend",
        },
        {
            "id": "Fig. 2",
            "title": "Five-model evidence-level decision patterns",
            "conclusion": "Escalation/rejection patterns vary by model and are non-monotonic across E0-E6.",
            "panels": ["heatmap of rejection counts by model and level", "stacked aggregate decision totals by level"],
            "status": "planned_requires_backend",
        },
        {
            "id": "Fig. 3",
            "title": "Claim boundary and setting-validity map",
            "conclusion": "Supported findings are bounded by leakage controls, protocol repairs, and remaining external-validity threats.",
            "panels": ["supported claims vs evidence sources", "controlled artifacts vs remaining threats"],
            "status": "planned_requires_backend",
        },
    ]

    checks = [
        check("validity_audit_passed_with_bounded_claims", validity.get("overall_status") == "passed_with_bounded_claims", validity.get("overall_status")),
        check("five_model_synthesis_passed", five.get("later_model_audit_status") == "passed", five.get("later_model_audit_status")),
        check("no_verdict_comparison_checks_present", len(no_verdict.get("checks", [])) >= 1, len(no_verdict.get("checks", []))),
        check("hard_tool_contestation_audit_passed", hard.get("audit_status") == "passed", hard.get("audit_status")),
        check("realistic_gate_not_verifier_ready", hard_gate.get("passed") is False, hard_gate),
    ]

    return {
        "artifact_id": "final_manuscript_claim_map_v0_1",
        "date": "2026-07-03",
        "paper_target": "stable CCF-C submission",
        "scope": {
            "api_call_attempted": False,
            "raw_model_outputs_read": False,
            "prompt_text_read": False,
            "patch_text_read": False,
            "figure_backend_selected": False,
        },
        "inputs": {
            "validity_audit": "data/reviews/final_experiment_setting_validity_audit_v0_1.json",
            "five_model_synthesis": "data/protocols/evp8_five_model_synthesis_v0_1.json",
            "no_verdict_comparison": "data/reviews/evp8_e6_no_verdict_ablation_comparison.json",
            "hard_tool_contestation": "data/protocols/evp8_hard_tool_contestation_result_audit_v0_1.json",
            "realistic_gate": "data/protocols/evp8_realistic_hardneg_combined_generation_gate_with_full_file_v0_1.json",
        },
        "manuscript_argument": manuscript_argument,
        "terminology_ledger": terminology,
        "claims": claims,
        "forbidden_claims": read_json(VALIDITY_AUDIT).get("forbidden_claims", []),
        "remaining_threats": read_json(VALIDITY_AUDIT).get("remaining_threats", []),
        "decision_totals_by_level": decision_totals_by_level(five),
        "per_model_level_counts": compact_level_counts(five),
        "hard_tool_contestation_summary": {
            "deepseek_opportunity": (deepseek_contest.get("opportunity_correction_vs_tool") or {}).get("tool_false_accepts"),
            "qwen_opportunity": (qwen_contest.get("opportunity_correction_vs_tool") or {}).get("tool_false_accepts"),
        },
        "realistic_gate_summary": {
            "visible_pass_hidden_fail_count": hard_gate.get("visible_pass_hidden_fail_count"),
            "minimum_count": hard_gate.get("minimum_count"),
            "visible_pass_hidden_fail_projects": hard_gate.get("visible_pass_hidden_fail_projects"),
            "minimum_projects": hard_gate.get("minimum_projects"),
            "passed": hard_gate.get("passed"),
        },
        "figure_plan": figures,
        "checks": checks,
        "status": "passed" if all(item["passed"] for item in checks) else "failed",
    }


def write_claim_markdown(path: Path, claim_map: dict[str, Any]) -> None:
    lines = [
        "# Final Manuscript Claim Map v0.1",
        "",
        "Date: 2026-07-03",
        "",
        f"- status: `{claim_map['status']}`",
        f"- target: `{claim_map['paper_target']}`",
        "",
        "## One-Sentence Argument",
        "",
        claim_map["manuscript_argument"],
        "",
        "## Terminology Ledger",
        "",
        "| canonical term | definition | decision |",
        "| --- | --- | --- |",
    ]
    for row in claim_map["terminology_ledger"]:
        lines.append(f"| {row['term']} | {row['definition']} | {row['decision']} |")
    lines += [
        "",
        "## Claim-Evidence Map",
        "",
        "| id | claim | status | evidence | paper location | boundary |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in claim_map["claims"]:
        lines.append(
            f"| `{row['id']}` | {row['claim']} | `{row['status']}` | "
            f"{', '.join(row['evidence'])} | {row['paper_location']} | {row['boundary']} |"
        )
    lines += ["", "## Forbidden Claims", ""]
    for claim in claim_map["forbidden_claims"]:
        lines.append(f"- {claim}")
    lines += [
        "",
        "## Figure Plan",
        "",
        "| figure | title | conclusion | status |",
        "| --- | --- | --- | --- |",
    ]
    for row in claim_map["figure_plan"]:
        lines.append(f"| {row['id']} | {row['title']} | {row['conclusion']} | `{row['status']}` |")
    lines += [
        "",
        "## Checks",
        "",
        "| check | passed | detail |",
        "| --- | ---: | --- |",
    ]
    for item in claim_map["checks"]:
        lines.append(f"| `{item['check']}` | {str(item['passed']).lower()} | `{item['detail']}` |")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_manuscript_markdown(path: Path, claim_map: dict[str, Any]) -> None:
    totals = claim_map["decision_totals_by_level"]
    totals_text = "; ".join(
        f"{level}: " + ", ".join(f"{decision}={count}" for decision, count in counts.items())
        for level, counts in totals.items()
    )
    realistic = claim_map["realistic_gate_summary"]
    deepseek_opp = claim_map["hard_tool_contestation_summary"]["deepseek_opportunity"] or {}
    qwen_opp = claim_map["hard_tool_contestation_summary"]["qwen_opportunity"] or {}
    lines = [
        "# Evidence Visibility Shapes Risk Behavior in LLM-Based Candidate Patch Verification",
        "",
        "Draft status: stable CCF-C manuscript rewrite v0.1, 2026-07-03.",
        "",
        "## Abstract",
        "",
        "Large language models (LLMs) are increasingly used to review software patches, but a patch-verification decision depends on the evidence visible at review time. We study candidate patch verification as an evidence-conditioned merge-gate task, where a verifier must accept, reject, or escalate a candidate patch while hidden evaluator labels remain withheld until after the decision. Using a frozen EVP-8 packet set with 98 candidate patches, seven evidence levels, and five LLMs, we find that evidence visibility changes decision patterns, but not as a monotonic correctness curve. The five-model synthesis passed run, parse, and coverage checks, and aggregate decisions varied across evidence levels. Accept-aware analyses further show why an earlier zero-accept setting should be treated as a protocol artifact rather than a main behavioral finding. In ablations, removing verdict-like fields and adding tool-contestation changed model behavior, but the strongest supported effect was risk triage through escalation rather than strict semantic correction. A fresh realistic hard-negative branch produced 26 visible-pass/hidden-fail cases across two projects, but failed the predeclared three-project verifier-readiness gate. The results support bounded claims about evidence-conditioned risk behavior in LLM-based patch verification, not reliable autonomous correctness verification.",
        "",
        "## 1. Introduction",
        "",
        "Candidate patches generated or reviewed by automated systems can look plausible while remaining incomplete, irrelevant, or unsafe to merge. This creates a software-quality problem: teams need to decide not only whether a patch resembles a fix, but whether the evidence available at review time is sufficient to accept it. In practice, that evidence may include issue summaries, patch diffs, static checks, visible tests, generated tests, or tool summaries. A verifier that ignores this evidence boundary risks confusing apparent plausibility with correctness.",
        "",
        "LLMs are attractive as patch reviewers because they can read code context and produce structured explanations. However, model behavior may depend strongly on what evidence is visible. If a study does not control the model-visible evidence, it becomes difficult to distinguish model capability from evidence presentation, tool-summary anchoring, or prompt-induced caution. This paper therefore treats evidence visibility as the main experimental variable in candidate patch verification.",
        "",
        "We study a hidden-evaluator workflow in which model-visible evidence packets are separated from evaluator-only labels. The verifier emits one merge-gate decision: accept, reject, or escalate. Correctness labels, hidden oracle outcomes, and failure taxonomy labels are joined only after execution for analysis. This design lets us ask a bounded question: how does evidence visibility shape LLM risk behavior when reviewing candidate patches?",
        "",
        "Our central finding is that evidence visibility changes merge-gate behavior, but the change is model-dependent and non-monotonic. The result is not evidence that LLMs are reliable autonomous patch correctness verifiers. Instead, it supports a software-quality interpretation: LLM verifiers should be evaluated as evidence-conditioned risk controllers whose behavior can shift toward rejection, escalation, or tool-summary dependence depending on the setting.",
        "",
        "## 2. Background and Related Work",
        "",
        "Patch correctness has long been a central concern in automated program repair and software testing. Generate-and-validate systems can produce plausible patches that pass available tests while failing broader semantic expectations. LLM-based coding agents expand this problem because they can generate fluent explanations and plausible edits, but plausibility is not equivalent to merge readiness.",
        "",
        "Existing repair benchmarks primarily evaluate whether a system can resolve a task. The verification problem studied here is adjacent but distinct: given a candidate patch, what decision should a verifier make under a stated evidence boundary? This distinction matters for software quality because a patch-review system may be useful as a triage layer even when it cannot prove correctness.",
        "",
        "Prior experiments in this repository also showed that prompt-only or verdict-like settings can create misleading interpretations. We therefore separate paper-facing results from diagnostic protocol history. The manuscript uses accept-aware repaired analyses, no-verdict ablations, tool-contestation audits, and final setting-validity checks to avoid overclaiming from a single prompt or protocol version.",
        "",
        "## 3. Evidence-Visibility Protocol",
        "",
        "The unit of analysis is a candidate patch reviewed under a predefined evidence packet. Each packet contains only model-visible information for its evidence level, while hidden evaluator labels and oracle outcomes remain unavailable to the model. After the model decision, evaluator-only labels are joined to compute false accepts, correct recall, escalation, and other bounded metrics.",
        "",
        "The EVP-8 packet set contains 98 candidate patches reviewed across seven evidence levels, E0 through E6. Five selected models produced 686 parse-valid decisions each on the frozen packet set. The synthesis supports descriptive per-level decision-pattern reporting for the packet set; it does not support broad claims that one evidence level is universally optimal or that LLMs outperform deterministic baselines.",
        "",
        "The protocol also distinguishes paper-facing evidence from diagnostic history. Earlier settings that produced zero accept decisions are treated as protocol artifacts unless repaired by accept-aware construction and label-conditioned analysis. This separation is necessary because otherwise a setting artifact could be mistaken for a general property of LLM patch verification.",
        "",
        "## 4. Experimental Design",
        "",
        "We organize the study around five evidence sources. First, the five-model EVP-8 synthesis measures descriptive decision patterns across seven evidence levels. Second, accept-aware v0.2/v0.3 analyses repair the earlier zero-accept artifact and allow bounded recall and false-accept analysis. Third, E6 no-verdict ablations test whether verdict-like tool summaries anchor model behavior. Fourth, EVP-8-HARD tool-contestation asks whether models challenge visible-test-only accept premises or route risk to escalation. Fifth, the realistic hard-negative branch evaluates whether a fresh source-acquisition pipeline can produce a verifier-ready three-project hard-negative cohort.",
        "",
        "All paper-facing claims are constrained by a final setting-validity audit. That audit verifies run and parse coverage, raw-output-free summaries, post-execution label joins, prompt-boundary checks, and the non-overclaiming of the realistic hard-negative branch. It passed only with bounded claims: the results are usable as real evidence for evidence-conditioned risk behavior, not as proof of autonomous correctness verification.",
        "",
        "## 5. Results",
        "",
        "### 5.1 Evidence visibility changed five-model decision patterns",
        "",
        f"Across the frozen EVP-8 packet set, aggregate decisions varied by evidence level: {totals_text}. These totals show that the decision pattern was not a simple monotonic curve from less evidence to more evidence.",
        "",
        "The variation was also model-dependent. DeepSeek V4 Pro and Qwen3.7 Max showed visible level-specific changes, whereas Devstral 2 saturated to escalation across the full packet set. Kimi K2.6 and Gemini 2.5 Flash mostly escalated, with limited local rejection differences. This spread is a software-quality result: a verifier can avoid unsafe accepts by escalating, but a system that escalates nearly everything provides limited automation value.",
        "",
        "### 5.2 Accept-aware analyses controlled a protocol artifact",
        "",
        "The earlier zero-accept behavior is not used as a main behavioral claim. Accept-aware v0.2/v0.3 analyses repair this setting and support bounded label-conditioned interpretation. In the final validity audit, the Qwen label-conditioned matrix had complete candidate-level coverage, no missing or duplicate cells, and hidden labels joined only after execution. This supports the claim that the repaired analyses are interpretable, while the historical zero-accept behavior remains protocol history.",
        "",
        "### 5.3 Verdict-like evidence changed policy behavior",
        "",
        "The E6 no-verdict ablation shows that verdict-like tool summaries affect model policy behavior. Removing verdict-like fields did not turn the models into reliable semantic verifiers. Instead, it exposed model-dependent tradeoffs between accepting correct patches, rejecting wrong patches, and escalating uncertain cases. This is why the paper reports verdict-full, no-verdict, and tool-contestation conditions separately.",
        "",
        "### 5.4 Tool-contestation supported risk triage, not strict correction",
        "",
        f"On EVP-8-HARD, tool-contestation covered 47 candidates for both Qwen and DeepSeek. For the known tool false-accept opportunity set, DeepSeek shifted {deepseek_opp.get('candidate_count')} tool false accepts to {deepseek_opp.get('escalated')} escalations and {deepseek_opp.get('corrected_to_reject')} strict rejects. Qwen shifted {qwen_opp.get('candidate_count')} tool false accepts to {qwen_opp.get('escalated')} escalations, with {qwen_opp.get('corrected_to_reject')} strict rejects and {qwen_opp.get('repeated_accept')} repeated accept. The supported interpretation is therefore risk triage through escalation, not semantic correction of wrong patches.",
        "",
        "### 5.5 Realistic hard-negative acquisition remained a boundary",
        "",
        f"The fresh realistic branch produced {realistic.get('visible_pass_hidden_fail_count')} visible-pass/hidden-fail cases, below the predeclared target of {realistic.get('minimum_count')}, and covered {len(realistic.get('visible_pass_hidden_fail_projects') or [])} projects rather than the required {realistic.get('minimum_projects')}. It is therefore a source-acquisition and gate-readiness negative result, not a verifier-ready main experiment.",
        "",
        "## 6. Discussion",
        "",
        "The results support a bounded but practically important interpretation. LLM-based patch verifiers are not only functions of model identity; they are functions of the evidence boundary. A model may become conservative, tool-dependent, or saturated depending on how patch evidence is presented. This matters for software quality because a deployment pipeline must decide whether escalation is acceptable, whether tool summaries should be trusted, and when a patch should remain under human review.",
        "",
        "The most important rival explanation is that the observed behavior is a setup artifact. The final setting-validity audit reduces this risk but does not erase all limitations. It shows that run coverage, parse validity, post-execution label joins, prompt-boundary checks, and claim boundaries are in place. It also identifies remaining threats: cohort diversity is limited, prompt formatting can influence behavior, and the realistic three-project hard-negative gate remains blocked.",
        "",
        "The paper should therefore avoid a stronger interpretation. It does not show that LLMs reliably verify patch correctness. It shows that evidence visibility shapes risk behavior in candidate patch verification and that some apparent improvements are better understood as conservative routing rather than correctness proof.",
        "",
        "## 7. Threats to Validity",
        "",
        "Internal validity may be affected by prompt wording, output schema, and evidence formatting. We mitigate this by using frozen packet sets, tracked prompt-boundary audits, raw-output-free summaries, and post-run matrix checks, but the findings remain tied to the evaluated protocol versions.",
        "",
        "Construct validity is limited by the accept/reject/escalate decision space. Escalation is useful as a human-review routing decision, but it is not strict correction. The manuscript therefore separates strict correction from safe handling.",
        "",
        "External validity is bounded by the EVP-8 candidate set, the EVP-8-HARD controlled cohort, and the selected models. The realistic hard-negative branch provides useful source-acquisition evidence but did not pass the three-project verifier-readiness gate. We therefore report it as a negative boundary rather than as main verifier evidence.",
        "",
        "Historical protocol versions are treated as diagnostic material. In particular, earlier zero-accept behavior is not used as a main result after accept-aware repair exposed its setting dependence.",
        "",
        "## 8. Conclusion",
        "",
        "This study shows that evidence visibility is a first-order variable in LLM-based candidate patch verification. Across frozen evidence packets, repaired analyses, no-verdict ablations, and tool-contestation audits, the strongest supported conclusion is that LLM verifier behavior is evidence-conditioned, model-dependent, and often conservative. These findings are useful for software-quality evaluation of LLM review pipelines, but they do not establish reliable autonomous patch correctness verification. A stable CCF-C manuscript should therefore present the work as a bounded empirical study of risk behavior under controlled evidence visibility.",
        "",
        "## Planned Figures",
        "",
        "Figure generation is pending backend selection. The current figure plan is:",
        "",
    ]
    for figure in claim_map["figure_plan"]:
        lines.append(f"- {figure['id']}: {figure['title']} — {figure['conclusion']}")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--out-claim-md", type=Path, default=DEFAULT_CLAIM_MD_OUT)
    parser.add_argument("--out-manuscript-md", type=Path, default=DEFAULT_MANUSCRIPT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    claim_map = build_claim_map()
    write_json(args.out_json, claim_map)
    write_claim_markdown(args.out_claim_md, claim_map)
    write_manuscript_markdown(args.out_manuscript_md, claim_map)
    if args.check and claim_map["status"] != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
