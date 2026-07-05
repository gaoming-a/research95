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
Z_95 = 1.959963984540054
VALIDITY_AUDIT = REPO_ROOT / "data" / "reviews" / "final_experiment_setting_validity_audit_v0_1.json"
FIVE_MODEL_SYNTHESIS = REPO_ROOT / "data" / "protocols" / "evp8_five_model_synthesis_v0_1.json"
NO_VERDICT_COMPARISON = REPO_ROOT / "data" / "reviews" / "evp8_e6_no_verdict_ablation_comparison.json"
HARD_TOOL_CONTESTATION = REPO_ROOT / "data" / "protocols" / "evp8_hard_tool_contestation_result_audit_v0_1.json"
REALISTIC_GATE = REPO_ROOT / "data" / "protocols" / "evp8_realistic_hardneg_combined_generation_gate_with_full_file_v0_1.json"
QWEN_LABEL_CONDITIONED = REPO_ROOT / "data" / "reviews" / "evp8_qwen_first_main_v0_3_prompt_v0_2_label_conditioned_summary.json"
DEEPSEEK_LABEL_CONDITIONED = REPO_ROOT / "data" / "reviews" / "evp8_deepseek_repaired_v0_3_prompt_v0_2_label_conditioned_summary.json"
GEMINI_LABEL_CONDITIONED = REPO_ROOT / "data" / "reviews" / "evp8_gemini_repaired_v0_3_prompt_v0_2_label_conditioned_summary.json"
PHASE_A_ANALYSIS = REPO_ROOT / "data" / "reviews" / "evp8_phase_a_paper_ready_analysis.json"
EVP8_PROTOCOL_V03 = REPO_ROOT / "data" / "protocols" / "evp8_protocol_v0_3_qwen_first.json"
BASELINE_FEASIBILITY = REPO_ROOT / "data" / "reviews" / "ccfc_baseline_feasibility_audit_v0_1.json"
CITATION_SUPPORT_BANK = REPO_ROOT / "docs" / "paper" / "ccfc_citation_support_bank_v0_1.md"

DEFAULT_JSON_OUT = REPO_ROOT / "data" / "reviews" / "final_manuscript_claim_map_v0_1.json"
DEFAULT_CLAIM_MD_OUT = REPO_ROOT / "docs" / "paper" / "final_manuscript_claim_map_v0_1.md"
DEFAULT_MANUSCRIPT_MD_OUT = REPO_ROOT / "docs" / "paper" / "ccfc_manuscript_rewrite_v0_1.md"
CCFC_FIGURE_DIR = REPO_ROOT / "docs" / "figures" / "ccfc"
FIGURE_FORMATS = ("pdf", "svg", "png")


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


def figure_output_status(stem: str) -> dict[str, Any]:
    outputs = [f"docs/figures/ccfc/{stem}.{suffix}" for suffix in FIGURE_FORMATS]
    complete = all((REPO_ROOT / output).exists() for output in outputs)
    return {
        "backend": "python" if complete else None,
        "output_stem": stem,
        "outputs": outputs if complete else [],
        "status": "generated_python" if complete else "planned_requires_backend",
    }


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


def percent(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value) * 100:.2f}%"


def ci_percent(interval: dict[str, Any] | None) -> str:
    if not interval:
        return "n/a"
    return (
        f"{percent(interval.get('estimate'))} "
        f"[{percent(interval.get('ci_95_low'))}, {percent(interval.get('ci_95_high'))}]"
    )


def wilson_interval(successes: int, total: int, z: float = Z_95) -> dict[str, Any]:
    if total == 0:
        return {
            "successes": successes,
            "total": total,
            "estimate": None,
            "ci_95_low": None,
            "ci_95_high": None,
        }
    p = successes / total
    denominator = 1 + z**2 / total
    center = (p + z**2 / (2 * total)) / denominator
    margin = z * ((p * (1 - p) + z**2 / (4 * total)) / total) ** 0.5 / denominator
    return {
        "successes": successes,
        "total": total,
        "estimate": round(p, 6),
        "ci_95_low": round(max(0.0, center - margin), 6),
        "ci_95_high": round(min(1.0, center + margin), 6),
    }


def citation_support_rows() -> list[dict[str, str]]:
    return [
        {
            "segment": "S1",
            "paper_location": "Introduction / Related Work",
            "claim": "Visible plausibility and test passing do not guarantee patch correctness.",
            "citation_keys": "qi_issta_2015_patch_plausibility; legoues_icse_2012_genprog; just_issta_2014_defects4j",
            "boundary": "Motivates the task; does not prove EVP-8 effectiveness.",
        },
        {
            "segment": "S2",
            "paper_location": "Related Work",
            "claim": "APR and bug-fix studies commonly use controlled datasets and test-based evaluation.",
            "citation_keys": "just_issta_2014_defects4j; legoues_icse_2012_genprog; tufano_icse_2019_bugfix_nmt",
            "boundary": "Positions the setting; does not imply the same task distribution.",
        },
        {
            "segment": "S3",
            "paper_location": "Related Work",
            "claim": "LLMs have been studied for repair and code editing, but verifier behavior is a separate decision problem.",
            "citation_keys": "xia_zhang_icse_2023_llm_apr; tufano_icse_2019_bugfix_nmt",
            "boundary": "Background only; not autonomous verifier evidence.",
        },
        {
            "segment": "S4",
            "paper_location": "Related Work / Method",
            "claim": "Code review is a socio-technical merge-gate process rather than a pure test outcome.",
            "citation_keys": "bacchelli_bird_icse_2013_code_review",
            "boundary": "Supports merge-gate framing; not an industrial deployment claim.",
        },
        {
            "segment": "S5",
            "paper_location": "Method",
            "claim": "The accept/reject/escalate output space is related to reject-option and selective-classification work.",
            "citation_keys": "chow_tit_1970_reject_option; geifman_el_yaniv_2017_selective_classification",
            "boundary": "Conceptual support; no calibrated probability claim.",
        },
        {
            "segment": "S6",
            "paper_location": "Method / Threats",
            "claim": "Evaluator-only labels should remain separate because software testing has an oracle problem.",
            "citation_keys": "barr_tse_2015_oracle_problem",
            "boundary": "Supports hidden-evaluator separation and validity limits.",
        },
        {
            "segment": "S7",
            "paper_location": "Discussion",
            "claim": "LLM-as-judge evaluations require bounded claims and controlled protocols.",
            "citation_keys": "zheng_neurips_2023_llm_judge",
            "boundary": "General evaluation caution; not direct patch-verifier transfer.",
        },
        {
            "segment": "S8",
            "paper_location": "Discussion",
            "claim": "Automation outputs can induce misuse or over-reliance, motivating explicit evidence-boundary reporting.",
            "citation_keys": "parasuraman_riley_1997_automation",
            "boundary": "Supports reliance risk; not a patch-specific empirical result.",
        },
    ]


