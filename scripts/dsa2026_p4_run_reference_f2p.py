#!/usr/bin/env python3
"""Run a P4 official reference F2P in two fresh isolated containers."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "data/protocols/dsa_p4_preflight_v0_1.json"
CURSOR = ROOT / "data/protocols/dsa_p4_replacement_cursor_v0_1.json"
SOURCE_REGISTRY = ROOT / "data/protocols/dsa_p4_task_source_registry_v0_1.json"
RESULTS_OUT = ROOT / "data/hidden/dsa_p4_reference_f2p_results_v0_1.json"
DISCARD_OUT = ROOT / "data/hidden/dsa_p4_pre_candidate_discard_v0_1.json"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def docker_json(arguments: list[str]) -> Any:
    return json.loads(subprocess.check_output(["docker", *arguments], text=True, encoding="utf-8"))


def run_fresh_container(
    task_id: str,
    run_id: str,
    image: str,
    command_timeout: int,
    total_timeout: int,
) -> dict[str, Any]:
    short = task_id.removeprefix("bugsinpy_").replace("_", "-")
    name = f"dsa-p4-{short}-f2p-{run_id.lower()}-{uuid.uuid4().hex[:8]}"
    container_id = subprocess.check_output(
        [
            "docker", "create", "--network", "none", "--name", name,
            image, "official-f2p", "--timeout", str(command_timeout),
        ],
        text=True,
        encoding="utf-8",
    ).strip()
    before = docker_json(["inspect", container_id])[0]
    if before.get("Mounts"):
        subprocess.run(["docker", "rm", "-f", container_id], check=False, capture_output=True)
        raise RuntimeError(f"fresh container unexpectedly has mounts: {before['Mounts']}")
    try:
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
        worker = json.loads(lines[-1]) if lines else {
            "worker_error": "MissingWorkerOutput",
            "message": started.stderr[-2000:],
        }
        return {
            "run_id": run_id,
            "container_id": container_id,
            "container_name": name,
            "created": before["Created"],
            "image_id": before["Image"],
            "network_mode": before["HostConfig"]["NetworkMode"],
            "mounts": before["Mounts"],
            "container_exit_code": after["State"]["ExitCode"],
            "worker": worker,
        }
    finally:
        subprocess.run(["docker", "rm", "-f", container_id], check=False, capture_output=True)


def load_or_run(args: argparse.Namespace, runtime_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    paths = [runtime_dir / f"{args.task_id}_reference_f2p_{suffix}.json" for suffix in ("a", "b")]
    if args.write:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(
                    run_fresh_container,
                    args.task_id,
                    run_id,
                    args.image,
                    args.command_timeout,
                    args.total_timeout,
                )
                for run_id in ("A", "B")
            ]
            runs = [future.result() for future in futures]
        runtime_dir.mkdir(parents=True, exist_ok=True)
        for path, run in zip(paths, runs, strict=True):
            path.write_text(
                json.dumps(run, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
                newline="\n",
            )
        return runs[0], runs[1]
    return read_json(paths[0]), read_json(paths[1])


def compact_run(run: dict[str, Any]) -> dict[str, Any]:
    worker = run["worker"]
    value = {
        key: run[key]
        for key in (
            "run_id", "container_id", "created", "image_id", "network_mode",
            "mounts", "container_exit_code",
        )
    }
    if "worker_error" in worker:
        value["worker_error"] = worker
        value["checks"] = []
        return value
    value["preparation"] = worker["preparation"]
    value["environment"] = worker["environment"]
    value["checks"] = worker["checks"]
    return value


def environment_fingerprint(environment: dict[str, Any]) -> dict[str, Any]:
    python = environment["python"]
    return {
        "python": {
            key: python[key]
            for key in ("command", "exit_code", "timed_out", "outcome", "output_sha256", "output_excerpt")
        },
        "build_artifacts": environment["build_artifacts"],
    }


def build_result(
    args: argparse.Namespace,
    run_a: dict[str, Any],
    run_b: dict[str, Any],
) -> dict[str, Any]:
    preflight = read_json(PREFLIGHT)
    cursor = read_json(CURSOR)
    source_root = read_json(SOURCE_REGISTRY)
    task = next(item for item in preflight["tasks"] if item["task_id"] == args.task_id)
    source = next(item for item in source_root["records"] if item["task_id"] == args.task_id)
    if cursor["cursor"]["next_task_id"] != args.task_id:
        raise ValueError("task does not equal current frozen cursor")
    if source["candidate_materialized"] or source["candidate_outcome_observed"]:
        raise ValueError("source registry records forbidden candidate activity")
    image = docker_json(["image", "inspect", args.image])[0]
    labels = image.get("Config", {}).get("Labels", {}) or {}
    expected_labels = {
        "dsa2026.p4.task_id": args.task_id,
        "dsa2026.p4.project": task["project"],
        "dsa2026.p4.python_env": args.python_env,
        "dsa2026.p4.buggy_commit": task["buggy_commit_id"],
        "dsa2026.p4.fixed_commit": task["fixed_commit_id"],
        "dsa2026.p4.candidate_materialized": "false",
        "dsa2026.p4.model_api_called": "false",
    }
    label_match = all(labels.get(key) == value for key, value in expected_labels.items())
    compact_a = compact_run(run_a)
    compact_b = compact_run(run_b)
    worker_ok = "worker_error" not in run_a["worker"] and "worker_error" not in run_b["worker"]
    declared = task["declared_f2p_commands"]

    def run_passed(run: dict[str, Any]) -> bool:
        worker = run["worker"]
        return (
            "worker_error" not in worker
            and len(worker.get("checks", [])) == len(declared)
            and all(
                check["command"] == ["/bin/bash", "-c", command]
                and check["exit_code"] == 0
                and check["timed_out"] is False
                and check["outcome"] == "passed"
                for check, command in zip(worker["checks"], declared, strict=True)
            )
        )

    run_a_passed = run_passed(run_a)
    run_b_passed = run_passed(run_b)
    if worker_ok:
        preparation_equal = run_a["worker"]["preparation"] == run_b["worker"]["preparation"]
        environment_equal = environment_fingerprint(run_a["worker"]["environment"]) == environment_fingerprint(
            run_b["worker"]["environment"]
        )
        outcomes_equal = [
            (item["exit_code"], item["timed_out"], item["outcome"])
            for item in run_a["worker"]["checks"]
        ] == [
            (item["exit_code"], item["timed_out"], item["outcome"])
            for item in run_b["worker"]["checks"]
        ]
    else:
        preparation_equal = False
        environment_equal = False
        outcomes_equal = False
    isolation_passed = all(
        run["network_mode"] == "none" and run["mounts"] == [] and run["image_id"] == image["Id"]
        for run in (run_a, run_b)
    )
    reference_f2p_passed = (
        label_match and isolation_passed and run_a_passed and run_b_passed
        and preparation_equal and environment_equal and outcomes_equal
    )
    result = {
        "task_id": args.task_id,
        "project": task["project"],
        "stream_role": task["role"],
        "stream_order": task["stream_order"],
        "status": "reference_f2p_passed_pre_pool" if reference_f2p_passed else "discard_pre_candidate_reference_f2p_failure",
        "executor_commit": args.executor_commit,
        "cursor_sha256": cursor["cursor_sha256"],
        "source_record_sha256": source["record_sha256"],
        "task_image": args.image,
        "task_image_id": image["Id"],
        "image_labels_match": label_match,
        "isolation_passed": isolation_passed,
        "reference_preparation_equal": preparation_equal,
        "environment_equal": environment_equal,
        "f2p_outcomes_equal": outcomes_equal,
        "run_a_passed": run_a_passed,
        "run_b_passed": run_b_passed,
        "reference_f2p_passed": reference_f2p_passed,
        "run_a": compact_a,
        "run_b": compact_b,
        "regression_pool_discovered_or_frozen": False,
        "transformed_candidate_materialized": False,
        "transformed_candidate_outcome_observed": False,
        "model_api_calls": 0,
    }
    result["record_sha256"] = sha256_bytes(canonical_bytes(result))
    return result


def registry_with(path: Path, registry_id: str, visibility: str, record: dict[str, Any]) -> dict[str, Any]:
    records = []
    if path.exists():
        records = [item for item in read_json(path).get("records", []) if item["task_id"] != record["task_id"]]
    records.append(record)
    records.sort(key=lambda item: (item.get("stream_role", ""), item.get("stream_order", 0), item["task_id"]))
    return {
        "registry_id": registry_id,
        "created_date": "2026-07-11",
        "visibility": visibility,
        "records": records,
    }


def discard_record(result: dict[str, Any]) -> dict[str, Any]:
    record = {
        "task_id": result["task_id"],
        "project": result["project"],
        "stream_role": result["stream_role"],
        "stream_order": result["stream_order"],
        "status": "discard_pre_candidate_reference_f2p_failure",
        "reason_code": "official_reference_f2p_failed_or_disagreed_in_dual_fresh_environments",
        "cursor_sha256": result["cursor_sha256"],
        "source_record_sha256": result["source_record_sha256"],
        "task_image_created": True,
        "task_image_id": result["task_image_id"],
        "reference_f2p_result_sha256": result["record_sha256"],
        "official_reference_f2p_executed": True,
        "reference_f2p_passed": False,
        "regression_pool_discovered_or_frozen": False,
        "transformed_candidate_materialized": False,
        "transformed_candidate_outcome_observed": False,
        "model_api_calls": 0,
        "dependency_or_oracle_repair_performed": False,
    }
    record["record_sha256"] = sha256_bytes(canonical_bytes(record))
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--python-env", required=True)
    parser.add_argument("--executor-commit", required=True)
    parser.add_argument("--runtime-dir", required=True)
    parser.add_argument("--command-timeout", type=int, default=300)
    parser.add_argument("--total-timeout", type=int, default=900)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", args.executor_commit, "HEAD"],
        cwd=ROOT,
        capture_output=True,
    ).returncode != 0:
        raise SystemExit("executor commit is not an ancestor of HEAD")
    run_a, run_b = load_or_run(args, Path(args.runtime_dir).resolve())
    result = build_result(args, run_a, run_b)
    results_registry = registry_with(
        RESULTS_OUT,
        "dsa_p4_reference_f2p_results_v0_1",
        "private_hidden_pre_candidate_reference_evidence",
        result,
    )
    outputs = {
        RESULTS_OUT: json.dumps(results_registry, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    }
    if not result["reference_f2p_passed"]:
        discard_registry = registry_with(
            DISCARD_OUT,
            "dsa_p4_pre_candidate_discard_v0_1",
            "private_hidden_environment_gate",
            discard_record(result),
        )
        discard_registry["boundary"] = (
            "Pre-candidate environment/reference evidence only; no regression pool, transformed candidate, prompt, P5, or model outcome."
        )
        outputs[DISCARD_OUT] = json.dumps(discard_registry, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    else:
        stale = [
            str(path.relative_to(ROOT)) for path, content in outputs.items()
            if not path.exists() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            raise SystemExit(f"stale reference F2P outputs: {stale}")
    print(json.dumps({
        "task_id": result["task_id"],
        "task_image_id": result["task_image_id"],
        "container_ids": [result["run_a"]["container_id"], result["run_b"]["container_id"]],
        "reference_f2p_passed": result["reference_f2p_passed"],
        "status": result["status"],
        "record_sha256": result["record_sha256"],
        "candidate_materialized": result["transformed_candidate_materialized"],
        "model_api_calls": result["model_api_calls"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
