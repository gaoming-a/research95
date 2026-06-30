from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


BASELINE_LABELS = {
    "no_api_accept_all::accept_all": "accept-all",
    "no_api_reject_all::reject_all": "reject-all",
    "no_api_oracle_upper_bound::oracle_upper_bound": "oracle upper bound",
}

EVIDENCE_LEVELS = ("E0", "E2", "E4", "E6")
EVP8_EVIDENCE_LEVELS = ("E0", "E1", "E2", "E3", "E4", "E5", "E6")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fmt(value: Any) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def fmt_latex(value: Any) -> str:
    if value is None:
        return "--"
    return fmt(value)


def md_count_table(title: str, counts: dict[str, Any], key_label: str) -> list[str]:
    lines = [f"## {title}", "", f"| {key_label} | count |", "|---|---:|"]
    for key, value in counts.items():
        lines.append(f"| `{key}` | {value} |")
    lines.append("")
    return lines


def latex_count_table(caption: str, label: str, counts: dict[str, Any], key_label: str) -> str:
    rows = "\n".join(f"{escape_latex(str(key))} & {value} \\\\" for key, value in counts.items())
    return "\n".join(
        [
            "\\begin{table}[t]",
            "\\centering",
            f"\\caption{{{escape_latex(caption)}}}",
            f"\\label{{{label}}}",
            "\\begin{tabular}{lr}",
            "\\toprule",
            f"{escape_latex(key_label)} & Count \\\\",
            "\\midrule",
            rows,
            "\\bottomrule",
            "\\end{tabular}",
            "\\end{table}",
            "",
        ]
    )


def fit_width_table(tabular: str) -> str:
    return "\n".join(
        [
            r"\resizebox{\textwidth}{!}{%",
            tabular,
            "}",
        ]
    )


