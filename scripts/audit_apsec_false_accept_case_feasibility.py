# ruff: noqa: E402
from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/audit_apsec_false_accept_case_feasibility.py")

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
QWEN_LABEL_SUMMARY = (
    REPO_ROOT
    / "data"
    / "reviews"
    / "evp8_qwen_first_main_v0_3_prompt_v0_2_label_conditioned_summary.json"
)
CANDIDATE_SET_SUMMARY = (
    REPO_ROOT / "data" / "protocols" / "evp8_candidate_set_v0_1_summary.json"
)
CANDIDATE_SET = REPO_ROOT / "data" / "protocols" / "evp8_candidate_set_v0_1.json"
APSEC_AUDIT = REPO_ROOT / "data" / "reviews" / "apsec_manuscript_rewrite_audit_v0_1.json"
DEFAULT_JSON_OUT = (
    REPO_ROOT / "data" / "reviews" / "apsec_false_accept_case_feasibility_v0_1.json"
)
DEFAULT_MD_OUT = (
    REPO_ROOT / "docs" / "paper" / "apsec_false_accept_case_feasibility_v0_1.md"
)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def check(name: str, passed: bool, detail: Any = "") -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def has_candidate_level_false_accept_records(summary: dict[str, Any]) -> bool:
    candidate_records = summary.get("candidate_level_false_accepts")
    if isinstance(candidate_records, list) and candidate_records:
        required = {
            "candidate_id",
            "project",
            "task_id",
            "candidate_type",
            "label_with_p2p_broad",
            "e6_decision",
        }
        return all(isinstance(item, dict) and required <= set(item) for item in candidate_records)
    return False


def build_audit() -> dict[str, Any]:
    qwen = read_json(QWEN_LABEL_SUMMARY)
    candidate_summary = read_json(CANDIDATE_SET_SUMMARY)
    candidate_set = read_json(CANDIDATE_SET)
    apsec = read_json(APSEC_AUDIT)

    e6_breakdown = qwen["breakdowns_by_evidence_level"]["E6"]["candidate_type"]
    partial_accepts = e6_breakdown["partial_fix"]["decision_counts"].get("accept", 0)
    regression_accepts = e6_breakdown["regression_patch"]["decision_counts"].get("accept", 0)
    false_accept_total = qwen["per_evidence_level"]["E6"]["confusion_counts"]["false_accept"]

    records = candidate_set.get("records")
    candidate_metadata_fields = set()
    if isinstance(records, list) and records:
        candidate_metadata_fields = set(records[0])

    required_case_fields = [
        "candidate_id",
        "project",
        "task_id",
        "candidate_type",
        "hidden_label",
        "E6 decision",
        "E6 no-verdict decision",
        "tool-contestation linkage",
        "rationale category without raw response text",
    ]

    checks = [
        check("qwen_label_summary_exists", QWEN_LABEL_SUMMARY.exists(), str(QWEN_LABEL_SUMMARY.relative_to(REPO_ROOT))),
        check("candidate_set_summary_exists", CANDIDATE_SET_SUMMARY.exists(), str(CANDIDATE_SET_SUMMARY.relative_to(REPO_ROOT))),
        check("candidate_set_metadata_exists", CANDIDATE_SET.exists(), str(CANDIDATE_SET.relative_to(REPO_ROOT))),
        check("apsec_audit_passed", apsec.get("status") == "passed", apsec.get("status")),
        check("e6_false_accept_total_is_four", false_accept_total == 4, false_accept_total),
        check("aggregate_partial_false_accepts_available", partial_accepts == 3, partial_accepts),
        check("aggregate_regression_false_accepts_available", regression_accepts == 1, regression_accepts),
        check(
            "candidate_set_has_metadata_but_not_labels_or_decisions",
            {"evp8_candidate_id", "source_candidate_id", "project", "task_id"} <= candidate_metadata_fields
            and "candidate_type" not in candidate_metadata_fields
            and "decision" not in candidate_metadata_fields,
            sorted(candidate_metadata_fields),
        ),
        check(
            "qwen_summary_has_candidate_level_false_accept_records",
            has_candidate_level_false_accept_records(qwen),
            "No candidate-level false-accept records are present in the tracked aggregate summary.",
        ),
        check("api_call_attempted_by_this_audit", True, False),
        check("raw_response_read_by_this_audit", True, False),
        check("patch_diff_read_by_this_audit", True, False),
        check("rendered_prompt_read_by_this_audit", True, False),
    ]

    case_level_ready = all(
        item["passed"]
        for item in checks
        if item["check"]
        in {
            "qwen_label_summary_exists",
            "candidate_set_summary_exists",
            "candidate_set_metadata_exists",
            "apsec_audit_passed",
            "e6_false_accept_total_is_four",
            "aggregate_partial_false_accepts_available",
            "aggregate_regression_false_accepts_available",
            "qwen_summary_has_candidate_level_false_accept_records",
        }
    )

    return {
        "audit_id": "apsec_false_accept_case_feasibility_v0_1",
        "status": "case_level_analysis_ready" if case_level_ready else "blocked_missing_candidate_level_decision_export",
        "boundary": "no API call, no raw response read, no patch diff read, no rendered prompt read.",
        "inputs": {
            "qwen_label_summary": str(QWEN_LABEL_SUMMARY.relative_to(REPO_ROOT)),
            "candidate_set_summary": str(CANDIDATE_SET_SUMMARY.relative_to(REPO_ROOT)),
            "candidate_set_metadata": str(CANDIDATE_SET.relative_to(REPO_ROOT)),
            "apsec_audit": str(APSEC_AUDIT.relative_to(REPO_ROOT)),
        },
        "aggregate_supported_anatomy": {
            "e6_false_accept_total": false_accept_total,
            "partial_fix_false_accepts": partial_accepts,
            "regression_patch_false_accepts": regression_accepts,
        },
        "checks": checks,
        "case_level_table_allowed_now": case_level_ready,
        "blocked_reason": ""
        if case_level_ready
        else "Tracked paper-facing summaries expose aggregate false-accept counts but not the candidate IDs behind the four Qwen E6 false accepts.",
        "minimum_next_artifact": {
            "name": "raw_output_free_qwen_e6_false_accept_decision_export",
            "required_fields": required_case_fields,
            "forbidden_fields": [
                "raw_response_text",
                "full model rationale text",
                "rendered prompt text",
                "patch diff",
                "API credentials",
            ],
            "construction_note": "Generate from existing local execution artifacts only if explicitly authorized to read the needed raw decision source; store only sanitized decision/category fields.",
        },
    }


