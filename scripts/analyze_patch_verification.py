from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


CORRECT_OUTCOMES = {"correct"}
NEGATIVE_OUTCOMES = {"incorrect", "partial", "overfitted", "irrelevant_or_noop"}
EXCLUDED_OUTCOMES = {"environment_invalid"}
VALID_OUTCOMES = CORRECT_OUTCOMES | NEGATIVE_OUTCOMES | EXCLUDED_OUTCOMES
VALID_DECISIONS = {"accept", "reject", "escalate", "invalid_output"}
DEFAULT_TASK_COHORTS = Path("data/cohorts/task_cohort_registry.json")

REQUIRED_CANDIDATE_FIELDS = {
    "patch_id",
    "task_id",
    "project",
    "candidate_type",
    "expected_outcome",
}
REQUIRED_VERIFIER_FIELDS = {
    "patch_id",
    "verifier_id",
    "condition",
    "decision",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            value = json.loads(stripped)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number} is not a JSON object")
            records.append(value)
    return records


def write_json(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def require_fields(record: dict[str, Any], required: set[str], label: str) -> None:
    missing = sorted(required - record.keys())
    if missing:
        raise ValueError(f"{label} missing fields: {missing}")


def safe_divide(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def empty_counts() -> Counter[str]:
    return Counter(
        {
            "true_accept": 0,
            "false_accept": 0,
            "true_reject": 0,
            "false_reject": 0,
            "escalated_correct": 0,
            "escalated_incorrect": 0,
            "invalid_output": 0,
            "excluded_environment_invalid": 0,
        }
    )


def classify(candidate: dict[str, Any], verifier_output: dict[str, Any]) -> str:
    outcome = candidate["expected_outcome"]
    decision = verifier_output["decision"]

    if outcome in EXCLUDED_OUTCOMES:
        return "excluded_environment_invalid"
    if decision == "invalid_output":
        return "invalid_output"
    if outcome in CORRECT_OUTCOMES:
        if decision == "accept":
            return "true_accept"
        if decision == "reject":
            return "false_reject"
        if decision == "escalate":
            return "escalated_correct"
    if outcome in NEGATIVE_OUTCOMES:
        if decision == "accept":
            return "false_accept"
        if decision == "reject":
            return "true_reject"
        if decision == "escalate":
            return "escalated_incorrect"
    raise ValueError(
        f"Unsupported outcome/decision pair for {candidate['patch_id']}: {outcome}/{decision}"
    )


def metrics_from_counts(counts: Counter[str]) -> dict[str, Any]:
    true_accept = counts["true_accept"]
    false_accept = counts["false_accept"]
    true_reject = counts["true_reject"]
    false_reject = counts["false_reject"]
    escalated_correct = counts["escalated_correct"]
    escalated_incorrect = counts["escalated_incorrect"]
    invalid_output = counts["invalid_output"]
    excluded = counts["excluded_environment_invalid"]

    valid_decisions = (
        true_accept
        + false_accept
        + true_reject
        + false_reject
        + escalated_correct
        + escalated_incorrect
        + invalid_output
    )
    all_records = valid_decisions + excluded
    accepted = true_accept + false_accept
    correct_total = true_accept + false_reject + escalated_correct
    negative_total = false_accept + true_reject + escalated_incorrect
    escalated = escalated_correct + escalated_incorrect

    return {
        "counts": dict(counts),
        "records": all_records,
        "valid_records": valid_decisions,
        "accepted": accepted,
        "acceptance_rate": safe_divide(accepted, valid_decisions),
        "accepted_precision": safe_divide(true_accept, accepted),
        "correct_patch_recall": safe_divide(true_accept, correct_total),
        "false_accept_rate": safe_divide(false_accept, negative_total),
        "false_reject_rate": safe_divide(false_reject, correct_total),
        "escalation_rate": safe_divide(escalated, valid_decisions),
        "invalid_output_rate": safe_divide(invalid_output, valid_decisions),
    }


def validate_candidates(candidates: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        require_fields(candidate, REQUIRED_CANDIDATE_FIELDS, "candidate")
        patch_id = candidate["patch_id"]
        if patch_id in by_id:
            raise ValueError(f"Duplicate candidate patch_id: {patch_id}")
        outcome = candidate["expected_outcome"]
        if outcome not in VALID_OUTCOMES:
            raise ValueError(f"{patch_id} has invalid expected_outcome: {outcome}")
        by_id[patch_id] = candidate
    return by_id


def validate_verifier_outputs(
    verifier_outputs: list[dict[str, Any]], candidates_by_id: dict[str, dict[str, Any]]
) -> None:
    seen: set[tuple[str, str, str]] = set()
    for output in verifier_outputs:
        require_fields(output, REQUIRED_VERIFIER_FIELDS, "verifier_output")
        patch_id = output["patch_id"]
        if patch_id not in candidates_by_id:
            raise ValueError(f"Verifier output references unknown patch_id: {patch_id}")
        decision = output["decision"]
        if decision not in VALID_DECISIONS:
            raise ValueError(f"{patch_id} has invalid decision: {decision}")
        key = (patch_id, output["verifier_id"], output["condition"])
        if key in seen:
            raise ValueError(f"Duplicate verifier output: {key}")
        seen.add(key)


def task_ids_for_main_cohort(cohort_registry: dict[str, Any]) -> set[str]:
    task_ids = set()
    for task in cohort_registry.get("tasks", []):
        if not isinstance(task, dict):
            continue
        if (
            task.get("project_level_p2p_status") == "completed"
            and task.get("p2p_broad_main_included") is True
        ):
            task_id = task.get("task_id")
            if isinstance(task_id, str):
                task_ids.add(task_id)
    return task_ids


def filter_to_task_ids(
    candidates: list[dict[str, Any]],
    verifier_outputs: list[dict[str, Any]],
    task_ids: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    filtered_candidates = [candidate for candidate in candidates if candidate.get("task_id") in task_ids]
    retained_patch_ids = {candidate["patch_id"] for candidate in filtered_candidates}
    filtered_outputs = [
        output for output in verifier_outputs if output.get("patch_id") in retained_patch_ids
    ]
    return (
        filtered_candidates,
        filtered_outputs,
        {
            "enabled": True,
            "included_task_ids": sorted(task_ids),
            "candidate_count_before": len(candidates),
            "candidate_count_after": len(filtered_candidates),
            "verifier_output_count_before": len(verifier_outputs),
            "verifier_output_count_after": len(filtered_outputs),
        },
    )


def analyze(
    candidates: list[dict[str, Any]],
    verifier_outputs: list[dict[str, Any]],
    cohort_filter: dict[str, Any] | None = None,
) -> dict[str, Any]:
    candidates_by_id = validate_candidates(candidates)
    validate_verifier_outputs(verifier_outputs, candidates_by_id)

    grouped_counts: dict[str, Counter[str]] = defaultdict(empty_counts)
    grouped_by_type: dict[str, dict[str, Counter[str]]] = defaultdict(lambda: defaultdict(empty_counts))
    grouped_by_project: dict[str, dict[str, Counter[str]]] = defaultdict(lambda: defaultdict(empty_counts))
    output_counts = Counter()

    for output in verifier_outputs:
        candidate = candidates_by_id[output["patch_id"]]
        group_key = f"{output['condition']}::{output['verifier_id']}"
        bucket = classify(candidate, output)
        grouped_counts[group_key][bucket] += 1
        grouped_by_type[group_key][candidate["candidate_type"]][bucket] += 1
        grouped_by_project[group_key][candidate["project"]][bucket] += 1
        output_counts[group_key] += 1

    groups: dict[str, Any] = {}
    for group_key, counts in sorted(grouped_counts.items()):
        groups[group_key] = metrics_from_counts(counts)
        groups[group_key]["by_candidate_type"] = {
            candidate_type: metrics_from_counts(type_counts)
            for candidate_type, type_counts in sorted(grouped_by_type[group_key].items())
        }
        groups[group_key]["by_project"] = {
            project: metrics_from_counts(project_counts)
            for project, project_counts in sorted(grouped_by_project[group_key].items())
        }

    return {
        "cohort_filter": cohort_filter or {"enabled": False},
        "candidate_count": len(candidates),
        "verifier_output_count": len(verifier_outputs),
        "candidate_type_counts": dict(sorted(Counter(c["candidate_type"] for c in candidates).items())),
        "expected_outcome_counts": dict(sorted(Counter(c["expected_outcome"] for c in candidates).items())),
        "project_counts": dict(sorted(Counter(c["project"] for c in candidates).items())),
        "verifier_record_counts": dict(sorted(output_counts.items())),
        "groups": groups,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze patch-verification decisions against candidate outcomes."
    )
    parser.add_argument("--candidates", required=True, help="Patch candidate JSONL.")
    parser.add_argument("--verifier-outputs", required=True, help="Verifier output JSONL.")
    parser.add_argument("--out", required=True, help="Metrics JSON output.")
    parser.add_argument(
        "--task-cohorts",
        default=str(DEFAULT_TASK_COHORTS),
        help="Task cohort registry JSON. Defaults to data/cohorts/task_cohort_registry.json.",
    )
    parser.add_argument(
        "--no-cohort-filter",
        action="store_true",
        help="Disable the default p2p_broad_main task filter.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candidates = read_jsonl(Path(args.candidates))
    verifier_outputs = read_jsonl(Path(args.verifier_outputs))
    cohort_filter: dict[str, Any] | None = None
    if not args.no_cohort_filter:
        registry_path = Path(args.task_cohorts)
        if registry_path.exists():
            task_ids = task_ids_for_main_cohort(read_json(registry_path))
            candidates, verifier_outputs, cohort_filter = filter_to_task_ids(
                candidates,
                verifier_outputs,
                task_ids,
            )
        else:
            cohort_filter = {
                "enabled": False,
                "reason": f"missing task cohort registry: {registry_path}",
            }
    metrics = analyze(candidates, verifier_outputs, cohort_filter=cohort_filter)
    write_json(Path(args.out), metrics)
    print(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
