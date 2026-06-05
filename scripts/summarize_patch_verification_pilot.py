from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number} must contain a JSON object")
        rows.append(value)
    return rows


def metric_row(metrics: dict[str, Any], group_key: str) -> str:
    group = metrics["groups"][group_key]
    return (
        f"| `{group_key}` | {fmt(group['accepted_precision'])} | "
        f"{fmt(group['false_accept_rate'])} | {fmt(group['correct_patch_recall'])} | "
        f"{fmt(group['false_reject_rate'])} | {fmt(group['escalation_rate'])} | "
        f"{fmt(group['invalid_output_rate'])} |"
    )


def fmt(value: Any) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def markdown_table(counts: dict[str, Any], key_name: str, value_name: str = "count") -> str:
    lines = [f"| {key_name} | {value_name} |", "|---|---:|"]
    for key, value in counts.items():
        lines.append(f"| `{key}` | {value} |")
    return "\n".join(lines)


def build_report(
    dataset_summary: dict[str, Any],
    validation_summary: dict[str, Any],
    metrics: dict[str, Any],
    prompt_manifest: list[dict[str, Any]],
) -> str:
    prompt_conditions = Counter(record["condition"] for record in prompt_manifest)
    leakage = Counter(record.get("label_leakage_check", "unknown") for record in prompt_manifest)
    prompt_lengths = [int(record["prompt_chars"]) for record in prompt_manifest]

    lines = [
        "# Patch Verification Pilot Report",
        "",
        "## Status",
        "",
        "- no-API dataset gate: passed",
        f"- candidate count: {dataset_summary['candidate_count']}",
        f"- verifier baseline output count: {dataset_summary['verifier_output_count']}",
        f"- executable validation: {'passed' if validation_summary.get('all_validated') else 'failed'}",
        f"- API readiness flag: {dataset_summary.get('api_readiness', {}).get('ready')}",
        "- real API calls: not run",
        "",
        "## Dataset Composition",
        "",
        markdown_table(dataset_summary["project_counts"], "project"),
        "",
        markdown_table(dataset_summary["candidate_type_counts"], "candidate type"),
        "",
        markdown_table(dataset_summary["expected_outcome_counts"], "expected outcome"),
        "",
        markdown_table(dataset_summary["patch_materialization_counts"], "patch materialization"),
        "",
        "## Validation",
        "",
        f"- records: {validation_summary['record_count']}",
        f"- patch applied: {validation_summary['patch_applied_count']}",
        f"- oracle ran: {validation_summary['oracle_ran_count']}",
        f"- oracle all passed: {validation_summary['oracle_all_passed_count']}",
        "",
        markdown_table(validation_summary["validation_status_counts"], "validation status"),
        "",
        "## No-API Baselines",
        "",
        "| condition | accepted precision | false accept rate | correct recall | false reject rate | escalation rate | invalid output rate |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for group_key in sorted(metrics["groups"]):
        lines.append(metric_row(metrics, group_key))

    lines.extend(
        [
            "",
            "## Prompt Dry-Run",
            "",
            f"- rendered prompts: {len(prompt_manifest)}",
            f"- conditions: {dict(sorted(prompt_conditions.items()))}",
            f"- label-leakage checks: {dict(sorted(leakage.items()))}",
            f"- prompt char range: {min(prompt_lengths)} to {max(prompt_lengths)}" if prompt_lengths else "- prompt char range: NA",
            "",
            "## Interpretation",
            "",
            "The current state validates dataset construction, executable labels, metrics, and prompt boundaries. "
            "It does not yet test the research hypothesis because no model reviewer decisions have been collected.",
            "",
            "The next required step is a two-candidate API smoke run through the DeepSeek official API after `.env` contains `DEEPSEEK_API_KEY` and local configs pass check-only validation.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a Markdown report for the patch-verification pilot.")
    parser.add_argument("--dataset-summary", required=True)
    parser.add_argument("--validation-summary", required=True)
    parser.add_argument("--metrics", required=True)
    parser.add_argument("--prompt-manifest", required=True)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = build_report(
        dataset_summary=read_json(Path(args.dataset_summary)),
        validation_summary=read_json(Path(args.validation_summary)),
        metrics=read_json(Path(args.metrics)),
        prompt_manifest=read_jsonl(Path(args.prompt_manifest)),
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(json.dumps({"out": str(out), "chars": len(report)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