def render_md(audit: dict[str, Any]) -> str:
    lines = [
        "# APSEC False-Accept Case-Analysis Feasibility v0.1",
        "",
        f"- audit id: `{audit['audit_id']}`",
        f"- status: `{audit['status']}`",
        f"- boundary: {audit['boundary']}",
        f"- case-level table allowed now: `{audit['case_level_table_allowed_now']}`",
        "",
        "## Aggregate Anatomy Currently Supported",
        "",
        "| item | count |",
        "|---|---:|",
    ]
    for key, value in audit["aggregate_supported_anatomy"].items():
        lines.append(f"| `{key}` | {value} |")
    lines += [
        "",
        "## Checks",
        "",
        "| check | passed | detail |",
        "|---|---:|---|",
    ]
    for item in audit["checks"]:
        lines.append(f"| `{item['check']}` | {item['passed']} | `{item.get('detail', '')}` |")
    lines += [
        "",
        "## Blocked Reason",
        "",
        audit["blocked_reason"] or "Not blocked.",
        "",
        "## Minimum Next Artifact",
        "",
        f"- name: `{audit['minimum_next_artifact']['name']}`",
        "- required fields:",
        *[f"  - {field}" for field in audit["minimum_next_artifact"]["required_fields"]],
        "- forbidden fields:",
        *[f"  - {field}" for field in audit["minimum_next_artifact"]["forbidden_fields"]],
        f"- construction note: {audit['minimum_next_artifact']['construction_note']}",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-json", default=str(DEFAULT_JSON_OUT))
    parser.add_argument("--out-md", default=str(DEFAULT_MD_OUT))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    audit = build_audit()
    rendered_json = json.dumps(audit, ensure_ascii=False, indent=2) + "\n"
    rendered_md = render_md(audit)
    out_json = Path(args.out_json)
    out_md = Path(args.out_md)

    if args.check:
        existing_json = out_json.read_text(encoding="utf-8") if out_json.exists() else ""
        existing_md = out_md.read_text(encoding="utf-8") if out_md.exists() else ""
        if existing_json != rendered_json or existing_md != rendered_md:
            raise SystemExit("APSEC false-accept feasibility outputs are stale")
        print("APSEC false-accept feasibility outputs are current")
        return

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(rendered_json, encoding="utf-8")
    out_md.write_text(rendered_md, encoding="utf-8")
    print(f"wrote {out_json.relative_to(REPO_ROOT)}")
    print(f"wrote {out_md.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
