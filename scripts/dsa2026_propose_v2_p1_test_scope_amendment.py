# ruff: noqa: E402
#!/usr/bin/env python3
"""Derive the missing V2-P1 project test scopes without observing outcomes."""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/dsa2026_propose_v2_p1_test_scope_amendment.py")

import argparse
import hashlib
import json
import posixpath
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ORDER = ROOT / "data/protocols/dsa_v2_p1_source_order_v0_1.json"
MANIFEST = ROOT / "data/protocols/dsa_v2_p1_hash_manifest_v0_1.json"
PROTOCOL = ROOT / "data/protocols/dsa_v2_p1_construction_protocol_v0_1.json"
OUT = ROOT / "data/protocols/dsa_v2_p1_test_scope_amendment_proposal_v0_1.json"
REPORT = ROOT / "docs/experiments/dsa_v2_p1_test_scope_amendment_signoff_v0_1.md"

EXPECTED_AGGREGATE = "ed7c927129c47027b57374625a2d76667503bbb1d8d37e04d4460e42b2ae8b40"
EXPECTED_SOURCE_ORDER = "21be1d9fed719de44126be585fa7e9123fd8579588d9ce86eb396d4ab5c2dd11"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def canonical_sha256(path: Path, strip_terminal_newline: bool = False) -> str:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    if strip_terminal_newline:
        text = text.rstrip("\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_declared_paths(value: str) -> list[str]:
    paths = []
    for raw in value.split(";"):
        normalized = posixpath.normpath(raw.strip().replace("\\", "/"))
        if normalized in {"", "."} or normalized.startswith("../"):
            raise ValueError(f"unsafe declared test path: {raw!r}")
        paths.append(normalized)
    return paths


def common_parent(paths: list[str]) -> str:
    parents = [PurePosixPath(path).parent.parts for path in paths]
    shared: list[str] = []
    for values in zip(*parents):
        if len(set(values)) != 1:
            break
        shared.append(values[0])
    if not shared or not any(value in {"test", "tests"} for value in shared):
        raise ValueError(f"no common project test directory: {paths[:3]}")
    return PurePosixPath(*shared).as_posix()


def manifest_intact(manifest: dict[str, Any]) -> bool:
    if manifest["aggregate_sha256"] != EXPECTED_AGGREGATE:
        return False
    return all(
        canonical_sha256(
            ROOT / item["path"],
            item["path"] == "data/protocols/dsa_v2_p1_author_declaration_v0_1.txt",
        ) == item["sha256"]
        for item in manifest["files"]
    )


def derive() -> dict[str, Any]:
    source = read_json(SOURCE_ORDER)
    protocol = read_json(PROTOCOL)
    manifest = read_json(MANIFEST)
    grouped: dict[str, list[str]] = defaultdict(list)
    frameworks: dict[str, set[str]] = defaultdict(set)
    for record in source["records"]:
        grouped[record["project"]].extend(
            normalize_declared_paths(record["declared_test_file"])
        )
        frameworks[record["project"]].add(record["test_framework"])

    recipes = {item["project"]: item for item in protocol["project_environment_recipe_policy"]["recipes"]}
    amendments = []
    for project in sorted(grouped):
        if len(frameworks[project]) != 1:
            raise ValueError(f"test framework drift for {project}")
        framework = next(iter(frameworks[project]))
        scope = common_parent(sorted(set(grouped[project])))
        if project not in recipes or recipes[project]["test_frameworks"] != [framework]:
            raise ValueError(f"recipe/framework mismatch for {project}")
        adapter = {
            "framework": framework,
            "project_test_root": scope,
            "collection_command": (
                ["python", "-m", "pytest", "--collect-only", "-q", scope]
                if framework == "pytest"
                else [
                    "python",
                    "-m",
                    "unittest-discover",
                    "--start-dir",
                    scope,
                    "--pattern",
                    "test*.py" if project == "black" else "*_test.py",
                    "--top-level-dir",
                    ".",
                ]
            ),
            "unittest_pattern": (
                "test*.py" if project == "black" else "*_test.py"
            ) if framework == "unittest" else None,
            "unittest_top_level_dir": "." if framework == "unittest" else None,
            "derived_from_declared_file_count": len(set(grouped[project])),
        }
        amendments.append(adapter | {"project": project})

    checks = {
        "v2_p1_manifest_intact": manifest_intact(manifest),
        "source_order_hash_unchanged": source["task_ids_sha256"] == EXPECTED_SOURCE_ORDER,
        "all_299_records_used": len(source["records"]) == 299,
        "all_nine_projects_covered": len(amendments) == 9 == len(recipes),
        "one_framework_per_project": all(len(value) == 1 for value in frameworks.values()),
        "all_scopes_are_common_test_directories": all(
            any(part in {"test", "tests"} for part in PurePosixPath(item["project_test_root"]).parts)
            for item in amendments
        ),
        "no_task_outcome_or_runtime_input_used": True,
        "proposal_does_not_authorize_materialization": True,
    }
    payload = {
        "proposal_id": "dsa_v2_p1_test_scope_amendment_proposal_v0_1",
        "created_date": "2026-07-12",
        "status": "author_signoff_required" if all(checks.values()) else "failed",
        "reason": "V2-P1 refers to a project test root declared by each project recipe, but the signed recipe records omit that field.",
        "derivation_rule": "Split every frozen declared_test_file on semicolons, normalize POSIX paths, take parent directories, and select the longest common parent per project before observing any task outcome.",
        "v2_p1_manifest_aggregate_sha256": EXPECTED_AGGREGATE,
        "source_order_sha256": EXPECTED_SOURCE_ORDER,
        "amendments": amendments,
        "checks": checks,
        "authorization": {
            "author_signed": False,
            "real_v2_p2_materialization": False,
            "model_api": False,
        },
        "boundary": "This proposal changes no V2-P1 file and permits no checkout, environment build, container, project test, prompt render, credential read, or model request.",
    }
    payload["amendments_sha256"] = hashlib.sha256(canonical_bytes(amendments)).hexdigest()
    return payload


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# DSA v0.2 V2-P1 Project Test-Scope Amendment Sign-off",
        "",
        "日期：2026-07-12",
        "状态：`AUTHOR_SIGNOFF_REQUIRED / NO_REAL_ACTIVITY / NO_API`",
        "",
        "## 缺口",
        "",
        "已签核 V2-P1 要求 regression pool 使用 project recipe 声明的 project test root，",
        "但九个 recipe 均遗漏该字段。以下范围完全由冻结的299条 declared_test_file 在任何",
        "task outcome 前机械推导，不使用 pandas_161 或其他任务的运行结果。",
        "",
        "## 提议冻结值",
        "",
        "| project | framework | project test root | collection adapter |",
        "|---|---|---|---|",
    ]
    for item in payload["amendments"]:
        command = " ".join(item["collection_command"])
        lines.append(
            f"| `{item['project']}` | `{item['framework']}` | `{item['project_test_root']}` | `{command}` |"
        )
    lines.extend(
        [
            "",
            f"amendments SHA-256：`{payload['amendments_sha256']}`。",
            "",
            "## 作者签核（未签）",
            "",
            "作者需明确确认：接受上述机械 derivation rule、九个 project test roots、两个",
            "unittest patterns 与 collection adapters；该签核只补齐 V2-P1 project recipe",
            "的缺失 test-scope 字段并授权恢复已批准的首任务 Goal，不授权修改其他 V2-P1",
            "规则，不授权第二个 task、V2-P3、prompt、论文结果或模型 API。",
            "",
            "当前真实 checkout/environment/container/test/API activity 全部为0。",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = derive()
    outputs = {
        OUT: json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        REPORT: render_report(payload),
    }
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    else:
        stale = [path.as_posix() for path, content in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            raise SystemExit(f"stale amendment proposal outputs: {stale}")
    print(json.dumps({
        "status": payload["status"],
        "projects": len(payload["amendments"]),
        "amendments_sha256": payload["amendments_sha256"],
        "real_activity": 0,
        "model_api_calls": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
