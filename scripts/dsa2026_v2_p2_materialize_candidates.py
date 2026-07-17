# ruff: noqa: E402
#!/usr/bin/env python3
"""Materialize all frozen-order V2-P2 candidates before candidate outcomes."""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/dsa2026_v2_p2_materialize_candidates.py")

import argparse
import hashlib
import json
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from unidiff import PatchSet

from dsa2026_p4_materialize_candidate import (
    apply_patch,
    patch_newlines,
    read_lines_exact,
    unified_diff_for_paths,
    write_text_exact,
)
from dsa2026_p4_prepare_task_context import tree_sha256
from dsa2026_v2_p2_freeze_task_context import signed_amendment


ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "bugsinpy_pandas_161"
ORDER = 1
REGISTRY_ID = "dsa_v2_p2_pandas_161_candidate_registry_v0_1"
CONTEXT = ROOT / f"tmp/dsa2026_v2_p2_runtime/task_contexts/{TASK_ID}"
ORACLE = ROOT / "data/hidden/dsa_v2_p2_pandas_161_oracle_v0_1.json"
OUT = ROOT / "data/hidden/dsa_v2_p2_pandas_161_candidate_registry_v0_1.json"
PATCH_ROOT = ROOT / f"tmp/dsa2026_v2_p2_runtime/candidates/{TASK_ID}"
PROTOCOL = ROOT / "data/protocols/dsa_v2_p1_construction_protocol_v0_1.json"


@dataclass(frozen=True)
class EditUnit:
    class_id: str
    descriptor: dict[str, Any]
    selected: Callable[[str, int, int, int], bool]


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def is_test_path(path: str) -> bool:
    parts = [item.lower() for item in Path(path).parts]
    return any(item in {"test", "tests"} for item in parts) or Path(path).name.lower().startswith("test_")


def descriptor(
    class_id: str,
    path: str,
    hunk_index: int | None = None,
    edit_block_index: int | None = None,
    line_index: int | None = None,
    edit_kind: str | None = None,
    raw_line_value: str | None = None,
) -> dict[str, Any]:
    return {
        "class_id": class_id,
        "path": path,
        "hunk_index": hunk_index,
        "edit_block_index": edit_block_index,
        "line_index": line_index,
        "edit_kind": edit_kind,
        "raw_line_value": raw_line_value,
    }


def edit_blocks(hunk: Any) -> list[list[int]]:
    blocks: list[list[int]] = []
    current: list[int] = []
    for index, line in enumerate(hunk):
        if line.is_added or line.is_removed:
            current.append(index)
        elif current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)
    return blocks


def enumerate_units(patch: PatchSet) -> list[EditUnit]:
    files = [item for item in patch if not is_test_path(item.path)]
    if len(files) != len(patch):
        raise ValueError("V2-P2 input patch must be source-only")
    units_by_class: dict[str, list[EditUnit]] = {
        "T1_omit_one_source_file": [],
        "T2_omit_one_hunk": [],
        "T3_omit_one_edit_block": [],
        "T4_revert_one_changed_line": [],
    }
    if len(files) >= 2:
        for changed_file in files:
            path = changed_file.path
            units_by_class["T1_omit_one_source_file"].append(EditUnit(
                "T1_omit_one_source_file",
                descriptor("T1_omit_one_source_file", path),
                lambda candidate_path, _h, _b, _l, path=path: candidate_path == path,
            ))

    hunk_rows = [(changed_file.path, index, hunk) for changed_file in files for index, hunk in enumerate(changed_file)]
    if len(hunk_rows) >= 2:
        for path, hunk_index, _hunk in hunk_rows:
            units_by_class["T2_omit_one_hunk"].append(EditUnit(
                "T2_omit_one_hunk",
                descriptor("T2_omit_one_hunk", path, hunk_index=hunk_index),
                lambda candidate_path, candidate_hunk, _b, _l, path=path, hunk_index=hunk_index: candidate_path == path and candidate_hunk == hunk_index,
            ))

    block_rows = []
    line_rows = []
    for path, hunk_index, hunk in hunk_rows:
        for block_index, indices in enumerate(edit_blocks(hunk)):
            block_rows.append((path, hunk_index, block_index, indices))
        for line_index, line in enumerate(hunk):
            if line.is_added or line.is_removed:
                line_rows.append((path, hunk_index, line_index, "added" if line.is_added else "removed", line.value))
    if len(block_rows) >= 2:
        for path, hunk_index, block_index, _indices in block_rows:
            units_by_class["T3_omit_one_edit_block"].append(EditUnit(
                "T3_omit_one_edit_block",
                descriptor("T3_omit_one_edit_block", path, hunk_index, block_index),
                lambda candidate_path, candidate_hunk, candidate_block, _l, path=path, hunk_index=hunk_index, block_index=block_index: candidate_path == path and candidate_hunk == hunk_index and candidate_block == block_index,
            ))
    if len(line_rows) >= 2:
        for path, hunk_index, line_index, kind, value in line_rows:
            units_by_class["T4_revert_one_changed_line"].append(EditUnit(
                "T4_revert_one_changed_line",
                descriptor("T4_revert_one_changed_line", path, hunk_index, None, line_index, kind, value),
                lambda candidate_path, candidate_hunk, _b, candidate_line, path=path, hunk_index=hunk_index, line_index=line_index: candidate_path == path and candidate_hunk == hunk_index and candidate_line == line_index,
            ))

    protocol = read_json(PROTOCOL)
    classes = [item["id"] for item in protocol["candidate_generation"]["candidate_classes_in_priority_order"]]
    seed = protocol["candidate_generation"]["tie_preimage"].split("|<task_id>", 1)[0]
    result: list[EditUnit] = []
    for class_id in classes:
        ranked = sorted(
            units_by_class[class_id],
            key=lambda unit: (
                sha256_bytes(f"{seed}|{TASK_ID}|{canonical_json(unit.descriptor)}".encode("utf-8")),
                canonical_json(unit.descriptor),
            ),
        )
        result.extend(ranked)
    return result


