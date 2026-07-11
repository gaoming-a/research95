#!/usr/bin/env python3
"""Materialize one frozen P4 candidate pair before observing candidate outcomes."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

from unidiff import PatchSet


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "data/protocols/dsa_p4_preflight_v0_1.json"
ORACLE_REGISTRY = ROOT / "data/hidden/dsa_p4_oracle_pool_registry_v0_1.json"
CANDIDATE_REGISTRY = ROOT / "data/hidden/dsa_p4_candidate_registry_v0_1.json"
SKIP_NAMES = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", "build", "dist"}
T4_ID = "T4_partial_multiline_reversion"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root)
        if any(part in SKIP_NAMES for part in relative.parts) or not path.is_file():
            continue
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).hexdigest().encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def is_test_path(path: str) -> bool:
    parts = [part.lower() for part in PurePosixPath(path).parts]
    name = parts[-1] if parts else ""
    return (
        any(part in {"test", "tests", "testing"} for part in parts[:-1])
        or name.startswith(("test_", "tests_"))
        or name.endswith(("_test.py", "_tests.py"))
    )


def copy_baseline(task_context: Path, destination: Path) -> None:
    shutil.copytree(task_context / "buggy_source", destination)
    fixed_root = task_context / "fixed_tests"
    for source in sorted(fixed_root.rglob("*")):
        if source.is_file():
            target = destination / source.relative_to(fixed_root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def apply_patch(workspace: Path, patch_path: Path) -> None:
    checked = subprocess.run(
        ["git", "apply", "--check", str(patch_path)],
        cwd=workspace,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if checked.returncode != 0:
        raise RuntimeError(f"patch check failed: {checked.stderr[-2000:]}")
    applied = subprocess.run(
        ["git", "apply", str(patch_path)],
        cwd=workspace,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if applied.returncode != 0:
        raise RuntimeError(f"patch apply failed: {applied.stderr[-2000:]}")


def t4_edit_rows(patch_text: str) -> list[dict[str, Any]]:
    patch = PatchSet(patch_text.splitlines(keepends=True))
    rows: list[dict[str, Any]] = []
    for patched_file in patch:
        if is_test_path(patched_file.path):
            continue
        for hunk_index, hunk in enumerate(patched_file):
            target_index = hunk.target_start - 1
            for line_index, line in enumerate(hunk):
                if line.is_context:
                    target_index += 1
                    continue
                kind = "added" if line.is_added else "removed"
                identity = {
                    "path": patched_file.path,
                    "hunk_index": hunk_index,
                    "line_index": line_index,
                    "kind": kind,
                    "value": line.value.replace("\r\n", "\n").replace("\r", "\n"),
                }
                rows.append(
                    {
                        **identity,
                        "target_index": target_index,
                        "identity_sha256": sha256_bytes(canonical_bytes(identity)),
                    }
                )
                if line.is_added:
                    target_index += 1
    rows.sort(key=lambda item: (item["identity_sha256"], canonical_bytes(item)))
    return rows


def read_lines_exact(path: Path) -> list[str]:
    return path.read_bytes().decode("utf-8").splitlines(keepends=True)


def write_text_exact(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value.encode("utf-8"))


def unified_diff_for_paths(
    baseline: Path,
    candidate: Path,
    source_paths: list[str],
) -> str:
    chunks: list[str] = []
    for relative in sorted(source_paths):
        before = read_lines_exact(baseline / relative)
        after = read_lines_exact(candidate / relative)
        chunks.extend(
            difflib.unified_diff(
                before,
                after,
                fromfile=f"a/{relative}",
                tofile=f"b/{relative}",
                n=3,
                lineterm="\n",
            )
        )
    return "".join(chunks)


def normalized_patch(patch_text: str, path_map: dict[str, str]) -> str:
    result = patch_text.replace("\r\n", "\n").replace("\r", "\n")
    for source, target in sorted(path_map.items(), key=lambda item: -len(item[0])):
        result = result.replace(f"a/{source}", f"a/{target}")
        result = result.replace(f"b/{source}", f"b/{target}")
    return result


def context_range(patch_text: str, path: str, line_count: int) -> tuple[int, int]:
    patched_file = next(item for item in PatchSet(patch_text.splitlines(keepends=True)) if item.path == path)
    starts = [hunk.source_start for hunk in patched_file]
    ends = [hunk.source_start + max(hunk.source_length, hunk.target_length) for hunk in patched_file]
    return max(1, min(starts) - 12), min(line_count, max(ends) + 12)


def code_context(
    baseline: Path,
    candidate: Path,
    official_patch: str,
    source_paths: list[str],
    path_map: dict[str, str],
) -> str:
    blocks: list[str] = []
    for relative in sorted(source_paths):
        before = read_lines_exact(baseline / relative)
        after = read_lines_exact(candidate / relative)
        start, end = context_range(official_patch, relative, max(len(before), len(after)))
        before_text = "".join(before[start - 1 : end]).replace("\r\n", "\n").replace("\r", "\n")
        after_text = "".join(after[start - 1 : end]).replace("\r\n", "\n").replace("\r", "\n")
        blocks.append(
            f"File: {path_map[relative]}\n"
            f"Before lines {start}-{end}:\n{before_text}"
            f"Candidate lines {start}-{end}:\n{after_text}"
        )
    return "\n".join(blocks)


def candidate_record(
    role: str,
    patch_text: str,
    candidate_root: Path,
    baseline_root: Path,
    official_patch: str,
    source_paths: list[str],
    path_map: dict[str, str],
) -> dict[str, Any]:
    patch_bytes = patch_text.encode("utf-8")
    patch_sha256 = sha256_bytes(patch_bytes)
    return {
        "role": role,
        "opaque_id": f"cand_{patch_sha256[:16]}",
        "patch_sha256": patch_sha256,
        "patch_utf8_bytes": len(patch_bytes),
        "patch_text": patch_text,
        "candidate_tree_sha256": tree_sha256(candidate_root),
        "neutral_payload": {
            "change_request": {
                "neutral_description": (
                    "Update optional credential handling when the supplied authorization scheme "
                    "does not match the expected scheme."
                ),
                "candidate_diff": normalized_patch(patch_text, path_map),
                "code_context": code_context(
                    baseline_root,
                    candidate_root,
                    official_patch,
                    source_paths,
                    path_map,
                ),
            }
        },
    }


def build_materialization(
    task_id: str,
    task_context: Path,
    task_image_id: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    preflight = read_json(PREFLIGHT)
    task = next(item for item in preflight["tasks"] if item["task_id"] == task_id)
    oracle_registry = read_json(ORACLE_REGISTRY)
    oracle = next(item for item in oracle_registry["records"] if item["task_id"] == task_id)
    if preflight.get("status") != "passed":
        raise ValueError("P4 preflight is not passed")
    if task.get("selected_transform_id") != T4_ID or oracle.get("selected_transform_id") != T4_ID:
        raise ValueError("task is not frozen to T4")
    allowed_states = {
        "oracle_frozen_transform_not_materialized",
        "candidates_materialized_outcomes_not_observed",
    }
    if oracle.get("status") not in allowed_states:
        raise ValueError(f"unexpected oracle state: {oracle.get('status')}")
    if oracle.get("task_image_id") != task_image_id:
        raise ValueError("task image ID drift")
    already_materialized = oracle.get("status") == "candidates_materialized_outcomes_not_observed"
    if oracle.get("transformed_candidate_outcome_observed"):
        raise ValueError("candidate activity already recorded")
    if bool(oracle.get("transformed_candidate_materialized")) != already_materialized:
        raise ValueError("candidate materialization flag disagrees with oracle state")

    metadata = task_context / "metadata"
    official_patch_path = metadata / "bug_patch.txt"
    official_patch_bytes = official_patch_path.read_bytes()
    if sha256_bytes(official_patch_bytes) != task["metadata_sha256"]["reference_patch"]:
        raise ValueError("official patch hash drift")
    official_patch = (
        official_patch_bytes.decode("utf-8")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )
    source_paths = list(task["reference_source_paths"])
    patch_files = [item.path for item in PatchSet(official_patch.splitlines(keepends=True))]
    if any(is_test_path(path) for path in patch_files):
        raise ValueError("this task-level materializer requires a source-only official patch")
    if sorted(patch_files) != sorted(source_paths):
        raise ValueError("official patch paths do not equal frozen source paths")

    with tempfile.TemporaryDirectory(prefix="dsa-p4-materialize-") as temporary:
        temp = Path(temporary)
        baseline = temp / "baseline"
        positive_root = temp / "positive"
        negative_root = temp / "negative"
        copy_baseline(task_context, baseline)
        shutil.copytree(baseline, positive_root)
        apply_patch(positive_root, official_patch_path)
        if tree_sha256(positive_root) != oracle["collection"]["candidate_tree_sha256"]:
            raise ValueError("reference tree does not match the pre-outcome oracle freeze")

        rows = t4_edit_rows(official_patch)
        if len(rows) < 3:
            raise ValueError("T4 requires at least three changed non-header lines")
        selected = rows[0]
        shutil.copytree(positive_root, negative_root)
        selected_path = negative_root / selected["path"]
        candidate_lines = read_lines_exact(selected_path)
        index = selected["target_index"]
        value = selected["value"]
        if selected["kind"] == "added":
            if index >= len(candidate_lines) or candidate_lines[index].replace("\r\n", "\n").replace("\r", "\n") != value:
                raise ValueError("selected added line does not match the reference-fixed file")
            del candidate_lines[index]
        else:
            candidate_lines.insert(index, value)
        write_text_exact(selected_path, "".join(candidate_lines))
        negative_patch = unified_diff_for_paths(baseline, negative_root, source_paths)
        if not negative_patch:
            raise ValueError("T4 produced the buggy baseline")
        if negative_patch.replace("\r\n", "\n") == official_patch.replace("\r\n", "\n"):
            raise ValueError("T4 did not change the reference patch")

        negative_patch_path = temp / "negative.patch"
        write_text_exact(negative_patch_path, negative_patch)
        verification_root = temp / "negative-verification"
        shutil.copytree(baseline, verification_root)
        apply_patch(verification_root, negative_patch_path)
        if tree_sha256(verification_root) != tree_sha256(negative_root):
            raise ValueError("materialized negative patch is not reproducible")

        path_map = {
            path: f"module_{index:03d}{Path(path).suffix}"
            for index, path in enumerate(sorted(source_paths), start=1)
        }
        candidates = [
            candidate_record(
                "oracle_positive",
                official_patch,
                positive_root,
                baseline,
                official_patch,
                source_paths,
                path_map,
            ),
            candidate_record(
                "hard_negative",
                negative_patch,
                negative_root,
                baseline,
                official_patch,
                source_paths,
                path_map,
            ),
        ]

    role_by_id = {item["opaque_id"]: item["role"] for item in candidates}
    if len(role_by_id) != 2:
        raise ValueError("candidate opaque IDs are not distinct")
    record = {
        "task_id": task_id,
        "project": task["project"],
        "stream_role": task["role"],
        "stream_order": task["stream_order"],
        "status": "materialized_outcomes_not_observed",
        "task_image": oracle["task_image"],
        "task_image_id": task_image_id,
        "source_paths": source_paths,
        "normalized_path_map": path_map,
        "reference_patch_sha256": task["metadata_sha256"]["reference_patch"],
        "transform_id": T4_ID,
        "transform_implementation": {
            "unit": "one added or removed non-header source-diff line",
            "identity_fields": ["path", "hunk_index", "line_index", "kind", "value"],
            "identity_serialization": "canonical JSON UTF-8, sort_keys=true, separators=(',', ':')",
            "order": "SHA-256(identity) ascending, then canonical identity bytes ascending",
            "operation": "invert the first ordered line on the reference-fixed tree",
            "selected_identity": {
                key: selected[key]
                for key in ("path", "hunk_index", "line_index", "kind", "value", "identity_sha256")
            },
            "eligible_edit_count": len(rows),
            "outcome_observed_before_selection": False,
        },
        "frozen_checks": {
            "official_f2p_nodeids": oracle["official_f2p_nodeids"],
            "visible_p2p_nodeids": oracle["visible_p2p_nodeids"],
            "hidden_regression_nodeids": oracle["hidden_regression_nodeids"],
            "visible_p2p_sha256": oracle["visible_p2p_sha256"],
            "hidden_regression_sha256": oracle["hidden_regression_sha256"],
        },
        "candidates": candidates,
        "role_by_opaque_id": role_by_id,
        "candidate_outcome_observed": False,
        "task_gate": "pending_candidate_runs",
    }
    materialization_sha256 = sha256_bytes(canonical_bytes(record))
    record["materialization_sha256"] = materialization_sha256

    updated_oracle = json.loads(json.dumps(oracle_registry))
    updated_record = next(item for item in updated_oracle["records"] if item["task_id"] == task_id)
    updated_record.update(
        {
            "status": "candidates_materialized_outcomes_not_observed",
            "transformed_candidate_materialized": True,
            "transformed_candidate_outcome_observed": False,
            "candidate_materialization_sha256": materialization_sha256,
        }
    )
    return record, updated_oracle


def registry_with(record: dict[str, Any]) -> dict[str, Any]:
    existing_records: list[dict[str, Any]] = []
    if CANDIDATE_REGISTRY.exists():
        existing_records = [
            item
            for item in read_json(CANDIDATE_REGISTRY).get("records", [])
            if item["task_id"] != record["task_id"]
        ]
    existing_records.append(record)
    existing_records.sort(key=lambda item: (item["stream_role"], item["stream_order"], item["task_id"]))
    return {
        "registry_id": "dsa_p4_candidate_registry_v0_1",
        "created_date": "2026-07-11",
        "visibility": "hidden_never_model_visible",
        "status": "materialization_in_progress",
        "records": existing_records,
        "boundary": "Candidate identities and transforms are frozen before any candidate check outcome.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--task-context", required=True)
    parser.add_argument("--image", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    inspected = json.loads(
        subprocess.check_output(
            ["docker", "image", "inspect", args.image],
            text=True,
            encoding="utf-8",
        )
    )
    if len(inspected) != 1:
        raise ValueError("expected exactly one task image")
    record, updated_oracle = build_materialization(
        args.task_id,
        Path(args.task_context).resolve(),
        inspected[0]["Id"],
    )
    registry = registry_with(record)
    outputs = {
        CANDIDATE_REGISTRY: json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        ORACLE_REGISTRY: json.dumps(updated_oracle, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    }
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    else:
        stale = [
            str(path.relative_to(ROOT))
            for path, content in outputs.items()
            if not path.exists() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            raise SystemExit(f"stale materialization outputs: {stale}")
    print(
        json.dumps(
            {
                "task_id": record["task_id"],
                "transform_id": record["transform_id"],
                "selected_edit_sha256": record["transform_implementation"]["selected_identity"]["identity_sha256"],
                "candidate_ids": sorted(record["role_by_opaque_id"]),
                "candidate_outcome_observed": record["candidate_outcome_observed"],
                "materialization_sha256": record["materialization_sha256"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
