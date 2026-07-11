"""Reproduce legacy validity failures and enforce the DSA quarantine boundary.

This P1 audit is deterministic and never calls a model API.  It uses synthetic
empty patch/test inputs when exercising the retired packet constructors, so no
legacy patch text, prompt text, raw response, or credential is read.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_evp8_deepseek_qwen_smoke as base_runner  # noqa: E402
import run_evp8_e6_no_verdict_ablation as no_verdict_runner  # noqa: E402


DENYLIST_PATH = REPO_ROOT / "data/protocols/dsa_legacy_analysis_denylist_v0_1.json"
AUDIT_JSON_PATH = REPO_ROOT / "data/protocols/dsa_legacy_quarantine_audit_v0_1.json"
EXCLUSION_PATH = REPO_ROOT / "data/protocols/dsa_legacy_task_exclusion_registry_v0_1.json"
AUDIT_MD_PATH = REPO_ROOT / "docs/experiments/dsa_legacy_quarantine_audit_v0_1.md"
CONFIG_PATHS = (
    REPO_ROOT / "configs/evp8_deepseek_qwen_accept_v0_2.example.json",
    REPO_ROOT / "configs/evp8_qwen_first_main_v0_3.example.json",
)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def display(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def walk(value: Any, prefix: str = "") -> Iterable[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            yield path, item
            yield from walk(item, path)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk(item, f"{prefix}[{index}]")


def synthetic_legacy_packets(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Exercise the retired constructor without opening legacy patch sources."""
    spec = read_json(REPO_ROOT / str(config["protocol_spec"]))
    candidate_set = read_json(REPO_ROOT / str(config["candidate_set"]))
    levels = {item["level"]: item for item in spec["evidence_ladder"]}
    scope = config["full"]
    packets: list[dict[str, Any]] = []
    empty_artifacts = {
        "mode": str(config.get("evidence_source_mode") or "placeholder_not_run"),
        "visible_test_outcomes": {},
        "visible_tool_summaries": {},
        "tool_only_decisions": {},
    }
    for candidate in candidate_set["records"]:
        source = {
            "evp7_candidate_id": candidate["source_candidate_id"],
            "model_visible_seed": {
                "issue_summary": None,
                "patch_text": "",
                "touched_files": list(candidate.get("touched_files") or []),
            },
            "visible_tests": [],
            "validation_summary": {},
        }
        groups = base_runner._visible_field_groups(candidate, source, "full", empty_artifacts)
        for level_name in scope["levels"]:
            level = levels[level_name]
            field_names = list(level.get("model_visible_field_groups") or [])
            packets.append(
                {
                    "cohort_id": "EVP-8",
                    "evidence_level": level_name,
                    "anonymous_candidate_id": candidate["evp8_candidate_id"],
                    "visible_fields": {
                        name: groups[name] for name in field_names if name in groups
                    },
                }
            )
    return packets


def reproduce_nested_verdict(packets: list[dict[str, Any]]) -> dict[str, Any]:
    e6_packets = [packet for packet in packets if packet["evidence_level"] == "E6"]
    stripped = [no_verdict_runner.strip_verdict_fields(packet) for packet in e6_packets]
    nested_path = (
        "visible_fields.visible_pass_to_pass_regression_evidence."
        "visible_tests_rule_decision"
    )
    nested_count = 0
    leaked_paths: Counter[str] = Counter()
    removed_top_level_remaining = 0
    for packet in stripped:
        summary = packet["visible_fields"].get("deterministic_visible_merge_gate_summary") or {}
        removed_top_level_remaining += sum(
            key in summary for key in no_verdict_runner.REMOVED_VERDICT_FIELDS
        )
        for path, _ in walk(packet):
            normalized = path.replace("[0]", "[]")
            if path == nested_path:
                nested_count += 1
            if path.endswith("visible_tests_rule_decision"):
                leaked_paths[normalized] += 1
    passed = (
        len(stripped) == 98
        and nested_count == 98
        and removed_top_level_remaining == 0
    )
    return {
        "condition": "E6-no-verdict",
        "packet_count": len(stripped),
        "removed_top_level_verdict_fields_remaining": removed_top_level_remaining,
        "nested_rule_decision_count": nested_count,
        "nested_rule_decision_paths": dict(sorted(leaked_paths.items())),
        "failure_reproduced": passed,
    }


def materialization_summary(packets: list[dict[str, Any]]) -> dict[str, Any]:
    marker_counts: Counter[str] = Counter()
    empty_p2p_counts: Counter[str] = Counter()
    for packet in packets:
        for path, value in walk(packet):
            if isinstance(value, str):
                if "not_run" in value:
                    marker_counts[f"{path}::not_run"] += 1
                if "not_separately_materialized" in value:
                    marker_counts[f"{path}::not_separately_materialized"] += 1
                if "not_recorded" in value:
                    marker_counts[f"{path}::not_recorded"] += 1
            if value == [] and (
                path.endswith("visible_pass_to_pass_test_names")
                or path.endswith("visible_pass_to_pass_outcomes")
            ):
                empty_p2p_counts[path] += 1
    return {
        "packet_count": len(packets),
        "placeholder_path_counts": dict(sorted(marker_counts.items())),
        "empty_p2p_path_counts": dict(sorted(empty_p2p_counts.items())),
        "incomplete_evidence_reproduced": bool(marker_counts and empty_p2p_counts),
    }


