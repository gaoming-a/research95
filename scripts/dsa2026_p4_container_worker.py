# ruff: noqa: E402
#!/usr/bin/env python3
"""Run one isolated P4 reference/candidate check inside a task image."""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/dsa2026_p4_container_worker.py")

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import textwrap
from pathlib import Path
from typing import Any


TASK_ROOT = Path(os.environ.get("DSA_P4_TASK_ROOT", "/opt/dsa2026/task"))
PYTHON_ENV = os.environ.get("DSA_P4_PYTHON_ENV", "")
WORKSPACE = Path("/workspace/project")
SKIP_NAMES = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", "build", "dist"}

UNITTEST_DISCOVERY = textwrap.dedent(
    """
    import argparse
    import json
    import traceback
    import unittest

    def flatten(suite):
        for item in suite:
            if isinstance(item, unittest.TestSuite):
                yield from flatten(item)
            else:
                yield item

    parser = argparse.ArgumentParser()
    parser.add_argument("--start-dir", required=True)
    parser.add_argument("--pattern", required=True)
    parser.add_argument("--top-level-dir", default="")
    args = parser.parse_args()
    loader = unittest.TestLoader()
    kwargs = {"start_dir": args.start_dir, "pattern": args.pattern}
    if args.top_level_dir:
        kwargs["top_level_dir"] = args.top_level_dir
    try:
        suite = loader.discover(**kwargs)
        tests = []
        errors = []
        for test in flatten(suite):
            test_id = test.id()
            if test_id.startswith("unittest.loader._FailedTest"):
                error = getattr(test, "_exception", None)
                errors.append({
                    "test_id": test_id,
                    "error_type": type(error).__name__ if error is not None else "UnittestFailedImport",
                    "message": str(error) if error is not None else test_id,
                    "traceback_excerpt": "".join(traceback.format_exception(error))[-2000:] if error is not None else test_id,
                })
            else:
                tests.append(test_id)
        print(json.dumps({"tests": sorted(set(tests)), "errors": errors}, sort_keys=True))
    except Exception as error:
        print(json.dumps({
            "tests": [],
            "errors": [{
                "test_id": args.start_dir,
                "error_type": type(error).__name__,
                "message": str(error),
                "traceback_excerpt": traceback.format_exc()[-2000:],
            }],
        }, sort_keys=True))
        raise
    """
)


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
    normalized_patch = WORKSPACE.parent / "reference_validation.patch"
    normalized_patch.write_bytes(patch.read_bytes().replace(b"\r\n", b"\n"))
    check = subprocess.run(
        ["git", "apply", "--check", str(normalized_patch)],
        cwd=WORKSPACE,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check.returncode != 0:
        raise RuntimeError(f"reference patch check failed: {check.stderr[-2000:]}")
    apply = subprocess.run(
        ["git", "apply", str(normalized_patch)],
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


def prepare_candidate(
    candidate_patch: Path,
    expected_patch_sha256: str,
    expected_tree_sha256: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if WORKSPACE.exists():
        if WORKSPACE != Path("/workspace/project"):
            raise RuntimeError(f"refusing to replace unexpected workspace: {WORKSPACE}")
        shutil.rmtree(WORKSPACE)
    WORKSPACE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(TASK_ROOT / "buggy_source", WORKSPACE)
    copied_tests = copy_fixed_tests()
    actual_patch_sha256 = sha256_bytes(candidate_patch.read_bytes())
    if actual_patch_sha256 != expected_patch_sha256:
        raise RuntimeError("candidate patch hash drift")
    command = ["git", "apply", "--check", str(candidate_patch)]
    checked = subprocess.run(
        command,
        cwd=WORKSPACE,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    normalized = (checked.stdout + checked.stderr).replace(str(candidate_patch), "<CANDIDATE_PATCH>")
    patch_check = {
        "check_code": "basic_patch_apply",
        "check_kind": "patch_apply",
        "command": ["git", "apply", "--check", "<CANDIDATE_PATCH>"],
        "exit_code": checked.returncode,
        "timed_out": False,
        "outcome": "passed" if checked.returncode == 0 else "failed",
        "output_sha256": sha256_bytes(normalized.encode("utf-8")),
        "output_excerpt": normalized[-4000:] or "candidate patch applies cleanly",
    }
    if checked.returncode != 0:
        raise RuntimeError(f"candidate patch check failed: {normalized[-2000:]}")
    applied = subprocess.run(
        ["git", "apply", str(candidate_patch)],
        cwd=WORKSPACE,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if applied.returncode != 0:
        raise RuntimeError(f"candidate patch apply failed: {applied.stderr[-2000:]}")
    actual_tree_sha256 = tree_sha256(WORKSPACE)
    if actual_tree_sha256 != expected_tree_sha256:
        raise RuntimeError("candidate tree hash drift")
    preparation = {
        "fixed_test_paths": copied_tests,
        "candidate_patch_sha256": actual_patch_sha256,
        "candidate_tree_sha256": actual_tree_sha256,
    }
    return preparation, patch_check


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


def collect_nodes(
    test_framework: str,
    test_root: str,
    unittest_pattern: str,
    unittest_top_level_dir: str,
    timeout: int,
) -> dict[str, Any]:
    preparation = prepare_reference()
    if test_framework == "unittest":
        command = [
            str(env_bin("python")), "-c", UNITTEST_DISCOVERY,
            "--start-dir", test_root,
            "--pattern", unittest_pattern,
            "--top-level-dir", unittest_top_level_dir,
        ]
    else:
        command = [str(env_bin("python")), "-m", "pytest", "--collect-only", "-q", test_root]
    result = run_command(command, timeout)
    nodes: list[str] = []
    collection_errors: list[dict[str, Any]] = []
    if test_framework == "unittest":
        output_lines = [line for line in result["_normalized_output"].splitlines() if line.strip()]
        if output_lines:
            try:
                payload = json.loads(output_lines[-1])
                nodes = [str(item) for item in payload.get("tests", [])]
                collection_errors = [item for item in payload.get("errors", []) if isinstance(item, dict)]
            except json.JSONDecodeError:
                collection_errors = [{"error_type": "DiscoveryOutputParseError", "message": output_lines[-1][-1000:]}]
    else:
        for line in result["_normalized_output"].splitlines():
            stripped = line.strip()
            if "::" in stripped and not stripped.startswith(("<", "=")):
                nodes.append(stripped)
    result["collected_nodeids"] = sorted(set(nodes))
    result["collected_node_count"] = len(result["collected_nodeids"])
    result["test_framework"] = test_framework
    result["collection_errors"] = collection_errors
    result["collection_error_count"] = len(collection_errors)
    result.pop("_normalized_output", None)
    return {"preparation": preparation, "collection": result}


def official_f2p(timeout: int) -> dict[str, Any]:
    preparation = prepare_reference()
    environment = environment_audit()
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
    return {"preparation": preparation, "environment": environment, "checks": checks}


def run_nodes(nodeids: list[str], test_framework: str, timeout: int) -> dict[str, Any]:
    preparation = prepare_reference()
    checks = []
    for nodeid in nodeids:
        command = (
            [str(env_bin("python")), "-m", "unittest", "-q", nodeid]
            if test_framework == "unittest"
            else [str(env_bin("python")), "-m", "pytest", "-q", nodeid]
        )
        result = run_command(command, timeout)
        result.pop("_normalized_output", None)
        result["nodeid"] = nodeid
        checks.append(result)
    return {"preparation": preparation, "checks": checks}


def evidence_result(result: dict[str, Any], **fields: Any) -> dict[str, Any]:
    value = {key: item for key, item in result.items() if key != "_normalized_output"}
    if not str(value.get("output_excerpt", "")).strip():
        value["output_excerpt"] = "command completed with no output"
    value.update(fields)
    return value


def candidate_run(args: argparse.Namespace) -> dict[str, Any]:
    candidate_patch = Path(args.candidate_patch)
    preparation, patch_check = prepare_candidate(
        candidate_patch,
        args.expected_patch_sha256,
        args.expected_tree_sha256,
    )
    environment = environment_audit()
    basic_checks = [patch_check]
    for index, source_path in enumerate(args.source_path, start=1):
        result = run_command(
            [str(env_bin("python")), "-m", "py_compile", source_path],
            args.timeout,
        )
        basic_checks.append(
            evidence_result(
                result,
                check_code=f"basic_static_{index:03d}",
                check_kind="syntax_or_import_or_static",
            )
        )
    f2p_checks = []
    for index, command in enumerate(args.f2p_command, start=1):
        result = run_command(["/bin/bash", "-c", command], args.timeout)
        f2p_checks.append(
            evidence_result(
                result,
                check_code=f"f2p_{index:03d}",
                test_name=f"visible_behavior_{index:03d}",
            )
        )
    visible_checks = []
    for index, nodeid in enumerate(args.visible_node, start=1):
        command = (
            [str(env_bin("python")), "-m", "unittest", "-q", nodeid]
            if args.test_framework == "unittest"
            else [str(env_bin("python")), "-m", "pytest", "-q", nodeid]
        )
        result = run_command(command, args.timeout)
        visible_checks.append(
            evidence_result(
                result,
                check_code=f"p2p_{index:03d}",
                test_name=nodeid,
            )
        )
    hidden_checks = []
    for index, nodeid in enumerate(args.hidden_node, start=1):
        command = (
            [str(env_bin("python")), "-m", "unittest", "-q", nodeid]
            if args.test_framework == "unittest"
            else [str(env_bin("python")), "-m", "pytest", "-q", nodeid]
        )
        result = run_command(command, args.timeout)
        hidden_checks.append(
            evidence_result(
                result,
                check_code=f"hidden_{index:03d}",
                test_name=nodeid,
            )
        )
    return {
        "preparation": preparation,
        "environment": environment,
        "executable_basic": basic_checks,
        "visible_f2p": f2p_checks,
        "visible_p2p": visible_checks,
        "hidden_regression": hidden_checks,
    }


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
    collect.add_argument("--test-framework", choices=("pytest", "unittest"), default="pytest")
    collect.add_argument("--unittest-pattern", default="*_test.py")
    collect.add_argument("--unittest-top-level-dir", default=".")
    collect.add_argument("--timeout", type=int, default=1800)
    nodes = subparsers.add_parser("run-nodes")
    nodes.add_argument("--node", action="append", required=True)
    nodes.add_argument("--test-framework", choices=("pytest", "unittest"), default="pytest")
    nodes.add_argument("--timeout", type=int, default=300)
    candidate = subparsers.add_parser("candidate-run")
    candidate.add_argument("--candidate-patch", required=True)
    candidate.add_argument("--expected-patch-sha256", required=True)
    candidate.add_argument("--expected-tree-sha256", required=True)
    candidate.add_argument("--source-path", action="append", required=True)
    candidate.add_argument("--f2p-command", action="append", required=True)
    candidate.add_argument("--visible-node", action="append", required=True)
    candidate.add_argument("--hidden-node", action="append", required=True)
    candidate.add_argument("--test-framework", choices=("pytest", "unittest"), default="pytest")
    candidate.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    if args.command == "environment-audit":
        value = environment_audit()
    elif args.command == "official-f2p":
        value = official_f2p(args.timeout)
    elif args.command == "collect":
        value = collect_nodes(
            args.test_framework,
            args.test_root,
            args.unittest_pattern,
            args.unittest_top_level_dir,
            args.timeout,
        )
    elif args.command == "run-nodes":
        value = run_nodes(args.node, args.test_framework, args.timeout)
    else:
        value = candidate_run(args)
    print(json.dumps(value, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"worker_error": type(error).__name__, "message": str(error)}, sort_keys=True))
        sys.exit(1)
