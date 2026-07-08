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
COVERAGE_CONTESTATION_ANALYSIS = (
    REPO_ROOT
    / "data"
    / "reviews"
    / "evp8_coverage_contestation_current98_analysis_v0_1.json"
)
STRESS_MATRIX_ANALYSIS = (
    REPO_ROOT
    / "data"
    / "reviews"
    / "evp8_realistic_hardneg_stress_matrix_analysis_v0_1.json"
)
FALSE_ACCEPT_CASE_ANALYSIS = (
    REPO_ROOT / "data" / "reviews" / "apsec_false_accept_case_analysis_v0_2.json"
)


MODEL_NAMES = {
    "qwen/qwen3.7-max": "Qwen",
    "deepseek/deepseek-v4-pro": "DeepSeek",
    "google/gemini-2.5-flash": "Gemini",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def model_name(model_id: str) -> str:
    return MODEL_NAMES.get(model_id, model_id)


def condition_name(condition: str) -> str:
    replacements = {
        "rule-only": "Rule-only visible-tool",
        "deepseek/deepseek-v4-pro E6-full": "DeepSeek E6-full",
        "deepseek/deepseek-v4-pro E6-no-verdict": "DeepSeek E6-no-verdict",
        "qwen/qwen3.7-max E6-full": "Qwen E6-full",
        "qwen/qwen3.7-max E6-no-verdict": "Qwen E6-no-verdict",
    }
    return replacements.get(condition, condition)


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
            f"| {condition_name(row['condition'])} | {accept} | {reject} | {escalate} | "
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


def repaired_selected_levels_table(*summaries: dict[str, Any]) -> list[str]:
    lines = [
        "| model | level | accept | correct accept | false accept | accepted precision | correct recall | false accept rate | escalation rate |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for summary in summaries:
        for level in ["E0", "E3", "E6"]:
            row = summary["per_evidence_level"][level]
            confusion = row["confusion_counts"]
            lines.append(
                f"| {model_name(summary['model_id'])} | {level} | "
                f"{row['decision_counts'].get('accept', 0)} | "
                f"{confusion['true_accept']} | {confusion['false_accept']} | "
                f"{percent(row.get('accepted_precision'))} | "
                f"{percent(row.get('correct_recall'))} | "
                f"{percent(row.get('false_accept_rate'))} | "
                f"{percent(row.get('escalation_rate'))} |"
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


def coverage_contestation_table(analysis: dict[str, Any]) -> list[str]:
    lines = [
        "| model | accept | reject | escalate | repeated false accept | strict reject on wrong | safe escalation on wrong | correct recall | correct recall loss |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for model_id, row in analysis["model_summaries"].items():
        decisions = row.get("decision_counts", {})
        lines.append(
            f"| {model_name(model_id)} | {decisions.get('accept', 0)} | {decisions.get('reject', 0)} | {decisions.get('escalate', 0)} | "
            f"{percent(row.get('repeated_false_accept_rate_on_incorrect'))} | "
            f"{percent(row.get('strict_reject_rate_on_incorrect'))} | "
            f"{percent(row.get('safe_escalation_rate_on_incorrect'))} | "
            f"{percent(row.get('correct_recall'))} | {percent(row.get('correct_recall_loss'))} |"
        )
    return lines


def stress_matrix_aggregate_table(analysis: dict[str, Any]) -> list[str]:
    lines = [
        "| condition | records | repeated false accepts | strict rejects | safe escalations | safe handling |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    labels = {
        "current_merge_gate": "Current prompt",
        "coverage_contestation": "Coverage prompt",
    }
    for condition in ("current_merge_gate", "coverage_contestation"):
        row = analysis["aggregate_by_condition"][condition]
        lines.append(
            f"| {labels[condition]} | {row['record_count']} | "
            f"{row['repeated_false_accept_count']} ({percent(row['repeated_false_accept_rate'])}) | "
            f"{row['strict_reject_count']} ({percent(row['strict_reject_rate'])}) | "
            f"{row['safe_escalation_count']} ({percent(row['safe_escalation_rate'])}) | "
            f"{row['safe_handling_count']} ({percent(row['safe_handling_rate'])}) |"
        )
    return lines


def stress_matrix_model_table(analysis: dict[str, Any]) -> list[str]:
    lines = [
        "| condition | model | accept | reject | escalate | safe handling |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for condition in ("current_merge_gate", "coverage_contestation"):
        models = analysis["per_condition_model"][condition]
        for model, payload in models.items():
            row = payload["metrics"]
            decisions = row["decision_counts"]
            lines.append(
                f"| {condition} | {model} | {decisions.get('accept', 0)} | "
                f"{decisions.get('reject', 0)} | {decisions.get('escalate', 0)} | "
                f"{row['safe_handling_count']} ({percent(row['safe_handling_rate'])}) |"
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
    rows = [
        (
            "Correct reference",
            candidate_counts["correct_reference"],
            "correct",
            "correct-patch recall",
        ),
        (
            "Buggy no-op",
            candidate_counts["buggy_noop"],
            "Issue not fixed",
            "obvious negative",
        ),
        (
            "Irrelevant patch",
            candidate_counts["irrelevant_patch"],
            "Issue not fixed",
            "plausibility trap",
        ),
        (
            "Partial fix",
            candidate_counts["partial_fix"],
            "Issue not fixed",
            "semantic incompleteness",
        ),
        (
            "Regression patch",
            candidate_counts["regression_patch"],
            "regression",
            "regression risk",
        ),
    ]

    lines = [
        "| candidate type | count | hidden label | purpose |",
        "| --- | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} |")
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
            f"| {model_name(summary['model_id'])} | {partial_accept}/41 | {regression_accept}/1 | {total_false_accept} | semantic incompleteness and regression-safety failures remain visible-evidence risks |"
        )
    return lines


def false_accept_case_group_table(case_analysis: dict[str, Any]) -> list[str]:
    grouped: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in case_analysis["case_rows"]:
        key = (
            row["project"],
            row["task_id"].replace("bugsinpy_", ""),
            row["candidate_type"],
        )
        bucket = grouped.setdefault(
            key,
            {"models": set(), "rationales": set()},
        )
        bucket["models"].add(model_name(row["model"]))
        bucket["rationales"].add(row["rationale_category"])

    lines = [
        "| project/task | negative type | models accepting | likely cause |",
        "| --- | --- | --- | --- |",
    ]
    type_labels = {
        "regression_patch": "Regression patch",
        "partial_fix": "Partial fix",
    }
    for (project, task, candidate_type), payload in sorted(grouped.items()):
        rationales = payload["rationales"]
        if candidate_type == "regression_patch":
            cause = "visible E6 evidence missed a hidden P2P-broad regression"
        elif "accepted_due_to_visible_test_success" in rationales:
            cause = "visible tests encouraged acceptance despite partial semantic repair"
        else:
            cause = "merge-gate summary did not expose the remaining semantic gap"
        lines.append(
            f"| {project} / {task} | {type_labels.get(candidate_type, candidate_type)} | "
            f"{', '.join(sorted(payload['models']))} | {cause} |"
        )
    return lines


def write_apsec_markdown(path: Path, claim_map: dict[str, Any]) -> None:
    candidate_summary = read_json(CANDIDATE_SET_SUMMARY)
    label_summary = read_json(QWEN_LABEL_CONDITIONED_SUMMARY)
    deepseek_label_summary = read_json(DEEPSEEK_LABEL_CONDITIONED_SUMMARY)
    gemini_label_summary = read_json(GEMINI_LABEL_CONDITIONED_SUMMARY)
    coverage_contestation = read_json(COVERAGE_CONTESTATION_ANALYSIS)
    stress_matrix = read_json(STRESS_MATRIX_ANALYSIS)
    false_accept_cases = read_json(FALSE_ACCEPT_CASE_ANALYSIS)
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
        "Target format note: this draft is shaped for an APSEC-style technical research paper. The IEEEtran source package is generated separately; this Markdown file is not the final PDF.",
        "",
        "## Abstract",
        "",
        "Patch-verification decisions made by large language models (LLMs) are meaningful only relative to the evidence visible at review time. Existing evaluations often report whether an LLM accepts or rejects a patch without making this evidence boundary explicit, which makes it difficult to separate model capability from visible-test evidence, tool-summary anchoring, or prompt-induced caution. This paper introduces the Evidence-Visibility Protocol (EVP-8), a hidden-evaluator protocol for candidate patch verification. EVP-8 reviews 98 candidate patches across seven cumulative evidence levels while withholding evaluator-only correctness labels until post-decision analysis. In three repaired v0.3 runs, Qwen reached 95.24% E6 correct recall with 83.33% accepted precision, DeepSeek reached 80.95% E6 correct recall with 80.95% accepted precision, and Gemini reached 95.24% E6 correct recall with 80.00% accepted precision. The three models still accepted 4-5 of 77 non-correct candidates at E6. E6 ablations and contestation tests show that prompt framing can shift decisions toward tool-following, abstention, or risk routing; a supplemental 31-case hard-negative stress matrix confirms that safer handling can come through escalation rather than strict rejection. These results support a bounded software-engineering claim: EVP-8 reveals when LLM patch verifiers behave as tool followers, abstainers, or risk routers under explicit evidence boundaries, not whether they provide general autonomous correctness verification.",
        "",
        "## 1. Introduction",
        "",
        "Automated patch generation and LLM-assisted review are increasingly positioned near software merge decisions. This creates a practical software-quality question: when a candidate patch appears plausible, which visible evidence is sufficient for a verifier to accept it rather than reject it or escalate it for human review? Prior automated program repair work has shown that plausible or test-passing patches can still be incorrect [qi_issta_2015_patch_plausibility; legoues_icse_2012_genprog], so a merge decision cannot be reduced to surface plausibility alone.",
        "",
        "The difficulty is not only whether an LLM can read code. It is that a verifier's decision may change when issue context, patch structure, static status, visible tests, regression checks, diagnostics, or tool summaries become visible. If these evidence fields are not controlled, an evaluation may conflate model judgment with evidence presentation. In particular, authoritative-looking tool summaries can encourage acceptance even when the underlying semantic correctness remains unknown.",
        "",
        "This paper studies candidate patch verification as an evidence-conditioned merge-gate task. A verifier receives a candidate patch and a predefined model-visible evidence packet, then emits one of three decisions: accept, reject, or escalate. Correctness labels and hidden evaluator outcomes are joined only after the decision. This design follows the intuition behind reject-option and selective-classification settings [chow_tit_1970_reject_option; cortes_jmlr_2016_reject_option; geifman_el_yaniv_2017_selective_classification], but applies it to software patch verification. The current empirical scope is intentionally controlled: the paper-facing main result is a three-model repaired v0.3 analysis for Qwen, DeepSeek, and Gemini, supported by E6 ablations and tool-contestation evidence, rather than a broad claim about all LLM verifiers.",
        "",
        "The paper makes three contributions:",
        "",
        "- It defines EVP-8, a hidden-evaluator evidence-visibility protocol for measuring accept, reject, and escalation behavior in candidate patch verification.",
        "- It reports repaired Qwen, DeepSeek, and Gemini v0.3 label-conditioned results showing that visible executable and tool evidence can unlock correct-patch acceptance while introducing bounded false-accept risk.",
        "- It analyzes E6 rule-only, no-verdict, tool-contestation, coverage-contestation, and hard-negative stress-test conditions to separate deterministic tool evidence, verdict-like anchoring, safe handling, strict correction, and prompt-induced conservatism.",
        "",
        "The claim is deliberately bounded. The results do not establish reliable autonomous patch correctness verification, nor do they show that LLM decisions consistently outperform deterministic baselines. They show that evidence visibility is a measurable experimental variable that should be controlled and reported in LLM patch-verifier studies.",
        "",
        "## 2. Background and Motivation",
        "",
        "Automated program repair research has long distinguished plausible patches from correct patches. Generate-and-validate and semantic-repair systems make this distinction visible, while controlled benchmarks expose why available tests are not complete correctness oracles [qi_issta_2015_patch_plausibility; long_popl_2016_prophet; long_fse_2015_spr; nguyen_icse_2013_semfix; smith_fse_2015_overfitting; just_issta_2014_defects4j; widyasari_fse_2020_bugsinpy; durieux_saner_2019_bears; lin_splash_2017_quixbugs]. EVP-8 studies the downstream verifier setting: after a candidate patch exists, the question is not how it was generated, but whether a merge-gate decision is justified by the evidence visible to the verifier.",
        "",
        "Software testing research also motivates the hidden-evaluator design. The oracle problem means that deciding correctness is itself a validity boundary [barr_tse_2015_oracle_problem]. EVP-8 therefore keeps evaluator-only labels separate from model-visible evidence and joins them only after decisions have been produced.",
        "",
        "LLM-based repair, code generation, and code-editing studies show that LLMs can produce or inspect patches [xia_zhang_icse_2023_llm_apr; tufano_icse_2019_bugfix_nmt; chen_arxiv_2021_codex; joshi_arxiv_2022_repair_is_nearly_generation]. However, verifier behavior is not identical to generation performance. A patch reviewer must decide whether visible evidence is enough to accept, reject, or escalate. This makes the task closer to code review and risk triage than to benchmark success alone [bacchelli_bird_icse_2013_code_review; li_fse_2022_codereviewer].",
        "",
        "Recent software-agent benchmarks further show why task framing and evaluation protocol matter for code-oriented LLM systems [jimenez_iclr_2024_swebench; yang_neurips_2024_sweagent]. Finally, LLM-as-judge and automation-reliance work warn that model judgments and automation outputs require controlled protocols and explicit boundaries [zheng_neurips_2023_llm_judge; wang_acl_2024_not_fair_evaluators; parasuraman_riley_1997_automation]. The protocol in this paper responds to that concern by making evidence visibility an explicit variable rather than an implicit property of the prompt.",
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
        f"The current packet set contains {candidate_summary['candidate_count']} candidate patches from {candidate_summary['project_count']} projects and {candidate_summary['task_count']} BugsInPy tasks [widyasari_fse_2020_bugsinpy]. It contains {label_distribution['correct_count']} correct patches and {label_distribution['incorrect_count']} non-correct patches under hidden F2P/P2P-broad evaluator labels. The candidate mix is intentionally skewed toward negative and partial cases because the merge-gate risk is false acceptance rather than classification accuracy on a balanced benchmark.",
        "",
        *candidate_composition_table(candidate_summary, label_summary),
        "",
        "The 76 issue-not-fixed negatives plus one regression negative form the 77 non-correct candidates. Project counts are PySnooper 10, cookiecutter 19, httpie 6, thefuck 4, tqdm 7, and youtube-dl 52.",
        "",
        "Five selected models produced complete parse-valid decisions on an earlier frozen E0-E6 packet set, but the paper-facing main result now uses repaired Qwen, DeepSeek, and Gemini v0.3 label-conditioned analyses plus the E6 ablation package. The earlier five-model aggregate synthesis is used only descriptively and not as evidence of final model superiority. The repaired three-model main table removes the previous single-/two-model visibility weakness, but it still does not prove broad LLM superiority over deterministic tool summaries.",
        "",
        "## 4. Experimental Design",
        "",
        "The experiment asks three research questions. RQ1 asks whether repaired accept-aware evidence changes Qwen, DeepSeek, and Gemini label-conditioned decisions across E0-E6. RQ2 asks whether verdict-like deterministic tool summaries anchor E6 decisions. RQ3 asks: when visible evidence is challenged, do models correct wrong accepts or route them to escalation? Tool-contestation, current-98 coverage-contestation, and the hard-negative stress matrix are three evidence sources for RQ3 rather than separate main questions. The hard-negative stress matrix remains a supplemental stress test because its third project comes from curated no-API stress-source variants, not a pure agent-generated realistic cohort.",
        "",
        "All metrics are computed after post-decision hidden-label join. The main metrics are accepted precision, correct recall, false accept rate, false reject rate, and escalation rate. Accepted precision measures the correctness of accepted patches. Correct recall measures how many correct patches were accepted. False accept rate measures how often non-correct candidates were accepted. Escalation rate measures routing to human review.",
        "",
        "The baseline boundary is explicit. Always-escalate, always-reject, and always-accept are deterministic reference policies calculated from label totals. Uniform random three-way is an expected reference policy, not a stochastic experiment. The completed deterministic baseline is rule-only visible-tool. Qwen E0 is an observed model condition, not a deterministic no-tool verifier. Majority-vote and a separate E0/no-tool deterministic verifier are not reported as completed because current tracked summaries do not contain candidate-level aligned decision records.",
        "",
        "### 4.1 Implementation and artifact boundary",
        "",
        "All repaired main runs used the same frozen prompt template, `evp8_visible_evidence_merge_gate_v0_2`, the same E0-E6 packet construction, temperature 0.0, and a 4096-token output cap. The three repaired full runs each produced 686 parse-valid records, covering 98 candidates across seven levels. Parse validity required a schema-conforming accept, reject, or escalate decision with required structured fields; invalid JSON or missing decisions were execution-chain failures, not model decisions. Cost telemetry was tracked when available, but cost comparison is not used as a paper-facing claim. The paper-facing artifacts are raw-output-free summaries, scripts, generated packets, audits, and anonymized aggregate tables; raw provider responses, rendered prompts, patch diffs, local configs, and credentials remain excluded from tracked outputs.",
        "",
        "All paper-facing claims are constrained by a setting-validity audit. The audit checks run coverage, parse validity, raw-output-free summaries, post-execution label joins, prompt-boundary conditions, baseline feasibility, and exclusion of the earlier invalid setting. The audit passed only for bounded claims.",
        "",
        "## 5. Results",
        "",
        "### 5.1 Visible executable evidence changed three repaired model policies",
        "",
        "In the repaired Qwen, DeepSeek, and Gemini v0.3 runs, E0-E2 produced no accepted correct patches for Qwen and DeepSeek and only a single incorrect Gemini accept at E1. Once visible executable evidence entered the packet, all three models began accepting correct patches, but their risk policies diverged. Qwen reached 80.95% correct recall at E3 and 95.24% at E6. DeepSeek reached 61.90% correct recall at E3 and 80.95% at E6. Gemini reached 95.24% correct recall from E3 through E6, but accepted five of 77 non-correct candidates at E6. The repaired three-model table therefore strengthens the evidence-visibility finding while preserving the false-accept risk boundary.",
        "",
        *repaired_selected_levels_table(label_summary, deepseek_label_summary, gemini_label_summary),
        "",
        "![Figure 2. Three-model repaired evidence metrics.](../figures/ccfc/ccfc_fig2_decision_patterns.png)",
        "",
        "**Figure 2. Three-model repaired evidence metrics.** The figure compares Qwen, DeepSeek, and Gemini at E0, E3, and E6 for correct recall, false accept rate, and escalation rate. It summarizes the main evidence-visibility result while leaving the complete E0-E6 curves to the artifact.",
        "",
        "The three-model result supports an evidence-visibility claim, not a monotonic correctness claim. More evidence changed policy behavior and unlocked acceptance, but intermediate-level non-monotonic behavior in the full artifact and the shared partial/regression false accepts show that visible evidence did not become a correctness oracle.",
        "",
        "### 5.2 Verdict-like evidence affected policy behavior",
        "",
        "The E6 ablation is a separate verdict-field ablation package rather than the repaired v0.3 E0-E6 main table. It compares the deterministic rule-only visible-tool baseline, full E6 model conditions, and E6-no-verdict conditions to test whether model decisions add value beyond following visible tool verdict fields. Therefore, the DeepSeek E6-full row below should be read as ablation evidence, while the repaired v0.3 DeepSeek E6 row in Section 5.1 is the main E0-E6 evidence-visibility result.",
        "",
        *metric_table(claim_map["e6_ablation_metrics"]),
        "",
        "Qwen E6-full and rule-only produced similar correct recall, accepted precision, and false accept rates. Qwen E6-no-verdict remained close to Qwen E6-full. DeepSeek E6-no-verdict removed false accepts in this cohort, but correct recall dropped to 52.38% and escalation increased to 14.29%. The safer behavior therefore appears to be partly abstention-driven rather than strict semantic discrimination.",
        "",
        "This is an important negative result for the LLM-verifier claim. The deterministic rule-only baseline was already strong: it reached 95.24% correct recall and 80.00% accepted precision, compared with 95.24% and 83.33% for Qwen E6-full. The goal of EVP-8 is not to show that LLMs dominate rule-only tool summaries, but to expose when LLM decisions collapse into tool-following, abstention, or prompt-induced conservatism. The current evidence therefore does not justify claiming a large LLM gain over the tool summary. The value of the LLM conditions in this draft is narrower: they expose how model policy changes when verdict-like fields are removed or challenged, and they show whether risky accepts are routed to escalation rather than autonomous acceptance.",
        "",
        "The Wilson intervals are wide, so the ablation should be read as bounded risk-policy evidence rather than as a ranking of model quality. The full CI table remains part of the analysis package rather than a main-body table.",
        "",
        "### 5.3 Tool-contestation shifted risky accepts to escalation, not strict correction",
        "",
        f"On the EVP-8-HARD cohort, tool-contestation evaluated 47 candidates for both Qwen and DeepSeek. For the known tool false-accept opportunity set, DeepSeek shifted {deepseek_opp.get('candidate_count')} tool false accepts to {deepseek_opp.get('escalated')} escalations and {deepseek_opp.get('corrected_to_reject')} strict rejects. Qwen shifted {qwen_opp.get('candidate_count')} tool false accepts to {qwen_opp.get('escalated')} escalations, with {qwen_opp.get('corrected_to_reject')} strict rejects and {qwen_opp.get('repeated_accept')} repeated accept.",
        "",
        "This result supports safe handling through escalation. It does not support a claim that tool-contestation reliably identifies semantic incorrectness, because strict correction remained zero for both models.",
        "",
        "The opportunity-set Wilson intervals are wide and are retained in the analysis package rather than expanded into a separate main-body table.",
        "",
        "### 5.4 Coverage-contestation removed repeated false accepts by becoming highly conservative",
        "",
        "The current-98 coverage-contestation condition tested whether a stronger prompt could challenge visible-test-only acceptance without changing the frozen E6/no-verdict packet set. It removed repeated false accepts for Qwen, DeepSeek, and Gemini, reducing the false accept rate on 77 non-correct candidates to 0.00% for all three models. This is prompt-sensitivity evidence, not a new main result, because the same condition also collapsed correct-patch acceptance. DeepSeek and Gemini accepted no correct patches, and Qwen accepted only 2 of 21 correct patches.",
        "",
        "The result answers a narrow prompt-setting question. A model can be instructed to challenge coverage sufficiency and avoid visible-test-only acceptance on this frozen cohort, but the observed mechanism is mostly conservative triage rather than semantic discrimination. Therefore the paper should not claim that coverage-contestation improves autonomous verification. The supported claim is that prompt framing can move false-accept risk into reject/escalate outcomes while imposing a large correct-recall cost.",
        "",
        "### 5.5 A hard-negative stress matrix reduced false accepts through escalation",
        "",
        "After the current-98 prompt-sensitivity result, we constructed a separated hard-negative stress cohort to test visible-pass/hidden-fail cases more directly. The cohort contains 31 hidden-failing candidates across PySnooper, cookiecutter, and scrapy. The visible-tool baseline accepted all 31 cases. Because the scrapy cases are curated no-API stress-source partial variants, this is a hard-negative stress-test supplement rather than a pure agent-generated realistic cohort.",
        "",
        "Across Qwen, DeepSeek, and Gemini, the current merge-gate prompt produced 62 repeated false accepts in 93 model-condition records. The coverage-contestation prompt reduced repeated false accepts to 12/93. The reduction came entirely through escalation: strict rejects remained 0 in both conditions.",
        "",
        *stress_matrix_aggregate_table(stress_matrix),
        "",
        "This stress result strengthens the risk-triage interpretation. It is bounded triage evidence: the stronger prompt can route many visible-pass/hidden-fail candidates away from autonomous acceptance, including all Gemini stress cases and all DeepSeek stress cases. It does not show semantic correction, because no condition strictly rejected the hard negatives. Correct recall is also undefined in this all-negative cohort.",
        "",
        "### 5.6 E6 false accepts were concentrated in partial and regression negatives",
        "",
        "The most important failure mode is not the average E6 score but the remaining E6 false accepts among 77 non-correct candidates. Aggregate false-accept anatomy shows that Qwen and DeepSeek each accepted three partial fixes and one regression patch, while Gemini accepted four partial fixes and one regression patch. In the single regression negative included in EVP-8, all three repaired models accepted it at E6; this is a severe failure signal, not a statistical claim about regression-safety failures. The partial-fix rows show a broader semantic-incompleteness pattern concentrated in youtube-dl tasks.",
        "",
        *false_accept_case_group_table(false_accept_cases),
        "",
        "The sanitized case-level export records candidate id, project, task, negative type, E6 decision, no-verdict decision where available, and compressed rationale categories, but excludes raw response text, full rationale text, rendered prompts, patch diffs, and credentials. The table supports failure anatomy, not a claim that the complete model rationale has been audited semantically.",
        "",
        "## 6. Discussion",
        "",
        "The main implication is that LLM patch verification should be evaluated with explicit evidence boundaries. The same candidate patch may be treated differently when visible tests, regression checks, diagnostics, or deterministic tool summaries are introduced. Reporting only an aggregate accept/reject rate would hide this dependence.",
        "",
        "Prompt sensitivity is part of the measurement target rather than only a nuisance variable. EVP-8 exposes whether a prompt reduces false-accept risk through semantic discrimination or through abstention-driven routing. In the current evidence, the safer coverage-contestation behavior was mostly abstention and escalation, not strict correction.",
        "",
        "The results also clarify the role of escalation. Escalation can be useful for software-quality workflows because it routes risky cases away from autonomous acceptance. However, escalation is not strict correction, and aggressive contestation can destroy correct-patch recall. This distinction matters for deployment: a verifier that escalates risky candidates may reduce unsafe automation, but it has not proven semantic incorrectness or preserved useful acceptance.",
        "",
        "The strongest current contribution is methodological. EVP-8 provides a reproducible way to separate model-visible evidence from hidden evaluator labels, report accept/reject/escalate outcomes, and connect each claim to a validity gate. This is why the paper is framed as a controlled protocol and measurement study rather than as a new repair or verification algorithm.",
        "",
        "Several reviewer concerns remain bounded rather than eliminated. The cohort is small, Wilson intervals are wide, repaired Qwen, DeepSeek, and Gemini are the main model conditions, majority-vote cannot be computed from the current tracked summaries, and the hard-negative stress matrix is a stress-test supplement rather than a pure realistic agent-patch cohort. Most importantly, the current paper-facing main result is three-model but still not broad-model. These are not hidden weaknesses; they are the boundary conditions under which the current claims are valid.",
        "",
        "## 7. Threats to Validity",
        "",
        "**Internal validity.** Prompt wording, output schema, and evidence formatting may influence decisions. The study mitigates this risk through frozen packets, tracked prompt-boundary checks, parse-validity audits, raw-output-free summaries, and post-decision label joins. These controls reduce setup risk but do not make the results independent of the evaluated protocol versions.",
        "",
        "**Construct validity.** The accept/reject/escalate decision space simplifies real review workflows. Escalation is a routing outcome, not proof of semantic rejection. Hidden evaluator labels are used only for post-decision analysis and should not be interpreted as model-visible truth.",
        "",
        "**External validity.** The main evidence comes from a 98-candidate EVP-8 cohort, an EVP-8-HARD controlled cohort, a 31-case hard-negative stress matrix, and selected model conditions. The repaired E0-E6 main result now covers Qwen, DeepSeek, and Gemini, but it is still not a broad-model result. The hard-negative stress matrix reaches three projects, but the scrapy cases are curated no-API stress-source variants, so it should not be generalized as a pure agent-generated realistic cohort. The results therefore support bounded evidence-conditioned risk behavior in a controlled patch-verifier study, not universal LLM patch-verifier reliability.",
        "",
        "**Baseline validity.** Rule-only visible-tool is the completed deterministic baseline. Always-* and uniform-random policies are reference policies. Majority-vote and a separate deterministic E0/no-tool verifier remain unavailable under the current tracked-summary boundary.",
        "",
        "## 8. Conclusion",
        "",
        "This paper introduces EVP-8 as a hidden-evaluator evidence-visibility protocol for candidate patch verification. The repaired Qwen, DeepSeek, and Gemini v0.3 results show that visible executable and tool evidence can unlock correct-patch acceptance while retaining false-accept risk and model-dependent caution. E6 ablations, tool-contestation, coverage-contestation, and the hard-negative stress matrix further show that verdict-like evidence and prompt framing can shape policy behavior. EVP-8's engineering value is to reveal when LLMs behave as tool followers, abstainers, or risk routers under explicit evidence boundaries. The contribution is a reproducible software-engineering protocol for measuring evidence-conditioned risk behavior in a controlled LLM patch-verifier study, not a claim of autonomous patch correctness verification.",
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
