from __future__ import annotations

import argparse
import ast
import configparser
import json
import os
import shlex
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
COVERAGE_ADDOPTS = {
    "--cov",
    "--cov-report",
    "--cov-config",
    "--cov-context",
    "--cov-fail-under",
}
COVERAGE_FLAG_ADDOPTS = {
    "--cov-append",
    "--cov-branch",
    "--cov-reset",
}


PROJECT_LEVEL_SCOPE_TYPES = {"project_level_p2p_broad", "project_level_official_test_root"}


def is_project_level_path(test_path: str) -> bool:
    return test_path in {"", ".", "./"}


def is_project_level_scope(scope_type: str) -> bool:
    return scope_type in PROJECT_LEVEL_SCOPE_TYPES


def write_json(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def checkout_root(source_root: Path, task_id: str, version: str, project: str) -> Path:
    bug_dir = task_id.replace("bugsinpy_", "")
    return source_root / bug_dir / version / project


def discover_test_paths(checkout: Path) -> list[str]:
    ignored_parts = {
        ".git",
        ".tox",
        ".venv",
        "build",
        "dist",
        "__pycache__",
        "env",
        "venv",
    }
    paths: list[str] = []
    for path in checkout.rglob("*.py"):
        relative = path.relative_to(checkout)
        if any(part in ignored_parts for part in relative.parts):
            continue
        name = path.name
        if name.startswith("test") or name.endswith("_test.py") or name == "tests.py":
            paths.append(relative.as_posix())
    return sorted(set(paths))


def read_pytest_addopts(checkout: Path) -> dict[str, str]:
    candidates = [
        ("setup.cfg", "tool:pytest"),
        ("pytest.ini", "pytest"),
        ("tox.ini", "pytest"),
    ]
    for file_name, section in candidates:
        path = checkout / file_name
        if not path.exists():
            continue
        parser = configparser.ConfigParser()
        parser.read(path, encoding="utf-8")
        if parser.has_option(section, "addopts"):
            return {
                "config_source": file_name,
                "config_section": section,
                "original_addopts": parser.get(section, "addopts"),
            }
    return {"config_source": "", "config_section": "", "original_addopts": ""}


def sanitize_coverage_addopts(original_addopts: str) -> dict[str, Any]:
    tokens = shlex.split(original_addopts, posix=False)
    retained: list[str] = []
    removed: list[str] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        option = token.split("=", 1)[0]
        if option in COVERAGE_FLAG_ADDOPTS or any(token.startswith(f"{item}=") for item in COVERAGE_ADDOPTS):
            removed.append(token)
            index += 1
            continue
        if option in COVERAGE_ADDOPTS:
            removed.append(token)
            if index + 1 < len(tokens) and not tokens[index + 1].startswith("-"):
                removed.append(tokens[index + 1])
                index += 2
            else:
                index += 1
            continue
        retained.append(token)
        index += 1
    return {
        "removed_tokens": removed,
        "retained_tokens": retained,
        "sanitized_addopts": " ".join(shlex.quote(token) for token in retained),
    }


def build_addopts_override_audit(task_id: str, project: str, buggy: Path, fixed: Path, enabled: bool) -> dict[str, Any]:
    buggy_config = read_pytest_addopts(buggy)
    fixed_config = read_pytest_addopts(fixed)
    original_addopts = buggy_config["original_addopts"]
    if fixed_config["original_addopts"] and fixed_config["original_addopts"] != original_addopts:
        return {
            "enabled": enabled,
            "task_id": task_id,
            "project": project,
            "override_type": "coverage_only_addopts_sanitization",
            "allowed": False,
            "reason": "buggy and reference pytest addopts differ; refusing automatic sanitizer",
            "buggy": buggy_config,
            "reference": fixed_config,
        }
    sanitized = sanitize_coverage_addopts(original_addopts)
    return {
        "enabled": enabled,
        "task_id": task_id,
        "project": project,
        "override_type": "coverage_only_addopts_sanitization",
        "allowed": enabled and bool(sanitized["removed_tokens"]),
        "config_source": buggy_config["config_source"],
        "config_section": buggy_config["config_section"],
        "original_addopts": original_addopts,
        "removed_tokens": sanitized["removed_tokens"],
        "retained_tokens": sanitized["retained_tokens"],
        "sanitized_addopts": sanitized["sanitized_addopts"],
        "reason": "coverage-only pytest-cov options blocked collection before P2P scope construction",
        "pytest_cov_installed": False,
        "main_experiment_allowed": True,
    }


def pytest_command(python: str, pytest_args: list[str], addopts_override: str | None) -> list[str]:
    command = [python, "-m", "pytest"]
    if addopts_override is not None:
        command.extend(["-o", f"addopts={addopts_override}"])
    command.extend(pytest_args)
    return command


def build_compat_shim(out_dir: Path) -> Path:
    shim_dir = out_dir / "compat_shim"
    shim_dir.mkdir(parents=True, exist_ok=True)
    write_text(
        shim_dir / "sitecustomize.py",
        "\n".join(
            [
                "import builtins",
                "import inspect",
                "import asyncio",
                "import collections",
                "import collections.abc",
                "import sys",
                "import types",
                "import unittest.mock as _unittest_mock",
                "from collections import namedtuple",
                "if sys.platform.startswith('win') and hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):",
                "    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())",
                "if not hasattr(asyncio, 'coroutine'):",
                "    asyncio.coroutine = types.coroutine",
                "for _asyncio_name in ['Event', 'Lock', 'Condition', 'Semaphore', 'BoundedSemaphore', 'Queue']:",
                "    if hasattr(asyncio, _asyncio_name):",
                "        _asyncio_original = getattr(asyncio, _asyncio_name)",
                "        def _drop_loop_arg(*args, __original=_asyncio_original, **kwargs):",
                "            kwargs.pop('loop', None)",
                "            return __original(*args, **kwargs)",
                "        setattr(asyncio, _asyncio_name, _drop_loop_arg)",
                "sys.modules.setdefault('mock', _unittest_mock)",
                "if 'psutil' not in sys.modules:",
                "    _psutil = types.ModuleType('psutil')",
                "    class _Process:",
                "        def children(self):",
                "            return []",
                "    _psutil.Process = _Process",
                "    sys.modules['psutil'] = _psutil",
                "for _name in dir(collections.abc):",
                "    if not hasattr(collections, _name):",
                "        setattr(collections, _name, getattr(collections.abc, _name))",
                "if not hasattr(inspect, 'ArgSpec'):",
                "    inspect.ArgSpec = namedtuple('ArgSpec', 'args varargs keywords defaults')",
                "if not hasattr(inspect, 'getargspec'):",
                "    def _getargspec(func):",
                "        spec = inspect.getfullargspec(func)",
                "        return inspect.ArgSpec(spec.args, spec.varargs, spec.varkw, spec.defaults)",
                "    inspect.getargspec = _getargspec",
                "try:",
                "    import requests.compat",
                "    if not hasattr(requests.compat, 'is_py26'):",
                "        requests.compat.is_py26 = False",
                "    if not hasattr(requests.compat, 'is_py3'):",
                "        requests.compat.is_py3 = True",
                "    if not hasattr(requests.compat, 'is_windows'):",
                "        requests.compat.is_windows = sys.platform.startswith('win')",
                "    if not hasattr(requests.compat, 'str'):",
                "        requests.compat.str = builtins.str",
                "    if not hasattr(requests.compat, 'bytes'):",
                "        requests.compat.bytes = builtins.bytes",
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
    process: subprocess.Popen[str] | None = None
    try:
        process = subprocess.Popen(
            command,
            cwd=str(cwd),
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
        )
        stdout, stderr = process.communicate(timeout=timeout_seconds)
        return {
            "command": command,
            "exit_code": process.returncode,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "stdout": stdout,
            "stderr": stderr,
            "timeout": False,
        }
    except subprocess.TimeoutExpired as exc:
        if process is not None:
            kill_process_tree(process.pid)
            stdout, stderr = process.communicate()
        else:
            stdout = exc.stdout if isinstance(exc.stdout, str) else ""
            stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return {
            "command": command,
            "exit_code": None,
            "elapsed_seconds": timeout_seconds,
            "stdout": stdout,
            "stderr": stderr,
            "timeout": True,
        }


def kill_process_tree(pid: int) -> None:
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return
    subprocess.run(["pkill", "-TERM", "-P", str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def os_environ_with_pythonpath(pythonpath: Path) -> dict[str, str]:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(pythonpath.resolve()) if not existing else f"{pythonpath.resolve()}{os.pathsep}{existing}"
    return env


def normalize_nodeid(line: str, test_path: str) -> str | None:
    stripped = line.strip()
    if "::" not in stripped or ".py" not in stripped:
        return None
    normalized = stripped.replace("\\", "/")
    if is_project_level_path(test_path):
        prefix = normalized.split("::", 1)[0]
        if prefix.endswith(".py"):
            return normalized
        return None
    test_path_normalized = test_path.replace("\\", "/")
    marker = f"{test_path_normalized}::"
    if marker in normalized:
        return marker + normalized.split(marker, 1)[1]
    if normalized.startswith(test_path_normalized):
        return normalized
    return None


def normalize_project_nodeid(line: str, test_paths: list[str]) -> str | None:
    stripped = line.strip()
    if "::" not in stripped or ".py" not in stripped:
        return None
    normalized = stripped.replace("\\", "/")
    for test_path in sorted(test_paths, key=len, reverse=True):
        marker = f"{test_path}::"
        if marker in normalized:
            return marker + normalized.split(marker, 1)[1]
    return None


def parse_pytest_collect_tree(stdout: str, test_path: str) -> list[str]:
    nodeids: list[str] = []
    class_stack: list[tuple[int, str]] = []
    for line in stdout.splitlines():
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))
        if stripped.startswith("<Class ") and stripped.endswith(">"):
            class_name = stripped.removeprefix("<Class ").removesuffix(">")
            class_stack = [(level, value) for level, value in class_stack if level < indent]
            class_stack.append((indent, class_name))
            continue
        if stripped.startswith("<Module ") or stripped.startswith("<Package ") or stripped.startswith("<Dir "):
            if stripped.startswith("<Module "):
                class_stack = []
            continue
        if not stripped.startswith("<Function ") or not stripped.endswith(">"):
            continue
        function_name = stripped.removeprefix("<Function ").removesuffix(">")
        class_parts = [value for _, value in class_stack if value]
        nodeids.append("::".join([test_path, *class_parts, function_name]))
    return nodeids


def normalize_parametrized_nodeid(nodeid: str) -> str:
    return "::".join(part.split("[", 1)[0] for part in nodeid.split("::"))


def collect_tests(
    python: str,
    checkout: Path,
    test_paths: list[str],
    timeout_seconds: int,
    pythonpath: Path,
    project_level: bool,
    addopts_override: str | None = None,
) -> tuple[list[str], dict[str, Any]]:
    result = run_command(
        pytest_command(python, ["--collect-only", "-q", *test_paths], addopts_override),
        cwd=checkout,
        timeout_seconds=timeout_seconds,
        pythonpath=pythonpath,
    )
    tests = []
    for line in result["stdout"].splitlines():
        nodeid = normalize_project_nodeid(line, test_paths) if project_level else normalize_nodeid(line, test_paths[0])
        if nodeid:
            tests.append(nodeid)
    if not tests and len(test_paths) == 1:
        tests = parse_pytest_collect_tree(result["stdout"], test_paths[0])
    return sorted(set(tests)), compact_result(result)


def collect_tests_by_file(
    python: str,
    checkout: Path,
    test_paths: list[str],
    timeout_seconds: int,
    pythonpath: Path,
    addopts_override: str | None = None,
) -> tuple[list[str], dict[str, Any]]:
    tests: list[str] = []
    files: list[dict[str, Any]] = []
    for test_path in test_paths:
        result = run_command(
            pytest_command(python, ["--collect-only", "-q", test_path], addopts_override),
            cwd=checkout,
            timeout_seconds=timeout_seconds,
            pythonpath=pythonpath,
        )
        nodeids = []
        for line in result["stdout"].splitlines():
            nodeid = normalize_project_nodeid(line, [test_path])
            if nodeid:
                nodeids.append(nodeid)
        if not nodeids:
            nodeids = parse_pytest_collect_tree(result["stdout"], test_path)
        compact = compact_result(result)
        compact["test_path"] = test_path
        compact["collected_count"] = len(nodeids)
        compact["collection_error"] = result["exit_code"] not in {0, 5}
        files.append(compact)
        tests.extend(nodeids)
    summary = {
        "command": pytest_command(python, ["--collect-only", "-q", "<per-file>"], addopts_override),
        "exit_code": 0 if all(not item["collection_error"] for item in files) else 2,
        "elapsed_seconds": round(sum(float(item.get("elapsed_seconds") or 0.0) for item in files), 3),
        "timeout": any(bool(item.get("timeout")) for item in files),
        "stdout_tail": "",
        "stderr_tail": "",
        "collection_mode": "per_file",
        "test_file_count": len(test_paths),
        "collection_error_files": [
            item["test_path"] for item in files if item["collection_error"]
        ],
        "collection_error_count": sum(1 for item in files if item["collection_error"]),
        "files": files,
    }
    return sorted(set(tests)), summary


UNITTEST_DISCOVERY_SNIPPET = r"""
import argparse
import json
import os
import sys
import traceback
import unittest
from pathlib import Path


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-dir", required=True)
    parser.add_argument("--pattern", required=True)
    parser.add_argument("--top-level-dir", default="")
    args = parser.parse_args()
    loader = unittest.TestLoader()
    try:
        kwargs = {"start_dir": args.start_dir, "pattern": args.pattern}
        if args.top_level_dir:
            kwargs["top_level_dir"] = args.top_level_dir
        suite = loader.discover(**kwargs)
        tests = []
        errors = []
        for test_case in flatten(suite):
            test = test_case.id()
            if test.startswith("unittest.loader._FailedTest"):
                exception = getattr(test_case, "_exception", None)
                traceback_excerpt = (
                    "".join(traceback.format_exception(exception))[-2000:]
                    if exception is not None
                    else test
                )
                errors.append(
                    {
                        "module_or_path": test,
                        "error_type": type(exception).__name__ if exception is not None else "UnittestFailedImport",
                        "message": str(exception) if exception is not None else "unittest discovery produced _FailedTest",
                        "traceback_excerpt": traceback_excerpt,
                    }
                )
            else:
                tests.append(test)
        print(json.dumps({"tests": sorted(set(tests)), "errors": errors}, sort_keys=True))
    except Exception as exc:
        print(
            json.dumps(
                {
                    "tests": [],
                    "errors": [
                        {
                            "module_or_path": args.start_dir,
                            "error_type": type(exc).__name__,
                            "message": str(exc),
                            "traceback_excerpt": traceback.format_exc()[-2000:],
                        }
                    ],
                },
                sort_keys=True,
            )
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
"""


def collect_unittest_tests(
    python: str,
    checkout: Path,
    start_dir: str,
    pattern: str,
    top_level_dir: str,
    timeout_seconds: int,
    pythonpath: Path,
) -> tuple[list[str], dict[str, Any]]:
    result = run_command(
        [
            python,
            "-c",
            UNITTEST_DISCOVERY_SNIPPET,
            "--start-dir",
            start_dir,
            "--pattern",
            pattern,
            "--top-level-dir",
            top_level_dir,
        ],
        cwd=checkout,
        timeout_seconds=timeout_seconds,
        pythonpath=pythonpath,
    )
    tests: list[str] = []
    errors: list[dict[str, Any]] = []
    if result["stdout"].strip():
        last_line = result["stdout"].strip().splitlines()[-1]
        try:
            payload = json.loads(last_line)
            if isinstance(payload, dict):
                tests = sorted(str(test) for test in payload.get("tests", []) if isinstance(test, str))
                errors = [error for error in payload.get("errors", []) if isinstance(error, dict)]
        except json.JSONDecodeError:
            errors = [
                {
                    "module_or_path": start_dir,
                    "error_type": "DiscoveryOutputParseError",
                    "message": "unittest discovery did not emit JSON",
                    "traceback_excerpt": tail(result["stdout"] + "\n" + result["stderr"]),
                }
            ]
    elif result["exit_code"] != 0:
        errors = [
            {
                "module_or_path": start_dir,
                "error_type": "DiscoveryProcessError",
                "message": f"unittest discovery exited with {result['exit_code']}",
                "traceback_excerpt": tail(result["stdout"] + "\n" + result["stderr"]),
            }
        ]
    summary = compact_result(result)
    summary.update(
        {
            "collection_mode": "unittest_discovery",
            "start_dir": start_dir,
            "pattern": pattern,
            "top_level_dir": top_level_dir,
            "collection_error_count": len(errors),
            "collection_error_files": [str(error.get("module_or_path")) for error in errors],
            "errors": errors,
            "collected_count": len(tests),
        }
    )
    return tests, summary


def static_source_segments(checkout: Path, test_path: str, nodeids: list[str]) -> dict[str, str]:
    methods: dict[str, str] = {}
    file_paths = sorted({nodeid.split("::", 1)[0] for nodeid in nodeids if "::" in nodeid})
    if not is_project_level_path(test_path) and not (checkout / test_path).is_dir():
        file_paths = [test_path]

    for relative_file in file_paths:
        test_file = checkout / relative_file
        if not test_file.exists():
            continue
        source = test_file.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for class_node in [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]:
            for child in class_node.body:
                if isinstance(child, ast.FunctionDef) and child.name.startswith("test_"):
                    segment = ast.get_source_segment(source, child) or ""
                    methods[f"{relative_file}::{class_node.name}::{child.name}"] = segment
        for child in tree.body:
            if isinstance(child, ast.FunctionDef) and child.name.startswith("test_"):
                segment = ast.get_source_segment(source, child) or ""
                methods[f"{relative_file}::{child.name}"] = segment
    return {nodeid: methods.get(nodeid, methods.get(normalize_parametrized_nodeid(nodeid), "")) for nodeid in nodeids}


def static_external_dependency_reasons(segments: dict[str, str], tokens: list[str]) -> dict[str, str]:
    if not tokens:
        return {}
    reasons: dict[str, str] = {}
    lowered_tokens = [token.lower() for token in tokens]
    for nodeid, segment_text in segments.items():
        segment = segment_text.lower()
        if any(token in segment for token in lowered_tokens):
            reasons[nodeid] = "excluded_static_external_dependency"
    return reasons


def static_include_reasons(segments: dict[str, str], tokens: list[str]) -> dict[str, str]:
    if not tokens:
        return {}
    lowered_tokens = [token.lower() for token in tokens]
    reasons: dict[str, str] = {}
    for nodeid, segment_text in segments.items():
        segment = segment_text.lower()
        if not any(token in segment for token in lowered_tokens):
            reasons[nodeid] = "excluded_static_include_filter"
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
    test_framework: str = "pytest",
    addopts_override: str | None = None,
) -> list[dict[str, Any]]:
    results = []
    for run_index in range(1, runs + 1):
        command = (
            [python, "-m", "unittest", nodeid]
            if test_framework == "unittest"
            else pytest_command(python, ["-q", nodeid], addopts_override)
        )
        result = run_command(
            command,
            cwd=checkout,
            timeout_seconds=timeout_seconds,
            pythonpath=pythonpath,
        )
        compact = compact_result(result)
        compact["run_index"] = run_index
        compact["passed"] = result["exit_code"] == 0
        results.append(compact)
    return results


def run_batch_repeated(
    python: str,
    checkout: Path,
    nodeids: list[str],
    runs: int,
    timeout_seconds: int,
    pythonpath: Path,
    test_framework: str = "pytest",
    addopts_override: str | None = None,
) -> list[dict[str, Any]]:
    results = []
    for run_index in range(1, runs + 1):
        command = (
            [python, "-m", "unittest", *nodeids]
            if test_framework == "unittest"
            else pytest_command(python, ["-q", *nodeids], addopts_override)
        )
        result = run_command(
            command,
            cwd=checkout,
            timeout_seconds=timeout_seconds,
            pythonpath=pythonpath,
        )
        compact = compact_result(result)
        compact["run_index"] = run_index
        compact["passed"] = result["exit_code"] == 0
        compact["nodeid_count"] = len(nodeids)
        results.append(compact)
    return results


def chunks(values: list[Any], chunk_size: int) -> list[list[Any]]:
    return [values[index : index + chunk_size] for index in range(0, len(values), chunk_size)]


def batch_record_groups(records: list[dict[str, Any]], batch_size: int, group_by_file: bool) -> list[list[dict[str, Any]]]:
    if not group_by_file:
        return chunks(records, batch_size)

    by_file: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        nodeid = str(record["nodeid"])
        file_path = nodeid.split("::", 1)[0] if "::" in nodeid else ".".join(nodeid.split(".")[:2])
        by_file.setdefault(file_path, []).append(record)

    groups: list[list[dict[str, Any]]] = []
    for file_path in sorted(by_file):
        groups.extend(chunks(by_file[file_path], batch_size))
    return groups


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
        f"- scope type: {scope['scope_type']}",
        f"- test path: {scope['test_path']}",
        f"- stability runs per version: {scope['runs_per_version']}",
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


def build_collection_error_manifest(scope: dict[str, Any]) -> dict[str, Any]:
    errors = []
    for side in ["buggy", "reference"]:
        collection = scope.get("collection", {}).get(side, {})
        for error in collection.get("errors", []):
            if isinstance(error, dict):
                item = dict(error)
                item["version"] = side
                errors.append(item)
        for file_record in collection.get("files", []):
            if isinstance(file_record, dict) and file_record.get("collection_error"):
                errors.append(
                    {
                        "version": side,
                        "module_or_path": file_record.get("test_path"),
                        "error_type": "CollectionError",
                        "message": f"collection exited with {file_record.get('exit_code')}",
                        "traceback_excerpt": str(file_record.get("stdout_tail", ""))
                        + "\n"
                        + str(file_record.get("stderr_tail", "")),
                    }
                )
    return {
        "task_id": scope["task_id"],
        "project": scope["project"],
        "scope_type": scope["scope_type"],
        "test_framework": scope.get("test_framework"),
        "error_count": len(errors),
        "errors": errors,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build pass-to-pass stable test scopes for a BugsInPy task.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--test-path", default="tests/tests.py")
    parser.add_argument("--test-framework", choices=["pytest", "unittest"], default="pytest")
    parser.add_argument("--unittest-start-dir", default="tests")
    parser.add_argument("--unittest-pattern", default="test*.py")
    parser.add_argument("--unittest-top-level-dir", default=".")
    parser.add_argument("--source-workspace-root", default=str(DEFAULT_SOURCE_ROOT))
    parser.add_argument("--fail-to-pass-nodeid", action="append", default=[])
    parser.add_argument("--core-pattern", action="append", default=[])
    parser.add_argument("--runs", type=int, default=2)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--batch-timeout-seconds", type=int, default=120)
    parser.add_argument("--batch-size", type=int, default=50)
    parser.add_argument("--batch-group-by-file", action="store_true")
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--manifest-out")
    parser.add_argument(
        "--scope-type",
        choices=["project_level_p2p_broad", "project_level_official_test_root", "task_file_p2p_broad"],
    )
    parser.add_argument(
        "--scope-policy-name",
        default="",
        help="Optional policy identifier recorded in the manifest for scoped project-level discovery.",
    )
    parser.add_argument(
        "--scope-policy-reason",
        default="",
        help="Optional policy reason recorded in the manifest for scoped project-level discovery.",
    )
    parser.add_argument(
        "--full-repo-discovery-attempts",
        type=int,
        default=0,
        help="Number of prior full-repository discovery attempts to record in the manifest.",
    )
    parser.add_argument(
        "--full-repo-discovery-status",
        default="",
        help="Prior full-repository discovery status to record in the manifest.",
    )
    parser.add_argument(
        "--static-exclude-token",
        action="append",
        default=["httpbin", "http://", "https://"],
        help="Exclude test methods whose source contains this token before dynamic runs. Repeatable.",
    )
    parser.add_argument(
        "--static-include-token",
        action="append",
        default=[],
        help="If provided, only dynamically run test methods whose source contains at least one token. Repeatable.",
    )
    parser.add_argument(
        "--batch-first",
        action="store_true",
        help="Validate candidate P2P tests in batches first; fall back to per-test runs only if the batch fails.",
    )
    parser.add_argument(
        "--sanitize-coverage-addopts",
        action="store_true",
        help=(
            "Override pytest addopts after removing coverage-only pytest-cov options. "
            "Writes the original, removed, retained, and sanitized tokens into the scope manifest."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and print a no-run plan without creating output directories, shims, or manifests.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    source_root = Path(args.source_workspace_root)
    buggy = checkout_root(source_root, args.task_id, "buggy", args.project)
    fixed = checkout_root(source_root, args.task_id, "fixed", args.project)
    if not buggy.exists():
        raise FileNotFoundError(f"missing buggy checkout: {buggy}")
    if not fixed.exists():
        raise FileNotFoundError(f"missing fixed checkout: {fixed}")

    addopts_audit = build_addopts_override_audit(
        task_id=args.task_id,
        project=args.project,
        buggy=buggy,
        fixed=fixed,
        enabled=args.sanitize_coverage_addopts,
    )
    if args.sanitize_coverage_addopts and not addopts_audit.get("allowed"):
        raise ValueError(f"coverage addopts sanitizer is not allowed: {addopts_audit}")
    addopts_override = (
        str(addopts_audit["sanitized_addopts"]) if args.sanitize_coverage_addopts and addopts_audit.get("allowed") else None
    )

    fail_to_pass = set(args.fail_to_pass_nodeid or DEFAULT_FAIL_TO_PASS.get(args.task_id, []))
    core_patterns = args.core_pattern or DEFAULT_CORE_PATTERNS.get(args.task_id, [])

    scope_type = args.scope_type
    if scope_type is None:
        scope_type = "project_level_p2p_broad" if is_project_level_path(args.test_path) else "task_file_p2p_broad"

    if is_project_level_scope(scope_type) and args.test_framework == "pytest":
        buggy_test_paths = discover_test_paths(buggy)
        fixed_test_paths = discover_test_paths(fixed)
        common_test_paths = sorted(set(buggy_test_paths) & set(fixed_test_paths))
        if scope_type == "project_level_official_test_root":
            root = args.test_path.strip("/\\")
            prefix = f"{root}/" if root else ""
            test_paths = [path for path in common_test_paths if path == root or path.startswith(prefix)]
        else:
            test_paths = common_test_paths
        if not test_paths:
            raise ValueError(f"no common test files discovered for project-level scope: {args.task_id}")
    elif is_project_level_scope(scope_type):
        test_paths = [args.unittest_start_dir]
    else:
        test_paths = [args.test_path]

    if args.dry_run:
        dry_run_record = {
            "mode": "p2p_scope_builder_dry_run",
            "task_id": args.task_id,
            "project": args.project,
            "scope_type": scope_type,
            "test_framework": args.test_framework,
            "source_workspace_root": str(source_root),
            "buggy_checkout": str(buggy),
            "fixed_checkout": str(fixed),
            "buggy_checkout_exists": buggy.exists(),
            "fixed_checkout_exists": fixed.exists(),
            "test_paths": test_paths,
            "fail_to_pass_nodeids": sorted(fail_to_pass),
            "core_patterns": core_patterns,
            "runs": args.runs,
            "timeout_seconds": args.timeout_seconds,
            "batch_timeout_seconds": args.batch_timeout_seconds,
            "batch_size": args.batch_size,
            "batch_first": args.batch_first,
            "static_exclude_tokens": args.static_exclude_token,
            "static_include_tokens": args.static_include_token,
            "out_dir": str(out_dir),
            "out_dir_exists": out_dir.exists(),
            "manifest_out": args.manifest_out,
            "manifest_out_exists": Path(args.manifest_out).exists() if args.manifest_out else False,
            "will_execute_tests": False,
            "will_create_output_dir": False,
            "will_create_compat_shim": False,
            "will_write_manifest": False,
            "pytest_addopts_override": addopts_audit,
        }
        print(json.dumps(dry_run_record, ensure_ascii=False, indent=2, sort_keys=True))
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    shim_dir = build_compat_shim(out_dir)

    if args.test_framework == "unittest":
        buggy_tests, buggy_collect = collect_unittest_tests(
            args.python,
            buggy,
            args.unittest_start_dir,
            args.unittest_pattern,
            args.unittest_top_level_dir,
            args.timeout_seconds,
            shim_dir,
        )
        fixed_tests, fixed_collect = collect_unittest_tests(
            args.python,
            fixed,
            args.unittest_start_dir,
            args.unittest_pattern,
            args.unittest_top_level_dir,
            args.timeout_seconds,
            shim_dir,
        )
    elif is_project_level_scope(scope_type):
        buggy_tests, buggy_collect = collect_tests_by_file(
            args.python,
            buggy,
            test_paths,
            args.timeout_seconds,
            shim_dir,
            addopts_override=addopts_override,
        )
        fixed_tests, fixed_collect = collect_tests_by_file(
            args.python,
            fixed,
            test_paths,
            args.timeout_seconds,
            shim_dir,
            addopts_override=addopts_override,
        )
    else:
        buggy_tests, buggy_collect = collect_tests(
            args.python,
            buggy,
            test_paths,
            args.timeout_seconds,
            shim_dir,
            project_level=False,
            addopts_override=addopts_override,
        )
        fixed_tests, fixed_collect = collect_tests(
            args.python,
            fixed,
            test_paths,
            args.timeout_seconds,
            shim_dir,
            project_level=False,
            addopts_override=addopts_override,
        )
    collected = sorted(set(buggy_tests) & set(fixed_tests))
    all_seen = sorted(set(buggy_tests) | set(fixed_tests))
    source_segments = static_source_segments(buggy, args.test_path, all_seen)
    static_exclusions = static_external_dependency_reasons(source_segments, args.static_exclude_token)
    static_include_exclusions = static_include_reasons(source_segments, args.static_include_token)
    records = []
    p2p_broad = []
    exclusions = []
    pending_dynamic: list[dict[str, Any]] = []

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
        if nodeid in static_include_exclusions:
            reason = static_include_exclusions[nodeid]
            record["exclusion_reason"] = reason
            record["static_include_tokens"] = args.static_include_token
            records.append(record)
            exclusions.append({"nodeid": nodeid, "reason": reason})
            continue
        pending_dynamic.append(record)

    batch_runs: dict[str, Any] | None = None
    if args.batch_first and pending_dynamic:
        still_pending: list[dict[str, Any]] = []
        batch_runs = {"chunks": []}
        for chunk_records in batch_record_groups(pending_dynamic, args.batch_size, args.batch_group_by_file):
            batch_nodeids = [record["nodeid"] for record in chunk_records]
            buggy_batch = run_batch_repeated(
                args.python,
                buggy,
                batch_nodeids,
                args.runs,
                args.batch_timeout_seconds,
                shim_dir,
                test_framework=args.test_framework,
                addopts_override=addopts_override,
            )
            fixed_batch = run_batch_repeated(
                args.python,
                fixed,
                batch_nodeids,
                args.runs,
                args.batch_timeout_seconds,
                shim_dir,
                test_framework=args.test_framework,
                addopts_override=addopts_override,
            )
            chunk_record = {
                "nodeid_count": len(batch_nodeids),
                "buggy_runs": buggy_batch,
                "reference_runs": fixed_batch,
                "passed": all(run["passed"] for run in buggy_batch + fixed_batch),
            }
            batch_runs["chunks"].append(chunk_record)
            if not chunk_record["passed"]:
                still_pending.extend(chunk_records)
                continue
            for record in chunk_records:
                record["exclusion_reason"] = None
                record["batch_validated"] = True
                records.append(record)
                p2p_broad.append(record["nodeid"])
        pending_dynamic = still_pending

    for record in pending_dynamic:
        nodeid = record["nodeid"]
        buggy_runs = run_test_repeated(
            args.python,
            buggy,
            nodeid,
            args.runs,
            args.timeout_seconds,
            shim_dir,
            test_framework=args.test_framework,
            addopts_override=addopts_override,
        )
        fixed_runs = run_test_repeated(
            args.python,
            fixed,
            nodeid,
            args.runs,
            args.timeout_seconds,
            shim_dir,
            test_framework=args.test_framework,
            addopts_override=addopts_override,
        )
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
        "scope_id": f"{args.task_id}_{scope_type}",
        "scope_type": scope_type,
        "p2p_scope_type": scope_type,
        "p2p_scope_roots": [args.test_path.rstrip("/\\") + "/"]
        if scope_type == "project_level_official_test_root"
        else [],
        "full_repo_discovery": {
            "attempted": args.full_repo_discovery_attempts > 0 or bool(args.full_repo_discovery_status),
            "attempts": args.full_repo_discovery_attempts,
            "status": args.full_repo_discovery_status,
            "manifest_generated": False if args.full_repo_discovery_status == "timeout" else None,
        },
        "scope_policy": {
            "policy_name": args.scope_policy_name,
            "reason": args.scope_policy_reason,
            "is_task_file_level": False if is_project_level_scope(scope_type) else True,
            "is_project_official_test_root": scope_type == "project_level_official_test_root",
        },
        "main_experiment_eligibility": {
            "requires_p2p_broad_size_at_least": 3,
            "requires_stability_runs": 3,
            "no_test_fixture_shim": True,
        },
        "test_framework": args.test_framework,
        "task_id": args.task_id,
        "project": args.project,
        "test_path": args.test_path,
        "test_paths": test_paths,
        "unittest_discovery": {
            "start_dir": args.unittest_start_dir,
            "pattern": args.unittest_pattern,
            "top_level_dir": args.unittest_top_level_dir,
        }
        if args.test_framework == "unittest"
        else None,
        "runs_per_version": args.runs,
        "stability_runs": args.runs,
        "buggy_baseline_pass_required": True,
        "reference_patch_pass_required": True,
        "timeout_seconds": args.timeout_seconds,
        "compat_shim": {
            "enabled": True,
            "path": str(shim_dir),
            "reason": (
                "restore legacy Python APIs removed in the current Python environment, "
                "including collections aliases, inspect.getargspec, requests.compat constants, "
                "and asyncio loop/coroutine compatibility"
            ),
        },
        "pytest_addopts_override": addopts_audit,
        "collection": {
            "buggy": buggy_collect,
            "reference": fixed_collect,
            "discovered_test_files": len(test_paths),
            "buggy_collected_count": len(buggy_tests),
            "reference_collected_count": len(fixed_tests),
        },
        "fail_to_pass_nodeids": sorted(fail_to_pass),
        "core_patterns": core_patterns,
        "static_exclude_tokens": args.static_exclude_token,
        "static_include_tokens": args.static_include_token,
        "p2p_broad_tests": p2p_broad,
        "p2p_core_tests": p2p_core,
        "exclusions": exclusions,
        "records": records,
        "batch_runs": batch_runs,
        "counts": {
            "collected_tests": len(all_seen),
            "common_collected_tests": len(collected),
            "excluded_fail_to_pass_oracle": exclusion_counts.get("excluded_fail_to_pass_oracle", 0),
            "excluded_uncollectable": exclusion_counts.get("excluded_collection_mismatch", 0),
            "collection_error_files": max(
                int(buggy_collect.get("collection_error_count") or 0),
                int(fixed_collect.get("collection_error_count") or 0),
            ),
            "excluded_external_dependency": sum(
                count
                for reason, count in exclusion_counts.items()
                if "external_dependency" in reason or "network" in reason
            ),
            "excluded_timeout": exclusion_counts.get("excluded_timeout", 0),
            "excluded_flaky": exclusion_counts.get("excluded_unstable", 0),
            "included_p2p_tests": len(p2p_broad),
            "p2p_broad_tests": len(p2p_broad),
            "p2p_core_tests": len(p2p_core),
            "exclusion_reason_counts": dict(sorted(exclusion_counts.items())),
        },
    }
    write_json(out_dir / "p2p_scope.json", scope)
    write_text(out_dir / "p2p_scope.md", render_markdown(scope))
    collection_error_manifest = build_collection_error_manifest(scope)
    collection_error_path = (
        Path(args.manifest_out).with_name(f"{Path(args.manifest_out).stem}_collection_errors.json")
        if args.manifest_out
        else out_dir / "collection_error_manifest.json"
    )
    if collection_error_manifest["error_count"] or collection_error_path.exists():
        write_json(collection_error_path, collection_error_manifest)
        scope["collection_error_manifest"] = str(collection_error_path)
        write_json(out_dir / "p2p_scope.json", scope)
        if args.manifest_out:
            write_json(Path(args.manifest_out), scope)
    if addopts_audit.get("enabled"):
        addopts_audit_path = (
            Path(args.manifest_out).with_name(f"{Path(args.manifest_out).stem}_addopts_override_audit.json")
            if args.manifest_out
            else out_dir / "addopts_override_audit.json"
        )
        write_json(addopts_audit_path, addopts_audit)
        scope["pytest_addopts_override"]["audit_manifest"] = str(addopts_audit_path)
        write_json(out_dir / "p2p_scope.json", scope)
        if args.manifest_out:
            write_json(Path(args.manifest_out), scope)
    if args.manifest_out:
        write_json(Path(args.manifest_out), scope)
    print(json.dumps(scope["counts"], ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