def escape_latex(text: str) -> str:
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def build_markdown(
    dataset: dict[str, Any],
    validation: dict[str, Any],
    metrics: dict[str, Any],
    repro: dict[str, Any],
    evp7_workload: dict[str, Any],
    evp7_summary: dict[str, Any],
    evp7_quality: dict[str, Any],
    evp7_statistics: dict[str, Any],
    evp7_utility: dict[str, Any],
    evp7_tool_attribution: dict[str, Any],
    evp8_synthesis: dict[str, Any],
    evp8_cost_accounting: dict[str, Any],
) -> str:
    lines = [
        "# Paper Tables",
        "",
        "These tables are generated from current tracked artifacts. Raw model responses are not included.",
        "",
    ]
    lines.extend(md_count_table("Dataset By Project", dataset["project_counts"], "project"))
    lines.extend(md_count_table("Candidate Types", dataset["candidate_type_counts"], "candidate type"))
    lines.extend(md_count_table("Expected Outcomes", dataset["expected_outcome_counts"], "expected outcome"))
    lines.extend(md_count_table("Patch Materialization", dataset["patch_materialization_counts"], "materialization"))
    lines.extend(evp7_workload_markdown(evp7_workload))
    lines.extend(
        [
            "## Executable Validation",
            "",
            "| item | value |",
            "|---|---:|",
            f"| records | {validation['record_count']} |",
            f"| patch applied | {validation['patch_applied_count']} |",
            f"| oracle ran | {validation['oracle_ran_count']} |",
            f"| oracle all passed | {validation['oracle_all_passed_count']} |",
            f"| all validated | {validation['all_validated']} |",
            "",
            "## No-API Baselines",
            "",
            "| baseline | accepted precision | false accept rate | correct recall | false reject rate | escalation rate | invalid output rate |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for key in sorted(metrics["groups"]):
        group = metrics["groups"][key]
        label = BASELINE_LABELS.get(key, key)
        lines.append(
            f"| {label} | {fmt(group['accepted_precision'])} | {fmt(group['false_accept_rate'])} | "
            f"{fmt(group['correct_patch_recall'])} | {fmt(group['false_reject_rate'])} | "
            f"{fmt(group['escalation_rate'])} | {fmt(group['invalid_output_rate'])} |"
        )
    lines.extend(
        [
            "",
            "## EVP-7 G5 Evidence Visibility Results",
            "",
            f"- cohort: 20 tasks / 94 candidates / 376 evidence packets",
            f"- provider/model: `{evp7_summary['provider']}` / `{evp7_summary['model']}`",
            f"- quality audit: `{evp7_quality['quality_status']}`",
            f"- cost note: {evp7_summary['workflow']['cost_note']}",
            f"- cost summary: `{json.dumps(evp7_summary['workflow'].get('cost_summary'), sort_keys=True)}`",
            "",
            "| evidence | records | decisions | invalid | false accept | accepted precision | correct recall | Evidence Gain vs E0 |",
            "|---|---:|---|---:|---:|---:|---:|---:|",
        ]
    )
    for level in EVIDENCE_LEVELS:
        group = evp7_summary["metrics"]["metric_groups"][level]
        lines.append(
            f"| {level} | {group['record_count']} | `{json.dumps(group['decision_counts'], sort_keys=True)}` | "
            f"{fmt(group['invalid_output_rate'])} | {fmt(group['false_accept_rate'])} | "
            f"{fmt(group['accepted_precision'])} | {fmt(group['correct_recall'])} | "
            f"{fmt(group['evidence_gain_vs_e0'])} |"
    )
    lines.extend(evp7_statistics_markdown(evp7_statistics))
    lines.extend(evp7_utility_markdown(evp7_utility))
    lines.extend(evp7_tool_attribution_markdown(evp7_tool_attribution))
    lines.extend(evp8_five_model_markdown(evp8_synthesis))
    lines.extend(evp8_cost_accounting_markdown(evp8_cost_accounting))
    lines.extend(
        [
            "",
            "## EVP-7 Claim Boundary",
            "",
            "| supported claims | unsupported claims |",
            "|---|---|",
        ]
    )
    supported = evp7_quality.get("supported_claims", [])
    unsupported = evp7_quality.get("unsupported_claims", [])
    row_count = max(len(supported), len(unsupported))
    for index in range(row_count):
        left = supported[index] if index < len(supported) else ""
        right = unsupported[index] if index < len(unsupported) else ""
        lines.append(f"| {left} | {right} |")
    lines.extend(
        [
            "",
            "## Deterministic Reproducibility",
            "",
            "| item | value |",
            "|---|---:|",
            f"| matched | {repro['matched']} |",
            f"| checked deterministic files | {repro['checked_file_count']} |",
            f"| mismatches | {len(repro['mismatches'])} |",
            f"| missing | {len(repro['missing'])} |",
            "",
        ]
    )
    return "\n".join(lines)


def build_latex(
    dataset: dict[str, Any],
    validation: dict[str, Any],
    metrics: dict[str, Any],
    repro: dict[str, Any],
    evp7_workload: dict[str, Any],
    evp7_summary: dict[str, Any],
    evp7_quality: dict[str, Any],
    evp7_statistics: dict[str, Any],
    evp7_utility: dict[str, Any],
    evp7_tool_attribution: dict[str, Any],
    evp8_synthesis: dict[str, Any],
    evp8_cost_accounting: dict[str, Any],
) -> str:
    parts = [
        "% Generated paper tables. Requires booktabs.",
        latex_count_table("Dataset by project.", "tab:dataset-projects", dataset["project_counts"], "Project"),
        latex_count_table("Candidate types.", "tab:candidate-types", dataset["candidate_type_counts"], "Candidate type"),
        evp7_workload_latex_table(evp7_workload),
        "\\begin{table}[t]\n"
        "\\centering\n"
        "\\caption{Executable validation summary.}\n"
        "\\label{tab:validation-summary}\n"
        "\\begin{tabular}{lr}\n"
        "\\toprule\n"
        "Item & Value \\\\\n"
        "\\midrule\n"
        f"Records & {validation['record_count']} \\\\\n"
        f"Patch applied & {validation['patch_applied_count']} \\\\\n"
        f"Oracle ran & {validation['oracle_ran_count']} \\\\\n"
        f"Oracle all passed & {validation['oracle_all_passed_count']} \\\\\n"
        f"All validated & {str(validation['all_validated']).lower()} \\\\\n"
        "\\bottomrule\n"
        "\\end{tabular}\n"
        "\\end{table}\n",
        "\\begin{table*}[t]\n"
        "\\centering\n"
        "\\caption{No-API baseline metrics. These baselines validate metric behavior but are not model-review results.}\n"
        "\\label{tab:no-api-baselines}\n"
        + fit_width_table(
            "\\begin{tabular}{lrrrrrr}\n"
            "\\toprule\n"
            "Baseline & Accepted precision & False accept & Correct recall & False reject & Escalation & Invalid output \\\\\n"
            "\\midrule\n"
            + "\n".join(
                baseline_latex_row(BASELINE_LABELS.get(key, key), metrics["groups"][key])
                for key in sorted(metrics["groups"])
            )
            + "\n\\bottomrule\n"
            "\\end{tabular}"
        )
        + "\n"
        "\\end{table*}\n",
        "\\begin{table}[t]\n"
        "\\centering\n"
        "\\caption{Deterministic no-API reproducibility check.}\n"
        "\\label{tab:reproducibility}\n"
        "\\begin{tabular}{lr}\n"
        "\\toprule\n"
        "Item & Value \\\\\n"
        "\\midrule\n"
        f"Matched & {str(repro['matched']).lower()} \\\\\n"
        f"Checked files & {repro['checked_file_count']} \\\\\n"
        f"Mismatches & {len(repro['mismatches'])} \\\\\n"
        f"Missing & {len(repro['missing'])} \\\\\n"
        "\\bottomrule\n"
        "\\end{tabular}\n"
        "\\end{table}\n",
        evp7_latex_table(evp7_summary),
        evp7_statistics_latex_table(evp7_statistics),
        evp7_utility_latex_table(evp7_utility),
        evp7_tool_attribution_latex_table(evp7_tool_attribution),
        evp8_five_model_latex_table(evp8_synthesis),
        evp8_cost_accounting_latex_table(evp8_cost_accounting),
        evp7_claim_boundary_latex_table(evp7_quality),
    ]
    return "\n\n".join(parts)


def baseline_latex_row(label: str, group: dict[str, Any]) -> str:
    values = [
        escape_latex(label),
        fmt_latex(group["accepted_precision"]),
        fmt_latex(group["false_accept_rate"]),
        fmt_latex(group["correct_patch_recall"]),
        fmt_latex(group["false_reject_rate"]),
        fmt_latex(group["escalation_rate"]),
        fmt_latex(group["invalid_output_rate"]),
    ]
    return " & ".join(values) + r" \\"


def observed_check_value(audit: dict[str, Any], check_name: str, default: Any = None) -> Any:
    checks = audit.get("checks", [])
    if isinstance(checks, dict):
        item = checks.get(check_name)
        if isinstance(item, dict):
            return item.get("observed", default)
        return default
    if isinstance(checks, list):
        for item in checks:
            if isinstance(item, dict) and item.get("check") == check_name:
                return item.get("observed", default)
    return default


def build_evp7_workload(
    task_summary: dict[str, Any],
    candidate_summary: dict[str, Any],
    packet_summary: dict[str, Any],
    tool_only_metrics: dict[str, Any],
    evp7_summary: dict[str, Any],
    evp7_quality: dict[str, Any],
    qualitative_cases: dict[str, Any],
) -> dict[str, str]:
    labels = candidate_summary.get("label_with_p2p_broad_counts", {})
    visible_status = packet_summary.get("visible_outcome_status_counts", {})
    tool_summary_status = packet_summary.get("visible_tool_summary_status_counts", {})
    cost_summary = evp7_summary.get("workflow", {}).get("cost_summary", {})
    level_counts = evp7_quality.get("level_counts", {})
    level_count_text = ", ".join(f"{level}={level_counts[level]}" for level in EVIDENCE_LEVELS if level in level_counts)
    regression_count = labels.get("incorrect_regression", 0)
    regression_label = "negative" if regression_count == 1 else "negatives"
    return {
        "Task admission": (
            f"{task_summary['main_task_count']} tasks / {len(task_summary['main_projects'])} projects "
            "admitted through project-level P2P or documented bounded policies."
        ),
        "Candidate construction": (
            f"{candidate_summary['candidate_count']} candidates: "
            f"{labels.get('correct_under_f2p_and_p2p_broad', 0)} correct references, "
            f"{labels.get('incorrect_issue_not_fixed', 0)} issue-not-fixed negatives, "
            f"{regression_count} regression {regression_label}."
        ),
        "Evidence packets": (
            f"{packet_summary['packet_count']} E0/E2/E4/E6 packets for "
            f"{packet_summary['candidate_count']} candidates; G1={packet_summary['g1_packet_completeness']}, "
            f"G2={packet_summary['g2_leakage_audit']}, leakage findings={packet_summary['leakage_findings_count']}."
        ),
        "Visible evidence sources": (
            f"visible tests completed={visible_status.get('completed', 0)}, "
            f"visible errors={visible_status.get('error', 0)}, "
            f"tool summaries complete={tool_summary_status.get('complete', 0)}."
        ),
        "Tool-only baselines": (
            f"{tool_only_metrics['decision_count']} deterministic decisions across "
            f"{len(tool_only_metrics['conditions'])} conditions; G3={tool_only_metrics['g3_baseline_readiness']}."
        ),
        "Real LLM G5 run": (
            f"{evp7_quality['review_count']} DeepSeek G5 records over "
            f"20 tasks / {evp7_quality['candidate_count']} candidates; {level_count_text}; "
            f"invalid rate={fmt(observed_check_value(evp7_quality, 'invalid_output_rate_within_limit', 0.0))}."
        ),
        "Audit and interpretation": (
            f"quality={evp7_quality['quality_status']}; qualitative cases={qualitative_cases['case_count']}; "
            f"cost observability unknown={cost_summary.get('unknown_cost_record_count', 0)}."
        ),
    }


def evp7_workload_markdown(workload: dict[str, str]) -> list[str]:
    lines = [
        "## EVP-7 Workload Ledger",
        "",
        "| pipeline stage | tracked workload evidence |",
        "|---|---|",
    ]
    for stage, evidence in workload.items():
        lines.append(f"| {stage} | {evidence} |")
    lines.append("")
    return lines


def evp7_workload_latex_table(workload: dict[str, str]) -> str:
    rows = "\n".join(
        f"{escape_latex(stage)} & {escape_latex(evidence)} \\\\" for stage, evidence in workload.items()
    )
    return (
        "\\begin{table*}[t]\n"
        "\\centering\n"
        "\\caption{EVP-7 workload ledger. Counts are generated from tracked task, candidate, evidence, baseline, review, and audit summaries; raw model responses are not included.}\n"
        "\\label{tab:evp7-workload-ledger}\n"
        "\\begin{tabular}{p{0.25\\textwidth}p{0.68\\textwidth}}\n"
        "\\toprule\n"
        "Pipeline stage & Tracked workload evidence \\\\\n"
        "\\midrule\n"
        + rows
        + "\n\\bottomrule\n"
        "\\end{tabular}\n"
        "\\end{table*}\n"
    )


def evp7_latex_table(summary: dict[str, Any]) -> str:
    rows = "\n".join(
        evp7_latex_row(level, summary["metrics"]["metric_groups"][level])
        for level in EVIDENCE_LEVELS
    )
    cost = summary["workflow"].get("total_cost_usd_reported_by_runner")
    caption = (
        "\\caption{EVP-7 G5 evidence-visibility results on the 376-packet frozen cohort. "
        + "Runner-estimated total cost was "
        + fmt_latex(cost)
        + " USD.}\n"
    )
    return (
        "\\begin{table*}[t]\n"
        "\\centering\n"
        + caption
        + "\\label{tab:evp7-g5-results}\n"
        + fit_width_table(
            "\\begin{tabular}{lrrrrrrr}\n"
            "\\toprule\n"
            "Evidence & Records & Accept & Escalate & Reject & False accept & Correct recall & Evidence Gain \\\\\n"
            "\\midrule\n"
            + rows
            + "\n\\bottomrule\n"
            "\\end{tabular}"
        )
        + "\n"
        "\\end{table*}\n"
    )


def evp7_latex_row(level: str, group: dict[str, Any]) -> str:
    decisions = group.get("decision_counts", {})
    values = [
        escape_latex(level),
        str(group.get("record_count")),
        str(decisions.get("accept", 0)),
        str(decisions.get("escalate", 0)),
        str(decisions.get("reject", 0)),
        fmt_latex(group.get("false_accept_rate")),
        fmt_latex(group.get("correct_recall")),
        fmt_latex(group.get("evidence_gain_vs_e0")),
    ]
    return " & ".join(values) + r" \\"


def evp7_statistics_markdown(statistics: dict[str, Any]) -> list[str]:
    lines = [
        "",
        "## EVP-7 Statistical Intervals",
        "",
        f"- bootstrap unit: `{statistics['method']['bootstrap_unit']}`",
        f"- bootstrap samples: {statistics['method']['bootstrap_samples']}",
        f"- bootstrap seed: {statistics['method']['bootstrap_seed']}",
        "",
        "| evidence | false accept Wilson 95% CI | correct recall Wilson 95% CI | escalation bootstrap 95% CI | utility delta vs E0 bootstrap 95% CI |",
        "|---|---:|---:|---:|---:|",
    ]
    paired = statistics["paired_deltas_vs_e0"]
    for level in EVIDENCE_LEVELS:
        group = statistics["per_evidence_level"][level]
        bootstrap = statistics["bootstrap_intervals"][level]
        delta = "--"
        if level != "E0":
            delta = interval_text(paired[level]["utility_score"]["bootstrap_ci_95"])
        lines.append(
            f"| {level} | {interval_text(group['wilson_ci_95']['false_accept_rate'])} | "
            f"{interval_text(group['wilson_ci_95']['correct_recall'])} | "
            f"{interval_text(bootstrap['escalation_rate'])} | {delta} |"
        )
    return lines


def evp7_statistics_latex_table(statistics: dict[str, Any]) -> str:
    rows = []
    paired = statistics["paired_deltas_vs_e0"]
    for level in EVIDENCE_LEVELS:
        group = statistics["per_evidence_level"][level]
        bootstrap = statistics["bootstrap_intervals"][level]
        delta = "--"
        if level != "E0":
            delta = interval_text(paired[level]["utility_score"]["bootstrap_ci_95"])
        values = [
            escape_latex(level),
            escape_latex(interval_text(group["wilson_ci_95"]["false_accept_rate"])),
            escape_latex(interval_text(group["wilson_ci_95"]["correct_recall"])),
            escape_latex(interval_text(bootstrap["escalation_rate"])),
            escape_latex(delta),
        ]
        rows.append(" & ".join(values) + r" \\")
    samples = statistics["method"]["bootstrap_samples"]
    return (
        "\\begin{table*}[t]\n"
        "\\centering\n"
        "\\caption{EVP-7 G5 statistical intervals. Wilson intervals are used for binomial rates; candidate-level bootstrap intervals use "
        + str(samples)
        + " deterministic resamples.}\n"
        "\\label{tab:evp7-statistical-intervals}\n"
        + fit_width_table(
            "\\begin{tabular}{lrrrr}\n"
            "\\toprule\n"
            "Evidence & False accept Wilson 95\\% CI & Correct recall Wilson 95\\% CI & Escalation bootstrap 95\\% CI & Utility delta bootstrap 95\\% CI \\\\\n"
            "\\midrule\n"
            + "\n".join(rows)
            + "\n\\bottomrule\n"
            "\\end{tabular}"
        )
        + "\n"
        "\\end{table*}\n"
    )


def evp7_utility_markdown(utility: dict[str, Any]) -> list[str]:
    stability = utility["stability_summary"]
    return [
        "",
        "## EVP-7 Utility Sensitivity",
        "",
        f"- utility formula: `{utility['utility_formula']}`",
        f"- scenario count: {utility['scenario_count']}",
        f"- dominant best level: `{stability['dominant_best_level']}`",
        f"- dominant best-level share: {fmt(stability['dominant_best_level_share'])}",
        f"- dominant ranking: `{stability['dominant_ranking']}`",
        f"- dominant ranking share: {fmt(stability['dominant_ranking_share'])}",
        f"- interpretation: {stability['interpretation']}",
        "",
        "| evidence level | scenarios as best |",
        "|---|---:|",
        *[
            f"| {level} | {utility['best_level_counts'].get(level, 0)} |"
            for level in EVIDENCE_LEVELS
        ],
    ]


def evp7_utility_latex_table(utility: dict[str, Any]) -> str:
    rows = "\n".join(
        f"{escape_latex(level)} & {utility['best_level_counts'].get(level, 0)} \\\\"
        for level in EVIDENCE_LEVELS
    )
    stability = utility["stability_summary"]
    caption = (
        "\\caption{EVP-7 utility sensitivity over false-accept, escalation, and false-reject penalty grids. "
        f"The dominant ranking was {escape_latex(stability['dominant_ranking'])} across "
        f"{fmt(stability['dominant_ranking_share'])} of scenarios.}}\n"
    )
    return (
        "\\begin{table}[t]\n"
        "\\centering\n"
        + caption
        + "\\label{tab:evp7-utility-sensitivity}\n"
        "\\begin{tabular}{lr}\n"
        "\\toprule\n"
        "Evidence level & Scenarios as best \\\\\n"
        "\\midrule\n"
        + rows
        + "\n\\bottomrule\n"
        "\\end{tabular}\n"
        "\\end{table}\n"
    )


def evp7_tool_attribution_markdown(attribution: dict[str, Any]) -> list[str]:
    lines = [
        "",
        "## EVP-7 Tool-Only Attribution",
        "",
        f"- boundary: {attribution['boundary']}",
        "",
        "| evidence | tool condition | agreement | LLM accepts outside tool accepts | recovered tool false accepts | downgraded tool true accepts |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for level in EVIDENCE_LEVELS:
        if level not in attribution["comparisons"]:
            continue
        item = attribution["comparisons"][level]
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
    return lines


def evp7_tool_attribution_latex_table(attribution: dict[str, Any]) -> str:
    rows = []
    for level in EVIDENCE_LEVELS:
        if level not in attribution["comparisons"]:
            continue
        item = attribution["comparisons"][level]
        counts = item["label_interaction_counts"]
        recovery = item["tool_false_accept_recovery"]
        retention = item["tool_true_accept_retention"]
        rows.append(
            " & ".join(
                [
                    escape_latex(level),
                    escape_latex(item["tool_condition"].replace("tool_only_", "")),
                    f"{item['agreement_count']}/{item['record_count']}",
                    str(counts.get("llm_accept_not_tool_accept", 0)),
                    f"{recovery['recovered']}/{recovery['total_tool_false_accepts']}",
                    f"{retention['downgraded']}/{retention['total_tool_true_accepts']}",
                ]
            )
            + r" \\"
        )
    return (
        "\\begin{table*}[t]\n"
        "\\centering\n"
        "\\caption{EVP-7 deterministic tool-only attribution. LLM decisions are compared with the matched visible-test or visible-tool-summary baseline at the same evidence level.}\n"
        "\\label{tab:evp7-tool-attribution}\n"
        + fit_width_table(
            "\\begin{tabular}{llrrrr}\n"
            "\\toprule\n"
            "Evidence & Tool condition & Agreement & LLM accept outside tool & Recovered tool false accepts & Downgraded tool true accepts \\\\\n"
            "\\midrule\n"
            + "\n".join(rows)
            + "\n\\bottomrule\n"
            "\\end{tabular}"
        )
        + "\n"
        "\\end{table*}\n"
    )


def interval_text(interval: dict[str, Any]) -> str:
    if interval.get("low") is None or interval.get("high") is None:
        return "--"
    return f"[{fmt(interval['low'])}, {fmt(interval['high'])}]"


def evp7_claim_boundary_latex_table(quality: dict[str, Any]) -> str:
    supported = quality.get("supported_claims", [])
    unsupported = quality.get("unsupported_claims", [])
    row_count = max(len(supported), len(unsupported))
    rows = []
    for index in range(row_count):
        left = supported[index] if index < len(supported) else ""
        right = unsupported[index] if index < len(unsupported) else ""
        rows.append(f"{escape_latex(left)} & {escape_latex(right)} \\\\")
    return (
        "\\begin{table*}[t]\n"
        "\\centering\n"
        "\\caption{EVP-7 G5 claim boundary.}\n"
        "\\label{tab:evp7-claim-boundary}\n"
        "\\begin{tabular}{p{0.45\\textwidth}p{0.45\\textwidth}}\n"
        "\\toprule\n"
        "Supported in the bounded EVP-7 pilot & Not supported \\\\\n"
        "\\midrule\n"
        + "\n".join(rows)
        + "\n\\bottomrule\n"
        "\\end{tabular}\n"
        "\\end{table*}\n"
    )


def decision_cell(counts: dict[str, Any]) -> str:
    if not isinstance(counts, dict) or not counts:
        return "--"
    ordered = []
    for key, label in (("accept", "A"), ("escalate", "E"), ("reject", "R")):
        value = int(counts.get(key, 0) or 0)
        if value:
            ordered.append(f"{label}{value}")
    return "/".join(ordered) if ordered else "--"


def evp8_five_model_markdown(synthesis: dict[str, Any]) -> list[str]:
    counts_by_level = synthesis.get("per_level_decision_counts_by_model", {})
    models = synthesis.get("expected_model_ids", [])
    lines = [
        "",
        "## EVP-8 Five-Model Decision Patterns",
        "",
        f"- synthesis status: `{synthesis.get('synthesis_status')}`",
        f"- protocol: `{synthesis.get('protocol_id')}`",
        f"- candidate set: `{synthesis.get('candidate_set_id')}`",
        f"- allowed claim: {synthesis.get('allowed_claim')}",
        f"- forbidden claim: {synthesis.get('forbidden_claim')}",
        "",
        "| model | " + " | ".join(EVP8_EVIDENCE_LEVELS) + " |",
        "|---|" + "---:|" * len(EVP8_EVIDENCE_LEVELS),
    ]
    for model in models:
        cells = []
        for level in EVP8_EVIDENCE_LEVELS:
            level_counts = counts_by_level.get(level, {})
            cells.append(decision_cell(level_counts.get(model, {})))
        lines.append(f"| `{model}` | " + " | ".join(cells) + " |")
    lines.append("")
    return lines


def evp8_five_model_latex_table(synthesis: dict[str, Any]) -> str:
    counts_by_level = synthesis.get("per_level_decision_counts_by_model", {})
    models = synthesis.get("expected_model_ids", [])
    rows = []
    for model in models:
        cells = [escape_latex(str(model))]
        for level in EVP8_EVIDENCE_LEVELS:
            level_counts = counts_by_level.get(level, {})
            cells.append(escape_latex(decision_cell(level_counts.get(model, {}))))
        rows.append(" & ".join(cells) + r" \\")
    return (
        "\\begin{table*}[t]\n"
        "\\centering\n"
        "\\scriptsize\n"
        "\\caption{EVP-8 five-model decision patterns on the frozen v0.1 98-candidate by 7-level packet set. Cells report A/E/R counts for accept, escalate, and reject.}\n"
        "\\label{tab:evp8-five-model-patterns}\n"
        + fit_width_table(
            "\\begin{tabular}{lccccccc}\n"
            "\\toprule\n"
            "Model & E0 & E1 & E2 & E3 & E4 & E5 & E6 \\\\\n"
            "\\midrule\n"
            + "\n".join(rows)
            + "\n\\bottomrule\n"
            "\\end{tabular}"
        )
        + "\n"
        "\\end{table*}\n"
    )


def evp8_cost_accounting_markdown(costs: dict[str, Any]) -> list[str]:
    totals = costs.get("totals", {})
    lines = [
        "",
        "## EVP-8 Cost Accounting",
        "",
        f"- status: `{costs.get('cost_status')}`",
        f"- API freeze: `{str(costs.get('decision', {}).get('api_freeze')).lower()}`",
        f"- passed-result USD excluding Qwen: `{fmt(totals.get('passed_result_usd_excluding_qwen'))}`",
        f"- passed Qwen CNY: `{fmt(totals.get('passed_qwen_cny'))}`",
        f"- blocked-attempt USD: `{fmt(totals.get('blocked_attempt_usd'))}`",
        f"- observable USD including blocked attempts, excluding Qwen: `{fmt(totals.get('tracked_plus_blocked_observable_usd_excluding_qwen'))}`",
        "",
        "| category | model | reviews | valid | invalid | USD | CNY |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in costs.get("passed_result_costs", []):
        lines.append(
            f"| passed | `{row.get('configured_model_id')}` | {row.get('review_count')} | "
            f"{row.get('parse_valid_count')} | {row.get('invalid_parse_count')} | "
            f"{fmt(row.get('cost_usd'))} | {fmt(row.get('cost_cny'))} |"
        )
    for row in costs.get("blocked_attempt_costs", []):
        lines.append(
            f"| blocked | `{row.get('configured_model_id')}` | {row.get('review_count')} | "
            f"{row.get('parse_valid_count')} | {row.get('invalid_parse_count')} | "
            f"{fmt(row.get('cost_usd'))} | {fmt(row.get('cost_cny'))} |"
        )
    lines.extend(["", f"- boundary: {costs.get('claim_boundary')}", ""])
    return lines


def evp8_cost_accounting_latex_table(costs: dict[str, Any]) -> str:
    rows = []
    for category, key in (("passed", "passed_result_costs"), ("blocked", "blocked_attempt_costs")):
        for row in costs.get(key, []):
            values = [
                escape_latex(category),
                escape_latex(str(row.get("configured_model_id"))),
                str(row.get("review_count")),
                str(row.get("parse_valid_count")),
                str(row.get("invalid_parse_count")),
                fmt_latex(row.get("cost_usd")),
                fmt_latex(row.get("cost_cny")),
            ]
            rows.append(" & ".join(values) + r" \\")
    return (
        "\\begin{table*}[t]\n"
        "\\centering\n"
        "\\caption{EVP-8 cost accounting. Blocked attempts are cost and execution-risk evidence only; they are not included as valid model-result records.}\n"
        "\\label{tab:evp8-cost-accounting}\n"
        + fit_width_table(
            "\\begin{tabular}{llrrrrr}\n"
            "\\toprule\n"
            "Category & Model & Reviews & Valid & Invalid & USD & CNY \\\\\n"
            "\\midrule\n"
            + "\n".join(rows)
            + "\n\\bottomrule\n"
            "\\end{tabular}"
        )
        + "\n"
        "\\end{table*}\n"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate paper-ready tables from current tracked outputs.")
    parser.add_argument("--dataset-summary", default="outputs/patch_verification_pilot_001/dataset_summary.json")
    parser.add_argument("--validation-summary", default="outputs/patch_verification_pilot_001/validation_summary.json")
    parser.add_argument("--metrics", default="outputs/patch_verification_pilot_001/metrics.json")
    parser.add_argument("--reproducibility", default="outputs/reproducibility/pilot_compare.json")
    parser.add_argument("--evp7-task-summary", default="data/tasks/evp7_manifest_summary.json")
    parser.add_argument("--evp7-candidate-summary", default="data/patches/evp7_candidate_summary.json")
    parser.add_argument("--evp7-packet-summary", default="data/evidence/evp7_evidence_packet_summary.json")
    parser.add_argument("--evp7-tool-only-metrics", default="data/baselines/evp7_tool_only_metrics.json")
    parser.add_argument("--evp7-summary", default="data/reviews/evp7_g5_llm_376_full_summary.json")
    parser.add_argument("--evp7-quality-audit", default="data/reviews/evp7_g5_376_full_quality_audit.json")
    parser.add_argument("--evp7-statistics", default="data/reviews/evp7_g5_376_statistical_analysis.json")
    parser.add_argument("--evp7-utility-sensitivity", default="data/reviews/evp7_g5_376_utility_sensitivity.json")
    parser.add_argument("--evp7-tool-attribution", default="data/reviews/evp7_g5_376_tool_attribution.json")
    parser.add_argument("--evp7-qualitative-cases", default="data/reviews/evp7_g5_376_qualitative_cases.json")
    parser.add_argument("--evp8-five-model-synthesis", default="data/protocols/evp8_five_model_synthesis_v0_1.json")
    parser.add_argument("--evp8-cost-accounting", default="data/reviews/evp8_cost_accounting_summary.json")
    parser.add_argument("--out-md", default="docs/paper/generated_tables.md")
    parser.add_argument("--out-tex", default="docs/paper/generated_tables.tex")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset = read_json(Path(args.dataset_summary))
    validation = read_json(Path(args.validation_summary))
    metrics = read_json(Path(args.metrics))
    repro = read_json(Path(args.reproducibility))
    evp7_task_summary = read_json(Path(args.evp7_task_summary))
    evp7_candidate_summary = read_json(Path(args.evp7_candidate_summary))
    evp7_packet_summary = read_json(Path(args.evp7_packet_summary))
    evp7_tool_only_metrics = read_json(Path(args.evp7_tool_only_metrics))
    evp7_summary = read_json(Path(args.evp7_summary))
    evp7_quality = read_json(Path(args.evp7_quality_audit))
    evp7_statistics = read_json(Path(args.evp7_statistics))
    evp7_utility = read_json(Path(args.evp7_utility_sensitivity))
    evp7_tool_attribution = read_json(Path(args.evp7_tool_attribution))
    evp7_qualitative_cases = read_json(Path(args.evp7_qualitative_cases))
    evp8_synthesis = read_json(Path(args.evp8_five_model_synthesis))
    evp8_cost_accounting = read_json(Path(args.evp8_cost_accounting))
    evp7_workload = build_evp7_workload(
        evp7_task_summary,
        evp7_candidate_summary,
        evp7_packet_summary,
        evp7_tool_only_metrics,
        evp7_summary,
        evp7_quality,
        evp7_qualitative_cases,
    )
    write_text(
        Path(args.out_md),
        build_markdown(
            dataset,
            validation,
            metrics,
            repro,
            evp7_workload,
            evp7_summary,
            evp7_quality,
            evp7_statistics,
            evp7_utility,
            evp7_tool_attribution,
            evp8_synthesis,
            evp8_cost_accounting,
        ),
    )
    write_text(
        Path(args.out_tex),
        build_latex(
            dataset,
            validation,
            metrics,
            repro,
            evp7_workload,
            evp7_summary,
            evp7_quality,
            evp7_statistics,
            evp7_utility,
            evp7_tool_attribution,
            evp8_synthesis,
            evp8_cost_accounting,
        ),
    )
    print(json.dumps({"out_md": args.out_md, "out_tex": args.out_tex}, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
