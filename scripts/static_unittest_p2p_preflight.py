from __future__ import annotations

import argparse
import ast
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_SOURCE_ROOT = Path("..") / "research" / "data" / "real_bugs" / "bugsinpy_workspace"


def checkout_root(source_root: Path, task_id: str, version: str, project: str) -> Path:
    bug_dir = task_id.replace("bugsinpy_", "")
    return source_root / bug_dir / version / project


def module_name(root: Path, path: Path) -> str:
    return path.relative_to(root).with_suffix("").as_posix().replace("/", ".")


def iter_test_files(start_dir: Path, pattern: str) -> list[Path]:
    ignored_parts = {".git", ".tox", ".venv", "__pycache__", "build", "dist", "env", "venv"}
    files = []
    for path in start_dir.rglob(pattern):
        if not path.is_file() or path.suffix != ".py":
            continue
        relative = path.relative_to(start_dir)
        if any(part in ignored_parts for part in relative.parts):
            continue
        files.append(path)
    return sorted(files)


def summarize_version(root: Path, start_dir: str, pattern: str, exclude_tokens: list[str]) -> dict[str, Any]:
    start_path = root / start_dir
    if not start_path.exists():
        raise FileNotFoundError(f"missing unittest start dir: {start_path}")

    lowered_tokens = [token.lower() for token in exclude_tokens]
    methods: list[dict[str, Any]] = []
    parse_errors: list[dict[str, str]] = []

    for path in iter_test_files(start_path, pattern):
        relative_file = path.relative_to(root).as_posix()
        source = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(source, filename=relative_file)
        except SyntaxError as exc:
            parse_errors.append({"file": relative_file, "error": str(exc)})
            continue

        module = module_name(root, path)
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            for child in node.body:
                if not isinstance(child, ast.FunctionDef) or not child.name.startswith("test"):
                    continue
                segment = ast.get_source_segment(source, child) or ""
                segment_lower = segment.lower()
                hits = [token for token, lowered in zip(exclude_tokens, lowered_tokens) if lowered in segment_lower]
                methods.append(
                    {
                        "nodeid": f"{module}.{node.name}.{child.name}",
                        "file": relative_file,
                        "excluded_by_tokens": hits,
                    }
                )

    remaining = [method for method in methods if not method["excluded_by_tokens"]]
    excluded = [method for method in methods if method["excluded_by_tokens"]]
    remaining_by_file = Counter(method["file"] for method in remaining)

    return {
        "checkout": str(root),
        "start_dir": start_dir,
        "pattern": pattern,
        "test_files_static": len(iter_test_files(start_path, pattern)),
        "total_test_methods_static": len(methods),
        "excluded_by_static_tokens": len(excluded),
        "remaining_after_static_exclusions": len(remaining),
        "remaining_by_file_top": [
            {"file": file_name, "remaining_methods": count}
            for file_name, count in sorted(remaining_by_file.items(), key=lambda item: (-item[1], item[0]))[:10]
        ],
        "parse_error_files": parse_errors,
        "remaining_nodeids": sorted(method["nodeid"] for method in remaining),
    }


def build_summary(args: argparse.Namespace) -> dict[str, Any]:
    source_root = Path(args.source_workspace_root)
    buggy_root = checkout_root(source_root, args.task_id, "buggy", args.project)
    fixed_root = checkout_root(source_root, args.task_id, "fixed", args.project)
    if not buggy_root.exists():
        raise FileNotFoundError(f"missing buggy checkout: {buggy_root}")
    if not fixed_root.exists():
        raise FileNotFoundError(f"missing fixed checkout: {fixed_root}")

    buggy = summarize_version(buggy_root, args.unittest_start_dir, args.unittest_pattern, args.static_exclude_token)
    fixed = summarize_version(fixed_root, args.unittest_start_dir, args.unittest_pattern, args.static_exclude_token)
    buggy_remaining = set(buggy.pop("remaining_nodeids"))
    fixed_remaining = set(fixed.pop("remaining_nodeids"))

    return {
        "task_id": args.task_id,
        "project": args.project,
        "framework": "unittest",
        "mode": "static_no_run_preflight",
        "executed_tests": False,
        "created_p2p_manifest": False,
        "source_workspace_root": str(source_root),
        "static_exclude_tokens": args.static_exclude_token,
        "buggy": buggy,
        "fixed": fixed,
        "remaining_set_comparison": {
            "common_count": len(buggy_remaining & fixed_remaining),
            "buggy_only_count": len(buggy_remaining - fixed_remaining),
            "fixed_only_count": len(fixed_remaining - buggy_remaining),
            "buggy_only_sample": sorted(buggy_remaining - fixed_remaining)[:10],
            "fixed_only_sample": sorted(fixed_remaining - buggy_remaining)[:10],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Static no-run preflight for unittest P2P scope size.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--source-workspace-root", default=str(DEFAULT_SOURCE_ROOT))
    parser.add_argument("--unittest-start-dir", default="test")
    parser.add_argument("--unittest-pattern", default="test*.py")
    parser.add_argument("--static-exclude-token", action="append", default=[])
    parser.add_argument("--out-json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = build_summary(args)
    payload = json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.out_json:
        out_path = Path(args.out_json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
