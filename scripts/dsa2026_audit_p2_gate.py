# ruff: noqa: E402
"""Consolidate the no-API P2 gate and freeze the DSA Regular protocol."""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/dsa2026_audit_p2_gate.py")

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PATHS = {
    "p1_audit": ROOT / "data/protocols/dsa_legacy_quarantine_audit_v0_1.json",
    "development_exclusions": ROOT / "data/protocols/dsa_p2_development_exclusion_registry_v0_1.json",
    "source_frame": ROOT / "data/protocols/dsa_p2_source_frame_v0_1.json",
    "source_selection": ROOT / "data/protocols/dsa_p2_source_selection_v0_1.json",
    "transform_registry": ROOT / "data/protocols/dsa_p2_transform_registry_v0_1.json",
    "transform_validation": ROOT / "data/protocols/dsa_p2_transform_validation_v0_1.json",
    "precision": ROOT / "data/protocols/dsa_p2_precision_simulation_v0_1.json",
    "literature": ROOT / "data/protocols/dsa_p2_literature_search_log_v0_1.json",
}
AUDIT_OUT = ROOT / "data/protocols/dsa_p2_gate_audit_v0_1.json"
DECISION_OUT = ROOT / "data/protocols/dsa_p2_protocol_decision_v0_1.json"
REPORT_OUT = ROOT / "docs/experiments/dsa_p2_source_feasibility_and_protocol_decision_v0_1.md"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    data = {name: read_json(path) for name, path in PATHS.items()}
    exclusions = set(data["development_exclusions"]["excluded_task_ids"])
    excluded_projects = set(data["development_exclusions"]["base_project_exclusions"])
    regular = data["source_selection"]["regular"]
    regular_primary = regular["primary"]
    regular_reserve = regular["reserve"]
    selected = regular_primary + regular_reserve
    selected_ids = {record["task_id"] for record in selected}
    selected_projects = {record["project"] for record in selected}
    frame_by_task = {
        record["task_id"]: record for record in data["source_frame"]["records"]
    }
    primary_counts = Counter(record["project"] for record in regular_primary)
    reserve_projects = {record["project"] for record in regular_reserve}
    checks = {
        "p1_quarantine_passed": data["p1_audit"]["status"] == "passed",
        "development_source_task_overlap_zero": not (selected_ids & exclusions),
        "base_excluded_project_overlap_zero": not (selected_projects & excluded_projects),
        "official_source_frame_has_at_least_30_primary_and_10_reserve": (
            len(regular_primary) == 30 and len(regular_reserve) == 10
        ),
        "regular_has_at_least_eight_projects": len(primary_counts) >= 8,
        "regular_primary_project_cap_at_most_four": max(primary_counts.values()) <= 4,
        "reserve_covers_every_primary_project": set(primary_counts) <= reserve_projects,
        "all_regular_tasks_are_new_project_tasks": all(
            record["project"] not in excluded_projects for record in regular_primary
        ),
        "new_project_requirement_at_least_15_tasks_and_4_projects": (
            len(regular_primary) >= 15 and len(primary_counts) >= 4
        ),
        "all_selected_sources_have_improved_environment_reproduction": all(
            frame_by_task[record["task_id"]]["external_reproduction_evidence"]["improved_conda_expected_pair_passed"]
            for record in selected
        ),
        "all_selected_sources_have_visible_and_hidden_oracle_source_plan": all(
            frame_by_task[record["task_id"]]["declared_f2p_commands"]
            and frame_by_task[record["task_id"]]["hidden_oracle_source_plan"]
            for record in selected
        ),
        "no_source_transform_applied_in_p2": all(
            not frame_by_task[record["task_id"]]["transform_applied"]
            for record in selected
        ),
        "no_candidate_hidden_result_observed_in_p2": all(
            not frame_by_task[record["task_id"]]["candidate_hidden_result_observed"]
            for record in selected
        ),
        "transform_registry_frozen_for_author_review": (
            data["transform_registry"]["status"] == "frozen_for_p3_author_review"
        ),
        "transform_validation_passed": data["transform_validation"]["status"] == "passed",
        "regular_precision_passed": data["precision"]["regular"]["passed"],
        "nearest_neighbor_positioning_passed": data["literature"]["positioning_gate_passed"],
        "nearest_neighbor_exact_design_match_absent": not data["literature"]["exact_design_match_found"],
        "no_api_prompt_or_old_result_use": (
            not data["source_frame"]["data_boundary"]["model_api_called"]
            and not data["source_frame"]["data_boundary"]["prompt_created"]
            and not data["source_frame"]["data_boundary"]["legacy_paper_metric_read"]
            and not data["source_frame"]["data_boundary"]["legacy_raw_output_read"]
            and not data["precision"]["data_boundary"]["model_api_called"]
            and not data["precision"]["data_boundary"]["legacy_paper_metric_read"]
        ),
    }
    passed = all(checks.values())
    decision = {
        "decision_id": "dsa_p2_protocol_decision_v0_1",
        "decision_date": "2026-07-11",
        "status": "regular_frozen" if passed else "no_protocol_frozen",
        "selected_protocol": "Regular" if passed else None,
        "regular": {
            "primary_tasks": 30,
            "reserve_tasks": 10,
            "projects": len(primary_counts),
            "candidates_planned_for_p4": 60,
            "fixed_models_to_freeze_in_p3": 3,
            "stateless_repeats": 3,
            "source_selection": PATHS["source_selection"].relative_to(ROOT).as_posix(),
        },
        "short": {
            "status": "inactive_not_a_post_result_fallback" if passed else "requires_author_signoff_if_only_short_passes",
            "precision_simulation_preserved": True,
        },
        "irreversibility": (
            "After P3 author sign-off or any model call, Regular/Short, task/project counts, "
            "model count, repeat count, source order, and transform priority cannot change "
            "because of results, interval width, model disagreement, or review feedback."
        ),
        "next_phase": "P3 author preregistration and prompt/schema freeze",
        "p3_not_started": True,
        "api_authorized_now": False,
        "fresh_p4_requirement": (
            "Every selected candidate must still pass two fresh clean-environment runs in P4. "
            "The external reproduction result is P2 source feasibility, not final cohort admission."
        ),
    }
    audit = {
        "audit_id": "dsa_p2_gate_audit_v0_1",
        "audit_date": "2026-07-11",
        "status": "passed" if passed else "failed",
        "checks": checks,
        "evidence": {name: path.relative_to(ROOT).as_posix() for name, path in PATHS.items()},
        "source_summary": {
            "development_excluded_tasks": len(exclusions),
            "base_excluded_projects": len(excluded_projects),
            "eligible_source_tasks": data["source_frame"]["eligible_record_count"],
            "eligible_source_projects": len(data["source_frame"]["eligible_project_counts"]),
            "regular_primary_project_counts": dict(sorted(primary_counts.items(), key=lambda item: item[0].lower())),
            "regular_reserve_project_count": len(reserve_projects),
        },
        "precision_summary": {
            "regular_maximum_rate_width": data["precision"]["regular"]["maximum_rate_interval_width"],
            "regular_maximum_effect_width": data["precision"]["regular"]["maximum_paired_effect_interval_width"],
            "short_maximum_effect_width": data["precision"]["short"]["maximum_paired_effect_interval_width"],
        },
        "literature_summary": {
            "reference_count": data["literature"]["reference_count"],
            "exact_design_match_found": data["literature"]["exact_design_match_found"],
            "allowed_positioning": data["literature"]["allowed_positioning"],
        },
        "decision": DECISION_OUT.relative_to(ROOT).as_posix(),
    }
    return audit, decision


