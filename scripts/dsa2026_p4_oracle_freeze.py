#!/usr/bin/env python3
"""Discover and freeze a pre-transform P4 regression-node pool."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "data/protocols/dsa_p4_preflight_v0_1.json"
OUT = ROOT / "data/hidden/dsa_p4_oracle_pool_registry_v0_1.json"
SEED = "dsa2026-p4-regression-split-v0_1"
GENERIC_TOKENS = {
    "py", "test", "tests", "testing", "src", "source", "lib", "main", "init"
}
FROZEN_RECORD_FIELDS = {
    "stream_role",
    "stream_order",
    "task_id",
    "project",
    "task_image",
    "task_image_id",
    "python_version",
    "selected_transform_id",
    "reference_source_paths",
    "source_tokens",
    "official_f2p_nodeids",
    "test_framework",
    "unittest_pattern",
    "unittest_top_level_dir",
    "test_root",
    "collection",
    "selection_rule",
    "pool",
    "pool_node_count",
    "pool_sha256",
    "transformed_candidate_materialized",
    "transformed_candidate_outcome_observed",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def tokens(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", value.lower())
        if len(token) >= 2 and token not in GENERIC_TOKENS
    }


def tie_hash(task_id: str, nodeid: str) -> str:
    return sha256_bytes(f"{SEED}|{task_id}|{nodeid}".encode("utf-8"))


def inspect_image(image: str) -> dict[str, Any]:
    values = json.loads(
        subprocess.check_output(
            ["docker", "image", "inspect", image],
            text=True,
            encoding="utf-8",
        )
    )
    if len(values) != 1:
        raise ValueError(f"expected one image: {image}")
    return values[0]


def discover(
    image: str,
    test_framework: str,
    test_root: str,
    unittest_pattern: str,
    unittest_top_level_dir: str,
    timeout: int,
) -> dict[str, Any]:
    result = subprocess.run(
        [
            "docker", "run", "--rm", "--network", "none", image,
            "collect", "--test-framework", test_framework,
            "--test-root", test_root,
            "--unittest-pattern", unittest_pattern,
            "--unittest-top-level-dir", unittest_top_level_dir,
            "--timeout", str(timeout),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout + 120,
    )
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError(f"collection worker returned no JSON: {result.stderr[-2000:]}")
    value = json.loads(lines[-1])
    if "worker_error" in value:
        raise RuntimeError(value)
    return value


def build_record(
    task: dict[str, Any],
    image: str,
    source_paths: list[str],
    official_f2p_nodeids: list[str],
    test_root: str,
    test_framework: str,
    unittest_pattern: str,
    unittest_top_level_dir: str,
    discovery: dict[str, Any],
) -> dict[str, Any]:
    image_data = inspect_image(image)
    collection = discovery["collection"]
    preparation = discovery["preparation"]
    source_tokens = set().union(*(tokens(path) for path in source_paths))
    official = set(official_f2p_nodeids)
    rows = []
    for nodeid in collection["collected_nodeids"]:
        if nodeid in official:
            continue
        overlap = sorted(source_tokens & tokens(nodeid))
        rows.append(
            {
                "nodeid": nodeid,
                "relatedness_score": len(overlap),
                "overlap_tokens": overlap,
                "tie_sha256": tie_hash(task["task_id"], nodeid),
            }
        )
    rows.sort(key=lambda row: (-row["relatedness_score"], row["tie_sha256"], row["nodeid"]))
    pool = rows[:40]
    pool_nodeids = [row["nodeid"] for row in pool]
    record = {
        "stream_role": task["role"],
        "stream_order": task["stream_order"],
        "task_id": task["task_id"],
        "project": task["project"],
        "status": "pretransform_pool_frozen",
        "task_image": image,
        "task_image_id": image_data["Id"],
        "python_version": task["python_version"],
        "selected_transform_id": task["selected_transform_id"],
        "reference_source_paths": source_paths,
        "source_tokens": sorted(source_tokens),
        "official_f2p_nodeids": sorted(official),
        "test_root": test_root,
        "collection": {
            "exit_code": collection["exit_code"],
            "outcome": collection["outcome"],
            "output_sha256": collection["output_sha256"],
            "collected_node_count": collection["collected_node_count"],
            "candidate_tree_sha256": preparation["candidate_tree_sha256"],
            "reference_patch_sha256": preparation["reference_patch_sha256"],
        },
        "selection_rule": {
            "tokenization": "lowercase [a-z0-9]+ tokens of length >=2",
            "discarded_generic_tokens": sorted(GENERIC_TOKENS),
            "score": "count of distinct exact tokens shared by source paths and nodeid",
            "order": "score descending, then tie SHA-256 ascending, then nodeid ascending",
            "tie_preimage": f"{SEED}|<task_id>|<nodeid>",
            "maximum_pool_nodes": 40,
            "official_f2p_excluded": True,
        },
        "pool": pool,
        "pool_node_count": len(pool),
        "pool_sha256": sha256_bytes(canonical_bytes(pool_nodeids)),
        "reference_pool_outcome_observed": False,
        "transformed_candidate_materialized": False,
        "transformed_candidate_outcome_observed": False,
    }
    if test_framework != "pytest":
        record.update(
            {
                "test_framework": test_framework,
                "unittest_pattern": unittest_pattern,
                "unittest_top_level_dir": unittest_top_level_dir,
            }
        )
    return record


def registry_with(record: dict[str, Any]) -> dict[str, Any]:
    if OUT.exists():
        registry = read_json(OUT)
        records = [item for item in registry.get("records", []) if item["task_id"] != record["task_id"]]
    else:
        records = []
    records.append(record)
    role_rank = {"primary": 0, "reserve": 1}
    records.sort(key=lambda item: (role_rank[item["stream_role"]], item["stream_order"]))
    return {
        "registry_id": "dsa_p4_oracle_pool_registry_v0_1",
        "created_date": "2026-07-11",
        "status": "pretransform_freeze_in_progress",
        "visibility": "hidden_never_model_visible",
        "records": records,
        "boundary": "Pool identities are frozen before their reference outcomes and before any transformed candidate is materialized.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--source-path", action="append", required=True)
    parser.add_argument("--official-f2p-nodeid", action="append", required=True)
    parser.add_argument("--test-root", required=True)
    parser.add_argument("--test-framework", choices=("pytest", "unittest"), default="pytest")
    parser.add_argument("--unittest-pattern", default="*_test.py")
    parser.add_argument("--unittest-top-level-dir", default=".")
    parser.add_argument("--runtime-output", required=True)
    parser.add_argument("--collection-timeout", type=int, default=1800)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    preflight = read_json(PREFLIGHT)
    task = next(item for item in preflight["tasks"] if item["task_id"] == args.task_id)
    runtime = Path(args.runtime_output).resolve()
    if args.write:
        discovery = discover(
            args.image,
            args.test_framework,
            args.test_root,
            args.unittest_pattern,
            args.unittest_top_level_dir,
            args.collection_timeout,
        )
        runtime.parent.mkdir(parents=True, exist_ok=True)
        runtime.write_text(
            json.dumps(discovery, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    else:
        discovery = read_json(runtime)
    record = build_record(
        task,
        args.image,
        args.source_path,
        args.official_f2p_nodeid,
        args.test_root,
        args.test_framework,
        args.unittest_pattern,
        args.unittest_top_level_dir,
        discovery,
    )
    existing_record = None
    if OUT.exists():
        existing_registry = read_json(OUT)
        existing_record = next(
            (item for item in existing_registry.get("records", []) if item["task_id"] == args.task_id),
            None,
        )
    if existing_record and existing_record.get("reference_pool_outcome_observed"):
        if args.write:
            raise SystemExit("refusing to overwrite a pool after reference outcomes exist")
        mismatched = [
            field for field in sorted(FROZEN_RECORD_FIELDS)
            if existing_record.get(field) != record.get(field)
        ]
        if mismatched:
            raise SystemExit(f"pre-outcome frozen fields drifted: {mismatched}")
        print(json.dumps({
            "task_id": record["task_id"],
            "pool_node_count": record["pool_node_count"],
            "pool_sha256": record["pool_sha256"],
            "task_image_id": record["task_image_id"],
            "post_outcome_frozen_fields_check": "passed",
        }, sort_keys=True))
        return
    registry = registry_with(record)
    content = json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(content, encoding="utf-8", newline="\n")
    elif not OUT.exists() or OUT.read_text(encoding="utf-8") != content:
        raise SystemExit(f"stale registry: {OUT.relative_to(ROOT)}")
    print(json.dumps({
        "task_id": record["task_id"],
        "pool_node_count": record["pool_node_count"],
        "pool_sha256": record["pool_sha256"],
        "task_image_id": record["task_image_id"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
