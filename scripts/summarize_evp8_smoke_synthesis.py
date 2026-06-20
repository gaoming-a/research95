"""Summarize EVP-8 DeepSeek/Qwen smoke results without reading raw outputs.

This is the G4 smoke-synthesis scaffold. Before real smoke execution it reports
``waiting_for_execution``. After execution it consumes only tracked
raw-output-free summaries via the post-smoke audit path.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import audit_evp8_smoke_results as audit_module


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = REPO_ROOT / "data" / "protocols" / "evp8_deepseek_qwen_smoke_execution_packet_v0_1.json"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "protocols" / "evp8_deepseek_qwen_smoke_synthesis_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_deepseek_qwen_smoke_synthesis_v0_1.md"
EXPECTED_LEVELS = tuple(audit_module.EXPECTED_LEVELS)


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_synthesis(packet_path: Path) -> dict[str, Any]:
    audit = audit_module.build_audit(packet_path)
    model_summaries = [_model_summary(item) for item in audit["model_audits"]]
    model_by_id = {item["model_id"]: item for item in model_summaries}
    deepseek = model_by_id.get("deepseek/deepseek-v4-pro")
    qwen = model_by_id.get("qwen/qwen3.7-max")
    synthesis_status = _synthesis_status(audit["audit_status"], deepseek, qwen)
    comparison = _per_level_comparison(model_summaries)
    checks = [
        _check("audit_no_api", audit.get("api_call_attempted") is False, audit.get("api_call_attempted")),
        _check("audit_raw_outputs_not_read", audit.get("raw_outputs_read") is False, audit.get("raw_outputs_read")),
        _check(
            "audit_status_supported_for_synthesis",
            audit["audit_status"] in {"waiting_for_execution", "partial_waiting_for_remaining_model", "passed"},
            audit["audit_status"],
        ),
        _check(
            "qwen_not_present_before_deepseek_passed",
            not (qwen and qwen["summary_present"]) or bool(deepseek and deepseek["status"] == "passed"),
            {
                "deepseek_status": deepseek and deepseek["status"],
                "qwen_summary_present": qwen and qwen["summary_present"],
            },
        ),
        _check(
            "per_level_counts_available_for_present_passed_models",
            _present_passed_models_have_levels(model_summaries),
            {
                item["model_id"]: sorted(item["decision_counts_by_evidence_level"])
                for item in model_summaries
                if item["summary_present"] and item["status"] == "passed"
            },
        ),
    ]
    if audit["audit_status"] == "failed":
        checks.append(_check("audit_status_not_failed", False, audit["audit_status"]))
    return {
        "synthesis_id": "evp8_deepseek_qwen_smoke_synthesis_v0_1",
        "cohort_id": "EVP-8",
        "protocol_id": audit.get("protocol_id"),
        "candidate_set_id": audit.get("candidate_set_id"),
        "synthesis_status": synthesis_status,
        "audit_status": audit["audit_status"],
        "api_call_attempted": False,
        "raw_outputs_read": False,
        "raw_outputs_generated_by_synthesis": False,
        "rendered_prompt_text_read": False,
        "model_summaries": model_summaries,
        "per_level_decision_counts_by_model": comparison,
        "checks": checks,
        "allowed_claim": (
            "After both smoke models pass, report only descriptive DeepSeek/Qwen "
            "per-level decision patterns for the frozen EVP-8 v0.1 smoke subset."
        ),
        "forbidden_claim": (
            "Do not report five-model journal conclusions, full-cohort "
            "generalization, LLM superiority over deterministic baselines, or "
            "final evidence-level effectiveness from this smoke synthesis."
        ),
    }


def _model_summary(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "model_id": item["model_id"],
        "status": item["status"],
        "summary_present": item["summary_present"],
        "summary_path": item["summary_path"],
        "raw_response_path": item["raw_response_path"],
        "decision_counts_by_evidence_level": item.get("decision_counts_by_evidence_level") or {},
    }


def _synthesis_status(
    audit_status: str,
    deepseek: dict[str, Any] | None,
    qwen: dict[str, Any] | None,
) -> str:
    if audit_status == "waiting_for_execution":
        return "waiting_for_execution"
    if audit_status == "passed":
        return "passed"
    if audit_status == "partial_waiting_for_remaining_model":
        if deepseek and deepseek["status"] == "passed" and qwen and not qwen["summary_present"]:
            return "partial_waiting_for_qwen"
    return "failed"


def _per_level_comparison(model_summaries: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, int]]]:
    comparison: dict[str, dict[str, dict[str, int]]] = {level: {} for level in EXPECTED_LEVELS}
    for item in model_summaries:
        if not item["summary_present"] or item["status"] != "passed":
            continue
        by_level = item["decision_counts_by_evidence_level"]
        for level in EXPECTED_LEVELS:
            comparison[level][item["model_id"]] = by_level.get(level) or {}
    return comparison


def _present_passed_models_have_levels(model_summaries: list[dict[str, Any]]) -> bool:
    expected = list(EXPECTED_LEVELS)
    for item in model_summaries:
        if item["summary_present"] and item["status"] == "passed":
            if sorted(item["decision_counts_by_evidence_level"]) != expected:
                return False
    return True


def _check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def write_markdown(path: Path, synthesis: dict[str, Any]) -> None:
    lines = [
        "# EVP-8 DeepSeek/Qwen Smoke Synthesis v0.1",
        "",
        f"- Status: `{synthesis['synthesis_status']}`",
        f"- Audit status: `{synthesis['audit_status']}`",
        f"- API call attempted by synthesis: `{str(synthesis['api_call_attempted']).lower()}`",
        f"- Raw outputs read: `{str(synthesis['raw_outputs_read']).lower()}`",
        f"- Raw outputs generated by synthesis: `{str(synthesis['raw_outputs_generated_by_synthesis']).lower()}`",
        "",
        "## Model Summaries",
        "",
    ]
    for item in synthesis["model_summaries"]:
        lines.append(f"- `{item['model_id']}`: `{item['status']}`")
        lines.append(f"  - summary present: `{str(item['summary_present']).lower()}`")
    lines.extend(["", "## Per-Level Decision Counts", ""])
    for level, counts_by_model in synthesis["per_level_decision_counts_by_model"].items():
        lines.append(f"- `{level}`: `{json.dumps(counts_by_model, ensure_ascii=False, sort_keys=True)}`")
    lines.extend(["", "## Checks", ""])
    lines.extend(f"- {item['check']}: `{str(item['passed']).lower()}`" for item in synthesis["checks"])
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Allowed: {synthesis['allowed_claim']}",
            f"- Forbidden: {synthesis['forbidden_claim']}",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def assert_synthesis(synthesis: dict[str, Any]) -> None:
    if synthesis["synthesis_status"] not in {"waiting_for_execution", "partial_waiting_for_qwen", "passed"}:
        raise SystemExit(f"EVP-8 smoke synthesis failed: {synthesis['synthesis_status']}")
    if synthesis["api_call_attempted"] is not False:
        raise SystemExit("synthesis must not call APIs")
    if synthesis["raw_outputs_read"] is not False:
        raise SystemExit("synthesis must not read raw outputs")
    if not all(item["passed"] for item in synthesis["checks"]):
        raise SystemExit(f"EVP-8 smoke synthesis checks failed: {synthesis['checks']}")


def run_self_test() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="evp8_smoke_synthesis_selftest_") as temp_dir:
        root = Path(temp_dir)
        deepseek_raw = "outputs/evp8_phase1_deepseek_qwen_smoke/deepseek_deepseek-v4-pro/raw_responses.jsonl"
        qwen_raw = "outputs/evp8_phase1_deepseek_qwen_smoke/qwen_qwen3.7-max/raw_responses.jsonl"
        deepseek_summary = audit_module.executed_summary("deepseek/deepseek-v4-pro", deepseek_raw)
        qwen_summary = audit_module.executed_summary("qwen/qwen3.7-max", qwen_raw)
        cases = [
            _run_case(
                root / "waiting_for_execution",
                deepseek_summary=None,
                qwen_summary=None,
                expected_status="waiting_for_execution",
                assert_check_passes=True,
            ),
            _run_case(
                root / "deepseek_only_passed",
                deepseek_summary=deepseek_summary,
                qwen_summary=None,
                expected_status="partial_waiting_for_qwen",
                assert_check_passes=True,
            ),
            _run_case(
                root / "both_models_passed",
                deepseek_summary=deepseek_summary,
                qwen_summary=qwen_summary,
                expected_status="passed",
                assert_check_passes=True,
            ),
            _run_case(
                root / "qwen_without_deepseek",
                deepseek_summary=None,
                qwen_summary=qwen_summary,
                expected_status="failed",
                assert_check_passes=False,
            ),
        ]
    return {
        "self_test_status": "passed",
        "case_count": len(cases),
        "cases": cases,
        "api_call_attempted": False,
        "raw_outputs_read": False,
        "raw_outputs_generated": False,
        "tracked_outputs_written": False,
    }


def _run_case(
    case_dir: Path,
    *,
    deepseek_summary: dict[str, Any] | None,
    qwen_summary: dict[str, Any] | None,
    expected_status: str,
    assert_check_passes: bool,
) -> dict[str, Any]:
    packet_path = case_dir / "packet.json"
    deepseek_path = case_dir / "deepseek_summary.json"
    qwen_path = case_dir / "qwen_summary.json"
    audit_module.self_test_packet(packet_path, deepseek_path, qwen_path)
    if deepseek_summary is not None:
        audit_module.write_json(deepseek_path, deepseek_summary)
    if qwen_summary is not None:
        audit_module.write_json(qwen_path, qwen_summary)
    synthesis = build_synthesis(packet_path)
    if synthesis["synthesis_status"] != expected_status:
        raise SystemExit(
            f"self-test expected {expected_status} but got {synthesis['synthesis_status']} for {case_dir.name}"
        )
    try:
        assert_synthesis(synthesis)
        assert_raised = False
    except SystemExit:
        assert_raised = True
    if assert_check_passes and assert_raised:
        raise SystemExit(f"self-test expected assert_synthesis to pass for {case_dir.name}")
    if not assert_check_passes and not assert_raised:
        raise SystemExit(f"self-test expected assert_synthesis to fail for {case_dir.name}")
    return {
        "case": case_dir.name,
        "synthesis_status": synthesis["synthesis_status"],
        "assert_check_passes": assert_check_passes,
        "api_call_attempted": synthesis["api_call_attempted"],
        "raw_outputs_read": synthesis["raw_outputs_read"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=PACKET_PATH)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        result = run_self_test()
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0

    synthesis = build_synthesis(args.packet)
    write_json(args.json_out, synthesis)
    write_markdown(args.md_out, synthesis)
    if args.check:
        assert_synthesis(synthesis)
    print(json.dumps(synthesis, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
