"""Audit the v0.1 pre-model termination and the bounded v0.2 design draft.

This check is read-only. It does not run a task, container, test, prompt render,
or model request, and it never reads an API credential.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "data/protocols/dsa_v0_1_termination_and_v0_2_redesign_v0_1.json"
P3_MANIFEST = ROOT / "data/protocols/dsa_p3_hash_manifest_v0_1.json"
TASK_GATES = ROOT / "data/hidden/dsa_p4_task_gate_v0_1.json"
PRE_CANDIDATE = ROOT / "data/hidden/dsa_p4_pre_candidate_discard_v0_1.json"
PLAN = ROOT / "docs/plans/dsa_agent_evidence_experiment_v0_2_zh.md"
TERMINATION = ROOT / "docs/experiments/dsa_p4_v0_1_termination_v0_1.md"
SIGNOFF = ROOT / "docs/experiments/dsa_v0_2_construction_protocol_signoff_v0_1.md"
V2P1_PROTOCOL = ROOT / "data/protocols/dsa_v2_p1_construction_protocol_v0_1.json"
CURRENT_PLAN = ROOT / "docs/plans/current_plan_zh.md"
CURRENT_STATE = ROOT / "docs/plans/current_project_state_zh.md"
MASTER_PLAN = ROOT / "docs/plans/dsa_2026_submission_execution_plan_zh.md"
INDEX = ROOT / "docs/INDEX.md"
README = ROOT / "README.md"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def canonical_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def p3_manifest_intact(manifest: dict[str, Any]) -> bool:
    return all(
        (ROOT / record["path"]).exists()
        and canonical_sha256(ROOT / record["path"]) == record["sha256"]
        for record in manifest["files"]
    )


def build_checks() -> dict[str, bool]:
    design = read_json(DESIGN)
    manifest = read_json(P3_MANIFEST)
    gates = read_json(TASK_GATES)
    discards = read_json(PRE_CANDIDATE)
    v2p1 = read_json(V2P1_PROTOCOL)
    old = design["v0_1_termination"]
    new = design["v0_2_design"]
    gate_by_task = {record["task_id"]: record for record in gates["records"]}
    discard_by_task = {record["task_id"]: record for record in discards["records"]}
    condition_groups = [item["groups"] for item in new["cumulative_evidence"]]
    plan_text = PLAN.read_text(encoding="utf-8")
    termination_text = TERMINATION.read_text(encoding="utf-8")
    signoff_text = SIGNOFF.read_text(encoding="utf-8")
    current_surfaces = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (CURRENT_PLAN, CURRENT_STATE, MASTER_PLAN, INDEX, README)
    )
    return {
        "p3_v0_1_manifest_intact": (
            manifest["aggregate_sha256"]
            == old["immutable_p3_manifest_aggregate_sha256"]
            == "f81ba7063297dc9264041256b99a7daa002bd730cbe1dbd9bfb105cd7aa71297"
            and p3_manifest_intact(manifest)
        ),
        "fastapi_terminal_gate_bound": (
            gate_by_task["bugsinpy_fastapi_12"]["task_gate"] == "DISCARD_TASK"
            and gate_by_task["bugsinpy_fastapi_12"]["model_api_calls"] == 0
        ),
        "tornado_environment_gate_bound": (
            discard_by_task["bugsinpy_tornado_10"]["status"]
            == "discard_pre_candidate_environment_build_failure"
            and discard_by_task["bugsinpy_tornado_10"]["model_api_calls"] == 0
        ),
        "matplotlib_reference_gate_bound": (
            discard_by_task["bugsinpy_matplotlib_21"]["status"]
            == "discard_pre_candidate_reference_f2p_failure"
            and discard_by_task["bugsinpy_matplotlib_21"]["model_api_calls"] == 0
        ),
        "termination_is_not_capacity_or_model_result": (
            old["capacity_stop_rule_triggered"] is False
            and old["model_api_calls"] == 0
            and old["confirmatory_model_outputs"] == 0
            and old["confirmatory_effect_estimates_available"] is False
        ),
        "five_active_tasks_development_only": len(old["v0_2_development_exclusion_task_ids"]) == 5,
        "agent_boundary_is_prompt_only": (
            "without autonomous tools" in new["agent_boundary"]
            and "supplied cumulative evidence packet" in new["agent_boundary"]
        ),
        "core_factorial_count_is_2160": (
            new["planned_valid_responses"]
            == new["target_task_pairs"]
            * new["candidates_per_task"]
            * len(new["conditions"])
            * new["models"]
            * new["stateless_repeats"]
            == 2160
        ),
        "c0_c3_are_strictly_cumulative": condition_groups == [
            ["change_request"],
            ["change_request", "executable_basic"],
            ["change_request", "executable_basic", "visible_f2p"],
            ["change_request", "executable_basic", "visible_f2p", "visible_p2p"],
        ],
        "construction_precedes_confirmatory_freeze": (
            [phase["phase"] for phase in new["phases"]]
            == ["V2-D0", "V2-P1", "V2-P2", "V2-P3", "V2-P4", "V2-P5", "V2-P6"]
            and new["construction_protocol"]["model_outcome_used_for_construction"] is False
        ),
        "api_only_in_v2_p5": all(
            phase["api_allowed"] is (phase["phase"] == "V2-P5")
            for phase in new["phases"]
        ),
        "current_authorization_is_no_api_no_materialization": (
            new["current_authorization"]["v0_2_materialization"] is False
            and new["current_authorization"]["v0_2_prompt_change"] is False
            and new["current_authorization"]["model_api"] is False
        ),
        "plan_has_required_boundaries": all(
            marker in plan_text
            for marker in (
                "V2-P1_PASS_AUTHOR_SIGNED / RULES_FROZEN / V2-P2_NOT_AUTHORIZED / NO_API",
                "reviewer agent",
                "Delta_minus",
                "Delta_plus",
                "2160",
                "真实 materialization",
            )
        ),
        "termination_doc_has_required_boundaries": all(
            marker in termination_text
            for marker in (
                "TERMINATED_BEFORE_MODEL_OUTPUT",
                "capacity",
                "模型 API calls=0",
                "不得进入 v0.2",
            )
        ),
        "signoff_is_signed_and_v2_p2_remains_bounded": (
            all(
                marker in signoff_text
                for marker in (
                    "AUTHOR_SIGNED / V2-P1_RULE_FREEZE_AUTHORIZED",
                    "65328de6aa913bd8ee04dfdbfd172960745bc431ab7d2f7742c8aa7038dbe2ca",
                    "不授权进入 V2-P2",
                    "不授权修改 prompt 或调用模型 API",
                )
            )
            and v2p1["author_signoff"]["status"] == "signed"
            and v2p1["current_authorization"]["v2_p2_materialization"] is False
            and v2p1["current_authorization"]["model_api"] is False
        ),
        "current_surfaces_point_to_v0_2_no_api": all(
            marker in current_surfaces
            for marker in (
                "dsa_agent_evidence_experiment_v0_2_zh.md",
                "V0_1_TERMINATED_BEFORE_MODEL_OUTPUT",
                "V2_P1_PASS_AUTHOR_SIGNED",
                "V2_P2_NOT_AUTHORIZED",
                "NO_API",
            )
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    checks = build_checks()
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise SystemExit(f"v0.2 redesign audit failed: {failed}")
    print(json.dumps({"status": "passed", "checks": checks, "model_api_calls": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
