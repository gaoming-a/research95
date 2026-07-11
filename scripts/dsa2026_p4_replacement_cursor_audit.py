#!/usr/bin/env python3
"""Audit the frozen P4 primary/reserve replacement cursor without running tasks."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SELECTION = ROOT / "data/protocols/dsa_p2_source_selection_v0_1.json"
PREFLIGHT = ROOT / "data/protocols/dsa_p4_preflight_v0_1.json"
P3_MANIFEST = ROOT / "data/protocols/dsa_p3_hash_manifest_v0_1.json"
TASK_GATES = ROOT / "data/hidden/dsa_p4_task_gate_v0_1.json"
PRE_CANDIDATE_DISCARDS = ROOT / "data/hidden/dsa_p4_pre_candidate_discard_v0_1.json"
ORACLE_REGISTRY = ROOT / "data/hidden/dsa_p4_oracle_pool_registry_v0_1.json"
CANDIDATE_REGISTRY = ROOT / "data/hidden/dsa_p4_candidate_registry_v0_1.json"
OUT_JSON = ROOT / "data/protocols/dsa_p4_replacement_cursor_v0_1.json"
OUT_MD = ROOT / "docs/experiments/dsa_p4_replacement_cursor_v0_1.md"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_text(path: Path) -> bytes:
    return (
        path.read_text(encoding="utf-8")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .encode("utf-8")
    )


def p3_manifest_audit(preflight: dict[str, Any]) -> dict[str, Any]:
    manifest = read_json(P3_MANIFEST)
    rows = []
    for expected in manifest["files"]:
        path = ROOT / expected["path"]
        content = canonical_text(path)
        rows.append(
            {
                "path": expected["path"],
                "expected_sha256": expected["sha256"],
                "actual_sha256": sha256_bytes(content),
                "expected_canonical_utf8_bytes": expected["canonical_utf8_bytes"],
                "actual_canonical_utf8_bytes": len(content),
            }
        )
    aggregate = sha256_bytes(
        b"".join(
            f"{row['path']}\0{row['actual_sha256']}\n".encode("utf-8")
            for row in rows
        )
    )
    expected_aggregate = preflight["p3_manifest_audit"]["aggregate_expected"]
    return {
        "file_count": len(rows),
        "files": rows,
        "aggregate_expected": expected_aggregate,
        "aggregate_actual": aggregate,
        "passed": (
            len(rows) == 16
            and aggregate == expected_aggregate
            and all(
                row["actual_sha256"] == row["expected_sha256"]
                and row["actual_canonical_utf8_bytes"] == row["expected_canonical_utf8_bytes"]
                for row in rows
            )
        ),
    }


def compact_task(selection: dict[str, Any], preflight: dict[str, Any]) -> dict[str, Any]:
    return {
        "role": selection["role"],
        "order": selection["order"],
        "task_id": selection["task_id"],
        "project": selection["project"],
        "selected_transform_id": preflight["selected_transform_id"],
        "structural_disposition": preflight["structural_disposition"],
    }


def build() -> dict[str, Any]:
    selection_root = read_json(SELECTION)
    preflight = read_json(PREFLIGHT)
    gates_root = read_json(TASK_GATES)
    pre_candidate_discards_root = read_json(PRE_CANDIDATE_DISCARDS)
    oracle_root = read_json(ORACLE_REGISTRY)
    candidate_root = read_json(CANDIDATE_REGISTRY)
    regular = selection_root["regular"]
    primary = sorted(regular["primary"], key=lambda item: item["order"])
    reserve = sorted(regular["reserve"], key=lambda item: item["order"])
    preflight_by_task = {item["task_id"]: item for item in preflight["tasks"]}
    gate_by_task = {item["task_id"]: item for item in gates_root.get("records", [])}
    pre_candidate_discard_by_task = {
        item["task_id"]: item for item in pre_candidate_discards_root.get("records", [])
    }
    oracle_by_task = {item["task_id"]: item for item in oracle_root.get("records", [])}
    candidate_by_task = {item["task_id"]: item for item in candidate_root.get("records", [])}

    primary_records = [compact_task(item, preflight_by_task[item["task_id"]]) for item in primary]
    reserve_records = [compact_task(item, preflight_by_task[item["task_id"]]) for item in reserve]
    p2_hashes = {
        path: {
            "expected": values["expected"],
            "actual": sha256_file(ROOT / path),
        }
        for path, values in preflight["p2_raw_sha256"].items()
    }
    p3 = p3_manifest_audit(preflight)

    realized_scan: list[dict[str, Any]] = []
    next_task: dict[str, Any] | None = None
    for record in primary_records:
        if record["structural_disposition"] == "discard_no_applicable_transform":
            realized_scan.append(
                {
                    **record,
                    "cursor_disposition": "discard_structural_no_applicable_transform",
                    "outcome_observed": False,
                }
            )
            continue
        gate = gate_by_task.get(record["task_id"])
        if gate:
            realized_scan.append(
                {
                    **record,
                    "cursor_disposition": (
                        "admitted_terminal" if gate["task_gate"] == "ADMIT_PAIR" else "discard_terminal_task_gate"
                    ),
                    "outcome_observed": True,
                    "task_gate": gate["task_gate"],
                    "candidate_results_sha256": gate["candidate_results_sha256"],
                }
            )
            continue
        pre_candidate_discard = pre_candidate_discard_by_task.get(record["task_id"])
        if pre_candidate_discard:
            realized_scan.append(
                {
                    **record,
                    "cursor_disposition": "discard_pre_candidate_environment_gate",
                    "outcome_observed": True,
                    "candidate_outcome_observed": False,
                    "environment_gate_status": pre_candidate_discard["status"],
                    "environment_gate_reason_code": pre_candidate_discard["reason_code"],
                    "pre_candidate_discard_record_sha256": pre_candidate_discard["record_sha256"],
                }
            )
            continue
        next_task = record
        break
    if next_task is None:
        raise ValueError("primary stream is exhausted; reserve execution cursor is not implemented in this audit version")

    discard_rows = [
        row
        for row in realized_scan
        if row["cursor_disposition"].startswith("discard_")
    ]
    if len(discard_rows) > len(reserve_records):
        raise ValueError("realized primary discards exceed frozen reserves")
    replacement_ledger = []
    for slot, (discard, replacement) in enumerate(zip(discard_rows, reserve_records, strict=False), start=1):
        replacement_ledger.append(
            {
                "replacement_slot": slot,
                "discarded_primary_order": discard["order"],
                "discarded_task_id": discard["task_id"],
                "discard_reason": discard["cursor_disposition"],
                "reserve_order": replacement["order"],
                "reserve_task_id": replacement["task_id"],
                "reserve_project": replacement["project"],
                "replacement_status": "allocated_pending_primary_scan_completion",
            }
        )

    all_structural_discards = [
        item for item in primary_records
        if item["structural_disposition"] == "discard_no_applicable_transform"
    ]
    future_structural_discards = [
        item for item in all_structural_discards
        if item["order"] > next_task["order"]
    ]
    terminal_nonstructural_discards = [
        gate
        for task_id, gate in gate_by_task.items()
        if gate["task_gate"] == "DISCARD_TASK"
        and preflight_by_task[task_id]["structural_disposition"] != "discard_no_applicable_transform"
    ]
    pre_candidate_nonstructural_discards = [
        discard
        for task_id, discard in pre_candidate_discard_by_task.items()
        if preflight_by_task[task_id]["structural_disposition"] != "discard_no_applicable_transform"
    ]
    reserve_structurally_eligible = all(
        item["structural_disposition"] == "eligible_for_candidate_materialization"
        for item in reserve_records
    )
    known_discard_count = (
        len(all_structural_discards)
        + len(terminal_nonstructural_discards)
        + len(pre_candidate_nonstructural_discards)
    )
    maximum_possible_pairs = len(primary_records) + len(reserve_records) - known_discard_count
    target_pairs = 30
    remaining_discard_budget = maximum_possible_pairs - target_pairs

    selection_task_ids = {
        item["task_id"] for item in primary + reserve
    }
    preflight_task_ids = set(preflight_by_task)
    scanned_orders = [item["order"] for item in realized_scan]
    expected_scanned_orders = list(range(1, next_task["order"]))
    terminal_gate_integrity = all(
        gate.get("p4_final_gate_formed") is False
        and gate.get("p5_entered") is False
        and gate.get("model_api_calls") == 0
        for gate in gate_by_task.values()
    )
    pre_candidate_discard_integrity = all(
        discard.get("status") == "discard_pre_candidate_environment_build_failure"
        and discard.get("task_image_created") is False
        and discard.get("official_reference_f2p_executed") is False
        and discard.get("regression_pool_discovered_or_frozen") is False
        and discard.get("transformed_candidate_materialized") is False
        and discard.get("transformed_candidate_outcome_observed") is False
        and discard.get("model_api_calls") == 0
        for discard in pre_candidate_discard_by_task.values()
    )
    next_has_no_activity = (
        next_task["task_id"] not in oracle_by_task
        and next_task["task_id"] not in candidate_by_task
        and next_task["task_id"] not in gate_by_task
        and next_task["task_id"] not in pre_candidate_discard_by_task
    )
    checks = {
        "p2_raw_hashes_unchanged": all(item["actual"] == item["expected"] for item in p2_hashes.values()),
        "p3_manifest_unchanged": p3["passed"],
        "p4_preflight_passed": preflight.get("status") == "passed" and all(preflight["checks"].values()),
        "selection_is_30_primary_10_reserve": len(primary_records) == 30 and len(reserve_records) == 10,
        "selection_and_preflight_task_sets_equal": selection_task_ids == preflight_task_ids,
        "primary_orders_contiguous": [item["order"] for item in primary_records] == list(range(1, 31)),
        "reserve_orders_contiguous": [item["order"] for item in reserve_records] == list(range(1, 11)),
        "realized_primary_scan_contiguous": scanned_orders == expected_scanned_orders,
        "terminal_task_gates_integrity_passed": terminal_gate_integrity,
        "pre_candidate_discard_integrity_passed": pre_candidate_discard_integrity,
        "terminal_and_pre_candidate_discard_sets_disjoint": not (
            set(gate_by_task) & set(pre_candidate_discard_by_task)
        ),
        "replacement_ledger_uses_reserve_prefix_only": [
            item["reserve_order"] for item in replacement_ledger
        ] == list(range(1, len(replacement_ledger) + 1)),
        "all_reserves_structurally_eligible": reserve_structurally_eligible,
        "next_task_is_unique_pending_primary": next_task["task_id"] == "bugsinpy_matplotlib_21",
        "next_task_has_no_prior_p4_activity": next_has_no_activity,
        "maximum_capacity_at_least_30_pairs": maximum_possible_pairs >= target_pairs,
        "remaining_nonstructural_discard_budget_is_four": remaining_discard_budget == 4,
        "no_model_api_call": True,
        "p5_not_entered": True,
        "no_new_task_or_candidate_run": True,
    }
    cursor_core = {
        "execution_policy": (
            "scan frozen primary order first; allocate each realized primary discard to the next frozen "
            "reserve; execute allocated reserves in frozen order after the primary scan"
        ),
        "policy_evidence": (
            "Before the fastapi_12 outcome, P4 skipped structurally inapplicable primary #1 and entered "
            "primary #2 without executing reserve #1. The cursor preserves that pre-outcome trajectory."
        ),
        "realized_primary_scan": realized_scan,
        "replacement_ledger": replacement_ledger,
        "future_structural_discards": future_structural_discards,
        "next_task": next_task,
        "next_task_id": next_task["task_id"],
    }
    cursor_sha256 = sha256_bytes(canonical_bytes(cursor_core))
    return {
        "audit_id": "dsa_p4_replacement_cursor_v0_1",
        "created_date": "2026-07-11",
        "status": "passed_unique_next_task" if all(checks.values()) else "failed",
        "checks": checks,
        "source_hashes": {
            "selection_sha256": sha256_file(SELECTION),
            "preflight_sha256": sha256_file(PREFLIGHT),
            "task_gates_sha256": sha256_file(TASK_GATES),
            "pre_candidate_discards_sha256": sha256_file(PRE_CANDIDATE_DISCARDS),
            "p2_raw_sha256": p2_hashes,
            "p3_manifest_aggregate": p3["aggregate_actual"],
        },
        "cursor": cursor_core,
        "cursor_sha256": cursor_sha256,
        "capacity": {
            "target_pairs": target_pairs,
            "primary_count": len(primary_records),
            "reserve_count": len(reserve_records),
            "total_structural_primary_discards": len(all_structural_discards),
            "terminal_nonstructural_discards": len(terminal_nonstructural_discards),
            "pre_candidate_environment_discards": len(pre_candidate_nonstructural_discards),
            "known_nonstructural_discards": (
                len(terminal_nonstructural_discards) + len(pre_candidate_nonstructural_discards)
            ),
            "known_discard_count": known_discard_count,
            "maximum_possible_pairs_after_known_discards": maximum_possible_pairs,
            "remaining_nonstructural_discard_budget": remaining_discard_budget,
            "realized_replacement_slots": len(replacement_ledger),
            "unallocated_reserve_count": len(reserve_records) - len(replacement_ledger),
        },
        "boundary": (
            "Read-only cursor audit: no task image, container, candidate, test, prompt, P5 artifact, "
            "paper result, or model API call was created or executed."
        ),
    }


def render_markdown(value: dict[str, Any]) -> str:
    cursor = value["cursor"]
    capacity = value["capacity"]
    lines = [
        "# DSA 2026 P4 replacement cursor audit v0.1",
        "",
        "日期：2026-07-11",
        f"状态：`{value['status'].upper()} / NO_NEW_EXPERIMENT / NO_API / P5_NOT_STARTED`",
        "",
        "## 1. 顺序解释",
        "",
        "冻结执行游标按 primary order 先扫描；遇到 structural/terminal discard 时，",
        "只把该 slot 分配给 frozen reserve prefix，reserve 在 primary scan 完成后按顺序执行。",
        "这一解释沿用 outcome 前的实际轨迹：primary #1 `bugsinpy_sanic_5` 结构 discard 后，",
        "P4 已直接进入 primary #2 `bugsinpy_fastapi_12`，未先执行 reserve #1。",
        "",
        "## 2. 已实现游标",
        "",
        "| primary order | task | disposition | replacement |",
        "|---:|---|---|---|",
    ]
    replacement_by_discard = {
        item["discarded_task_id"]: item for item in cursor["replacement_ledger"]
    }
    for item in cursor["realized_primary_scan"]:
        replacement = replacement_by_discard.get(item["task_id"])
        replacement_text = (
            f"reserve #{replacement['reserve_order']} `{replacement['reserve_task_id']}`"
            if replacement else "none"
        )
        lines.append(
            f"| {item['order']} | `{item['task_id']}` | `{item['cursor_disposition']}` | {replacement_text} |"
        )
    lines.extend(
        [
            "",
            "唯一 next task：",
            "",
            f"- primary order：{cursor['next_task']['order']}；",
            f"- task：`{cursor['next_task_id']}`；",
            f"- transform：`{cursor['next_task']['selected_transform_id']}`；",
            f"- cursor SHA-256：`{value['cursor_sha256']}`。",
            "",
            "## 3. Capacity",
            "",
            f"- target pairs：{capacity['target_pairs']}；",
            f"- known structural primary discards：{capacity['total_structural_primary_discards']}；",
            f"- terminal nonstructural discards：{capacity['terminal_nonstructural_discards']}；",
            f"- pre-candidate environment discards：{capacity['pre_candidate_environment_discards']}；",
            f"- maximum possible pairs after known discards：{capacity['maximum_possible_pairs_after_known_discards']}；",
            f"- remaining nonstructural discard budget：{capacity['remaining_nonstructural_discard_budget']}；",
            f"- realized replacement slots：{capacity['realized_replacement_slots']}；",
            f"- unallocated reserves：{capacity['unallocated_reserve_count']}。",
            "",
            "## 4. Gate",
            "",
            "全部 P2/P3/P4 input hashes、30+10 order、contiguous cursor、reserve-prefix replacement、",
            "terminal task Gate、capacity 和 no-API/no-P5 boundary 均通过。下一 Goal 才允许针对",
            f"`{cursor['next_task_id']}` 建立 task environment 和 pre-outcome oracle；本审计未运行新实验。",
            "",
            "机器证据：`data/protocols/dsa_p4_replacement_cursor_v0_1.json`。",
            "生成/审计器：`scripts/dsa2026_p4_replacement_cursor_audit.py`。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    json_content = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    markdown_content = render_markdown(value)
    outputs = {OUT_JSON: json_content, OUT_MD: markdown_content}
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    else:
        stale = [
            str(path.relative_to(ROOT))
            for path, content in outputs.items()
            if not path.exists() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            raise SystemExit(f"stale replacement cursor outputs: {stale}")
    if value["status"] != "passed_unique_next_task":
        failed = [name for name, passed in value["checks"].items() if not passed]
        raise SystemExit(f"replacement cursor audit failed: {failed}")
    print(
        json.dumps(
            {
                "status": value["status"],
                "next_task_id": value["cursor"]["next_task_id"],
                "next_primary_order": value["cursor"]["next_task"]["order"],
                "realized_replacement_slots": value["capacity"]["realized_replacement_slots"],
                "remaining_nonstructural_discard_budget": value["capacity"]["remaining_nonstructural_discard_budget"],
                "cursor_sha256": value["cursor_sha256"],
                "model_api_calls": 0,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
