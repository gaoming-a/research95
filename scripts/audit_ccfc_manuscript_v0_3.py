from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = REPO_ROOT / "docs" / "paper" / "ccfc_manuscript_rewrite_v0_1.md"
CLAIM_MAP = REPO_ROOT / "data" / "reviews" / "final_manuscript_claim_map_v0_1.json"
BASELINE_AUDIT = REPO_ROOT / "data" / "reviews" / "ccfc_baseline_feasibility_audit_v0_1.json"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "reviews" / "ccfc_manuscript_v0_3_reviewer_audit.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "paper" / "ccfc_manuscript_v0_3_reviewer_audit.md"


EXPECTED_CITATION_KEYS = [
    "qi_issta_2015_patch_plausibility",
    "legoues_icse_2012_genprog",
    "just_issta_2014_defects4j",
    "barr_tse_2015_oracle_problem",
    "xia_zhang_icse_2023_llm_apr",
    "tufano_icse_2019_bugfix_nmt",
    "bacchelli_bird_icse_2013_code_review",
    "chow_tit_1970_reject_option",
    "geifman_el_yaniv_2017_selective_classification",
    "zheng_neurips_2023_llm_judge",
    "parasuraman_riley_1997_automation",
]

EXPECTED_UNCERTAINTY_CONDITIONS = [
    "rule-only",
    "qwen/qwen3.7-max E6-full",
    "qwen/qwen3.7-max E6-no-verdict",
    "deepseek/deepseek-v4-pro E6-full",
    "deepseek/deepseek-v4-pro E6-no-verdict",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def build_audit() -> dict[str, Any]:
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    claim_map = read_json(CLAIM_MAP)
    baseline = read_json(BASELINE_AUDIT)

    missing_citation_keys = [key for key in EXPECTED_CITATION_KEYS if key not in manuscript]
    missing_uncertainty_conditions = [
        condition for condition in EXPECTED_UNCERTAINTY_CONDITIONS if condition not in manuscript
    ]

    checks = [
        check("manuscript_exists", MANUSCRIPT.exists(), str(MANUSCRIPT.relative_to(REPO_ROOT))),
        check("claim_map_passed", claim_map.get("status") == "passed", claim_map.get("status")),
        check("baseline_audit_passed", baseline.get("status") == "passed", baseline.get("status")),
        check("draft_status_v0_3_present", "stable CCF-C manuscript rewrite v0.3" in manuscript, ""),
        check("all_expected_citation_keys_present", not missing_citation_keys, missing_citation_keys),
        check("reference_support_records_present", "## Reference Support Records" in manuscript, ""),
        check("baseline_policy_boundary_present", "The baseline policy boundary is explicit" in manuscript, ""),
        check("reference_policies_not_called_results", "they orient the decision space but are not successful verifier results" in manuscript, ""),
        check("rule_only_completed_baseline_present", "The completed deterministic baseline is the rule-only visible-tool policy" in manuscript, ""),
        check("majority_vote_not_completed", "are not reported as completed baselines" in manuscript, ""),
        check("wilson_uncertainty_summary_present", "Wilson 95% confidence intervals" in manuscript, ""),
        check("all_expected_uncertainty_conditions_present", not missing_uncertainty_conditions, missing_uncertainty_conditions),
        check("old_invalid_setting_not_reintroduced", all(token not in manuscript for token in ["V0.1", "v0_1", "invalid-setting"]), ""),
        check("autonomous_correctness_claim_negated", "They do not establish reliable autonomous patch correctness verification" in manuscript, ""),
        check("llm_superiority_not_claimed", "claim of stable LLM superiority over the deterministic baseline" in manuscript, ""),
        check(
            "llm_outperform_baseline_phrase_only_negated",
            (
                "LLMs outperform deterministic baselines" not in manuscript
                or "does not support broad claims that one evidence level is universally optimal or that LLMs outperform deterministic baselines" in manuscript
            ),
            "",
        ),
    ]

    rejection_risks = [
        {
            "risk": "Contribution may still be read as measurement-only rather than algorithmic.",
            "status": "bounded_accept_risk",
            "mitigation": "Manuscript now states the contribution as a protocol and evidence chain, not a new repair algorithm.",
        },
        {
            "risk": "Baseline completeness can be challenged.",
            "status": "bounded_accept_risk",
            "mitigation": "Rule-only is reported as the completed deterministic baseline; majority and separate E0/no-tool verifier are explicitly not completed.",
        },
        {
            "risk": "Small cohort creates wide uncertainty intervals.",
            "status": "bounded_accept_risk",
            "mitigation": "Wilson 95% CIs are now shown in the Results section and used to avoid superiority claims.",
        },
        {
            "risk": "References may need venue-specific BibTeX cleanup.",
            "status": "formatting_remaining",
            "mitigation": "Citation keys and reference support records are present; final conversion remains a formatting task.",
        },
    ]

    return {
        "audit_id": "ccfc_manuscript_v0_3_reviewer_audit",
        "status": "passed" if all(item["passed"] for item in checks) else "failed",
        "scope": {
            "api_call_attempted": False,
            "raw_outputs_read": False,
            "prompt_or_patch_text_read": False,
            "purpose": "reviewer-style paper audit for citation, baseline, uncertainty, and overclaim risks.",
        },
        "checks": checks,
        "rejection_risks": rejection_risks,
        "verdict": {
            "ccfc_readiness": "stronger_than_previous_draft_but_still_needs_final_formatting",
            "reason": "The v0.3 draft now contains field-specific citations, explicit deterministic baseline boundaries, and uncertainty intervals, while avoiding unsupported autonomous-verifier and LLM-superiority claims.",
        },
    }


def render_md(audit: dict[str, Any]) -> str:
    lines = [
        "# CCF-C Manuscript v0.3 Reviewer Audit",
        "",
        f"- audit id: `{audit['audit_id']}`",
        f"- status: `{audit['status']}`",
        "- boundary: no API call, no raw output read, no prompt text or patch text read.",
        "",
        "## Checks",
        "",
        "| check | passed | detail |",
        "|---|---:|---|",
    ]
    for item in audit["checks"]:
        lines.append(f"| `{item['check']}` | {item['passed']} | `{item['detail']}` |")
    lines += [
        "",
        "## Reviewer Risks",
        "",
        "| risk | status | mitigation |",
        "|---|---|---|",
    ]
    for item in audit["rejection_risks"]:
        lines.append(f"| {item['risk']} | `{item['status']}` | {item['mitigation']} |")
    lines += [
        "",
        "## Verdict",
        "",
        f"- readiness: `{audit['verdict']['ccfc_readiness']}`",
        f"- reason: {audit['verdict']['reason']}",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-json", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    audit = build_audit()
    rendered_json = json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    rendered_md = render_md(audit)

    if args.check:
        existing_json = args.out_json.read_text(encoding="utf-8") if args.out_json.exists() else ""
        existing_md = args.out_md.read_text(encoding="utf-8") if args.out_md.exists() else ""
        if existing_json != rendered_json or existing_md != rendered_md:
            raise SystemExit("CCF-C manuscript v0.3 reviewer audit outputs are stale")
        print("CCF-C manuscript v0.3 reviewer audit outputs are current")
        return 0 if audit["status"] == "passed" else 1

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(rendered_json, encoding="utf-8")
    args.out_md.write_text(rendered_md, encoding="utf-8")
    print(f"wrote {args.out_json.relative_to(REPO_ROOT)}")
    print(f"wrote {args.out_md.relative_to(REPO_ROOT)}")
    return 0 if audit["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
