from __future__ import annotations

import argparse
import json
import math
import random
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REVIEWS = REPO_ROOT / "outputs" / "evp7_g5_llm_376_full_001" / "reviews.jsonl"
DEFAULT_CANDIDATES = REPO_ROOT / "data" / "patches" / "evp7_candidates.jsonl"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "reviews" / "evp7_g5_376_statistical_analysis.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp7_g5_376_statistical_analysis.md"

EVIDENCE_LEVELS = ("E0", "E2", "E4", "E6")
METRIC_NAMES = ("false_accept_rate", "accepted_precision", "correct_recall", "escalation_rate")
DELTA_METRICS = ("false_accept_rate", "correct_recall", "escalation_rate", "utility_score")
CORRECT_LABEL = "correct_under_f2p_and_p2p_broad"
RAW_FIELD_MARKERS = ("raw_" + "response_text", "prompt_" + "text")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def candidate_metadata(candidates_path: Path) -> dict[str, dict[str, Any]]:
    records = read_jsonl(candidates_path)
    return {
        record["evp7_candidate_id"]: {
            "project": record["project"],
            "patch_source_label": record["patch_source_label"],
            "label_with_p2p_broad": record["label_with_p2p_broad"],
        }
        for record in records
    }


def normalized_reviews(reviews_path: Path, candidates: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for record in read_jsonl(reviews_path):
        candidate_id = record["candidate_id"]
        metadata = candidates[candidate_id]
        parsed = record.get("parsed_output") if record.get("parse_status") == "valid" else {}
        decision = parsed.get("decision") if isinstance(parsed, dict) else None
        records.append(
            {
                "candidate_id": candidate_id,
                "evidence_level": record["evidence_level"],
                "decision": decision or "invalid_output",
                "parse_status": record.get("parse_status"),
                "project": metadata["project"],
                "patch_source_label": metadata["patch_source_label"],
                "is_correct": metadata["label_with_p2p_broad"] == CORRECT_LABEL,
                "cost_usd": record.get("cost_usd"),
            }
        )
    return records


def analyze(
    reviews_path: Path,
    candidates_path: Path,
    bootstrap_samples: int,
    seed: int,
) -> dict[str, Any]:
    candidates = candidate_metadata(candidates_path)
    reviews = normalized_reviews(reviews_path, candidates)
    candidate_ids = sorted(candidates)
    _check_review_matrix(reviews, candidate_ids)

    by_level = {
        level: metrics_for_records([record for record in reviews if record["evidence_level"] == level])
        for level in EVIDENCE_LEVELS
    }
    bootstrap = bootstrap_intervals(reviews, candidate_ids, bootstrap_samples, seed)
    paired = paired_deltas(reviews, candidate_ids, bootstrap_samples, seed)
    project_breakdown = grouped_breakdown(reviews, lambda record: record["project"])
    patch_source_breakdown = grouped_breakdown(reviews, lambda record: record["patch_source_label"])

    analysis = {
        "analysis_id": "evp7_g5_376_statistical_analysis",
        "boundary": (
            "Raw model responses remain ignored under outputs/. This artifact reads only "
            "review structure, decisions, costs, candidate labels, project, and patch-source "
            "metadata, then writes aggregate raw-output-free statistics."
        ),
        "inputs": {
            "reviews": repo_relative(reviews_path),
            "candidates": repo_relative(candidates_path),
        },
        "cohort": {
            "task_count": 20,
            "candidate_count": len(candidate_ids),
            "evidence_packet_count": len(reviews),
            "evidence_levels": list(EVIDENCE_LEVELS),
        },
        "method": {
            "wilson_confidence_level": 0.95,
            "bootstrap_confidence_level": 0.95,
            "bootstrap_unit": "candidate_id",
            "bootstrap_samples": bootstrap_samples,
            "bootstrap_seed": seed,
            "paired_baseline": "E0",
            "effect_size": "point estimate delta versus E0 for paired comparisons",
        },
        "per_evidence_level": by_level,
        "bootstrap_intervals": bootstrap,
        "paired_deltas_vs_e0": paired,
        "per_project_breakdown": project_breakdown,
        "per_patch_source_breakdown": patch_source_breakdown,
        "raw_output_free_check": {
            "passed": not contains_raw_markers(by_level)
            and not contains_raw_markers(bootstrap)
            and not contains_raw_markers(paired)
            and not contains_raw_markers(project_breakdown)
            and not contains_raw_markers(patch_source_breakdown),
            "checked_for_raw_response_fields": True,
        },
    }
    if not analysis["raw_output_free_check"]["passed"]:
        raise SystemExit("statistical analysis output contains raw-output field markers")
    return analysis


def _check_review_matrix(reviews: list[dict[str, Any]], candidate_ids: list[str]) -> None:
    expected = {(candidate_id, level) for candidate_id in candidate_ids for level in EVIDENCE_LEVELS}
    observed = {(record["candidate_id"], record["evidence_level"]) for record in reviews}
    missing = sorted(expected - observed)
    extra = sorted(observed - expected)
    if missing or extra or len(reviews) != len(expected):
        raise SystemExit(
            "review matrix mismatch: "
            f"expected={len(expected)} observed={len(reviews)} missing={len(missing)} extra={len(extra)}"
        )


def metrics_for_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    counts = confusion_counts(records)
    accepted = counts["true_accept"] + counts["false_accept"]
    correct_total = counts["true_accept"] + counts["false_reject"] + counts["escalated_correct"]
    incorrect_total = counts["false_accept"] + counts["true_reject"] + counts["escalated_incorrect"]
    escalated = counts["escalated_correct"] + counts["escalated_incorrect"]
    record_count = len(records)
    metrics = {
        "record_count": record_count,
        "decision_counts": count_values(record["decision"] for record in records),
        "confusion_counts": counts,
        "false_accept_rate": proportion(counts["false_accept"], incorrect_total),
        "accepted_precision": proportion(counts["true_accept"], accepted),
        "correct_recall": proportion(counts["true_accept"], correct_total),
        "false_reject_rate": proportion(counts["false_reject"], correct_total),
        "escalation_rate": proportion(escalated, record_count),
        "invalid_output_rate": proportion(counts["invalid_output"], record_count),
        "utility_score": round(
            counts["true_accept"]
            - 5 * counts["false_accept"]
            - 0.25 * escalated
            - counts["false_reject"],
            6,
        ),
        "cost_usd_total": round(sum(float(record.get("cost_usd") or 0.0) for record in records), 9),
    }
    metrics["wilson_ci_95"] = {
        "false_accept_rate": wilson_interval(counts["false_accept"], incorrect_total),
        "accepted_precision": wilson_interval(counts["true_accept"], accepted),
        "correct_recall": wilson_interval(counts["true_accept"], correct_total),
        "escalation_rate": wilson_interval(escalated, record_count),
        "invalid_output_rate": wilson_interval(counts["invalid_output"], record_count),
    }
    return metrics


def confusion_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    counts = {
        "true_accept": 0,
        "false_accept": 0,
        "true_reject": 0,
        "false_reject": 0,
        "escalated_correct": 0,
        "escalated_incorrect": 0,
        "invalid_output": 0,
    }
    for record in records:
        decision = record["decision"]
        is_correct = bool(record["is_correct"])
        if decision == "accept" and is_correct:
            counts["true_accept"] += 1
        elif decision == "accept":
            counts["false_accept"] += 1
        elif decision == "reject" and is_correct:
            counts["false_reject"] += 1
        elif decision == "reject":
            counts["true_reject"] += 1
        elif decision == "escalate" and is_correct:
            counts["escalated_correct"] += 1
        elif decision == "escalate":
            counts["escalated_incorrect"] += 1
        else:
            counts["invalid_output"] += 1
    return counts


def count_values(values: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def proportion(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 6)


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> dict[str, Any]:
    if total == 0:
        return {"n": 0, "successes": successes, "point": None, "low": None, "high": None}
    p = successes / total
    denom = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    half_width = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denom
    return {
        "n": total,
        "successes": successes,
        "point": round(p, 6),
        "low": round(max(0.0, center - half_width), 6),
        "high": round(min(1.0, center + half_width), 6),
    }


def bootstrap_intervals(
    reviews: list[dict[str, Any]],
    candidate_ids: list[str],
    samples: int,
    seed: int,
) -> dict[str, Any]:
    rng = random.Random(seed)
    by_candidate_level = index_by_candidate_level(reviews)
    distributions: dict[str, dict[str, list[float]]] = {
        level: {metric: [] for metric in METRIC_NAMES + ("utility_score",)}
        for level in EVIDENCE_LEVELS
    }
    for _ in range(samples):
        sampled = [rng.choice(candidate_ids) for _ in candidate_ids]
        for level in EVIDENCE_LEVELS:
            metrics = metrics_for_records([by_candidate_level[(candidate_id, level)] for candidate_id in sampled])
            for metric in distributions[level]:
                value = metrics.get(metric)
                if value is not None:
                    distributions[level][metric].append(float(value))
    return {
        level: {
            metric: percentile_interval(values)
            for metric, values in metric_values.items()
        }
        for level, metric_values in distributions.items()
    }


def paired_deltas(
    reviews: list[dict[str, Any]],
    candidate_ids: list[str],
    samples: int,
    seed: int,
) -> dict[str, Any]:
    rng = random.Random(seed + 17)
    by_candidate_level = index_by_candidate_level(reviews)
    point_metrics = {
        level: metrics_for_records([record for record in reviews if record["evidence_level"] == level])
        for level in EVIDENCE_LEVELS
    }
    result: dict[str, Any] = {}
    for level in EVIDENCE_LEVELS:
        if level == "E0":
            continue
        result[level] = {}
        for metric in DELTA_METRICS:
            base_value = point_metrics["E0"].get(metric)
            level_value = point_metrics[level].get(metric)
            point_delta = None if base_value is None or level_value is None else round(level_value - base_value, 6)
            distribution = []
            for _ in range(samples):
                sampled = [rng.choice(candidate_ids) for _ in candidate_ids]
                base_records = [by_candidate_level[(candidate_id, "E0")] for candidate_id in sampled]
                level_records = [by_candidate_level[(candidate_id, level)] for candidate_id in sampled]
                base_metric = metrics_for_records(base_records).get(metric)
                level_metric = metrics_for_records(level_records).get(metric)
                if base_metric is not None and level_metric is not None:
                    distribution.append(float(level_metric) - float(base_metric))
            interval = percentile_interval(distribution)
            result[level][metric] = {
                "point_delta": point_delta,
                "effect_size": point_delta,
                "bootstrap_ci_95": interval,
                "bootstrap_probability_delta_gt_0": probability_gt_zero(distribution),
            }
    return result


def index_by_candidate_level(reviews: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (record["candidate_id"], record["evidence_level"]): record
        for record in reviews
    }


def percentile_interval(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"samples": 0, "low": None, "median": None, "high": None}
    ordered = sorted(values)
    return {
        "samples": len(ordered),
        "low": round(percentile(ordered, 0.025), 6),
        "median": round(percentile(ordered, 0.5), 6),
        "high": round(percentile(ordered, 0.975), 6),
    }


def percentile(sorted_values: list[float], q: float) -> float:
    if len(sorted_values) == 1:
        return sorted_values[0]
    index = q * (len(sorted_values) - 1)
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return sorted_values[lower]
    weight = index - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def probability_gt_zero(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(1 for value in values if value > 0) / len(values), 6)


def grouped_breakdown(
    reviews: list[dict[str, Any]],
    key_fn: Callable[[dict[str, Any]], str],
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in reviews:
        grouped[key_fn(record)].append(record)
    return {
        key: {
            level: metrics_for_records([record for record in records if record["evidence_level"] == level])
            for level in EVIDENCE_LEVELS
        }
        for key, records in sorted(grouped.items())
    }


def contains_raw_markers(value: Any) -> bool:
    return any(marker in json.dumps(value, ensure_ascii=False) for marker in RAW_FIELD_MARKERS)


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def fmt(value: Any) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def fmt_ci(interval: dict[str, Any] | None) -> str:
    if not interval or interval.get("low") is None:
        return "NA"
    return f"[{interval['low']:.4f}, {interval['high']:.4f}]"


def render_markdown(analysis: dict[str, Any]) -> str:
    lines = [
        "# EVP-7 G5 376-Record Statistical Analysis",
        "",
        analysis["boundary"],
        "",
        "## Method",
        "",
        f"- Bootstrap unit: `{analysis['method']['bootstrap_unit']}`",
        f"- Bootstrap samples: {analysis['method']['bootstrap_samples']}",
        f"- Bootstrap seed: {analysis['method']['bootstrap_seed']}",
        f"- Paired baseline: `{analysis['method']['paired_baseline']}`",
        f"- Effect size: {analysis['method']['effect_size']}",
        "",
        "## Per-Evidence-Level Intervals",
        "",
        "| evidence | metric | point | Wilson 95% CI | bootstrap 95% CI |",
        "|---|---|---:|---:|---:|",
    ]
    for level in EVIDENCE_LEVELS:
        group = analysis["per_evidence_level"][level]
        bootstrap = analysis["bootstrap_intervals"][level]
        for metric in METRIC_NAMES:
            lines.append(
                f"| {level} | {metric} | {fmt(group.get(metric))} | "
                f"{fmt_ci(group['wilson_ci_95'].get(metric))} | {fmt_ci(bootstrap.get(metric))} |"
            )
    lines.extend(
        [
            "",
            "## Paired Delta Versus E0",
            "",
            "| comparison | metric | point delta | bootstrap 95% CI | P(delta > 0) |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for level, metrics in analysis["paired_deltas_vs_e0"].items():
        for metric, values in metrics.items():
            lines.append(
                f"| {level} - E0 | {metric} | {fmt(values['point_delta'])} | "
                f"{fmt_ci(values['bootstrap_ci_95'])} | {fmt(values['bootstrap_probability_delta_gt_0'])} |"
            )
    lines.extend(render_breakdown("Per-Project Breakdown", analysis["per_project_breakdown"]))
    lines.extend(render_breakdown("Per-Patch-Source Breakdown", analysis["per_patch_source_breakdown"]))
    lines.extend(
        [
            "",
            "## Boundary Check",
            "",
            f"- Raw-output-free check passed: {str(analysis['raw_output_free_check']['passed']).lower()}",
            "- Raw response and prompt text fields are omitted from this tracked artifact.",
            "",
        ]
    )
    return "\n".join(lines)


def render_breakdown(title: str, breakdown: dict[str, Any]) -> list[str]:
    lines = [
        "",
        f"## {title}",
        "",
        "| group | evidence | records | false accept | correct recall | escalation | utility |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for group_name, by_level in breakdown.items():
        for level in EVIDENCE_LEVELS:
            metrics = by_level[level]
            lines.append(
                f"| {group_name} | {level} | {metrics['record_count']} | "
                f"{fmt(metrics['false_accept_rate'])} | {fmt(metrics['correct_recall'])} | "
                f"{fmt(metrics['escalation_rate'])} | {fmt(metrics['utility_score'])} |"
            )
    return lines


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze EVP-7 G5 376-run statistical intervals.")
    parser.add_argument("--reviews", type=Path, default=DEFAULT_REVIEWS)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=9507)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    analysis = analyze(args.reviews, args.candidates, args.bootstrap_samples, args.seed)
    write_json(args.json_out, analysis)
    write_text(args.md_out, render_markdown(analysis))
    print(
        json.dumps(
            {
                "out_json": str(args.json_out),
                "out_md": str(args.md_out),
                "raw_output_free": analysis["raw_output_free_check"]["passed"],
                "bootstrap_samples": args.bootstrap_samples,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
