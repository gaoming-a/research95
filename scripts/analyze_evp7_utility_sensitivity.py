from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REVIEWS = REPO_ROOT / "outputs" / "evp7_g5_llm_376_full_001" / "reviews.jsonl"
DEFAULT_CANDIDATES = REPO_ROOT / "data" / "patches" / "evp7_candidates.jsonl"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "reviews" / "evp7_g5_376_utility_sensitivity.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp7_g5_376_utility_sensitivity.md"

EVIDENCE_LEVELS = ("E0", "E2", "E4", "E6")
CORRECT_LABEL = "correct_under_f2p_and_p2p_broad"
LAMBDA_VALUES = (1.0, 5.0, 10.0)
MU_VALUES = (0.1, 0.25, 0.5)
NU_VALUES = (0.5, 1.0, 2.0)
RAW_MARKERS = ("raw_" + "response_text", "prompt_" + "text")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def candidate_labels(candidates_path: Path) -> dict[str, bool]:
    return {
        record["evp7_candidate_id"]: record["label_with_p2p_broad"] == CORRECT_LABEL
        for record in read_jsonl(candidates_path)
    }


def normalized_reviews(reviews_path: Path, labels: dict[str, bool]) -> list[dict[str, Any]]:
    records = []
    for record in read_jsonl(reviews_path):
        parsed = record.get("parsed_output") if record.get("parse_status") == "valid" else {}
        decision = parsed.get("decision") if isinstance(parsed, dict) else "invalid_output"
        candidate_id = record["candidate_id"]
        records.append(
            {
                "candidate_id": candidate_id,
                "evidence_level": record["evidence_level"],
                "decision": decision,
                "is_correct": labels[candidate_id],
            }
        )
    return records


def analyze(reviews_path: Path, candidates_path: Path) -> dict[str, Any]:
    labels = candidate_labels(candidates_path)
    records = normalized_reviews(reviews_path, labels)
    check_matrix(records, labels)
    counts_by_level = {
        level: confusion_counts([record for record in records if record["evidence_level"] == level])
        for level in EVIDENCE_LEVELS
    }
    scenarios = []
    best_counter: Counter[str] = Counter()
    ranking_counter: Counter[str] = Counter()
    for lambda_penalty in LAMBDA_VALUES:
        for mu_penalty in MU_VALUES:
            for nu_penalty in NU_VALUES:
                scenario = scenario_result(counts_by_level, lambda_penalty, mu_penalty, nu_penalty)
                scenarios.append(scenario)
                best_counter[scenario["best_level"]] += 1
                ranking_counter[" > ".join(scenario["ranking"])] += 1
    result = {
        "analysis_id": "evp7_g5_376_utility_sensitivity",
        "boundary": (
            "This analysis reads ignored review records structurally and joins tracked "
            "candidate labels only for aggregate utility calculations. It writes no raw "
            "model responses or prompt text."
        ),
        "inputs": {
            "reviews": repo_relative(reviews_path),
            "candidates": repo_relative(candidates_path),
        },
        "utility_formula": "true_accept - lambda*false_accept - mu*escalated - nu*false_reject",
        "parameter_grid": {
            "lambda_false_accept_penalty": list(LAMBDA_VALUES),
            "mu_escalation_penalty": list(MU_VALUES),
            "nu_false_reject_penalty": list(NU_VALUES),
        },
        "cohort": {
            "candidate_count": len(labels),
            "evidence_packet_count": len(records),
            "evidence_levels": list(EVIDENCE_LEVELS),
        },
        "confusion_counts_by_level": counts_by_level,
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "best_level_counts": dict(sorted(best_counter.items())),
        "ranking_counts": dict(sorted(ranking_counter.items())),
        "stability_summary": stability_summary(best_counter, ranking_counter, len(scenarios)),
    }
    result["raw_output_free_check"] = {
        "passed": not contains_raw_markers(result),
        "checked_for_raw_response_fields": True,
    }
    if not result["raw_output_free_check"]["passed"]:
        raise SystemExit("utility sensitivity output contains raw-output field markers")
    return result


def check_matrix(records: list[dict[str, Any]], labels: dict[str, bool]) -> None:
    expected = {(candidate_id, level) for candidate_id in labels for level in EVIDENCE_LEVELS}
    observed = {(record["candidate_id"], record["evidence_level"]) for record in records}
    if expected != observed or len(records) != len(expected):
        raise SystemExit(
            f"review matrix mismatch: expected={len(expected)} observed={len(records)} "
            f"missing={len(expected - observed)} extra={len(observed - expected)}"
        )


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


