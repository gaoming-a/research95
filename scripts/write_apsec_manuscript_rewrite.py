"""Write an APSEC-style technical-track manuscript rewrite.

This script is no-API and raw-output-free. It reuses the tracked final claim
map generator and produces a conference-paper shaped Markdown draft while
preserving the existing stable CCF-C manuscript.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from write_final_manuscript_claim_map import build_claim_map, ci_percent, percent


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_MD = REPO_ROOT / "docs" / "paper" / "apsec_technical_track_rewrite_v0_1.md"


def metric_table(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| condition | accept | reject | escalate | accepted precision | correct recall | false accept rate | escalation rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        decisions = row.get("decision_counts", {})
        accept = row.get("accept", decisions.get("accept", 0))
        reject = row.get("reject", decisions.get("reject", 0))
        escalate = row.get("escalate", decisions.get("escalate", 0))
        lines.append(
            f"| {row['condition']} | {accept} | {reject} | {escalate} | "
            f"{percent(row.get('accepted_precision'))} | {percent(row.get('correct_recall'))} | "
            f"{percent(row.get('false_accept_rate'))} | {percent(row.get('escalation_rate'))} |"
        )
    return lines


def qwen_table(claim_map: dict[str, Any]) -> list[str]:
    lines = [
        "| level | accept | correct accept | false accept | accepted precision | correct recall | false accept rate | escalation rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in claim_map["qwen_label_conditioned_metrics"]:
        lines.append(
            f"| {row['level']} | {row['accept']} | {row['correct_accept']} | {row['false_accept']} | "
            f"{percent(row.get('accepted_precision'))} | {percent(row.get('correct_recall'))} | "
            f"{percent(row.get('false_accept_rate'))} | {percent(row.get('escalation_rate'))} |"
        )
    return lines


def uncertainty_table(claim_map: dict[str, Any]) -> list[str]:
    lines = [
        "| condition | accepted precision 95% CI | correct recall 95% CI | false accept rate 95% CI | escalation rate 95% CI |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in claim_map["phase_a_uncertainty_summary"]:
        lines.append(
            f"| {row['condition']} | {ci_percent(row.get('accepted_precision'))} | "
            f"{ci_percent(row.get('correct_recall'))} | {ci_percent(row.get('false_accept_rate'))} | "
            f"{ci_percent(row.get('escalation_rate'))} |"
        )
    return lines


def tool_contestation_table(claim_map: dict[str, Any]) -> list[str]:
    lines = [
        "| model | opportunity cases | safe handling 95% CI | strict correction 95% CI | repeated accept 95% CI |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in claim_map["tool_contestation_uncertainty_summary"]:
        lines.append(
            f"| {row['model']} | {row['candidate_count']} | {ci_percent(row['safe_handling_ci'])} | "
            f"{ci_percent(row['strict_correction_ci'])} | {ci_percent(row['repeated_accept_ci'])} |"
        )
    return lines


def evidence_ladder_table(claim_map: dict[str, Any]) -> list[str]:
    lines = [
        "| level | added evidence | role |",
        "| --- | --- | --- |",
    ]
    for row in claim_map["evidence_ladder"]:
        lines.append(
            f"| {row['level']} | {row['adds']} | {row['name']} |"
        )
    return lines


def baseline_table(claim_map: dict[str, Any]) -> list[str]:
    lines = [
        "| policy or condition | status | accept | reject | escalate | role |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in claim_map["baseline_policy_boundaries"]:
        role = row.get("paper_role", row.get("role", ""))
        lines.append(
            f"| {row['policy']} | {row['status']} | {row['accept']} | {row['reject']} | {row['escalate']} | {role} |"
        )
    return lines


def write_apsec_markdown(path: Path, claim_map: dict[str, Any]) -> None:
    qwen_opp = claim_map["hard_tool_contestation_summary"]["qwen_opportunity"]
    deepseek_opp = claim_map["hard_tool_contestation_summary"][
        "deepseek_opportunity"
    ]
    realistic = claim_map["realistic_gate_summary"]
    figures = {figure["id"]: figure for figure in claim_map["figure_plan"]}

    lines = [
        "# Evidence Visibility Shapes Risk Behavior in LLM-Based Patch Verification",
        "",
        "Draft status: APSEC technical-track Markdown rewrite v0.1, 2026-07-05.",
        "",
        "Target format note: this draft is shaped for an APSEC-style technical research paper. The next formatting step is an anonymous IEEEtran conference submission using the target venue page limit and reference style; this Markdown file is not yet the final PDF.",
        "",
        "## Abstract",
        "",
        "Patch-verification decisions made by large language models (LLMs) are meaningful only relative to the evidence visible at review time. Existing evaluations often report whether an LLM accepts or rejects a patch without making this evidence boundary explicit, which makes it difficult to separate model capability from visible-test evidence, tool-summary anchoring, or prompt-induced caution. This paper introduces the Evidence-Visibility Protocol (EVP-8), a hidden-evaluator protocol for candidate patch verification. EVP-8 reviews 98 candidate patches across seven cumulative evidence levels while withholding evaluator-only correctness labels until post-decision analysis. In the repaired Qwen v0.3 run, correct recall was 0.00% at E0-E2, 80.95% at E3, 85.71% at E4-E5, and 95.24% at E6; E6 accepted precision was 83.33%, with four false accepts among 77 non-correct candidates. E6 rule-only and no-verdict ablations show that verdict-like tool summaries can anchor policy behavior, and tool-contestation moved known tool false accepts mainly to escalation rather than strict rejection. These results support a bounded software-engineering claim: LLM patch verifiers should be evaluated as evidence-conditioned risk controllers, not as autonomous correctness oracles.",
        "",
        "## 1. Introduction",
        "",
        "Automated patch generation and LLM-assisted review are increasingly positioned near software merge decisions. This creates a practical software-quality question: when a candidate patch appears plausible, which visible evidence is sufficient for a verifier to accept it rather than reject it or escalate it for human review? Prior automated program repair work has shown that plausible or test-passing patches can still be incorrect [qi_issta_2015_patch_plausibility; legoues_icse_2012_genprog], so a merge decision cannot be reduced to surface plausibility alone.",
        "",
        "The difficulty is not only whether an LLM can read code. It is that a verifier's decision may change when issue context, patch structure, static status, visible tests, regression checks, diagnostics, or tool summaries become visible. If these evidence fields are not controlled, an evaluation may conflate model judgment with evidence presentation. In particular, authoritative-looking tool summaries can encourage acceptance even when the underlying semantic correctness remains unknown.",
        "",
        "This paper studies candidate patch verification as an evidence-conditioned merge-gate task. A verifier receives a candidate patch and a predefined model-visible evidence packet, then emits one of three decisions: accept, reject, or escalate. Correctness labels and hidden evaluator outcomes are joined only after the decision. This design follows the intuition behind reject-option and selective-classification settings [chow_tit_1970_reject_option; geifman_el_yaniv_2017_selective_classification], but applies it to software patch verification.",
        "",
        "The paper makes three contributions:",
        "",
        "- It defines EVP-8, a hidden-evaluator evidence-visibility protocol for measuring accept, reject, and escalation behavior in candidate patch verification.",
        "- It reports repaired Qwen v0.3 label-conditioned results showing that visible executable and tool evidence can unlock correct-patch acceptance while introducing bounded false-accept risk.",
        "- It analyzes E6 rule-only, no-verdict, and tool-contestation conditions to separate deterministic tool evidence, verdict-like anchoring, safe handling, and strict correction.",
        "",
        "The claim is deliberately bounded. The results do not establish reliable autonomous patch correctness verification, nor do they show that LLM decisions consistently outperform deterministic baselines. They show that evidence visibility is a measurable experimental variable that should be controlled and reported when evaluating LLM patch verifiers.",
        "",
        "## 2. Background and Motivation",
        "",
        "Automated program repair research has long distinguished plausible patches from correct patches. Generate-and-validate systems and controlled benchmarks have shown that passing available tests may be insufficient for semantic correctness [qi_issta_2015_patch_plausibility; just_issta_2014_defects4j]. EVP-8 studies the downstream verifier setting: after a candidate patch exists, the question is not how it was generated, but whether a merge-gate decision is justified by the evidence visible to the verifier.",
        "",
        "Software testing research also motivates the hidden-evaluator design. The oracle problem means that deciding correctness is itself a validity boundary [barr_tse_2015_oracle_problem]. EVP-8 therefore keeps evaluator-only labels separate from model-visible evidence and joins them only after decisions have been produced.",
        "",
        "LLM-based repair and code-editing studies show that LLMs can produce or inspect patches [xia_zhang_icse_2023_llm_apr; tufano_icse_2019_bugfix_nmt]. However, verifier behavior is not identical to generation performance. A patch reviewer must decide whether visible evidence is enough to accept, reject, or escalate. This makes the task closer to code review and risk triage than to benchmark success alone [bacchelli_bird_icse_2013_code_review].",
        "",
        "Finally, LLM-as-judge and automation-reliance work warn that model judgments and automation outputs require controlled protocols and explicit boundaries [zheng_neurips_2023_llm_judge; parasuraman_riley_1997_automation]. The protocol in this paper responds to that concern by making evidence visibility an explicit variable rather than an implicit property of the prompt.",
        "",
        "## 3. Evidence-Visibility Protocol",
        "",
        "EVP-8 evaluates a candidate patch under a fixed evidence packet. The model-visible packet contains only the evidence level assigned to that condition. The evaluator-only layer contains hidden correctness labels and oracle outcomes used only after the verifier emits its decision.",
        "",
        "![Figure 1. Hidden-evaluator evidence-visibility protocol.](../figures/ccfc/ccfc_fig1_protocol.png)",
        "",
        f"**Figure 1. {figures['Fig. 1']['title']}.** {figures['Fig. 1']['conclusion']} The model can inspect candidate patches and level-specific evidence, but evaluator labels remain hidden until post-decision analysis.",
        "",
        "The reviewed unit is a candidate patch. The decision space is accept, reject, or escalate. Escalation is treated as a human-review routing decision, not as semantic rejection. This distinction is important because safe handling of a risky patch can occur through escalation even when strict correction does not occur.",
        "",
        "EVP-8 uses seven cumulative evidence levels:",
        "",
        *evidence_ladder_table(claim_map),
        "",
        "The current packet set contains 98 candidate patches. Five selected models produced complete parse-valid decisions on the frozen E0-E6 packet set in earlier protocol runs, but the paper-facing main result uses the repaired Qwen v0.3 label-conditioned analysis and the E6 ablation package. The five-model aggregate synthesis is used only descriptively and not as evidence of final model superiority.",
        "",
        "## 4. Experimental Design",
        "",
        "The experiment asks four research questions. RQ1 asks whether repaired accept-aware evidence changes Qwen's label-conditioned decisions across E0-E6. RQ2 asks whether verdict-like deterministic tool summaries anchor E6 decisions. RQ3 asks whether explicit tool-contestation can challenge visible-test-only accept premises. RQ4 asks whether the fresh realistic hard-negative branch is ready to support a main verifier experiment.",
        "",
        "All metrics are computed after post-decision hidden-label join. The main metrics are accepted precision, correct recall, false accept rate, false reject rate, and escalation rate. Accepted precision measures the correctness of accepted patches. Correct recall measures how many correct patches were accepted. False accept rate measures how often non-correct candidates were accepted. Escalation rate measures routing to human review.",
        "",
        "The baseline boundary is explicit. Always-escalate, always-reject, and always-accept are deterministic reference policies calculated from label totals. Uniform random three-way is an expected reference policy, not a stochastic experiment. The completed deterministic baseline is rule-only visible-tool. Qwen E0 is an observed model condition, not a deterministic no-tool verifier. Majority-vote and a separate E0/no-tool deterministic verifier are not reported as completed because current tracked summaries do not contain candidate-level aligned decision records.",
        "",
        *baseline_table(claim_map),
        "",
        "All paper-facing claims are constrained by a setting-validity audit. The audit checks run coverage, parse validity, raw-output-free summaries, post-execution label joins, prompt-boundary conditions, baseline feasibility, and exclusion of the earlier invalid setting. The audit passed only for bounded claims.",
        "",
        "## 5. Results",
        "",
        "### 5.1 Visible executable evidence changed Qwen acceptance behavior",
        "",
        "In the repaired Qwen v0.3 run, the E0-E2 conditions produced no accepted correct patches. Once visible executable evidence entered the packet at E3, Qwen began accepting correct patches, reaching 80.95% correct recall at E3 and 95.24% at E6. This gain came with false-accept risk: E6 accepted 4 of 77 non-correct candidates.",
        "",
        *qwen_table(claim_map),
        "",
        "![Figure 2. Accept-aware and no-verdict metric evidence.](../figures/ccfc/ccfc_fig2_decision_patterns.png)",
        "",
        f"**Figure 2. {figures['Fig. 2']['title']}.** {figures['Fig. 2']['conclusion']} The figure emphasizes the main tradeoff: more visible evidence enabled correct accepts, but acceptance remained bounded by false-accept risk.",
        "",
        "The result supports an evidence-visibility claim, not a monotonic correctness claim. More evidence changed policy behavior and unlocked acceptance, but the E6 false accepts show that visible evidence did not become a correctness oracle.",
        "",
        "### 5.2 Verdict-like evidence affected policy behavior",
        "",
        "The E6 ablation compares the deterministic rule-only visible-tool baseline, full E6 model conditions, and E6-no-verdict conditions. This tests whether model decisions add value beyond following visible tool verdict fields.",
        "",
        *metric_table(claim_map["e6_ablation_metrics"]),
        "",
        "Qwen E6-full and rule-only produced similar correct recall, accepted precision, and false accept rates. Qwen E6-no-verdict remained close to Qwen E6-full. DeepSeek E6-no-verdict removed false accepts in this cohort, but correct recall dropped to 52.38% and escalation increased to 14.29%. The safer behavior therefore appears to be partly abstention-driven rather than strict semantic discrimination.",
        "",
        "The Wilson intervals are wide, so the ablation should be read as bounded risk-policy evidence rather than as a ranking of model quality.",
        "",
        *uncertainty_table(claim_map),
        "",
        "### 5.3 Tool-contestation shifted risky accepts to escalation, not strict correction",
        "",
        f"On the EVP-8-HARD cohort, tool-contestation evaluated 47 candidates for both Qwen and DeepSeek. For the known tool false-accept opportunity set, DeepSeek shifted {deepseek_opp.get('candidate_count')} tool false accepts to {deepseek_opp.get('escalated')} escalations and {deepseek_opp.get('corrected_to_reject')} strict rejects. Qwen shifted {qwen_opp.get('candidate_count')} tool false accepts to {qwen_opp.get('escalated')} escalations, with {qwen_opp.get('corrected_to_reject')} strict rejects and {qwen_opp.get('repeated_accept')} repeated accept.",
        "",
        "This result supports safe handling through escalation. It does not support a claim that tool-contestation reliably identifies semantic incorrectness, because strict correction remained zero for both models.",
        "",
        *tool_contestation_table(claim_map),
        "",
        "### 5.4 Realistic hard-negative acquisition remained a boundary",
        "",
        f"The fresh realistic branch produced {realistic.get('visible_pass_hidden_fail_count')} visible-pass/hidden-fail cases across {len(realistic.get('visible_pass_hidden_fail_projects') or [])} projects. This missed the predeclared verifier-readiness gate of {realistic.get('minimum_count')} cases across {realistic.get('minimum_projects')} projects. The branch is therefore reported as a source-acquisition boundary rather than a main verifier experiment.",
        "",
        "## 6. Discussion",
        "",
        "The main implication is that LLM patch verification should be evaluated with explicit evidence boundaries. The same candidate patch may be treated differently when visible tests, regression checks, diagnostics, or deterministic tool summaries are introduced. Reporting only an aggregate accept/reject rate would hide this dependence.",
        "",
        "The results also clarify the role of escalation. Escalation can be useful for software-quality workflows because it routes risky cases away from autonomous acceptance. However, escalation is not strict correction. This distinction matters for deployment: a verifier that escalates risky candidates may reduce unsafe automation, but it has not proven semantic incorrectness.",
        "",
        "The strongest current contribution is methodological. EVP-8 provides a reproducible way to separate model-visible evidence from hidden evaluator labels, report accept/reject/escalate outcomes, and connect each claim to a validity gate. This is why the paper is framed as a protocol and measurement study rather than as a new repair or verification algorithm.",
        "",
        "Several reviewer concerns remain bounded rather than eliminated. The cohort is small, Wilson intervals are wide, Qwen v0.3 is the main repaired condition, majority-vote cannot be computed from the current tracked summaries, and the realistic hard-negative branch did not pass the three-project readiness gate. These are not hidden weaknesses; they are the boundary conditions under which the current claims are valid.",
        "",
        "![Figure 3. Claim boundary and setting-validity map.](../figures/ccfc/ccfc_fig3_claim_boundary.png)",
        "",
        f"**Figure 3. {figures['Fig. 3']['title']}.** {figures['Fig. 3']['conclusion']} The map separates supported claims from forbidden overclaims and shows why the realistic branch remains a boundary result.",
        "",
        "## 7. Threats to Validity",
        "",
        "**Internal validity.** Prompt wording, output schema, and evidence formatting may influence decisions. The study mitigates this risk through frozen packets, tracked prompt-boundary checks, parse-validity audits, raw-output-free summaries, and post-decision label joins. These controls reduce setup risk but do not make the results independent of the evaluated protocol versions.",
        "",
        "**Construct validity.** The accept/reject/escalate decision space simplifies real review workflows. Escalation is a routing outcome, not proof of semantic rejection. Hidden evaluator labels are used only for post-decision analysis and should not be interpreted as model-visible truth.",
        "",
        "**External validity.** The main evidence comes from a 98-candidate EVP-8 cohort, an EVP-8-HARD controlled cohort, and selected models. The realistic hard-negative branch did not pass its readiness gate. The results therefore support bounded evidence-conditioned risk behavior, not universal LLM patch-verifier reliability.",
        "",
        "**Baseline validity.** Rule-only visible-tool is the completed deterministic baseline. Always-* and uniform-random policies are reference policies. Majority-vote and a separate deterministic E0/no-tool verifier remain unavailable under the current tracked-summary boundary.",
        "",
        "## 8. Conclusion",
        "",
        "This paper introduces EVP-8 as a hidden-evaluator evidence-visibility protocol for LLM-based candidate patch verification. The repaired Qwen v0.3 result shows that visible executable and tool evidence can unlock correct-patch acceptance while retaining false-accept risk. E6 ablations and tool-contestation further show that verdict-like evidence can shape policy behavior and that safe handling often occurs through escalation rather than strict correction. The contribution is a reproducible software-engineering protocol for measuring evidence-conditioned risk behavior, not a claim of autonomous patch correctness verification.",
        "",
        "## Reference Support Records",
        "",
        "The current Markdown rewrite retains citation keys pending final BibTeX conversion for the target APSEC/IEEEtran submission.",
        "",
    ]
    for record in claim_map["reference_records"]:
        lines.append(f"- `{record['key']}`: {record['reference']}")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    claim_map = build_claim_map()
    write_apsec_markdown(args.out_md, claim_map)
    if args.check and claim_map["status"] != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
