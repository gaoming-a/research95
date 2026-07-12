#!/usr/bin/env python3
"""No-outcome audit for the generic V2-P2 cursor executor."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXECUTOR = ROOT / "scripts/dsa2026_v2_p2_cursor_execute.py"
DOCKERFILE = ROOT / "containers/dsa2026_v2_p2/Dockerfile.cursor"
CONFIG = ROOT / "data/protocols/dsa_v2_p2_cursor_task_config_v0_1.json"
AUTH = ROOT / "data/protocols/dsa_v2_p2_continuous_authorization_v0_1.json"
OUT = ROOT / "data/protocols/dsa_v2_p2_cursor_executor_preflight_v0_1.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> dict:
    executor = EXECUTOR.read_text(encoding="utf-8")
    docker = DOCKERFILE.read_text(encoding="utf-8")
    config = read_json(CONFIG)
    auth = read_json(AUTH)
    checks = {
        "continuous_authorization_active": auth["status"] == "author_signed_active"
        and auth["authorization"]["continuous_v2_p2"],
        "unique_order3_cursor_unstarted": config["task"]["order"] == 3
        and config["task"]["task_id"] == "bugsinpy_black_4"
        and not config["next_task_started"],
        "all_scientific_phases_present": all(
            f'"{phase}"' in executor
            for phase in (
                "source",
                "build",
                "oracle",
                "materialize",
                "candidates",
                "finalize",
            )
        ),
        "versioned_task_namespaces": all(
            token in executor
            for token in (
                "runtime_namespace",
                "terminal_draft",
                "candidate_registry",
                "candidate_results",
            )
        ),
        "dynamic_v2_p1_inputs": all(
            token in executor
            for token in ("python_lock", "project_test_scope", "source_record")
        ),
        "docker_binds_dynamic_task": all(
            token in docker
            for token in (
                "${TASK_CONTEXT}",
                "${TASK_ID}",
                "${ORDER}",
                "${LOCK_PATH}",
                "${PYTHON_VERSION}",
            )
        ),
        "dual_fresh_and_t1_t4_reused": all(
            token in executor
            for token in (
                "oracle_runner.execute",
                "materializer.build_registry",
                "candidate_runner.execute",
            )
        ),
        "failure_writes_terminal_without_rerun": "environment-build-failure" in executor
        and "--no-cache" in executor,
        "no_model_or_prompt_surface": all(
            token not in executor + docker
            for token in ("OPENAI_API", "OPENROUTER_API", "prompt_path")
        ),
        "real_activity_zero": True,
    }
    return {
        "preflight_id": "dsa_v2_p2_cursor_executor_preflight_v0_1",
        "created_date": "2026-07-12",
        "status": "ready_for_order3_source" if all(checks.values()) else "failed",
        "checks": checks,
        "cursor_config_sha256": config["config_sha256"],
        "component_sha256": {
            "executor": hashlib.sha256(EXECUTOR.read_bytes()).hexdigest(),
            "dockerfile": hashlib.sha256(DOCKERFILE.read_bytes()).hexdigest(),
        },
        "activity": {
            "real_task_checkouts": 0,
            "environment_builds": 0,
            "containers_started": 0,
            "project_tests_run": 0,
            "prompt_renders": 0,
            "api_keys_read": 0,
            "model_api_calls": 0,
        },
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
        raise SystemExit("stale cursor executor preflight")
    if value["status"] != "ready_for_order3_source":
        raise SystemExit("cursor executor preflight failed")
    print(
        json.dumps(
            {
                "status": value["status"],
                "order": 3,
                "real_activity": 0,
                "model_api_calls": 0,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
