# ruff: noqa: E402
#!/usr/bin/env python3
"""Audit the author gate and static boundary of the real V2-P2 order-1 adapter."""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/dsa2026_v2_p2_real_preflight.py")

import argparse
import ast
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "data/protocols/dsa_v2_p1_test_scope_amendment_proposal_v0_1.json"
AMENDMENT = ROOT / "data/protocols/dsa_v2_p1_test_scope_amendment_v0_1.json"
SOURCE_FREEZER = ROOT / "scripts/dsa2026_v2_p2_freeze_task_context.py"
WORKER = ROOT / "scripts/dsa2026_v2_p2_container_worker.py"
IMAGE_BUILDER = ROOT / "scripts/dsa2026_v2_p2_build_task_image.py"
ORACLE_RUNNER = ROOT / "scripts/dsa2026_v2_p2_run_oracle.py"
CANDIDATE_MATERIALIZER = ROOT / "scripts/dsa2026_v2_p2_materialize_candidates.py"
CANDIDATE_RUNNER = ROOT / "scripts/dsa2026_v2_p2_run_candidates.py"
DOCKERFILE = ROOT / "containers/dsa2026_v2_p2/Dockerfile.task"
BUILD_SCRIPT = ROOT / "containers/dsa2026_v2_p2/build_task_environment.sh"
OUT = ROOT / "data/protocols/dsa_v2_p2_pandas_161_real_preflight_v0_1.json"
EXPECTED_AMENDMENTS_SHA256 = "b5778a7c95042d5475d333842c5b8a486a2798a7586d74a20a84e30487ddef94"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_freezer_has_author_gate() -> bool:
    tree = ast.parse(SOURCE_FREEZER.read_text(encoding="utf-8"))
    calls = [node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)]
    return "signed_amendment" in calls


def image_builder_has_author_gate() -> bool:
    tree = ast.parse(IMAGE_BUILDER.read_text(encoding="utf-8"))
    imports_gate = any(
        isinstance(node, ast.ImportFrom)
        and node.module == "dsa2026_v2_p2_freeze_task_context"
        and any(alias.name == "signed_amendment" for alias in node.names)
        for node in ast.walk(tree)
    )
    calls_gate = any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "signed_amendment"
        for node in ast.walk(tree)
    )
    return imports_gate and calls_gate


def script_has_signed_gate(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "signed_amendment"
        for node in ast.walk(tree)
    )


def build() -> dict[str, Any]:
    proposal = read_json(PROPOSAL)
    amendment = read_json(AMENDMENT) if AMENDMENT.is_file() else None
    author_gate = bool(
        amendment
        and amendment.get("status") == "author_signed_immutable"
        and amendment.get("amendments_sha256") == EXPECTED_AMENDMENTS_SHA256
        and amendment.get("authorization", {}).get("real_v2_p2_order_1") is True
    )
    docker_text = DOCKERFILE.read_text(encoding="utf-8")
    build_text = BUILD_SCRIPT.read_text(encoding="utf-8")
    checks = {
        "proposal_hash_matches": proposal["amendments_sha256"] == EXPECTED_AMENDMENTS_SHA256,
        "source_freezer_requires_signed_amendment": source_freezer_has_author_gate(),
        "image_builder_requires_signed_amendment": image_builder_has_author_gate(),
        "oracle_runner_requires_signed_amendment": script_has_signed_gate(ORACLE_RUNNER),
        "candidate_materializer_requires_signed_amendment": script_has_signed_gate(CANDIDATE_MATERIALIZER),
        "candidate_runner_requires_signed_amendment": script_has_signed_gate(CANDIDATE_RUNNER),
        "docker_binds_py383_lock": "py383-linux-64.txt" in docker_text and "3.8.3" in docker_text,
        "docker_uses_v2_p2_entrypoint": "dsa2026_v2_p2_container_worker.py" in docker_text,
        "docker_labels_order_one_and_no_api": 'dsa2026.v2_p2.order="1"' in docker_text and 'model_api_called="false"' in docker_text,
        "build_installs_official_requirements": "pip install -r" in build_text,
        "build_installs_project_editable": "pip install -e ." in build_text,
        "build_enforces_pip_check": "pip_check_status" in build_text,
        "official_setup_never_executed": "setup.sh" not in build_text and 'official_setup_executed.txt' in build_text,
        "no_prompt_or_model_surface": all(token not in (docker_text + build_text) for token in ("OPENAI", "OPENROUTER", "prompt")),
        "candidate_materializer_contains_t1_t4": all(
            class_id in CANDIDATE_MATERIALIZER.read_text(encoding="utf-8")
            for class_id in (
                "T1_omit_one_source_file",
                "T2_omit_one_hunk",
                "T3_omit_one_edit_block",
                "T4_revert_one_changed_line",
            )
        ),
        "oracle_runner_binds_dual_fresh_and_split": all(
            token in ORACLE_RUNNER.read_text(encoding="utf-8")
            for token in ("dual_run", "visible =", "hidden =", "--network", "none")
        ),
        "candidate_runner_stops_at_first_qualifying": "break" in CANDIDATE_RUNNER.read_text(encoding="utf-8"),
        "author_gate_passed": author_gate,
    }
    return {
        "preflight_id": "dsa_v2_p2_pandas_161_real_preflight_v0_1",
        "created_date": "2026-07-12",
        "status": "ready_for_real_activity" if all(checks.values()) else "author_signoff_required",
        "task_id": "bugsinpy_pandas_161",
        "order": 1,
        "checks": checks,
        "component_sha256": {
            "source_freezer": sha256(SOURCE_FREEZER),
            "worker": sha256(WORKER),
            "image_builder": sha256(IMAGE_BUILDER),
            "oracle_runner": sha256(ORACLE_RUNNER),
            "candidate_materializer": sha256(CANDIDATE_MATERIALIZER),
            "candidate_runner": sha256(CANDIDATE_RUNNER),
            "dockerfile": sha256(DOCKERFILE),
            "build_script": sha256(BUILD_SCRIPT),
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
        "boundary": "Real source acquisition and execution remain disabled until the exact author-signed amendment exists.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    content = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUT.write_text(content, encoding="utf-8", newline="\n")
    elif not OUT.is_file() or OUT.read_text(encoding="utf-8") != content:
        raise SystemExit("stale V2-P2 real preflight")
    print(json.dumps({
        "status": payload["status"],
        "author_gate_passed": payload["checks"]["author_gate_passed"],
        "real_activity": sum(payload["activity"].values()),
        "model_api_calls": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
