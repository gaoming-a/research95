# ruff: noqa: E402
#!/usr/bin/env python3
"""Build and verify the no-API DSA P3 mechanical freeze artifacts."""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/dsa2026_audit_p3_freeze.py")

import argparse
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "prompts/dsa2026_evidence_conditioned_patch_gate_v0_1.md"
SCHEMA = ROOT / "data/protocols/dsa_p3_output_schema_v0_1.json"
CONTRACT = ROOT / "data/protocols/dsa_p3_evidence_contract_v0_1.json"
MODEL_FREEZE = ROOT / "data/protocols/dsa_p3_model_freeze_v0_1.json"
PREREG = ROOT / "data/protocols/dsa_p3_preregistration_v0_1.json"
AUTHOR_DECLARATION = ROOT / "data/protocols/dsa_p3_author_declaration_v0_1.txt"
DENYLIST = ROOT / "data/protocols/dsa_legacy_analysis_denylist_v0_1.json"
BOUNDARY_OUT = ROOT / "data/protocols/dsa_p3_prompt_boundary_audit_v0_1.json"
MANIFEST_OUT = ROOT / "data/protocols/dsa_p3_hash_manifest_v0_1.json"
GATE_OUT = ROOT / "data/protocols/dsa_p3_gate_audit_v0_1.json"
PLACEHOLDER = "{{EVIDENCE_PACKET_JSON}}"
AUTHOR_ITEM_IDS = [
    "research_questions_claim_boundary",
    "estimands_scientific_unit",
    "cumulative_evidence_contract",
    "p2_regular_source_and_transform_freeze",
    "outcome_classification",
    "conditional_interval_and_stability",
    "exclusion_stop_and_no_rerun",
    "model_routes_parameters_order_and_repeats",
    "new_prompt_and_output_schema",
    "unfavorable_result_reporting",
    "scientific_ai_and_authorship_responsibility",
]
P2_FREEZE_COMMIT = "cb588a0502a58434db9758fa2bfe8265697c5274"
P2_FROZEN_SHA256 = {
    "data/protocols/dsa_p2_protocol_decision_v0_1.json": "b3443c506250196885787debb00adc612cca986f2485f63462f404f64b6c1ff2",
    "data/protocols/dsa_p2_source_selection_v0_1.json": "9fe40e8a38053ffdc8c965070740704924d13b9901cf0c3ed25aa4c1be14bd4b",
    "data/protocols/dsa_p2_transform_registry_v0_1.json": "7c2eb308378b732ca2dbe9d1f7b8dc86ba836173f0346374f576093796276430",
    "data/protocols/dsa_p2_development_exclusion_registry_v0_1.json": "7e8be772ac1b7fd70fcdaae1a038940916920cbf182d55fadf36717a2dcbba38",
}
P3_ALLOWED_CHANGED_PATHS = {
    "README.md",
    "data/protocols/dsa_legacy_quarantine_audit_v0_1.json",
    "data/protocols/dsa_p3_author_declaration_v0_1.txt",
    "data/protocols/dsa_p3_evidence_contract_v0_1.json",
    "data/protocols/dsa_p3_gate_audit_v0_1.json",
    "data/protocols/dsa_p3_hash_manifest_v0_1.json",
    "data/protocols/dsa_p3_model_freeze_v0_1.json",
    "data/protocols/dsa_p3_output_schema_v0_1.json",
    "data/protocols/dsa_p3_preregistration_v0_1.json",
    "data/protocols/dsa_p3_prompt_boundary_audit_v0_1.json",
    "docs/INDEX.md",
    "docs/experience/engineering_notes.md",
    "docs/experiments/dsa_p3_author_signoff_v0_1.md",
    "docs/experiments/dsa_p3_model_provider_verification_v0_1.md",
    "docs/experiments/dsa_p3_preregistration_v0_1.md",
    "docs/experiments/dsa_p3_prompt_change_record_v0_1.md",
    "docs/plans/current_plan_zh.md",
    "docs/plans/current_project_state_zh.md",
    "docs/plans/dsa_2026_submission_execution_plan_zh.md",
    "prompts/dsa2026_evidence_conditioned_patch_gate_v0_1.md",
    "prompts/prompt_change_log.md",
    "scripts/dsa2026_audit_p3_freeze.py",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_text_bytes(path: Path) -> bytes:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return text.encode("utf-8")


def git_paths(command: list[str]) -> set[str]:
    result = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return {line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()}


def synthetic_packets() -> dict[str, dict[str, Any]]:
    context = {
        "change_request": {
            "neutral_description": (
                "A submitted patch changes boundary handling in a small parser. "
                "Assess whether the supplied information supports automatic merge."
            ),
            "candidate_diff": (
                "diff --git a/module_A.py b/module_A.py\n"
                "--- a/module_A.py\n"
                "+++ b/module_A.py\n"
                "@@ -2,2 +2,2 @@\n"
                "-    return items[index]\n"
                "+    return items[index] if index < len(items) else None"
            ),
            "code_context": [
                {
                    "path_code": "module_A.py",
                    "language": "python",
                    "content": "def read_item(items, index):\n    return items[index]",
                }
            ],
        }
    }
    environment = {
        "runtime": "CPython 3.11.9",
        "dependency_lock_sha256": "a" * 64,
        "environment_image_sha256": "b" * 64,
    }
    c0 = copy.deepcopy(context)
    c1 = copy.deepcopy(c0)
    c1["executable_basic"] = {
        "environment": copy.deepcopy(environment),
        "checks": [
            {
                "check_code": "basic_01",
                "check_kind": "patch_apply",
                "command": "git apply --check candidate.patch",
                "exit_code": 0,
                "outcome": "passed",
                "output_excerpt": "patch applies cleanly",
            },
            {
                "check_code": "basic_02",
                "check_kind": "syntax_or_import_or_static",
                "command": "python -m py_compile module_A.py",
                "exit_code": 0,
                "outcome": "passed",
                "output_excerpt": "command completed without diagnostics",
            },
        ],
    }
    c2 = copy.deepcopy(c1)
    c2["visible_f2p"] = {
        "environment": copy.deepcopy(environment),
        "checks": [
            {
                "check_code": "behavior_01",
                "test_name": "test_boundary_read",
                "command": "python -m pytest -q tests/test_boundary.py::test_boundary_read",
                "exit_code": 0,
                "outcome": "passed",
                "output_excerpt": "1 passed",
            }
        ],
    }
    c3 = copy.deepcopy(c2)
    c3["visible_p2p"] = {
        "environment": copy.deepcopy(environment),
        "checks": [
            {
                "check_code": "regression_01",
                "test_name": "test_regular_read",
                "command": "python -m pytest -q tests/test_regular.py::test_regular_read",
                "exit_code": 0,
                "outcome": "passed",
                "output_excerpt": "1 passed",
            }
        ],
    }
    return {"C0": c0, "C1": c1, "C2": c2, "C3": c3}


def walk(value: Any, path: str = "$") -> list[tuple[str, str, Any]]:
    rows: list[tuple[str, str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            rows.append((child_path, "key", key))
            rows.extend(walk(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(walk(child, f"{path}[{index}]"))
    else:
        rows.append((path, "value", value))
    return rows


def packet_violations(packet: dict[str, Any], contract: dict[str, Any]) -> list[dict[str, Any]]:
    forbidden_fragments = [item.lower() for item in contract["forbidden_visible_key_fragments"]]
    placeholder_values = {
        "",
        "not_run",
        "not_recorded",
        "not_separately_materialized",
        "placeholder",
        "unknown",
    }
    hidden_exact_values = {
        "positive",
        "negative",
        "correct",
        "incorrect",
        "oracle_positive",
        "oracle-positive",
        "hard_negative",
        "hard-negative",
        "correct_patch",
        "incorrect_patch",
    }
    hidden_substring_markers = {
        "source_decision",
        "rule_decision",
        "hidden_label",
        "expected_behavior",
    }
    violations: list[dict[str, Any]] = []
    for path, kind, raw in walk(packet):
        if kind == "key":
            lowered = str(raw).lower()
            for fragment in forbidden_fragments:
                if fragment in lowered:
                    violations.append({"path": path, "type": "forbidden_key", "fragment": fragment})
        elif isinstance(raw, str):
            lowered = raw.strip().lower()
            if lowered in placeholder_values:
                violations.append({"path": path, "type": "placeholder_value", "value": lowered})
            if lowered in hidden_exact_values:
                violations.append({"path": path, "type": "hidden_exact_value", "value": lowered})
            for marker in hidden_substring_markers:
                if marker in lowered:
                    violations.append({"path": path, "type": "hidden_value_marker", "marker": marker})
        elif raw is None:
            violations.append({"path": path, "type": "null_value"})
    return violations


def check_group(group: dict[str, Any], required_fields: list[str]) -> list[str]:
    errors: list[str] = []
    environment = group.get("environment")
    if not isinstance(environment, dict):
        errors.append("missing_environment")
    else:
        expected_environment = {
            "runtime",
            "dependency_lock_sha256",
            "environment_image_sha256",
        }
        if set(environment) != expected_environment:
            errors.append("environment_fields")
        for name in ("dependency_lock_sha256", "environment_image_sha256"):
            if not re.fullmatch(r"[0-9a-f]{64}", str(environment.get(name, ""))):
                errors.append(f"invalid_{name}")
    checks = group.get("checks")
    if not isinstance(checks, list) or not checks:
        errors.append("empty_checks")
        return errors
    for index, check in enumerate(checks):
        if set(check) != set(required_fields):
            errors.append(f"check_{index}_fields")
        for field in required_fields:
            if check.get(field) in (None, ""):
                errors.append(f"check_{index}_{field}_empty")
    return errors


def build_boundary_audit() -> dict[str, Any]:
    prompt_text = PROMPT.read_text(encoding="utf-8")
    schema = load_json(SCHEMA)
    contract = load_json(CONTRACT)
    denylist = load_json(DENYLIST)
    packets = synthetic_packets()

    required_output_fields = {
        "decision",
        "confidence",
        "concise_rationale",
        "evidence_used",
        "uncertainty",
    }
    prompt_conflict_patterns = {
        "sparse_implies_escalate": r"sparse.{0,80}escalat",
        "failed_implies_reject": r"fail(?:ed|ing)?.{0,80}reject",
        "condition_explanation": r"\bC[0-3]\b|evidence[_ -]?level|packet[_ -]?variant",
        "coverage_instruction": r"coverage[- ]?contestation|coverage challenge",
        "decision_example": r"\bexample\b",
        "tool_or_rule_verdict": r"tool verdict|rule decision|expected behavior",
    }
    prompt_conflicts = {
        name: bool(re.search(pattern, prompt_text, flags=re.IGNORECASE | re.DOTALL))
        for name, pattern in prompt_conflict_patterns.items()
    }
    normalized_instruction_lines = [
        re.sub(r"\s+", " ", line.strip().lower())
        for line in prompt_text.splitlines()
        if len(line.strip()) >= 20
        and PLACEHOLDER not in line
        and not line.strip().startswith(("<evidence_packet_json>", "</evidence_packet_json>"))
    ]
    duplicate_instruction_lines = sorted({
        line for line in normalized_instruction_lines if normalized_instruction_lines.count(line) > 1
    })

    cumulative_expected = {
        "C0": ["change_request"],
        "C1": ["change_request", "executable_basic"],
        "C2": ["change_request", "executable_basic", "visible_f2p"],
        "C3": ["change_request", "executable_basic", "visible_f2p", "visible_p2p"],
    }
    cumulative_checks: dict[str, Any] = {}
    prior_code: str | None = None
    prior_packet: dict[str, Any] | None = None
    additions = {"C1": "executable_basic", "C2": "visible_f2p", "C3": "visible_p2p"}
    for code, packet in packets.items():
        current_errors: list[str] = []
        if list(packet) != cumulative_expected[code]:
            current_errors.append("top_level_groups")
        if prior_packet is not None and prior_code is not None:
            added = additions[code]
            reduced = {key: value for key, value in packet.items() if key != added}
            if canonical_json(reduced) != canonical_json(prior_packet):
                current_errors.append(f"prior_semantics_changed_from_{prior_code}")
        for group_name in ("executable_basic", "visible_f2p", "visible_p2p"):
            if group_name in packet:
                fields = contract["evidence_group_contract"][group_name]["required_fields_per_check"]
                current_errors.extend(f"{group_name}:{item}" for item in check_group(packet[group_name], fields))
        current_errors.extend(
            f"leakage:{item['path']}:{item['type']}" for item in packet_violations(packet, contract)
        )
        cumulative_checks[code] = {
            "top_level_groups": list(packet),
            "canonical_sha256": sha256_bytes(canonical_json(packet).encode("utf-8")),
            "errors": current_errors,
            "passed": not current_errors,
        }
        prior_code = code
        prior_packet = packet

    rendered_checks: dict[str, Any] = {}
    for code, packet in packets.items():
        serialized = canonical_json(packet)
        rendered = prompt_text.replace(PLACEHOLDER, serialized)
        extracted_match = re.search(
            r"<evidence_packet_json>\s*(.*?)\s*</evidence_packet_json>",
            rendered,
            flags=re.DOTALL,
        )
        errors: list[str] = []
        if PLACEHOLDER in rendered:
            errors.append("unresolved_placeholder")
        if rendered.count(serialized) != 1:
            errors.append("packet_serialization_count")
        if extracted_match is None or extracted_match.group(1) != serialized:
            errors.append("rendered_packet_extraction")
        else:
            extracted = json.loads(extracted_match.group(1))
            if packet_violations(extracted, contract):
                errors.append("rendered_packet_leakage")
        rendered_checks[code] = {
            "rendered_sha256": sha256_bytes(rendered.encode("utf-8")),
            "rendered_text_stored": False,
            "errors": errors,
            "passed": not errors,
        }

    active_templates = sorted(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "prompts").glob("*.md")
        if path.name != "prompt_change_log.md"
    )
    retired = denylist["retired_prompts"]
    retired_absent = all(not (ROOT / item["path"]).exists() for item in retired)
    prompt_hash = sha256_bytes(canonical_text_bytes(PROMPT))
    hash_distinct = all(prompt_hash != item["sha256_before_deletion"] for item in retired)

    checks = {
        "placeholder_exactly_once": prompt_text.count(PLACEHOLDER) == 1,
        "schema_exact_fields": set(schema.get("properties", {})) == required_output_fields
        and set(schema.get("required", [])) == required_output_fields
        and schema.get("additionalProperties") is False,
        "schema_decision_enum_exact": schema.get("properties", {}).get("decision", {}).get("enum")
        == ["accept", "reject", "escalate"],
        "prompt_conflict_patterns_absent": not any(prompt_conflicts.values()),
        "prompt_duplicate_instruction_lines_absent": not duplicate_instruction_lines,
        "synthetic_cumulative_contract_passed": all(item["passed"] for item in cumulative_checks.values()),
        "synthetic_rendered_prompt_passed": all(item["passed"] for item in rendered_checks.values()),
        "active_prompt_set_exact": active_templates
        == ["prompts/dsa2026_evidence_conditioned_patch_gate_v0_1.md"],
        "retired_prompt_paths_absent": retired_absent,
        "new_prompt_hash_distinct_from_retired_hashes": hash_distinct,
        "api_call_attempted": False,
        "p4_candidate_constructed_or_run": False,
        "deleted_prompt_content_read": False,
    }
    mechanical_pass = all(value is True for key, value in checks.items() if key not in {
        "api_call_attempted", "p4_candidate_constructed_or_run", "deleted_prompt_content_read"
    }) and not any(
        checks[key] for key in ("api_call_attempted", "p4_candidate_constructed_or_run", "deleted_prompt_content_read")
    )
    return {
        "audit_id": "dsa_p3_prompt_boundary_audit_v0_1",
        "audit_date": "2026-07-11",
        "status": "passed" if mechanical_pass else "failed",
        "scope": "Synthetic no-API prompt/schema/evidence-contract audit; no P4 candidate materialization.",
        "checks": checks,
        "prompt_conflict_matches": prompt_conflicts,
        "prompt_duplicate_instruction_lines": duplicate_instruction_lines,
        "synthetic_packets": cumulative_checks,
        "synthetic_rendered_prompts": rendered_checks,
        "prompt_sha256": prompt_hash,
        "active_templates": active_templates,
        "mechanical_pass": mechanical_pass,
    }


def author_signoff_complete(prereg: dict[str, Any]) -> bool:
    signoff = prereg.get("author_signoff", {})
    author_name = signoff.get("author_name")
    signed_at = signoff.get("signed_at")
    declaration_sha256 = signoff.get("declaration_sha256")
    return (
        signoff.get("status") == "signed"
        and isinstance(author_name, str)
        and bool(author_name.strip())
        and author_name.strip() not in {"【姓名】", "[name]"}
        and isinstance(signed_at, str)
        and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}", signed_at) is not None
        and signoff.get("scientific_responsibility_confirmed") is True
        and signoff.get("required_item_ids") == AUTHOR_ITEM_IDS
        and signoff.get("items_confirmed") == AUTHOR_ITEM_IDS
        and signoff.get("declaration_source") == "codex_user_message"
        and signoff.get("declaration_path") == "data/protocols/dsa_p3_author_declaration_v0_1.txt"
        and isinstance(declaration_sha256, str)
        and re.fullmatch(r"[0-9a-f]{64}", declaration_sha256) is not None
        and AUTHOR_DECLARATION.exists()
        and sha256_bytes(AUTHOR_DECLARATION.read_text(encoding="utf-8").rstrip("\r\n").encode("utf-8"))
        == declaration_sha256
    )


def build_manifest() -> dict[str, Any]:
    prereg = load_json(PREREG)
    author_signed = author_signoff_complete(prereg)
    frozen_paths = [
        "data/protocols/dsa_p2_protocol_decision_v0_1.json",
        "data/protocols/dsa_p2_source_selection_v0_1.json",
        "data/protocols/dsa_p2_transform_registry_v0_1.json",
        "data/protocols/dsa_p2_development_exclusion_registry_v0_1.json",
        "data/protocols/dsa_p3_preregistration_v0_1.json",
        "data/protocols/dsa_p3_author_declaration_v0_1.txt",
        "data/protocols/dsa_p3_evidence_contract_v0_1.json",
        "data/protocols/dsa_p3_model_freeze_v0_1.json",
        "data/protocols/dsa_p3_output_schema_v0_1.json",
        "prompts/dsa2026_evidence_conditioned_patch_gate_v0_1.md",
        "prompts/prompt_change_log.md",
        "docs/experiments/dsa_p3_preregistration_v0_1.md",
        "docs/experiments/dsa_p3_model_provider_verification_v0_1.md",
        "docs/experiments/dsa_p3_prompt_change_record_v0_1.md",
        "docs/experiments/dsa_p3_author_signoff_v0_1.md",
        "scripts/dsa2026_audit_p3_freeze.py",
    ]
    files = []
    for relative in frozen_paths:
        path = ROOT / relative
        canonical_bytes = canonical_text_bytes(path)
        files.append({
            "path": relative,
            "sha256": sha256_bytes(canonical_bytes),
            "canonical_utf8_bytes": len(canonical_bytes),
        })
    aggregate_source = "".join(f"{item['path']}\0{item['sha256']}\n" for item in files)
    return {
        "manifest_id": "dsa_p3_hash_manifest_v0_1",
        "status": "immutable_author_signed" if author_signed else "candidate_freeze_pending_author_signoff",
        "hash_algorithm": "SHA-256 over UTF-8 text after CRLF and CR normalization to LF",
        "aggregate_algorithm": "SHA-256 over ordered UTF-8 path, NUL, lowercase file hash, LF records",
        "scope": "All authoritative P2 freeze anchors and P3 design, model, prompt, schema, change, sign-off, and auditor-source inputs.",
        "excluded_derived_paths": [
            "data/protocols/dsa_p3_prompt_boundary_audit_v0_1.json",
            "data/protocols/dsa_p3_gate_audit_v0_1.json",
            "data/protocols/dsa_p3_hash_manifest_v0_1.json"
        ],
        "exclusion_reason": "Derived audits and the manifest itself are reproducibly checked against their generators and are excluded to avoid recursive self-hashing.",
        "files": files,
        "aggregate_sha256": sha256_bytes(aggregate_source.encode("utf-8")),
        "immutable": author_signed,
        "immutability_condition": "Explicit author sign-off followed by regeneration and a passing P3 gate before P4 or any model output.",
    }


def build_gate(boundary: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    prereg = load_json(PREREG)
    contract = load_json(CONTRACT)
    model_freeze = load_json(MODEL_FREEZE)
    signoff = prereg.get("author_signoff", {})
    author_identity_recorded = (
        isinstance(signoff.get("author_name"), str)
        and bool(signoff["author_name"].strip())
        and isinstance(signoff.get("signed_at"), str)
        and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}", signoff["signed_at"]) is not None
    )
    author_items_all_confirmed = (
        signoff.get("required_item_ids") == AUTHOR_ITEM_IDS
        and signoff.get("items_confirmed") == AUTHOR_ITEM_IDS
    )
    author_declaration_recorded = (
        signoff.get("declaration_source") == "codex_user_message"
        and signoff.get("declaration_path") == "data/protocols/dsa_p3_author_declaration_v0_1.txt"
        and isinstance(signoff.get("declaration_sha256"), str)
        and re.fullmatch(r"[0-9a-f]{64}", signoff["declaration_sha256"]) is not None
        and AUTHOR_DECLARATION.exists()
        and sha256_bytes(AUTHOR_DECLARATION.read_text(encoding="utf-8").rstrip("\r\n").encode("utf-8"))
        == signoff["declaration_sha256"]
    )
    author_signed = author_signoff_complete(prereg)
    p2_actual_hashes = {relative: sha256_file(ROOT / relative) for relative in P2_FROZEN_SHA256}
    changed_paths = git_paths(["git", "diff", "--name-only", P2_FREEZE_COMMIT]) | git_paths(
        ["git", "ls-files", "--others", "--exclude-standard"]
    )
    unexpected_changed_paths = sorted(changed_paths - P3_ALLOWED_CHANGED_PATHS)
    conditions = contract.get("conditions", [])
    model_routes = model_freeze.get("model_routes", [])
    interval = prereg.get("conditional_interval", {})
    outcomes = prereg.get("outcomes", {})
    design = prereg.get("design", {})
    expected_freeze_status = "frozen_after_author_signoff" if author_signed else "candidate_freeze_pending_author_signoff"
    checks = {
        "p2_regular_unchanged": load_json(ROOT / "data/protocols/dsa_p2_protocol_decision_v0_1.json").get("selected_protocol") == "Regular",
        "p2_frozen_hashes_unchanged": p2_actual_hashes == P2_FROZEN_SHA256,
        "p3_change_scope_only": not unexpected_changed_paths,
        "preregistration_complete": all(
            key in prereg
            for key in (
                "research_questions",
                "estimands",
                "outcomes",
                "conditional_interval",
                "exclusion_and_replacement",
                "stop_rules",
                "no_rerun_policy",
            )
        ),
        "three_research_questions_frozen": [item.get("rq") for item in prereg.get("research_questions", [])]
        == ["RQ1", "RQ2", "RQ3"],
        "primary_estimands_exact": [item.get("name") for item in prereg.get("estimands", {}).get("primary", [])]
        == ["Delta_minus", "Delta_plus"],
        "scientific_unit_task_n30": design.get("scientific_analysis_unit") == "task"
        and design.get("finite_cohort_n") == 30,
        "outcome_classes_frozen": outcomes.get("primary") == ["Delta_minus", "Delta_plus"]
        and bool(outcomes.get("secondary"))
        and bool(outcomes.get("descriptive_only")),
        "conditional_interval_exact": interval.get("bootstrap_draws") == 20000
        and interval.get("seed") == 2026071103
        and interval.get("random_generator") == "NumPy PCG64"
        and interval.get("familywise_level") == 0.95
        and "0.0125 and 0.9875" in " ".join(interval.get("algorithm", [])),
        "exclusion_stop_no_rerun_frozen": bool(prereg.get("exclusion_and_replacement"))
        and bool(prereg.get("stop_rules"))
        and bool(prereg.get("no_rerun_policy")),
        "evidence_contract_complete": [item.get("condition_code") for item in conditions]
        == ["C0", "C1", "C2", "C3"]
        and [item.get("addition_from_previous") for item in conditions]
        == [None, "executable_basic", "visible_f2p", "visible_p2p"],
        "three_exact_model_routes": [route.get("model_id") for route in model_routes]
        == ["qwen3.7-plus-2026-05-26", "deepseek-v4-flash", "gemini-3.5-flash"]
        and [route.get("route_order") for route in model_routes] == [1, 2, 3],
        "model_parameters_order_and_caps_frozen": all(
            route.get("provider") and route.get("endpoint") and route.get("parameters")
            for route in model_routes
        )
        and model_freeze.get("request_order", {}).get("repeat_indices") == [1, 2, 3]
        and model_freeze.get("attempt_budgets", {}).get("full_hard_maximum") == 2268
        and model_freeze.get("attempt_budgets", {}).get("smoke_hard_maximum") == 26,
        "three_stateless_repeats": model_freeze.get("common_request_contract", {}).get("stateless_repeats") == 3,
        "prompt_boundary_mechanical_pass": boundary["mechanical_pass"],
        "hash_manifest_complete": len(manifest["files"]) == 16,
        "freeze_status_consistent": prereg.get("status") == expected_freeze_status
        and contract.get("status") == expected_freeze_status
        and model_freeze.get("status") == expected_freeze_status
        and manifest.get("immutable") is author_signed,
        "author_identity_recorded": author_identity_recorded,
        "author_items_all_confirmed": author_items_all_confirmed,
        "author_declaration_recorded": author_declaration_recorded,
        "author_scientific_responsibility_signed": author_signed,
        "model_api_called": False,
        "p4_candidate_constructed_or_run": False,
        "p5_entered": False,
    }
    mechanical_names = [
        "p2_regular_unchanged",
        "p2_frozen_hashes_unchanged",
        "p3_change_scope_only",
        "preregistration_complete",
        "three_research_questions_frozen",
        "primary_estimands_exact",
        "scientific_unit_task_n30",
        "outcome_classes_frozen",
        "conditional_interval_exact",
        "exclusion_stop_no_rerun_frozen",
        "evidence_contract_complete",
        "three_exact_model_routes",
        "model_parameters_order_and_caps_frozen",
        "three_stateless_repeats",
        "prompt_boundary_mechanical_pass",
        "hash_manifest_complete",
        "freeze_status_consistent",
    ]
    prohibited_names = ["model_api_called", "p4_candidate_constructed_or_run", "p5_entered"]
    mechanical_pass = all(checks[name] for name in mechanical_names) and not any(
        checks[name] for name in prohibited_names
    )
    if mechanical_pass and author_signed:
        gate_status = "PASS"
    elif mechanical_pass:
        gate_status = "PENDING_AUTHOR_SIGNOFF"
    else:
        gate_status = "FAIL"
    return {
        "audit_id": "dsa_p3_gate_audit_v0_1",
        "audit_date": "2026-07-11",
        "gate_status": gate_status,
        "mechanical_gate_pass": mechanical_pass,
        "author_gate_pass": author_signed,
        "checks": checks,
        "p2_frozen_sha256": p2_actual_hashes,
        "changed_paths_since_p2": sorted(changed_paths),
        "unexpected_changed_paths": unexpected_changed_paths,
        "next_action": (
            "Record explicit author sign-off, regenerate hashes, and rerun this gate. Do not enter P4/P5 or call a model API."
            if gate_status == "PENDING_AUTHOR_SIGNOFF"
            else "P3 is complete; stop this phase without entering P4/P5 or calling a model API."
            if gate_status == "PASS"
            else "Diagnose and repair the failed P3 mechanical check before requesting sign-off."
        ),
    }


def render_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    boundary = build_boundary_audit()
    manifest = build_manifest()
    gate = build_gate(boundary, manifest)
    outputs = {
        BOUNDARY_OUT: render_json(boundary),
        MANIFEST_OUT: render_json(manifest),
        GATE_OUT: render_json(gate),
    }
    if args.write:
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8", newline="\n")
    else:
        mismatches = []
        for path, expected in outputs.items():
            actual = path.read_text(encoding="utf-8") if path.exists() else None
            if actual != expected:
                mismatches.append(path.relative_to(ROOT).as_posix())
        if mismatches:
            raise SystemExit("P3 generated artifact mismatch: " + ", ".join(mismatches))

    print(
        json.dumps(
            {
                "mode": "write" if args.write else "check",
                "mechanical_pass": boundary["mechanical_pass"],
                "gate_status": gate["gate_status"],
                "api_call_attempted": False,
                "p4_candidate_constructed_or_run": False,
            },
            sort_keys=True,
        )
    )
    return 0 if boundary["mechanical_pass"] and gate["gate_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
