#!/usr/bin/env python3
"""Audit order-2 terminal and extend the immutable V2-P2 ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from dsa2026_v2_p2_check_only import manifest_integrity


ROOT = Path(__file__).resolve().parents[1]
LEDGER_V1 = ROOT / "data/protocols/dsa_v2_p2_terminal_ledger_v0_1.json"
DRAFT = ROOT / "data/protocols/dsa_v2_p2_order2_terminal_draft_v0_1.json"
SOURCE = ROOT / "data/protocols/dsa_v2_p2_order2_task_source_registry_v0_1.json"
ENVIRONMENT = ROOT / "data/protocols/dsa_v2_p2_fastapi_11_environment_v0_1.json"
LOG = ROOT / "tmp/dsa2026_v2_p2_runtime/order2/docker_build.log"
LEDGER_V2 = ROOT / "data/protocols/dsa_v2_p2_terminal_ledger_v0_2.json"
AUDIT = ROOT / "data/protocols/dsa_v2_p2_order2_gate_audit_v0_1.json"
REPORT = ROOT / "docs/experiments/dsa_v2_p2_fastapi_11_terminal_gate_v0_1.md"
ORDER1_LEDGER_SHA = "d244f194627819e47eb50dc8936759f37ad66f31e29db95b0232442a70d81794"
FORBIDDEN = (
    ROOT / "data/hidden/dsa_v2_p2_fastapi_11_oracle_v0_1.json",
    ROOT / "data/hidden/dsa_v2_p2_fastapi_11_candidate_registry_v0_1.json",
    ROOT / "data/hidden/dsa_v2_p2_fastapi_11_candidate_results_v0_1.json",
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")).hexdigest()


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    prior = read_json(LEDGER_V1)
    draft = read_json(DRAFT)
    source = read_json(SOURCE)
    environment = read_json(ENVIRONMENT)
    manifest = manifest_integrity()
    order2 = draft["records"][0]
    log_bytes = LOG.read_bytes()
    image = subprocess.run(["docker", "image", "inspect", "dsa2026-v2-p2-task:bugsinpy_fastapi_11"], capture_output=True)
    containers = subprocess.check_output(["docker", "ps", "-a", "--format", "{{.Names}}"], text=True, encoding="utf-8").splitlines()
    ledger = {
        "ledger_id": "dsa_v2_p2_terminal_ledger_v0_2",
        "created_date": "2026-07-12",
        "status": "orders_1_2_terminal",
        "supersedes": "data/protocols/dsa_v2_p2_terminal_ledger_v0_1.json",
        "superseded_ledger_sha256": canonical_sha(prior),
        "records": [prior["records"][0], order2],
        "attempted_tasks": 2,
        "qualified_pairs": 0,
        "next_order": 3,
        "next_task_id": "bugsinpy_black_4",
        "next_task_started": False,
        "model_api_calls": 0,
    }
    checks = {
        "v2_p1_manifest_unchanged": manifest["files_all_passed"] and manifest["actual_aggregate_sha256"] == "ed7c927129c47027b57374625a2d76667503bbb1d8d37e04d4460e42b2ae8b40",
        "order1_ledger_byte_semantics_unchanged": canonical_sha(prior) == ORDER1_LEDGER_SHA,
        "order1_record_preserved_exactly": ledger["records"][0] == prior["records"][0],
        "only_order2_source_added": len(source["records"]) == 1 and source["records"][0]["order"] == 2 and source["records"][0]["task_id"] == "bugsinpy_fastapi_11",
        "environment_failure_terminal": environment["status"] == "materialization-failed" and environment["failure_reason"] == "environment-build-failure",
        "build_log_hash_matches": hashlib.sha256(log_bytes).hexdigest() == environment["build_output_sha256"],
        "exact_failure_evidence_present": b"editable_project failed (exit=1)" in log_bytes and b"setup.py\" not found" in log_bytes and b"starlette==0.13.2" in log_bytes,
        "no_setup_repair_or_rerun": environment["official_setup_executed"] is False and environment["task_specific_repair_attempted"] is False,
        "order2_draft_binds_environment": order2["environment_record_sha256"] == canonical_sha(environment),
        "order2_unique_terminal": len(draft["records"]) == 1 and order2["order"] == 2 and order2["disposition"] == "materialization-failed",
        "oracle_candidate_outputs_absent": not any(path.exists() for path in FORBIDDEN),
        "no_final_image_or_containers": image.returncode != 0 and not any("dsa-v2-p2" in name.lower() for name in containers),
        "activity_exact": environment["activity"] == {"real_task_checkouts": 1, "environment_builds": 1, "containers_started": 0, "project_tests_run": 0, "prompt_renders": 0, "api_keys_read": 0, "model_api_calls": 0},
        "cursor_advances_once_to_order3_not_started": ledger["next_order"] == 3 and ledger["next_task_id"] == "bugsinpy_black_4" and ledger["next_task_started"] is False,
        "model_api_zero": ledger["model_api_calls"] == 0,
    }
    audit = {
        "audit_id": "dsa_v2_p2_order2_gate_audit_v0_1", "created_date": "2026-07-12",
        "status": "passed_terminal_continue_cursor" if all(checks.values()) else "failed",
        "task_id": "bugsinpy_fastapi_11", "order": 2, "checks": checks,
        "source_record_sha256": source["records"][0]["record_sha256"],
        "environment_record_sha256": canonical_sha(environment), "terminal_record": order2,
        "activity": environment["activity"],
        "diagnosis": {
            "editable_project": "pip 20.1.1 cannot install this pyproject-only checkout in editable mode because setup.py is absent",
            "pip_check": "requirements installed fastapi 0.55.1 requiring starlette 0.13.2 while the frozen requirements contain starlette 0.12.8",
            "repair_or_rerun": "forbidden for terminal order 2",
        },
        "boundary": "No order-2 oracle/candidate/model outcome and no order-3 runtime activity occurred.",
    }
    return ledger, audit


def report(audit: dict[str, Any]) -> str:
    return "\n".join([
        "# DSA v0.2 V2-P2 fastapi_11 Terminal Gate", "",
        "日期：2026-07-12", "状态：`PASS / ENVIRONMENT TERMINAL / CONTINUE CURSOR / NO API`", "",
        "## 结果", "",
        "order=2 `bugsinpy_fastapi_11` 的唯一 no-cache build 在环境 Gate exit=1。外层日志明确记录：",
        "", "- editable install 失败：checkout 只有 `pyproject.toml`，冻结 pip 20.1.1 要求 `setup.py`；",
        "- `pip check` 失败：FastAPI 0.55.1 要求 Starlette 0.13.2，而冻结 requirements 是0.12.8；",
        "- 未执行 setup、未改依赖、未重跑；image/container/test/oracle/candidate/API 均为0。", "",
        "order1 ledger 保持不变；新 v0.2 ledger 仅追加 order2 terminal，cursor 指向未启动 order3 `bugsinpy_black_4`。", "",
        "## Checks", "",
        *[f"- `{name}`: {'PASS' if passed else 'FAIL'}" for name, passed in audit["checks"].items()], "",
        "## Boundary", "", "不得重跑 order2。本轮停在未启动的 order3 cursor，不创建或执行 order3 Goal。V2-P3/prompt/model API 仍禁止。", "",
    ])


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    ledger, audit = build()
    outputs = {LEDGER_V2: json.dumps(ledger, ensure_ascii=False, indent=2, sort_keys=True) + "\n", AUDIT: json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n", REPORT: report(audit)}
    if args.write:
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8", newline="\n")
    else:
        stale = [str(path) for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            raise SystemExit(f"stale order2 audit: {stale}")
    if audit["status"] != "passed_terminal_continue_cursor":
        raise SystemExit("order2 audit failed")
    print(json.dumps({"status": audit["status"], "task_id": audit["task_id"], "next_task_id": ledger["next_task_id"], "containers_started": 0, "project_tests_run": 0, "model_api_calls": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
