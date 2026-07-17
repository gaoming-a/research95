# ruff: noqa: E402
#!/usr/bin/env python3
"""Build or replay the frozen V2-P2 order-1 task image."""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/dsa2026_v2_p2_build_task_image.py")

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from dsa2026_v2_p2_freeze_task_context import signed_amendment, tree_sha256


ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "bugsinpy_pandas_161"
IMAGE = f"dsa2026-v2-p2-task:{TASK_ID}"
SOURCE_REGISTRY = ROOT / "data/protocols/dsa_v2_p2_task_source_registry_v0_1.json"
CONTEXT = ROOT / f"tmp/dsa2026_v2_p2_runtime/task_contexts/{TASK_ID}"
RUNTIME = ROOT / "tmp/dsa2026_v2_p2_runtime/environment"
OUT = ROOT / "data/protocols/dsa_v2_p2_pandas_161_environment_v0_1.json"
TERMINAL = ROOT / "data/protocols/dsa_v2_p2_terminal_ledger_v0_1.json"
DOCKERFILE = ROOT / "containers/dsa2026_v2_p2/Dockerfile.task"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def docker_json(arguments: list[str]) -> Any:
    return json.loads(subprocess.check_output(["docker", *arguments], text=True, encoding="utf-8"))


def validate_source() -> dict[str, Any]:
    signed_amendment()
    registry = read_json(SOURCE_REGISTRY)
    if registry.get("status") != "order_1_source_frozen" or len(registry.get("records", [])) != 1:
        raise PermissionError("V2-P2 order-1 source registry is not frozen")
    record = registry["records"][0]
    if record.get("task_id") != TASK_ID or record.get("order") != 1:
        raise PermissionError("source registry cursor drift")
    expected = record["context"]["context_tree_sha256"]
    if not CONTEXT.is_dir() or tree_sha256(CONTEXT) != expected:
        raise PermissionError("source context tree drift")
    return record


def terminal_ledger(environment: dict[str, Any]) -> dict[str, Any]:
    record = {
        "order": 1,
        "task_id": TASK_ID,
        "disposition": "materialization-failed",
        "reason": "environment-build-failure",
        "selected_candidate_sha256": None,
        "environment_record_sha256": sha256_bytes(
            json.dumps(environment, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
        ),
    }
    return {
        "ledger_id": "dsa_v2_p2_terminal_ledger_v0_1",
        "created_date": "2026-07-12",
        "status": "order_1_terminal",
        "records": [record],
        "next_order": 2,
        "next_task_id": "bugsinpy_fastapi_11",
        "next_task_started": False,
        "model_api_calls": 0,
    }


def run_build(timeout: int) -> dict[str, Any]:
    source = validate_source()
    RUNTIME.mkdir(parents=True, exist_ok=True)
    command = [
        "docker", "build", "--progress", "plain", "--no-cache",
        "-f", str(DOCKERFILE), "-t", IMAGE, str(ROOT),
    ]
    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        timeout=timeout,
    )
    output = result.stdout + result.stderr
    (RUNTIME / f"{TASK_ID}_docker_build.log").write_bytes(output)
    image_record = None
    if result.returncode == 0:
        inspected = docker_json(["image", "inspect", IMAGE])[0]
        labels = inspected.get("Config", {}).get("Labels", {}) or {}
        expected_labels = {
            "dsa2026.v2_p2.task_id": TASK_ID,
            "dsa2026.v2_p2.order": "1",
            "dsa2026.v2_p2.project": "pandas",
            "dsa2026.v2_p2.python_env": "py383",
            "dsa2026.v2_p2.buggy_commit": "a818281",
            "dsa2026.v2_p2.fixed_commit": "ca5198a6daa7757e398112a17ccadc9e7d078d96",
            "dsa2026.v2_p2.official_setup_executed": "false",
            "dsa2026.v2_p2.model_api_called": "false",
        }
        image_record = {
            "image": IMAGE,
            "image_id": inspected["Id"],
            "repo_digests": inspected.get("RepoDigests", []),
            "labels": {key: labels.get(key) for key in expected_labels},
            "labels_match": all(labels.get(key) == value for key, value in expected_labels.items()),
        }
        if not image_record["labels_match"]:
            raise RuntimeError("built image labels drift")
    payload = {
        "environment_id": "dsa_v2_p2_pandas_161_environment_v0_1",
        "created_date": "2026-07-12",
        "task_id": TASK_ID,
        "order": 1,
        "status": "environment-built-oracle-not-started" if result.returncode == 0 else "materialization-failed",
        "failure_reason": None if result.returncode == 0 else "environment-build-failure",
        "source_record_sha256": source["record_sha256"],
        "dockerfile_sha256": sha256_bytes(DOCKERFILE.read_bytes()),
        "build_command": ["docker", "build", "--progress", "plain", "--no-cache", "-f", "<DOCKERFILE>", "-t", IMAGE, "<ROOT>"],
        "build_exit_code": result.returncode,
        "build_output_sha256": sha256_bytes(output),
        "build_output_bytes": len(output),
        "image": image_record,
        "official_setup_executed": False,
        "task_specific_repair_attempted": False,
        "activity": {
            "real_task_checkouts": 1,
            "environment_builds": 1,
            "containers_started": 0,
            "project_tests_run": 0,
            "prompt_renders": 0,
            "api_keys_read": 0,
            "model_api_calls": 0,
        },
        "boundary": "An environment failure is terminal for order 1; success permits only the frozen dual-fresh oracle stage.",
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    if result.returncode != 0:
        ledger = terminal_ledger(payload)
        TERMINAL.write_text(json.dumps(ledger, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return payload


def replay() -> dict[str, Any]:
    validate_source()
    payload = read_json(OUT)
    if payload.get("task_id") != TASK_ID or payload.get("order") != 1:
        raise ValueError("environment record cursor drift")
    if payload["status"] == "environment-built-oracle-not-started":
        inspected = docker_json(["image", "inspect", payload["image"]["image_id"]])[0]
        if inspected["Id"] != payload["image"]["image_id"] or not payload["image"]["labels_match"]:
            raise ValueError("task image replay drift")
    elif payload["status"] == "materialization-failed":
        if not TERMINAL.is_file() or read_json(TERMINAL)["records"][0]["reason"] != "environment-build-failure":
            raise ValueError("environment failure terminal ledger missing")
    else:
        raise ValueError("unknown environment status")
    if payload["activity"]["model_api_calls"] != 0 or payload["task_specific_repair_attempted"]:
        raise ValueError("environment boundary drift")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--timeout", type=int, default=7200)
    args = parser.parse_args()
    payload = run_build(args.timeout) if args.run else replay()
    print(json.dumps({
        "status": payload["status"],
        "task_id": TASK_ID,
        "order": 1,
        "build_exit_code": payload["build_exit_code"],
        "containers_started": payload["activity"]["containers_started"],
        "model_api_calls": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
