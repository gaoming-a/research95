#!/usr/bin/env python3
"""Freeze one authorized V2-P2 task context from official commit archives."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from dsa2026_p4_prepare_task_context import (
    apply_reference,
    copy_fixed_tests,
    copy_metadata,
    extract_commit_archive,
    tree_sha256,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ORDER = ROOT / "data/protocols/dsa_v2_p1_source_order_v0_1.json"
AMENDMENT = ROOT / "data/protocols/dsa_v2_p1_test_scope_amendment_v0_1.json"
OUT = ROOT / "data/protocols/dsa_v2_p2_task_source_registry_v0_1.json"
CONTEXT_ROOT = (ROOT / "tmp/dsa2026_v2_p2_runtime/task_contexts").resolve()
TASK_ID = "bugsinpy_pandas_161"
SOURCE_REPOSITORY = "https://github.com/pandas-dev/pandas"
EXPECTED_AMENDMENTS_SHA256 = "b5778a7c95042d5475d333842c5b8a486a2798a7586d74a20a84e30487ddef94"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def signed_amendment() -> dict[str, Any]:
    if not AMENDMENT.is_file():
        raise PermissionError("author-signed V2-P1 test-scope amendment is absent")
    amendment = read_json(AMENDMENT)
    if amendment.get("status") != "author_signed_immutable":
        raise PermissionError("V2-P1 test-scope amendment is not author-signed immutable")
    if amendment.get("amendments_sha256") != EXPECTED_AMENDMENTS_SHA256:
        raise PermissionError("V2-P1 test-scope amendment hash drift")
    authorization = amendment.get("authorization", {})
    if authorization.get("real_v2_p2_order_1") is not True:
        raise PermissionError("signed amendment does not authorize V2-P2 order 1")
    if any(authorization.get(name) is True for name in ("real_v2_p2_order_2", "v2_p3", "prompt", "model_api")):
        raise PermissionError("signed amendment contains forbidden expanded authorization")
    return amendment


def task_record() -> dict[str, Any]:
    source = read_json(SOURCE_ORDER)
    records = [item for item in source["records"] if item["task_id"] == TASK_ID]
    if len(records) != 1 or records[0]["order"] != 1:
        raise ValueError("unique V2-P2 order-1 task drift")
    return records[0]


def build_registry(record: dict[str, Any], amendment: dict[str, Any]) -> dict[str, Any]:
    scoped = next(item for item in amendment["amendments"] if item["project"] == record["project"])
    value = {
        "task_id": TASK_ID,
        "order": 1,
        "status": "source_context_frozen_no_environment_outcome",
        "v2_p1_test_scope_amendments_sha256": amendment["amendments_sha256"],
        "project_test_scope": scoped,
        "source_record": record,
        "real_activity": {
            "real_task_checkouts": 1,
            "environment_builds": 0,
            "containers_started": 0,
            "project_tests_run": 0,
            "prompt_renders": 0,
            "api_keys_read": 0,
            "model_api_calls": 0,
        },
        "boundary": "Official archives and fixed tests are frozen; no environment, container, project test, candidate outcome, prompt, credential, or model request has started.",
    }
    value["record_sha256"] = hashlib.sha256(canonical_bytes(value)).hexdigest()
    return {
        "registry_id": "dsa_v2_p2_task_source_registry_v0_1",
        "created_date": "2026-07-12",
        "status": "order_1_source_frozen",
        "records": [value],
        "model_api_calls": 0,
    }


def build_context(
    task: dict[str, Any],
    buggy_archive: Path,
    fixed_archive: Path,
    catalog_root: Path,
    temporary_root: Path,
    archive_extractor=extract_commit_archive,
) -> tuple[Path, dict[str, Any]]:
    context = temporary_root / TASK_ID
    buggy_source = context / "buggy_source"
    fixed_source = temporary_root / "fixed_source"
    buggy_archive_record = archive_extractor(
        buggy_archive, buggy_source, f"{task['project']}-{task['buggy_commit_id']}"
    )
    fixed_archive_record = archive_extractor(
        fixed_archive, fixed_source, f"{task['project']}-{task['fixed_commit_id']}"
    )
    fixed_test_hashes = copy_fixed_tests(
        fixed_source, task["declared_test_file"], context / "fixed_tests"
    )
    metadata_task = dict(task)
    metadata_task["metadata_sha256"] = dict(task["metadata_sha256"])
    metadata_task["metadata_sha256"]["setup"] = task["metadata_sha256"][
        "setup_provenance_only"
    ]
    metadata_hashes = copy_metadata(
        catalog_root, metadata_task, context / "metadata"
    )
    reference = apply_reference(context)
    value = {
        "task_id": TASK_ID,
        "project": task["project"],
        "order": task["order"],
        "status": "v2_p2_source_context_frozen_no_candidate",
        "source_repository": SOURCE_REPOSITORY,
        "source_acquisition": "official GitHub codeload commit tarballs",
        "buggy_commit_id": task["buggy_commit_id"],
        "fixed_commit_id": task["fixed_commit_id"],
        "buggy_archive": buggy_archive_record,
        "fixed_archive": fixed_archive_record,
        "buggy_source_tree_sha256": tree_sha256(buggy_source),
        "fixed_test_sha256": fixed_test_hashes,
        "metadata_sha256": metadata_hashes,
        "reference_validation": reference,
        "context_tree_sha256": tree_sha256(context),
        "candidate_materialized": False,
        "candidate_outcome_observed": False,
        "model_api_calls": 0,
    }
    value["record_sha256"] = hashlib.sha256(canonical_bytes(value)).hexdigest()
    return context, value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog-root")
    parser.add_argument("--buggy-archive")
    parser.add_argument("--fixed-archive")
    parser.add_argument("--preflight", action="store_true")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    record = task_record()
    if args.preflight:
        print(json.dumps({
            "status": "ready" if AMENDMENT.is_file() else "author_signoff_required",
            "task_id": record["task_id"],
            "order": record["order"],
            "real_activity": 0,
            "model_api_calls": 0,
        }, sort_keys=True))
        return
    if not (args.write or args.check):
        parser.error("one of --preflight, --write, or --check is required")
    if not all((args.catalog_root, args.buggy_archive, args.fixed_archive)):
        parser.error("archive and catalog arguments are required for write/check")
    amendment = signed_amendment()
    target = CONTEXT_ROOT / TASK_ID
    with tempfile.TemporaryDirectory(prefix="dsa_v2_p2_context_") as raw:
        generated, p4_record = build_context(
            record,
            Path(args.buggy_archive).resolve(),
            Path(args.fixed_archive).resolve(),
            Path(args.catalog_root).resolve(),
            Path(raw),
        )
        registry = build_registry(record, amendment)
        registry["records"][0]["context"] = p4_record
        registry["records"][0]["context"]["status"] = "v2_p2_source_context_frozen_no_candidate"
        registry["records"][0]["context"]["record_sha256"] = hashlib.sha256(
            canonical_bytes({
                key: value
                for key, value in registry["records"][0]["context"].items()
                if key != "record_sha256"
            })
        ).hexdigest()
        registry["records"][0]["record_sha256"] = hashlib.sha256(
            canonical_bytes({k: v for k, v in registry["records"][0].items() if k != "record_sha256"})
        ).hexdigest()
        content = json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if args.write:
            if target.exists():
                shutil.rmtree(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(generated, target)
            OUT.write_text(content, encoding="utf-8", newline="\n")
        else:
            stale = []
            if not target.is_dir() or tree_sha256(target) != p4_record["context_tree_sha256"]:
                stale.append(str(target))
            if not OUT.is_file() or OUT.read_text(encoding="utf-8") != content:
                stale.append(str(OUT))
            if stale:
                raise SystemExit(f"stale V2-P2 source context: {stale}")
    print(json.dumps({
        "status": "passed",
        "task_id": TASK_ID,
        "order": 1,
        "context_tree_sha256": p4_record["context_tree_sha256"],
        "environment_builds": 0,
        "model_api_calls": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
