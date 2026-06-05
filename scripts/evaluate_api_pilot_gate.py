from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_ACCEPTANCE_FLOOR = 0.15
DEFAULT_MAX_RECALL_DROP = 0.25


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number} must contain a JSON object")
        rows.append(value)
    return rows


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fmt(value: Any) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def metric_value(group: dict[str, Any], name: str) -> float | None:
    value = group.get(name)
    if value is None:
        return None
    return float(value)


def select_group(metrics: dict[str, Any], condition: str, explicit_group: str | None) -> tuple[str, dict[str, Any]]:
    groups = metrics.get("groups", {})
    if explicit_group:
        if explicit_group not in groups:
            raise ValueError(f"missing explicit group: {explicit_group}")
        return explicit_group, groups[explicit_group]

    matches = [key for key in groups if key.startswith(f"{condition}::")]
    if len(matches) != 1:
        raise ValueError(
            f"condition {condition!r} matched {len(matches)} groups; pass an explicit group key"
        )
    group_key = matches[0]
    return group_key, groups[group_key]


def delta(new_value: float | None, old_value: float | None) -> float | None:
    if new_value is None or old_value is None:
        return None
    return new_value - old_value


def passed_lower(new_value: float | None, old_value: float | None) -> bool | None:
    if new_value is None or old_value is None:
        return None
    return new_value < old_value


def passed_higher(new_value: float | None, old_value: float | None) -> bool | None:
    if new_value is None or old_value is None:
        return None
    return new_value > old_value


def passed_recall_gate(
    evidence_recall: float | None,
    llm_recall: float | None,
    max_recall_drop: float,
) -> bool | None:
    if evidence_recall is None or llm_recall is None:
        return None
    return evidence_recall >= llm_recall - max_recall_drop


def evaluate_gate(
    metrics: dict[str, Any],
    reviews: list[dict[str, Any]],
    llm_condition: str,
    evidence_condition: str,
    llm_group: str | None,
    evidence_group: str | None,
    acceptance_floor: float,
    max_recall_drop: float,
) -> dict[str, Any]:
    selected_llm_key, selected_llm = select_group(metrics, llm_condition, llm_group)
    selected_evidence_key, selected_evidence = select_group(metrics, evidence_condition, evidence_group)

    mock_review_count = sum(1 for review in reviews if review.get("mock_run"))
    review_count = len(reviews)
    llm_false_accept = metric_value(selected_llm, "false_accept_rate")
    evidence_false_accept = metric_value(selected_evidence, "false_accept_rate")
    llm_precision = metric_value(selected_llm, "accepted_precision")
    evidence_precision = metric_value(selected_evidence, "accepted_precision")
    llm_recall = metric_value(selected_llm, "correct_patch_recall")
    evidence_recall = metric_value(selected_evidence, "correct_patch_recall")
    evidence_acceptance = metric_value(selected_evidence, "acceptance_rate")
    evidence_escalation = metric_value(selected_evidence, "escalation_rate")
    evidence_invalid = metric_value(selected_evidence, "invalid_output_rate")

    checks = {
        "false_accept_rate_lower": passed_lower(evidence_false_accept, llm_false_accept),
        "accepted_precision_higher": passed_higher(evidence_precision, llm_precision),
        "correct_recall_not_collapsed": passed_recall_gate(evidence_recall, llm_recall, max_recall_drop),
        "not_near_total_rejection_or_escalation": None,
        "valid_outputs_interpretable": None,
    }
    if evidence_acceptance is not None and evidence_escalation is not None:
        checks["not_near_total_rejection_or_escalation"] = (
            evidence_acceptance >= acceptance_floor or evidence_escalation < 1.0 - acceptance_floor
        )
    if evidence_invalid is not None:
        checks["valid_outputs_interpretable"] = evidence_invalid < 0.20

    if mock_review_count:
        verdict = "not_evidence"
        reason = "reviews contain mock outputs"
    elif any(value is None for value in checks.values()):
        verdict = "indeterminate"
        reason = "one or more gate checks could not be computed"
    elif all(checks.values()):
        verdict = "continue"
        reason = "evidence_first passes all configured stop/continue gates"
    else:
        verdict = "stop_or_redesign"
        reason = "evidence_first does not pass the configured stop/continue gates"

    return {
        "verdict": verdict,
        "reason": reason,
        "review_count": review_count,
        "mock_review_count": mock_review_count,
        "selected_groups": {
            "llm_only": selected_llm_key,
            "evidence_first": selected_evidence_key,
        },
        "thresholds": {
            "acceptance_floor": acceptance_floor,
            "max_recall_drop": max_recall_drop,
            "invalid_output_rate_ceiling": 0.20,
        },
        "checks": checks,
        "metrics": {
            "llm_only": {
                "false_accept_rate": llm_false_accept,
                "accepted_precision": llm_precision,
                "correct_patch_recall": llm_recall,
                "acceptance_rate": metric_value(selected_llm, "acceptance_rate"),
                "escalation_rate": metric_value(selected_llm, "escalation_rate"),
                "invalid_output_rate": metric_value(selected_llm, "invalid_output_rate"),
                "records": selected_llm.get("records"),
            },
            "evidence_first": {
                "false_accept_rate": evidence_false_accept,
                "accepted_precision": evidence_precision,
                "correct_patch_recall": evidence_recall,
                "acceptance_rate": evidence_acceptance,
                "escalation_rate": evidence_escalation,
                "invalid_output_rate": evidence_invalid,
                "records": selected_evidence.get("records"),
            },
            "delta_evidence_minus_llm": {
                "false_accept_rate": delta(evidence_false_accept, llm_false_accept),
                "accepted_precision": delta(evidence_precision, llm_precision),
                "correct_patch_recall": delta(evidence_recall, llm_recall),
            },
        },
    }


