#!/usr/bin/env python3
"""Run a frozen P4 node pool in two fresh reference containers."""

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
POOL_REGISTRY = ROOT / "data/hidden/dsa_p4_oracle_pool_registry_v0_1.json"
RESULTS_OUT = ROOT / "data/hidden/dsa_p4_reference_pool_results_v0_1.json"


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
    return json.loads(
        subprocess.check_output(
            ["docker", *arguments],
            text=True,
            encoding="utf-8",
        )
    )


def run_fresh_container(
    task_id: str,
    run_id: str,
    image: str,
    nodeids: list[str],
    node_timeout: int,
    total_timeout: int,
) -> dict[str, Any]:
    name = f"dsa-p4-{task_id.removeprefix('bugsinpy_').replace('_', '-')}-{run_id.lower()}-{uuid.uuid4().hex[:8]}"
    command = ["run-nodes", "--timeout", str(node_timeout)]
    for nodeid in nodeids:
        command.extend(["--node", nodeid])
    container_id = subprocess.check_output(
        ["docker", "create", "--network", "none", "--name", name, image, *command],
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
        if not lines:
            raise RuntimeError(f"worker returned no JSON: {started.stderr[-2000:]}")
        worker = json.loads(lines[-1])
        if "worker_error" in worker:
            raise RuntimeError(worker)
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


def load_or_run(
    args: argparse.Namespace,
    record: dict[str, Any],
    runtime_dir: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    paths = [runtime_dir / f"{args.task_id}_reference_pool_{suffix}.json" for suffix in ("a", "b")]
    if args.write:
        nodeids = [item["nodeid"] for item in record["pool"]]
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(
                    run_fresh_container,
                    args.task_id,
                    run_id,
                    record["task_image"],
                    nodeids,
                    args.node_timeout,
                    args.total_timeout,
                )
                for run_id in ("A", "B")
            ]
            runs = [future.result() for future in futures]
        runtime_dir.mkdir(parents=True, exist_ok=True)
        for path, value in zip(paths, runs, strict=True):
            path.write_text(
                json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
                newline="\n",
            )
        return runs[0], runs[1]
    return read_json(paths[0]), read_json(paths[1])


def compact_check(check: dict[str, Any]) -> dict[str, Any]:
    return {
        "nodeid": check["nodeid"],
        "command": check["command"],
        "exit_code": check["exit_code"],
        "timed_out": check["timed_out"],
        "outcome": check["outcome"],
        "output_sha256": check["output_sha256"],
        "output_excerpt": check["output_excerpt"][-1000:],
    }


def build_result(record: dict[str, Any], run_a: dict[str, Any], run_b: dict[str, Any]) -> dict[str, Any]:
    checks_a = {item["nodeid"]: item for item in run_a["worker"]["checks"]}
    checks_b = {item["nodeid"]: item for item in run_b["worker"]["checks"]}
    pool_nodeids = [item["nodeid"] for item in record["pool"]]
    if set(checks_a) != set(pool_nodeids) or set(checks_b) != set(pool_nodeids):
        raise ValueError("worker node set does not equal frozen pool")
    rows = []
    stable = []
    for nodeid in pool_nodeids:
        a = checks_a[nodeid]
        b = checks_b[nodeid]
        outcome_consistent = (
            a["exit_code"] == b["exit_code"]
            and a["timed_out"] == b["timed_out"]
            and a["outcome"] == b["outcome"]
        )
        stable_pass = outcome_consistent and a["exit_code"] == 0 and not a["timed_out"] and a["outcome"] == "passed"
        if stable_pass:
            stable.append(nodeid)
        rows.append(
            {
                "nodeid": nodeid,
                "outcome_consistent": outcome_consistent,
                "output_hash_equal": a["output_sha256"] == b["output_sha256"],
                "stable_pass": stable_pass,
                "run_a": compact_check(a),
                "run_b": compact_check(b),
            }
        )
    tie_by_node = {item["nodeid"]: item["tie_sha256"] for item in record["pool"]}
    stable_by_tie = sorted(stable, key=lambda nodeid: (tie_by_node[nodeid], nodeid))
    visible = stable_by_tie[:3]
    hidden = stable_by_tie[3:23]
    enough = len(visible) == 3 and len(hidden) >= 1
    tree_a = run_a["worker"]["preparation"]["candidate_tree_sha256"]
    tree_b = run_b["worker"]["preparation"]["candidate_tree_sha256"]
    return {
        "task_id": record["task_id"],
        "task_image_id": record["task_image_id"],
        "pool_sha256": record["pool_sha256"],
        "run_a": {
            key: run_a[key] for key in (
                "run_id", "container_id", "created", "image_id", "network_mode", "mounts", "container_exit_code"
            )
        },
        "run_b": {
            key: run_b[key] for key in (
                "run_id", "container_id", "created", "image_id", "network_mode", "mounts", "container_exit_code"
            )
        },
        "reference_tree_hash_equal": tree_a == tree_b,
        "reference_tree_sha256": tree_a,
        "pool_node_count": len(pool_nodeids),
        "stable_pass_count": len(stable_by_tie),
        "unstable_or_failed_count": len(pool_nodeids) - len(stable_by_tie),
        "visible_p2p_nodeids": visible,
        "hidden_regression_nodeids": hidden,
        "visible_p2p_sha256": sha256_bytes(canonical_bytes(visible)),
        "hidden_regression_sha256": sha256_bytes(canonical_bytes(hidden)),
        "oracle_capacity_passed": enough,
        "checks": rows,
    }


def update_registry(registry: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    updated = json.loads(json.dumps(registry))
    record = next(item for item in updated["records"] if item["task_id"] == result["task_id"])
    record.update(
        {
            "status": "oracle_frozen_transform_not_materialized" if result["oracle_capacity_passed"] else "discard_reference_pool_insufficient",
            "reference_pool_outcome_observed": True,
            "reference_pool_result_sha256": sha256_bytes(canonical_bytes(result)),
            "stable_reference_node_count": result["stable_pass_count"],
            "visible_p2p_nodeids": result["visible_p2p_nodeids"],
            "hidden_regression_nodeids": result["hidden_regression_nodeids"],
            "visible_p2p_sha256": result["visible_p2p_sha256"],
            "hidden_regression_sha256": result["hidden_regression_sha256"],
            "oracle_capacity_passed": result["oracle_capacity_passed"],
        }
    )
    return updated


def results_registry_with(result: dict[str, Any]) -> dict[str, Any]:
    if RESULTS_OUT.exists():
        existing = read_json(RESULTS_OUT)
        records = [item for item in existing.get("records", []) if item["task_id"] != result["task_id"]]
    else:
        records = []
    records.append(result)
    records.sort(key=lambda item: item["task_id"])
    return {
        "registry_id": "dsa_p4_reference_pool_results_v0_1",
        "created_date": "2026-07-11",
        "visibility": "hidden_never_model_visible",
        "records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--runtime-dir", required=True)
    parser.add_argument("--node-timeout", type=int, default=300)
    parser.add_argument("--total-timeout", type=int, default=14400)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    original_registry = read_json(POOL_REGISTRY)
    record = next(item for item in original_registry["records"] if item["task_id"] == args.task_id)
    if record["transformed_candidate_materialized"] or record["transformed_candidate_outcome_observed"]:
        raise SystemExit("refusing reference-pool run after transformed candidate activity")
    run_a, run_b = load_or_run(args, record, Path(args.runtime_dir).resolve())
    result = build_result(record, run_a, run_b)
    updated_registry = update_registry(original_registry, result)
    results_registry = results_registry_with(result)
    outputs = {
        POOL_REGISTRY: json.dumps(updated_registry, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        RESULTS_OUT: json.dumps(results_registry, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    }
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    else:
        stale = [str(path.relative_to(ROOT)) for path, content in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            raise SystemExit(f"stale reference outputs: {stale}")
    print(json.dumps({
        "task_id": result["task_id"],
        "container_ids": [result["run_a"]["container_id"], result["run_b"]["container_id"]],
        "stable_pass_count": result["stable_pass_count"],
        "visible_p2p_count": len(result["visible_p2p_nodeids"]),
        "hidden_count": len(result["hidden_regression_nodeids"]),
        "oracle_capacity_passed": result["oracle_capacity_passed"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
