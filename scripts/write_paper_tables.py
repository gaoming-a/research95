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


def build_markdown(dataset: dict[str, Any], validation: dict[str, Any], metrics: dict[str, Any], repro: dict[str, Any]) -> str:
    lines = [
        "# Paper Tables: Pre-API Patch Verification",
        "",
        "These tables are generated from current no-API outputs. They do not include real model-review results.",
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


def build_latex(dataset: dict[str, Any], validation: dict[str, Any], metrics: dict[str, Any], repro: dict[str, Any]) -> str:
    parts = [
        "% Generated pre-API paper tables. Requires booktabs.",
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate paper-ready pre-API tables from current outputs.")
    parser.add_argument("--dataset-summary", default="outputs/patch_verification_pilot_001/dataset_summary.json")
    parser.add_argument("--validation-summary", default="outputs/patch_verification_pilot_001/validation_summary.json")
    parser.add_argument("--metrics", default="outputs/patch_verification_pilot_001/metrics.json")
    parser.add_argument("--reproducibility", default="outputs/reproducibility/pilot_compare.json")
    parser.add_argument("--out-md", default="docs/paper/generated_tables.md")
    parser.add_argument("--out-tex", default="docs/paper/generated_tables.tex")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset = read_json(Path(args.dataset_summary))
    validation = read_json(Path(args.validation_summary))
    metrics = read_json(Path(args.metrics))
    repro = read_json(Path(args.reproducibility))
    write_text(Path(args.out_md), build_markdown(dataset, validation, metrics, repro))
    write_text(Path(args.out_tex), build_latex(dataset, validation, metrics, repro))
    print(json.dumps({"out_md": args.out_md, "out_tex": args.out_tex}, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