def collect_task_project_pairs(value: Any) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    if isinstance(value, dict):
        task_id = value.get("task_id")
        project = value.get("project")
        if isinstance(task_id, str) and isinstance(project, str):
            pairs.append((task_id, project))
        for item in value.values():
            pairs.extend(collect_task_project_pairs(item))
    elif isinstance(value, list):
        for item in value:
            pairs.extend(collect_task_project_pairs(item))
    return pairs


def exclusion_registry(denylist: dict[str, Any]) -> dict[str, Any]:
    tasks: set[str] = set()
    projects: set[str] = set()
    source_counts: dict[str, int] = {}
    for relative in denylist["safe_metadata_sources_for_exclusion_only"]:
        path = REPO_ROOT / relative
        if path.suffix == ".jsonl":
            values = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
        else:
            values = [read_json(path)]
        pairs: list[tuple[str, str]] = []
        for value in values:
            pairs.extend(collect_task_project_pairs(value))
            summary = value.get("candidate_summary") if isinstance(value, dict) else None
            if isinstance(summary, dict):
                tasks.update((summary.get("task_counts") or {}).keys())
                projects.update((summary.get("project_counts") or {}).keys())
        tasks.update(task for task, _ in pairs)
        projects.update(project for _, project in pairs)
        source_counts[relative] = len(pairs)
    return {
        "registry_id": "dsa_legacy_task_exclusion_registry_v0_1",
        "effective_date": "2026-07-11",
        "status": "active",
        "purpose": "P2 source and task disjointness exclusion only",
        "source_record_pair_counts": source_counts,
        "excluded_task_count": len(tasks),
        "excluded_project_count": len(projects),
        "excluded_task_ids": sorted(tasks),
        "excluded_projects": sorted(projects, key=str.lower),
        "not_a_candidate_pool": True,
    }


def retired_prompt_audit(denylist: dict[str, Any]) -> dict[str, Any]:
    change_log = (REPO_ROOT / "prompts/prompt_change_log.md").read_text(encoding="utf-8")
    records = []
    for item in denylist["retired_prompts"]:
        path = REPO_ROOT / item["path"]
        records.append(
            {
                **item,
                "absent": not path.exists(),
                "path_and_hash_recorded_in_change_log": (
                    item["path"] in change_log
                    and item["sha256_before_deletion"] in change_log
                ),
            }
        )
    return {
        "records": records,
        "all_absent": all(item["absent"] for item in records),
        "all_paths_and_hashes_recorded": all(
            item["path_and_hash_recorded_in_change_log"] for item in records
        ),
    }


def namespace_audit(denylist: dict[str, Any]) -> dict[str, Any]:
    violations: list[dict[str, str]] = []
    paths = sorted(REPO_ROOT.glob(denylist["scope"]["analysis_namespace_glob"]))
    forbidden_tokens = [token.lower() for token in denylist["forbidden_identifiers_in_dsa_analysis"]]
    forbidden_tokens.extend(
        path.lower() for path in denylist["forbidden_generator_scripts"]
    )
    forbidden_tokens.extend(
        glob.lower().replace("*", "") for glob in denylist["forbidden_input_globs"]
    )
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in sorted(set(forbidden_tokens)):
            if token and token in text:
                violations.append({"script": display(path), "forbidden_token": token})
    return {
        "namespace_glob": denylist["scope"]["analysis_namespace_glob"],
        "scanned_scripts": [display(path) for path in paths],
        "violations": violations,
        "passed": not violations,
        "note": "zero scripts is valid at P1; this guard must be rerun after every new DSA script",
    }


