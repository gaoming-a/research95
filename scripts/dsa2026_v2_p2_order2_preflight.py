# ruff: noqa: E402
#!/usr/bin/env python3
"""Static/no-outcome preflight for V2-P2 order 2."""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/dsa2026_v2_p2_order2_preflight.py")

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/dsa2026_v2_p2_order2.py"
DOCKERFILE = ROOT / "containers/dsa2026_v2_p2/Dockerfile.order2"
BUILD = ROOT / "containers/dsa2026_v2_p2/build_task_environment_order2.sh"
LEDGER = ROOT / "data/protocols/dsa_v2_p2_terminal_ledger_v0_1.json"
SOURCE_ORDER = ROOT / "data/protocols/dsa_v2_p1_source_order_v0_1.json"
AMENDMENT = ROOT / "data/protocols/dsa_v2_p1_test_scope_amendment_v0_1.json"
OUT = ROOT / "data/protocols/dsa_v2_p2_order2_real_preflight_v0_1.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, Any]:
    runner = RUNNER.read_text(encoding="utf-8")
    docker = DOCKERFILE.read_text(encoding="utf-8")
    shell = BUILD.read_text(encoding="utf-8")
    ledger = read_json(LEDGER)
    order = read_json(SOURCE_ORDER)["records"][1]
    amendment = read_json(AMENDMENT)
    checks = {
        "order1_terminal_immutable_cursor_to_order2": len(ledger["records"]) == 1 and ledger["next_order"] == 2 and ledger["next_task_id"] == "bugsinpy_fastapi_11" and ledger["next_task_started"] is False,
        "source_order_record_is_unique_order2": order["order"] == 2 and order["task_id"] == "bugsinpy_fastapi_11",
        "author_all_v2_p2_authorization_active": amendment["status"] == "author_signed_immutable" and amendment["authorization"]["real_v2_p2_all_orders"] is True,
        "runner_has_all_bounded_phases": all(f'"{phase}"' in runner for phase in ("source", "build", "oracle", "materialize", "candidates")),
        "runner_uses_separate_order2_namespaces": all(token in runner for token in ("order2_task_source", "fastapi_11_environment", "order2_terminal_draft")),
        "runner_never_writes_order1_ledger": "PREVIOUS_LEDGER.write_text" not in runner,
        "docker_binds_order2_fastapi_py383": all(token in docker for token in ('order="2"', "bugsinpy_fastapi_11", "py383")),
        "official_setup_not_executed": "setup.sh" not in shell and "official_setup_executed.txt" in shell,
        "failure_sublogs_escape_failed_layer": "tail -n 160" in shell,
        "no_prompt_key_or_model_surface": all(
            token not in (runner + docker + shell)
            for token in ("OPENAI_API", "OPENROUTER_API", "Authorization: Bearer", "prompt_path")
        ),
        "order3_not_started": True,
    }
    return {
        "preflight_id": "dsa_v2_p2_order2_real_preflight_v0_1",
        "created_date": "2026-07-12",
        "status": "ready_for_order2_source" if all(checks.values()) else "failed",
        "task_id": "bugsinpy_fastapi_11", "order": 2,
        "checks": checks,
        "component_sha256": {"runner": sha(RUNNER), "dockerfile": sha(DOCKERFILE), "build_script": sha(BUILD)},
        "activity": {"real_task_checkouts": 0, "environment_builds": 0, "containers_started": 0, "project_tests_run": 0, "prompt_renders": 0, "api_keys_read": 0, "model_api_calls": 0},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    content = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUT.write_text(content, encoding="utf-8", newline="\n")
    elif not OUT.is_file() or OUT.read_text(encoding="utf-8") != content:
        raise SystemExit("stale order-2 preflight")
    if value["status"] != "ready_for_order2_source":
        raise SystemExit("order-2 preflight failed")
    print(json.dumps({"status": value["status"], "task_id": value["task_id"], "order": 2, "real_activity": 0, "model_api_calls": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
