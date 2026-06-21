"""Build the EVP-8 five-model synthesis scaffold without reading raw outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
FIRST_BATCH_SYNTHESIS_PATH = REPO_ROOT / "data" / "protocols" / "evp8_deepseek_qwen_first_batch_full_synthesis_v0_1.json"
LATER_AUDIT_PATH = REPO_ROOT / "data" / "protocols" / "evp8_later_model_full_result_audit_v0_1.json"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "protocols" / "evp8_five_model_synthesis_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_five_model_synthesis_v0_1.md"
EXPECTED_LEVELS = ("E0", "E1", "E2", "E3", "E4", "E5", "E6")
EXPECTED_FIRST_BATCH_MODELS = ("deepseek/deepseek-v4-pro", "qwen/qwen3.7-max")
EXPECTED_LATER_MODELS = ("moonshotai/kimi-k2.6", "mistralai/devstral-2512", "google/gemini-2.5-flash")


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


def _first_batch_counts(first_batch: dict[str, Any]) -> dict[str, dict[str, dict[str, int]]]:
    return first_batch.get("per_level_decision_counts_by_model") or {}


def _later_counts(later_audit: dict[str, Any]) -> dict[str, dict[str, dict[str, int]]]:
    result: dict[str, dict[str, dict[str, int]]] = {level: {} for level in EXPECTED_LEVELS}
    for item in later_audit.get("model_audits") or []:
        if item.get("status") != "passed":
            continue
        counts = item.get("decision_counts_by_evidence_level") or {}
        for level in EXPECTED_LEVELS:
            result[level][item["model_id"]] = counts.get(level, {})
    return result


def _merge_counts(
    first_batch_counts: dict[str, dict[str, dict[str, int]]],
    later_counts: dict[str, dict[str, dict[str, int]]],
) -> dict[str, dict[str, dict[str, int]]]:
    merged: dict[str, dict[str, dict[str, int]]] = {}
    for level in EXPECTED_LEVELS:
        merged[level] = {}
        merged[level].update(first_batch_counts.get(level) or {})
        merged[level].update(later_counts.get(level) or {})
    return merged


def build_synthesis(first_batch_path: Path, later_audit_path: Path) -> dict[str, Any]:
    first_batch = read_json(first_batch_path)
    if first_batch is None:
        raise FileNotFoundError(display_path(first_batch_path))
    later_audit = read_json(later_audit_path)
    if later_audit is None:
        raise FileNotFoundError(display_path(later_audit_path))

    first_batch_model_ids = [item.get("model_id") for item in first_batch.get("model_summaries") or []]
    later_model_ids = [item.get("model_id") for item in later_audit.get("model_audits") or []]
    later_status = str(later_audit.get("audit_status"))
    first_batch_ready = first_batch.get("synthesis_status") == "passed"
    if not first_batch_ready:
        status = "blocked_first_batch_not_passed"
    elif later_status == "passed":
        status = "passed"
    elif later_status == "waiting_for_execution":
        status = "waiting_for_later_models"
    elif later_status == "partial_waiting_for_remaining_later_models":
        status = "partial_waiting_for_remaining_later_models"
    else:
        status = "failed"

    counts = _merge_counts(_first_batch_counts(first_batch), _later_counts(later_audit))
    checks = [
        check("first_batch_synthesis_passed", first_batch_ready, first_batch.get("synthesis_status")),
        check("first_batch_no_api", first_batch.get("api_call_attempted") is False, first_batch.get("api_call_attempted")),
        check("first_batch_raw_outputs_not_read", first_batch.get("raw_outputs_read") is False, first_batch.get("raw_outputs_read")),
        check("first_batch_models", first_batch_model_ids == list(EXPECTED_FIRST_BATCH_MODELS), first_batch_model_ids),
        check(
            "later_audit_status_supported",
            later_status in {"waiting_for_execution", "partial_waiting_for_remaining_later_models", "passed"},
            later_status,
        ),
        check("later_audit_no_api", later_audit.get("api_call_attempted") is False, later_audit.get("api_call_attempted")),
        check("later_audit_raw_outputs_not_read", later_audit.get("raw_outputs_read") is False, later_audit.get("raw_outputs_read")),
        check("later_models", later_model_ids == list(EXPECTED_LATER_MODELS), later_model_ids),
        check(
            "passed_status_requires_all_later_models",
            status != "passed" or later_audit.get("passed_model_count") == len(EXPECTED_LATER_MODELS),
            later_audit.get("passed_model_count"),
        ),
        check(
            "per_level_counts_have_expected_levels",
            sorted(counts) == list(EXPECTED_LEVELS),
            sorted(counts),
        ),
    ]
    if not all(item["passed"] for item in checks):
        status = "failed"
    return {
        "synthesis_id": "evp8_five_model_synthesis_v0_1",
        "cohort_id": "EVP-8",
        "protocol_id": first_batch.get("protocol_id"),
        "candidate_set_id": first_batch.get("candidate_set_id"),
        "synthesis_status": status,
        "first_batch_synthesis_status": first_batch.get("synthesis_status"),
        "later_model_audit_status": later_audit.get("audit_status"),
        "api_call_attempted": False,
        "raw_outputs_read": False,
        "raw_outputs_generated_by_synthesis": False,
        "rendered_prompt_text_read": False,
        "expected_model_ids": list(EXPECTED_FIRST_BATCH_MODELS + EXPECTED_LATER_MODELS),
        "first_batch_model_ids": first_batch_model_ids,
        "later_model_ids": later_model_ids,
        "later_summary_present_count": later_audit.get("summary_present_count"),
        "later_passed_model_count": later_audit.get("passed_model_count"),
        "per_level_decision_counts_by_model": counts,
        "checks": checks,
        "allowed_claim": (
            "Only after status is passed, report descriptive five-model per-level decision patterns "
            "for the frozen EVP-8 v0.1 packet set."
        ),
        "forbidden_claim": (
            "Do not report five-model journal conclusions, LLM superiority over deterministic baselines, "
            "or final evidence-level effectiveness while this scaffold is waiting or partial."
        ),
    }


def write_markdown(path: Path, synthesis: dict[str, Any]) -> None:
    lines = [
        "# EVP-8 Five-Model Synthesis v0.1",
        "",
        f"- Status: `{synthesis['synthesis_status']}`",
        f"- First-batch synthesis status: `{synthesis['first_batch_synthesis_status']}`",
        f"- Later-model audit status: `{synthesis['later_model_audit_status']}`",
        f"- API call attempted by synthesis: `{str(synthesis['api_call_attempted']).lower()}`",
        f"- Raw outputs read: `{str(synthesis['raw_outputs_read']).lower()}`",
        f"- Later summaries present: `{synthesis['later_summary_present_count']}` / `{len(EXPECTED_LATER_MODELS)}`",
        "",
        "## Models",
        "",
    ]
    for model_id in synthesis["expected_model_ids"]:
        lines.append(f"- `{model_id}`")
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
    allowed = {"waiting_for_later_models", "partial_waiting_for_remaining_later_models", "passed"}
    if synthesis["synthesis_status"] not in allowed:
        raise SystemExit(f"EVP-8 five-model synthesis failed: {synthesis['synthesis_status']}")
    if synthesis["api_call_attempted"] is not False:
        raise SystemExit("five-model synthesis must not call APIs")
    if synthesis["raw_outputs_read"] is not False:
        raise SystemExit("five-model synthesis must not read raw outputs")
    if not all(item["passed"] for item in synthesis["checks"]):
        raise SystemExit(f"EVP-8 five-model synthesis checks failed: {synthesis['checks']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--first-batch-synthesis", type=Path, default=FIRST_BATCH_SYNTHESIS_PATH)
    parser.add_argument("--later-audit", type=Path, default=LATER_AUDIT_PATH)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    synthesis = build_synthesis(args.first_batch_synthesis, args.later_audit)
    write_json(args.json_out, synthesis)
    write_markdown(args.md_out, synthesis)
    if args.check:
        assert_synthesis(synthesis)
    print(json.dumps(synthesis, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