def omitted_hunk_lines(hunk: Any, unit: EditUnit, path: str, hunk_index: int, crlf: bool) -> list[str]:
    blocks = {}
    for block_index, indices in enumerate(edit_blocks(hunk)):
        for line_index in indices:
            blocks[line_index] = block_index
    output: list[str] = []
    for line_index, line in enumerate(hunk):
        selected = unit.selected(path, hunk_index, blocks.get(line_index, -1), line_index)
        if line.is_context or (line.is_added and not selected) or (line.is_removed and selected):
            output.append(patch_newlines(line.value, crlf))
    return output


def materialize_tree(positive: Path, patch: PatchSet, unit: EditUnit, destination: Path) -> None:
    shutil.copytree(positive, destination)
    for changed_file in patch:
        path = changed_file.path
        target = destination / path
        lines = read_lines_exact(target)
        crlf = any(line.endswith("\r\n") for line in lines)
        for hunk_index in reversed(range(len(changed_file))):
            hunk = changed_file[hunk_index]
            start = hunk.target_start - 1
            stop = start + hunk.target_length
            lines[start:stop] = omitted_hunk_lines(hunk, unit, path, hunk_index, crlf)
        write_text_exact(target, "".join(lines))


def build_registry(context: Path, oracle: dict[str, Any], destination: Path) -> tuple[dict[str, Any], Path]:
    signed_amendment()
    if oracle.get("status") != "oracle-positive-qualified-candidates-not-materialized":
        raise PermissionError("oracle-positive is not qualified or candidates already started")
    official_patch_path = context / "metadata/bug_patch.txt"
    official_bytes = official_patch_path.read_bytes()
    official_text = official_bytes.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    patch = PatchSet(official_text.splitlines(keepends=True))
    source_paths = [item.path for item in patch]
    buggy = context / "buggy_source"
    baseline = destination / "baseline"
    shutil.copytree(buggy, baseline)
    for fixed_test in sorted((context / "fixed_tests").rglob("*")):
        if fixed_test.is_file():
            target = baseline / fixed_test.relative_to(context / "fixed_tests")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(fixed_test, target)
    positive = destination / "positive"
    shutil.copytree(baseline, positive)
    apply_patch(positive, official_patch_path)
    positive_hash = tree_sha256(positive)
    if positive_hash != oracle["oracle_positive_tree_sha256"]:
        raise ValueError("oracle-positive tree hash drift")
    patch_dir = destination / "patches"
    patch_dir.mkdir(parents=True)
    positive_patch = patch_dir / "oracle_positive.patch"
    positive_patch.write_bytes(official_bytes)
    seen = {tree_sha256(baseline), positive_hash}
    records = []
    for ordinal, unit in enumerate(enumerate_units(patch), start=1):
        candidate_tree = destination / f"candidate_{ordinal:04d}"
        materialize_tree(positive, patch, unit, candidate_tree)
        tree_hash = tree_sha256(candidate_tree)
        patch_text = unified_diff_for_paths(baseline, candidate_tree, source_paths)
        patch_bytes = patch_text.encode("utf-8")
        if not patch_text or tree_hash in seen:
            shutil.rmtree(candidate_tree)
            continue
        verify = destination / f"verify_{ordinal:04d}"
        shutil.copytree(baseline, verify)
        patch_path = patch_dir / f"candidate_{len(records) + 1:04d}.patch"
        patch_path.write_bytes(patch_bytes)
        apply_patch(verify, patch_path)
        if tree_sha256(verify) != tree_hash:
            raise ValueError("candidate patch/tree reproducibility failure")
        shutil.rmtree(verify)
        seen.add(tree_hash)
        descriptor_json = canonical_json(unit.descriptor)
        protocol = read_json(PROTOCOL)
        seed = protocol["candidate_generation"]["tie_preimage"].split("|<task_id>", 1)[0]
        records.append({
            "ordinal": len(records) + 1,
            "class_id": unit.class_id,
            "descriptor": unit.descriptor,
            "descriptor_json": descriptor_json,
            "order_sha256": sha256_bytes(f"{seed}|{TASK_ID}|{descriptor_json}".encode("utf-8")),
            "patch_runtime_path": patch_path.relative_to(ROOT).as_posix(),
            "patch_sha256": sha256_bytes(patch_bytes),
            "tree_sha256": tree_hash,
            "outcome_observed": False,
        })
    registry = {
        "registry_id": REGISTRY_ID,
        "created_date": "2026-07-12",
        "task_id": TASK_ID,
        "order": ORDER,
        "status": "candidates-materialized-outcomes-not-observed",
        "task_image_id": oracle["task_image_id"],
        "oracle_positive_patch_runtime_path": positive_patch.relative_to(ROOT).as_posix(),
        "oracle_positive_patch_sha256": sha256_bytes(official_bytes),
        "oracle_positive_tree_sha256": positive_hash,
        "source_paths": source_paths,
        "candidate_count": len(records),
        "candidates": records,
        "candidate_outcome_observed": False,
        "model_api_calls": 0,
        "boundary": "All T1-T4 candidates are hash-ordered and frozen before any candidate check outcome.",
    }
    return registry, destination


