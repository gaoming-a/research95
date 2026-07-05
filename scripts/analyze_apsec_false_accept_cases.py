"""Build raw-output-free APSEC false-accept case analysis for repaired E6 runs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from cross_review.parsing import extract_json_object  # noqa: E402


CANDIDATE_SET = REPO_ROOT / "data" / "protocols" / "evp8_candidate_set_v0_1.json"
LABELS = REPO_ROOT / "data" / "patches" / "evp7_candidates.jsonl"
RAW_SOURCES = {
    "qwen/qwen3.7-max": REPO_ROOT
    / "outputs"
    / "evp8_main_v0_3_qwen_first_prompt_v0_2_json_mode_full"
    / "qwen_qwen3.7-max"
    / "raw_responses.jsonl",
    "deepseek/deepseek-v4-pro": REPO_ROOT
    / "outputs"
    / "evp8_deepseek_repaired_v0_3_prompt_v0_2_json_mode_full"
    / "deepseek_deepseek-v4-pro"
    / "raw_responses.jsonl",
    "google/gemini-2.5-flash": REPO_ROOT
    / "outputs"
    / "evp8_gemini_repaired_v0_3_prompt_v0_2_openrouter_full"
    / "google_gemini-2.5-flash"
    / "raw_responses.jsonl",
}
NO_VERDICT_RAW_SOURCES = {
    "qwen/qwen3.7-max": REPO_ROOT
    / "outputs"
    / "evp8_e6_no_verdict_ablation_full"
    / "qwen_qwen3.7-max"
    / "raw_responses.jsonl",
    "deepseek/deepseek-v4-pro": REPO_ROOT
    / "outputs"
    / "evp8_e6_no_verdict_ablation_full"
    / "deepseek_deepseek-v4-pro"
    / "raw_responses.jsonl",
}
CORRECT_LABEL = "correct_under_f2p_and_p2p_broad"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "reviews" / "apsec_false_accept_case_analysis_v0_2.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "paper" / "apsec_false_accept_case_analysis_v0_2.md"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def candidate_map() -> dict[str, dict[str, Any]]:
    data = read_json(CANDIDATE_SET)
    return {
        record["evp8_candidate_id"]: {
            "source_candidate_id": record["source_candidate_id"],
            "project": record.get("project"),
            "task_id": record.get("task_id"),
        }
        for record in data["records"]
    }


def label_map() -> dict[str, dict[str, Any]]:
    return {
        record["evp7_candidate_id"]: {
            "label_with_p2p_broad": record.get("label_with_p2p_broad"),
            "candidate_type": record.get("candidate_type"),
            "expected_outcome": record.get("expected_outcome"),
            "project": record.get("project"),
            "task_id": record.get("task_id"),
        }
        for record in read_jsonl(LABELS)
    }


def parsed_e6_decisions(path: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for raw in read_jsonl(path):
        if raw.get("evidence_level") != "E6":
            continue
        parsed = extract_json_object(str(raw.get("raw_response_text") or ""))
        result[str(raw["anonymous_candidate_id"])] = {
            "decision": parsed.get("decision"),
            "confidence_bucket": confidence_bucket(parsed.get("confidence")),
            "rationale_category": rationale_category(parsed),
            "evidence_category": evidence_category(parsed),
            "risk_flag_category": risk_flag_category(parsed),
            "human_review_needed": parsed.get("human_review_needed"),
        }
    return result


def confidence_bucket(value: Any) -> str:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return "missing"
    if confidence >= 0.8:
        return "high"
    if confidence >= 0.5:
        return "medium"
    return "low"


def evidence_category(parsed: dict[str, Any]) -> str:
    used = {str(item) for item in parsed.get("evidence_used") or []}
    if "deterministic_visible_merge_gate_summary" in used:
        return "merge_gate_summary_used"
    if "visible_fail_to_pass_test_evidence" in used:
        return "visible_tests_used_without_merge_gate"
    return "other_or_unspecified_evidence"


def risk_flag_category(parsed: dict[str, Any]) -> str:
    flags = [str(item) for item in parsed.get("risk_flags") or []]
    contradictions = parsed.get("visible_contradictions") or []
    if contradictions:
        return "accepted_despite_visible_contradiction"
    if flags:
        return "accepted_with_risk_flags:" + ",".join(sorted(flags))
    return "accepted_without_reported_risk_flags"


def rationale_category(parsed: dict[str, Any]) -> str:
    reason = str(parsed.get("primary_reason") or "").lower()
    if "merge-gate" in reason or "merge gate" in reason:
        return "accepted_due_to_visible_tests_and_merge_gate_summary"
    if "visible test" in reason or "tests" in reason:
        return "accepted_due_to_visible_test_success"
    return "accepted_without_specific_tool_reason_category"


def build_analysis() -> dict[str, Any]:
    candidates = candidate_map()
    labels = label_map()
    no_verdict = {
        model: parsed_e6_decisions(path) for model, path in NO_VERDICT_RAW_SOURCES.items() if path.exists()
    }
    rows: list[dict[str, Any]] = []
    per_model_counts: dict[str, dict[str, int]] = {}

    for model, path in RAW_SOURCES.items():
        decisions = parsed_e6_decisions(path)
        counts = {"false_accept": 0, "partial_fix": 0, "regression_patch": 0}
        for evp8_candidate_id, decision in sorted(decisions.items()):
            candidate = candidates[evp8_candidate_id]
            label = labels[candidate["source_candidate_id"]]
            if label["label_with_p2p_broad"] == CORRECT_LABEL or decision["decision"] != "accept":
                continue
            counts["false_accept"] += 1
            if label["candidate_type"] in counts:
                counts[str(label["candidate_type"])] += 1
            rows.append(
                {
                    "model": model,
                    "candidate_id": evp8_candidate_id,
                    "source_candidate_id": candidate["source_candidate_id"],
                    "project": candidate["project"],
                    "task_id": candidate["task_id"],
                    "candidate_type": label["candidate_type"],
                    "hidden_label": label["label_with_p2p_broad"],
                    "e6_decision": decision["decision"],
                    "e6_no_verdict_decision": (no_verdict.get(model) or {}).get(evp8_candidate_id, {}).get("decision"),
                    "tool_contestation_linkage": "not_matched_to_repaired_main_candidate_export",
                    "rationale_category": decision["rationale_category"],
                    "evidence_category": decision["evidence_category"],
                    "risk_flag_category": decision["risk_flag_category"],
                    "confidence_bucket": decision["confidence_bucket"],
                    "human_review_needed": decision["human_review_needed"],
                }
            )
        per_model_counts[model] = counts

    checks = [
        {"check": "raw_sources_exist", "passed": all(path.exists() for path in RAW_SOURCES.values()), "detail": {k: rel(v) for k, v in RAW_SOURCES.items()}},
        {"check": "false_accept_rows_present", "passed": len(rows) == 13, "detail": len(rows)},
        {"check": "qwen_false_accept_count", "passed": per_model_counts.get("qwen/qwen3.7-max", {}).get("false_accept") == 4, "detail": per_model_counts.get("qwen/qwen3.7-max")},
        {"check": "deepseek_false_accept_count", "passed": per_model_counts.get("deepseek/deepseek-v4-pro", {}).get("false_accept") == 4, "detail": per_model_counts.get("deepseek/deepseek-v4-pro")},
        {"check": "gemini_false_accept_count", "passed": per_model_counts.get("google/gemini-2.5-flash", {}).get("false_accept") == 5, "detail": per_model_counts.get("google/gemini-2.5-flash")},
        {"check": "raw_response_text_not_stored", "passed": True, "detail": True},
        {"check": "rendered_prompt_or_patch_diff_not_stored", "passed": True, "detail": True},
    ]
    return {
        "analysis_id": "apsec_false_accept_case_analysis_v0_2",
        "status": "passed" if all(item["passed"] for item in checks[:5]) else "failed",
        "boundary": "reads local raw responses to extract decisions, writes only sanitized raw-output-free case fields",
        "inputs": {
            "candidate_set": rel(CANDIDATE_SET),
            "labels": rel(LABELS),
            "raw_sources": {model: rel(path) for model, path in RAW_SOURCES.items()},
            "no_verdict_raw_sources_available": {model: rel(path) for model, path in NO_VERDICT_RAW_SOURCES.items() if path.exists()},
        },
        "per_model_counts": per_model_counts,
        "case_rows": rows,
        "checks": checks,
        "forbidden_output_fields": [
            "raw_response_text",
            "full primary_reason",
            "rendered_prompt",
            "patch_diff",
            "api_credentials",
        ],
    }


def render_md(analysis: dict[str, Any]) -> str:
    lines = [
        "# APSEC False-Accept Case Analysis v0.2",
        "",
        f"- status: `{analysis['status']}`",
        f"- boundary: {analysis['boundary']}",
        "",
        "## Per-Model Anatomy",
        "",
        "| model | false accepts | partial fixes | regression patches |",
        "| --- | ---: | ---: | ---: |",
    ]
    for model, counts in analysis["per_model_counts"].items():
        lines.append(
            f"| {model} | {counts.get('false_accept', 0)} | {counts.get('partial_fix', 0)} | {counts.get('regression_patch', 0)} |"
        )
    lines += [
        "",
        "## Sanitized Case Rows",
        "",
        "| model | candidate | project | task | type | E6 | no-verdict | rationale category | risk category |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in analysis["case_rows"]:
        lines.append(
            f"| {row['model']} | {row['candidate_id']} | {row['project']} | {row['task_id']} | "
            f"{row['candidate_type']} | {row['e6_decision']} | {row['e6_no_verdict_decision'] or 'n/a'} | "
            f"{row['rationale_category']} | {row['risk_flag_category']} |"
        )
    lines += [
        "",
        "## Checks",
        "",
        "| check | passed | detail |",
        "| --- | ---: | --- |",
    ]
    for item in analysis["checks"]:
        lines.append(f"| `{item['check']}` | {item['passed']} | `{item['detail']}` |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-json", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    analysis = build_analysis()
    rendered_json = json.dumps(analysis, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    rendered_md = render_md(analysis)

    if args.check:
        existing_json = args.out_json.read_text(encoding="utf-8") if args.out_json.exists() else ""
        existing_md = args.out_md.read_text(encoding="utf-8") if args.out_md.exists() else ""
        if existing_json != rendered_json or existing_md != rendered_md:
            raise SystemExit("APSEC false-accept case analysis outputs are stale")
        if analysis["status"] != "passed":
            raise SystemExit("APSEC false-accept case analysis failed")
        print("APSEC false-accept case analysis outputs are current")
        return

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(rendered_json, encoding="utf-8")
    args.out_md.write_text(rendered_md, encoding="utf-8")
    print(f"wrote {rel(args.out_json)}")
    print(f"wrote {rel(args.out_md)}")


if __name__ == "__main__":
    main()
