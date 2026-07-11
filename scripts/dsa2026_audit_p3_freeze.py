#!/usr/bin/env python3
"""Build and verify the no-API DSA P3 mechanical freeze artifacts."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "prompts/dsa2026_evidence_conditioned_patch_gate_v0_1.md"
SCHEMA = ROOT / "data/protocols/dsa_p3_output_schema_v0_1.json"
CONTRACT = ROOT / "data/protocols/dsa_p3_evidence_contract_v0_1.json"
MODEL_FREEZE = ROOT / "data/protocols/dsa_p3_model_freeze_v0_1.json"
PREREG = ROOT / "data/protocols/dsa_p3_preregistration_v0_1.json"
DENYLIST = ROOT / "data/protocols/dsa_legacy_analysis_denylist_v0_1.json"
BOUNDARY_OUT = ROOT / "data/protocols/dsa_p3_prompt_boundary_audit_v0_1.json"
MANIFEST_OUT = ROOT / "data/protocols/dsa_p3_hash_manifest_v0_1.json"
GATE_OUT = ROOT / "data/protocols/dsa_p3_gate_audit_v0_1.json"
PLACEHOLDER = "{{EVIDENCE_PACKET_JSON}}"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


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
    hidden_value_markers = {
        "oracle_positive",
        "hard_negative",
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
            for marker in hidden_value_markers:
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
    prompt_hash = sha256_file(PROMPT)
    hash_distinct = all(prompt_hash != item["sha256_before_deletion"] for item in retired)

    checks = {
        "placeholder_exactly_once": prompt_text.count(PLACEHOLDER) == 1,
        "schema_exact_fields": set(schema.get("properties", {})) == required_output_fields
        and set(schema.get("required", [])) == required_output_fields
        and schema.get("additionalProperties") is False,
        "schema_decision_enum_exact": schema.get("properties", {}).get("decision", {}).get("enum")
        == ["accept", "reject", "escalate"],
        "prompt_conflict_patterns_absent": not any(prompt_conflicts.values()),
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
        "synthetic_packets": cumulative_checks,
        "synthetic_rendered_prompts": rendered_checks,
        "prompt_sha256": prompt_hash,
        "active_templates": active_templates,
        "mechanical_pass": mechanical_pass,
    }


def build_manifest() -> dict[str, Any]:
    prereg = load_json(PREREG)
    author_signed = (
        prereg.get("author_signoff", {}).get("status") == "signed"
        and prereg.get("author_signoff", {}).get("scientific_responsibility_confirmed") is True
    )
    frozen_paths = [
        "data/protocols/dsa_p2_protocol_decision_v0_1.json",
        "data/protocols/dsa_p2_source_selection_v0_1.json",
        "data/protocols/dsa_p2_transform_registry_v0_1.json",
        "data/protocols/dsa_p2_development_exclusion_registry_v0_1.json",
        "data/protocols/dsa_p3_preregistration_v0_1.json",
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
        files.append({"path": relative, "sha256": sha256_file(path), "bytes": path.stat().st_size})
    aggregate_source = "".join(f"{item['path']}\0{item['sha256']}\n" for item in files)
    return {
        "manifest_id": "dsa_p3_hash_manifest_v0_1",
        "status": "immutable_author_signed" if author_signed else "candidate_freeze_pending_author_signoff",
        "hash_algorithm": "SHA-256",
        "aggregate_algorithm": "SHA-256 over ordered UTF-8 path, NUL, lowercase file hash, LF records",
        "files": files,
        "aggregate_sha256": sha256_bytes(aggregate_source.encode("utf-8")),
        "immutable": author_signed,
        "immutability_condition": "Explicit author sign-off followed by regeneration and a passing P3 gate before P4 or any model output.",
    }


def build_gate(boundary: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    prereg = load_json(PREREG)
    contract = load_json(CONTRACT)
    model_freeze = load_json(MODEL_FREEZE)
    author_signed = (
        prereg.get("author_signoff", {}).get("status") == "signed"
        and prereg.get("author_signoff", {}).get("scientific_responsibility_confirmed") is True
    )
    expected_freeze_status = "frozen_after_author_signoff" if author_signed else "candidate_freeze_pending_author_signoff"
    checks = {
        "p2_regular_unchanged": load_json(ROOT / "data/protocols/dsa_p2_protocol_decision_v0_1.json").get("selected_protocol") == "Regular",
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
        "evidence_contract_complete": len(contract.get("conditions", [])) == 4,
        "three_exact_model_routes": len(model_freeze.get("model_routes", [])) == 3
        and all(route.get("model_id") for route in model_freeze.get("model_routes", [])),
        "three_stateless_repeats": model_freeze.get("common_request_contract", {}).get("stateless_repeats") == 3,
        "prompt_boundary_mechanical_pass": boundary["mechanical_pass"],
        "hash_manifest_complete": len(manifest["files"]) == 15,
        "freeze_status_consistent": prereg.get("status") == expected_freeze_status
        and contract.get("status") == expected_freeze_status
        and model_freeze.get("status") == expected_freeze_status
        and manifest.get("immutable") is author_signed,
        "author_scientific_responsibility_signed": author_signed,
        "model_api_called": False,
        "p4_candidate_constructed_or_run": False,
        "p5_entered": False,
    }
    mechanical_names = [
        "p2_regular_unchanged",
        "preregistration_complete",
        "evidence_contract_complete",
        "three_exact_model_routes",
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
