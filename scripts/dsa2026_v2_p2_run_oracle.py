#!/usr/bin/env python3
"""Run the V2-P2 order-1 dual-fresh oracle and freeze its visible/hidden split."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shlex
import subprocess
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from unidiff import PatchSet

from dsa2026_v2_p2_freeze_task_context import signed_amendment


ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "bugsinpy_pandas_161"
ORDER = 1
ORACLE_ID = "dsa_v2_p2_pandas_161_oracle_v0_1"
ENVIRONMENT = ROOT / "data/protocols/dsa_v2_p2_pandas_161_environment_v0_1.json"
SOURCE = ROOT / "data/protocols/dsa_v2_p2_task_source_registry_v0_1.json"
PROTOCOL = ROOT / "data/protocols/dsa_v2_p1_construction_protocol_v0_1.json"
CONTEXT = ROOT / f"tmp/dsa2026_v2_p2_runtime/task_contexts/{TASK_ID}"
RUNTIME = ROOT / "tmp/dsa2026_v2_p2_runtime/oracle"
OUT = ROOT / "data/hidden/dsa_v2_p2_pandas_161_oracle_v0_1.json"
TERMINAL = ROOT / "data/protocols/dsa_v2_p2_terminal_ledger_v0_1.json"
GENERIC_TOKENS = {"init", "lib", "main", "py", "source", "src", "test", "testing", "tests"}
TIE_SEED = "DSA-V2-P1-REGRESSION-POOL-20260712-V1"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def stable_check(check: dict[str, Any]) -> dict[str, Any]:
    return {key: check.get(key) for key in ("exit_code", "timed_out", "outcome", "output_sha256")}


def stable_environment(environment: dict[str, Any]) -> dict[str, Any]:
    return {
        "python": stable_check(environment["python"]),
        "build_artifacts": environment["build_artifacts"],
    }


def worker_fingerprint(worker: dict[str, Any]) -> dict[str, Any]:
    value: dict[str, Any] = {
        "preparation": worker.get("preparation"),
        "environment": stable_environment(worker["environment"]) if "environment" in worker else None,
    }
    for field in ("checks", "executable_basic", "visible_f2p", "visible_p2p", "hidden_regression"):
        if field in worker:
            value[field] = [stable_check(item) | ({"nodeid": item.get("nodeid")} if "nodeid" in item else {}) for item in worker[field]]
    return value


def docker_json(arguments: list[str]) -> Any:
    return json.loads(subprocess.check_output(["docker", *arguments], text=True, encoding="utf-8"))


def run_container(
    image_id: str,
    label: str,
    command: list[str],
    timeout: int,
    copy_source: Path | None = None,
    copy_target: str | None = None,
) -> dict[str, Any]:
    name = f"dsa-v2-p2-{label}-{uuid.uuid4().hex[:10]}"
    container_id = subprocess.check_output(
        ["docker", "create", "--network", "none", "--name", name, image_id, *command],
        text=True,
        encoding="utf-8",
    ).strip()
    before = docker_json(["inspect", container_id])[0]
    if before["Mounts"] or before["HostConfig"]["NetworkMode"] != "none" or before["Image"] != image_id:
        subprocess.run(["docker", "rm", "-f", container_id], check=False, capture_output=True)
        raise RuntimeError("fresh container isolation drift")
    try:
        if copy_source is not None and copy_target is not None:
            subprocess.run(["docker", "cp", str(copy_source), f"{container_id}:{copy_target}"], check=True)
        result = subprocess.run(
            ["docker", "start", "--attach", container_id],
            capture_output=True,
            timeout=timeout,
        )
        output = result.stdout + result.stderr
        RUNTIME.mkdir(parents=True, exist_ok=True)
        (RUNTIME / f"{label}_{container_id[:12]}.log").write_bytes(output)
        lines = [line for line in output.decode("utf-8", errors="replace").splitlines() if line.strip()]
        worker = json.loads(lines[-1]) if lines else {"worker_error": "MissingWorkerOutput"}
        after = docker_json(["inspect", container_id])[0]
        return {
            "container_id": container_id,
            "container_name": name,
            "image_id": before["Image"],
            "network_mode": before["HostConfig"]["NetworkMode"],
            "mounts": before["Mounts"],
            "container_exit_code": after["State"]["ExitCode"],
            "output_sha256": sha256_bytes(output),
            "output_bytes": len(output),
            "worker": worker,
        }
    finally:
        subprocess.run(["docker", "rm", "-f", container_id], check=False, capture_output=True)


def dual_run(image_id: str, label: str, command: list[str], timeout: int, patch: Path | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    def one(suffix: str) -> dict[str, Any]:
        return run_container(
            image_id,
            f"{label}-{suffix}",
            command,
            timeout,
            patch,
            f"/tmp/{label}-{suffix}.patch" if patch else None,
        )
    commands = []
    if patch:
        for suffix in ("a", "b"):
            target = f"/tmp/{label}-{suffix}.patch"
            commands.append((suffix, [target if item == "<PATCH>" else item for item in command]))
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(run_container, image_id, f"{label}-{suffix}", cmd, timeout, patch, f"/tmp/{label}-{suffix}.patch") for suffix, cmd in commands]
            return futures[0].result(), futures[1].result()
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(one, suffix) for suffix in ("a", "b")]
        return futures[0].result(), futures[1].result()


def all_pass(checks: list[dict[str, Any]]) -> bool:
    return bool(checks) and all(item.get("outcome") == "passed" and item.get("exit_code") == 0 and not item.get("timed_out") for item in checks)


def official_f2p_pass(run: dict[str, Any], expected_count: int) -> bool:
    worker = run["worker"]
    return (
        "worker_error" not in worker
        and run["container_exit_code"] == 0
        and len(worker.get("checks", [])) == expected_count
        and all_pass(worker["checks"])
    )


def candidate_pass(run: dict[str, Any], hidden_must_pass: bool) -> bool:
    worker = run["worker"]
    if "worker_error" in worker or run["container_exit_code"] != 0:
        return False
    required = worker.get("executable_basic", []) + worker.get("visible_f2p", []) + worker.get("visible_p2p", [])
    hidden = worker.get("hidden_regression", [])
    return all_pass(required) and bool(hidden) and (all_pass(hidden) if hidden_must_pass else not all_pass(hidden))


def tokens(value: str) -> set[str]:
    return {item for item in re.findall(r"[a-z0-9]+", value.lower()) if len(item) >= 2 and item not in GENERIC_TOKENS}


def source_paths() -> list[str]:
    patch_text = (CONTEXT / "metadata/bug_patch.txt").read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    patch = PatchSet(patch_text.splitlines(keepends=True))
    return [item.path for item in patch]


def f2p_nodeids(commands: list[str]) -> set[str]:
    result = set()
    for command in commands:
        parts = shlex.split(command)
        if parts and Path(parts[0]).name == "pytest":
            result.update(item for item in parts[1:] if not item.startswith("-"))
    return result


def freeze_pool(collected: list[str], paths: list[str], excluded: set[str]) -> list[dict[str, Any]]:
    source_token_set = set().union(*(tokens(path) for path in paths))
    rows = []
    for nodeid in sorted(set(collected) - excluded):
        rows.append({
            "nodeid": nodeid,
            "relatedness": len(source_token_set & tokens(nodeid)),
            "tie_sha256": sha256_bytes(f"{TIE_SEED}|{TASK_ID}|{nodeid}".encode("utf-8")),
        })
    rows.sort(key=lambda item: (-item["relatedness"], item["tie_sha256"], item["nodeid"]))
    return rows[:40]


def write_terminal(reason: str, oracle: dict[str, Any]) -> None:
    digest = sha256_bytes(json.dumps(oracle, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    ledger = {
        "ledger_id": "dsa_v2_p2_terminal_ledger_v0_1",
        "created_date": "2026-07-12",
        "status": "order_1_terminal",
        "records": [{
            "order": ORDER,
            "task_id": TASK_ID,
            "disposition": "materialization-failed",
            "reason": reason,
            "selected_candidate_sha256": None,
            "oracle_record_sha256": digest,
        }],
        "next_order": 2,
        "next_task_id": "bugsinpy_fastapi_11",
        "next_task_started": False,
        "model_api_calls": 0,
    }
    TERMINAL.write_text(json.dumps(ledger, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def execute(timeout: int, collection_timeout: int) -> dict[str, Any]:
    signed_amendment()
    environment = read_json(ENVIRONMENT)
    source = read_json(SOURCE)["records"][0]
    if environment.get("status") != "environment-built-oracle-not-started":
        raise PermissionError("task environment is not ready for oracle")
    if TERMINAL.is_file():
        raise PermissionError("order 1 already has a terminal disposition")
    image_id = environment["image"]["image_id"]
    f2p_commands = source["source_record"]["declared_f2p_commands"]
    paths = source_paths()
    f2p_a, f2p_b = dual_run(image_id, "official-f2p", ["official-f2p", "--timeout", str(timeout)], timeout * max(2, len(f2p_commands) + 1))
    f2p_ok = (
        official_f2p_pass(f2p_a, len(f2p_commands))
        and official_f2p_pass(f2p_b, len(f2p_commands))
        and worker_fingerprint(f2p_a["worker"]) == worker_fingerprint(f2p_b["worker"])
    )
    payload: dict[str, Any] = {
        "oracle_id": ORACLE_ID,
        "created_date": "2026-07-12",
        "task_id": TASK_ID,
        "order": ORDER,
        "task_image_id": image_id,
        "source_paths": paths,
        "official_f2p": {"run_a": f2p_a, "run_b": f2p_b, "dual_pass": f2p_ok},
        "model_api_calls": 0,
    }
    containers_started = 2
    tests_run = len(f2p_commands) * 2
    if not f2p_ok:
        payload.update({"status": "materialization-failed", "failure_reason": "oracle-positive-f2p-failure-or-dual-disagreement"})
    else:
        scope = source["project_test_scope"]
        collect_command = [
            "collect", "--test-root", scope["project_test_root"], "--test-framework", scope["framework"],
            "--timeout", str(collection_timeout),
        ]
        if scope["framework"] == "unittest":
            collect_command += ["--unittest-pattern", scope["unittest_pattern"], "--unittest-top-level-dir", scope["unittest_top_level_dir"]]
        collection = run_container(image_id, "collect", collect_command, collection_timeout + 120)
        containers_started += 1
        tests_run += 1
        worker = collection["worker"]
        collected = worker.get("collection", {}).get("collected_nodeids", [])
        pool = freeze_pool(collected, paths, f2p_nodeids(f2p_commands))
        payload["collection"] = collection
        payload["pool"] = pool
        payload["pool_sha256"] = sha256_bytes(json.dumps([item["nodeid"] for item in pool], ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
        if "worker_error" in worker or collection["container_exit_code"] != 0 or len(pool) < 4:
            payload.update({"status": "materialization-failed", "failure_reason": "regression-pool-collection-failure-or-insufficient-capacity"})
        else:
            nodeids = [item["nodeid"] for item in pool]
            command = ["run-nodes", "--test-framework", scope["framework"], "--timeout", str(timeout)]
            for nodeid in nodeids:
                command += ["--node", nodeid]
            pool_a, pool_b = dual_run(image_id, "reference-pool", command, timeout * (len(nodeids) + 1))
            containers_started += 2
            tests_run += len(nodeids) * 2
            checks_a = {item["nodeid"]: item for item in pool_a["worker"].get("checks", [])}
            checks_b = {item["nodeid"]: item for item in pool_b["worker"].get("checks", [])}
            stable = [
                item for item in pool
                if item["nodeid"] in checks_a
                and item["nodeid"] in checks_b
                and stable_check(checks_a[item["nodeid"]]) == stable_check(checks_b[item["nodeid"]])
                and checks_a[item["nodeid"]].get("outcome") == "passed"
            ]
            visible = [item["nodeid"] for item in stable[:3]]
            hidden = [item["nodeid"] for item in stable[3:23]]
            payload["reference_pool"] = {"run_a": pool_a, "run_b": pool_b, "stable_pass_count": len(stable)}
            payload["visible_p2p_nodeids"] = visible
            payload["hidden_regression_nodeids"] = hidden
            if len(visible) != 3 or len(hidden) < 1:
                payload.update({"status": "materialization-failed", "failure_reason": "regression-pool-dual-stability-insufficient"})
            else:
                official_patch = CONTEXT / "metadata/bug_patch.txt"
                patch_hash = sha256_bytes(official_patch.read_bytes())
                tree_hash = source["context"]["reference_validation"]["reference_tree_sha256"]
                candidate_command = [
                    "candidate-run", "--candidate-patch", "<PATCH>",
                    "--expected-patch-sha256", patch_hash,
                    "--expected-tree-sha256", tree_hash,
                    "--test-framework", scope["framework"], "--timeout", str(timeout),
                ]
                for path in paths:
                    candidate_command += ["--source-path", path]
                for command_text in f2p_commands:
                    candidate_command += ["--f2p-command", command_text]
                for nodeid in visible:
                    candidate_command += ["--visible-node", nodeid]
                for nodeid in hidden:
                    candidate_command += ["--hidden-node", nodeid]
                positive_a, positive_b = dual_run(
                    image_id, "oracle-positive", candidate_command,
                    timeout * (len(f2p_commands) + len(visible) + len(hidden) + len(paths) + 2),
                    official_patch,
                )
                containers_started += 2
                tests_run += (len(paths) + len(f2p_commands) + len(visible) + len(hidden)) * 2
                positive_ok = (
                    candidate_pass(positive_a, True)
                    and candidate_pass(positive_b, True)
                    and worker_fingerprint(positive_a["worker"]) == worker_fingerprint(positive_b["worker"])
                )
                payload["oracle_positive"] = {"run_a": positive_a, "run_b": positive_b, "dual_pass": positive_ok}
                payload["oracle_positive_tree_sha256"] = tree_hash
                payload["oracle_positive_patch_sha256"] = patch_hash
                payload.update({
                    "status": "oracle-positive-qualified-candidates-not-materialized" if positive_ok else "materialization-failed",
                    "failure_reason": None if positive_ok else "oracle-positive-full-qualification-failure-or-dual-disagreement",
                })
    payload["activity"] = {
        "real_task_checkouts": 1,
        "environment_builds": 1,
        "containers_started": containers_started,
        "project_tests_run": tests_run,
        "prompt_renders": 0,
        "api_keys_read": 0,
        "model_api_calls": 0,
    }
    payload["task_specific_repair_attempted"] = False
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    if payload["status"] == "materialization-failed":
        write_terminal(payload["failure_reason"], payload)
    return payload


def replay() -> dict[str, Any]:
    signed_amendment()
    payload = read_json(OUT)
    if payload.get("task_id") != TASK_ID or payload.get("order") != ORDER or payload.get("model_api_calls") != 0:
        raise ValueError("oracle record boundary drift")
    if payload["status"] == "materialization-failed":
        if not TERMINAL.is_file() or read_json(TERMINAL)["records"][0]["reason"] != payload["failure_reason"]:
            raise ValueError("oracle failure terminal ledger drift")
    elif payload["status"] == "oracle-positive-qualified-candidates-not-materialized":
        if len(payload["visible_p2p_nodeids"]) != 3 or not (1 <= len(payload["hidden_regression_nodeids"]) <= 20):
            raise ValueError("oracle split drift")
        if not payload["oracle_positive"]["dual_pass"]:
            raise ValueError("oracle-positive qualification drift")
    else:
        raise ValueError("unknown oracle status")
    if payload["task_specific_repair_attempted"]:
        raise ValueError("task-specific repair recorded")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--collection-timeout", type=int, default=3600)
    args = parser.parse_args()
    payload = execute(args.timeout, args.collection_timeout) if args.run else replay()
    print(json.dumps({
        "status": payload["status"],
        "failure_reason": payload.get("failure_reason"),
        "containers_started": payload["activity"]["containers_started"],
        "project_tests_run": payload["activity"]["project_tests_run"],
        "model_api_calls": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
