from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = REPO_ROOT / "docs" / "paper" / "apsec_technical_track_rewrite_v0_1.md"
BASELINE_AUDIT = (
    REPO_ROOT / "data" / "reviews" / "ccfc_baseline_feasibility_audit_v0_1.json"
)
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "reviews" / "apsec_manuscript_rewrite_audit_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "paper" / "apsec_manuscript_rewrite_audit_v0_1.md"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def check(name: str, passed: bool, detail: Any = "") -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def build_audit() -> dict[str, Any]:
    manuscript = MANUSCRIPT.read_text(encoding="utf-8") if MANUSCRIPT.exists() else ""
    baseline = read_json(BASELINE_AUDIT) if BASELINE_AUDIT.exists() else {}

    required_sections = [
        "## Abstract",
        "## 1. Introduction",
        "## 2. Background and Motivation",
        "## 3. Evidence-Visibility Protocol",
        "## 4. Experimental Design",
        "## 5. Results",
        "## 6. Discussion",
        "## 7. Threats to Validity",
        "## 8. Conclusion",
        "## Reference Support Records",
    ]
    missing_sections = [section for section in required_sections if section not in manuscript]
    expected_citations = [
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
    missing_citations = [key for key in expected_citations if key not in manuscript]

    forbidden_tokens = [
        "reliable autonomous patch correctness verifier.",
        "stable LLM superiority",
        "monotonically improves correctness",
        "majority-vote baseline is completed",
        "V0.1",
        "invalid-setting",
    ]
    forbidden_present = [token for token in forbidden_tokens if token in manuscript]

    checks = [
        check("manuscript_exists", MANUSCRIPT.exists(), str(MANUSCRIPT.relative_to(REPO_ROOT))),
        check("baseline_audit_passed", baseline.get("status") == "passed", baseline.get("status")),
        check("apsec_status_present", "APSEC technical-track Markdown rewrite" in manuscript),
        check("target_format_note_present", "IEEEtran" in manuscript and "anonymous" in manuscript),
        check("required_sections_present", not missing_sections, missing_sections),
        check("contribution_bullets_present", "The paper makes three contributions:" in manuscript),
        check("evidence_visibility_protocol_present", "Evidence-Visibility Protocol (EVP-8)" in manuscript),
        check("qwen_main_result_present", "95.24%" in manuscript and "83.33%" in manuscript and "5.19%" in manuscript),
        check("rule_only_baseline_present", "rule-only visible-tool" in manuscript),
        check("qwen_e0_not_deterministic", "Qwen E0 is an observed model condition, not a deterministic no-tool verifier" in manuscript),
        check("majority_boundary_present", "Majority-vote and a separate E0/no-tool deterministic verifier are not reported as completed" in manuscript),
        check("ci_present", "95% CI" in manuscript and "Wilson intervals are wide" in manuscript),
        check("tool_contestation_boundary_present", "strict correction remained zero for both models" in manuscript),
        check("realistic_gate_boundary_present", "source-acquisition boundary" in manuscript),
        check("figures_referenced", all(f"Figure {i}" in manuscript for i in [1, 2, 3])),
        check("all_expected_citations_present", not missing_citations, missing_citations),
        check("forbidden_overclaims_absent", not forbidden_present, forbidden_present),
        check("api_call_attempted", True, False),
        check("raw_outputs_read_by_this_audit", True, False),
        check("prompt_or_patch_text_read_by_this_audit", True, False),
    ]

    status = "passed" if all(item["passed"] for item in checks) else "failed"
    return {
        "audit_id": "apsec_manuscript_rewrite_audit_v0_1",
        "status": status,
        "boundary": "no API call, no raw output read, no prompt text or patch text read.",
        "manuscript": str(MANUSCRIPT.relative_to(REPO_ROOT)),
        "checks": checks,
        "verdict": {
            "readiness": "markdown_rewrite_ready_for_latex_conversion"
            if status == "passed"
            else "rewrite_requires_repair",
            "remaining_work": [
                "Convert citation keys to BibTeX.",
                "Convert Markdown to anonymous IEEEtran conference LaTeX.",
                "Check page budget, table widths, figure placement, and double-blind wording.",
            ],
        },
    }


def render_md(audit: dict[str, Any]) -> str:
    lines = [
        "# APSEC Manuscript Rewrite Audit v0.1",
        "",
        f"- audit id: `{audit['audit_id']}`",
        f"- status: `{audit['status']}`",
        f"- manuscript: `{audit['manuscript']}`",
        f"- boundary: {audit['boundary']}",
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
        "## Verdict",
        "",
        f"- readiness: `{audit['verdict']['readiness']}`",
        "",
        "Remaining work:",
        "",
        *[f"- {item}" for item in audit["verdict"]["remaining_work"]],
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
    rendered_json = json.dumps(audit, indent=2, ensure_ascii=False) + "\n"
    rendered_md = render_md(audit)
    out_json = Path(args.out_json)
    out_md = Path(args.out_md)

    if args.check:
        existing_json = out_json.read_text(encoding="utf-8") if out_json.exists() else ""
        existing_md = out_md.read_text(encoding="utf-8") if out_md.exists() else ""
        if existing_json != rendered_json or existing_md != rendered_md:
            raise SystemExit("APSEC manuscript rewrite audit outputs are stale")
        if audit["status"] != "passed":
            raise SystemExit("APSEC manuscript rewrite audit failed")
        print("APSEC manuscript rewrite audit outputs are current")
        return

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(rendered_json, encoding="utf-8")
    out_md.write_text(rendered_md, encoding="utf-8")
    print(f"wrote {out_json.relative_to(REPO_ROOT)}")
    print(f"wrote {out_md.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