def reference_records() -> list[dict[str, str]]:
    return [
        {
            "key": "qi_issta_2015_patch_plausibility",
            "reference": "Zichao Qi, Fan Long, Sara Achour, and Martin Rinard. \"An Analysis of Patch Plausibility and Correctness for Generate-and-Validate Patch Generation Systems.\" ISSTA 2015. DOI: 10.1145/2771783.2771791.",
        },
        {
            "key": "legoues_icse_2012_genprog",
            "reference": "Claire Le Goues, ThanhVu Nguyen, Stephanie Forrest, and Westley Weimer. \"A Systematic Study of Automated Program Repair: Fixing 55 out of 105 Bugs for $8 Each.\" ICSE 2012. DOI: 10.1109/ICSE.2012.6227211.",
        },
        {
            "key": "just_issta_2014_defects4j",
            "reference": "Rene Just, Darioush Jalali, and Michael D. Ernst. \"Defects4J: A Database of Existing Faults to Enable Controlled Testing Studies for Java Programs.\" ISSTA 2014. DOI: 10.1145/2610384.2628055.",
        },
        {
            "key": "barr_tse_2015_oracle_problem",
            "reference": "Earl T. Barr, Mark Harman, Phil McMinn, Muzammil Shahbaz, and Shin Yoo. \"The Oracle Problem in Software Testing: A Survey.\" IEEE TSE 2015. DOI: 10.1109/TSE.2014.2372785.",
        },
        {
            "key": "xia_zhang_icse_2023_llm_apr",
            "reference": "Chunqiu Steven Xia and Lingming Zhang. \"Automated Program Repair in the Era of Large Pre-trained Language Models.\" ICSE 2023. DOI: 10.1109/ICSE48619.2023.00129.",
        },
        {
            "key": "tufano_icse_2019_bugfix_nmt",
            "reference": "Michele Tufano, Cody Watson, Gabriele Bavota, Massimiliano Di Penta, Martin White, and Denys Poshyvanyk. \"An Empirical Investigation into Learning Bug-Fixing Patches in the Wild via Neural Machine Translation.\" ICSE 2019. DOI: 10.1109/ICSE.2019.00064.",
        },
        {
            "key": "bacchelli_bird_icse_2013_code_review",
            "reference": "Alberto Bacchelli and Christian Bird. \"Expectations, Outcomes, and Challenges of Modern Code Review.\" ICSE 2013. DOI: 10.1109/ICSE.2013.6606617.",
        },
        {
            "key": "chow_tit_1970_reject_option",
            "reference": "C. K. Chow. \"On Optimum Recognition Error and Reject Tradeoff.\" IEEE Transactions on Information Theory 1970. DOI: 10.1109/TIT.1970.1054406.",
        },
        {
            "key": "geifman_el_yaniv_2017_selective_classification",
            "reference": "Yonatan Geifman and Ran El-Yaniv. \"Selective Classification for Deep Neural Networks.\" arXiv:1705.08500, 2017.",
        },
        {
            "key": "zheng_neurips_2023_llm_judge",
            "reference": "Lianmin Zheng et al. \"Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena.\" NeurIPS 2023. arXiv:2306.05685.",
        },
        {
            "key": "parasuraman_riley_1997_automation",
            "reference": "Raja Parasuraman and Victor Riley. \"Humans and Automation: Use, Misuse, Disuse, Abuse.\" Human Factors 1997. DOI: 10.1518/001872097778543886.",
        },
    ]