def build_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# API Pilot Stop/Continue Gate",
        "",
        "## Verdict",
        "",
        f"- verdict: `{report['verdict']}`",
        f"- reason: {report['reason']}",
        f"- reviewer records: {report['review_count']}",
        f"- mock reviewer records: {report['mock_review_count']}",
        f"- llm-only group: `{report['selected_groups']['llm_only']}`",
        f"- evidence-first group: `{report['selected_groups']['evidence_first']}`",
        "",
    ]
    if report["mock_review_count"]:
        lines.extend(
            [
                "## Boundary",
                "",
                "This gate report contains mock reviewer outputs and is only a pipeline check. It must not be used as experimental evidence.",
                "",
            ]
        )

    lines.extend(
        [
            "## Gate Checks",
            "",
            "| check | passed |",
            "|---|---:|",
        ]
    )
    for name, value in report["checks"].items():
        lines.append(f"| `{name}` | `{value}` |")

    lines.extend(
        [
            "",
            "## Metrics",
            "",
            "| condition | false accept rate | accepted precision | correct recall | acceptance rate | escalation rate | invalid output rate | records |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for condition in ["llm_only", "evidence_first"]:
        values = report["metrics"][condition]
        lines.append(
            f"| `{condition}` | {fmt(values['false_accept_rate'])} | "
            f"{fmt(values['accepted_precision'])} | {fmt(values['correct_patch_recall'])} | "
            f"{fmt(values['acceptance_rate'])} | {fmt(values['escalation_rate'])} | "
            f"{fmt(values['invalid_output_rate'])} | {fmt(values['records'])} |"
        )

    deltas = report["metrics"]["delta_evidence_minus_llm"]
    lines.extend(
        [
            "",
            "## Deltas",
            "",
            "| metric | evidence_first - llm_only |",
            "|---|---:|",
        ]
    )
    for name, value in deltas.items():
        lines.append(f"| `{name}` | {fmt(value)} |")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate the API pilot stop/continue gate.")
    parser.add_argument("--metrics", required=True, help="API pilot metrics JSON.")
    parser.add_argument("--reviews", help="Optional reviews JSONL used to detect mock outputs.")
    parser.add_argument("--out-json", required=True, help="Gate report JSON output.")
    parser.add_argument("--out-md", required=True, help="Gate report Markdown output.")
    parser.add_argument("--llm-condition", default="llm_only")
    parser.add_argument("--evidence-condition", default="evidence_first")
    parser.add_argument("--llm-group", help="Explicit metrics group key for LLM-only.")
    parser.add_argument("--evidence-group", help="Explicit metrics group key for evidence-first.")
    parser.add_argument("--acceptance-floor", type=float, default=DEFAULT_ACCEPTANCE_FLOOR)
    parser.add_argument("--max-recall-drop", type=float, default=DEFAULT_MAX_RECALL_DROP)
    parser.add_argument("--fail-on-stop", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metrics = read_json(Path(args.metrics))
    reviews = read_jsonl(Path(args.reviews)) if args.reviews else []
    report = evaluate_gate(
        metrics=metrics,
        reviews=reviews,
        llm_condition=args.llm_condition,
        evidence_condition=args.evidence_condition,
        llm_group=args.llm_group,
        evidence_group=args.evidence_group,
        acceptance_floor=args.acceptance_floor,
        max_recall_drop=args.max_recall_drop,
    )
    write_json(Path(args.out_json), report)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(report), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    if args.fail_on_stop and report["verdict"] in {"stop_or_redesign", "indeterminate", "not_evidence"}:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
