#!/usr/bin/env python3
"""Run one isolated P4 reference/candidate check inside a task image."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


TASK_ROOT = Path(os.environ.get("DSA_P4_TASK_ROOT", "/opt/dsa2026/task"))
PYTHON_ENV = os.environ.get("DSA_P4_PYTHON_ENV", "")
WORKSPACE = Path("/workspace/project")
SKIP_NAMES = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", "build", "dist"}


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


def copy_fixed_tests() -> list[str]:
    copied: list[str] = []
    fixed_root = TASK_ROOT / "fixed_tests"
    for source in sorted(fixed_root.rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(fixed_root)
        target = WORKSPACE / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append(relative.as_posix())
    return copied


def prepare_reference() -> dict[str, Any]:
    if WORKSPACE.exists():
        if WORKSPACE != Path("/workspace/project"):
            raise RuntimeError(f"refusing to replace unexpected workspace: {WORKSPACE}")
        shutil.rmtree(WORKSPACE)
    WORKSPACE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(TASK_ROOT / "buggy_source", WORKSPACE)
    copied_tests = copy_fixed_tests()
    patch = TASK_ROOT / "metadata" / "bug_patch.txt"
    check = subprocess.run(
        ["git", "apply", "--check", str(patch)],
        cwd=WORKSPACE,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check.returncode != 0:
        raise RuntimeError(f"reference patch check failed: {check.stderr[-2000:]}")
    apply = subprocess.run(
        ["git", "apply", str(patch)],
        cwd=WORKSPACE,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if apply.returncode != 0:
        raise RuntimeError(f"reference patch apply failed: {apply.stderr[-2000:]}")
    return {
        "candidate": "reference",
        "fixed_test_paths": copied_tests,
        "reference_patch_sha256": sha256_bytes(patch.read_bytes()),
        "candidate_tree_sha256": tree_sha256(WORKSPACE),
    }


def env_bin(name: str) -> Path:
    path = Path("/opt/conda/envs") / PYTHON_ENV / "bin" / name
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def run_command(command: list[str], timeout: int) -> dict[str, Any]:
    started = time.monotonic()
    command_cwd = WORKSPACE if WORKSPACE.is_dir() else Path("/")
    try:
        result = subprocess.run(
            command,
            cwd=command_cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env={**os.environ, "PATH": f"{env_bin('python').parent}:{os.environ.get('PATH', '')}"},
        )
        timed_out = False
        exit_code = result.returncode
        output = result.stdout + result.stderr
    except subprocess.TimeoutExpired as error:
        timed_out = True
        exit_code = 124
        stdout = error.stdout.decode("utf-8", errors="replace") if isinstance(error.stdout, bytes) else (error.stdout or "")
        stderr = error.stderr.decode("utf-8", errors="replace") if isinstance(error.stderr, bytes) else (error.stderr or "")
        output = stdout + stderr
    normalized = output.replace(str(WORKSPACE), "<PROJECT>").replace("\r\n", "\n").replace("\r", "\n")
    return {
        "command": command,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "duration_seconds": round(time.monotonic() - started, 3),
        "outcome": "passed" if exit_code == 0 and not timed_out else "failed",
        "output_sha256": sha256_bytes(normalized.encode("utf-8")),
        "output_excerpt": normalized[-4000:],
        "_normalized_output": normalized,
    }


def collect_nodes(test_root: str, timeout: int) -> dict[str, Any]:
    preparation = prepare_reference()
    result = run_command(
        [str(env_bin("python")), "-m", "pytest", "--collect-only", "-q", test_root],
        timeout,
    )
    nodes: list[str] = []
    for line in result["_normalized_output"].splitlines():
        stripped = line.strip()
        if "::" in stripped and not stripped.startswith(("<", "=")):
            nodes.append(stripped)
    result["collected_nodeids"] = sorted(set(nodes))
    result["collected_node_count"] = len(result["collected_nodeids"])
    result.pop("_normalized_output", None)
    return {"preparation": preparation, "collection": result}


def official_f2p(timeout: int) -> dict[str, Any]:
    preparation = prepare_reference()
    commands = [
        line.strip()
        for line in (TASK_ROOT / "metadata" / "run_test.sh").read_text(encoding="utf-8").replace("\r", "").splitlines()
        if line.strip()
    ]
    checks = []
    for command in commands:
        result = run_command(["/bin/bash", "-c", command], timeout)
        result.pop("_normalized_output", None)
        checks.append(result)
    return {"preparation": preparation, "checks": checks}


def run_nodes(nodeids: list[str], timeout: int) -> dict[str, Any]:
    preparation = prepare_reference()
    checks = []
    for nodeid in nodeids:
        result = run_command(
            [str(env_bin("python")), "-m", "pytest", "-q", nodeid],
            timeout,
        )
        result.pop("_normalized_output", None)
        result["nodeid"] = nodeid
        checks.append(result)
    return {"preparation": preparation, "checks": checks}


def environment_audit() -> dict[str, Any]:
    records = {}
    build = TASK_ROOT / "environment_build"
    for path in sorted(build.iterdir()):
        if path.is_file():
            records[path.name] = {
                "sha256": sha256_bytes(path.read_bytes()),
                "bytes": path.stat().st_size,
            }
    version = run_command([str(env_bin("python")), "--version"], 30)
    version.pop("_normalized_output", None)
    return {"python": version, "build_artifacts": records}


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("environment-audit")
    f2p = subparsers.add_parser("official-f2p")
    f2p.add_argument("--timeout", type=int, default=300)
    collect = subparsers.add_parser("collect")
    collect.add_argument("--test-root", required=True)
    collect.add_argument("--timeout", type=int, default=1800)
    nodes = subparsers.add_parser("run-nodes")
    nodes.add_argument("--node", action="append", required=True)
    nodes.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    if args.command == "environment-audit":
        value = environment_audit()
    elif args.command == "official-f2p":
        value = official_f2p(args.timeout)
    elif args.command == "collect":
        value = collect_nodes(args.test_root, args.timeout)
    else:
        value = run_nodes(args.node, args.timeout)
    print(json.dumps(value, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"worker_error": type(error).__name__, "message": str(error)}, sort_keys=True))
        sys.exit(1)
