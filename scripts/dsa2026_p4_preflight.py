#!/usr/bin/env python3
"""Freeze and verify DSA 2026 P4 structural and bootstrap inputs.

This command never materializes a candidate, executes a project test, reads a
legacy result, renders a prompt, or calls a model API.  It binds the immutable
P2/P3 inputs, the source-only transform applicability decision for all 40
frozen tasks, and the candidate-independent Docker/Conda bootstrap image.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

from unidiff import PatchSet


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/protocols/dsa_p4_preflight_v0_1.json"
SOURCE_FRAME = ROOT / "data/protocols/dsa_p2_source_frame_v0_1.json"
SOURCE_SELECTION = ROOT / "data/protocols/dsa_p2_source_selection_v0_1.json"
P3_MANIFEST = ROOT / "data/protocols/dsa_p3_hash_manifest_v0_1.json"
P3_GATE = ROOT / "data/protocols/dsa_p3_gate_audit_v0_1.json"

P2_RAW_SHA256 = {
    "data/protocols/dsa_p2_protocol_decision_v0_1.json":
        "b3443c506250196885787debb00adc612cca986f2485f63462f404f64b6c1ff2",
    "data/protocols/dsa_p2_source_selection_v0_1.json":
        "9fe40e8a38053ffdc8c965070740704924d13b9901cf0c3ed25aa4c1be14bd4b",
    "data/protocols/dsa_p2_transform_registry_v0_1.json":
        "7c2eb308378b732ca2dbe9d1f7b8dc86ba836173f0346374f576093796276430",
    "data/protocols/dsa_p2_development_exclusion_registry_v0_1.json":
        "7e8be772ac1b7fd70fcdaae1a038940916920cbf182d55fadf36717a2dcbba38",
}
P3_AGGREGATE_SHA256 = "f81ba7063297dc9264041256b99a7daa002bd730cbe1dbd9bfb105cd7aa71297"
BASE_IMAGE = "dsa2026-p4-base:conda23.3.1-r1"
BASE_REPO_DIGEST = (
    "dsa2026-p4-base@sha256:"
    "e4e42fb5e98a45ba82afd5f9d4cd2ad297bbfe912ca3954eb03f2d7b57c7fa98"
)
TOOLCHAIN_IMAGE = "dsa2026-p4-toolchains:bootstrap-v0_1"
TOOLCHAIN_IMAGE_ID = (
    "sha256:97e089cee02d0908e374f7b784ee0ffbb2fe5a2d64f619335aa962dc3ab3d768"
)
LOCKS = {
    "3.6.9": ("py369", "127d75b0d841583a2250c48b0a833de078b5ae45e0e606888f6928eb621c7a4e"),
    "3.7.0": ("py370", "2b79c03af7d1cffa7d8a91b0830da6ddc27e353f7ec482434173671824825b82"),
    "3.7.3": ("py373", "f5f36238a1b97f435d93a9ff7b23c5fa12b075fc616ee05e66bd2c6e72552fd5"),
    "3.7.7": ("py377", "8fd9517e7b4a6a22002488faa14b752e4de41bad6e37211a81ec8f67fe11adb7"),
    "3.8.1": ("py381", "df1e425eedcb0d3806b5bf10c55e369648621d93f46f5754cdc85f8435cf21f8"),
    "3.8.3": ("py383", "6a25cb9316d222d0bf8b53b516268668cb23b3bebc1cf3ede3d6d33dbc872144"),
}
TRANSFORMS = (
    ("T1_omit_secondary_source_file", "file_count", 2),
    ("T2_omit_secondary_hunk", "hunk_count", 2),
    ("T3_omit_secondary_edit_block", "edit_block_count", 2),
    ("T4_partial_multiline_reversion", "changed_line_count", 3),
)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_text(path: Path) -> bytes:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def canonical_sha256(path: Path) -> str:
    return sha256_bytes(canonical_text(path))


def git_head(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        text=True,
        encoding="utf-8",
    ).strip()


def docker_inspect(image: str) -> dict[str, Any]:
    output = subprocess.check_output(
        ["docker", "image", "inspect", image],
        text=True,
        encoding="utf-8",
    )
    values = json.loads(output)
    if len(values) != 1:
        raise ValueError(f"expected one Docker image: {image}")
    return values[0]


def is_test_path(path: str) -> bool:
    parts = [part.lower() for part in PurePosixPath(path).parts]
    name = parts[-1] if parts else ""
    return (
        any(part in {"test", "tests", "testing"} for part in parts[:-1])
        or name.startswith(("test_", "tests_"))
        or name.endswith(("_test.py", "_tests.py"))
    )


def source_diff_shape(patch_text: str) -> tuple[dict[str, int], list[str], list[str]]:
    patch = PatchSet(patch_text.splitlines(keepends=True))
    source_files = [item for item in patch if not is_test_path(item.path)]
    test_files = [item.path for item in patch if is_test_path(item.path)]
    hunk_count = 0
    edit_block_count = 0
    changed_line_count = 0
    for item in source_files:
        hunk_count += len(item)
        for hunk in item:
            in_edit = False
            for line in hunk:
                changed = bool(line.is_added or line.is_removed)
                if changed:
                    changed_line_count += 1
                    if not in_edit:
                        edit_block_count += 1
                        in_edit = True
                else:
                    in_edit = False
    return (
        {
            "file_count": len(source_files),
            "hunk_count": hunk_count,
            "edit_block_count": edit_block_count,
            "changed_line_count": changed_line_count,
        },
        sorted(item.path for item in source_files),
        sorted(test_files),
    )


def first_applicable_transform(shape: dict[str, int]) -> str | None:
    for transform_id, field, minimum in TRANSFORMS:
        if shape[field] >= minimum:
            return transform_id
    return None


def normalized_command_lines(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").replace("\r", "").splitlines() if line.strip()]


def p3_manifest_audit() -> dict[str, Any]:
    manifest = read_json(P3_MANIFEST)
    records: list[dict[str, Any]] = []
    for expected in manifest["files"]:
        path = ROOT / expected["path"]
        actual_hash = canonical_sha256(path)
        actual_size = len(canonical_text(path))
        records.append(
            {
                "path": expected["path"],
                "expected_sha256": expected["sha256"],
                "actual_sha256": actual_hash,
                "expected_canonical_utf8_bytes": expected["canonical_utf8_bytes"],
                "actual_canonical_utf8_bytes": actual_size,
                "passed": actual_hash == expected["sha256"] and actual_size == expected["canonical_utf8_bytes"],
            }
        )
    aggregate_input = b"".join(
        f"{record['path']}\0{record['actual_sha256']}\n".encode("utf-8") for record in records
    )
    actual_aggregate = sha256_bytes(aggregate_input)
    return {
        "manifest_status": manifest.get("status"),
        "immutable": manifest.get("immutable"),
        "file_count": len(records),
        "aggregate_expected": P3_AGGREGATE_SHA256,
        "aggregate_actual": actual_aggregate,
        "files_all_passed": all(record["passed"] for record in records),
        "records": records,
    }


def task_record(
    item: dict[str, Any],
    role: str,
    catalog: Path,
    source_by_task: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    source = source_by_task[item["task_id"]]
    bug_dir = catalog / "projects" / item["project"] / "bugs" / str(item["bug_id"])
    required = {
        "bug_info": bug_dir / "bug.info",
        "reference_patch": bug_dir / "bug_patch.txt",
        "requirements": bug_dir / "requirements.txt",
        "run_test": bug_dir / "run_test.sh",
    }
    missing = [name for name, path in required.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"{item['task_id']} missing metadata: {missing}")
    setup = bug_dir / "setup.sh"
    patch_text = required["reference_patch"].read_text(encoding="utf-8", errors="strict")
    shape, source_paths, excluded_test_paths = source_diff_shape(patch_text)
    transform_id = first_applicable_transform(shape)
    declared_commands = list(source["declared_f2p_commands"])
    catalog_commands = normalized_command_lines(required["run_test"])
    return {
        "stream_order": item["order"],
        "role": role,
        "task_id": item["task_id"],
        "project": item["project"],
        "bug_id": item["bug_id"],
        "python_version": item["python_version"],
        "buggy_commit_id": source["buggy_commit_id"],
        "fixed_commit_id": source["fixed_commit_id"],
        "declared_test_file": source["declared_test_file"],
        "declared_f2p_commands": declared_commands,
        "catalog_f2p_commands": catalog_commands,
        "f2p_command_match": declared_commands == catalog_commands,
        "metadata_sha256": {
            name: sha256_file(path) for name, path in sorted(required.items())
        } | ({"setup": sha256_file(setup)} if setup.is_file() else {}),
        "reference_source_paths": source_paths,
        "reference_test_paths_excluded_from_transform": excluded_test_paths,
        "source_diff_shape": shape,
        "selected_transform_id": transform_id,
        "structural_disposition": "eligible_for_candidate_materialization" if transform_id else "discard_no_applicable_transform",
        "candidate_materialized": False,
        "candidate_hidden_result_observed": False,
    }


def build(catalog: Path) -> dict[str, Any]:
    source_frame = read_json(SOURCE_FRAME)
    selection = read_json(SOURCE_SELECTION)["regular"]
    source_by_task = {record["task_id"]: record for record in source_frame["records"]}
    p3 = p3_manifest_audit()
    p3_gate = read_json(P3_GATE)
    p2_hashes = {
        path: {"expected": expected, "actual": sha256_file(ROOT / path)}
        for path, expected in P2_RAW_SHA256.items()
    }
    records = [
        task_record(item, role, catalog, source_by_task)
        for role in ("primary", "reserve")
        for item in selection[role]
    ]
    transform_counts = Counter(
        record["selected_transform_id"] or "NONE" for record in records
    )
    lock_records = []
    for version, (environment_name, expected_hash) in LOCKS.items():
        path = ROOT / "data/environment_locks/dsa2026_p4_bootstrap" / f"{environment_name}-linux-64.txt"
        text = path.read_text(encoding="utf-8")
        lock_records.append(
            {
                "python_version": version,
                "environment_name": environment_name,
                "path": path.relative_to(ROOT).as_posix(),
                "expected_sha256": expected_hash,
                "actual_sha256": sha256_file(path),
                "explicit": "@EXPLICIT" in text,
                "only_frozen_https_mirror": all(
                    not line.startswith("http")
                    or line.startswith("https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/")
                    for line in text.splitlines()
                ),
            }
        )
    base = docker_inspect(BASE_IMAGE)
    toolchain = docker_inspect(TOOLCHAIN_IMAGE)
    checks = {
        "p2_raw_hashes_unchanged": all(value["actual"] == value["expected"] for value in p2_hashes.values()),
        "p3_gate_pass": p3_gate.get("gate_status") == "PASS",
        "p3_manifest_immutable_author_signed": p3["manifest_status"] == "immutable_author_signed" and p3["immutable"] is True,
        "p3_manifest_16_files": p3["file_count"] == 16,
        "p3_manifest_files_unchanged": p3["files_all_passed"],
        "p3_manifest_aggregate_unchanged": p3["aggregate_actual"] == p3["aggregate_expected"],
        "official_catalog_commit_unchanged": git_head(catalog) == source_frame["official_source"]["catalog_commit"],
        "regular_order_30_primary_10_reserve": len(selection["primary"]) == 30 and len(selection["reserve"]) == 10,
        "all_f2p_commands_match_catalog": all(record["f2p_command_match"] for record in records),
        "all_task_metadata_hashed": all(len(record["metadata_sha256"]) >= 4 for record in records),
        "transform_structure_frozen_before_candidates": all(not record["candidate_materialized"] for record in records),
        "structural_capacity_at_least_30": sum(record["selected_transform_id"] is not None for record in records) >= 30,
        "bootstrap_locks_complete": len(lock_records) == 6,
        "bootstrap_locks_hash_match": all(record["actual_sha256"] == record["expected_sha256"] for record in lock_records),
        "bootstrap_locks_explicit_https_only": all(record["explicit"] and record["only_frozen_https_mirror"] for record in lock_records),
        "base_image_digest_match": BASE_REPO_DIGEST in (base.get("RepoDigests") or []),
        "toolchain_image_id_match": toolchain.get("Id") == TOOLCHAIN_IMAGE_ID,
        "no_model_api_call": True,
        "p5_not_entered": True,
        "no_rendered_prompt_generated": True,
        "no_legacy_candidate_or_result_read": True,
    }
    return {
        "preflight_id": "dsa_p4_preflight_v0_1",
        "created_date": "2026-07-11",
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "p2_raw_sha256": p2_hashes,
        "p3_manifest_audit": p3,
        "reference_boundary": {
            "authoritative_patch": "official BugsInPy bug_patch.txt applied to the declared buggy commit",
            "authoritative_f2p": "official run_test.sh, byte-bound to P2 source-frame declared command(s)",
            "test_path_predicate": "exclude path components test/tests/testing and Python basenames test_*, tests_*, *_test.py, *_tests.py from transform application",
            "test_file_edits_are_never_candidate_edits": True,
            "transform_selection": "first structurally applicable P2 transform over source-only reference diff shape; no outcome-dependent fallback",
        },
        "timeouts_and_pass_rules": {
            "dependency_image_build_seconds": 3600,
            "test_collection_seconds": 1800,
            "individual_f2p_or_regression_node_seconds": 300,
            "command_pass": "exit code 0 with framework summary showing the selected node(s) passed and no failure/error",
            "dual_environment_consistency": "same normalized outcome and exit code in two fresh containers from one locked task-image digest",
        },
        "environment_bootstrap": {
            "base_image": BASE_IMAGE,
            "base_repo_digest": BASE_REPO_DIGEST,
            "toolchain_image": TOOLCHAIN_IMAGE,
            "toolchain_image_id": TOOLCHAIN_IMAGE_ID,
            "conda_channel": "https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main",
            "pip_index": "https://pypi.tuna.tsinghua.edu.cn/simple",
            "ssl_verification": True,
            "bootstrap_packages": {
                "pip": "20.1.1",
                "setuptools": "47.1.1",
                "wheel": "0.34.2",
                "pytest": "5.4.3",
                "packaging": "20.4",
            },
            "locks": lock_records,
            "candidate_source_or_outcome_in_image": False,
        },
        "structural_summary": {
            "primary_count": len(selection["primary"]),
            "reserve_count": len(selection["reserve"]),
            "structurally_eligible_count": sum(record["selected_transform_id"] is not None for record in records),
            "structural_discard_count": sum(record["selected_transform_id"] is None for record in records),
            "remaining_nonstructural_discard_budget": sum(record["selected_transform_id"] is not None for record in records) - 30,
            "transform_counts": dict(sorted(transform_counts.items())),
        },
        "tasks": records,
        "boundary": "P4 preflight only: no candidate, hidden outcome, model-visible packet, rendered prompt, P5 artifact, paper metric, or model API call was produced.",
    }


def serialize(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog-root", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build(Path(args.catalog_root).resolve())
    content = serialize(value)
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(content, encoding="utf-8", newline="\n")
    elif not OUT.exists() or OUT.read_text(encoding="utf-8") != content:
        raise SystemExit(f"stale or missing output: {OUT.relative_to(ROOT)}")
    if value["status"] != "passed":
        failed = [name for name, passed in value["checks"].items() if not passed]
        raise SystemExit(f"P4 preflight failed: {failed}")
    print(json.dumps({"status": value["status"], **value["structural_summary"]}, sort_keys=True))


if __name__ == "__main__":
    main()