def scenario_result(
    counts_by_level: dict[str, dict[str, int]],
    lambda_penalty: float,
    mu_penalty: float,
    nu_penalty: float,
) -> dict[str, Any]:
    utilities = {
        level: utility_score(counts, lambda_penalty, mu_penalty, nu_penalty)
        for level, counts in counts_by_level.items()
    }
    deltas_vs_e0 = {
        level: round(score - utilities["E0"], 6)
        for level, score in utilities.items()
    }
    ranking = sorted(EVIDENCE_LEVELS, key=lambda level: (-utilities[level], level))
    return {
        "lambda_false_accept_penalty": lambda_penalty,
        "mu_escalation_penalty": mu_penalty,
        "nu_false_reject_penalty": nu_penalty,
        "utilities": utilities,
        "deltas_vs_e0": deltas_vs_e0,
        "best_level": ranking[0],
        "ranking": ranking,
    }


def utility_score(counts: dict[str, int], lambda_penalty: float, mu_penalty: float, nu_penalty: float) -> float:
    escalated = counts["escalated_correct"] + counts["escalated_incorrect"]
    return round(
        counts["true_accept"]
        - lambda_penalty * counts["false_accept"]
        - mu_penalty * escalated
        - nu_penalty * counts["false_reject"],
        6,
    )


def stability_summary(best_counter: Counter[str], ranking_counter: Counter[str], scenario_count: int) -> dict[str, Any]:
    most_common_ranking, ranking_count = ranking_counter.most_common(1)[0]
    best_level, best_count = best_counter.most_common(1)[0]
    return {
        "scenario_count": scenario_count,
        "dominant_best_level": best_level,
        "dominant_best_level_share": round(best_count / scenario_count, 6),
        "dominant_ranking": most_common_ranking,
        "dominant_ranking_share": round(ranking_count / scenario_count, 6),
        "interpretation": (
            "The current grid changes escalation and false-reject penalties but does "
            "not change false-accept penalties in this run because observed false "
            "accept counts are zero at every evidence level."
        ),
    }


def contains_raw_markers(value: Any) -> bool:
    serialized = json.dumps(value, ensure_ascii=False)
    return any(marker in serialized for marker in RAW_MARKERS)


def fmt(value: float) -> str:
    return f"{value:.4f}"


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# EVP-7 G5 376-Record Utility Sensitivity",
        "",
        result["boundary"],
        "",
        "## Method",
        "",
        f"- Utility formula: `{result['utility_formula']}`",
        f"- False accept penalties: `{result['parameter_grid']['lambda_false_accept_penalty']}`",
        f"- Escalation penalties: `{result['parameter_grid']['mu_escalation_penalty']}`",
        f"- False reject penalties: `{result['parameter_grid']['nu_false_reject_penalty']}`",
        f"- Scenario count: {result['scenario_count']}",
        "",
        "## Stability Summary",
        "",
        f"- Dominant best level: `{result['stability_summary']['dominant_best_level']}`",
        f"- Dominant best-level share: {fmt(result['stability_summary']['dominant_best_level_share'])}",
        f"- Dominant ranking: `{result['stability_summary']['dominant_ranking']}`",
        f"- Dominant ranking share: {fmt(result['stability_summary']['dominant_ranking_share'])}",
        f"- Interpretation: {result['stability_summary']['interpretation']}",
        "",
        "## Best Level Counts",
        "",
        "| evidence level | scenarios as best |",
        "|---|---:|",
    ]
    for level in EVIDENCE_LEVELS:
        lines.append(f"| {level} | {result['best_level_counts'].get(level, 0)} |")
    lines.extend(
        [
            "",
            "## Scenario Results",
            "",
            "| lambda | mu | nu | best | ranking | E0 | E2 | E4 | E6 |",
            "|---:|---:|---:|---|---|---:|---:|---:|---:|",
        ]
    )
    for scenario in result["scenarios"]:
        utilities = scenario["utilities"]
        lines.append(
            f"| {fmt(scenario['lambda_false_accept_penalty'])} | {fmt(scenario['mu_escalation_penalty'])} | "
            f"{fmt(scenario['nu_false_reject_penalty'])} | {scenario['best_level']} | "
            f"{' > '.join(scenario['ranking'])} | {fmt(utilities['E0'])} | {fmt(utilities['E2'])} | "
            f"{fmt(utilities['E4'])} | {fmt(utilities['E6'])} |"
        )
    lines.extend(
        [
            "",
            "## Boundary Check",
            "",
            f"- Raw-output-free check passed: {str(result['raw_output_free_check']['passed']).lower()}",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze EVP-7 utility sensitivity over penalty parameters.")
    parser.add_argument("--reviews", type=Path, default=DEFAULT_REVIEWS)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = analyze(args.reviews, args.candidates)
    write_json(args.json_out, result)
    write_text(args.md_out, render_markdown(result))
    print(
        json.dumps(
            {
                "out_json": repo_relative(args.json_out),
                "out_md": repo_relative(args.md_out),
                "passed": result["raw_output_free_check"]["passed"],
                "scenario_count": result["scenario_count"],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
