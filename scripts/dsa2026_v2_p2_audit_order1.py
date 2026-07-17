# ruff: noqa: E402
#!/usr/bin/env python3
"""Audit the terminal V2-P2 order-1 materialization result."""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/dsa2026_v2_p2_audit_order1.py")

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from dsa2026_v2_p2_check_only import manifest_integrity


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/protocols/dsa_v2_p2_task_source_registry_v0_1.json"
ENVIRONMENT = ROOT / "data/protocols/dsa_v2_p2_pandas_161_environment_v0_1.json"
TERMINAL = ROOT / "data/protocols/dsa_v2_p2_terminal_ledger_v0_1.json"
AMENDMENT = ROOT / "data/protocols/dsa_v2_p1_test_scope_amendment_v0_1.json"
RUNTIME_LOG = ROOT / "tmp/dsa2026_v2_p2_runtime/environment/bugsinpy_pandas_161_docker_build.log"
AUDIT = ROOT / "data/protocols/dsa_v2_p2_order1_gate_audit_v0_1.json"
REPORT = ROOT / "docs/experiments/dsa_v2_p2_pandas_161_terminal_gate_v0_1.md"
FORBIDDEN_OUTCOMES = (
    ROOT / "data/hidden/dsa_v2_p2_pandas_161_oracle_v0_1.json",
    ROOT / "data/hidden/dsa_v2_p2_pandas_161_candidate_registry_v0_1.json",
    ROOT / "data/hidden/dsa_v2_p2_pandas_161_candidate_results_v0_1.json",
)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()


def runtime_state() -> dict[str, Any]:
    image = subprocess.run(
        ["docker", "image", "inspect", "dsa2026-v2-p2-task:bugsinpy_pandas_161"],
        capture_output=True,
    )
    names = subprocess.check_output(
        ["docker", "ps", "-a", "--format", "{{.Names}}"], text=True, encoding="utf-8"
    ).splitlines()
    return {
        "final_task_image_exists": image.returncode == 0,
        "v2_p2_container_names": [name for name in names if "dsa-v2-p2" in name.lower()],
    }


def build() -> dict[str, Any]:
    source = read_json(SOURCE)
    environment = read_json(ENVIRONMENT)
    terminal = read_json(TERMINAL)
    amendment = read_json(AMENDMENT)
    manifest = manifest_integrity()
    runtime = runtime_state()
    source_record = source["records"][0]
    terminal_record = terminal["records"][0]
    runtime_hash = hashlib.sha256(RUNTIME_LOG.read_bytes()).hexdigest() if RUNTIME_LOG.is_file() else None
    checks = {
        "v2_p1_manifest_aggregate_unchanged": (
            manifest["actual_aggregate_sha256"]
            == manifest["expected_aggregate_sha256"]
            == "ed7c927129c47027b57374625a2d76667503bbb1d8d37e04d4460e42b2ae8b40"
        ),
        "v2_p1_files_unchanged": manifest["files_all_passed"],
        "test_scope_amendment_author_signed": amendment["status"] == "author_signed_immutable",
        "only_order_1_source_frozen": len(source["records"]) == 1 and source_record["order"] == 1 and source_record["task_id"] == "bugsinpy_pandas_161",
        "source_context_hash_bound": source_record["context"]["context_tree_sha256"] == "fc25ef1325ecba7a346f576012d13349050e76709cc1f07fad7b05d81aee7108",
        "environment_failure_is_terminal": environment["status"] == "materialization-failed" and environment["failure_reason"] == "environment-build-failure",
        "build_log_hash_matches": runtime_hash == environment["build_output_sha256"],
        "official_setup_not_executed": environment["official_setup_executed"] is False,
        "no_task_specific_repair": environment["task_specific_repair_attempted"] is False,
        "unique_terminal_record": len(terminal["records"]) == 1 and terminal_record["order"] == 1,
        "terminal_binds_environment_record": terminal_record["environment_record_sha256"] == canonical_sha256(environment),
        "terminal_reason_matches": terminal_record["reason"] == "environment-build-failure" and terminal_record["disposition"] == "materialization-failed",
        "next_task_selected_but_not_started": terminal["next_order"] == 2 and terminal["next_task_id"] == "bugsinpy_fastapi_11" and terminal["next_task_started"] is False,
        "oracle_and_candidate_outputs_absent": not any(path.exists() for path in FORBIDDEN_OUTCOMES),
        "no_final_task_image": runtime["final_task_image_exists"] is False,
        "no_v2_p2_containers": runtime["v2_p2_container_names"] == [],
        "activity_counts_match_terminal_stage": environment["activity"] == {
            "real_task_checkouts": 1,
            "environment_builds": 1,
            "containers_started": 0,
            "project_tests_run": 0,
            "prompt_renders": 0,
            "api_keys_read": 0,
            "model_api_calls": 0,
        },
        "model_api_calls_zero": terminal["model_api_calls"] == 0 and environment["activity"]["model_api_calls"] == 0,
    }
    return {
        "audit_id": "dsa_v2_p2_order1_gate_audit_v0_1",
        "created_date": "2026-07-12",
        "status": "passed_terminal_continue_cursor" if all(checks.values()) else "failed",
        "task_id": "bugsinpy_pandas_161",
        "order": 1,
        "checks": checks,
        "v2_p1_manifest": manifest,
        "source_record_sha256": source_record["record_sha256"],
        "environment_record_sha256": canonical_sha256(environment),
        "terminal_record": terminal_record,
        "runtime": runtime,
        "activity": environment["activity"],
        "diagnosis": {
            "known": "The no-cache Docker build failed inside the frozen dependency-build step after the py383 lock and source copies completed.",
            "unknown": "The exact failing subcommand among requirements install, editable project install, and pip check is not recoverable because sublogs were stored only in the discarded failed layer.",
            "repair_or_rerun": "forbidden for this terminal task",
        },
        "boundary": "Order 1 is terminal. Oracle, regression-pool, candidate, prompt, credential, model API, and order-2 runtime activity did not occur in this bounded Goal; the frozen cursor may continue in a separate order-2 Goal.",
    }