def self_test() -> dict[str, Any]:
    patch_text = """--- a/pkg/a.py\n+++ b/pkg/a.py\n@@ -1,3 +1,3 @@\n one\n-old\n+new\n three\n--- a/pkg/b.py\n+++ b/pkg/b.py\n@@ -1,4 +1,4 @@\n alpha\n-x\n+y\n omega\n tail\n"""
    patch = PatchSet(patch_text.splitlines(keepends=True))
    units = enumerate_units(patch)
    counts = {class_id: sum(unit.class_id == class_id for unit in units) for class_id in {
        "T1_omit_one_source_file", "T2_omit_one_hunk", "T3_omit_one_edit_block", "T4_revert_one_changed_line"
    }}
    expected = {
        "T1_omit_one_source_file": 2,
        "T2_omit_one_hunk": 2,
        "T3_omit_one_edit_block": 2,
        "T4_revert_one_changed_line": 4,
    }
    if counts != expected:
        raise AssertionError(f"synthetic enumeration drift: {counts}")
    with tempfile.TemporaryDirectory(prefix="dsa_v2_p2_candidate_selftest_") as raw:
        root = Path(raw)
        buggy = root / "buggy"
        (buggy / "pkg").mkdir(parents=True)
        (buggy / "pkg/a.py").write_text("one\nold\nthree\n", encoding="utf-8", newline="\n")
        (buggy / "pkg/b.py").write_text("alpha\nx\nomega\ntail\n", encoding="utf-8", newline="\n")
        official = root / "official.patch"
        official.write_text(patch_text, encoding="utf-8", newline="\n")
        positive = root / "positive"
        shutil.copytree(buggy, positive)
        apply_patch(positive, official)
        reproducible = 0
        for index, unit in enumerate(units, start=1):
            candidate = root / f"candidate_{index}"
            materialize_tree(positive, patch, unit, candidate)
            candidate_patch = unified_diff_for_paths(buggy, candidate, ["pkg/a.py", "pkg/b.py"])
            if not candidate_patch:
                raise AssertionError("synthetic candidate collapsed to buggy tree")
            candidate_patch_path = root / f"candidate_{index}.patch"
            candidate_patch_path.write_text(candidate_patch, encoding="utf-8", newline="\n")
            verify = root / f"verify_{index}"
            shutil.copytree(buggy, verify)
            apply_patch(verify, candidate_patch_path)
            if tree_sha256(verify) != tree_sha256(candidate):
                raise AssertionError("synthetic candidate patch/tree mismatch")
            reproducible += 1
    return {
        "status": "passed",
        "counts": counts,
        "reproducible_candidates": reproducible,
        "real_activity": 0,
        "model_api_calls": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), sort_keys=True))
        return
    oracle = read_json(ORACLE)
    with tempfile.TemporaryDirectory(prefix="dsa_v2_p2_candidates_") as raw:
        registry, generated = build_registry(CONTEXT, oracle, Path(raw) / TASK_ID)
        content = json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if args.write:
            if PATCH_ROOT.exists():
                shutil.rmtree(PATCH_ROOT)
            PATCH_ROOT.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(generated, PATCH_ROOT)
            OUT.write_text(content, encoding="utf-8", newline="\n")
        else:
            if not OUT.is_file() or OUT.read_text(encoding="utf-8") != content:
                raise SystemExit("stale V2-P2 candidate registry")
            for item in registry["candidates"]:
                path = ROOT / item["patch_runtime_path"]
                if not path.is_file() or sha256_bytes(path.read_bytes()) != item["patch_sha256"]:
                    raise SystemExit(f"candidate patch drift: {path}")
    print(json.dumps({
        "status": registry["status"],
        "candidate_count": registry["candidate_count"],
        "candidate_outcomes": 0,
        "model_api_calls": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
