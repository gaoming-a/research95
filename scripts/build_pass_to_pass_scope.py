from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_SOURCE_ROOT = Path("..") / "research" / "data" / "real_bugs" / "bugsinpy_workspace"
DEFAULT_FAIL_TO_PASS = {
    "bugsinpy_httpie_5": ["tests/tests.py::TestItemParsing::test_escape_longsep"],
}
DEFAULT_CORE_PATTERNS = {
    "bugsinpy_httpie_5": ["tests/tests.py::TestItemParsing::"],
}


def write_json(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def checkout_root(source_root: Path, task_id: str, version: str, project: str) -> Path:
    bug_dir = task_id.replace("bugsinpy_", "")
    return source_root / bug_dir / version / project


def build_compat_shim(out_dir: Path) -> Path:
    shim_dir = out_dir / "compat_shim"
    shim_dir.mkdir(parents=True, exist_ok=True)
    write_text(
        shim_dir / "sitecustomize.py",
        "\n".join(
            [
                "import builtins",
                "try:",
                "    import requests.compat",
                "    if not hasattr(requests.compat, 'is_py26'):",
                "        requests.compat.is_py26 = False",
                "    if not hasattr(requests.compat, 'str'):",
                "        requests.compat.str = builtins.str",
                "except Exception:",
                "    pass",
                "",
            ]
        ),
    )
    return shim_dir


def run_command(
    command: list[str],
    cwd: Path,
    timeout_seconds: int,
    pythonpath: Path,
) -> dict[str, Any]:
    env = dict(**os_environ_with_pythonpath(pythonpath))
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
        )
        return {
            "command": command,
            "exit_code": completed.returncode,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "timeout": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "exit_code": None,
            "elapsed_seconds": timeout_seconds,
            "stdout": exc.stdout if isinstance(exc.stdout, str) else "",
            "stderr": exc.stderr if isinstance(exc.stderr, str) else "",
            "timeout": True,
        }


def os_environ_with_pythonpath(pythonpath: Path) -> dict[str, str]:
    import os

    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(pythonpath.resolve()) if not existing else f"{pythonpath.resolve()}{os.pathsep}{existing}"
    return env


def normalize_nodeid(line: str, test_path: str) -> str | None:
    stripped = line.strip()
    if "::" not in stripped or ".py" not in stripped:
        return None
    normalized = stripped.replace("\\", "/")
    test_path_normalized = test_path.replace("\\", "/")
    marker = f"{test_path_normalized}::"
    if marker in normalized:
        return marker + normalized.split(marker, 1)[1]
    if normalized.startswith(test_path_normalized):
        return normalized
    return None


def collect_tests(
    python: str,
    checkout: Path,
    test_path: str,
    timeout_seconds: int,
    pythonpath: Path,
) -> tuple[list[str], dict[str, Any]]:
    result = run_command(
        [python, "-m", "pytest", "--collect-only", "-q", test_path],
        cwd=checkout,
        timeout_seconds=timeout_seconds,
        pythonpath=pythonpath,
    )
    tests = []
    if result["exit_code"] == 0:
        for line in result["stdout"].splitlines():
            nodeid = normalize_nodeid(line, test_path)
            if nodeid:
                tests.append(nodeid)
    return sorted(set(tests)), compact_result(result)


def static_external_dependency_reasons(checkout: Path, test_path: str, nodeids: list[str], tokens: list[str]) -> dict[str, str]:
    if not tokens:
        return {}
    test_file = checkout / test_path
    if not test_file.exists():
        return {}
    source = test_file.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(source)
    methods: dict[str, str] = {}
    for class_node in [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]:
        for child in class_node.body:
            if isinstance(child, ast.FunctionDef) and child.name.startswith("test_"):
                segment = ast.get_source_segment(source, child) or ""
                methods[f"{test_path}::{class_node.name}::{child.name}"] = segment
    reasons: dict[str, str] = {}
    lowered_tokens = [token.lower() for token in tokens]
    for nodeid in nodeids:
        segment = methods.get(nodeid, "").lower()
        if any(token in segment for token in lowered_tokens):
            reasons[nodeid] = "excluded_static_external_dependency"
    return reasons