def render(value: dict[str, Any]) -> str:
    lines = [
        "# DSA v0.2 V2-P2 pandas_161 Terminal Gate",
        "",
        "日期：2026-07-12",
        "状态：`PASS / MATERIALIZATION_FAILED_ENVIRONMENT / CONTINUE_CURSOR / NO_API`",
        "",
        "## 结果",
        "",
        "冻结 order=1 `bugsinpy_pandas_161` 已在 environment build 形成唯一 terminal。",
        "py383 explicit lock 与 source copy 完成后，冻结 dependency-build aggregate exit=1；",
        "未生成最终 task image，未启动 qualification container 或项目测试。",
        "",
        f"- source record：`{value['source_record_sha256']}`；",
        f"- environment record：`{value['environment_record_sha256']}`；",
        f"- build output SHA-256：`{read_json(ENVIRONMENT)['build_output_sha256']}`；",
        "- official setup executed：false；task-specific repair：false；",
        "- checkout/build/container/test/prompt/key/API：1/1/0/0/0/0/0；",
        "- next cursor：order=2 `bugsinpy_fastapi_11`，started=false。",
        "",
        "## 诊断边界",
        "",
        value["diagnosis"]["known"],
        value["diagnosis"]["unknown"],
        "按冻结 no-rerun 规则，不修改环境、不重试该 task。",
        "",
        "## Gate checks",
        "",
    ]
    lines.extend(f"- `{name}`: {'PASS' if passed else 'FAIL'}" for name, passed in value["checks"].items())
    lines.extend([
        "",
        "## Boundary",
        "",
        "本记录不包含 oracle/candidate/model outcome。不得继续 order=1；本 bounded Goal",
        "未启动 order=2，但作者自动授权允许下一独立 Goal 从冻结 cursor 继续。V2-P3、",
        "prompt 与模型 API 仍未授权。",
    ])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    outputs = {
        AUDIT: json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        REPORT: render(value),
    }
    if args.write:
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8", newline="\n")
    else:
        stale = [str(path) for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            raise SystemExit(f"stale order-1 terminal audit: {stale}")
    if value["status"] != "passed_terminal_continue_cursor":
        raise SystemExit("order-1 terminal audit failed")
    print(json.dumps({
        "status": value["status"],
        "task_id": value["task_id"],
        "terminal_reason": value["terminal_record"]["reason"],
        "containers_started": value["activity"]["containers_started"],
        "project_tests_run": value["activity"]["project_tests_run"],
        "model_api_calls": value["activity"]["model_api_calls"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
