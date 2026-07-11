#!/usr/bin/env python3
"""Generate/replay the synthetic-only V2-P2 executor preflight and audit."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from dsa2026_v2_p2_executor import (
    CandidateObservation,
    FrozenSpec,
    ProtocolViolation,
    RunOutcome,
    TaskObservation,
    TerminalRecord,
    cursor_state,
    execute_synthetic,
    frozen_spec,
)


ROOT = Path(__file__).resolve().parents[1]
V2P1_MANIFEST = ROOT / "data/protocols/dsa_v2_p1_hash_manifest_v0_1.json"
V2P1_PROTOCOL = ROOT / "data/protocols/dsa_v2_p1_construction_protocol_v0_1.json"
SOURCE_ORDER = ROOT / "data/protocols/dsa_v2_p1_source_order_v0_1.json"
EXECUTOR = ROOT / "scripts/dsa2026_v2_p2_executor.py"
PREFLIGHT_OUT = ROOT / "data/protocols/dsa_v2_p2_executor_preflight_v0_1.json"
AUDIT_OUT = ROOT / "data/protocols/dsa_v2_p2_synthetic_audit_v0_1.json"
REPORT_OUT = ROOT / "docs/experiments/dsa_v2_p2_executor_check_only_v0_1.md"

EXPECTED_MANIFEST_AGGREGATE = "ed7c927129c47027b57374625a2d76667503bbb1d8d37e04d4460e42b2ae8b40"
EXPECTED_SOURCE_ORDER_SHA256 = "21be1d9fed719de44126be585fa7e9123fd8579588d9ce86eb396d4ab5c2dd11"
EXPECTED_FIRST_TASK = "bugsinpy_pandas_161"
SAFE_EXECUTOR_IMPORTS = {"__future__", "dataclasses", "hashlib", "json", "re", "typing"}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_text_bytes(path: Path, strip_terminal_newline: bool = False) -> bytes:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    if strip_terminal_newline:
        text = text.rstrip("\n")
    return text.encode("utf-8")


def canonical_sha256(path: Path, strip_terminal_newline: bool = False) -> str:
    return sha256_bytes(canonical_text_bytes(path, strip_terminal_newline))


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode(
        "utf-8"
    )


def serialized_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def manifest_integrity() -> dict[str, Any]:
    manifest = read_json(V2P1_MANIFEST)
    records = []
    for expected in manifest["files"]:
        path = ROOT / expected["path"]
        strip = expected["path"] == "data/protocols/dsa_v2_p1_author_declaration_v0_1.txt"
        actual = canonical_sha256(path, strip)
        records.append(
            {
                "path": expected["path"],
                "expected_sha256": expected["sha256"],
                "actual_sha256": actual,
                "passed": actual == expected["sha256"],
            }
        )
    aggregate_input = b"".join(
        f"{record['path']}\0{record['actual_sha256']}\n".encode("utf-8") for record in records
    )
    actual_aggregate = sha256_bytes(aggregate_input)
    return {
        "status": manifest["status"],
        "expected_aggregate_sha256": EXPECTED_MANIFEST_AGGREGATE,
        "manifest_aggregate_sha256": manifest["aggregate_sha256"],
        "actual_aggregate_sha256": actual_aggregate,
        "files_all_passed": all(record["passed"] for record in records),
        "records": records,
    }


def executor_static_boundary() -> dict[str, Any]:
    tree = ast.parse(EXECUTOR.read_text(encoding="utf-8"), filename=str(EXECUTOR))
    imports: set[str] = set()
    calls: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add((node.module or "").split(".", 1)[0])
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)
    forbidden_call_names = {
        "Popen",
        "check_call",
        "check_output",
        "connect",
        "getenv",
        "open",
        "request",
        "run",
        "system",
        "urlopen",
    }
    return {
        "imports": sorted(imports),
        "unexpected_imports": sorted(imports - SAFE_EXECUTOR_IMPORTS),
        "forbidden_calls": sorted(set(calls) & forbidden_call_names),
        "passed": not (imports - SAFE_EXECUTOR_IMPORTS)
        and not (set(calls) & forbidden_call_names),
    }


PASS_ALL = RunOutcome(True, True, True, True)
NEGATIVE_QUALIFIES = RunOutcome(True, True, True, False)
VISIBLE_FAIL = RunOutcome(True, True, False, False)


def candidate(
    spec: FrozenSpec,
    task_id: str,
    class_id: str,
    token: str,
    run: RunOutcome,
) -> CandidateObservation:
    descriptor = {
        "class_id": class_id,
        "path": f"src/{token}.py",
        "hunk_index": 0,
        "edit_block_index": 0,
        "line_index": 0,
        "edit_kind": "removed",
        "raw_line_value": token,
    }
    descriptor_json = json.dumps(
        descriptor, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    )
    order_sha256 = hashlib.sha256(
        f"{spec.candidate_order_seed}|{task_id}|{descriptor_json}".encode("utf-8")
    ).hexdigest()
    return CandidateObservation(class_id, descriptor_json, order_sha256, run, run)


def observation(
    task_id: str,
    *,
    environment: tuple[bool, bool] = (True, True),
    oracle: tuple[RunOutcome, RunOutcome] = (PASS_ALL, PASS_ALL),
    candidates: tuple[CandidateObservation, ...] = (),
) -> TaskObservation:
    return TaskObservation(task_id, environment[0], environment[1], oracle[0], oracle[1], candidates)


def expect_protocol_violation(name: str, action: Any) -> dict[str, Any]:
    try:
        action()
    except ProtocolViolation as exc:
        return {"case": name, "rejected": True, "reason": str(exc)}
    return {"case": name, "rejected": False, "reason": None}


def synthetic_cases(
    spec: FrozenSpec,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, bool]]:
    first = spec.task_ids[0]
    visible_fail_candidate = candidate(
        spec, first, spec.candidate_classes[0], "a-visible-fail", VISIBLE_FAIL
    )
    qualifying_candidate = candidate(
        spec, first, spec.candidate_classes[1], "b-qualifies", NEGATIVE_QUALIFIES
    )
    success_candidates = tuple(
        sorted(
            (visible_fail_candidate, qualifying_candidate),
            key=lambda item: (
                spec.candidate_classes.index(item.class_id),
                item.order_sha256,
                item.descriptor_json,
            ),
        )
    )
    success = execute_synthetic(
        spec,
        [],
        observation(first, candidates=success_candidates),
    )
    environment_failure = execute_synthetic(
        spec,
        [],
        observation(first, environment=(False, False)),
    )
    oracle_failure = execute_synthetic(
        spec,
        [],
        observation(first, oracle=(VISIBLE_FAIL, VISIBLE_FAIL)),
    )
    hidden_pass_candidate = candidate(
        spec, first, spec.candidate_classes[0], "c-hidden-pass", PASS_ALL
    )
    no_negative = execute_synthetic(
        spec,
        [],
        observation(first, candidates=(hidden_pass_candidate,)),
    )

    exhaustion_ledger: list[TerminalRecord] = []
    last_exhaustion = None
    for task_id in spec.task_ids:
        last_exhaustion = execute_synthetic(
            spec,
            exhaustion_ledger,
            observation(task_id, environment=(False, False)),
        )
        exhaustion_ledger.append(last_exhaustion.terminal_record)
    assert last_exhaustion is not None

    target_ledger: list[TerminalRecord] = []
    last_target = None
    for task_id in spec.task_ids[: spec.target_pairs]:
        token = f"target-{task_id}"
        qualifying = candidate(
            spec, task_id, spec.candidate_classes[0], token, NEGATIVE_QUALIFIES
        )
        last_target = execute_synthetic(
            spec,
            target_ledger,
            observation(task_id, candidates=(qualifying,)),
        )
        target_ledger.append(last_target.terminal_record)
    assert last_target is not None

    tampered = CandidateObservation(
        qualifying_candidate.class_id,
        qualifying_candidate.descriptor_json,
        "0" * 64,
        qualifying_candidate.run_a,
        qualifying_candidate.run_b,
    )
    noncontiguous_ledger = [
        TerminalRecord(2, spec.task_ids[1], "materialization-failed", "synthetic", None)
    ]
    protocol_rejections = [
        expect_protocol_violation(
            "out_of_order_task_rejected",
            lambda: execute_synthetic(
                spec, [], observation(spec.task_ids[1], environment=(False, False))
            ),
        ),
        expect_protocol_violation(
            "tampered_candidate_order_hash_rejected",
            lambda: execute_synthetic(
                spec, [], observation(first, candidates=(tampered,))
            ),
        ),
        expect_protocol_violation(
            "noncontiguous_ledger_rejected",
            lambda: cursor_state(spec, noncontiguous_ledger),
        ),
        expect_protocol_violation(
            "execution_after_target_rejected",
            lambda: execute_synthetic(
                spec,
                target_ledger,
                observation(spec.task_ids[spec.target_pairs], environment=(False, False)),
            ),
        ),
        expect_protocol_violation(
            "execution_after_source_exhaustion_rejected",
            lambda: execute_synthetic(
                spec, exhaustion_ledger, observation(first, environment=(False, False))
            ),
        ),
    ]

    cases = [
        {
            "case": "pair_success",
            "terminal": asdict(success.terminal_record),
            "trace": list(success.trace),
            "output_cursor": asdict(success.output_cursor),
            "selected_task_started": success.selected_task_started,
            "activity": success.activity,
        },
        {
            "case": "environment_failure",
            "terminal": asdict(environment_failure.terminal_record),
            "trace": list(environment_failure.trace),
            "output_cursor": asdict(environment_failure.output_cursor),
            "selected_task_started": environment_failure.selected_task_started,
            "activity": environment_failure.activity,
        },
        {
            "case": "oracle_positive_failure",
            "terminal": asdict(oracle_failure.terminal_record),
            "trace": list(oracle_failure.trace),
            "output_cursor": asdict(oracle_failure.output_cursor),
            "selected_task_started": oracle_failure.selected_task_started,
            "activity": oracle_failure.activity,
        },
        {
            "case": "no_qualifying_hard_negative",
            "terminal": asdict(no_negative.terminal_record),
            "trace": list(no_negative.trace),
            "output_cursor": asdict(no_negative.output_cursor),
            "selected_task_started": no_negative.selected_task_started,
            "activity": no_negative.activity,
        },
        {
            "case": "source_exhaustion",
            "attempted_tasks": len(exhaustion_ledger),
            "first_task": exhaustion_ledger[0].task_id,
            "last_task": exhaustion_ledger[-1].task_id,
            "output_cursor": asdict(last_exhaustion.output_cursor),
            "selected_task_started": last_exhaustion.selected_task_started,
            "activity": last_exhaustion.activity,
        },
        {
            "case": "target_30_reached",
            "attempted_tasks": len(target_ledger),
            "first_task": target_ledger[0].task_id,
            "last_task": target_ledger[-1].task_id,
            "output_cursor": asdict(last_target.output_cursor),
            "selected_task_started": last_target.selected_task_started,
            "activity": last_target.activity,
        },
    ]
    zero_activity = all(
        all(value == 0 for value in case["activity"].values()) for case in cases
    )
    checks = {
        "success_selects_first_qualifying_candidate": (
            success.terminal_record.disposition == "pair-qualified"
            and success.terminal_record.selected_candidate_sha256
            == qualifying_candidate.order_sha256
            and success.output_cursor.next_task_id == spec.task_ids[1]
        ),
        "environment_failure_is_terminal": (
            environment_failure.terminal_record.reason
            == "environment-failure-or-dual-disagreement"
            and environment_failure.terminal_record.disposition == "materialization-failed"
        ),
        "oracle_positive_failure_is_terminal": (
            oracle_failure.terminal_record.reason
            == "oracle-positive-failure-or-dual-disagreement"
            and oracle_failure.terminal_record.disposition == "materialization-failed"
        ),
        "no_qualifying_negative_is_terminal": (
            no_negative.terminal_record.reason == "no-qualifying-hard-negative"
            and no_negative.terminal_record.disposition == "materialization-failed"
        ),
        "source_exhaustion_stops_before_30": (
            last_exhaustion.output_cursor.status == "source-exhausted"
            and last_exhaustion.output_cursor.qualified_pairs == 0
            and last_exhaustion.output_cursor.next_task_id is None
        ),
        "target_30_stops_without_source_exhaustion": (
            last_target.output_cursor.status == "cohort-qualified"
            and last_target.output_cursor.qualified_pairs == 30
            and last_target.output_cursor.next_task_id is None
        ),
        "all_cases_keep_real_activity_zero": zero_activity,
        "all_cases_refuse_to_start_selected_task": all(
            case["selected_task_started"] is False for case in cases
        ),
        "all_protocol_drift_attempts_rejected": all(
            case["rejected"] is True for case in protocol_rejections
        ),
    }
    return cases, protocol_rejections, checks


def render_report(preflight: dict[str, Any], audit: dict[str, Any]) -> str:
    lines = [
        "# DSA v0.2 V2-P2 Executor Synthetic Check-Only",
        "",
        "日期：2026-07-12",
        "状态：`PASS / SYNTHETIC_ONLY / FIRST_TASK_NOT_STARTED / NO_API`",
        "",
        "## 1. 结果",
        "",
        "V2-P2 executor 已实现为纯状态机。它只能消费审计器传入的 synthetic metadata，",
        "没有 filesystem/process/network/container/test/prompt/API 能力。V2-P1 manifest、",
        "299-task source order、六个 locks、project recipe、T1--T4、3-visible/20-hidden、",
        "dual-fresh 和30-pair/source-exhaustion规则全部绑定。",
        "",
        f"- V2-P1 aggregate：`{preflight['v2_p1_manifest']['actual_aggregate_sha256']}`；",
        f"- source-order：`{preflight['source_order_sha256']}`；",
        f"- 唯一 next task：`{preflight['cursor']['next_task_id']}`；",
        "- next task started：false；",
        "- real checkout/environment/container/project-test/model API：全部0。",
        "",
        "## 2. Synthetic paths",
        "",
        "| path | terminal cursor | result |",
        "|---|---|---|",
    ]
    for case in audit["cases"]:
        cursor = case["output_cursor"]
        result = case.get("terminal", {}).get("reason") or cursor["stop_reason"]
        lines.append(f"| `{case['case']}` | `{cursor['status']}` | `{result}` |")
    lines.extend(["", "## 3. Protocol drift rejection", ""])
    lines.extend(
        f"- `{case['case']}`: {'REJECTED' if case['rejected'] else 'NOT REJECTED'} "
        f"(`{case['reason']}`)"
        for case in audit["protocol_rejections"]
    )
    lines.extend(["", "## 4. Preflight checks", ""])
    lines.extend(
        f"- `{name}`: {'PASS' if passed else 'FAIL'}"
        for name, passed in preflight["checks"].items()
    )
    lines.extend(["", "## 5. Synthetic checks", ""])
    lines.extend(
        f"- `{name}`: {'PASS' if passed else 'FAIL'}"
        for name, passed in audit["checks"].items()
    )
    lines.extend(
        [
            "",
            "## 6. Boundary",
            "",
            "本记录不授权真实 V2-P2。`bugsinpy_pandas_161` 只作为 cursor identity 被读取，",
            "未 checkout、未构建、未启动、未测试。真实材料化必须由新的明确授权 Goal 开始。",
            "prompt/schema、论文结果和模型 API 均未触碰。",
        ]
    )
    return "\n".join(lines) + "\n"


def build_outputs() -> dict[Path, str]:
    protocol = read_json(V2P1_PROTOCOL)
    source_order = read_json(SOURCE_ORDER)
    spec = frozen_spec(protocol, source_order)
    initial_cursor = cursor_state(spec, [])
    manifest = manifest_integrity()
    static_boundary = executor_static_boundary()
    locks = protocol["project_environment_recipe_policy"]["candidate_independent_base"][
        "python_explicit_locks"
    ]
    recipes = protocol["project_environment_recipe_policy"]["recipes"]
    candidate_classes = tuple(
        item["id"]
        for item in protocol["candidate_generation"]["candidate_classes_in_priority_order"]
    )
    oracle = protocol["regression_oracle_construction"]
    preflight_checks = {
        "v2_p1_manifest_aggregate_unchanged": (
            manifest["manifest_aggregate_sha256"]
            == manifest["actual_aggregate_sha256"]
            == manifest["expected_aggregate_sha256"]
        ),
        "v2_p1_manifest_files_unchanged": manifest["files_all_passed"],
        "source_order_count_is_299": len(spec.task_ids) == 299,
        "source_order_sha256_unchanged": source_order["task_ids_sha256"]
        == EXPECTED_SOURCE_ORDER_SHA256,
        "cursor_selects_only_frozen_first_task": initial_cursor.next_task_id
        == EXPECTED_FIRST_TASK
        and initial_cursor.next_order == 1,
        "cursor_does_not_start_task": True,
        "six_base_locks_match": len(locks) == 6
        and all(item["actual_sha256"] == item["expected_sha256"] for item in locks),
        "project_recipe_count_is_nine": len(recipes) == 9,
        "project_recipe_boundaries_match_v2_p1": all(
            recipe["same_template_for_all_project_tasks"] is True
            and recipe["official_setup_sh_role"]
            == "provenance hash only; never executed as dependency authority"
            and recipe["post_outcome_task_specific_repair"] == "forbidden"
            and "same frozen task-image ID"
            in recipe["candidate_role_environment_equality"]
            and "network=none" in recipe["network_boundary"]
            for recipe in recipes
        ),
        "candidate_class_order_matches_v2_p1": candidate_classes == spec.candidate_classes,
        "oracle_split_matches_v2_p1": oracle["visible_p2p_count"] == 3
        and oracle["hidden_count"] == 20,
        "dual_fresh_matches_v2_p1": spec.fresh_run_count == 2,
        "cursor_stop_rules_match_v2_p1": spec.target_pairs == 30
        and len(spec.task_ids) == 299,
        "executor_has_no_external_execution_capability": static_boundary["passed"],
        "v2_p2_real_materialization_not_authorized": protocol["current_authorization"][
            "v2_p2_materialization"
        ]
        is False,
        "model_api_not_authorized": protocol["current_authorization"]["model_api"] is False,
    }
    preflight = {
        "preflight_id": "dsa_v2_p2_executor_preflight_v0_1",
        "created_date": "2026-07-12",
        "status": "passed" if all(preflight_checks.values()) else "failed",
        "mode": "synthetic_check_only",
        "checks": preflight_checks,
        "v2_p1_manifest": manifest,
        "source_order_sha256": source_order["task_ids_sha256"],
        "executor_sha256": canonical_sha256(EXECUTOR),
        "checker_sha256": canonical_sha256(Path(__file__).resolve()),
        "executor_static_boundary": static_boundary,
        "cursor": asdict(initial_cursor),
        "selected_task_started": False,
        "activity": {
            "real_task_checkouts": 0,
            "environment_builds": 0,
            "containers_started": 0,
            "project_tests_run": 0,
            "prompt_renders": 0,
            "api_keys_read": 0,
            "model_api_calls": 0,
        },
        "boundary": "No real task, environment, container, project test, prompt, credential, paper result, or model request is accessed.",
    }
    cases, protocol_rejections, synthetic_checks = synthetic_cases(spec)
    audit = {
        "audit_id": "dsa_v2_p2_synthetic_audit_v0_1",
        "created_date": "2026-07-12",
        "status": "passed" if all(synthetic_checks.values()) else "failed",
        "mode": "synthetic_check_only",
        "checks": synthetic_checks,
        "cases": cases,
        "protocol_rejections": protocol_rejections,
        "case_names_sha256": sha256_bytes(
            canonical_json_bytes([case["case"] for case in cases])
        ),
        "real_activity": preflight["activity"],
        "selected_real_task": EXPECTED_FIRST_TASK,
        "selected_real_task_started": False,
        "model_api_calls": 0,
    }
    report = render_report(preflight, audit)
    return {
        PREFLIGHT_OUT: serialized_json(preflight),
        AUDIT_OUT: serialized_json(audit),
        REPORT_OUT: report,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs()
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    else:
        stale = [
            path.relative_to(ROOT).as_posix()
            for path, content in outputs.items()
            if not path.exists() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            raise SystemExit(f"stale or missing V2-P2 check-only outputs: {stale}")
    preflight = json.loads(outputs[PREFLIGHT_OUT])
    audit = json.loads(outputs[AUDIT_OUT])
    if preflight["status"] != "passed" or audit["status"] != "passed":
        failed = [
            name
            for value in (preflight, audit)
            for name, passed in value["checks"].items()
            if not passed
        ]
        raise SystemExit(f"V2-P2 check-only failed: {failed}")
    print(
        json.dumps(
            {
                "status": "passed",
                "next_task_id": preflight["cursor"]["next_task_id"],
                "next_task_started": False,
                "synthetic_cases": len(audit["cases"]),
                "real_task_checkouts": 0,
                "containers_started": 0,
                "project_tests_run": 0,
                "model_api_calls": 0,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