def compact_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "command": result["command"],
        "exit_code": result["exit_code"],
        "elapsed_seconds": result["elapsed_seconds"],
        "timeout": result["timeout"],
        "stdout_tail": tail(result["stdout"]),
        "stderr_tail": tail(result["stderr"]),
    }


def tail(text: str, max_chars: int = 1200) -> str:
    return text[-max_chars:] if len(text) > max_chars else text


def run_test_repeated(
    python: str,
    checkout: Path,
    nodeid: str,
    runs: int,
    timeout_seconds: int,
    pythonpath: Path,
) -> list[dict[str, Any]]:
    results = []
    for run_index in range(1, runs + 1):
        result = run_command(
            [python, "-m", "pytest", "-q", nodeid],
            cwd=checkout,
            timeout_seconds=timeout_seconds,
            pythonpath=pythonpath,
        )
        compact = compact_result(result)
        compact["run_index"] = run_index
        compact["passed"] = result["exit_code"] == 0
        results.append(compact)
    return results


def classify_exclusion(nodeid: str, buggy_runs: list[dict[str, Any]], fixed_runs: list[dict[str, Any]]) -> str | None:
    all_runs = buggy_runs + fixed_runs
    if all(run["passed"] for run in all_runs):
        return None
    if any(run.get("timeout") for run in all_runs):
        return "excluded_timeout"
    text = "\n".join(str(run.get("stdout_tail", "")) + "\n" + str(run.get("stderr_tail", "")) for run in all_runs)
    lowered = text.lower()
    if any(token in lowered for token in ["httpbin", "connection", "network", "proxy", "timeout"]):
        return "excluded_external_dependency_or_network"
    if any(not run["passed"] for run in buggy_runs):
        return "excluded_failed_on_buggy_baseline"
    if any(not run["passed"] for run in fixed_runs):
        return "excluded_failed_on_reference_fixed"
    return "excluded_unstable"