def build_outputs() -> tuple[dict[str, Any], dict[str, Any], str]:
    denylist = read_json(DENYLIST_PATH)
    materialization: dict[str, Any] = {}
    reference_packets: list[dict[str, Any]] | None = None
    for config_path in CONFIG_PATHS:
        packets = synthetic_legacy_packets(read_json(config_path))
        if reference_packets is None:
            reference_packets = packets
        materialization[display(config_path)] = materialization_summary(packets)
    assert reference_packets is not None
    leakage = reproduce_nested_verdict(reference_packets)
    prompts = retired_prompt_audit(denylist)
    namespace = namespace_audit(denylist)
    exclusion = exclusion_registry(denylist)
    checks = {
        "nested_verdict_failure_reproduced": leakage["failure_reproduced"],
        "legacy_evidence_incompleteness_reproduced": all(
            item["packet_count"] == 686 and item["incomplete_evidence_reproduced"]
            for item in materialization.values()
        ),
        "retired_prompts_absent_and_hashes_recorded": (
            prompts["all_absent"] and prompts["all_paths_and_hashes_recorded"]
        ),
        "task_project_registry_frozen": (
            exclusion["excluded_task_count"] == 28
            and exclusion["excluded_project_count"] == 8
        ),
        "dsa_namespace_guard_passed": namespace["passed"],
    }
    audit = {
        "audit_id": "dsa_legacy_quarantine_audit_v0_1",
        "audit_date": "2026-07-11",
        "status": "passed" if all(checks.values()) else "failed",
        "supersedes": denylist["supersedes"],
        "execution_boundary": {
            "api_call_attempted": False,
            "api_key_read": False,
            "raw_model_output_read": False,
            "prompt_text_read": False,
            "legacy_patch_text_read": False,
            "synthetic_empty_patch_used": True,
        },
        "checks": checks,
        "nested_verdict_reproduction": leakage,
        "evidence_materialization_reproduction": materialization,
        "retired_prompt_audit": prompts,
        "dsa_namespace_audit": namespace,
        "exclusion_registry": display(EXCLUSION_PATH),
        "conclusion": (
            "Legacy results are provenance/development evidence only and cannot support "
            "DSA paper-facing estimates or claims."
        ),
    }
    markdown = render_markdown(audit, exclusion)
    return audit, exclusion, markdown


def render_markdown(audit: dict[str, Any], exclusion: dict[str, Any]) -> str:
    leak = audit["nested_verdict_reproduction"]
    lines = [
        "# DSA 2026 旧证据隔离审计 v0.1",
        "",
        "日期：2026-07-11",
        f"状态：{audit['status'].upper()} / SUPERSEDING_AUDIT",
        "",
        "## 1. 结论",
        "",
        "旧实验只能作为 provenance、失败复盘和新任务排除依据，不能进入 DSA 的效果量、",
        "图表、claim map 或正文数字。本审计取代 2026-07-03 的 bounded-claim validity audit。",
        "",
        "## 2. 机械复现",
        "",
        f"- E6-no-verdict 合成等结构 packet：{leak['packet_count']} 个。",
        f"- 顶层已删除 verdict 字段残留：{leak['removed_top_level_verdict_fields_remaining']}。",
        f"- 嵌套 `visible_tests_rule_decision` 残留：{leak['nested_rule_decision_count']} / {leak['packet_count']}。",
        "- 两个旧 full config 均重建 686 个结构等价 packet，并再次出现 `not_run`、",
        "  `not_separately_materialized`、`not_recorded` 和空 P2P evidence。",
        "- 复现只使用空 patch/test 合成输入；未读取 prompt、patch 正文、raw response、API key，",
        "  且没有 API 调用。",
        "",
        "## 3. 排除注册表",
        "",
        f"冻结旧任务 {exclusion['excluded_task_count']} 个、旧项目 {exclusion['excluded_project_count']} 个。",
        "该集合只供 P2 做 source/task disjointness 排除，不是候选池。机器记录见",
        "`data/protocols/dsa_legacy_task_exclusion_registry_v0_1.json`。",
        "",
        "## 4. Gate",
        "",
    ]
    for name, passed in audit["checks"].items():
        lines.append(f"- `{name}`: {'PASS' if passed else 'FAIL'}")
    lines.extend(
        [
            "",
            "P1 只有在全部检查 PASS 时完成。新增或修改任何 `scripts/dsa2026_*.py` 后必须重跑",
            "`python scripts/audit_dsa_legacy_quarantine.py --check`。",
            "",
        ]
    )
    return "\n".join(lines)


def serialized_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def write_outputs(audit: dict[str, Any], exclusion: dict[str, Any], markdown: str) -> None:
    for path, content in (
        (AUDIT_JSON_PATH, serialized_json(audit)),
        (EXCLUSION_PATH, serialized_json(exclusion)),
        (AUDIT_MD_PATH, markdown),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def check_outputs(audit: dict[str, Any], exclusion: dict[str, Any], markdown: str) -> None:
    expected = {
        AUDIT_JSON_PATH: serialized_json(audit),
        EXCLUSION_PATH: serialized_json(exclusion),
        AUDIT_MD_PATH: markdown,
    }
    stale = [display(path) for path, content in expected.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
    if stale:
        raise SystemExit(f"stale or missing P1 outputs: {stale}")
    if audit["status"] != "passed":
        raise SystemExit("P1 audit checks did not all pass")


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    audit, exclusion, markdown = build_outputs()
    if args.write:
        write_outputs(audit, exclusion, markdown)
    else:
        check_outputs(audit, exclusion, markdown)
    print(json.dumps({"status": audit["status"], "checks": audit["checks"]}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
