"""Build and audit the frozen EVP-8 prompt template without API calls."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_IN = REPO_ROOT / "data" / "protocols" / "evp8_protocol_v0_1.json"
TEMPLATE_IN = REPO_ROOT / "prompts" / "evp8_visible_evidence_merge_gate_v0_1.md"
MANIFEST_OUT = REPO_ROOT / "data" / "protocols" / "evp8_prompt_manifest_v0_1.json"
BOUNDARY_AUDIT_OUT = REPO_ROOT / "data" / "protocols" / "evp8_prompt_boundary_audit_v0_1.json"

DEFAULT_PROMPT_ID = "evp8_visible_evidence_merge_gate_v0_1"
PLACEHOLDER = "{visible_evidence_packet_json}"
FORBIDDEN_MARKERS = (
    "expected_outcome",
    "candidate_type",
    "failure_type_label",
    "label_with_p2p_broad",
    "label_retained_oracle",
    "hidden_oracles",
    "hidden_oracle_paths",
    "hidden_oracle_result",
    "hidden_oracle_results",
    "patch_materialization",
    "patch_source_label",
    "source_model_candidate_id",
    "validation_summary",
    "reference_patch_provenance",
    "reference_patch_label",
    "evaluator_merge_label",
    "correct_under_f2p_and_p2p_broad",
    "incorrect_issue_not_fixed",
    "incorrect_regression",
    "correct_reference",
    "irrelevant_patch",
    "buggy_noop",
    "partial_fix",
    "regression_patch",
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _boundary_findings(text: str) -> list[str]:
    lowered = text.lower()
    return [marker for marker in FORBIDDEN_MARKERS if marker.lower() in lowered]


def _sample_visible_packet(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "cohort_id": spec.get("cohort_id"),
        "protocol_id": spec.get("protocol_id"),
        "evidence_level": "E6",
        "evidence_level_name": "deterministic_visible_tool_summary",
        "anonymous_candidate_id": "evp8_smoke_candidate_0001",
        "task_id": "sample_task",
        "project": "sample_project",
        "model_visible_field_groups": [
            "issue_patch_seed",
            "patch_surface_map",
            "patch_application_static_status",
            "visible_fail_to_pass_test_evidence",
            "visible_pass_to_pass_regression_evidence",
            "broader_visible_tool_diagnostics",
            "deterministic_visible_merge_gate_summary",
        ],
        "visible_fields": {
            "issue_summary": "A concise task behavior summary.",
            "candidate_patch_diff": "diff --git a/example.py b/example.py",
            "touched_filenames": ["example.py"],
            "patch_surface_map": {
                "changed_files": ["example.py"],
                "changed_functions": ["example_function"],
                "changed_classes": [],
                "hunk_locations": ["example.py:10"],
                "neighboring_symbols": ["helper_function"],
                "related_imports": ["example"],
                "related_module_paths": ["example.py"],
            },
            "patch_application_static_status": {
                "patch_apply_status": "applied",
                "syntax_check_status": "passed",
                "import_smoke_status": "not_run",
                "configured_static_check_status": "not_run",
            },
            "visible_fail_to_pass_test_evidence": {
                "visible_fail_to_pass_scope_id": "sample_visible_f2p_scope",
                "visible_fail_to_pass_test_names": ["test_example_behavior"],
                "visible_fail_to_pass_outcomes": ["passed"],
            },
            "visible_pass_to_pass_regression_evidence": {
                "visible_pass_to_pass_scope_id": "sample_visible_p2p_scope",
                "visible_pass_to_pass_test_names": ["test_existing_behavior"],
                "visible_pass_to_pass_outcomes": ["passed"],
            },
            "broader_visible_tool_diagnostics": {
                "lint_or_static_diagnostic_summary": "not_run",
                "sanitized_test_log_observations": [],
                "environment_diagnostic_summary": "not_recorded",
                "diagnostic_tool_versions": {},
            },
            "deterministic_visible_merge_gate_summary": {
                "visible_tool_summary_counts": {"passed": 2, "failed": 0},
                "visible_tool_summary_contradictions": [],
                "rule_based_visible_merge_gate_decision": "accept",
                "rule_based_visible_merge_gate_reasons": ["visible checks passed"],
            },
        },
    }


def render_prompt(template: str, visible_packet: dict[str, Any]) -> str:
    payload = json.dumps(visible_packet, ensure_ascii=False, indent=2, sort_keys=True)
    return template.replace(PLACEHOLDER, payload)


def build_prompt_artifacts(
    spec_path: Path,
    template_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    spec_path = spec_path if spec_path.is_absolute() else REPO_ROOT / spec_path
    template_path = template_path if template_path.is_absolute() else REPO_ROOT / template_path
    spec = _load_json(spec_path)
    template = template_path.read_text(encoding="utf-8")
    sample_prompt = render_prompt(template, _sample_visible_packet(spec))
    output_schema = spec.get("output_schema") or {}
    prompt_id = (spec.get("prompt_policy") or {}).get("prompt_id") or DEFAULT_PROMPT_ID
    required_keys = output_schema.get("required_keys") or []
    decision_values = output_schema.get("decision_values") or []
    risk_values = output_schema.get("risk_flag_values") or []

    template_findings = _boundary_findings(template)
    sample_findings = _boundary_findings(sample_prompt)
    missing_required_keys = [key for key in required_keys if f'"{key}"' not in template]
    missing_decision_values = [value for value in decision_values if value not in template]
    missing_risk_values = [value for value in risk_values if value not in template]
    placeholder_present = PLACEHOLDER in template
    prompt_id_matches_spec = (spec.get("prompt_policy") or {}).get("prompt_id") == prompt_id

    manifest = {
        "prompt_id": prompt_id,
        "cohort_id": spec.get("cohort_id"),
        "protocol_id": spec.get("protocol_id"),
        "prompt_template_path": str(template_path.relative_to(REPO_ROOT)),
        "prompt_template_sha256": _sha256(template),
        "prompt_template_chars": len(template),
        "estimated_template_tokens_char_div_4": round(len(template) / 4),
        "prompt_template_text_tracked": True,
        "rendered_prompt_text_stored": False,
        "visible_packet_placeholder": PLACEHOLDER,
        "output_schema_required_keys": required_keys,
        "decision_values": decision_values,
        "risk_flag_values": risk_values,
        "api_call_attempted": False,
        "evidence_packets_generated": False,
        "prompt_manifest_status": "passed" if not _blocking_errors(
            template_findings,
            sample_findings,
            missing_required_keys,
            missing_decision_values,
            missing_risk_values,
            placeholder_present,
            prompt_id_matches_spec,
        ) else "failed",
        "claim_boundary": "This manifest freezes the EVP-8 prompt template only; it is not model-result evidence.",
    }
    boundary_audit = {
        "prompt_id": prompt_id,
        "protocol_id": spec.get("protocol_id"),
        "api_call_attempted": False,
        "evidence_packets_generated": False,
        "placeholder_present": placeholder_present,
        "prompt_id_matches_spec": prompt_id_matches_spec,
        "template_boundary_findings": template_findings,
        "sample_render_boundary_findings": sample_findings,
        "missing_required_schema_keys_in_template": missing_required_keys,
        "missing_decision_values_in_template": missing_decision_values,
        "missing_risk_flag_values_in_template": missing_risk_values,
        "sample_render_sha256": _sha256(sample_prompt),
        "sample_render_chars": len(sample_prompt),
        "rendered_prompt_text_stored": False,
        "prompt_boundary_audit_status": manifest["prompt_manifest_status"],
    }
    return manifest, boundary_audit


def _blocking_errors(
    template_findings: list[str],
    sample_findings: list[str],
    missing_required_keys: list[str],
    missing_decision_values: list[str],
    missing_risk_values: list[str],
    placeholder_present: bool,
    prompt_id_matches_spec: bool,
) -> list[str]:
    errors: list[str] = []
    if template_findings:
        errors.append("template_boundary_findings")
    if sample_findings:
        errors.append("sample_render_boundary_findings")
    if missing_required_keys:
        errors.append("missing_required_schema_keys_in_template")
    if missing_decision_values:
        errors.append("missing_decision_values_in_template")
    if missing_risk_values:
        errors.append("missing_risk_flag_values_in_template")
    if not placeholder_present:
        errors.append("visible_packet_placeholder_missing")
    if not prompt_id_matches_spec:
        errors.append("prompt_id_mismatch")
    return errors


def _check(manifest: dict[str, Any], boundary_audit: dict[str, Any]) -> None:
    if manifest["prompt_manifest_status"] != "passed":
        raise SystemExit(f"EVP-8 prompt manifest failed: {boundary_audit}")
    if boundary_audit["prompt_boundary_audit_status"] != "passed":
        raise SystemExit(f"EVP-8 prompt boundary audit failed: {boundary_audit}")
    if manifest["api_call_attempted"] is not False:
        raise SystemExit("prompt manifest must be no-API")
    if manifest["evidence_packets_generated"] is not False:
        raise SystemExit("prompt manifest must not generate evidence packets")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-in", type=Path, default=SPEC_IN)
    parser.add_argument("--template-in", type=Path, default=TEMPLATE_IN)
    parser.add_argument("--manifest-out", type=Path, default=MANIFEST_OUT)
    parser.add_argument("--boundary-audit-out", type=Path, default=BOUNDARY_AUDIT_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    manifest, boundary_audit = build_prompt_artifacts(args.spec_in, args.template_in)
    _write_json(args.manifest_out, manifest)
    _write_json(args.boundary_audit_out, boundary_audit)
    if args.check:
        _check(manifest, boundary_audit)
    print(json.dumps({"manifest": manifest, "boundary_audit": boundary_audit}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
