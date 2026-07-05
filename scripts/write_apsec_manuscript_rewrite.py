"""Write an APSEC-style technical-track manuscript rewrite.

This script is no-API and raw-output-free. It reuses the tracked final claim
map generator and produces a conference-paper shaped Markdown draft while
preserving the existing stable CCF-C manuscript.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from write_final_manuscript_claim_map import build_claim_map, ci_percent, percent


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_MD = REPO_ROOT / "docs" / "paper" / "apsec_technical_track_rewrite_v0_1.md"
CANDIDATE_SET_SUMMARY = (
    REPO_ROOT / "data" / "protocols" / "evp8_candidate_set_v0_1_summary.json"
)
QWEN_LABEL_CONDITIONED_SUMMARY = (
    REPO_ROOT
    / "data"
    / "reviews"
    / "evp8_qwen_first_main_v0_3_prompt_v0_2_label_conditioned_summary.json"
)
DEEPSEEK_LABEL_CONDITIONED_SUMMARY = (
    REPO_ROOT
    / "data"
    / "reviews"
    / "evp8_deepseek_repaired_v0_3_prompt_v0_2_label_conditioned_summary.json"
)
GEMINI_LABEL_CONDITIONED_SUMMARY = (
    REPO_ROOT
    / "data"
    / "reviews"
    / "evp8_gemini_repaired_v0_3_prompt_v0_2_label_conditioned_summary.json"
)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


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


def label_conditioned_table(summary: dict[str, Any]) -> list[str]:
    lines = [
        "| level | accept | correct accept | false accept | accepted precision | correct recall | false accept rate | escalation rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for level in ["E0", "E1", "E2", "E3", "E4", "E5", "E6"]:
        row = summary["per_evidence_level"][level]
        confusion = row["confusion_counts"]
        lines.append(
            f"| {level} | {row['decision_counts'].get('accept', 0)} | {confusion['true_accept']} | {confusion['false_accept']} | "
            f"{percent(row.get('accepted_precision'))} | {percent(row.get('correct_recall'))} | "
            f"{percent(row.get('false_accept_rate'))} | {percent(row.get('escalation_rate'))} |"
        )
    return lines


def repaired_model_summary_table(
    *summaries: dict[str, Any],
) -> list[str]:
    lines = [
        "| model | E6 accept | E6 correct accept | E6 false accept | E6 accepted precision | E6 correct recall | E6 false accept rate | E6 escalation rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for summary in summaries:
        row = summary["per_evidence_level"]["E6"]
        confusion = row["confusion_counts"]
        lines.append(
            f"| {summary['model_id']} | {row['decision_counts'].get('accept', 0)} | {confusion['true_accept']} | {confusion['false_accept']} | "
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
    humanized = {
        "E0": ("Issue summary and candidate patch diff", "minimal review context"),
        "E1": (
            "Structured changed-file/function map",
            "patch surface information",
        ),
        "E2": (
            "Patch application and static-check status",
            "basic feasibility evidence",
        ),
        "E3": (
            "Visible fail-to-pass test results",
            "issue-relevant executable evidence",
        ),
        "E4": (
            "Visible pass-to-pass regression results",
            "regression-safety evidence",
        ),
        "E5": ("Additional diagnostics", "broader tool evidence"),
        "E6": (
            "Deterministic merge-gate summary",
            "summarized tool verdict",
        ),
    }
    lines = [
        "| level | visible evidence | meaning |",
        "| --- | --- | --- |",
    ]
    for row in claim_map["evidence_ladder"]:
        visible, meaning = humanized[row["level"]]
        lines.append(
            f"| {row['level']} | {visible} | {meaning} |"
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


def candidate_composition_table(
    candidate_summary: dict[str, Any], label_summary: dict[str, Any]
) -> list[str]:
    candidate_counts = candidate_summary["aggregate_candidate_type_counts"]
    label_counts = candidate_summary["aggregate_p2p_label_counts"]
    rows = [
        (
            "correct_reference",
            candidate_counts["correct_reference"],
            "correct_under_f2p_and_p2p_broad",
            label_counts["correct_under_f2p_and_p2p_broad"],
            "hidden F2P and P2P-broad evaluator labels",
            "measure correct-patch recall",
        ),
        (
            "buggy_noop",
            candidate_counts["buggy_noop"],
            "incorrect_issue_not_fixed",
            "",
            "hidden evaluator labels",
            "issue-not-fixed false-accept risk",
        ),
        (
            "irrelevant_patch",
            candidate_counts["irrelevant_patch"],
            "incorrect_issue_not_fixed",
            "",
            "hidden evaluator labels",
            "plausibility-trap negative patches",
        ),
        (
            "partial_fix",
            candidate_counts["partial_fix"],
            "incorrect_issue_not_fixed",
            "",
            "hidden F2P and P2P-broad evaluator labels",
            "semantic incompleteness and partial repair risk",
        ),
        (
            "regression_patch",
            candidate_counts["regression_patch"],
            "incorrect_regression",
            label_counts["incorrect_regression"],
            "P2P-broad regression label",
            "regression-safety risk",
        ),
    ]
    incorrect_total = label_summary["label_distribution"]["incorrect_count"]
    rows[1] = (
        rows[1][0],
        rows[1][1],
        rows[1][2],
        f"part of {incorrect_total - label_counts['incorrect_regression']} issue-not-fixed negatives",
        rows[1][4],
        rows[1][5],
    )
    rows[2] = (
        rows[2][0],
        rows[2][1],
        rows[2][2],
        f"part of {incorrect_total - label_counts['incorrect_regression']} issue-not-fixed negatives",
        rows[2][4],
        rows[2][5],
    )
    rows[3] = (
        rows[3][0],
        rows[3][1],
        rows[3][2],
        f"part of {incorrect_total - label_counts['incorrect_regression']} issue-not-fixed negatives",
        rows[3][4],
        rows[3][5],
    )

    lines = [
        "| candidate type | count | evaluator label | label count | label source | purpose |",
        "| --- | ---: | --- | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} |")
    return lines


def false_accept_anatomy_table(*summaries: dict[str, Any]) -> list[str]:
    lines = [
        "| model | partial_fix accepts | regression_patch accepts | total E6 false accepts | what the failure shows |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for summary in summaries:
        e6 = summary["breakdowns_by_evidence_level"]["E6"]["candidate_type"]
        partial_accept = e6["partial_fix"]["decision_counts"].get("accept", 0)
        regression_accept = e6["regression_patch"]["decision_counts"].get("accept", 0)
        total_false_accept = (
            summary["per_evidence_level"]["E6"]["confusion_counts"]["false_accept"]
        )
        lines.append(
            f"| {summary['model_id']} | {partial_accept}/41 | {regression_accept}/1 | {total_false_accept} | semantic incompleteness and regression-safety failures remain visible-evidence risks |"
        )
    return lines


def write_apsec_markdown(path: Path, claim_map: dict[str, Any]) -> None:
    candidate_summary = read_json(CANDIDATE_SET_SUMMARY)
    label_summary = read_json(QWEN_LABEL_CONDITIONED_SUMMARY)
    deepseek_label_summary = read_json(DEEPSEEK_LABEL_CONDITIONED_SUMMARY)
    gemini_label_summary = read_json(GEMINI_LABEL_CONDITIONED_SUMMARY)
    qwen_opp = claim_map["hard_tool_contestation_summary"]["qwen_opportunity"]
    deepseek_opp = claim_map["hard_tool_contestation_summary"][
        "deepseek_opportunity"
    ]
    realistic = claim_map["realistic_gate_summary"]
    figures = {figure["id"]: figure for figure in claim_map["figure_plan"]}
    label_distribution = label_summary["label_distribution"]

    lines = [
        "# Evidence Visibility Shapes Risk Behavior in a Controlled LLM Patch-Verifier Study",
        "",
        "Draft status: APSEC technical-track Markdown rewrite v0.1, 2026-07-05.",
        "",
        "Target format note: this draft is shaped for an APSEC-style technical research paper. The companion IEEEtran/BibTeX/page-budget draft package is generated separately; this Markdown file is not the final PDF.",
        "",
        "## Abstract",
        "",
        "Patch-verification decisions made by large language models (LLMs) are meaningful only relative to the evidence visible at review time. Existing evaluations often report whether an LLM accepts or rejects a patch without making this evidence boundary explicit, which makes it difficult to separate model capability from visible-test evidence, tool-summary anchoring, or prompt-induced caution. This paper introduces the Evidence-Visibility Protocol (EVP-8), a hidden-evaluator protocol for candidate patch verification. EVP-8 reviews 98 candidate patches across seven cumulative evidence levels while withholding evaluator-only correctness labels until post-decision analysis. In three repaired v0.3 runs, Qwen reached 95.24% E6 correct recall with 83.33% accepted precision, DeepSeek reached 80.95% E6 correct recall with 80.95% accepted precision, and Gemini reached 95.24% E6 correct recall with 80.00% accepted precision. The three models still accepted 4-5 of 77 non-correct candidates at E6. E6 rule-only and no-verdict ablations show that verdict-like tool summaries can anchor policy behavior, and tool-contestation moved known tool false accepts mainly to escalation rather than strict rejection. These results support a bounded software-engineering claim: in this controlled LLM patch-verifier study, evidence visibility should be treated as an experimental variable for risk control, not as proof of general autonomous correctness verification.",
        "",
        "## 1. Introduction",
        "",
        "Automated patch generation and LLM-assisted review are increasingly positioned near software merge decisions. This creates a practical software-quality question: when a candidate patch appears plausible, which visible evidence is sufficient for a verifier to accept it rather than reject it or escalate it for human review? Prior automated program repair work has shown that plausible or test-passing patches can still be incorrect [qi_issta_2015_patch_plausibility; legoues_icse_2012_genprog], so a merge decision cannot be reduced to surface plausibility alone.",
        "",
        "The difficulty is not only whether an LLM can read code. It is that a verifier's decision may change when issue context, patch structure, static status, visible tests, regression checks, diagnostics, or tool summaries become visible. If these evidence fields are not controlled, an evaluation may conflate model judgment with evidence presentation. In particular, authoritative-looking tool summaries can encourage acceptance even when the underlying semantic correctness remains unknown.",
        "",
        "This paper studies candidate patch verification as an evidence-conditioned merge-gate task. A verifier receives a candidate patch and a predefined model-visible evidence packet, then emits one of three decisions: accept, reject, or escalate. Correctness labels and hidden evaluator outcomes are joined only after the decision. This design follows the intuition behind reject-option and selective-classification settings [chow_tit_1970_reject_option; geifman_el_yaniv_2017_selective_classification], but applies it to software patch verification. The current empirical scope is intentionally controlled: the paper-facing main result is a three-model repaired v0.3 analysis for Qwen, DeepSeek, and Gemini, supported by E6 ablations and tool-contestation evidence, rather than a broad claim about all LLM verifiers.",
        "",
        "The paper makes three contributions:",
        "",
        "- It defines EVP-8, a hidden-evaluator evidence-visibility protocol for measuring accept, reject, and escalation behavior in candidate patch verification.",
        "- It reports repaired Qwen, DeepSeek, and Gemini v0.3 label-conditioned results showing that visible executable and tool evidence can unlock correct-patch acceptance while introducing bounded false-accept risk.",
        "- It analyzes E6 rule-only, no-verdict, and tool-contestation conditions to separate deterministic tool evidence, verdict-like anchoring, safe handling, and strict correction.",
        "",
        "The claim is deliberately bounded. The results do not establish reliable autonomous patch correctness verification, nor do they show that LLM decisions consistently outperform deterministic baselines. They show that evidence visibility is a measurable experimental variable that should be controlled and reported in LLM patch-verifier studies.",
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
        f"The current packet set contains {candidate_summary['candidate_count']} candidate patches from {candidate_summary['project_count']} projects and {candidate_summary['task_count']} BugsInPy tasks. It contains {label_distribution['correct_count']} correct patches and {label_distribution['incorrect_count']} non-correct patches under hidden F2P/P2P-broad evaluator labels. The candidate mix is intentionally skewed toward negative and partial cases because the merge-gate risk is false acceptance rather than classification accuracy on a balanced benchmark.",
        "",
        *candidate_composition_table(candidate_summary, label_summary),
        "",
        "Five selected models produced complete parse-valid decisions on an earlier frozen E0-E6 packet set, but the paper-facing main result now uses repaired Qwen, DeepSeek, and Gemini v0.3 label-conditioned analyses plus the E6 ablation package. The earlier five-model aggregate synthesis is used only descriptively and not as evidence of final model superiority. The repaired three-model main table removes the previous single-/two-model visibility weakness, but it still does not prove broad LLM superiority over deterministic tool summaries.",
        "",
        "## 4. Experimental Design",
        "",
        "The experiment asks three research questions. RQ1 asks whether repaired accept-aware evidence changes Qwen, DeepSeek, and Gemini label-conditioned decisions across E0-E6. RQ2 asks whether verdict-like deterministic tool summaries anchor E6 decisions. RQ3 asks whether explicit tool-contestation can challenge visible-test-only accept premises. The fresh realistic hard-negative branch is not treated as a main research question because it did not pass its predeclared source-acquisition gate; it is reported later as a boundary condition.",
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
        "### 5.1 Visible executable evidence changed three repaired model policies",
        "",
        "In the repaired Qwen, DeepSeek, and Gemini v0.3 runs, E0-E2 produced no accepted correct patches for Qwen and DeepSeek and only a single incorrect Gemini accept at E1. Once visible executable evidence entered the packet, all three models began accepting correct patches, but their risk policies diverged. Qwen reached 80.95% correct recall at E3 and 95.24% at E6. DeepSeek reached 61.90% correct recall at E3, became more conservative at E4-E5, and reached 80.95% at E6. Gemini reached 95.24% correct recall from E3 through E6, but accepted five of 77 non-correct candidates at E6. The repaired three-model table therefore strengthens the evidence-visibility finding while preserving the false-accept risk boundary.",
        "",
        *repaired_model_summary_table(label_summary, deepseek_label_summary, gemini_label_summary),
        "",
        "Qwen level-conditioned metrics:",
        "",
        *label_conditioned_table(label_summary),
        "",
        "DeepSeek level-conditioned metrics:",
        "",
        *label_conditioned_table(deepseek_label_summary),
        "",
        "Gemini level-conditioned metrics:",
        "",
        *label_conditioned_table(gemini_label_summary),
        "",
        "![Figure 2. Accept-aware and no-verdict metric evidence.](../figures/ccfc/ccfc_fig2_decision_patterns.png)",
        "",
        f"**Figure 2. {figures['Fig. 2']['title']}.** {figures['Fig. 2']['conclusion']} The figure emphasizes the main tradeoff: more visible evidence enabled correct accepts, but acceptance remained bounded by false-accept risk.",
        "",
        "The three-model result supports an evidence-visibility claim, not a monotonic correctness claim. More evidence changed policy behavior and unlocked acceptance, but DeepSeek's E4-E5 conservatism and the shared partial/regression false accepts show that visible evidence did not become a correctness oracle.",
        "",
        "### 5.2 Verdict-like evidence affected policy behavior",
        "",
        "The E6 ablation is a separate verdict-field ablation package rather than the repaired v0.3 E0-E6 main table. It compares the deterministic rule-only visible-tool baseline, full E6 model conditions, and E6-no-verdict conditions to test whether model decisions add value beyond following visible tool verdict fields. Therefore, the DeepSeek E6-full row below should be read as ablation evidence, while the repaired v0.3 DeepSeek E6 row in Section 5.1 is the main E0-E6 evidence-visibility result.",
        "",
        *metric_table(claim_map["e6_ablation_metrics"]),
        "",
        "Qwen E6-full and rule-only produced similar correct recall, accepted precision, and false accept rates. Qwen E6-no-verdict remained close to Qwen E6-full. DeepSeek E6-no-verdict removed false accepts in this cohort, but correct recall dropped to 52.38% and escalation increased to 14.29%. The safer behavior therefore appears to be partly abstention-driven rather than strict semantic discrimination.",
        "",
        "This is an important negative result for the LLM-verifier claim. The deterministic rule-only baseline was already strong: it reached 95.24% correct recall and 80.00% accepted precision, compared with 95.24% and 83.33% for Qwen E6-full. The current evidence therefore does not justify claiming a large LLM gain over the tool summary. The value of the LLM conditions in this draft is narrower: they expose how model policy changes when verdict-like fields are removed or challenged, and they show whether risky accepts are routed to escalation rather than autonomous acceptance.",
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
        "### 5.4 E6 false accepts were concentrated in partial and regression negatives",
        "",
        "The most important failure mode is not the average E6 score but the remaining E6 false accepts among 77 non-correct candidates. Aggregate false-accept anatomy shows that Qwen and DeepSeek each accepted three partial fixes and one regression patch, while Gemini accepted four partial fixes and one regression patch. This breakdown supports the paper's risk framing: visible executable and tool evidence can unlock correct accepts, but summarized tool evidence can still miss semantic incompleteness and regression-safety failures. It remains aggregate anatomy, not a case-level project or rationale table.",
        "",
        *false_accept_anatomy_table(label_summary, deepseek_label_summary, gemini_label_summary),
        "",
        "A sanitized case-level analysis is now available for these model-specific false accepts. It records candidate id, project, task, negative type, E6 decision, no-verdict decision where available, and compressed rationale categories, but excludes raw response text, full rationale text, rendered prompts, patch diffs, and credentials. The case rows show repeated risk concentration in the same regression case and several youtube-dl partial fixes; they support failure anatomy, not a claim that the complete model rationale has been audited semantically.",
        "",
        "### 5.5 Realistic hard-negative acquisition remained a boundary",
        "",
        f"The fresh realistic branch produced {realistic.get('visible_pass_hidden_fail_count')} visible-pass/hidden-fail cases across {len(realistic.get('visible_pass_hidden_fail_projects') or [])} projects. This missed the predeclared verifier-readiness gate of {realistic.get('minimum_count')} cases across {realistic.get('minimum_projects')} projects. The branch is therefore reported as a source-acquisition boundary rather than a main verifier experiment.",
        "",
        "## 6. Discussion",
        "",
        "The main implication is that LLM patch verification should be evaluated with explicit evidence boundaries. The same candidate patch may be treated differently when visible tests, regression checks, diagnostics, or deterministic tool summaries are introduced. Reporting only an aggregate accept/reject rate would hide this dependence.",
        "",
        "The results also clarify the role of escalation. Escalation can be useful for software-quality workflows because it routes risky cases away from autonomous acceptance. However, escalation is not strict correction. This distinction matters for deployment: a verifier that escalates risky candidates may reduce unsafe automation, but it has not proven semantic incorrectness.",
        "",
        "The strongest current contribution is methodological. EVP-8 provides a reproducible way to separate model-visible evidence from hidden evaluator labels, report accept/reject/escalate outcomes, and connect each claim to a validity gate. This is why the paper is framed as a controlled protocol and measurement study rather than as a new repair or verification algorithm.",
        "",
        "Several reviewer concerns remain bounded rather than eliminated. The cohort is small, Wilson intervals are wide, repaired Qwen, DeepSeek, and Gemini are the main model conditions, majority-vote cannot be computed from the current tracked summaries, and the realistic hard-negative branch did not pass the three-project readiness gate. Most importantly, the current paper-facing main result is three-model but still not broad-model. These are not hidden weaknesses; they are the boundary conditions under which the current claims are valid.",
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
        "**External validity.** The main evidence comes from a 98-candidate EVP-8 cohort, an EVP-8-HARD controlled cohort, and selected model conditions. The repaired E0-E6 main result now covers Qwen, DeepSeek, and Gemini, but it is still not a broad-model result, and the realistic hard-negative branch did not pass its readiness gate. The results therefore support bounded evidence-conditioned risk behavior in a controlled patch-verifier study, not universal LLM patch-verifier reliability.",
        "",
        "**Baseline validity.** Rule-only visible-tool is the completed deterministic baseline. Always-* and uniform-random policies are reference policies. Majority-vote and a separate deterministic E0/no-tool verifier remain unavailable under the current tracked-summary boundary.",
        "",
        "## 8. Conclusion",
        "",
        "This paper introduces EVP-8 as a hidden-evaluator evidence-visibility protocol for candidate patch verification. The repaired Qwen, DeepSeek, and Gemini v0.3 results show that visible executable and tool evidence can unlock correct-patch acceptance while retaining false-accept risk and model-dependent caution. E6 ablations and tool-contestation further show that verdict-like evidence can shape policy behavior and that safe handling often occurs through escalation rather than strict correction. The contribution is a reproducible software-engineering protocol for measuring evidence-conditioned risk behavior in a controlled LLM patch-verifier study, not a claim of autonomous patch correctness verification.",
        "",
        "The companion IEEEtran/BibTeX/page-budget draft package converts these citation keys into a draft reference file; final submission still requires BibTeX field normalization, PDF compilation, visual page-budget inspection, and double-blind checks.",
        "",
    ]
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
