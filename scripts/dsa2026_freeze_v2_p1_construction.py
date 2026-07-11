#!/usr/bin/env python3
"""Freeze and audit the author-signed DSA v0.2 V2-P1 construction rules.

This command reads only source/protocol metadata. It never checks out a task,
builds an environment, starts a container, executes a project test, renders a
prompt, reads a model credential, or calls a model API.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_FRAME = ROOT / "data/protocols/dsa_p2_source_frame_v0_1.json"
P2_EXCLUSIONS = ROOT / "data/protocols/dsa_p2_development_exclusion_registry_v0_1.json"
P3_MANIFEST = ROOT / "data/protocols/dsa_p3_hash_manifest_v0_1.json"
REDESIGN = ROOT / "data/protocols/dsa_v0_1_termination_and_v0_2_redesign_v0_1.json"
DECLARATION = ROOT / "data/protocols/dsa_v2_p1_author_declaration_v0_1.txt"
SIGNOFF = ROOT / "docs/experiments/dsa_v0_2_construction_protocol_signoff_v0_1.md"
V2_PLAN = ROOT / "docs/plans/dsa_agent_evidence_experiment_v0_2_zh.md"

SOURCE_ORDER_OUT = ROOT / "data/protocols/dsa_v2_p1_source_order_v0_1.json"
PROTOCOL_OUT = ROOT / "data/protocols/dsa_v2_p1_construction_protocol_v0_1.json"
MANIFEST_OUT = ROOT / "data/protocols/dsa_v2_p1_hash_manifest_v0_1.json"
AUDIT_OUT = ROOT / "data/protocols/dsa_v2_p1_gate_audit_v0_1.json"
REPORT_OUT = ROOT / "docs/experiments/dsa_v2_p1_construction_freeze_v0_1.md"

EXPECTED_DECLARATION = (
    "我作为作者【高明】签核 DSA v0.2 V2-P1 材料构造协议的全部 8 项；"
    "我已审查核心问题、reviewer-agent 边界、pre-confirmatory materialization、"
    "source/exclusion、project-level environment policy、candidate qualification、"
    "30-pair/stop rule 和后续独立冻结责任。我理解该签核只授权后续 Goal 冻结 V2-P1 "
    "规则，不授权运行 task/test/container，不授权进入 V2-P2，不授权修改 prompt 或调用模型 API。"
)
EXPECTED_DECLARATION_SHA256 = "65328de6aa913bd8ee04dfdbfd172960745bc431ab7d2f7742c8aa7038dbe2ca"
SIGNED_AT = "2026-07-12T01:04:41+08:00"
SEED_DOMAIN = "DSA-V2-P1-SOURCE-ORDER-20260712-V1"
REGRESSION_SEED = "DSA-V2-P1-REGRESSION-POOL-20260712-V1"
CANDIDATE_SEED = "DSA-V2-P1-CANDIDATE-ORDER-20260712-V1"
GENERIC_TOKENS = ["init", "lib", "main", "py", "source", "src", "test", "testing", "tests"]
BASE_LOCKS = {
    "3.6.9": ("py369", "127d75b0d841583a2250c48b0a833de078b5ae45e0e606888f6928eb621c7a4e"),
    "3.7.0": ("py370", "2b79c03af7d1cffa7d8a91b0830da6ddc27e353f7ec482434173671824825b82"),
    "3.7.3": ("py373", "f5f36238a1b97f435d93a9ff7b23c5fa12b075fc616ee05e66bd2c6e72552fd5"),
    "3.7.7": ("py377", "8fd9517e7b4a6a22002488faa14b752e4de41bad6e37211a81ec8f67fe11adb7"),
    "3.8.1": ("py381", "df1e425eedcb0d3806b5bf10c55e369648621d93f46f5754cdc85f8435cf21f8"),
    "3.8.3": ("py383", "6a25cb9316d222d0bf8b53b516268668cb23b3bebc1cf3ede3d6d33dbc872144"),
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_text_bytes(path: Path, strip_terminal_newline: bool = False) -> bytes:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    if strip_terminal_newline:
        text = text.rstrip("\n")
    return text.encode("utf-8")


def canonical_sha256(path: Path, strip_terminal_newline: bool = False) -> str:
    return sha256_bytes(canonical_text_bytes(path, strip_terminal_newline))


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def serialized_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def git_head(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        text=True,
        encoding="utf-8",
    ).strip()


def normalized_command_lines(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").replace("\r", "").splitlines()
        if line.strip()
    ]


def source_seed(frame: dict[str, Any]) -> str:
    return sha256_bytes(
        f"{frame['selection_seed_sha256']}|{SEED_DOMAIN}".encode("utf-8")
    )


def stable_key(seed: str, namespace: str, value: str) -> str:
    return sha256_bytes(f"{seed}|{namespace}|{value}".encode("utf-8"))


def metadata_record(catalog: Path, source: dict[str, Any]) -> dict[str, Any]:
    bug_dir = catalog / "projects" / source["project"] / "bugs" / str(source["bug_id"])
    required = {
        "bug_info": bug_dir / "bug.info",
        "reference_patch": bug_dir / "bug_patch.txt",
        "run_test": bug_dir / "run_test.sh",
    }
    missing = [name for name, path in required.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"{source['task_id']} missing metadata: {missing}")
    setup = bug_dir / "setup.sh"
    requirements = bug_dir / "requirements.txt"
    catalog_commands = normalized_command_lines(required["run_test"])
    metadata_hashes = {
        name: sha256_file(path) for name, path in sorted(required.items())
    }
    if requirements.is_file():
        metadata_hashes["requirements"] = sha256_file(requirements)
    if setup.is_file():
        metadata_hashes["setup_provenance_only"] = sha256_file(setup)
    return {
        "task_id": source["task_id"],
        "project": source["project"],
        "bug_id": source["bug_id"],
        "python_version": source["python_version"],
        "test_framework": source["test_framework"],
        "buggy_commit_id": source["buggy_commit_id"],
        "fixed_commit_id": source["fixed_commit_id"],
        "declared_test_file": source["declared_test_file"],
        "declared_f2p_commands": source["declared_f2p_commands"],
        "catalog_f2p_commands": catalog_commands,
        "f2p_command_match": source["declared_f2p_commands"] == catalog_commands,
        "environment_risk_tags": source["environment_risk_tags"],
        "requirements_metadata": {
            "present": requirements.is_file(),
            "nonempty": requirements.is_file() and requirements.stat().st_size > 0,
        },
        "metadata_sha256": metadata_hashes,
        "official_setup_executable_authority": False,
        "candidate_materialized": False,
        "candidate_outcome_observed": False,
        "model_outcome_observed": False,
    }


def round_robin_order(
    records: list[dict[str, Any]], seed: str
) -> tuple[list[dict[str, Any]], list[str]]:
    projects = sorted(
        {record["project"] for record in records},
        key=lambda project: (stable_key(seed, "project", project), project.lower()),
    )
    queues = {
        project: deque(
            sorted(
                [record for record in records if record["project"] == project],
                key=lambda record: (
                    stable_key(seed, f"task:{project}", record["task_id"]),
                    record["task_id"],
                ),
            )
        )
        for project in projects
    }
    ordered: list[dict[str, Any]] = []
    round_index = 0
    while any(queues[project] for project in projects):
        round_index += 1
        for project_position, project in enumerate(projects, 1):
            if not queues[project]:
                continue
            record = queues[project].popleft()
            ordered.append(
                {
                    "order": len(ordered) + 1,
                    "round": round_index,
                    "project_position": project_position,
                    "project_order_sha256": stable_key(seed, "project", project),
                    "task_order_sha256": stable_key(
                        seed, f"task:{project}", record["task_id"]
                    ),
                    **record,
                }
            )
    return ordered, projects


def build_source_order(catalog: Path) -> dict[str, Any]:
    frame = read_json(SOURCE_FRAME)
    redesign = read_json(REDESIGN)
    p2_exclusions = read_json(P2_EXCLUSIONS)
    v0_1_exclusions = set(
        redesign["v0_1_termination"]["v0_2_development_exclusion_task_ids"]
    )
    p2_excluded_tasks = set(p2_exclusions["excluded_task_ids"])
    p2_excluded_projects = set(p2_exclusions["base_project_exclusions"])
    eligible_sources = [
        record
        for record in frame["records"]
        if record["eligible_for_source_frame"]
        and record["task_id"] not in v0_1_exclusions
    ]
    seed = source_seed(frame)
    metadata = [metadata_record(catalog, record) for record in eligible_sources]
    ordered, projects = round_robin_order(metadata, seed)
    task_ids = [record["task_id"] for record in ordered]
    project_counts = Counter(record["project"] for record in ordered)
    return {
        "source_order_id": "dsa_v2_p1_source_order_v0_1",
        "created_date": "2026-07-12",
        "status": "frozen_after_v2_p1_author_signoff",
        "source_frame": SOURCE_FRAME.relative_to(ROOT).as_posix(),
        "official_catalog": {
            "repository": frame["official_source"]["repository"],
            "expected_commit": frame["official_source"]["catalog_commit"],
            "actual_commit": git_head(catalog),
        },
        "selection_seed": {
            "p2_seed_sha256": frame["selection_seed_sha256"],
            "domain": SEED_DOMAIN,
            "v2_seed_sha256": seed,
        },
        "selection_rule": {
            "project_order": "ascending SHA-256(seed|project|project), then lowercase project",
            "within_project_order": "ascending SHA-256(seed|task:<project>|task_id), then task_id",
            "global_order": "round-robin one task per nonempty project queue until all eligible tasks are exhausted",
            "qualification_use": "process in this order; freeze the first 30 fully qualified pairs",
            "candidate_or_model_outcome_used": False,
        },
        "project_order": projects,
        "source_frame_eligible_count_before_v0_1_exclusion": frame["eligible_record_count"],
        "v0_1_development_exclusion_task_ids": sorted(v0_1_exclusions),
        "eligible_task_count": len(ordered),
        "eligible_project_count": len(projects),
        "eligible_project_counts": dict(sorted(project_counts.items())),
        "task_ids_sha256": sha256_bytes(canonical_json_bytes(task_ids)),
        "records": ordered,
        "checks_internal": {
            "p2_development_tasks_absent": not (set(task_ids) & p2_excluded_tasks),
            "p2_excluded_projects_absent": not (
                {record["project"] for record in ordered} & p2_excluded_projects
            ),
            "v0_1_active_tasks_absent": not (set(task_ids) & v0_1_exclusions),
            "all_f2p_commands_match_catalog": all(
                record["f2p_command_match"] for record in ordered
            ),
            "all_orders_contiguous": [record["order"] for record in ordered]
            == list(range(1, len(ordered) + 1)),
            "all_tasks_unique": len(task_ids) == len(set(task_ids)),
            "no_candidate_or_model_outcome": all(
                not record["candidate_materialized"]
                and not record["candidate_outcome_observed"]
                and not record["model_outcome_observed"]
                for record in ordered
            ),
        },
        "boundary": "Source metadata/order freeze only; no task checkout, environment, candidate, test, packet, prompt, or model request was created or executed.",
    }


def project_recipe_templates(source_order: dict[str, Any]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in source_order["records"]:
        grouped[record["project"]].append(record)
    recipes = []
    for project in source_order["project_order"]:
        records = grouped[project]
        frameworks = sorted({record["test_framework"] for record in records})
        versions = sorted({record["python_version"] for record in records})
        recipes.append(
            {
                "project": project,
                "eligible_task_count": len(records),
                "python_versions": versions,
                "test_frameworks": frameworks,
                "freeze_timing": "instantiate and hash before the first V2-P2 task outcome for this project",
                "command_template": [
                    "create a fresh Linux environment at the task-declared Python version",
                    "install frozen bootstrap pip/setuptools/wheel and the declared test framework",
                    "install the task's official requirements.txt when non-empty",
                    "install the buggy checkout with `python -m pip install -e .` so project-declared runtime dependencies are resolved",
                    "run `python -m pip check`, export the complete dependency lock, and bind the image ID",
                ],
                "same_template_for_all_project_tasks": True,
                "official_setup_sh_role": "provenance hash only; never executed as dependency authority",
                "post_outcome_task_specific_repair": "forbidden",
                "candidate_role_environment_equality": "oracle-positive and every partial-fix candidate use the same frozen task-image ID",
                "network_boundary": "network is allowed only while building the frozen image; every qualification run uses network=none and no shared writable mount",
            }
        )
    return recipes


def build_protocol(source_order: dict[str, Any]) -> dict[str, Any]:
    declaration_text = DECLARATION.read_text(encoding="utf-8").rstrip("\r\n")
    redesign = read_json(REDESIGN)
    base_locks = []
    for version, (environment_name, expected_sha256) in BASE_LOCKS.items():
        path = (
            ROOT
            / "data/environment_locks/dsa2026_p4_bootstrap"
            / f"{environment_name}-linux-64.txt"
        )
        base_locks.append(
            {
                "python_version": version,
                "environment_name": environment_name,
                "path": path.relative_to(ROOT).as_posix(),
                "expected_sha256": expected_sha256,
                "actual_sha256": sha256_file(path),
            }
        )
    return {
        "protocol_id": "dsa_v2_p1_construction_protocol_v0_1",
        "created_date": "2026-07-12",
        "status": "immutable_author_signed_rules_only",
        "target": "DSA 2026 Regular",
        "scientific_objective": redesign["v0_2_design"]["one_sentence_argument"],
        "agent_boundary": redesign["v0_2_design"]["agent_boundary"],
        "author_signoff": {
            "status": "signed",
            "author_name": "高明",
            "recorded_at": SIGNED_AT,
            "declaration_path": DECLARATION.relative_to(ROOT).as_posix(),
            "canonicalization": "UTF-8 exact user message with terminal CR/LF removed",
            "declaration_sha256": sha256_bytes(declaration_text.encode("utf-8")),
            "confirmed_item_ids": [
                "central_question",
                "agent_boundary",
                "preconfirmatory_materialization",
                "source_and_exclusion",
                "environment_policy",
                "candidate_qualification",
                "cohort_and_stop",
                "freeze_and_responsibility",
            ],
        },
        "source": {
            "order_registry": SOURCE_ORDER_OUT.relative_to(ROOT).as_posix(),
            "eligible_task_count": source_order["eligible_task_count"],
            "eligible_project_count": source_order["eligible_project_count"],
            "v0_1_active_task_exclusion_count": len(
                source_order["v0_1_development_exclusion_task_ids"]
            ),
            "processing_rule": "attempt tasks strictly in frozen source order and retain complete disposition records",
            "cohort_rule": "freeze the first 30 fully qualified task pairs in that order",
            "stop_rule": "if the frozen eligible source order is exhausted before 30 pairs qualify, stop before V2-P3 and every model request",
        },
        "project_environment_recipe_policy": {
            "candidate_independent_base": {
                "bootstrap_packages": {
                    "pip": "20.1.1",
                    "setuptools": "47.1.1",
                    "wheel": "0.34.2",
                    "pytest": "5.4.3",
                    "packaging": "20.4",
                },
                "python_explicit_locks": base_locks,
                "lock_rule": "the task-declared Python version selects exactly one hash-matched base lock",
            },
            "recipes": project_recipe_templates(source_order),
            "allowed_dependency_authorities": [
                "task official requirements.txt",
                "project package metadata resolved by `python -m pip install -e .`",
                "frozen bootstrap/test-framework packages",
            ],
            "forbidden_authorities": [
                "decayed official setup.sh commands",
                "packages inherited from a shared historical environment",
                "task-specific dependency additions after observing a failure",
                "source/test/fixture compatibility edits",
            ],
            "failure_disposition": "record pre-confirmatory environment failure and continue to the next frozen task; do not repair and rerun the task",
        },
        "regression_oracle_construction": {
            "timing": "collect and freeze node identities on the oracle-positive fixed tree before any partial-fix candidate is materialized",
            "official_f2p": "all exact catalog run_test.sh commands; always visible and excluded from the regression pool",
            "test_scope": "project test root declared by the frozen project recipe; no task-specific scope shrink after collection begins",
            "tokenization": "lowercase [a-z0-9]+ tokens of length >=2 from changed source paths and collected node IDs",
            "discarded_generic_tokens": GENERIC_TOKENS,
            "relatedness": "count distinct exact source-path tokens shared with each non-F2P node ID",
            "order": "relatedness descending, then SHA-256 tie ascending, then node ID ascending",
            "tie_preimage": f"{REGRESSION_SEED}|<task_id>|<nodeid>",
            "maximum_pool_nodes": 40,
            "dual_positive_stability": "run the pool in two fresh isolated oracle-positive containers and retain only nodes that pass with identical normalized outcomes",
            "visible_p2p_count": 3,
            "hidden_count": 20,
            "split_rule": "first three stable nodes are visible P2P; the next up to 20 are hidden; require at least three visible and one hidden node",
        },
        "candidate_generation": {
            "input": "source-only official reference patch; every test-path edit is excluded",
            "candidate_classes_in_priority_order": [
                {
                    "id": "T1_omit_one_source_file",
                    "enumeration": "one candidate per source file when at least two source files contain reference edits; omit all reference edits for that file",
                },
                {
                    "id": "T2_omit_one_hunk",
                    "enumeration": "one candidate per source hunk when at least two source hunks exist; omit that hunk",
                },
                {
                    "id": "T3_omit_one_edit_block",
                    "enumeration": "one candidate per contiguous added/removed edit block when at least two edit blocks exist; omit that block",
                },
                {
                    "id": "T4_revert_one_changed_line",
                    "enumeration": "one candidate per source changed line when at least two changed lines exist; reverse that one reference edit using the source newline style",
                },
            ],
            "descriptor": "canonical JSON over class ID, path, hunk index, edit-block index, line index, edit kind, and raw line value; unused fields are null",
            "within_class_order": "ascending SHA-256(candidate-order seed|task_id|canonical descriptor), then canonical descriptor bytes",
            "tie_preimage": f"{CANDIDATE_SEED}|<task_id>|<canonical_descriptor>",
            "deduplication": "discard candidates whose patch/tree hash equals buggy, oracle-positive, or an earlier generated candidate",
            "selection": "execute in frozen class/descriptor order and select the first candidate satisfying every hard-negative qualification rule",
            "manual_candidate_repair_or_reordering": "forbidden",
        },
        "qualification": {
            "fresh_run_count": 2,
            "isolation": "same frozen task-image ID, network=none, no shared writable mount, distinct fresh containers",
            "oracle_positive": [
                "patch applies exactly to the frozen buggy tree",
                "syntax/import/static basic checks pass",
                "all official visible F2P commands pass",
                "all three visible P2P nodes pass",
                "all frozen hidden nodes pass",
                "both fresh runs agree on normalized outcomes",
            ],
            "hard_negative": [
                "patch applies exactly and differs from both buggy and oracle-positive trees",
                "syntax/import/static basic checks pass",
                "all official visible F2P commands pass",
                "all three visible P2P nodes pass",
                "at least one independent hidden node fails",
                "both fresh runs agree on every required pass and the qualifying hidden failure",
            ],
            "task_admission": "admit exactly one oracle-positive plus the first qualifying hard negative; otherwise record materialization failure",
            "model_outcome_used": False,
        },
        "execution_cursor": {
            "state_transition": "pending -> environment-qualified -> oracle-qualified -> candidate-search -> pair-qualified or materialization-failed",
            "advance": "advance exactly once to the next frozen source-order record after a terminal pair-qualified/materialization-failed disposition",
            "rerun_after_terminal_disposition": "forbidden",
        },
        "current_authorization": {
            "v2_p1_rules_frozen": True,
            "v2_p2_materialization": False,
            "task_checkout": False,
            "environment_build": False,
            "container_run": False,
            "project_test": False,
            "prompt_change": False,
            "prompt_render": False,
            "model_api": False,
            "paper_result_change": False,
        },
        "next_gate": "A separate user-authorized Goal may implement V2-P2 executors and run a check-only dry-run against synthetic metadata; real task/container/test materialization still requires explicit V2-P2 authorization.",
    }


def p3_manifest_intact() -> bool:
    manifest = read_json(P3_MANIFEST)
    return (
        manifest["status"] == "immutable_author_signed"
        and manifest["aggregate_sha256"]
        == "f81ba7063297dc9264041256b99a7daa002bd730cbe1dbd9bfb105cd7aa71297"
        and all(
            canonical_sha256(ROOT / record["path"]) == record["sha256"]
            for record in manifest["files"]
        )
    )


def render_report(
    source_order: dict[str, Any], protocol: dict[str, Any], checks: dict[str, bool]
) -> str:
    first_tasks = source_order["records"][:12]
    lines = [
        "# DSA v0.2 V2-P1 材料构造协议冻结记录",
        "",
        "日期：2026-07-12",
        "状态：`PASS / AUTHOR_SIGNED / RULES_FROZEN / V2-P2_NOT_AUTHORIZED / NO_API`",
        "",
        "## 1. 结果",
        "",
        "作者高明签核的8项声明已保存、哈希绑定并与机器协议逐项对应。V2-P1 只冻结",
        "材料构造规则和完整 source order；没有 checkout、环境构建、container、project test、",
        "candidate outcome、prompt render 或模型请求。",
        "",
        f"- author declaration SHA-256：`{protocol['author_signoff']['declaration_sha256']}`；",
        f"- eligible tasks：{source_order['eligible_task_count']}；",
        f"- projects：{source_order['eligible_project_count']}；",
        f"- frozen source-order SHA-256：`{source_order['task_ids_sha256']}`；",
        "- target：机械顺序中前30个完整 oracle-positive/hard-negative pairs；",
        "- source 耗尽不足30 pairs：在 V2-P3/API 前停止。",
        "",
        "## 2. Source order 前12项",
        "",
        "| order | round | project | task | framework |",
        "|---:|---:|---|---|---|",
    ]
    lines.extend(
        f"| {item['order']} | {item['round']} | {item['project']} | `{item['task_id']}` | {item['test_framework']} |"
        for item in first_tasks
    )
    lines.extend(
        [
            "",
            "完整299项及所有 official metadata hashes 位于",
            "`data/protocols/dsa_v2_p1_source_order_v0_1.json`。顺序使用 domain-separated",
            "SHA-256 project/task keys 做 project round-robin，不读取 candidate 或 model outcome。",
            "",
            "## 3. 冻结构造规则",
            "",
            "- 环境：每个 project 在首个 outcome 前实例化同一 recipe template；使用 task",
            "  requirements、project package metadata、六个 hash-bound Python explicit locks",
            "  和 pip20.1.1/setuptools47.1.1/wheel0.34.2/pytest5.4.3/packaging20.4；",
            "  不执行腐化 `setup.sh`；",
            "  task 失败后禁止定向补依赖或兼容修补。",
            "- regression oracle：fixed tree 上先冻结最多40个相关 nodes；双 fresh positive",
            "  稳定通过后，前3个作 visible P2P、随后最多20个作 hidden，至少需3+1。",
            "- candidate：按 T1 file、T2 hunk、T3 edit block、T4 changed line 的固定优先级",
            "  枚举；类内按 descriptor hash；选择第一个 visible 全过且 hidden 稳定失败者。",
            "- positive/negative 均需两个 distinct fresh、network-none、mount-free containers；",
            "  语法/basic 或任何 visible failure 都不能成为 hard negative。",
            "",
            "## 4. Gate checks",
            "",
        ]
    )
    lines.extend(
        f"- `{name}`: {'PASS' if passed else 'FAIL'}" for name, passed in checks.items()
    )
    lines.extend(
        [
            "",
            "## 5. 当前边界",
            "",
            "V2-P1 完成不等于 V2-P2 授权。下一 Goal 最多可实现 executor 和 synthetic",
            "check-only dry-run；真实 task checkout、environment、container/test 和 model API",
            "仍需新的明确授权。prompt/schema 保持 v0.1 冻结文件不变且当前不执行。",
            "",
            "机器协议：`data/protocols/dsa_v2_p1_construction_protocol_v0_1.json`。",
            "机器审计：`data/protocols/dsa_v2_p1_gate_audit_v0_1.json`。",
            "冻结 manifest：`data/protocols/dsa_v2_p1_hash_manifest_v0_1.json`。",
        ]
    )
    return "\n".join(lines) + "\n"


def build_outputs(catalog: Path) -> dict[Path, str]:
    source_order = build_source_order(catalog)
    protocol = build_protocol(source_order)
    declaration_text = DECLARATION.read_text(encoding="utf-8").rstrip("\r\n")
    signoff_text = SIGNOFF.read_text(encoding="utf-8")
    design = read_json(REDESIGN)
    confirmed = protocol["author_signoff"]["confirmed_item_ids"]
    source_checks = source_order["checks_internal"]
    checks = {
        "author_declaration_exact": declaration_text == EXPECTED_DECLARATION,
        "author_declaration_sha256": protocol["author_signoff"]["declaration_sha256"]
        == EXPECTED_DECLARATION_SHA256,
        "author_signed_all_eight_items": len(confirmed) == 8 and len(set(confirmed)) == 8,
        "signoff_document_bound": (
            "AUTHOR_SIGNED / V2-P1_RULE_FREEZE_AUTHORIZED" in signoff_text
            and EXPECTED_DECLARATION_SHA256 in signoff_text
            and SIGNED_AT in signoff_text
        ),
        "p3_v0_1_manifest_intact": p3_manifest_intact(),
        "official_catalog_commit_match": source_order["official_catalog"]["actual_commit"]
        == source_order["official_catalog"]["expected_commit"],
        "eligible_count_is_299": source_order["eligible_task_count"] == 299,
        "eligible_projects_are_nine": source_order["eligible_project_count"] == 9,
        "p2_development_tasks_absent": source_checks["p2_development_tasks_absent"],
        "p2_excluded_projects_absent": source_checks["p2_excluded_projects_absent"],
        "v0_1_active_tasks_absent": source_checks["v0_1_active_tasks_absent"],
        "all_f2p_commands_match_catalog": source_checks["all_f2p_commands_match_catalog"],
        "source_order_contiguous_unique": source_checks["all_orders_contiguous"]
        and source_checks["all_tasks_unique"],
        "source_order_is_pre_outcome": source_checks["no_candidate_or_model_outcome"],
        "project_recipes_cover_all_projects": len(
            protocol["project_environment_recipe_policy"]["recipes"]
        )
        == source_order["eligible_project_count"],
        "base_python_locks_complete_and_hash_matched": (
            len(protocol["project_environment_recipe_policy"]["candidate_independent_base"]["python_explicit_locks"])
            == 6
            and all(
                item["actual_sha256"] == item["expected_sha256"]
                for item in protocol["project_environment_recipe_policy"]["candidate_independent_base"]["python_explicit_locks"]
            )
        ),
        "official_setup_is_not_executable_authority": all(
            recipe["official_setup_sh_role"]
            == "provenance hash only; never executed as dependency authority"
            for recipe in protocol["project_environment_recipe_policy"]["recipes"]
        ),
        "candidate_order_has_four_frozen_classes": len(
            protocol["candidate_generation"]["candidate_classes_in_priority_order"]
        )
        == 4,
        "qualification_requires_dual_visible_pass_hidden_fail": (
            protocol["qualification"]["fresh_run_count"] == 2
            and any(
                "all three visible P2P nodes pass" in rule
                for rule in protocol["qualification"]["hard_negative"]
            )
            and any(
                "at least one independent hidden node fails" in rule
                for rule in protocol["qualification"]["hard_negative"]
            )
        ),
        "target_and_source_exhaustion_stop_frozen": (
            design["v0_2_design"]["target_task_pairs"] == 30
            and "first 30" in protocol["source"]["cohort_rule"]
            and "exhausted" in protocol["source"]["stop_rule"]
        ),
        "no_v2_p2_or_api_authorization": (
            protocol["current_authorization"]["v2_p2_materialization"] is False
            and protocol["current_authorization"]["task_checkout"] is False
            and protocol["current_authorization"]["container_run"] is False
            and protocol["current_authorization"]["project_test"] is False
            and protocol["current_authorization"]["prompt_change"] is False
            and protocol["current_authorization"]["model_api"] is False
        ),
    }
    report = render_report(source_order, protocol, checks)
    source_content = serialized_json(source_order)
    protocol_content = serialized_json(protocol)
    authoritative_contents: list[tuple[str, bytes]] = [
        (DECLARATION.relative_to(ROOT).as_posix(), canonical_text_bytes(DECLARATION, True)),
        (REDESIGN.relative_to(ROOT).as_posix(), canonical_text_bytes(REDESIGN)),
        (V2_PLAN.relative_to(ROOT).as_posix(), canonical_text_bytes(V2_PLAN)),
        (SIGNOFF.relative_to(ROOT).as_posix(), canonical_text_bytes(SIGNOFF)),
        (SOURCE_FRAME.relative_to(ROOT).as_posix(), canonical_text_bytes(SOURCE_FRAME)),
        (P2_EXCLUSIONS.relative_to(ROOT).as_posix(), canonical_text_bytes(P2_EXCLUSIONS)),
        (Path(__file__).resolve().relative_to(ROOT).as_posix(), canonical_text_bytes(Path(__file__).resolve())),
        (SOURCE_ORDER_OUT.relative_to(ROOT).as_posix(), source_content.encode("utf-8")),
        (PROTOCOL_OUT.relative_to(ROOT).as_posix(), protocol_content.encode("utf-8")),
        (REPORT_OUT.relative_to(ROOT).as_posix(), report.encode("utf-8")),
    ]
    for environment_name, _ in BASE_LOCKS.values():
        lock_path = (
            ROOT
            / "data/environment_locks/dsa2026_p4_bootstrap"
            / f"{environment_name}-linux-64.txt"
        )
        authoritative_contents.append(
            (lock_path.relative_to(ROOT).as_posix(), canonical_text_bytes(lock_path))
        )
    manifest_files = [
        {"path": path, "sha256": sha256_bytes(content), "canonical_utf8_bytes": len(content)}
        for path, content in authoritative_contents
    ]
    aggregate_input = b"".join(
        f"{record['path']}\0{record['sha256']}\n".encode("utf-8")
        for record in manifest_files
    )
    manifest = {
        "manifest_id": "dsa_v2_p1_hash_manifest_v0_1",
        "created_date": "2026-07-12",
        "status": "immutable_author_signed_rules_only",
        "hash_algorithm": "SHA-256 over UTF-8 text after CRLF/CR normalization to LF; author declaration also strips terminal LF",
        "aggregate_algorithm": "SHA-256 over ordered UTF-8 path, NUL, lowercase file hash, LF records",
        "aggregate_sha256": sha256_bytes(aggregate_input),
        "files": manifest_files,
        "excluded_derived_paths": [
            MANIFEST_OUT.relative_to(ROOT).as_posix(),
            AUDIT_OUT.relative_to(ROOT).as_posix(),
        ],
        "immutability_boundary": "V2-P1 construction rules and source order only; no task outcome, final cohort, prompt/model/statistical freeze, or API authorization.",
    }
    checks["all_gate_checks_pass"] = all(checks.values())
    audit = {
        "audit_id": "dsa_v2_p1_gate_audit_v0_1",
        "created_date": "2026-07-12",
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "author_declaration_sha256": EXPECTED_DECLARATION_SHA256,
        "source_order_sha256": source_order["task_ids_sha256"],
        "manifest_aggregate_sha256": manifest["aggregate_sha256"],
        "counts": {
            "eligible_tasks": source_order["eligible_task_count"],
            "eligible_projects": source_order["eligible_project_count"],
            "v0_1_active_task_exclusions": len(
                source_order["v0_1_development_exclusion_task_ids"]
            ),
            "target_pairs": 30,
            "model_api_calls": 0,
        },
        "boundary": "Check-only V2-P1 freeze: no checkout, environment build, container, project test, candidate outcome, prompt change/render, paper result, or model request.",
    }
    return {
        SOURCE_ORDER_OUT: source_content,
        PROTOCOL_OUT: protocol_content,
        REPORT_OUT: report,
        MANIFEST_OUT: serialized_json(manifest),
        AUDIT_OUT: serialized_json(audit),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog-root", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs(Path(args.catalog_root).resolve())
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
            raise SystemExit(f"stale or missing V2-P1 outputs: {stale}")
    audit = json.loads(outputs[AUDIT_OUT])
    if audit["status"] != "passed":
        failed = [name for name, passed in audit["checks"].items() if not passed]
        raise SystemExit(f"V2-P1 gate failed: {failed}")
    print(
        json.dumps(
            {
                "status": audit["status"],
                "eligible_tasks": audit["counts"]["eligible_tasks"],
                "eligible_projects": audit["counts"]["eligible_projects"],
                "source_order_sha256": audit["source_order_sha256"],
                "manifest_aggregate_sha256": audit["manifest_aggregate_sha256"],
                "model_api_calls": 0,
                "v2_p2_authorized": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
