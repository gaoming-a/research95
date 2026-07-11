#!/usr/bin/env python3
"""Record and replay-audit a P4 task discarded at the environment gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "data/protocols/dsa_p4_preflight_v0_1.json"
CURSOR = ROOT / "data/protocols/dsa_p4_replacement_cursor_v0_1.json"
SOURCE_REGISTRY = ROOT / "data/protocols/dsa_p4_task_source_registry_v0_1.json"
POOL_REGISTRY = ROOT / "data/hidden/dsa_p4_oracle_pool_registry_v0_1.json"
CANDIDATE_REGISTRY = ROOT / "data/hidden/dsa_p4_candidate_registry_v0_1.json"
CANDIDATE_RESULTS = ROOT / "data/hidden/dsa_p4_candidate_results_v0_1.json"
OUT = ROOT / "data/hidden/dsa_p4_pre_candidate_discard_v0_1.json"
TASK_IMAGE = "dsa2026-p4-task:bugsinpy_tornado_10"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def exit_code(runtime: Path, name: str) -> int:
    return int((runtime / name).read_text(encoding="utf-8").strip())


def task_absent(path: Path, task_id: str) -> bool:
    if not path.exists():
        return True
    return not any(item.get("task_id") == task_id for item in read_json(path).get("records", []))


def build_record(task_id: str, runtime: Path, attempted_commit: str) -> dict[str, Any]:
    preflight = read_json(PREFLIGHT)
    cursor = read_json(CURSOR)
    source_registry = read_json(SOURCE_REGISTRY)
    task = next(item for item in preflight["tasks"] if item["task_id"] == task_id)
    source = next(item for item in source_registry["records"] if item["task_id"] == task_id)
    if cursor["cursor"]["next_task_id"] != task_id:
        raise ValueError("task does not equal the frozen cursor")
    if source["candidate_materialized"] or source["candidate_outcome_observed"]:
        raise ValueError("source registry records forbidden candidate activity")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", attempted_commit, "HEAD"],
        cwd=ROOT,
        capture_output=True,
    ).returncode != 0:
        raise ValueError("attempted commit is not an ancestor of HEAD")

    setup_path = ROOT / "tmp/dsa2026_p4_runtime/task_contexts" / task_id / "metadata/setup.sh"
    if sha256_file(setup_path) != task["metadata_sha256"]["setup"]:
        raise ValueError("setup metadata hash drift")
    commands = [line.strip() for line in setup_path.read_text(encoding="utf-8").replace("\r", "").splitlines() if line.strip()]
    if commands != ["pip install unittest", "pip install python-gettext", "pip install tornado"]:
        raise ValueError(f"unexpected frozen setup commands: {commands}")

    status = {
        "requirements_before": exit_code(runtime, "requirements_before.exit_code"),
        "setup_1": exit_code(runtime, "setup_1.exit_code"),
        "setup_2": exit_code(runtime, "setup_2.exit_code"),
        "setup_3": exit_code(runtime, "setup_3.exit_code"),
        "requirements_after": exit_code(runtime, "requirements_after.exit_code"),
        "pip_check": exit_code(runtime, "pip_check.exit_code"),
        "setup_overall": exit_code(runtime, "setup_status.txt"),
    }
    if status != {
        "requirements_before": 0,
        "setup_1": 1,
        "setup_2": 0,
        "setup_3": 0,
        "requirements_after": 0,
        "pip_check": 0,
        "setup_overall": 1,
    }:
        raise ValueError(f"environment failure signature drift: {status}")
    setup_1_log = (runtime / "setup_1.log").read_text(encoding="utf-8", errors="replace")
    required_markers = [
        "Could not find a version that satisfies the requirement unittest",
        "No matching distribution found for unittest",
    ]
    if not all(marker in setup_1_log for marker in required_markers):
        raise ValueError("setup_1 failure reason drift")

    activity = {
        "oracle_pool_record_absent": task_absent(POOL_REGISTRY, task_id),
        "candidate_registry_record_absent": task_absent(CANDIDATE_REGISTRY, task_id),
        "candidate_result_record_absent": task_absent(CANDIDATE_RESULTS, task_id),
        "source_registry_candidate_materialized": source["candidate_materialized"],
        "source_registry_candidate_outcome_observed": source["candidate_outcome_observed"],
        "source_registry_model_api_calls": source["model_api_calls"],
    }
    if activity != {
        "oracle_pool_record_absent": True,
        "candidate_registry_record_absent": True,
        "candidate_result_record_absent": True,
        "source_registry_candidate_materialized": False,
        "source_registry_candidate_outcome_observed": False,
        "source_registry_model_api_calls": 0,
    }:
        raise ValueError(f"forbidden post-environment activity found: {activity}")

    logs = {
        path.name: {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted(runtime.iterdir(), key=lambda item: item.name)
        if path.is_file()
    }
    lock = next(
        item for item in preflight["environment_bootstrap"]["locks"]
        if item["python_version"] == task["python_version"]
    )
    record = {
        "task_id": task_id,
        "project": task["project"],
        "stream_role": task["role"],
        "stream_order": task["stream_order"],
        "status": "discard_pre_candidate_environment_build_failure",
        "reason_code": "official_setup_command_uninstallable_stdlib_distribution",
        "attempted_from_commit": attempted_commit,
        "cursor_sha256": cursor["cursor_sha256"],
        "source_record_sha256": source["record_sha256"],
        "python_version": task["python_version"],
        "environment_name": lock["environment_name"],
        "environment_lock_sha256": lock["actual_sha256"],
        "toolchain_image": preflight["environment_bootstrap"]["toolchain_image"],
        "toolchain_image_id": preflight["environment_bootstrap"]["toolchain_image_id"],
        "task_image": TASK_IMAGE,
        "task_image_created": False,
        "frozen_setup_sha256": task["metadata_sha256"]["setup"],
        "frozen_setup_commands": commands,
        "command_exit_codes": status,
        "failed_command_index": 1,
        "failed_command": commands[0],
        "failure_markers": required_markers,
        "runtime_log_manifest": logs,
        "activity_audit": activity,
        "official_reference_f2p_executed": False,
        "regression_pool_discovered_or_frozen": False,
        "transformed_candidate_materialized": False,
        "transformed_candidate_outcome_observed": False,
        "model_api_calls": 0,
        "dependency_or_oracle_repair_performed": False,
        "disposition_rule": "Discard the task before candidate activity when the frozen official environment build fails; do not alter dependencies, oracle, transform, or task.",
    }
    record["record_sha256"] = sha256_bytes(canonical_bytes(record))
    return record


def registry_with(record: dict[str, Any]) -> dict[str, Any]:
    records = []
    if OUT.exists():
        records = [item for item in read_json(OUT).get("records", []) if item["task_id"] != record["task_id"]]
    records.append(record)
    records.sort(key=lambda item: (item["stream_role"], item["stream_order"], item["task_id"]))
    return {
        "registry_id": "dsa_p4_pre_candidate_discard_v0_1",
        "created_date": "2026-07-11",
        "visibility": "private_hidden_environment_gate",
        "records": records,
        "boundary": "Environment-gate evidence only; no F2P, regression-pool, transformed-candidate, prompt, P5, or model outcome.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--runtime-dir", required=True)
    parser.add_argument("--attempted-commit", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    runtime = Path(args.runtime_dir).resolve()
    if args.write:
        image_check = subprocess.run(
            ["docker", "image", "inspect", TASK_IMAGE],
            cwd=ROOT,
            capture_output=True,
        )
        if image_check.returncode == 0:
            raise SystemExit(f"task image unexpectedly exists: {TASK_IMAGE}")
    record = build_record(args.task_id, runtime, args.attempted_commit)
    registry = registry_with(record)
    content = json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(content, encoding="utf-8", newline="\n")
    elif not OUT.exists() or OUT.read_text(encoding="utf-8") != content:
        raise SystemExit(f"stale discard evidence: {OUT.relative_to(ROOT)}")
    print(json.dumps({
        "task_id": record["task_id"],
        "status": record["status"],
        "reason_code": record["reason_code"],
        "record_sha256": record["record_sha256"],
        "candidate_materialized": record["transformed_candidate_materialized"],
        "model_api_calls": record["model_api_calls"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
