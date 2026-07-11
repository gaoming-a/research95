#!/usr/bin/env python3
"""Prepare and audit one P4 task context from frozen official commit archives."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "data/protocols/dsa_p4_preflight_v0_1.json"
SOURCE_FRAME = ROOT / "data/protocols/dsa_p2_source_frame_v0_1.json"
CURSOR = ROOT / "data/protocols/dsa_p4_replacement_cursor_v0_1.json"
OUT = ROOT / "data/protocols/dsa_p4_task_source_registry_v0_1.json"
CONTEXT_ROOT = (ROOT / "tmp/dsa2026_p4_runtime/task_contexts").resolve()
SKIP_NAMES = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", "build", "dist"}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


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


def extract_commit_archive(archive: Path, destination: Path, expected_root: str) -> dict[str, Any]:
    destination.mkdir(parents=True, exist_ok=False)
    file_count = 0
    symlink_members: list[tarfile.TarInfo] = []
    roots: set[str] = set()
    with tarfile.open(archive, "r:gz") as tar:
        members = tar.getmembers()
        for member in members:
            parts = PurePosixPath(member.name).parts
            if not parts:
                continue
            roots.add(parts[0])
            if parts[0] != expected_root:
                raise ValueError(f"archive root drift: {parts[0]} != {expected_root}")
            relative_parts = parts[1:]
            if not relative_parts:
                continue
            if any(part in {"", ".", ".."} for part in relative_parts):
                raise ValueError(f"unsafe archive path: {member.name}")
            target = destination.joinpath(*relative_parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            if member.issym():
                symlink_members.append(member)
                continue
            if not member.isfile():
                raise ValueError(f"unsupported archive member type: {member.name}")
            target.parent.mkdir(parents=True, exist_ok=True)
            source = tar.extractfile(member)
            if source is None:
                raise ValueError(f"archive file has no payload: {member.name}")
            with source, target.open("wb") as output:
                shutil.copyfileobj(source, output)
            try:
                os.chmod(target, member.mode & 0o777)
            except OSError:
                pass
            file_count += 1
        for member in symlink_members:
            parts = PurePosixPath(member.name).parts[1:]
            relative_link = PurePosixPath(*parts)
            if PurePosixPath(member.linkname).is_absolute():
                raise ValueError(f"unsafe absolute symlink target: {member.name}")
            normalized_target = posixpath.normpath(
                str(relative_link.parent / PurePosixPath(member.linkname))
            )
            target_parts = PurePosixPath(normalized_target).parts
            if not target_parts or target_parts[0] == "..":
                raise ValueError(f"symlink escapes archive root: {member.name}")
            source_path = destination.joinpath(*target_parts)
            target_path = destination.joinpath(*relative_link.parts)
            if not source_path.exists():
                raise ValueError(f"symlink target missing: {member.name} -> {member.linkname}")
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if source_path.is_dir():
                shutil.copytree(source_path, target_path)
            else:
                shutil.copy2(source_path, target_path)
    if roots != {expected_root}:
        raise ValueError(f"archive roots drifted: {sorted(roots)}")
    return {
        "archive_sha256": sha256_file(archive),
        "archive_bytes": archive.stat().st_size,
        "archive_root": expected_root,
        "extracted_file_count": file_count,
        "materialized_symlink_count": len(symlink_members),
        "extracted_tree_sha256": tree_sha256(destination),
    }


def copy_metadata(catalog_root: Path, task: dict[str, Any], destination: Path) -> dict[str, str]:
    source = catalog_root / "projects" / task["project"] / "bugs" / str(task["bug_id"])
    names = ["bug.info", "bug_patch.txt", "requirements.txt", "run_test.sh"]
    if (source / "setup.sh").is_file():
        names.append("setup.sh")
    destination.mkdir(parents=True, exist_ok=False)
    hashes = {}
    key_by_name = {
        "bug.info": "bug_info",
        "bug_patch.txt": "reference_patch",
        "requirements.txt": "requirements",
        "run_test.sh": "run_test",
        "setup.sh": "setup",
    }
    for name in names:
        source_path = source / name
        target = destination / name
        shutil.copy2(source_path, target)
        key = key_by_name[name]
        actual = sha256_file(target)
        if actual != task["metadata_sha256"][key]:
            raise ValueError(f"metadata hash drift: {name}")
        hashes[name] = actual
    return hashes


def copy_fixed_tests(fixed_source: Path, declared: str, destination: Path) -> dict[str, str]:
    hashes = {}
    for value in declared.split(";"):
        relative = value.strip()
        if not relative:
            continue
        source = fixed_source / relative
        if not source.is_file():
            raise FileNotFoundError(source)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        hashes[relative] = sha256_file(target)
    if not hashes:
        raise ValueError("declared fixed test set is empty")
    return hashes


def apply_reference(context: Path) -> dict[str, Any]:
    candidate = context.parent / "reference_validation"
    shutil.copytree(context / "buggy_source", candidate)
    for source in sorted((context / "fixed_tests").rglob("*")):
        if source.is_file():
            target = candidate / source.relative_to(context / "fixed_tests")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    patch = context / "metadata/bug_patch.txt"
    patch_bytes = patch.read_bytes()
    normalized_patch = context.parent / "reference_validation.patch"
    normalized_patch.write_bytes(patch_bytes.replace(b"\r\n", b"\n"))
    checked = subprocess.run(
        ["git", "apply", "--check", str(normalized_patch)],
        cwd=candidate,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if checked.returncode != 0:
        raise RuntimeError(f"reference patch check failed: {checked.stderr[-2000:]}")
    applied = subprocess.run(
        ["git", "apply", str(normalized_patch)],
        cwd=candidate,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if applied.returncode != 0:
        raise RuntimeError(f"reference patch apply failed: {applied.stderr[-2000:]}")
    return {
        "patch_check_exit_code": checked.returncode,
        "patch_apply_exit_code": applied.returncode,
        "patch_line_endings_normalized": patch_bytes != normalized_patch.read_bytes(),
        "normalized_patch_sha256": sha256_file(normalized_patch),
        "reference_tree_sha256": tree_sha256(candidate),
    }


def build_context(
    task_id: str,
    buggy_archive: Path,
    fixed_archive: Path,
    catalog_root: Path,
    temporary_root: Path,
) -> tuple[Path, dict[str, Any]]:
    preflight = read_json(PREFLIGHT)
    source_frame = read_json(SOURCE_FRAME)
    cursor = read_json(CURSOR)
    task = next(item for item in preflight["tasks"] if item["task_id"] == task_id)
    source = next(item for item in source_frame["records"] if item["task_id"] == task_id)
    if cursor["status"] != "passed_unique_next_task" or cursor["cursor"]["next_task_id"] != task_id:
        raise ValueError("task does not equal the frozen replacement cursor")
    if task["candidate_materialized"] or task["candidate_hidden_result_observed"]:
        raise ValueError("preflight records prior candidate activity")
    if source["project_repository"] != "https://github.com/tornadoweb/tornado":
        raise ValueError("unexpected official project repository")

    context = temporary_root / task_id
    buggy_source = context / "buggy_source"
    fixed_source = temporary_root / "fixed_source"
    buggy_root = f"{task['project']}-{task['buggy_commit_id']}"
    fixed_root = f"{task['project']}-{task['fixed_commit_id']}"
    buggy_archive_record = extract_commit_archive(buggy_archive, buggy_source, buggy_root)
    fixed_archive_record = extract_commit_archive(fixed_archive, fixed_source, fixed_root)
    fixed_test_hashes = copy_fixed_tests(fixed_source, task["declared_test_file"], context / "fixed_tests")
    metadata_hashes = copy_metadata(catalog_root, task, context / "metadata")
    reference = apply_reference(context)
    record = {
        "task_id": task_id,
        "project": task["project"],
        "stream_role": task["role"],
        "stream_order": task["stream_order"],
        "status": "task_context_frozen_no_candidate",
        "source_repository": source["project_repository"],
        "source_acquisition": "official GitHub codeload commit tarballs after git transport reset",
        "buggy_commit_id": task["buggy_commit_id"],
        "fixed_commit_id": task["fixed_commit_id"],
        "buggy_archive": buggy_archive_record,
        "fixed_archive": fixed_archive_record,
        "buggy_source_tree_sha256": tree_sha256(buggy_source),
        "fixed_test_sha256": fixed_test_hashes,
        "metadata_sha256": metadata_hashes,
        "reference_validation": reference,
        "context_tree_sha256": tree_sha256(context),
        "cursor_sha256": cursor["cursor_sha256"],
        "candidate_materialized": False,
        "candidate_outcome_observed": False,
        "model_api_calls": 0,
    }
    record["record_sha256"] = sha256_bytes(canonical_bytes(record))
    return context, record


def registry_with(record: dict[str, Any]) -> dict[str, Any]:
    records = []
    if OUT.exists():
        records = [item for item in read_json(OUT).get("records", []) if item["task_id"] != record["task_id"]]
    records.append(record)
    records.sort(key=lambda item: (item["stream_role"], item["stream_order"], item["task_id"]))
    return {
        "registry_id": "dsa_p4_task_source_registry_v0_1",
        "created_date": "2026-07-11",
        "visibility": "private_pre_candidate_provenance",
        "records": records,
        "boundary": "Official task source and metadata only; no candidate, test outcome, prompt, P5 artifact, or model API call.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--buggy-archive", required=True)
    parser.add_argument("--fixed-archive", required=True)
    parser.add_argument("--catalog-root", required=True)
    parser.add_argument("--context-out", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    target = Path(args.context_out).resolve()
    if target.parent != CONTEXT_ROOT or target.name != args.task_id:
        raise ValueError(f"context output must be {CONTEXT_ROOT / args.task_id}")
    with tempfile.TemporaryDirectory(prefix="dsa-p4-source-") as temporary:
        generated_context, record = build_context(
            args.task_id,
            Path(args.buggy_archive).resolve(),
            Path(args.fixed_archive).resolve(),
            Path(args.catalog_root).resolve(),
            Path(temporary),
        )
        registry = registry_with(record)
        registry_content = json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if args.write:
            if target.exists():
                shutil.rmtree(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(generated_context, target)
            OUT.parent.mkdir(parents=True, exist_ok=True)
            OUT.write_text(registry_content, encoding="utf-8", newline="\n")
        else:
            stale = []
            if not target.is_dir() or tree_sha256(target) != record["context_tree_sha256"]:
                stale.append(str(target))
            if not OUT.exists() or OUT.read_text(encoding="utf-8") != registry_content:
                stale.append(str(OUT.relative_to(ROOT)))
            if stale:
                raise SystemExit(f"stale task context outputs: {stale}")
    print(
        json.dumps(
            {
                "task_id": record["task_id"],
                "buggy_archive_sha256": record["buggy_archive"]["archive_sha256"],
                "fixed_archive_sha256": record["fixed_archive"]["archive_sha256"],
                "context_tree_sha256": record["context_tree_sha256"],
                "reference_tree_sha256": record["reference_validation"]["reference_tree_sha256"],
                "record_sha256": record["record_sha256"],
                "candidate_materialized": record["candidate_materialized"],
                "model_api_calls": record["model_api_calls"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
