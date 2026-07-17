# ruff: noqa: E402
#!/usr/bin/env python3
"""Execute frozen-order V2-P2 candidates and write the unique order-1 terminal record."""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/dsa2026_v2_p2_run_candidates.py")

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from dsa2026_v2_p2_freeze_task_context import signed_amendment
from dsa2026_v2_p2_run_oracle import candidate_pass, dual_run, worker_fingerprint


ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "bugsinpy_pandas_161"
ORDER = 1
RESULTS_ID = "dsa_v2_p2_pandas_161_candidate_results_v0_1"
SOURCE = ROOT / "data/protocols/dsa_v2_p2_task_source_registry_v0_1.json"
ORACLE = ROOT / "data/hidden/dsa_v2_p2_pandas_161_oracle_v0_1.json"
CANDIDATES = ROOT / "data/hidden/dsa_v2_p2_pandas_161_candidate_registry_v0_1.json"
OUT = ROOT / "data/hidden/dsa_v2_p2_pandas_161_candidate_results_v0_1.json"
TERMINAL = ROOT / "data/protocols/dsa_v2_p2_terminal_ledger_v0_1.json"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def candidate_command(
    candidate: dict[str, Any],
    source: dict[str, Any],
    oracle: dict[str, Any],
    timeout: int,
) -> list[str]:
    scope = source["project_test_scope"]
    command = [
        "candidate-run", "--candidate-patch", "<PATCH>",
        "--expected-patch-sha256", candidate["patch_sha256"],
        "--expected-tree-sha256", candidate["tree_sha256"],
        "--test-framework", scope["framework"], "--timeout", str(timeout),
    ]
    for path in oracle["source_paths"]:
        command += ["--source-path", path]
    for f2p in source["source_record"]["declared_f2p_commands"]:
        command += ["--f2p-command", f2p]
    for nodeid in oracle["visible_p2p_nodeids"]:
        command += ["--visible-node", nodeid]
    for nodeid in oracle["hidden_regression_nodeids"]:
        command += ["--hidden-node", nodeid]
    return command