def baseline_policy_rows(baseline: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    metrics = baseline.get("completed_or_calculable_metrics") or {}
    feasibility = baseline.get("feasibility") or {}
    for key in [
        "always_escalate",
        "always_reject",
        "always_accept",
        "uniform_random_three_way_expected",
        "rule_only_visible_tool",
    ]:
        row_metrics = metrics.get(key) or {}
        decisions = row_metrics.get("decision_counts") or {}
        rows.append(
            {
                "policy": key,
                "status": (feasibility.get(key) or {}).get("status", ""),
                "paper_role": (feasibility.get(key) or {}).get("paper_role", ""),
                "accept": decisions.get("accept", 0),
                "reject": decisions.get("reject", 0),
                "escalate": decisions.get("escalate", 0),
                "accepted_precision": row_metrics.get("accepted_precision"),
                "correct_recall": row_metrics.get("correct_recall"),
                "false_accept_rate": row_metrics.get("false_accept_rate"),
            }
        )
    return rows


def tool_contestation_ci_rows(hard: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for model_id, model in sorted((hard.get("models") or {}).items()):
        opportunity = (
            (model.get("opportunity_correction_vs_tool") or {})
            .get("tool_false_accepts")
            or {}
        )
        total = int(opportunity.get("candidate_count") or 0)
        strict = int(opportunity.get("corrected_to_reject") or 0)
        escalated = int(opportunity.get("escalated") or 0)
        repeated = int(opportunity.get("repeated_accept") or 0)
        rows.append(
            {
                "model": model_id,
                "candidate_count": total,
                "safe_handled": strict + escalated,
                "strict_corrected_to_reject": strict,
                "escalated": escalated,
                "repeated_accept": repeated,
                "safe_handling_ci": wilson_interval(strict + escalated, total),
                "strict_correction_ci": wilson_interval(strict, total),
                "repeated_accept_ci": wilson_interval(repeated, total),
            }
        )
    return rows


def uncertainty_rows(phase_a: dict[str, Any]) -> list[dict[str, Any]]:
    confidence = phase_a.get("confidence_intervals") or {}
    rows: list[dict[str, Any]] = []
    for condition in [
        "rule-only",
        "qwen/qwen3.7-max E6-full",
        "qwen/qwen3.7-max E6-no-verdict",
        "deepseek/deepseek-v4-pro E6-full",
        "deepseek/deepseek-v4-pro E6-no-verdict",
    ]:
        intervals = confidence.get(condition) or {}
        rows.append(
            {
                "condition": condition,
                "accepted_precision": intervals.get("accepted_precision"),
                "correct_recall": intervals.get("correct_recall"),
                "false_accept_rate": intervals.get("false_accept_rate"),
                "escalation_rate": intervals.get("escalation_rate"),
            }
        )
    return rows


def evidence_ladder_rows(protocol: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in protocol.get("evidence_ladder") or []:
        level = str(item.get("level", ""))
        if level == "E7":
            continue
        rows.append(
            {
                "level": level,
                "name": str(item.get("level_name", "")),
                "adds": str(item.get("adds_evidence_class", "")),
                "field_groups": ", ".join(str(group) for group in item.get("model_visible_field_groups", [])),
            }
        )
    return rows


def qwen_label_metric_rows(label_conditioned: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for level, metrics in sorted((label_conditioned.get("per_evidence_level") or {}).items()):
        confusion = metrics.get("confusion_counts") or {}
        rows.append(
            {
                "level": level,
                "accept": (metrics.get("decision_counts") or {}).get("accept", 0),
                "correct_accept": confusion.get("true_accept", 0),
                "false_accept": confusion.get("false_accept", 0),
                "accepted_precision": metrics.get("accepted_precision"),
                "correct_recall": metrics.get("correct_recall"),
                "false_accept_rate": metrics.get("false_accept_rate"),
                "false_reject_rate": metrics.get("false_reject_rate"),
                "escalation_rate": metrics.get("escalation_rate"),
            }
        )
    return rows


def repaired_model_e6_rows(*summaries: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for summary in summaries:
        metrics = summary["per_evidence_level"]["E6"]
        confusion = metrics["confusion_counts"]
        rows.append(
            {
                "model": summary["model_id"],
                "accept": (metrics.get("decision_counts") or {}).get("accept", 0),
                "reject": (metrics.get("decision_counts") or {}).get("reject", 0),
                "escalate": (metrics.get("decision_counts") or {}).get("escalate", 0),
                "correct_accept": confusion.get("true_accept", 0),
                "false_accept": confusion.get("false_accept", 0),
                "accepted_precision": metrics.get("accepted_precision"),
                "correct_recall": metrics.get("correct_recall"),
                "false_accept_rate": metrics.get("false_accept_rate"),
                "escalation_rate": metrics.get("escalation_rate"),
            }
        )
    return rows


def e6_ablation_metric_rows(no_verdict: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rule_metrics = (no_verdict.get("rule_only") or {}).get("metrics") or {}
    rows.append({"condition": "rule-only", **rule_metrics})
    for model, model_data in sorted((no_verdict.get("per_model") or {}).items()):
        for condition, condition_data in sorted((model_data.get("conditions") or {}).items()):
            rows.append({"condition": f"{model} {condition}", **(condition_data.get("metrics") or {})})
    return rows


def build_claim_map() -> dict[str, Any]:
    validity = read_json(VALIDITY_AUDIT)
    five = read_json(FIVE_MODEL_SYNTHESIS)
    no_verdict = read_json(NO_VERDICT_COMPARISON)
    hard = read_json(HARD_TOOL_CONTESTATION)
    realistic = read_json(REALISTIC_GATE)
    qwen_label = read_json(QWEN_LABEL_CONDITIONED)
    deepseek_label = read_json(DEEPSEEK_LABEL_CONDITIONED)
    gemini_label = read_json(GEMINI_LABEL_CONDITIONED)
    phase_a = read_json(PHASE_A_ANALYSIS)
    protocol_v03 = read_json(EVP8_PROTOCOL_V03)
    baseline_feasibility = read_json(BASELINE_FEASIBILITY)

    hard_gate = realistic.get("hard_negative_gate") or {}
    hard_models = hard.get("models") or {}
    deepseek_contest = hard_models.get("deepseek/deepseek-v4-pro", {})
    qwen_contest = hard_models.get("qwen/qwen3.7-max", {})

    manuscript_argument = (
        "In candidate patch verification, we show that a hidden-evaluator evidence-visibility "
        "protocol can measure evidence-conditioned LLM merge-gate behavior, supported by the "
        "accept-aware Qwen/DeepSeek/Gemini v0.3 label-conditioned analyses, E6 rule-only/no-verdict ablations, "
        "tool-contestation audits, and a realistic source-acquisition gate audit."
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
        {
            "term": "reference policy",
            "definition": "a deterministic policy calculated for baseline orientation rather than implemented as a verifier result",
            "decision": "Use for always-escalate, always-reject, and always-accept.",
        },
        {
            "term": "rule-only visible-tool baseline",
            "definition": "the completed deterministic E6 baseline using visible tool evidence",
            "decision": "Use as the current completed deterministic baseline.",
        },
    ]

    claims = [
        {
            "id": "C1",
            "claim": "EVP-8 defines a valid hidden-evaluator evidence boundary for candidate patch verification.",
            "status": "supported",
            "evidence": ["evp8_protocol_v0_3_qwen_first", "final_experiment_setting_validity_audit"],
            "paper_location": "Methods: Evidence-visibility protocol",
            "allowed_wording": "EVP-8 separates model-visible evidence from evaluator-only labels and supports post-decision metric joins.",
            "boundary": "Protocol validity, not model effectiveness.",
        },
        {
            "id": "C2",
            "claim": "In three repaired v0.3 accept-aware runs, visible executable and tool evidence changed correct-patch acceptance while retaining bounded false-accept risk.",
            "status": "supported_three_model",
            "evidence": ["v0_3_qwen_label_conditioned_summary", "v0_3_deepseek_label_conditioned_summary", "v0_3_gemini_label_conditioned_summary"],
            "paper_location": "Results: Accept-aware label-conditioned behavior",
            "allowed_wording": "For Qwen, DeepSeek, and Gemini v0.3 on the frozen 98-candidate packet set, visible executable/tool evidence shifted many correct patches from non-accept to accept while leaving 4-5 E6 false accepts.",
            "boundary": "Three-model v0.3 descriptive result; not broad-model superiority or autonomous correctness verification.",
        },
        {
            "id": "C3",
            "claim": "Verdict-like tool summaries can anchor model decisions; removing or contesting them changes behavior.",
            "status": "supported_qualified",
            "evidence": ["evp8_e6_no_verdict_ablation_comparison", "evp8_hard_tool_contestation_result_audit"],
            "paper_location": "Results: Verdict dependence and contestation",
            "allowed_wording": "Verdict removal and tool-contestation produced model-dependent risk-control tradeoffs.",
            "boundary": "Measured as policy behavior, not semantic proof.",
        },
        {
            "id": "C4",
            "claim": "Tool-contestation primarily improves safe handling through escalation rather than strict correction.",
            "status": "supported",
            "evidence": ["EVP-8-HARD tool-contestation audit"],
            "paper_location": "Results: Tool-contestation as risk triage",
            "allowed_wording": "Known false accepts were mostly shifted to escalation, so the supported contribution is risk triage.",
            "boundary": "Strict correction remains separate and limited.",
        },
        {
            "id": "C5",
            "claim": "The fresh realistic hard-negative branch is a source-acquisition negative result, not a verifier-ready main experiment.",
            "status": "supported_negative_boundary",
            "evidence": ["realistic_hardneg_generation_gate"],
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
            "title": "Accept-aware and no-verdict metric evidence",
            "conclusion": "Repaired evidence unlocks Qwen correct-patch acceptance while E6 ablations expose verdict-dependent risk tradeoffs.",
            "panels": ["Qwen v0.3 label-conditioned metrics by level", "rule-only, E6-full, and E6-no-verdict comparison"],
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
    for figure, stem in zip(
        figures,
        ("ccfc_fig1_protocol", "ccfc_fig2_decision_patterns", "ccfc_fig3_claim_boundary"),
        strict=True,
    ):
        figure.update(figure_output_status(stem))
    figures_generated = all(figure["status"] == "generated_python" for figure in figures)

    checks = [
        check("validity_audit_passed_with_bounded_claims", validity.get("overall_status") == "passed_with_bounded_claims", validity.get("overall_status")),
        check("five_model_synthesis_passed", five.get("later_model_audit_status") == "passed", five.get("later_model_audit_status")),
        check("no_verdict_comparison_checks_present", len(no_verdict.get("checks", [])) >= 1, len(no_verdict.get("checks", []))),
        check("hard_tool_contestation_audit_passed", hard.get("audit_status") == "passed", hard.get("audit_status")),
        check("realistic_gate_not_verifier_ready", hard_gate.get("passed") is False, hard_gate),
        check("qwen_label_conditioned_checks_passed", all(item.get("passed") for item in qwen_label.get("checks", [])), len(qwen_label.get("checks", []))),
        check("deepseek_label_conditioned_checks_passed", all(item.get("passed") for item in deepseek_label.get("checks", [])), len(deepseek_label.get("checks", []))),
        check("gemini_label_conditioned_checks_passed", all(item.get("passed") for item in gemini_label.get("checks", [])), len(gemini_label.get("checks", []))),
        check("phase_a_analysis_checks_passed", all(item.get("passed") for item in phase_a.get("checks", [])), len(phase_a.get("checks", []))),
        check("baseline_feasibility_audit_passed", baseline_feasibility.get("status") == "passed", baseline_feasibility.get("status")),
        check("citation_support_bank_present", CITATION_SUPPORT_BANK.exists(), str(CITATION_SUPPORT_BANK.relative_to(REPO_ROOT))),
    ]

    return {
        "artifact_id": "final_manuscript_claim_map_current",
        "date": "2026-07-03",
        "paper_target": "stable CCF-C submission",
        "scope": {
            "api_call_attempted": False,
            "raw_model_outputs_read": False,
            "prompt_text_read": False,
            "patch_text_read": False,
            "figure_backend": "python" if figures_generated else None,
            "figure_backend_selected": figures_generated,
        },
        "inputs": {
            "validity_audit": "data/reviews/final_experiment_setting_validity_audit_v0_1.json",
            "five_model_synthesis": "data/protocols/evp8_five_model_synthesis_v0_1.json",
            "no_verdict_comparison": "data/reviews/evp8_e6_no_verdict_ablation_comparison.json",
            "hard_tool_contestation": "data/protocols/evp8_hard_tool_contestation_result_audit_v0_1.json",
            "realistic_gate": "data/protocols/evp8_realistic_hardneg_combined_generation_gate_with_full_file_v0_1.json",
            "qwen_label_conditioned": "data/reviews/evp8_qwen_first_main_v0_3_prompt_v0_2_label_conditioned_summary.json",
            "deepseek_label_conditioned": "data/reviews/evp8_deepseek_repaired_v0_3_prompt_v0_2_label_conditioned_summary.json",
            "gemini_label_conditioned": "data/reviews/evp8_gemini_repaired_v0_3_prompt_v0_2_label_conditioned_summary.json",
            "phase_a_analysis": "data/reviews/evp8_phase_a_paper_ready_analysis.json",
            "evp8_protocol_v0_3": "data/protocols/evp8_protocol_v0_3_qwen_first.json",
            "baseline_feasibility": "data/reviews/ccfc_baseline_feasibility_audit_v0_1.json",
            "citation_support_bank": "docs/paper/ccfc_citation_support_bank_v0_1.md",
        },
        "manuscript_argument": manuscript_argument,
        "terminology_ledger": terminology,
        "claims": claims,
        "forbidden_claims": read_json(VALIDITY_AUDIT).get("forbidden_claims", []),
        "remaining_threats": read_json(VALIDITY_AUDIT).get("remaining_threats", []),
        "decision_totals_by_level": decision_totals_by_level(five),
        "per_model_level_counts": compact_level_counts(five),
        "evidence_ladder": evidence_ladder_rows(protocol_v03),
        "qwen_label_conditioned_metrics": qwen_label_metric_rows(qwen_label),
        "repaired_model_e6_metrics": repaired_model_e6_rows(qwen_label, deepseek_label, gemini_label),
        "e6_ablation_metrics": e6_ablation_metric_rows(no_verdict),
        "citation_support": citation_support_rows(),
        "reference_records": reference_records(),
        "baseline_policy_boundaries": baseline_policy_rows(baseline_feasibility),
        "baseline_feasibility_boundary": baseline_feasibility.get("claim_boundary") or {},
        "phase_a_uncertainty_summary": uncertainty_rows(phase_a),
        "tool_contestation_uncertainty_summary": tool_contestation_ci_rows(hard),
        "phase_a_confidence_intervals": phase_a.get("confidence_intervals") or {},
        "phase_a_boundary": phase_a.get("claim_boundary") or {},
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
        "# Current Final Manuscript Claim Map",
        "",
        "Date: 2026-07-04",
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
    lines += [
        "",
        "## Citation Support",
        "",
        "| segment | paper location | claim | citation keys | boundary |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in claim_map["citation_support"]:
        lines.append(
            f"| `{row['segment']}` | {row['paper_location']} | {row['claim']} | "
            f"`{row['citation_keys']}` | {row['boundary']} |"
        )
    lines += [
        "",
        "## Reference Support Records",
        "",
        "| key | reference |",
        "| --- | --- |",
    ]
    for row in claim_map["reference_records"]:
        lines.append(f"| `{row['key']}` | {row['reference']} |")
    lines += [
        "",
        "## Evidence Ladder",
        "",
        "| level | name | added evidence class | model-visible field groups |",
        "| --- | --- | --- | --- |",
    ]
    for row in claim_map["evidence_ladder"]:
        lines.append(f"| {row['level']} | {row['name']} | {row['adds']} | {row['field_groups']} |")
    lines += [
        "",
        "## Qwen v0.3 Label-Conditioned Metrics",
        "",
        "| level | accept | correct accept | false accept | accepted precision | correct recall | false accept rate | escalation rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in claim_map["qwen_label_conditioned_metrics"]:
        lines.append(
            f"| {row['level']} | {row['accept']} | {row['correct_accept']} | {row['false_accept']} | "
            f"{percent(row['accepted_precision'])} | {percent(row['correct_recall'])} | "
            f"{percent(row['false_accept_rate'])} | {percent(row['escalation_rate'])} |"
        )
    lines += [
        "",
        "## E6 Baseline And No-Verdict Metrics",
        "",
        "| condition | accept | reject | escalate | accepted precision | correct recall | false accept rate | escalation rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in claim_map["e6_ablation_metrics"]:
        decisions = row.get("decision_counts") or {}
        lines.append(
            f"| {row['condition']} | {decisions.get('accept', 0)} | {decisions.get('reject', 0)} | "
            f"{decisions.get('escalate', 0)} | {percent(row.get('accepted_precision'))} | "
            f"{percent(row.get('correct_recall'))} | {percent(row.get('false_accept_rate'))} | "
            f"{percent(row.get('escalation_rate'))} |"
        )
    lines += [
        "",
        "## Baseline Policy Boundaries",
        "",
        "| policy | status | accept | reject | escalate | role |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in claim_map["baseline_policy_boundaries"]:
        lines.append(
            f"| `{row['policy']}` | `{row['status']}` | {row['accept']} | "
            f"{row['reject']} | {row['escalate']} | {row['paper_role']} |"
        )
    lines += [
        "",
        "## Phase A Uncertainty Summary",
        "",
        "| condition | accepted precision 95% CI | correct recall 95% CI | false accept rate 95% CI | escalation rate 95% CI |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in claim_map["phase_a_uncertainty_summary"]:
        lines.append(
            f"| {row['condition']} | {ci_percent(row.get('accepted_precision'))} | "
            f"{ci_percent(row.get('correct_recall'))} | {ci_percent(row.get('false_accept_rate'))} | "
            f"{ci_percent(row.get('escalation_rate'))} |"
        )
    lines += [
        "",
        "## Tool-Contestation Opportunity Uncertainty",
        "",
        "| model | opportunity cases | safe handling 95% CI | strict correction 95% CI | repeated accept 95% CI |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in claim_map["tool_contestation_uncertainty_summary"]:
        lines.append(
            f"| {row['model']} | {row['candidate_count']} | {ci_percent(row['safe_handling_ci'])} | "
            f"{ci_percent(row['strict_correction_ci'])} | {ci_percent(row['repeated_accept_ci'])} |"
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
    figures_generated = all(figure["status"] == "generated_python" for figure in claim_map["figure_plan"])
    figure_assets = {figure["id"]: figure for figure in claim_map["figure_plan"]}
    fig1 = figure_assets["Fig. 1"]
    fig2 = figure_assets["Fig. 2"]
    fig3 = figure_assets["Fig. 3"]
    evidence_table_lines = [
        "| level | added model-visible evidence | role in the protocol |",
        "| --- | --- | --- |",
    ]
    for row in claim_map["evidence_ladder"]:
        evidence_table_lines.append(f"| {row['level']} | {row['adds']} | {row['name']} |")
    qwen_table_lines = [
        "| level | accept | correct accept | false accept | accepted precision | correct recall | false accept rate | escalation rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in claim_map["qwen_label_conditioned_metrics"]:
        qwen_table_lines.append(
            f"| {row['level']} | {row['accept']} | {row['correct_accept']} | {row['false_accept']} | "
            f"{percent(row['accepted_precision'])} | {percent(row['correct_recall'])} | "
            f"{percent(row['false_accept_rate'])} | {percent(row['escalation_rate'])} |"
        )
    repaired_e6_table_lines = [
        "| model | accept | reject | escalate | correct accept | false accept | accepted precision | correct recall | false accept rate | escalation rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in claim_map["repaired_model_e6_metrics"]:
        repaired_e6_table_lines.append(
            f"| {row['model']} | {row['accept']} | {row['reject']} | {row['escalate']} | "
            f"{row['correct_accept']} | {row['false_accept']} | {percent(row['accepted_precision'])} | "
            f"{percent(row['correct_recall'])} | {percent(row['false_accept_rate'])} | "
            f"{percent(row['escalation_rate'])} |"
        )
    e6_table_lines = [
        "| condition | accept | reject | escalate | accepted precision | correct recall | false accept rate | escalation rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in claim_map["e6_ablation_metrics"]:
        decisions = row.get("decision_counts") or {}
        e6_table_lines.append(
            f"| {row['condition']} | {decisions.get('accept', 0)} | {decisions.get('reject', 0)} | "
            f"{decisions.get('escalate', 0)} | {percent(row.get('accepted_precision'))} | "
            f"{percent(row.get('correct_recall'))} | {percent(row.get('false_accept_rate'))} | "
            f"{percent(row.get('escalation_rate'))} |"
        )
    baseline_policy_table_lines = [
        "| policy | status | accept | reject | escalate | paper role |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in claim_map["baseline_policy_boundaries"]:
        baseline_policy_table_lines.append(
            f"| {row['policy']} | {row['status']} | {row['accept']} | {row['reject']} | "
            f"{row['escalate']} | {row['paper_role']} |"
        )
    uncertainty_table_lines = [
        "| condition | accepted precision 95% CI | correct recall 95% CI | false accept rate 95% CI | escalation rate 95% CI |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in claim_map["phase_a_uncertainty_summary"]:
        uncertainty_table_lines.append(
            f"| {row['condition']} | {ci_percent(row.get('accepted_precision'))} | "
            f"{ci_percent(row.get('correct_recall'))} | {ci_percent(row.get('false_accept_rate'))} | "
            f"{ci_percent(row.get('escalation_rate'))} |"
        )
    tool_contestation_ci_table_lines = [
        "| model | opportunity cases | safe handling 95% CI | strict correction 95% CI | repeated accept 95% CI |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in claim_map["tool_contestation_uncertainty_summary"]:
        tool_contestation_ci_table_lines.append(
            f"| {row['model']} | {row['candidate_count']} | {ci_percent(row['safe_handling_ci'])} | "
            f"{ci_percent(row['strict_correction_ci'])} | {ci_percent(row['repeated_accept_ci'])} |"
        )
    lines = [
        "# Evidence Visibility Shapes Risk Behavior in LLM-Based Candidate Patch Verification",
        "",
        "Draft status: stable CCF-C manuscript rewrite v0.3, 2026-07-04.",
        "",
        "## Abstract",
        "",
        "Large language models (LLMs) are increasingly used to inspect software patches, but a merge decision is only meaningful relative to the evidence available at review time. We formulate candidate patch verification as an evidence-conditioned merge-gate task: given a candidate patch and model-visible evidence, a verifier must accept, reject, or escalate while evaluator-only correctness labels remain hidden until post-decision analysis. We introduce the Evidence-Visibility Protocol (EVP-8), a frozen 98-candidate packet set with seven cumulative evidence levels and tracked hidden-evaluator joins. In three repaired v0.3 runs, Qwen and Gemini reached 95.24% E6 correct recall while DeepSeek reached 80.95%; accepted precision was 83.33% for Qwen, 80.95% for DeepSeek, and 80.00% for Gemini, with 4-5 false accepts among 77 non-correct candidates. E6 rule-only and no-verdict ablations further show that verdict-like tool summaries can anchor behavior, and tool-contestation shifts known false accepts mainly to escalation, not strict rejection. These results support a bounded methodological contribution: evidence visibility should be controlled and reported when evaluating LLM patch verifiers. They do not establish reliable autonomous patch correctness verification.",
        "",
        "## 1. Introduction",
        "",
        "Candidate patches generated or reviewed by automated systems can look plausible while remaining incomplete, irrelevant, or unsafe to merge. Prior automated program repair studies have shown that plausible or test-passing patches can still be incorrect [qi_issta_2015_patch_plausibility; legoues_icse_2012_genprog]. This creates a software-quality problem: teams need to decide not only whether a patch resembles a fix, but whether the evidence available at review time is sufficient to accept it. In practice, that evidence may include issue summaries, patch diffs, static checks, visible tests, generated tests, or tool summaries. A verifier that ignores this evidence boundary risks confusing apparent plausibility with correctness.",
        "",
        "LLMs are attractive as patch reviewers because they can read code context and produce structured explanations. However, model behavior may depend strongly on what evidence is visible. If a study does not control the model-visible evidence, it becomes difficult to distinguish model capability from evidence presentation, tool-summary anchoring, or prompt-induced caution. This paper therefore treats evidence visibility as the main experimental variable in candidate patch verification.",
        "",
        "We study a hidden-evaluator workflow in which model-visible evidence packets are separated from evaluator-only labels. The verifier emits one merge-gate decision: accept, reject, or escalate, following the broader idea that a classifier can reject or abstain when the available evidence is insufficient [chow_tit_1970_reject_option; geifman_el_yaniv_2017_selective_classification]. Correctness labels, hidden oracle outcomes, and failure taxonomy labels are joined only after execution for analysis. This design lets us ask a bounded question: how does evidence visibility shape LLM risk behavior when reviewing candidate patches?",
        "",
        "Our central finding is that, once the evidence construction is repaired, visible executable and tool evidence can unlock correct-patch acceptance while exposing a measurable false-accept tradeoff. The result is not evidence that LLMs are reliable autonomous patch correctness verifiers. Instead, it supports a software-quality interpretation: LLM verifiers should be evaluated as evidence-conditioned risk controllers whose behavior can shift toward acceptance, rejection, escalation, or tool-summary dependence depending on the setting.",
        "",
        "## 2. Background and Related Work",
        "",
        "Patch correctness has long been a central concern in automated program repair and software testing. Generate-and-validate repair systems can produce plausible patches that pass available tests while failing broader semantic expectations, a problem commonly discussed as plausible or overfitting patches [qi_issta_2015_patch_plausibility]. Controlled fault benchmarks and systematic APR studies provide the evaluation context for this problem [just_issta_2014_defects4j; legoues_icse_2012_genprog]. This paper studies the downstream verification side: after a candidate patch exists, what evidence is sufficient for a merge-gate decision?",
        "",
        "Testing and oracle research provide the technical basis for exposing the limits of visible evidence. The oracle problem in software testing means that deciding whether observed behavior is correct is itself a non-trivial validity boundary [barr_tse_2015_oracle_problem]. Visible fail-to-pass tests, pass-to-pass regression checks, static diagnostics, and broader tool summaries can each support a reviewer, but none is identical to a hidden evaluator label. The EVP-8 design therefore separates model-visible evidence from evaluator-only outcomes rather than asking an LLM to see or infer the final label.",
        "",
        "LLM-based repair and LLM-as-judge studies further motivate the evidence-boundary question. Large pretrained models have been studied as program repair systems and code-editing tools [xia_zhang_icse_2023_llm_apr; tufano_icse_2019_bugfix_nmt], while LLM-as-judge evaluations show that model judgments require controlled protocols and bounded claims [zheng_neurips_2023_llm_judge]. LLMs can summarize code context and produce structured rationales, but their decisions may be shaped by prompt framing, output schema, and authoritative-looking tool verdicts. We therefore evaluate LLM patch verification as a selective decision problem with an explicit escalation option, closer to human-in-the-loop triage and abstention than to proof of semantic correctness.",
        "",
        "The distinction from prior benchmark-style repair evaluation is methodological. Existing benchmarks primarily ask whether a system resolves a task. Code review work, by contrast, emphasizes that a merge decision is embedded in a review process rather than reducible to a single test outcome [bacchelli_bird_icse_2013_code_review]. EVP-8 asks how a verifier behaves under controlled evidence visibility after a candidate patch is already available. The contribution is not a new repair algorithm; it is a reproducible protocol and evidence chain for measuring evidence-conditioned risk behavior.",
        "",
        "## 3. Methods: Evidence-Visibility Protocol",
        "",
        "The unit of analysis is a candidate patch reviewed under a predefined evidence packet. Each packet contains only model-visible information for its evidence level, while hidden evaluator labels and oracle outcomes remain unavailable to the model. After the model decision, evaluator-only labels are joined to compute false accepts, correct recall, escalation, and other bounded metrics.",
        "",
        "![Figure 1. Hidden-evaluator evidence-visibility protocol.](../figures/ccfc/ccfc_fig1_protocol.png)",
        "",
        f"**Figure 1. {fig1['title']}.** {fig1['conclusion']} The figure defines the paper's evidence boundary: candidate patches and level-specific evidence are visible to the model, whereas evaluator labels are withheld until post-decision analysis. Source assets: `docs/figures/ccfc/ccfc_fig1_protocol.pdf`, `.svg`, and `.png`.",
        "",
        "The EVP-8 packet set contains 98 candidate patches reviewed across seven evidence levels, E0 through E6. Five selected models produced 686 parse-valid decisions each on the frozen packet set. The synthesis supports descriptive per-level decision-pattern reporting for the packet set; it does not support broad claims that one evidence level is universally optimal or that LLMs outperform deterministic baselines.",
        "",
        "The evidence levels are cumulative and intentionally transparent:",
        "",
        *evidence_table_lines,
        "",
        "## 4. Methods: Data, Metrics, and Validity Gates",
        "",
        "The study is organized around four research questions. RQ1 asks whether repaired accept-aware evidence changes label-conditioned Qwen, DeepSeek, and Gemini decisions across E0-E6. RQ2 asks whether verdict-like deterministic tool summaries anchor E6 behavior. RQ3 asks whether explicit tool-contestation can make models challenge visible-test-only accept premises. RQ4 asks whether a fresh realistic hard-negative source-acquisition branch is ready to support a main verifier experiment.",
        "",
        "The evaluated evidence sources match those questions. First, the accept-aware Qwen, DeepSeek, and Gemini v0.3 analyses compute label-conditioned accepted precision, correct recall, false accept rate, false reject rate, and escalation rate after post-execution label join. Second, E6 full, rule-only, and E6 no-verdict comparisons test the effect of verdict-like tool fields. Third, EVP-8-HARD tool-contestation evaluates known false-accept opportunities. Fourth, the realistic hard-negative branch is treated as a source-acquisition gate rather than a main verifier result because it failed the predeclared three-project readiness threshold.",
        "",
        "All paper-facing claims are constrained by a final setting-validity audit. That audit verifies run and parse coverage, raw-output-free summaries, post-execution label joins, prompt-boundary checks, and the non-overclaiming of the realistic hard-negative branch. It passed only with bounded claims: the results are usable as real evidence for evidence-conditioned risk behavior, not as proof of autonomous correctness verification. Reference policies calculated from aggregate labels are therefore reported only as decision-space boundaries, while candidate-level baselines that require aligned decisions, such as majority voting, are not reported as completed results.",
        "",
        "The baseline policy boundary is explicit. Always-escalate, always-reject, and always-accept are deterministic reference policies calculated from aggregate label totals; they orient the decision space but are not successful verifier results. Uniform random three-way is reported only as an expected reference policy over accept, reject, and escalate, not as a stochastic experiment. The completed deterministic baseline is the rule-only visible-tool policy. Majority voting across models and a separate E0/no-tool deterministic verifier require candidate-level aligned audits and are not reported as completed baselines.",
        "",
        *baseline_policy_table_lines,
        "",
        "## 5. Results",
        "",
        "### 5.1 RQ1: Accept-aware evidence changed three repaired model policies",
        "",
        "The repaired Qwen, DeepSeek, and Gemini v0.3 accept-aware runs provide direct label-conditioned results on the frozen 98-candidate packet set. Hidden labels were joined only after execution, and each matrix had complete candidate-level coverage with no missing or duplicate cells.",
        "",
        *repaired_e6_table_lines,
        "",
        "The three-model E6 table removes the earlier single-model weakness but does not remove the main risk boundary. Qwen and Gemini reached 95.24% correct recall, while DeepSeek was more conservative at 80.95%. All three retained false accepts: Qwen and DeepSeek accepted four non-correct candidates, and Gemini accepted five. The supported claim is therefore evidence-conditioned risk behavior, not reliable autonomous correctness verification or stable superiority over rule-only evidence.",
        "",
        "Qwen level-conditioned metrics remain shown below as the detailed evidence-visibility curve used by the current figure set:",
        "",
        *qwen_table_lines,
        "",
        "![Figure 2. Accept-aware and no-verdict metric evidence.](../figures/ccfc/ccfc_fig2_decision_patterns.png)",
        "",
        f"**Figure 2. {fig2['title']}.** {fig2['conclusion']} Panel a reports Qwen v0.3 correct recall and false accept rate across E0--E6; panel b compares rule-only, E6-full, and E6-no-verdict conditions; panel c summarizes the current result-chain boundary. Source assets: `docs/figures/ccfc/ccfc_fig2_decision_patterns.pdf`, `.svg`, and `.png`.",
        "",
        "The detailed Qwen table illustrates the evidence-visibility curve: at E0-E2, Qwen accepted no correct patches, so the setting mainly measured caution. At E3-E6, executable and tool evidence enabled many correct-patch accepts. The three-model summary shows the same higher-level pattern with model-specific policy differences. The improvement was not free: E6 false accepts remained in all three repaired runs. The supported claim is therefore not that more evidence monotonically proves correctness; it is that visible evidence can unlock acceptance behavior while exposing a measurable false-accept tradeoff.",
        "",
        "### 5.2 RQ2: Verdict-like evidence changed policy behavior",
        "",
        "The E6 no-verdict ablation compares a deterministic rule-only baseline, the E6-full setting with verdict-like tool fields, and E6-no-verdict variants that remove those fields. This directly tests whether the model is adding value beyond following a visible tool verdict.",
        "",
        *e6_table_lines,
        "",
        "The comparison is model-dependent. Qwen E6-no-verdict remains close to Qwen E6-full, preserving high correct recall but repeating four false accepts. DeepSeek E6-no-verdict removes false accepts on this cohort, but its correct recall drops to 52.38% and escalation rises to 14.29%. The result supports a risk-policy interpretation: removing verdict-like fields can reduce unsafe accepts for some models, but the gain may come from abstention rather than semantic discrimination.",
        "",
        "The uncertainty summary reinforces the same boundary. Wilson 95% confidence intervals are wide because the cohort has 21 correct and 77 incorrect candidates, so point-estimate differences should not be overstated. The intervals support bounded comparison and risk reporting rather than a claim of stable LLM superiority over the deterministic baseline.",
        "",
        *uncertainty_table_lines,
        "",
        "### 5.3 RQ3: Tool-contestation supported risk triage, not strict correction",
        "",
        f"On EVP-8-HARD, tool-contestation covered 47 candidates for both Qwen and DeepSeek. For the known tool false-accept opportunity set, DeepSeek shifted {deepseek_opp.get('candidate_count')} tool false accepts to {deepseek_opp.get('escalated')} escalations and {deepseek_opp.get('corrected_to_reject')} strict rejects. Qwen shifted {qwen_opp.get('candidate_count')} tool false accepts to {qwen_opp.get('escalated')} escalations, with {qwen_opp.get('corrected_to_reject')} strict rejects and {qwen_opp.get('repeated_accept')} repeated accept. The supported interpretation is therefore risk triage through escalation, not semantic correction of wrong patches.",
        "",
        "Opportunity-set uncertainty is also large. Safe handling was high because most tool false accepts moved to escalation, but strict correction remained zero for both models. The Wilson intervals therefore support the weaker claim that tool-contestation can route known risky accepts away from autonomous acceptance; they do not support a claim that it reliably identifies semantic incorrectness.",
        "",
        *tool_contestation_ci_table_lines,
        "",
        "### 5.4 RQ4: Realistic hard-negative acquisition remained a boundary",
        "",
        f"The fresh realistic branch produced {realistic.get('visible_pass_hidden_fail_count')} visible-pass/hidden-fail cases, below the predeclared target of {realistic.get('minimum_count')}, and covered {len(realistic.get('visible_pass_hidden_fail_projects') or [])} projects rather than the required {realistic.get('minimum_projects')}. It is therefore a source-acquisition and gate-readiness negative result, not a verifier-ready main experiment.",
        "",
        "## 6. Discussion",
        "",
        "The results support a bounded but practically important interpretation. LLM-based patch verifiers are not only functions of model identity; they are functions of the evidence boundary. A model may become conservative, tool-dependent, or saturated depending on how patch evidence is presented. This matters for software quality because a deployment pipeline must decide whether escalation is acceptable, whether tool summaries should be trusted, and when a patch should remain under human review. Human-automation research has long warned that automation can be misused or over-trusted, so the evidence boundary should be reported rather than hidden [parasuraman_riley_1997_automation].",
        "",
        "The strongest contribution is methodological rather than algorithmic. EVP-8 makes evidence visibility explicit, separates model-visible information from evaluator-only labels, and forces each result to state whether it measures acceptance, false acceptance, strict rejection, or escalation.",
        "",
        "The most important rival explanation is that the observed behavior is a setup artifact. The final setting-validity audit reduces this risk but does not erase all limitations. It shows that run coverage, parse validity, post-execution label joins, prompt-boundary checks, and claim boundaries are in place. It also identifies remaining threats: cohort diversity is limited, prompt formatting can influence behavior, and the realistic three-project hard-negative gate remains blocked.",
        "",
        "The realistic hard-negative branch should be read as a boundary result. It demonstrates that constructing fresh visible-pass/hidden-fail cases is feasible but not yet ready as a main verifier experiment because the predeclared three-project gate failed. This negative result is valuable for reproducibility and source-acquisition planning, but it should not be used to strengthen the verifier claim.",
        "",
        "The paper should therefore avoid a stronger interpretation. It does not show that LLMs reliably verify patch correctness. It shows that evidence visibility shapes risk behavior in candidate patch verification and that some apparent improvements are better understood as conservative routing rather than correctness proof.",
        "",
        "![Figure 3. Claim boundary and setting-validity map.](../figures/ccfc/ccfc_fig3_claim_boundary.png)",
        "",
        f"**Figure 3. {fig3['title']}.** {fig3['conclusion']} The map connects each supported claim to tracked aggregate evidence, separates passed validity gates from the blocked realistic gate, and lists overclaims that the manuscript must not make. Source assets: `docs/figures/ccfc/ccfc_fig3_claim_boundary.pdf`, `.svg`, and `.png`.",
        "",
        "## 7. Threats to Validity",
        "",
        "Internal validity may be affected by prompt wording, output schema, and evidence formatting. We mitigate this by using frozen packet sets, tracked prompt-boundary audits, raw-output-free summaries, and post-run matrix checks, but the findings remain tied to the evaluated protocol versions.",
        "",
        "Construct validity is limited by the accept/reject/escalate decision space and by the evaluator label boundary. The oracle problem means that hidden labels should be treated as post-decision evaluation evidence, not as model-visible truth [barr_tse_2015_oracle_problem]. Escalation is useful as a human-review routing decision, but it is not strict correction. The manuscript therefore separates strict correction from safe handling.",
        "",
        "External validity is bounded by the EVP-8 candidate set, the EVP-8-HARD controlled cohort, and the selected models. The repaired main result now spans Qwen, DeepSeek, and Gemini, but it is still not a broad-model result. The realistic hard-negative branch provides useful source-acquisition evidence but did not pass the three-project verifier-readiness gate. We therefore report it as a negative boundary rather than as main verifier evidence.",
        "",
        "## 8. Conclusion",
        "",
        "This study introduces EVP-8 as a hidden-evaluator protocol for measuring evidence-conditioned LLM patch-verification behavior. The supported results come from repaired Qwen, DeepSeek, and Gemini label-conditioned analyses, E6 rule-only/no-verdict ablations, and tool-contestation audits. The practical value is risk triage under explicit evidence boundaries, not reliable autonomous patch correctness verification. A stable CCF-C manuscript should therefore present the work as a bounded methods-and-measurement contribution with transparent metrics, baselines, excluded settings, and threat boundaries.",
        "",
        "## Reference Support Records",
        "",
        "The current Markdown draft uses citation keys pending final venue-specific BibTeX conversion. The cited support records are:",
        "",
    ]
    for record in claim_map["reference_records"]:
        lines.append(f"- `{record['key']}`: {record['reference']}")
    lines += [
        "",
        "## Figure Asset Summary" if figures_generated else "## Planned Figures",
        "",
        (
            "Figures are placed inline above and generated with the Python/matplotlib backend under `docs/figures/ccfc/`."
            if figures_generated
            else "Figure generation is pending backend selection. The current figure plan is:"
        ),
        "",
    ]
    for figure in claim_map["figure_plan"]:
        outputs = figure.get("outputs") or []
        output_text = f" Outputs: {', '.join(outputs)}." if outputs else ""
        conclusion = str(figure["conclusion"]).rstrip(".")
        lines.append(f"- {figure['id']}: {figure['title']} — {conclusion}.{output_text}")
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