def render(audit: dict[str, Any], decision: dict[str, Any]) -> str:
    source = audit["source_summary"]
    precision = audit["precision_summary"]
    lines = [
        "# DSA 2026 P2 Source Feasibility and Protocol Decision v0.1",
        "",
        "日期：2026-07-11",
        "",
        "## 结论",
        "",
        f"P2 Gate：`{audit['status'].upper()}`。稿型冻结为 `{decision['selected_protocol']}`；Short 保留为预先模拟记录，但不再是结果不好时的 fallback。",
        "",
        "## Source feasibility",
        "",
        f"- 开发排除：{source['development_excluded_tasks']} tasks；整项目排除：{source['base_excluded_projects']} projects。",
        f"- 改进环境中 buggy=fail/fixed=pass 的新 source：{source['eligible_source_tasks']} tasks / {source['eligible_source_projects']} projects。",
        "- Regular：30 primary + 10 reserve，9 projects，每项目 primary 不超过 4，且每个 primary project 至少有 1 个 reserve。",
        f"- primary project counts：`{source['regular_primary_project_counts']}`。",
        "- source 排序由冻结 hash seed 决定；P2 未应用 transform、未查看 candidate hidden result。",
        "- SCAM 2023 改进环境结果只证明 P2 source-level feasibility；P4 仍须两次全新 clean-environment 复跑。",
        "",
        "## Transform、precision 与文献",
        "",
        "- 四类 transform 已在排除开发任务上做结构适用性验证并冻结优先级；P3 作者签核前不得用于 source。",
        f"- Regular worst rate width={precision['regular_maximum_rate_width']:.4f} <= 0.35；worst paired-effect width={precision['regular_maximum_effect_width']:.4f} <= 0.30。",
        f"- Short worst paired-effect width={precision['short_maximum_effect_width']:.4f} <= 0.40，但因 Regular 已通过而 inactive。",
        f"- 最近邻共 {audit['literature_summary']['reference_count']} 篇；未发现 exact design match。允许定位：{audit['literature_summary']['allowed_positioning']}",
        "",
        "## 边界与下一步",
        "",
        "- 未调用模型 API、未创建 prompt、未读取旧论文指标或旧 raw output。",
        "- 本轮不进入 P3。下一阶段必须由作者签核 RQ、estimands、C0--C3、transform、模型、统计、exclusion、prompt/schema 后才能继续。",
        "- V0 外部投稿许可仍并行 pending；它不否定 P2 科学 Gate，但未通过时不得提交 DSA。",
        "",
        "## Gate checks",
        "",
    ]
    lines.extend(f"- `{name}`: {'PASS' if passed else 'FAIL'}" for name, passed in audit["checks"].items())
    lines.append("")
    return "\n".join(lines)


def serialize(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    audit, decision = build()
    outputs = {
        AUDIT_OUT: serialize(audit),
        DECISION_OUT: serialize(decision),
        REPORT_OUT: render(audit, decision),
    }
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    else:
        stale = [str(path.relative_to(ROOT)) for path, content in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            raise SystemExit(f"stale or missing outputs: {stale}")
        if audit["status"] != "passed":
            raise SystemExit("P2 gate failed")
    print(json.dumps({"status": audit["status"], "selected_protocol": decision["selected_protocol"], "checks": audit["checks"]}, sort_keys=True))


if __name__ == "__main__":
    main()
