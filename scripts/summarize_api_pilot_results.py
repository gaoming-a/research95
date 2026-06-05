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
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number} must contain a JSON object")
        records.append(value)
    return records


def fmt(value: Any) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def markdown_count_table(title: str, counts: Counter[str] | dict[str, Any]) -> list[str]:
    lines = [f"## {title}", "", "| item | count |", "|---|---:|"]
    for key, value in sorted(dict(counts).items()):
        lines.append(f"| `{key}` | {value} |")
    lines.append("")
    return lines


def metrics_table(metrics: dict[str, Any]) -> list[str]:
    lines = [
        "## Metrics",
        "",
        "| group | accepted precision | false accept rate | correct recall | false reject rate | escalation rate | invalid output rate | records |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for group_key, group in sorted(metrics.get("groups", {}).items()):
        lines.append(
            f"| `{group_key}` | {fmt(group.get('accepted_precision'))} | "
            f"{fmt(group.get('false_accept_rate'))} | {fmt(group.get('correct_patch_recall'))} | "
            f"{fmt(group.get('false_reject_rate'))} | {fmt(group.get('escalation_rate'))} | "
            f"{fmt(group.get('invalid_output_rate'))} | {fmt(group.get('records'))} |"
        )
    lines.append("")
    return lines


def validate_review_metric_consistency(reviews: list[dict[str, Any]], metrics: dict[str, Any]) -> None:
    metric_count = int(metrics.get("verifier_output_count", -1))
    if metric_count != len(reviews):
        raise ValueError(
            f"review count mismatch: reviews.jsonl has {len(reviews)} records, "
            f"metrics.json reports {metric_count}"
        )


def build_report(
    reviews: list[dict[str, Any]],
    metrics: dict[str, Any],
    run_summary_path: Path | None,
) -> str:
    validate_review_metric_consistency(reviews, metrics)

    models = Counter(str(record.get("model", "unknown")) for record in reviews)
    conditions = Counter(str(record.get("condition", "unknown")) for record in reviews)
    decisions = Counter(str(record.get("decision", "unknown")) for record in reviews)
    prompt_versions = Counter(str(record.get("prompt_version", "unknown")) for record in reviews)
    mock_count = sum(1 for record in reviews if record.get("mock_run"))
    invalid_count = decisions.get("invalid_output", 0)
    total_cost = sum(float(record.get("cost_usd") or 0.0) for record in reviews)
    run_dates = sorted({str(record.get("run_date_utc", "unknown")) for record in reviews})
    report_kind = "mock pipeline check" if mock_count else "real API pilot"

    lines = [
        "# Patch Verification API Pilot Result Report",
        "",
        "## Status",
        "",
        f"- report kind: {report_kind}",
        f"- reviewer records: {len(reviews)}",
        f"- mock records: {mock_count}",
        f"- invalid outputs: {invalid_count}",
        f"- recorded cost usd: {total_cost:.6f}",
        f"- first run timestamp UTC: {run_dates[0] if run_dates else 'unknown'}",
        f"- last run timestamp UTC: {run_dates[-1] if run_dates else 'unknown'}",
        f"- run summary: `{run_summary_path.as_posix() if run_summary_path else 'not provided'}`",
        "",
    ]

    if mock_count:
        lines.extend(
            [
                "## Boundary",
                "",
                "This report contains mock reviewer outputs. It verifies the local reporting pipeline only and must not be used as model evidence, experiment results, or paper findings.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "## Boundary",
                "",
                "This report summarizes real model reviewer decisions from `reviews.jsonl`. Interpretation still depends on dataset validity, model selection, and failure-example inspection.",
                "",
            ]
        )

    lines.extend(markdown_count_table("Models", models))
    lines.extend(markdown_count_table("Conditions", conditions))
    lines.extend(markdown_count_table("Decisions", decisions))
    lines.extend(markdown_count_table("Prompt Versions", prompt_versions))
    lines.extend(metrics_table(metrics))

    lines.extend(
        [
            "## Interpretation Gate",
            "",
            "A result is worth writing into the paper only if `evidence_first` reduces false accepts relative to `llm_only`, accepted precision improves, correct-patch recall does not collapse, and the change is not explained by rejecting or escalating nearly everything.",
            "",
            "After a real run, inspect at least three accepted false positives, three rejected correct patches if present, and three evidence-first escalations before drawing conclusions.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize patch-verification API pilot outputs.")
    parser.add_argument("--reviews", required=True, help="API pilot reviews JSONL.")
    parser.add_argument("--metrics", required=True, help="API pilot metrics JSON.")
    parser.add_argument("--run-summary", help="Optional run summary Markdown path.")
    parser.add_argument("--out", required=True, help="Markdown report output path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    reviews = read_jsonl(Path(args.reviews))
    metrics = read_json(Path(args.metrics))
    run_summary = Path(args.run_summary) if args.run_summary else None
    report = build_report(reviews=reviews, metrics=metrics, run_summary_path=run_summary)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(json.dumps({"out": str(out), "chars": len(report)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
