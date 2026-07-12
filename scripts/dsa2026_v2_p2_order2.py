#!/usr/bin/env python3
"""Execute/replay the frozen V2-P2 order-2 FastAPI task in bounded phases."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import dsa2026_v2_p2_freeze_task_context as source_lib
import dsa2026_v2_p2_materialize_candidates as materializer
import dsa2026_v2_p2_run_candidates as candidate_runner
import dsa2026_v2_p2_run_oracle as oracle_runner


ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "bugsinpy_fastapi_11"
ORDER = 2
NEXT_TASK = "bugsinpy_black_4"
REPOSITORY = "https://github.com/tiangolo/fastapi"
IMAGE = f"dsa2026-v2-p2-task:{TASK_ID}"
SOURCE_ORDER = ROOT / "data/protocols/dsa_v2_p1_source_order_v0_1.json"
PREVIOUS_LEDGER = ROOT / "data/protocols/dsa_v2_p2_terminal_ledger_v0_1.json"
SOURCE_OUT = ROOT / "data/protocols/dsa_v2_p2_order2_task_source_registry_v0_1.json"
ENV_OUT = ROOT / "data/protocols/dsa_v2_p2_fastapi_11_environment_v0_1.json"
ORACLE_OUT = ROOT / "data/hidden/dsa_v2_p2_fastapi_11_oracle_v0_1.json"
CANDIDATE_REGISTRY = ROOT / "data/hidden/dsa_v2_p2_fastapi_11_candidate_registry_v0_1.json"
CANDIDATE_RESULTS = ROOT / "data/hidden/dsa_v2_p2_fastapi_11_candidate_results_v0_1.json"
TERMINAL_DRAFT = ROOT / "data/protocols/dsa_v2_p2_order2_terminal_draft_v0_1.json"
CONTEXT = ROOT / f"tmp/dsa2026_v2_p2_runtime/task_contexts/{TASK_ID}"
RUNTIME = ROOT / "tmp/dsa2026_v2_p2_runtime/order2"
PATCH_ROOT = ROOT / f"tmp/dsa2026_v2_p2_runtime/candidates/{TASK_ID}"
DOCKERFILE = ROOT / "containers/dsa2026_v2_p2/Dockerfile.order2"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")).hexdigest()


def task_record() -> dict[str, Any]:
    records = read_json(SOURCE_ORDER)["records"]
    record = records[ORDER - 1]
    if record["order"] != ORDER or record["task_id"] != TASK_ID:
        raise ValueError("frozen order-2 cursor drift")
    ledger = read_json(PREVIOUS_LEDGER)
    if len(ledger["records"]) != 1 or ledger["next_order"] != ORDER or ledger["next_task_id"] != TASK_ID or ledger["next_task_started"]:
        raise PermissionError("order-1 terminal does not authorize unique order-2 cursor")
    return record


def terminal_draft(disposition: str, reason: str, selected: str | None, evidence_field: str, evidence_sha: str) -> dict[str, Any]:
    return {
        "draft_id": "dsa_v2_p2_order2_terminal_draft_v0_1",
        "created_date": "2026-07-12",
        "records": [{
            "order": ORDER,
            "task_id": TASK_ID,
            "disposition": disposition,
            "reason": reason,
            "selected_candidate_sha256": selected,
            evidence_field: evidence_sha,
        }],
        "next_order": 3,
        "next_task_id": NEXT_TASK,
        "next_task_started": False,
        "model_api_calls": 0,
    }


def freeze_source(args: argparse.Namespace) -> dict[str, Any]:
    amendment = source_lib.signed_amendment()
    record = task_record()
    context_input = dict(record)
    context_input["metadata_sha256"] = dict(record["metadata_sha256"])
    context_input["metadata_sha256"].setdefault("setup_provenance_only", "")
    source_lib.TASK_ID = TASK_ID
    source_lib.SOURCE_REPOSITORY = REPOSITORY
    with tempfile.TemporaryDirectory(prefix="dsa_v2_p2_order2_source_") as raw:
        generated, context_record = source_lib.build_context(
            context_input,
            Path(args.buggy_archive).resolve(),
            Path(args.fixed_archive).resolve(),
            Path(args.catalog_root).resolve(),
            Path(raw),
        )
        scope = next(item for item in amendment["amendments"] if item["project"] == "fastapi")
        value = {
            "registry_id": "dsa_v2_p2_order2_task_source_registry_v0_1",
            "created_date": "2026-07-12",
            "status": "order_2_source_frozen",
            "previous_terminal_ledger_sha256": canonical_sha(read_json(PREVIOUS_LEDGER)),
            "records": [{
                "task_id": TASK_ID,
                "order": ORDER,
                "status": "source_context_frozen_no_environment_outcome",
                "project_test_scope": scope,
                "source_record": record,
                "context": context_record,
                "real_activity": {"real_task_checkouts": 1, "environment_builds": 0, "containers_started": 0, "project_tests_run": 0, "prompt_renders": 0, "api_keys_read": 0, "model_api_calls": 0},
            }],
            "model_api_calls": 0,
        }
        value["records"][0]["record_sha256"] = canonical_sha(value["records"][0])
        content = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if args.write:
            if CONTEXT.exists():
                shutil.rmtree(CONTEXT)
            CONTEXT.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(generated, CONTEXT)
            SOURCE_OUT.write_text(content, encoding="utf-8", newline="\n")
        elif not SOURCE_OUT.is_file() or SOURCE_OUT.read_text(encoding="utf-8") != content or source_lib.tree_sha256(CONTEXT) != context_record["context_tree_sha256"]:
            raise SystemExit("stale order-2 source context")
    return value


def build_image(timeout: int) -> dict[str, Any]:
    source_lib.signed_amendment()
    task_record()
    source = read_json(SOURCE_OUT)["records"][0]
    if source_lib.tree_sha256(CONTEXT) != source["context"]["context_tree_sha256"]:
        raise PermissionError("order-2 context drift")
    RUNTIME.mkdir(parents=True, exist_ok=True)
    command = ["docker", "build", "--progress", "plain", "--no-cache", "-f", str(DOCKERFILE), "-t", IMAGE, str(ROOT)]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=timeout)
    output = result.stdout + result.stderr
    (RUNTIME / "docker_build.log").write_bytes(output)
    image = None
    if result.returncode == 0:
        inspected = json.loads(subprocess.check_output(["docker", "image", "inspect", IMAGE], text=True, encoding="utf-8"))[0]
        image = {"image": IMAGE, "image_id": inspected["Id"], "labels": inspected["Config"].get("Labels", {})}
        expected = {"dsa2026.v2_p2.task_id": TASK_ID, "dsa2026.v2_p2.order": "2", "dsa2026.v2_p2.model_api_called": "false", "dsa2026.v2_p2.official_setup_executed": "false"}
        if not all(image["labels"].get(key) == value for key, value in expected.items()):
            raise RuntimeError("order-2 image label drift")
    payload = {
        "environment_id": "dsa_v2_p2_fastapi_11_environment_v0_1",
        "created_date": "2026-07-12", "task_id": TASK_ID, "order": ORDER,
        "status": "environment-built-oracle-not-started" if result.returncode == 0 else "materialization-failed",
        "failure_reason": None if result.returncode == 0 else "environment-build-failure",
        "source_record_sha256": source["record_sha256"], "build_exit_code": result.returncode,
        "build_output_sha256": hashlib.sha256(output).hexdigest(), "build_output_bytes": len(output),
        "dockerfile_sha256": hashlib.sha256(DOCKERFILE.read_bytes()).hexdigest(), "image": image,
        "official_setup_executed": False, "task_specific_repair_attempted": False,
        "activity": {"real_task_checkouts": 1, "environment_builds": 1, "containers_started": 0, "project_tests_run": 0, "prompt_renders": 0, "api_keys_read": 0, "model_api_calls": 0},
    }
    ENV_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    if result.returncode != 0:
        draft = terminal_draft("materialization-failed", "environment-build-failure", None, "environment_record_sha256", canonical_sha(payload))
        TERMINAL_DRAFT.write_text(json.dumps(draft, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return payload


def configure_oracle() -> None:
    oracle_runner.TASK_ID = TASK_ID
    oracle_runner.ENVIRONMENT = ENV_OUT
    oracle_runner.SOURCE = SOURCE_OUT
    oracle_runner.CONTEXT = CONTEXT
    oracle_runner.RUNTIME = RUNTIME / "oracle"
    oracle_runner.OUT = ORACLE_OUT
    oracle_runner.TERMINAL = TERMINAL_DRAFT

    def write_terminal(reason: str, oracle: dict[str, Any]) -> None:
        draft = terminal_draft("materialization-failed", reason, None, "oracle_record_sha256", canonical_sha(oracle))
        TERMINAL_DRAFT.write_text(json.dumps(draft, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    oracle_runner.write_terminal = write_terminal


def run_oracle(timeout: int, collection_timeout: int) -> dict[str, Any]:
    configure_oracle()
    return oracle_runner.execute(timeout, collection_timeout)


def materialize(write: bool) -> dict[str, Any]:
    materializer.TASK_ID = TASK_ID
    materializer.CONTEXT = CONTEXT
    materializer.ORACLE = ORACLE_OUT
    materializer.OUT = CANDIDATE_REGISTRY
    materializer.PATCH_ROOT = PATCH_ROOT
    oracle = read_json(ORACLE_OUT)
    with tempfile.TemporaryDirectory(prefix="dsa_v2_p2_order2_candidates_") as raw:
        registry, generated = materializer.build_registry(CONTEXT, oracle, Path(raw) / TASK_ID)
        content = json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if write:
            if PATCH_ROOT.exists():
                shutil.rmtree(PATCH_ROOT)
            PATCH_ROOT.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(generated, PATCH_ROOT)
            CANDIDATE_REGISTRY.write_text(content, encoding="utf-8", newline="\n")
        elif not CANDIDATE_REGISTRY.is_file() or CANDIDATE_REGISTRY.read_text(encoding="utf-8") != content:
            raise SystemExit("stale order-2 candidate registry")
    return registry


def configure_candidates() -> None:
    candidate_runner.TASK_ID = TASK_ID
    candidate_runner.SOURCE = SOURCE_OUT
    candidate_runner.ORACLE = ORACLE_OUT
    candidate_runner.CANDIDATES = CANDIDATE_REGISTRY
    candidate_runner.OUT = CANDIDATE_RESULTS
    candidate_runner.TERMINAL = TERMINAL_DRAFT

    def terminal_record(disposition: str, reason: str, selected: dict[str, Any] | None, results: dict[str, Any]) -> dict[str, Any]:
        return terminal_draft(disposition, reason, selected["order_sha256"] if selected else None, "candidate_results_sha256", canonical_sha(results))
    candidate_runner.terminal_record = terminal_record


def run_candidates(timeout: int) -> dict[str, Any]:
    configure_candidates()
    return candidate_runner.execute(timeout)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("source", "build", "oracle", "materialize", "candidates"))
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--catalog-root")
    parser.add_argument("--buggy-archive")
    parser.add_argument("--fixed-archive")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--collection-timeout", type=int, default=3600)
    args = parser.parse_args()
    if args.phase == "source":
        if not all((args.catalog_root, args.buggy_archive, args.fixed_archive)) or args.write == args.check:
            parser.error("source requires archive/catalog args and exactly one of --write/--check")
        value = freeze_source(args)
    elif args.phase == "build":
        if not args.write:
            parser.error("build requires --write")
        value = build_image(max(args.timeout, 7200))
    elif args.phase == "oracle":
        if not args.write:
            parser.error("oracle requires --write")
        value = run_oracle(args.timeout, args.collection_timeout)
    elif args.phase == "materialize":
        if args.write == args.check:
            parser.error("materialize requires exactly one of --write/--check")
        value = materialize(args.write)
    else:
        if not args.write:
            parser.error("candidates requires --write")
        value = run_candidates(args.timeout)
    print(json.dumps({"phase": args.phase, "status": value["status"], "task_id": TASK_ID, "order": ORDER, "model_api_calls": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
