#!/usr/bin/env python3
"""Run one frozen P4 candidate pair in two fresh containers per candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "data/protocols/dsa_p4_preflight_v0_1.json"
EVIDENCE_CONTRACT = ROOT / "data/protocols/dsa_p3_evidence_contract_v0_1.json"
ORACLE_REGISTRY = ROOT / "data/hidden/dsa_p4_oracle_pool_registry_v0_1.json"
CANDIDATE_REGISTRY = ROOT / "data/hidden/dsa_p4_candidate_registry_v0_1.json"
RESULTS_OUT = ROOT / "data/hidden/dsa_p4_candidate_results_v0_1.json"
GATE_OUT = ROOT / "data/hidden/dsa_p4_task_gate_v0_1.json"
VISIBLE_OUT = ROOT / "data/cohorts/dsa_p4_model_visible_candidates_v0_1.json"
SEPARATION_OUT = ROOT / "data/protocols/dsa_p4_separation_audit_v0_1.json"
HASH_OUT = ROOT / "data/protocols/dsa_p4_candidate_hash_manifest_v0_1.json"
WORKER = ROOT / "scripts/dsa2026_p4_container_worker.py"
GROUPS = ("executable_basic", "visible_f2p", "visible_p2p", "hidden_regression")
VISIBLE_GROUPS = ("executable_basic", "visible_f2p", "visible_p2p")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def docker_json(arguments: list[str]) -> Any:
    return json.loads(
        subprocess.check_output(
            ["docker", *arguments],
            text=True,
            encoding="utf-8",
        )
    )


def image_python(image_data: dict[str, Any]) -> str:
    values = {
        item.split("=", 1)[0]: item.split("=", 1)[1]
        for item in image_data["Config"].get("Env", [])
        if "=" in item
    }
    environment = values.get("DSA_P4_PYTHON_ENV")
    if not environment:
        raise ValueError("task image lacks DSA_P4_PYTHON_ENV")
    return f"/opt/conda/envs/{environment}/bin/python"


def candidate_command(
    candidate: dict[str, Any],
    task: dict[str, Any],
    oracle: dict[str, Any],
) -> list[str]:
    command = [
        "/tmp/dsa2026_p4_container_worker.py",
        "candidate-run",
        "--candidate-patch", "/tmp/candidate.patch",
        "--expected-patch-sha256", candidate["patch_sha256"],
        "--expected-tree-sha256", candidate["candidate_tree_sha256"],
        "--timeout", "300",
    ]
    for path in task["reference_source_paths"]:
        command.extend(["--source-path", path])
    for value in task["declared_f2p_commands"]:
        command.extend(["--f2p-command", value])
    for value in oracle["visible_p2p_nodeids"]:
        command.extend(["--visible-node", value])
    for value in oracle["hidden_regression_nodeids"]:
        command.extend(["--hidden-node", value])
    return command


def run_fresh_container(
    task_id: str,
    candidate: dict[str, Any],
    run_id: str,
    task: dict[str, Any],
    oracle: dict[str, Any],
    runtime_dir: Path,
    image_data: dict[str, Any],
    total_timeout: int,
) -> dict[str, Any]:
    name = f"dsa-p4-{candidate['opaque_id'].replace('_', '-')}-{run_id.lower()}-{uuid.uuid4().hex[:8]}"
    patch_path = runtime_dir / "candidate_patches" / f"{candidate['opaque_id']}_run_{run_id.lower()}.patch"
    patch_path.parent.mkdir(parents=True, exist_ok=True)
    patch_path.write_bytes(candidate["patch_text"].encode("utf-8"))
    if sha256_bytes(patch_path.read_bytes()) != candidate["patch_sha256"]:
        raise ValueError("runtime candidate patch hash drift")
    command = candidate_command(candidate, task, oracle)
    container_id = subprocess.check_output(
        [
            "docker", "create", "--network", "none", "--name", name,
            "--entrypoint", image_python(image_data), oracle["task_image"], *command,
        ],
        text=True,
        encoding="utf-8",
    ).strip()
    try:
        subprocess.run(
            ["docker", "cp", str(WORKER), f"{container_id}:/tmp/dsa2026_p4_container_worker.py"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        subprocess.run(
            ["docker", "cp", str(patch_path), f"{container_id}:/tmp/candidate.patch"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        before = docker_json(["inspect", container_id])[0]
        if before.get("Mounts"):
            raise RuntimeError(f"fresh container unexpectedly has mounts: {before['Mounts']}")
        if before["Image"] != oracle["task_image_id"]:
            raise RuntimeError("fresh container image ID drift")
        started = subprocess.run(
            ["docker", "start", "--attach", container_id],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=total_timeout,
        )
        after = docker_json(["inspect", container_id])[0]
        lines = [line for line in started.stdout.splitlines() if line.strip()]
        if not lines:
            raise RuntimeError(f"worker returned no JSON: {started.stderr[-2000:]}")
        worker = json.loads(lines[-1])
        if "worker_error" in worker:
            raise RuntimeError(worker)
        return {
            "task_id": task_id,
            "opaque_id": candidate["opaque_id"],
            "run_id": run_id,
            "container_id": container_id,
            "container_name": name,
            "created": before["Created"],
            "image_id": before["Image"],
            "network_mode": before["HostConfig"]["NetworkMode"],
            "mounts": before["Mounts"],
            "container_exit_code": after["State"]["ExitCode"],
            "worker_sha256": sha256_bytes(WORKER.read_bytes()),
            "candidate_patch_sha256": candidate["patch_sha256"],
            "worker": worker,
        }
    finally:
        subprocess.run(
            ["docker", "rm", "-f", container_id],
            check=False,
            capture_output=True,
        )


def load_or_run(
    args: argparse.Namespace,
    task: dict[str, Any],
    oracle: dict[str, Any],
    materialization: dict[str, Any],
) -> dict[str, dict[str, dict[str, Any]]]:
    runtime_dir = Path(args.runtime_dir).resolve()
    image_values = docker_json(["image", "inspect", oracle["task_image"]])
    if len(image_values) != 1 or image_values[0]["Id"] != oracle["task_image_id"]:
        raise ValueError("task image is missing or drifted")
    candidates = materialization["candidates"]
    if args.write:
        jobs = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            for candidate in candidates:
                for run_id in ("A", "B"):
                    jobs.append(
                        executor.submit(
                            run_fresh_container,
                            args.task_id,
                            candidate,
                            run_id,
                            task,
                            oracle,
                            runtime_dir,
                            image_values[0],
                            args.total_timeout,
                        )
                    )
            values = [job.result() for job in jobs]
        runtime_dir.mkdir(parents=True, exist_ok=True)
        for value in values:
            path = runtime_dir / f"{value['opaque_id']}_run_{value['run_id'].lower()}.json"
            path.write_text(
                json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
                newline="\n",
            )
    else:
        values = []
        for candidate in candidates:
            for run_id in ("A", "B"):
                path = runtime_dir / f"{candidate['opaque_id']}_run_{run_id.lower()}.json"
                values.append(read_json(path))
    result: dict[str, dict[str, dict[str, Any]]] = {}
    for value in values:
        result.setdefault(value["opaque_id"], {})[value["run_id"]] = value
    expected = {item["opaque_id"] for item in candidates}
    if set(result) != expected or any(set(runs) != {"A", "B"} for runs in result.values()):
        raise ValueError("runtime result set is incomplete")
    return result


def check_map(run: dict[str, Any], group: str) -> dict[str, dict[str, Any]]:
    values = run["worker"][group]
    result = {item["check_code"]: item for item in values}
    if len(result) != len(values):
        raise ValueError(f"duplicate check code in {group}")
    return result


def check_consistency(a: dict[str, Any], b: dict[str, Any]) -> bool:
    fields = ("check_code", "command", "exit_code", "timed_out", "outcome")
    return all(a.get(field) == b.get(field) for field in fields)


def checks_pass(values: list[dict[str, Any]]) -> bool:
    return all(
        value["exit_code"] == 0
        and value["timed_out"] is False
        and value["outcome"] == "passed"
        for value in values
    )


def environment_signature(run: dict[str, Any]) -> dict[str, Any]:
    environment = run["worker"]["environment"]
    python = environment["python"]
    return {
        "image_id": run["image_id"],
        "network_mode": run["network_mode"],
        "mounts": run["mounts"],
        "worker_sha256": run["worker_sha256"],
        "python": {
            key: python[key]
            for key in ("command", "exit_code", "timed_out", "outcome", "output_sha256")
        },
        "build_artifacts": environment["build_artifacts"],
    }


def build_candidate_result(
    candidate: dict[str, Any],
    run_a: dict[str, Any],
    run_b: dict[str, Any],
) -> dict[str, Any]:
    if run_a["container_id"] == run_b["container_id"]:
        raise ValueError("candidate runs reused a container")
    comparisons: list[dict[str, Any]] = []
    group_consistency: dict[str, bool] = {}
    group_pass: dict[str, bool] = {}
    for group in GROUPS:
        a_values = check_map(run_a, group)
        b_values = check_map(run_b, group)
        if set(a_values) != set(b_values):
            raise ValueError(f"run check identities differ for {group}")
        rows = []
        for check_code in sorted(a_values):
            consistent = check_consistency(a_values[check_code], b_values[check_code])
            rows.append(
                {
                    "check_code": check_code,
                    "consistent": consistent,
                    "output_hash_equal": a_values[check_code]["output_sha256"] == b_values[check_code]["output_sha256"],
                    "run_a": a_values[check_code],
                    "run_b": b_values[check_code],
                }
            )
        comparisons.extend({"group": group, **row} for row in rows)
        group_consistency[group] = all(row["consistent"] for row in rows)
        group_pass[group] = checks_pass(list(a_values.values())) and checks_pass(list(b_values.values()))
    hidden_a = check_map(run_a, "hidden_regression")
    hidden_b = check_map(run_b, "hidden_regression")
    stable_hidden_failures = [
        hidden_a[code]["test_name"]
        for code in sorted(hidden_a)
        if check_consistency(hidden_a[code], hidden_b[code])
        and hidden_a[code]["outcome"] == "failed"
        and hidden_b[code]["outcome"] == "failed"
    ]
    environment_consistent = environment_signature(run_a) == environment_signature(run_b)
    tree_consistent = (
        run_a["worker"]["preparation"]["candidate_tree_sha256"]
        == run_b["worker"]["preparation"]["candidate_tree_sha256"]
        == candidate["candidate_tree_sha256"]
    )
    patch_consistent = (
        run_a["worker"]["preparation"]["candidate_patch_sha256"]
        == run_b["worker"]["preparation"]["candidate_patch_sha256"]
        == candidate["patch_sha256"]
    )
    all_groups_consistent = all(group_consistency.values())
    visible_pass = all(group_pass[group] for group in VISIBLE_GROUPS)
    hidden_pass = group_pass["hidden_regression"]
    integrity_pass = environment_consistent and tree_consistent and patch_consistent and all_groups_consistent
    if candidate["role"] == "oracle_positive":
        accepted = integrity_pass and visible_pass and hidden_pass
        disposition = "positive_valid" if accepted else "discard_positive_invalid"
    elif not integrity_pass:
        accepted = False
        disposition = "discard_environment_or_outcome_disagreement"
    elif not visible_pass:
        accepted = False
        disposition = "discard_visible_check_failure"
    elif stable_hidden_failures:
        accepted = True
        disposition = "negative_valid"
    else:
        accepted = False
        disposition = "discard_hidden_all_pass"
    run_metadata_fields = (
        "run_id", "container_id", "created", "image_id", "network_mode", "mounts",
        "container_exit_code", "worker_sha256", "candidate_patch_sha256",
    )
    return {
        "opaque_id": candidate["opaque_id"],
        "role": candidate["role"],
        "patch_sha256": candidate["patch_sha256"],
        "candidate_tree_sha256": candidate["candidate_tree_sha256"],
        "run_a": {key: run_a[key] for key in run_metadata_fields},
        "run_b": {key: run_b[key] for key in run_metadata_fields},
        "environment_signature": environment_signature(run_a),
        "environment_consistent": environment_consistent,
        "tree_consistent": tree_consistent,
        "patch_consistent": patch_consistent,
        "group_consistency": group_consistency,
        "group_pass": group_pass,
        "stable_hidden_failures": stable_hidden_failures,
        "visible_pass": visible_pass,
        "hidden_pass": hidden_pass,
        "integrity_pass": integrity_pass,
        "candidate_gate_pass": accepted,
        "disposition": disposition,
        "comparisons": comparisons,
    }


def replace_visible(value: str, replacements: list[tuple[str, str]]) -> str:
    result = value
    for source, target in replacements:
        result = result.replace(source, target)
    return result


def sanitize(value: Any, replacements: list[tuple[str, str]]) -> Any:
    if isinstance(value, str):
        return replace_visible(value, replacements)
    if isinstance(value, list):
        return [sanitize(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: sanitize(item, replacements) for key, item in value.items()}
    return value


def visible_environment(run: dict[str, Any]) -> dict[str, Any]:
    environment = run["worker"]["environment"]
    return {
        "runtime": environment["python"]["output_excerpt"].strip(),
        "dependency_lock_sha256": environment["build_artifacts"]["conda-explicit.txt"]["sha256"],
        "environment_image_sha256": run["image_id"],
    }


def visible_checks(
    values: list[dict[str, Any]],
    environment: dict[str, Any],
    replacements: list[tuple[str, str]],
    group: str,
) -> dict[str, Any]:
    if not values:
        raise ValueError(f"empty visible evidence group: {group}")
    keys = ["check_code", "command", "exit_code", "outcome", "output_excerpt"]
    if group == "executable_basic":
        keys.insert(1, "check_kind")
    else:
        keys.insert(1, "test_name")
    checks = [
        sanitize({key: value[key] for key in keys}, replacements)
        for value in values
    ]
    return {"environment": environment, "checks": checks}


def forbidden_key_findings(value: Any, fragments: list[str], path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            lowered = key.lower()
            if any(fragment in lowered for fragment in fragments):
                findings.append(f"{path}.{key}")
            findings.extend(forbidden_key_findings(item, fragments, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(forbidden_key_findings(item, fragments, f"{path}[{index}]"))
    return findings


def build_visible_records(
    task: dict[str, Any],
    materialization: dict[str, Any],
    runtime: dict[str, dict[str, dict[str, Any]]],
    admitted: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not admitted:
        return [], {
            "path_replacements": materialization["normalized_path_map"],
            "symbol_replacements": {task["project"]: "package_001"},
        }
    replacements = [
        (source, target)
        for source, target in sorted(
            materialization["normalized_path_map"].items(),
            key=lambda item: -len(item[0]),
        )
    ]
    replacements.extend(
        [
            (task["task_id"], "<TASK>"),
            (task["buggy_commit_id"], "<REVISION>"),
            (task["fixed_commit_id"], "<REVISION>"),
            (task["project"], "package_001"),
        ]
    )
    records = []
    for candidate in sorted(materialization["candidates"], key=lambda item: item["opaque_id"]):
        run = runtime[candidate["opaque_id"]]["A"]
        environment = sanitize(visible_environment(run), replacements)
        packet = sanitize(candidate["neutral_payload"], replacements)
        packet["executable_basic"] = visible_checks(
            run["worker"]["executable_basic"], environment, replacements, "executable_basic"
        )
        packet["visible_f2p"] = visible_checks(
            run["worker"]["visible_f2p"], environment, replacements, "visible_f2p"
        )
        packet["visible_p2p"] = visible_checks(
            run["worker"]["visible_p2p"], environment, replacements, "visible_p2p"
        )
        records.append({"opaque_id": candidate["opaque_id"], "packet": packet})
    return records, {
        "path_replacements": materialization["normalized_path_map"],
        "symbol_replacements": {task["project"]: "package_001"},
    }


def registry_with(
    path: Path,
    registry_id: str,
    record: dict[str, Any],
    task_id: str,
    visibility: str,
) -> dict[str, Any]:
    records = []
    if path.exists():
        records = [item for item in read_json(path).get("records", []) if item.get("task_id") != task_id]
    records.append(record)
    records.sort(key=lambda item: item["task_id"])
    return {
        "registry_id": registry_id,
        "created_date": "2026-07-11",
        "visibility": visibility,
        "records": records,
    }


def update_candidate_registry(
    registry: dict[str, Any],
    task_id: str,
    candidate_results: list[dict[str, Any]],
    task_gate: str,
    result_sha256: str,
) -> dict[str, Any]:
    updated = json.loads(json.dumps(registry))
    record = next(item for item in updated["records"] if item["task_id"] == task_id)
    by_id = {item["opaque_id"]: item for item in candidate_results}
    for candidate in record["candidates"]:
        result = by_id[candidate["opaque_id"]]
        candidate["candidate_gate_pass"] = result["candidate_gate_pass"]
        candidate["disposition"] = result["disposition"]
        candidate["candidate_result_sha256"] = sha256_bytes(canonical_bytes(result))
    record.update(
        {
            "status": "task_admitted" if task_gate == "ADMIT_PAIR" else "task_discarded",
            "candidate_outcome_observed": True,
            "task_gate": task_gate,
            "candidate_results_sha256": result_sha256,
        }
    )
    return updated


def update_oracle_registry(
    registry: dict[str, Any],
    task_id: str,
    task_gate: str,
    result_sha256: str,
) -> dict[str, Any]:
    updated = json.loads(json.dumps(registry))
    record = next(item for item in updated["records"] if item["task_id"] == task_id)
    record.update(
        {
            "status": "task_admitted" if task_gate == "ADMIT_PAIR" else "task_discarded",
            "transformed_candidate_materialized": True,
            "transformed_candidate_outcome_observed": True,
            "candidate_results_sha256": result_sha256,
            "task_gate": task_gate,
        }
    )
    return updated


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--runtime-dir", required=True)
    parser.add_argument("--total-timeout", type=int, default=9000)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    preflight = read_json(PREFLIGHT)
    task = next(item for item in preflight["tasks"] if item["task_id"] == args.task_id)
    oracle_registry = read_json(ORACLE_REGISTRY)
    oracle = next(item for item in oracle_registry["records"] if item["task_id"] == args.task_id)
    candidate_registry = read_json(CANDIDATE_REGISTRY)
    materialization = next(item for item in candidate_registry["records"] if item["task_id"] == args.task_id)
    if args.write:
        if oracle["status"] != "candidates_materialized_outcomes_not_observed":
            raise ValueError(f"unexpected pre-run oracle state: {oracle['status']}")
        if materialization["status"] != "materialized_outcomes_not_observed":
            raise ValueError(f"unexpected pre-run candidate state: {materialization['status']}")
        if materialization["candidate_outcome_observed"]:
            raise ValueError("candidate outcome already observed")
    runtime = load_or_run(args, task, oracle, materialization)
    candidate_results = [
        build_candidate_result(candidate, runtime[candidate["opaque_id"]]["A"], runtime[candidate["opaque_id"]]["B"])
        for candidate in materialization["candidates"]
    ]
    by_role = {item["role"]: item for item in candidate_results}
    positive_valid = by_role["oracle_positive"]["candidate_gate_pass"]
    negative_valid = by_role["hard_negative"]["candidate_gate_pass"]
    task_gate = "ADMIT_PAIR" if positive_valid and negative_valid else "DISCARD_TASK"
    task_result = {
        "task_id": args.task_id,
        "materialization_sha256": materialization["materialization_sha256"],
        "task_image_id": oracle["task_image_id"],
        "candidate_results": candidate_results,
        "positive_valid": positive_valid,
        "negative_valid": negative_valid,
        "task_gate": task_gate,
    }
    result_sha256 = sha256_bytes(canonical_bytes(task_result))
    task_result["candidate_results_sha256"] = result_sha256
    gate_record = {
        "task_id": args.task_id,
        "stream_role": task["role"],
        "stream_order": task["stream_order"],
        "task_gate": task_gate,
        "positive_disposition": by_role["oracle_positive"]["disposition"],
        "negative_disposition": by_role["hard_negative"]["disposition"],
        "candidate_results_sha256": result_sha256,
        "replacement_action": "none" if task_gate == "ADMIT_PAIR" else "use_next_frozen_reserve_when_full_P4_continues",
        "p4_final_gate_formed": False,
        "p5_entered": False,
        "model_api_calls": 0,
    }
    visible_records, visible_map = build_visible_records(
        task,
        materialization,
        runtime,
        task_gate == "ADMIT_PAIR",
    )
    existing_visible = read_json(VISIBLE_OUT).get("records", []) if VISIBLE_OUT.exists() else []
    current_ids = {item["opaque_id"] for item in materialization["candidates"]}
    visible_manifest = {
        "records": sorted(
            [item for item in existing_visible if item.get("opaque_id") not in current_ids] + visible_records,
            key=lambda item: item["opaque_id"],
        )
    }
    contract = read_json(EVIDENCE_CONTRACT)
    fragments = [item.lower() for item in contract["forbidden_visible_key_fragments"]]
    key_findings = forbidden_key_findings(visible_manifest, fragments)
    visible_serialized = canonical_bytes(visible_manifest).decode("utf-8").lower()
    forbidden_values = [
        task["task_id"].lower(),
        task["project"].lower(),
        task["buggy_commit_id"].lower(),
        task["fixed_commit_id"].lower(),
        "oracle_positive",
        "hard_negative",
    ]
    value_findings = [value for value in forbidden_values if value and value in visible_serialized]
    placeholder_findings = [
        value
        for value in ("not_run", "not_recorded", "placeholder", "unknown")
        if value in visible_serialized
    ]
    separation_record = {
        "task_id": args.task_id,
        "task_gate": task_gate,
        "hidden_candidate_count": len(candidate_results),
        "model_visible_candidate_count": len(visible_records),
        "expected_model_visible_candidate_count": 2 if task_gate == "ADMIT_PAIR" else 0,
        "key_leakage_findings": key_findings,
        "value_leakage_findings": value_findings,
        "placeholder_findings": placeholder_findings,
        "model_visible_map": visible_map,
        "hidden_model_visible_leakage_count": len(key_findings) + len(value_findings),
        "passed": not key_findings and not value_findings and not placeholder_findings,
    }
    if not separation_record["passed"]:
        raise ValueError(f"model-visible separation failed: {separation_record}")

    results_registry = registry_with(
        RESULTS_OUT,
        "dsa_p4_candidate_results_v0_1",
        task_result,
        args.task_id,
        "hidden_never_model_visible",
    )
    gate_registry = registry_with(
        GATE_OUT,
        "dsa_p4_task_gate_v0_1",
        gate_record,
        args.task_id,
        "hidden_never_model_visible",
    )
    separation_registry = registry_with(
        SEPARATION_OUT,
        "dsa_p4_separation_audit_v0_1",
        separation_record,
        args.task_id,
        "audit_not_model_input",
    )
    updated_candidates = update_candidate_registry(
        candidate_registry,
        args.task_id,
        candidate_results,
        task_gate,
        result_sha256,
    )
    updated_oracle = update_oracle_registry(
        oracle_registry,
        args.task_id,
        task_gate,
        result_sha256,
    )
    preliminary_outputs = {
        CANDIDATE_REGISTRY: json.dumps(updated_candidates, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        ORACLE_REGISTRY: json.dumps(updated_oracle, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        RESULTS_OUT: json.dumps(results_registry, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        GATE_OUT: json.dumps(gate_registry, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        VISIBLE_OUT: json.dumps(visible_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        SEPARATION_OUT: json.dumps(separation_registry, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    }
    hash_record = {
        "task_id": args.task_id,
        "materialization_sha256": materialization["materialization_sha256"],
        "candidate_results_sha256": result_sha256,
        "p2_raw_sha256": preflight["p2_raw_sha256"],
        "p3_manifest_aggregate": preflight["p3_manifest_audit"]["aggregate_actual"],
        "worker_sha256": sha256_bytes(WORKER.read_bytes()),
        "artifact_sha256": {
            path.relative_to(ROOT).as_posix(): sha256_bytes(content.encode("utf-8"))
            for path, content in preliminary_outputs.items()
        },
        "task_gate": task_gate,
        "p5_entered": False,
        "model_api_calls": 0,
    }
    hash_registry = registry_with(
        HASH_OUT,
        "dsa_p4_candidate_hash_manifest_v0_1",
        hash_record,
        args.task_id,
        "audit_not_model_input",
    )
    outputs = preliminary_outputs | {
        HASH_OUT: json.dumps(hash_registry, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    }
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    else:
        stale = [
            str(path.relative_to(ROOT))
            for path, content in outputs.items()
            if not path.exists() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            raise SystemExit(f"stale candidate outputs: {stale}")
    print(
        json.dumps(
            {
                "task_id": args.task_id,
                "task_gate": task_gate,
                "positive_disposition": by_role["oracle_positive"]["disposition"],
                "negative_disposition": by_role["hard_negative"]["disposition"],
                "negative_stable_hidden_failures": len(by_role["hard_negative"]["stable_hidden_failures"]),
                "model_visible_candidate_count": len(visible_records),
                "leakage_count": separation_record["hidden_model_visible_leakage_count"],
                "candidate_results_sha256": result_sha256,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
