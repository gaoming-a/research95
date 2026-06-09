from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


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


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def elapsed_seconds(record: dict[str, Any]) -> float:
    patch_elapsed = float(record.get("patch_result", {}).get("elapsed_seconds") or 0.0)
    oracle_results = record.get("oracle_result", {}).get("results") or []
    oracle_elapsed = sum(float(result.get("elapsed_seconds") or 0.0) for result in oracle_results)
    return round(patch_elapsed + oracle_elapsed, 3)


def task_from_generation_record(record: dict[str, Any]) -> str | None:
    task_id = record.get("task_id")
    if isinstance(task_id, str) and task_id:
        return task_id
    patch_id = record.get("patch_id")
    if isinstance(patch_id, str) and "__" in patch_id:
        return patch_id.split("__", 1)[0]
    return None


def load_grouped(paths: list[str]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for path_text in paths:
        path = Path(path_text)
        if not path.exists():
            raise FileNotFoundError(f"missing input file: {path}")
        for record in read_jsonl(path):
            task_id = task_from_generation_record(record)
            if task_id:
                grouped[task_id].append(record)
    return grouped


def load_p2p_scopes(paths: list[str]) -> dict[str, dict[str, Any]]:
    scopes: dict[str, dict[str, Any]] = {}
    for path_text in paths:
        path = Path(path_text)
        if not path.exists():
            raise FileNotFoundError(f"missing P2P scope file: {path}")
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError(f"{path} must contain a JSON object")
        task_id = value.get("task_id")
        if isinstance(task_id, str) and task_id:
            scopes[task_id] = value
    return scopes


def generation_status(attempts: int, generated: int, applicable: int, correct: int) -> str:
    if attempts == 0 and generated == 0:
        return "not_attempted"
    if generated > 0 and applicable == 0:
        return "non_applicable_only"
    if correct > 0:
        return "solved"
    if applicable > 0:
        return "unsolved"
    return "not_applicable"


def task_role(
    environment_stable: bool,
    reference_patch_valid: bool,
    status: str,
) -> str:
    if not environment_stable or not reference_patch_valid:
        return "excluded_unstable_validation"
    if status in {"unsolved", "non_applicable_only"}:
        return "hard_generation_case"
    return "main_balanced_task"


def build_task_record(
    task_id: str,
    validation_records: list[dict[str, Any]],
    generated_records: list[dict[str, Any]],
    generation_attempts: int,
    p2p_scope: dict[str, Any] | None,
    p2p_records: list[dict[str, Any]],
) -> dict[str, Any]:
    projects = {str(record.get("project")) for record in validation_records if record.get("project")}
    project = sorted(projects)[0] if projects else None
    validation_statuses = Counter(str(record.get("validation_status")) for record in validation_records)
    all_validated = bool(validation_records) and set(validation_statuses) == {"validated"}
    all_applied = bool(validation_records) and all(bool(record.get("patch_applied")) for record in validation_records)
    all_oracles_ran = bool(validation_records) and all(bool(record.get("oracle_ran")) for record in validation_records)
    reference_records = [
        record for record in validation_records if record.get("candidate_type") == "correct_reference"
    ]
    reference_patch_valid = bool(reference_records) and all(
        record.get("validation_status") == "validated" and bool(record.get("oracle_passed"))
        for record in reference_records
    )
    buggy_failure_records = [
        record
        for record in validation_records
        if record.get("candidate_type") == "buggy_noop"
        or record.get("patch_materialization") == "empty_diff_against_buggy_checkout"
    ]
    buggy_failure_reproducible = bool(buggy_failure_records) and all(
        record.get("validation_status") == "validated" and not bool(record.get("oracle_passed"))
        for record in buggy_failure_records
    )
    runtime_values = [elapsed_seconds(record) for record in validation_records]

    generated = len(generated_records)
    applicable = sum(1 for record in generated_records if record.get("expected_outcome") != "environment_invalid")
    correct = sum(1 for record in generated_records if record.get("expected_outcome") == "correct")
    incorrect = sum(1 for record in generated_records if record.get("expected_outcome") == "incorrect")
    partial = sum(1 for record in generated_records if record.get("expected_outcome") in {"partial", "overfitted"})
    environment_invalid = sum(
        1 for record in generated_records if record.get("expected_outcome") == "environment_invalid"
    )
    status = generation_status(generation_attempts, generated, applicable, correct)
    environment_stable = all_validated and all_applied and all_oracles_ran

    p2p_broad_size = len(p2p_scope.get("p2p_broad_tests", [])) if p2p_scope else 0
    p2p_core_size = len(p2p_scope.get("p2p_core_tests", [])) if p2p_scope else 0
    p2p_completed = p2p_scope is not None and p2p_broad_size > 0
    return {
        "task_id": task_id,
        "project": project,
        "bug_id": task_id.replace("bugsinpy_", "").rsplit("_", 1)[-1],
        "environment_stable": environment_stable,
        "reference_patch_valid": reference_patch_valid,
        "buggy_failure_reproducible": buggy_failure_reproducible,
        "pass_to_pass_stable": True if p2p_completed else None,
        "pass_to_pass_stability_note": (
            "p2p_broad_stable_subset_completed"
            if p2p_completed
            else "not_measured_by_current_patch_verification_oracle"
        ),
        "p2p_status": "completed" if p2p_completed else "pending",
        "p2p_scope_size": p2p_broad_size,
        "p2p_core_size": p2p_core_size,
        "p2p_label_counts": count_by(p2p_records, "label_with_p2p_broad") if p2p_records else {},
        "label_scope_current": "f2p_plus_p2p_broad" if p2p_completed else "retained_oracle",
        "regression_scope_current": "p2p_broad_stable_subset" if p2p_completed else "undefined",
        "validation_record_count": len(validation_records),
        "validation_status_counts": dict(sorted(validation_statuses.items())),
        "patch_apply_stable": all_applied,
        "oracle_execution_stable": all_oracles_ran,
        "validation_runtime_seconds": {
            "max": max(runtime_values) if runtime_values else None,
            "mean": round(sum(runtime_values) / len(runtime_values), 3) if runtime_values else None,
        },
        "generator_attempts": generation_attempts,
        "num_ai_patches_generated": generated,
        "num_ai_patches_applicable": applicable,
        "num_ai_patches_correct": correct,
        "num_ai_patches_incorrect": incorrect,
        "num_ai_patches_partial": partial,
        "num_ai_patches_environment_invalid": environment_invalid,
        "generation_status": status,
        "task_role": task_role(environment_stable, reference_patch_valid, status),
        "main_experiment_included": environment_stable and reference_patch_valid,
        "exclusion_reason": None if environment_stable and reference_patch_valid else "unstable_validation",
    }


def build_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "task_count": len(records),
        "task_role_counts": dict(Counter(record["task_role"] for record in records)),
        "generation_status_counts": dict(Counter(record["generation_status"] for record in records)),
        "environment_stable_count": sum(1 for record in records if record["environment_stable"]),
        "reference_patch_valid_count": sum(1 for record in records if record["reference_patch_valid"]),
        "main_experiment_included_count": sum(1 for record in records if record["main_experiment_included"]),
    }


