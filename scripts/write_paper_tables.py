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
    evp7_summary: dict[str, Any],
    evp7_quality: dict[str, Any],
    evp7_statistics: dict[str, Any],
    evp7_utility: dict[str, Any],
    evp7_tool_attribution: dict[str, Any],
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
            "| evidence | records | decisions | invalid | false accept | accepted precision | correct recall | evidence gain vs E0 |",
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
    evp7_summary: dict[str, Any],
    evp7_quality: dict[str, Any],
    evp7_statistics: dict[str, Any],
    evp7_utility: dict[str, Any],
    evp7_tool_attribution: dict[str, Any],
) -> str:
    parts = [
        "% Generated paper tables. Requires booktabs.",
        latex_count_table("Dataset by project.", "tab:dataset-projects", dataset["project_counts"], "Project"),
        latex_count_table("Candidate types.", "tab:candidate-types", dataset["candidate_type_counts"], "Candidate type"),
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
        "\\begin{tabular}{lrrrrrr}\n"
        "\\toprule\n"
        "Baseline & Accepted precision & False accept & Correct recall & False reject & Escalation & Invalid output \\\\\n"
        "\\midrule\n"
        + "\n".join(
            baseline_latex_row(BASELINE_LABELS.get(key, key), metrics["groups"][key])
            for key in sorted(metrics["groups"])
        )
        + "\n\\bottomrule\n"
        "\\end{tabular}\n"
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
        "\\begin{tabular}{lrrrrrrr}\n"
        "\\toprule\n"
        "Evidence & Records & Accept & Escalate & Reject & False accept & Correct recall & Evidence gain \\\\\n"
        "\\midrule\n"
        + rows
        + "\n\\bottomrule\n"
        "\\end{tabular}\n"
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
        "\\begin{tabular}{lrrrr}\n"
        "\\toprule\n"
        "Evidence & False accept Wilson 95\\% CI & Correct recall Wilson 95\\% CI & Escalation bootstrap 95\\% CI & Utility delta bootstrap 95\\% CI \\\\\n"
        "\\midrule\n"
        + "\n".join(rows)
        + "\n\\bottomrule\n"
        "\\end{tabular}\n"
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
        "\\begin{tabular}{llrrrr}\n"
        "\\toprule\n"
        "Evidence & Tool condition & Agreement & LLM accept outside tool & Recovered tool false accepts & Downgraded tool true accepts \\\\\n"
        "\\midrule\n"
        + "\n".join(rows)
        + "\n\\bottomrule\n"
        "\\end{tabular}\n"
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate paper-ready tables from current tracked outputs.")
    parser.add_argument("--dataset-summary", default="outputs/patch_verification_pilot_001/dataset_summary.json")
    parser.add_argument("--validation-summary", default="outputs/patch_verification_pilot_001/validation_summary.json")
    parser.add_argument("--metrics", default="outputs/patch_verification_pilot_001/metrics.json")
    parser.add_argument("--reproducibility", default="outputs/reproducibility/pilot_compare.json")
    parser.add_argument("--evp7-summary", default="data/reviews/evp7_g5_llm_376_full_summary.json")
    parser.add_argument("--evp7-quality-audit", default="data/reviews/evp7_g5_376_full_quality_audit.json")
    parser.add_argument("--evp7-statistics", default="data/reviews/evp7_g5_376_statistical_analysis.json")
    parser.add_argument("--evp7-utility-sensitivity", default="data/reviews/evp7_g5_376_utility_sensitivity.json")
    parser.add_argument("--evp7-tool-attribution", default="data/reviews/evp7_g5_376_tool_attribution.json")
    parser.add_argument("--out-md", default="docs/paper/generated_tables.md")
    parser.add_argument("--out-tex", default="docs/paper/generated_tables.tex")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset = read_json(Path(args.dataset_summary))
    validation = read_json(Path(args.validation_summary))
    metrics = read_json(Path(args.metrics))
    repro = read_json(Path(args.reproducibility))
    evp7_summary = read_json(Path(args.evp7_summary))
    evp7_quality = read_json(Path(args.evp7_quality_audit))
    evp7_statistics = read_json(Path(args.evp7_statistics))
    evp7_utility = read_json(Path(args.evp7_utility_sensitivity))
    evp7_tool_attribution = read_json(Path(args.evp7_tool_attribution))
    write_text(
        Path(args.out_md),
        build_markdown(
            dataset,
            validation,
            metrics,
            repro,
            evp7_summary,
            evp7_quality,
            evp7_statistics,
            evp7_utility,
            evp7_tool_attribution,
        ),
    )
    write_text(
        Path(args.out_tex),
        build_latex(
            dataset,
            validation,
            metrics,
            repro,
            evp7_summary,
            evp7_quality,
            evp7_statistics,
            evp7_utility,
            evp7_tool_attribution,
        ),
    )
    print(json.dumps({"out_md": args.out_md, "out_tex": args.out_tex}, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
