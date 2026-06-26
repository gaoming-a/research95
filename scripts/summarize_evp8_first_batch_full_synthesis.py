"""Summarize EVP-8 first-batch full-run audit results without raw outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = REPO_ROOT / "data" / "protocols" / "evp8_deepseek_qwen_first_batch_full_result_audit_v0_1.json"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "protocols" / "evp8_deepseek_qwen_first_batch_full_synthesis_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_deepseek_qwen_first_batch_full_synthesis_v0_1.md"
EXPECTED_LEVELS = ("E0", "E1", "E2", "E3", "E4", "E5", "E6")


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{display_path(path)} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def display_path(path: Path) -> str:
    absolute = path if path.is_absolute() else REPO_ROOT / path
    try:
        return absolute.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(absolute)


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def build_synthesis(audit_path: Path) -> dict[str, Any]:
    audit = read_json(audit_path)
    if audit is None:
        raise FileNotFoundError(display_path(audit_path))
    model_summaries = audit.get("model_audits") or []
    passed_models = [item for item in model_summaries if item.get("status") == "passed"]
    qwen = next((item for item in model_summaries if item.get("model_id") == "qwen/qwen3.7-max"), None)
    deepseek = next((item for item in model_summaries if item.get("model_id") == "deepseek/deepseek-v4-pro"), None)
    qwen_first_allowed = audit.get("execution_order_policy") == "qwen_first_no_deepseek_dependency"
    if audit.get("audit_status") == "passed":
        status = "passed"
    elif audit.get("audit_status") == "partial_waiting_for_remaining_model":
        status = "partial_waiting_for_qwen"
    elif audit.get("audit_status") == "waiting_for_execution":
        status = "waiting_for_execution"
    else:
        status = "failed"
    per_level = {
        level: {
            item["model_id"]: item.get("decision_counts_by_evidence_level", {}).get(level, {})
            for item in passed_models
        }
        for level in EXPECTED_LEVELS
    }
    checks = [
        check("audit_no_api", audit.get("api_call_attempted") is False, audit.get("api_call_attempted")),
        check("audit_raw_outputs_not_read", audit.get("raw_outputs_read") is False, audit.get("raw_outputs_read")),
        check(
            "audit_status_supported_for_synthesis",
            audit.get("audit_status") in {"waiting_for_execution", "partial_waiting_for_remaining_model", "passed"},
            audit.get("audit_status"),
        ),
        check(
            "qwen_not_present_before_deepseek_passed",
            qwen_first_allowed or not (qwen and qwen.get("summary_present")) or bool(deepseek and deepseek.get("status") == "passed"),
            {
                "deepseek_status": deepseek and deepseek.get("status"),
                "qwen_summary_present": qwen and qwen.get("summary_present"),
                "execution_order_policy": audit.get("execution_order_policy"),
            },
        ),
        check(
            "per_level_counts_available_for_present_passed_models",
            all(set((item.get("decision_counts_by_evidence_level") or {}).keys()) >= set(EXPECTED_LEVELS) for item in passed_models),
            {item.get("model_id"): sorted((item.get("decision_counts_by_evidence_level") or {}).keys()) for item in passed_models},
        ),
    ]
    if not all(item["passed"] for item in checks):
        status = "failed"
    audit_id = str(audit.get("audit_id") or "evp8_deepseek_qwen_first_batch_full_result_audit_v0_1")
    synthesis_id = audit_id.replace("result_audit", "synthesis")
    if qwen_first_allowed:
        allowed_claim = (
            "After the Qwen-first summary passes, report only descriptive Qwen "
            "per-level decision patterns for the frozen EVP-8 98-candidate packet set "
            "and the audited evidence-source mode."
        )
        forbidden_claim = (
            "Do not report five-model journal conclusions, DeepSeek/Qwen comparative claims, "
            "LLM superiority over deterministic baselines, or final evidence-level effectiveness "
            "from this Qwen-first synthesis."
        )
    else:
        allowed_claim = (
            "After both first-batch models pass, report only descriptive DeepSeek/Qwen "
            "per-level decision patterns for the frozen EVP-8 98-candidate packet set and "
            "the audited evidence-source mode."
        )
        forbidden_claim = (
            "Do not report five-model journal conclusions, LLM superiority over deterministic "
            "baselines, or final evidence-level effectiveness from this first-batch synthesis."
        )
    return {
        "synthesis_id": synthesis_id,
        "cohort_id": "EVP-8",
        "protocol_id": audit.get("protocol_id"),
        "candidate_set_id": audit.get("candidate_set_id"),
        "source_audit_id": audit.get("audit_id"),
        "packet_id": audit.get("packet_id"),
        "evidence_source_mode": audit.get("evidence_source_mode"),
        "execution_order_policy": audit.get("execution_order_policy"),
        "synthesis_status": status,
        "audit_status": audit.get("audit_status"),
        "api_call_attempted": False,
        "raw_outputs_read": False,
        "raw_outputs_generated_by_synthesis": False,
        "rendered_prompt_text_read": False,
        "model_summaries": model_summaries,
        "per_level_decision_counts_by_model": per_level,
        "checks": checks,
        "allowed_claim": allowed_claim,
        "forbidden_claim": forbidden_claim,
    }


def write_markdown(path: Path, synthesis: dict[str, Any]) -> None:
    lines = [
        f"# {synthesis.get('synthesis_id', 'EVP-8 DeepSeek/Qwen First-Batch Full-Run Synthesis')}",
        "",
        f"- Status: `{synthesis['synthesis_status']}`",
        f"- Audit status: `{synthesis['audit_status']}`",
        f"- Packet: `{synthesis.get('packet_id')}`",
        f"- Evidence source mode: `{synthesis.get('evidence_source_mode')}`",
        f"- Execution order policy: `{synthesis.get('execution_order_policy')}`",
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
    for level, counts in synthesis["per_level_decision_counts_by_model"].items():
        lines.append(f"- `{level}`: `{json.dumps(counts, ensure_ascii=False, sort_keys=True)}`")
    lines.extend(["", "## Checks", ""])
    lines.extend(f"- {item['check']}: `{str(item['passed']).lower()}`" for item in synthesis["checks"])
    lines.extend(["", "## Claim Boundary", ""])
    lines.append(f"- Allowed: {synthesis['allowed_claim']}")
    lines.append(f"- Forbidden: {synthesis['forbidden_claim']}")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def assert_synthesis(synthesis: dict[str, Any]) -> None:
    if synthesis["synthesis_status"] not in {"waiting_for_execution", "partial_waiting_for_qwen", "passed"}:
        raise SystemExit(f"EVP-8 first-batch full synthesis failed: {synthesis['synthesis_status']}")
    if synthesis["api_call_attempted"] is not False:
        raise SystemExit("synthesis must not call APIs")
    if synthesis["raw_outputs_read"] is not False:
        raise SystemExit("synthesis must not read raw outputs")
    if not all(item["passed"] for item in synthesis["checks"]):
        raise SystemExit(f"EVP-8 first-batch full synthesis checks failed: {synthesis['checks']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, default=AUDIT_PATH)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    synthesis = build_synthesis(args.audit)
    write_json(args.json_out, synthesis)
    write_markdown(args.md_out, synthesis)
    if args.check:
        assert_synthesis(synthesis)
    print(json.dumps(synthesis, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