def terminal_record(disposition: str, reason: str, selected: dict[str, Any] | None, results: dict[str, Any]) -> dict[str, Any]:
    result_hash = sha256_bytes(json.dumps(results, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    return {
        "ledger_id": "dsa_v2_p2_terminal_ledger_v0_1",
        "created_date": "2026-07-12",
        "status": "order_1_terminal",
        "records": [{
            "order": ORDER,
            "task_id": TASK_ID,
            "disposition": disposition,
            "reason": reason,
            "selected_candidate_sha256": selected["order_sha256"] if selected else None,
            "candidate_results_sha256": result_hash,
        }],
        "qualified_pairs": 1 if disposition == "pair-qualified" else 0,
        "attempted_tasks": 1,
        "next_order": 2,
        "next_task_id": "bugsinpy_fastapi_11",
        "next_task_started": False,
        "model_api_calls": 0,
    }


def execute(timeout: int) -> dict[str, Any]:
    signed_amendment()
    if TERMINAL.is_file():
        raise PermissionError("order 1 already has a terminal disposition")
    source = read_json(SOURCE)["records"][0]
    oracle = read_json(ORACLE)
    registry = read_json(CANDIDATES)
    if oracle.get("status") != "oracle-positive-qualified-candidates-not-materialized":
        raise PermissionError("oracle-positive is not qualified")
    if registry.get("status") != "candidates-materialized-outcomes-not-observed" or registry.get("candidate_outcome_observed"):
        raise PermissionError("candidate registry is not pre-outcome frozen")
    if registry["task_image_id"] != oracle["task_image_id"]:
        raise PermissionError("candidate/oracle image drift")
    results = []
    selected = None
    per_run_checks = (
        len(oracle["source_paths"])
        + len(source["source_record"]["declared_f2p_commands"])
        + len(oracle["visible_p2p_nodeids"])
        + len(oracle["hidden_regression_nodeids"])
    )
    for candidate in registry["candidates"]:
        patch = ROOT / candidate["patch_runtime_path"]
        if not patch.is_file() or sha256_bytes(patch.read_bytes()) != candidate["patch_sha256"]:
            raise PermissionError("candidate patch runtime drift")
        command = candidate_command(candidate, source, oracle, timeout)
        run_a, run_b = dual_run(
            oracle["task_image_id"],
            f"candidate-{candidate['ordinal']:04d}",
            command,
            timeout * (per_run_checks + 2),
            patch,
        )
        qualifies = (
            candidate_pass(run_a, False)
            and candidate_pass(run_b, False)
            and worker_fingerprint(run_a["worker"]) == worker_fingerprint(run_b["worker"])
        )
        results.append({
            "ordinal": candidate["ordinal"],
            "class_id": candidate["class_id"],
            "descriptor_json": candidate["descriptor_json"],
            "order_sha256": candidate["order_sha256"],
            "patch_sha256": candidate["patch_sha256"],
            "tree_sha256": candidate["tree_sha256"],
            "run_a": run_a,
            "run_b": run_b,
            "dual_hard_negative_qualified": qualifies,
        })
        if qualifies:
            selected = candidate
            break
    payload = {
        "results_id": RESULTS_ID,
        "created_date": "2026-07-12",
        "task_id": TASK_ID,
        "order": ORDER,
        "status": "pair-qualified" if selected else "materialization-failed",
        "failure_reason": None if selected else "no-qualifying-hard-negative",
        "task_image_id": oracle["task_image_id"],
        "candidate_count_frozen": registry["candidate_count"],
        "candidate_count_executed": len(results),
        "candidate_execution_stopped_at_first_qualifying": selected is not None,
        "selected_candidate": ({
            "ordinal": selected["ordinal"],
            "class_id": selected["class_id"],
            "descriptor_json": selected["descriptor_json"],
            "order_sha256": selected["order_sha256"],
            "patch_sha256": selected["patch_sha256"],
            "tree_sha256": selected["tree_sha256"],
        } if selected else None),
        "results": results,
        "task_specific_repair_attempted": False,
        "candidate_reordered_or_repaired": False,
        "activity": {
            "real_task_checkouts": 1,
            "environment_builds": 1,
            "containers_started": oracle["activity"]["containers_started"] + 2 * len(results),
            "project_tests_run": oracle["activity"]["project_tests_run"] + 2 * per_run_checks * len(results),
            "prompt_renders": 0,
            "api_keys_read": 0,
            "model_api_calls": 0,
        },
        "model_api_calls": 0,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    ledger = terminal_record(
        "pair-qualified" if selected else "materialization-failed",
        "first-frozen-order-hard-negative-qualified" if selected else "no-qualifying-hard-negative",
        selected,
        payload,
    )
    TERMINAL.write_text(json.dumps(ledger, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return payload


def replay() -> dict[str, Any]:
    signed_amendment()
    payload = read_json(OUT)
    ledger = read_json(TERMINAL)
    terminal = ledger["records"][0]
    if payload.get("task_id") != TASK_ID or payload.get("order") != ORDER:
        raise ValueError("candidate result cursor drift")
    if payload["status"] != terminal["disposition"]:
        raise ValueError("candidate result/terminal disposition drift")
    if payload["status"] == "pair-qualified":
        if terminal["selected_candidate_sha256"] != payload["selected_candidate"]["order_sha256"]:
            raise ValueError("selected candidate hash drift")
        if not payload["results"][-1]["dual_hard_negative_qualified"]:
            raise ValueError("selected candidate does not qualify")
        if any(item["dual_hard_negative_qualified"] for item in payload["results"][:-1]):
            raise ValueError("selection skipped an earlier qualifying candidate")
    elif payload["failure_reason"] != "no-qualifying-hard-negative":
        raise ValueError("candidate failure reason drift")
    if payload["task_specific_repair_attempted"] or payload["candidate_reordered_or_repaired"] or payload["model_api_calls"] != 0:
        raise ValueError("candidate boundary drift")
    if ledger["next_task_started"] or ledger["model_api_calls"] != 0:
        raise ValueError("post-terminal boundary drift")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()
    payload = execute(args.timeout) if args.run else replay()
    print(json.dumps({
        "status": payload["status"],
        "candidate_count_executed": payload["candidate_count_executed"],
        "selected_order_sha256": payload["selected_candidate"]["order_sha256"] if payload["selected_candidate"] else None,
        "next_task_started": False,
        "model_api_calls": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
