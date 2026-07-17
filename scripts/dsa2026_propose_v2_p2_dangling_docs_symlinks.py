# ruff: noqa: E402
#!/usr/bin/env python3
"""Propose a no-outcome rule for dangling documentation symlinks."""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/dsa2026_propose_v2_p2_dangling_docs_symlinks.py")

import argparse
import hashlib
import json
import posixpath
import tarfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "data/protocols/dsa_v2_p2_cursor_task_config_v0_1.json"
OUT = (
    ROOT / "data/protocols/dsa_v2_p2_dangling_docs_symlink_amendment_proposal_v0_1.json"
)
REPORT = (
    ROOT / "docs/experiments/dsa_v2_p2_dangling_docs_symlink_amendment_signoff_v0_1.md"
)


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
        ).encode("utf-8")
    ).hexdigest()


def archive_manifest(path: Path) -> dict[str, Any]:
    archive_bytes = path.read_bytes()
    with tarfile.open(path, "r:gz") as tar:
        members = tar.getmembers()
        roots = {member.name.split("/", 1)[0] for member in members if member.name}
        if len(roots) != 1:
            raise ValueError("archive has non-unique root")
        root = next(iter(roots))
        names = {posixpath.normpath(member.name) for member in members}
        symlinks = []
        for member in members:
            if not (member.issym() or member.islnk()):
                continue
            resolved = posixpath.normpath(
                posixpath.join(posixpath.dirname(member.name), member.linkname)
            )
            relative = posixpath.relpath(posixpath.normpath(member.name), root)
            symlinks.append(
                {
                    "path": relative,
                    "target": member.linkname,
                    "resolved_archive_path": resolved,
                    "target_present": resolved in names,
                    "kind": "symbolic" if member.issym() else "hardlink",
                }
            )
    return {
        "archive_path": path.relative_to(ROOT).as_posix(),
        "archive_sha256": hashlib.sha256(archive_bytes).hexdigest(),
        "archive_root": root,
        "symlinks": sorted(symlinks, key=lambda item: (item["path"], item["target"])),
    }


def build(buggy: Path, fixed: Path) -> dict[str, Any]:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    if config["task"]["order"] != 3 or config["task"]["task_id"] != "bugsinpy_black_4":
        raise ValueError("proposal is not anchored to order3 Black_4")
    archives = [archive_manifest(buggy), archive_manifest(fixed)]
    dangling_by_archive = [
        [item for item in archive["symlinks"] if not item["target_present"]]
        for archive in archives
    ]
    identities = [
        [
            {"path": item["path"], "target": item["target"], "kind": item["kind"]}
            for item in rows
        ]
        for rows in dangling_by_archive
    ]
    declared_tests = set(config["task"]["declared_test_file"].split(";"))
    test_root = config["project_test_scope"]["project_test_root"].rstrip("/") + "/"
    forbidden_metadata = {
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "requirements.txt",
        "tox.ini",
    }
    changed_source_paths = {"black.py"}
    all_dangling = [item for rows in dangling_by_archive for item in rows]
    checks = {
        "cursor_is_unstarted_order3_black4": config["task"]["order"] == 3
        and not config["next_task_started"],
        "both_official_archives_inspected": len(archives) == 2,
        "dangling_identity_equal_across_commits": identities[0] == identities[1],
        "all_dangling_are_symbolic_docs_paths": bool(all_dangling)
        and all(
            item["kind"] == "symbolic" and item["path"].startswith("docs/")
            for item in all_dangling
        ),
        "no_declared_test_intersection": all(
            item["path"] not in declared_tests
            and not item["path"].startswith(test_root)
            for item in all_dangling
        ),
        "no_changed_source_intersection": all(
            item["path"] not in changed_source_paths for item in all_dangling
        ),
        "no_package_build_metadata_intersection": all(
            posixpath.basename(item["path"]) not in forbidden_metadata
            for item in all_dangling
        ),
        "no_real_activity_or_outcome_used": True,
        "author_signoff_required_before_extraction": True,
    }
    manifest = identities[0]
    return {
        "proposal_id": "dsa_v2_p2_dangling_docs_symlink_amendment_proposal_v0_1",
        "created_date": "2026-07-12",
        "status": "author_signoff_required" if all(checks.values()) else "failed",
        "task_id": "bugsinpy_black_4",
        "order": 3,
        "cursor_config_sha256": config["config_sha256"],
        "rule": "For a dangling symbolic link whose normalized path is strictly under docs/ and outside declared tests, project test root, changed source, and package/build metadata, preserve path/target/kind and archive hashes in a manifest and omit only the unmaterializable link from the Windows build/test tree. Any other dangling link is a frozen-content hard stop.",
        "archives": archives,
        "dangling_manifest": manifest,
        "dangling_manifest_sha256": canonical_sha(manifest),
        "dangling_count_per_archive": [len(rows) for rows in dangling_by_archive],
        "checks": checks,
        "authorization": {
            "author_signed": False,
            "source_extraction": False,
            "environment": False,
            "model_api": False,
        },
        "boundary": "No source tree was extracted, no environment/container/test was started, and no model API was called.",
    }


def render(value: dict[str, Any]) -> str:
    lines = [
        "# V2-P2 Dangling Documentation Symlink Amendment Sign-off",
        "",
        "日期：2026-07-12",
        "状态：`AUTHOR_SIGNOFF_REQUIRED / NO_REAL_ACTIVITY / NO_API`",
        "",
        "Black_4 的两个 official archives 含相同的 dangling documentation symlinks。Windows 当前权限不能原样创建。",
        "",
        f"manifest SHA-256：`{value['dangling_manifest_sha256']}`；每个 archive 数量：`{value['dangling_count_per_archive']}`。",
        "",
        "提议规则：仅对严格位于 docs/、与 declared tests/project test root/package-build metadata 零交集的 dangling symbolic link，记录 path/target/kind 与 archive hashes，并只从 Windows materialized tree 省略该不可创建 link。其他 dangling link 触发 hard stop。",
        "",
        "## Manifest",
        "",
    ]
    lines.extend(
        f"- `{item['path']}` -> `{item['target']}`"
        for item in value["dangling_manifest"]
    )
    lines.extend(
        ["", "作者尚未签核；source extraction/environment/test/API 均为0。", ""]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--buggy-archive", required=True)
    parser.add_argument("--fixed-archive", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build(
        Path(args.buggy_archive).resolve(), Path(args.fixed_archive).resolve()
    )
    outputs = {
        OUT: json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        REPORT: render(value),
    }
    if args.write:
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8", newline="\n")
    else:
        stale = [
            str(path)
            for path, content in outputs.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            raise SystemExit(f"stale dangling symlink proposal: {stale}")
    print(
        json.dumps(
            {
                "status": value["status"],
                "dangling_count": len(value["dangling_manifest"]),
                "manifest_sha256": value["dangling_manifest_sha256"],
                "real_activity": 0,
                "model_api_calls": 0,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
