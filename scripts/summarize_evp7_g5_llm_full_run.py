"""Summarize ignored EVP-7 G5 full-run outputs into tracked artifacts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REVIEWS = REPO_ROOT / "outputs" / "evp7_g5_llm_248_full" / "reviews.jsonl"
DEFAULT_METRICS = REPO_ROOT / "outputs" / "evp7_g5_llm_248_full" / "metrics.json"
DEFAULT_WORKFLOW = REPO_ROOT / "outputs" / "evp7_g5_llm_248_full" / "summary.json"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "reviews" / "evp7_g5_llm_full_run_summary.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp7_g5_llm_full_run_result.md"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def summarize(reviews_path: Path, metrics_path: Path, workflow_path: Path) -> dict[str, Any]:
    reviews = read_jsonl(reviews_path)
    metrics = read_json(metrics_path)
    workflow = read_json(workflow_path)
    parse_counts = Counter(record.get("parse_status") for record in reviews)
    decision_counts = Counter(_decision(record) for record in reviews)
    invalid_records = [
        {
            "evidence_packet_id": record.get("evidence_packet_id"),
            "candidate_id": record.get("candidate_id"),
            "evidence_level": record.get("evidence_level"),
            "invalid_reason": record.get("invalid_reason"),
            "raw_response_chars": len(record.get("raw_response_text") or ""),
            "prompt_chars": record.get("prompt_chars"),
        }
        for record in reviews
        if record.get("parse_status") != "valid"
    ]
    return {
        "cohort_id": "EVP-7",
        "run_name": "evp7_g5_llm_full_run",
        "provider": _unique_value(reviews, "api_provider"),
        "model": _unique_value(reviews, "model"),
        "prompt_id": _unique_value(reviews, "prompt_id"),
        "workflow": {
            "mode": workflow.get("mode"),
            "concurrency": workflow.get("concurrency"),
            "review_count": workflow.get("review_count"),
            "api_call_attempted": workflow.get("api_call_attempted"),
            "model_call_attempted": workflow.get("model_call_attempted"),
            "total_cost_usd_reported_by_runner": workflow.get("total_cost_usd"),
            "cost_note": "DeepSeek response did not expose billable cost in the stored usage field; runner total is not a billing estimate.",
        },
        "quality": {
            "review_count": len(reviews),
            "unique_review_ids": len({record.get("review_id") for record in reviews}),
            "parse_counts": dict(sorted(parse_counts.items())),
            "decision_counts": dict(sorted(decision_counts.items())),
            "invalid_output_count": len(invalid_records),
            "invalid_output_rate": round(len(invalid_records) / len(reviews), 6) if reviews else None,
            "invalid_records": invalid_records,
            "raw_outputs_tracked": False,
        },
        "metrics": {
            "run_kind": metrics.get("run_kind"),
            "g5_metric_scaffold": metrics.get("g5_metric_scaffold"),
            "g5_signal_claim_status": metrics.get("g5_signal_claim_status"),
            "analysis_boundary": metrics.get("analysis_boundary"),
            "metric_groups": metrics.get("metric_groups"),
            "signal_preview": metrics.get("signal_preview"),
        },
    }


def _decision(record: dict[str, Any]) -> str:
    if record.get("parse_status") != "valid":
        return "invalid_output"
    parsed = record.get("parsed_output")
    if not isinstance(parsed, dict):
        return "invalid_output"
    return str(parsed.get("decision", "invalid_output"))


def _unique_value(records: list[dict[str, Any]], key: str) -> str | None:
    values = sorted({str(record.get(key)) for record in records if record.get(key) is not None})
    if len(values) == 1:
        return values[0]
    return ",".join(values) if values else None


def render_markdown(summary: dict[str, Any]) -> str:
    workflow = summary["workflow"]
    quality = summary["quality"]
    metrics = summary["metrics"]
    lines = [
        "# EVP-7 G5 LLM Full Run Result",
        "",
        "This tracked summary excludes raw model responses. Raw outputs remain under ignored `outputs/`.",
        "",
        "## Run",
        "",
        f"- Provider: `{summary['provider']}`",
        f"- Model: `{summary['model']}`",
        f"- Prompt: `{summary['prompt_id']}`",
        f"- Concurrency: {workflow['concurrency']}",
        f"- Review count: {workflow['review_count']}",
        f"- API calls attempted: {str(workflow['api_call_attempted']).lower()}",
        f"- Model calls attempted: {str(workflow['model_call_attempted']).lower()}",
        f"- Runner-reported cost: {workflow['total_cost_usd_reported_by_runner']}",
        f"- Cost note: {workflow['cost_note']}",
        "",
        "## Quality",
        "",
        f"- Unique review ids: {quality['unique_review_ids']}",
        f"- Parse counts: `{json.dumps(quality['parse_counts'], sort_keys=True)}`",
        f"- Decision counts: `{json.dumps(quality['decision_counts'], sort_keys=True)}`",
        f"- Invalid output count: {quality['invalid_output_count']}",
        f"- Invalid output rate: {quality['invalid_output_rate']}",
        "",
        "## Metrics",
        "",
        f"- Run kind: `{metrics['run_kind']}`",
        f"- G5 metric scaffold: `{metrics['g5_metric_scaffold']}`",
        f"- G5 signal claim status: `{metrics['g5_signal_claim_status']}`",
        f"- Boundary: {metrics['analysis_boundary']}",
        "",
        "| Evidence | Records | Decisions | Invalid | FAR | Accepted precision | Correct recall | Evidence gain vs E0 |",
        "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for level, group in sorted((metrics["metric_groups"] or {}).items()):
        lines.append(
            "| {level} | {records} | `{decisions}` | {invalid} | {far} | {precision} | {recall} | {gain} |".format(
                level=level,
                records=group.get("record_count"),
                decisions=json.dumps(group.get("decision_counts"), sort_keys=True),
                invalid=group.get("invalid_output_rate"),
                far=group.get("false_accept_rate"),
                precision=group.get("accepted_precision"),
                recall=group.get("correct_recall"),
                gain=group.get("evidence_gain_vs_e0"),
            )
        )
    lines.extend(["", "## Invalid Records", ""])
    if quality["invalid_records"]:
        for record in quality["invalid_records"]:
            lines.append(
                "- `{evidence_packet_id}` ({evidence_level}): {invalid_reason}; raw chars={raw_response_chars}".format(
                    **record
                )
            )
    else:
        lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviews", type=Path, default=DEFAULT_REVIEWS)
    parser.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    parser.add_argument("--workflow", type=Path, default=DEFAULT_WORKFLOW)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    args = parser.parse_args()

    summary = summarize(args.reviews, args.metrics, args.workflow)
    write_json(args.json_out, summary)
    write_text(args.md_out, render_markdown(summary))
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