def render_markdown(scope: dict[str, Any]) -> str:
    lines = [
        f"# {scope['task_id']} Pass-to-Pass Scope",
        "",
        "## Summary",
        "",
        f"- collected tests: {scope['counts']['collected_tests']}",
        f"- excluded fail-to-pass oracle: {scope['counts']['excluded_fail_to_pass_oracle']}",
        f"- P2P broad tests: {scope['counts']['p2p_broad_tests']}",
        f"- P2P core tests: {scope['counts']['p2p_core_tests']}",
        "",
        "## Exclusion Counts",
        "",
    ]
    for reason, count in scope["counts"]["exclusion_reason_counts"].items():
        lines.append(f"- {reason}: {count}")
    lines.extend(["", "## P2P Broad Tests", ""])
    lines.extend(f"- `{nodeid}`" for nodeid in scope["p2p_broad_tests"])
    lines.extend(["", "## P2P Core Tests", ""])
    lines.extend(f"- `{nodeid}`" for nodeid in scope["p2p_core_tests"])
    lines.extend(["", "## Boundary", ""])
    lines.append(
        "This scope is an empirical stable runnable subset for the current local environment. "
        "It excludes the retained fail-to-pass oracle and tests that fail, time out, or require unavailable external resources."
    )
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build pass-to-pass stable test scopes for a BugsInPy task.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--test-path", default="tests/tests.py")
    parser.add_argument("--source-workspace-root", default=str(DEFAULT_SOURCE_ROOT))
    parser.add_argument("--fail-to-pass-nodeid", action="append", default=[])
    parser.add_argument("--core-pattern", action="append", default=[])
    parser.add_argument("--runs", type=int, default=2)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument(
        "--static-exclude-token",
        action="append",
        default=["httpbin", "http://", "https://"],
        help="Exclude test methods whose source contains this token before dynamic runs. Repeatable.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    shim_dir = build_compat_shim(out_dir)
    source_root = Path(args.source_workspace_root)
    buggy = checkout_root(source_root, args.task_id, "buggy", args.project)
    fixed = checkout_root(source_root, args.task_id, "fixed", args.project)
    if not buggy.exists():
        raise FileNotFoundError(f"missing buggy checkout: {buggy}")
    if not fixed.exists():
        raise FileNotFoundError(f"missing fixed checkout: {fixed}")

    fail_to_pass = set(args.fail_to_pass_nodeid or DEFAULT_FAIL_TO_PASS.get(args.task_id, []))
    core_patterns = args.core_pattern or DEFAULT_CORE_PATTERNS.get(args.task_id, [])

    buggy_tests, buggy_collect = collect_tests(args.python, buggy, args.test_path, args.timeout_seconds, shim_dir)
    fixed_tests, fixed_collect = collect_tests(args.python, fixed, args.test_path, args.timeout_seconds, shim_dir)
    collected = sorted(set(buggy_tests) & set(fixed_tests))
    all_seen = sorted(set(buggy_tests) | set(fixed_tests))
    static_exclusions = static_external_dependency_reasons(buggy, args.test_path, all_seen, args.static_exclude_token)
    records = []
    p2p_broad = []
    exclusions = []

    for nodeid in all_seen:
        record: dict[str, Any] = {
            "nodeid": nodeid,
            "collected_on_buggy": nodeid in buggy_tests,
            "collected_on_reference": nodeid in fixed_tests,
            "is_fail_to_pass_oracle": nodeid in fail_to_pass,
            "is_core_candidate": any(pattern in nodeid for pattern in core_patterns),
        }
        if nodeid not in collected:
            reason = "excluded_collection_mismatch"
            record["exclusion_reason"] = reason
            records.append(record)
            exclusions.append({"nodeid": nodeid, "reason": reason})
            continue
        if nodeid in fail_to_pass:
            reason = "excluded_fail_to_pass_oracle"
            record["exclusion_reason"] = reason
            records.append(record)
            exclusions.append({"nodeid": nodeid, "reason": reason})
            continue
        if nodeid in static_exclusions:
            reason = static_exclusions[nodeid]
            record["exclusion_reason"] = reason
            record["static_exclude_tokens"] = args.static_exclude_token
            records.append(record)
            exclusions.append({"nodeid": nodeid, "reason": reason})
            continue
        buggy_runs = run_test_repeated(args.python, buggy, nodeid, args.runs, args.timeout_seconds, shim_dir)
        fixed_runs = run_test_repeated(args.python, fixed, nodeid, args.runs, args.timeout_seconds, shim_dir)
        record["buggy_runs"] = buggy_runs
        record["reference_runs"] = fixed_runs
        reason = classify_exclusion(nodeid, buggy_runs, fixed_runs)
        record["exclusion_reason"] = reason
        if reason:
            exclusions.append({"nodeid": nodeid, "reason": reason})
        else:
            p2p_broad.append(nodeid)
        records.append(record)

    p2p_core = [nodeid for nodeid in p2p_broad if any(pattern in nodeid for pattern in core_patterns)]
    exclusion_counts = Counter(item["reason"] for item in exclusions)
    scope = {
        "task_id": args.task_id,
        "project": args.project,
        "test_path": args.test_path,
        "runs_per_version": args.runs,
        "timeout_seconds": args.timeout_seconds,
        "compat_shim": {
            "enabled": True,
            "path": str(shim_dir),
            "reason": "legacy tests import requests.compat.is_py26, absent in the current Python environment",
        },
        "collection": {
            "buggy": buggy_collect,
            "reference": fixed_collect,
            "buggy_collected_count": len(buggy_tests),
            "reference_collected_count": len(fixed_tests),
        },
        "fail_to_pass_nodeids": sorted(fail_to_pass),
        "core_patterns": core_patterns,
        "static_exclude_tokens": args.static_exclude_token,
        "p2p_broad_tests": p2p_broad,
        "p2p_core_tests": p2p_core,
        "exclusions": exclusions,
        "records": records,
        "counts": {
            "collected_tests": len(all_seen),
            "common_collected_tests": len(collected),
            "excluded_fail_to_pass_oracle": exclusion_counts.get("excluded_fail_to_pass_oracle", 0),
            "p2p_broad_tests": len(p2p_broad),
            "p2p_core_tests": len(p2p_core),
            "exclusion_reason_counts": dict(sorted(exclusion_counts.items())),
        },
    }
    write_json(out_dir / "p2p_scope.json", scope)
    write_text(out_dir / "p2p_scope.md", render_markdown(scope))
    print(json.dumps(scope["counts"], ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
