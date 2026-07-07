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
        "did not pass its readiness gate",
        "missed the predeclared verifier-readiness gate",
    ]
    forbidden_present = [token for token in forbidden_tokens if token in manuscript]

    checks = [
        check("manuscript_exists", MANUSCRIPT.exists(), str(MANUSCRIPT.relative_to(REPO_ROOT))),
        check("baseline_audit_passed", baseline.get("status") == "passed", baseline.get("status")),
        check("apsec_status_present", "APSEC technical-track Markdown rewrite" in manuscript),
        check(
            "target_format_note_present",
            "IEEEtran source package is generated separately" in manuscript
            and "not the final PDF" in manuscript,
        ),
        check("required_sections_present", not missing_sections, missing_sections),
        check(
            "title_scope_narrowed",
            "Evidence Visibility Shapes Risk Behavior in a Controlled LLM Patch-Verifier Study"
            in manuscript,
        ),
        check("contribution_bullets_present", "The paper makes three contributions:" in manuscript),
        check("evidence_visibility_protocol_present", "Evidence-Visibility Protocol (EVP-8)" in manuscript),
        check(
            "three_model_repaired_main_result_present",
            "three-model repaired v0.3 analysis for Qwen, DeepSeek, and Gemini" in manuscript
            and "| DeepSeek | E6 | 21 | 17 | 4 | 80.95% | 80.95% | 5.19% | 4.08% |"
            in manuscript
            and "| Gemini | E6 | 25 | 20 | 5 | 80.00% | 95.24% | 6.49% | 0.00% |"
            in manuscript,
        ),
        check(
            "dataset_composition_present",
            "98 candidate patches from 6 projects and 21 BugsInPy tasks" in manuscript
            and "| Correct reference | 21 |" in manuscript
            and "| Partial fix | 41 |" in manuscript
            and "| Regression patch | 1 |" in manuscript,
        ),
        check(
            "evidence_ladder_humanized",
            "Issue summary and candidate patch diff" in manuscript
            and "Structured changed-file/function map" in manuscript
            and "Deterministic merge-gate summary" in manuscript
            and "issue_patch_seed" not in manuscript,
        ),
        check(
            "rq4_demoted_from_main_questions",
            "The experiment asks three research questions." in manuscript
            and "RQ4 asks" not in manuscript,
        ),
        check(
            "qwen_main_result_present",
            "95.24%" in manuscript and "83.33%" in manuscript and "5.19%" in manuscript,
        ),
        check(
            "deepseek_main_result_present",
            "| DeepSeek | E3 | 16 | 13 | 3 | 81.25% | 61.90% | 3.90% | 8.16% |"
            in manuscript
            and "| DeepSeek | E6 | 21 | 17 | 4 | 80.95% | 80.95% | 5.19% | 4.08% |"
            in manuscript,
        ),
        check(
            "gemini_main_result_present",
            "| Gemini | E3 | 25 | 20 | 5 | 80.00% | 95.24% | 6.49% | 3.06% |"
            in manuscript
            and "| Gemini | E6 | 25 | 20 | 5 | 80.00% | 95.24% | 6.49% | 0.00% |"
            in manuscript,
        ),
        check(
            "ablation_main_table_boundary_present",
            "The E6 ablation is a separate verdict-field ablation package rather than the repaired v0.3 E0-E6 main table"
            in manuscript
            and "the DeepSeek E6-full row below should be read as ablation evidence"
            in manuscript,
        ),
        check("rule_only_baseline_present", "rule-only visible-tool" in manuscript),
        check(
            "rule_only_strength_acknowledged",
            "The deterministic rule-only baseline was already strong" in manuscript
            and "does not justify claiming a large LLM gain" in manuscript,
        ),
        check("qwen_e0_not_deterministic", "Qwen E0 is an observed model condition, not a deterministic no-tool verifier" in manuscript),
        check("majority_boundary_present", "Majority-vote and a separate E0/no-tool deterministic verifier are not reported as completed" in manuscript),
        check("ci_present", "CI table remains part of the analysis package" in manuscript and "Wilson intervals are wide" in manuscript),
        check(
            "false_accept_anatomy_present",
            "E6 false accepts were concentrated in partial and regression negatives" in manuscript
            and "Qwen and DeepSeek each accepted three partial fixes and one regression patch"
            in manuscript
            and "Gemini accepted four partial fixes and one regression patch"
            in manuscript
            and "| thefuck / thefuck_1 | Regression patch | DeepSeek, Gemini, Qwen |"
            in manuscript,
        ),
        check(
            "sanitized_false_accept_case_analysis_present",
            "The sanitized case-level export records candidate id" in manuscript
            and "excludes raw response text, full rationale text, rendered prompts, patch diffs, and credentials"
            in manuscript,
        ),
        check("tool_contestation_boundary_present", "strict correction remained zero for both models" in manuscript),
        check(
            "coverage_contestation_boundary_present",
            "Coverage-contestation removed repeated false accepts by becoming highly conservative" in manuscript
            and "reducing the false accept rate on 77 non-correct candidates to 0.00% for all three models" in manuscript
            and "DeepSeek and Gemini accepted no correct patches, and Qwen accepted only 2 of 21 correct patches" in manuscript
            and "prompt-sensitivity evidence, not a new main result" in manuscript
            and "should not claim that coverage-contestation improves autonomous verification" in manuscript,
        ),
        check(
            "hard_negative_stress_matrix_present",
            "A hard-negative stress matrix reduced false accepts through escalation" in manuscript
            and "31 hidden-failing candidates across PySnooper, cookiecutter, and scrapy" in manuscript
            and "The visible-tool baseline accepted all 31 cases" in manuscript
            and "62 repeated false accepts in 93 model-condition records" in manuscript
            and "reduced repeated false accepts to 12/93" in manuscript
            and "strict rejects remained 0 in both conditions" in manuscript,
        ),
        check(
            "hard_negative_stress_boundary_present",
            "curated no-API stress-source partial variants" in manuscript
            and "hard-negative stress-test supplement rather than a pure agent-generated realistic cohort" in manuscript
            and "Correct recall is also undefined in this all-negative cohort" in manuscript
            and "bounded triage evidence" in manuscript,
        ),
        check("figures_referenced", all(f"Figure {i}" in manuscript for i in [1, 2, 3])),
        check("all_expected_citations_present", not missing_citations, missing_citations),
        check("reference_support_records_removed", "Reference Support Records" not in manuscript),
        check(
            "remaining_broad_model_gap_explicit",
            "current paper-facing main result is three-model but still not broad-model" in manuscript
            and "still not a broad-model result" in manuscript,
        ),
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
            "readiness": "markdown_rewrite_ready_for_ieeetran_package"
            if status == "passed"
            else "rewrite_requires_repair",
            "remaining_work": [
                "Do not broaden the three-model repaired result into a universal LLM-verifier claim.",
                "Report coverage-contestation as conservative prompt-sensitivity evidence, not as an improved verifier.",
                "Report the hard-negative stress matrix as bounded triage evidence, not as strict correction or a pure realistic agent-patch result.",
                "Use the sanitized false-accept case analysis only as category-level failure anatomy, not as full rationale auditing.",
                "Compile and visually inspect the APSEC IEEEtran source package.",
                "Normalize BibTeX fields and check APSEC reference style.",
                "Check table widths, figure placement, page count, and double-blind wording in the compiled PDF.",
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