def count_by(records: list[dict[str, Any]], field: str) -> dict[str, int]:
    return dict(Counter(str(record.get(field)) for record in records))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build task-level generation accounting records.")
    parser.add_argument("--validation", action="append", default=[], help="Validation JSONL path. Repeatable.")
    parser.add_argument(
        "--generated-candidates",
        action="append",
        default=[],
        help="Relabeled generated candidate JSONL path. Repeatable.",
    )
    parser.add_argument(
        "--generation-manifest",
        action="append",
        default=[],
        help="Prompt manifest JSONL path used to count fixed-budget attempts. Repeatable.",
    )
    parser.add_argument("--p2p-scope", action="append", default=[], help="P2P scope JSON path. Repeatable.")
    parser.add_argument("--p2p-validation", action="append", default=[], help="P2P validation JSONL path. Repeatable.")
    parser.add_argument("--task-id", action="append", default=[], help="Restrict output to a task id. Repeatable.")
    parser.add_argument("--out-jsonl", required=True)
    parser.add_argument("--summary-out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    validations = load_grouped(args.validation)
    generated = load_grouped(args.generated_candidates)
    manifests = load_grouped(args.generation_manifest)
    p2p_scopes = load_p2p_scopes(args.p2p_scope)
    p2p_validations = load_grouped(args.p2p_validation)
    task_ids = sorted(
        set(args.task_id) or (set(validations) | set(generated) | set(manifests) | set(p2p_scopes) | set(p2p_validations))
    )
    records = [
        build_task_record(
            task_id=task_id,
            validation_records=validations.get(task_id, []),
            generated_records=generated.get(task_id, []),
            generation_attempts=len(manifests.get(task_id, [])),
            p2p_scope=p2p_scopes.get(task_id),
            p2p_records=p2p_validations.get(task_id, []),
        )
        for task_id in task_ids
    ]
    write_jsonl(Path(args.out_jsonl), records)
    write_json(Path(args.summary_out), build_summary(records))
    print(json.dumps(build_summary(records), ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
