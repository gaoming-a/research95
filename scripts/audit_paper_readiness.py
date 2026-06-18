from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from scripts.audit_submission_handoff import DEFAULT_HANDOFF, audit_handoff
except ModuleNotFoundError:
    from audit_submission_handoff import DEFAULT_HANDOFF, audit_handoff


DEFAULT_FULL_RUN_DIR = Path("outputs") / "patch_verification_api_pilot_002"
DEFAULT_TOOL_AUGMENTED_FULL_RUN_DIR = Path("outputs") / "patch_verification_tool_augmented_full_001"
DEFAULT_EVP7_SUMMARY = Path("data") / "reviews" / "evp7_g5_llm_376_full_summary.json"
DEFAULT_EVP7_QUALITY_AUDIT = Path("data") / "reviews" / "evp7_g5_376_full_quality_audit.json"
DEFAULT_EVP7_CLAIM_TRACEABILITY = Path("data") / "reviews" / "evp7_g5_376_claim_traceability.json"
DEFAULT_EVP7_UTILITY_SENSITIVITY = Path("data") / "reviews" / "evp7_g5_376_utility_sensitivity.json"
DEFAULT_EVP7_TOOL_ATTRIBUTION = Path("data") / "reviews" / "evp7_g5_376_tool_attribution.json"
DEFAULT_EVP7_QUALITATIVE_CASES = Path("data") / "reviews" / "evp7_g5_376_qualitative_cases.json"


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def count_jsonl(path: Path) -> int | None:
    if not path.exists():
        return None
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_text_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def file_state(path: Path) -> dict[str, Any]:
    return {
        "path": path.as_posix(),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
    }


def paper_framing_state() -> dict[str, Any]:
    current_title = "Evidence Visibility Matters: A Systematic Study of LLM-Based Verification for Candidate Patches"
    stale_title = "Verifiable Review of AI-Generated Patches"
    paths = {
        "research_definition": Path("docs") / "paper" / "research_definition.md",
        "paper_outline": Path("docs") / "paper" / "patch_verification_outline.md",
        "paper_draft": Path("docs") / "paper" / "patch_verification_draft.md",
        "ieee_submission_draft": Path("docs") / "paper" / "ieee_submission_draft.tex",
        "ieee_submission_generator": Path("scripts") / "write_ieee_latex_draft.py",
        "related_work_positioning": Path("docs") / "experiments" / "evp7_related_work_positioning.md",
        "related_work_ris": Path("docs") / "references" / "evp7_related_work_references.ris",
    }
    texts = {name: read_text_if_exists(path) for name, path in paths.items()}
    normalized_texts = {name: " ".join(text.split()) for name, text in texts.items()}
    checks = {
        "outline_uses_current_title": current_title in normalized_texts["paper_outline"],
        "outline_mentions_evidence_visibility": "evidence visibility" in texts["paper_outline"].lower(),
        "outline_mentions_bounded_evp7": "bounded EVP-7" in texts["paper_outline"],
        "research_definition_uses_evidence_visibility": "evidence-visibility workflow" in texts[
            "research_definition"
        ],
        "research_definition_bounds_current_claims": "bounded pilot observations only" in texts[
            "research_definition"
        ],
        "markdown_draft_uses_current_title": texts["paper_draft"].startswith(f"# {current_title}"),
        "ieee_draft_uses_current_title": rf"\title{{{current_title}}}" in texts["ieee_submission_draft"],
        "ieee_fig2_caption_uses_evp7_levels": "EVP-7 evidence visibility levels"
        in normalized_texts["ieee_submission_draft"],
        "ieee_fig2_caption_keeps_truth_labels_hidden": "Evaluator truth labels remain hidden at all levels"
        in normalized_texts["ieee_submission_draft"],
        "generator_fig2_caption_uses_evp7_levels": "EVP-7 evidence visibility levels"
        in normalized_texts["ieee_submission_generator"],
        "fig2_caption_does_not_use_old_condition_wording": "Evidence visibility by condition"
        not in texts["ieee_submission_draft"]
        and "tool-augmented condition is distinguished" not in texts["ieee_submission_draft"]
        and "Evidence visibility by condition" not in texts["ieee_submission_generator"]
        and "tool-augmented condition is distinguished" not in texts["ieee_submission_generator"],
        "ieee_abstract_foregrounds_frozen_evp7": "We construct a frozen EVP-7 pilot"
        in normalized_texts["ieee_submission_draft"]
        and "Earlier 30-candidate API pilots motivate the design boundary"
        in normalized_texts["ieee_submission_draft"],
        "generator_abstract_foregrounds_frozen_evp7": "We construct a frozen EVP-7 pilot"
        in normalized_texts["ieee_submission_generator"]
        and "Earlier 30-candidate API pilots motivate the design boundary"
        in normalized_texts["ieee_submission_generator"],
        "ieee_abstract_not_centered_on_old_first_pilot": "The first pilot contains 30 validated patch candidates"
        not in texts["ieee_submission_draft"]
        and "We then run an EVP-7 evidence-visibility pilot" not in texts["ieee_submission_draft"]
        and "The first pilot contains 30 validated patch candidates" not in texts["ieee_submission_generator"]
        and "We then run an EVP-7 evidence-visibility pilot" not in texts["ieee_submission_generator"],
        "ieee_mentions_tool_attribution_boundary": "deterministic tool-only attribution analysis"
        in normalized_texts["ieee_submission_draft"]
        and "bounded safety/recall tradeoff interpretation" in normalized_texts["ieee_submission_draft"],
        "generator_mentions_tool_attribution_boundary": "deterministic tool-only attribution analysis"
        in normalized_texts["ieee_submission_generator"]
        and "bounded safety/recall tradeoff interpretation" in normalized_texts["ieee_submission_generator"],
        "generated_tables_include_tool_attribution": "tab:evp7-tool-attribution" in texts["ieee_submission_draft"]
        and "EVP-7 deterministic tool-only attribution" in normalized_texts["ieee_submission_draft"],
        "ieee_mentions_qualitative_case_boundary": "qualitative case audit"
        in normalized_texts["ieee_submission_draft"]
        and "model-visible decision sequence" in normalized_texts["ieee_submission_draft"]
        and "evaluator-only interpretation" in normalized_texts["ieee_submission_draft"],
        "generator_mentions_qualitative_case_boundary": "qualitative case audit"
        in normalized_texts["ieee_submission_generator"]
        and "model-visible decision sequence" in normalized_texts["ieee_submission_generator"]
        and "evaluator-only interpretation" in normalized_texts["ieee_submission_generator"],
        "ieee_has_related_work_section": r"\section{Related Work and Positioning}"
        in texts["ieee_submission_draft"],
        "generator_has_related_work_section": r"\section{{Related Work and Positioning}}"
        in texts["ieee_submission_generator"],
        "markdown_draft_has_related_work_section": "## 2. Related Work and Positioning" in texts["paper_draft"],
        "related_work_distinguishes_evidence_visibility": "Evidence Gain is a descriptive pilot metric"
        in normalized_texts["ieee_submission_draft"]
        and "not a proposed universal benchmark score" in normalized_texts["ieee_submission_draft"],
        "related_work_cites_core_sources": all(
            key in texts["ieee_submission_draft"]
            for key in [
                "just2014defects4j",
                "widyasari2020bugsinpy",
                "jimenez2024swebench",
                "qi2015patchcorrectness",
                "xia2023llmapr",
                "yang2024sweagent",
            ]
        ),
        "related_work_has_bibliography": r"\begin{thebibliography}{9}" in texts["ieee_submission_draft"]
        and r"\end{thebibliography}" in texts["ieee_submission_draft"],
        "related_work_positioning_doc_exists": bool(texts["related_work_positioning"])
        and "Segment-to-Reference Map" in texts["related_work_positioning"],
        "related_work_ris_exists": bool(texts["related_work_ris"])
        and "TY  - CONF" in texts["related_work_ris"]
        and "ID  - just2014defects4j" in texts["related_work_ris"],
        "ieee_has_reader_flow_section": r"\section{How to Read the Experiment}"
        in texts["ieee_submission_draft"],
        "generator_has_reader_flow_section": r"\section{{How to Read the Experiment}}"
        in texts["ieee_submission_generator"],
        "markdown_draft_has_reader_flow_section": "## 3. How to Read the Experiment" in texts["paper_draft"],
        "reader_flow_mentions_five_step_path": all(
            phrase in normalized_texts["ieee_submission_draft"]
            for phrase in [
                "candidate patch",
                "model-visible evidence packet",
                "accept, reject, or escalate",
                "hidden evaluator labels and oracle outcomes are joined only after the decision",
                "aggregated into false accepts, correct recall, escalation, utility",
            ]
        ),
        "reader_flow_references_fig7": "fig7_decision_metric_flow.pdf" in texts["ieee_submission_draft"]
        and r"\label{fig:decision-metric-flow}" in texts["ieee_submission_draft"],
        "reader_flow_marks_first_pilot_diagnostic": "diagnostic design evidence"
        in normalized_texts["ieee_submission_draft"]
        and "frozen EVP-7 run is the paper-facing evidence-visibility result"
        in normalized_texts["ieee_submission_draft"],
        "final_polish_uses_bounded_conclusion": "The paper-facing artifact reports a frozen EVP-7"
        in normalized_texts["ieee_submission_draft"]
        and "Within this bounded single-model setting" in normalized_texts["ieee_submission_draft"],
        "final_polish_formats_unsupported_claims": "quality audit also rejects four interpretations"
        in normalized_texts["ieee_submission_draft"]
        and "(1) Scale-generalized paper claims beyond EVP-7" in normalized_texts["ieee_submission_draft"],
        "final_polish_uses_evidence_gain_title_case": "evidence gain 7" not in texts[
            "ieee_submission_draft"
        ]
        and "evidence gain 14" not in texts["ieee_submission_draft"]
        and "Evidence Gain" in texts["ieee_submission_draft"],
        "current_artifacts_do_not_use_stale_title": all(
            stale_title not in normalized_text for normalized_text in normalized_texts.values()
        ),
    }
    blockers = [name for name, passed in checks.items() if not passed]
    return {
        "passed": not blockers,
        "title": current_title,
        "paths": {name: path.as_posix() for name, path in paths.items()},
        "checks": checks,
        "blockers": blockers,
    }


def protocol_current_state() -> dict[str, Any]:
    path = Path("docs") / "protocol" / "evidence_visibility_protocol.md"
    text = read_text_if_exists(path)
    checks = {
        "mentions_21_task_structural_cohort": "21 tasks and 6 projects" in text
        or "21-task / 98-candidate / 392-packet" in text,
        "mentions_98_candidates": "98 promoted candidates" in text and "98-candidate" in text,
        "mentions_392_packets": "392 E0/E2/E4/E6" in text,
        "mentions_294_tool_only_decisions": "294 total tool-only decisions" in text,
        "mentions_376_real_llm_records": "376/376 parse-valid non-mock records" in text,
        "uses_current_g5_output_dir": "outputs/evp7_g5_llm_376_full_001/" in text,
        "keeps_248_run_historical": "248-packet DeepSeek official run remains a historical checkpoint" in text,
        "does_not_describe_86_as_current": "It contains 86 promoted candidates" not in text,
        "does_not_describe_70_per_condition_as_current": "each produce 70 schema-valid decisions" not in text,
        "does_not_describe_280_schema_as_current": "all 280 E0/E2/E4/E6" not in text,
        "does_not_describe_248_g5_as_current": "G5 has a fresh 248-packet real DeepSeek official run" not in text,
    }
    blockers = [name for name, passed in checks.items() if not passed]
    return {
        "passed": not blockers,
        "path": path.as_posix(),
        "checks": checks,
        "blockers": blockers,
    }


def protocol_pilot_report_state() -> dict[str, Any]:
    path = Path("docs") / "experiments" / "evp7_protocol_pilot.md"
    text = read_text_if_exists(path)
    checks = {
        "mentions_21_task_structural_state": "21 tasks / 6 projects / 98 candidates / 392" in text
        and "21-task/98-candidate/392-packet structural no-API cohort" in text,
        "mentions_historical_20_task_real_run_boundary": "20 tasks / 5 projects / 94 candidates / 376" in text
        and "scope boundary = frozen 20-task/94-candidate/376-packet" in text,
        "mentions_current_376_g5_run": "review count = 376" in text and "parse valid = 376/376" in text,
        "mentions_current_376_outputs": "outputs/evp7_g5_llm_376_full_001/" in text
        and "data/reviews/evp7_g5_llm_376_full_summary.json" in text,
        "mentions_current_quality_audit": "docs/experiments/evp7_g5_376_full_quality_audit.md" in text
        and "data/reviews/evp7_g5_376_full_quality_audit.json" in text,
        "keeps_248_run_historical": "248-record DeepSeek G5 full run remains a historical checkpoint" in text,
        "next_step_not_more_bug_or_g5_by_default": "not another bug admission or another G5 run" in text,
        "does_not_call_12_task_current": "current tracked EVP-7 structural cohort\nis therefore 12 bugs" not in text,
        "does_not_call_18_tasks_current": "contains 18 completed project-level P2P-broad tasks" not in text,
        "does_not_use_248_output_as_current": "outputs/evp7_g5_llm_248_full/" not in text,
        "does_not_say_376_run_pending": "fresh G5 real-LLM pass for the current 376-packet" not in text,
    }
    blockers = [name for name, passed in checks.items() if not passed]
    return {
        "passed": not blockers,
        "path": path.as_posix(),
        "checks": checks,
        "blockers": blockers,
    }


def final_roadmap_state() -> dict[str, Any]:
    path = Path("docs") / "plans" / "final_paper_roadmap_zh.md"
    text = read_text_if_exists(path)
    checks = {
        "mentions_current_21_98_392_structural_state": "21 tasks" in text
        and "98 candidates" in text
        and "392" in text,
        "mentions_current_294_tool_only": "294 条 schema-valid decisions" in text
        or "294" in text,
        "mentions_current_392_dry_run": "392 条 E0/E2/E4/E6 dry-run" in text
        or "392-packet" in text,
        "mentions_current_392_prompts": "392 条 prompts" in text
        or "392 prompt" in text,
        "mentions_current_376_g5_run": "当前 paper-facing 376-packet DeepSeek V4 G5 full run" in text
        and "376/376" in text,
        "keeps_248_run_historical": "248-packet historical bounded pilot observation" in text
        and "不再是当前主 cohort 的最新真实模型结果" in text,
        "does_not_call_46_candidates_current": "共 46 条候选" not in text,
        "does_not_call_200_packets_current": "共 200 条" not in text,
        "does_not_call_150_tool_decisions_current": "共生成 150 条 schema-valid decisions" not in text,
        "does_not_call_248_prompts_current": "248 条 prompts" not in text,
    }
    blockers = [name for name, passed in checks.items() if not passed]
    return {
        "passed": not blockers,
        "path": path.as_posix(),
        "checks": checks,
        "blockers": blockers,
    }


def review_state(run_dir: Path) -> dict[str, Any]:
    reviews_path = run_dir / "reviews.jsonl"
    metrics_path = run_dir / "metrics.json"
    reviews_count = count_jsonl(reviews_path)
    metrics = read_json(metrics_path)
    metric_count = metrics.get("verifier_output_count") if metrics else None
    return {
        "reviews_path": reviews_path.as_posix(),
        "reviews_count": reviews_count,
        "metrics_path": metrics_path.as_posix(),
        "metrics_count": metric_count,
        "counts_match": reviews_count is not None and reviews_count == metric_count,
    }


def failure_state(run_dir: Path) -> dict[str, Any]:
    failure_json = read_json(run_dir / "failure_examples.json")
    if failure_json is None:
        return {
            "exists": False,
            "mock_review_count": None,
            "bucket_counts": {},
            "usable_for_paper": False,
        }
    return {
        "exists": True,
        "mock_review_count": failure_json.get("mock_review_count"),
        "bucket_counts": failure_json.get("bucket_counts", {}),
        "usable_for_paper": failure_json.get("mock_review_count") == 0,
    }


def gate_state(run_dir: Path) -> dict[str, Any]:
    gate = read_json(run_dir / "gate_report.json")
    if gate is None:
        return {
            "exists": False,
            "verdict": None,
            "usable_for_positive_claim": False,
        }
    return {
        "exists": True,
        "verdict": gate.get("verdict"),
        "reason": gate.get("reason"),
        "mock_review_count": gate.get("mock_review_count"),
        "usable_for_positive_claim": gate.get("verdict") == "continue" and gate.get("mock_review_count") == 0,
    }


def tool_augmented_gate_state(run_dir: Path) -> dict[str, Any]:
    gate = read_json(run_dir / "tool_augmented_full_gate.json")
    if gate is None:
        return {
            "exists": False,
            "passed": False,
            "condition_counts": {},
            "metrics": {},
            "mock_review_count": None,
            "usable_for_tool_augmented_claim": False,
        }
    metrics = gate.get("metrics", {}) if isinstance(gate.get("metrics"), dict) else {}
    condition_counts = gate.get("condition_counts", {}) if isinstance(gate.get("condition_counts"), dict) else {}
    usable = (
        gate.get("passed") is True
        and gate.get("mock_review_count") == 0
        and condition_counts == {"tool_augmented_evidence": 30}
        and metrics.get("false_accept_rate") == 0.0
        and metrics.get("correct_patch_recall") == 1.0
        and metrics.get("invalid_output_rate") == 0.0
    )
    return {
        "exists": True,
        "passed": gate.get("passed") is True,
        "condition_counts": condition_counts,
        "metrics": metrics,
        "mock_review_count": gate.get("mock_review_count"),
        "usable_for_tool_augmented_claim": usable,
    }


def completeness_state(run_dir: Path) -> dict[str, Any]:
    completeness = read_json(run_dir / "run_completeness.json")
    if completeness is None:
        return {
            "exists": False,
            "passed": False,
            "expected_records": None,
            "review_count": None,
            "mock_review_count": None,
            "usable_full_run": False,
        }
    return {
        "exists": True,
        "passed": completeness.get("passed") is True,
        "expected_records": completeness.get("expected_records"),
        "review_count": completeness.get("review_count"),
        "mock_review_count": completeness.get("mock_review_count"),
        "usable_full_run": (
            completeness.get("passed") is True
            and completeness.get("expected_records") == 60
            and completeness.get("review_count") == 60
            and completeness.get("mock_review_count") == 0
        ),
    }


def tool_augmented_completeness_state(run_dir: Path) -> dict[str, Any]:
    completeness = read_json(run_dir / "run_completeness.json")
    if completeness is None:
        return {
            "exists": False,
            "passed": False,
            "expected_records": None,
            "review_count": None,
            "mock_review_count": None,
            "usable_tool_augmented_full_run": False,
        }
    return {
        "exists": True,
        "passed": completeness.get("passed") is True,
        "expected_records": completeness.get("expected_records"),
        "review_count": completeness.get("review_count"),
        "mock_review_count": completeness.get("mock_review_count"),
        "usable_tool_augmented_full_run": (
            completeness.get("passed") is True
            and completeness.get("expected_records") == 30
            and completeness.get("review_count") == 30
            and completeness.get("mock_review_count") == 0
        ),
    }


def evp7_g5_state(
    summary_path: Path,
    quality_path: Path,
    claim_traceability_path: Path,
    utility_sensitivity_path: Path,
    tool_attribution_path: Path,
    qualitative_cases_path: Path,
) -> dict[str, Any]:
    summary = read_json(summary_path)
    quality = read_json(quality_path)
    claim_traceability = read_json(claim_traceability_path)
    utility_sensitivity = read_json(utility_sensitivity_path)
    tool_attribution = read_json(tool_attribution_path)
    qualitative_cases = read_json(qualitative_cases_path)
    metrics = summary.get("metrics", {}) if isinstance(summary, dict) else {}
    metric_groups = metrics.get("metric_groups", {}) if isinstance(metrics, dict) else {}
    quality_checks = quality.get("checks", []) if isinstance(quality, dict) else []
    quality_check_map = {
        str(item.get("check")): item
        for item in quality_checks
        if isinstance(item, dict) and item.get("check") is not None
    }
    level_counts = quality.get("level_counts", {}) if isinstance(quality, dict) else {}
    required_docs = {
        "protocol": file_state(Path("docs") / "protocol" / "evidence_visibility_protocol.md"),
        "run_result": file_state(Path("docs") / "experiments" / "evp7_g5_llm_376_full_result.md"),
        "quality_audit": file_state(Path("docs") / "experiments" / "evp7_g5_376_full_quality_audit.md"),
        "claim_traceability": file_state(Path("docs") / "experiments" / "evp7_g5_376_claim_traceability.md"),
        "utility_sensitivity": file_state(Path("docs") / "experiments" / "evp7_g5_376_utility_sensitivity.md"),
        "tool_attribution": file_state(Path("docs") / "experiments" / "evp7_g5_376_tool_attribution.md"),
        "qualitative_cases": file_state(Path("docs") / "experiments" / "evp7_g5_376_qualitative_cases.md"),
        "expansion_readiness": file_state(Path("docs") / "experiments" / "evp7_expansion_readiness.md"),
    }
    required_levels = {"E0": 94, "E2": 94, "E4": 94, "E6": 94}
    supported_claims = quality.get("supported_claims", []) if isinstance(quality, dict) else []
    unsupported_claims = quality.get("unsupported_claims", []) if isinstance(quality, dict) else []
    ready = bool(
        summary
        and quality
        and metrics.get("run_kind") == "real_llm"
        and metrics.get("g5_metric_scaffold") == "passed"
        and metrics.get("g5_signal_claim_status") == "real_llm_verifier_signal_observed_on_evp7"
        and summary.get("quality", {}).get("review_count") == 376
        and summary.get("quality", {}).get("unique_review_ids") == 376
        and summary.get("quality", {}).get("invalid_output_rate", 1.0) <= 0.02
        and quality.get("quality_status") in {"passed", "passed_with_limitations"}
        and quality.get("raw_outputs_read") is False
        and quality.get("raw_outputs_tracked") is False
        and quality.get("review_count") == 376
        and quality.get("candidate_count") == 94
        and claim_traceability
        and claim_traceability.get("passed") is True
        and claim_traceability.get("raw_output_free_check", {}).get("passed") is True
        and utility_sensitivity
        and utility_sensitivity.get("raw_output_free_check", {}).get("passed") is True
        and utility_sensitivity.get("scenario_count") == 27
        and tool_attribution
        and tool_attribution.get("raw_output_free_check", {}).get("passed") is True
        and ((tool_attribution.get("comparisons") or {}).get("E6") or {}).get("agreement_count") == 76
        and ((tool_attribution.get("comparisons") or {}).get("E6") or {}).get(
            "llm_accept_subset_of_tool_accepts"
        )
        is True
        and (
            (((tool_attribution.get("comparisons") or {}).get("E6") or {}).get("tool_false_accept_recovery") or {}).get(
                "recovered"
            )
            == 4
        )
        and qualitative_cases
        and qualitative_cases.get("raw_output_free_check", {}).get("passed") is True
        and qualitative_cases.get("raw_output_free_check", {}).get("reviewer_facing_truth_label_separated") is True
        and qualitative_cases.get("case_count") == 6
        and set(qualitative_cases.get("case_roles", []))
        == {
            "evidence_enabled_accept",
            "tool_false_accept_recovered_by_llm",
            "correct_patch_downgraded_by_llm",
            "tool_summary_late_accept",
            "no_op_rejected_after_evidence",
            "partial_patch_rejected_after_evidence",
        }
        and level_counts == required_levels
        and all(doc["exists"] for doc in required_docs.values())
        and (metric_groups.get("E4") or {}).get("false_accept_rate") == 0.0
        and (metric_groups.get("E6") or {}).get("false_accept_rate") == 0.0
        and (metric_groups.get("E4") or {}).get("accepted_precision") == 1.0
        and (metric_groups.get("E6") or {}).get("accepted_precision") == 1.0
        and (metric_groups.get("E4") or {}).get("correct_recall", 0.0) > 0.0
        and (metric_groups.get("E6") or {}).get("correct_recall", 0.0) > 0.0
        and (metric_groups.get("E4") or {}).get("evidence_gain_vs_e0", 0.0) > 0.0
        and (metric_groups.get("E6") or {}).get("evidence_gain_vs_e0", 0.0) > 0.0
    )
    blockers: list[str] = []
    if summary is None:
        blockers.append(f"Missing EVP-7 G5 summary: {summary_path.as_posix()}.")
    if quality is None:
        blockers.append(f"Missing EVP-7 G5 quality audit: {quality_path.as_posix()}.")
    if claim_traceability is None:
        blockers.append(f"Missing EVP-7 claim traceability audit: {claim_traceability_path.as_posix()}.")
    if claim_traceability and claim_traceability.get("passed") is not True:
        blockers.append("EVP-7 claim traceability audit has not passed.")
    if claim_traceability and claim_traceability.get("raw_output_free_check", {}).get("passed") is not True:
        blockers.append("EVP-7 claim traceability audit is not raw-output-free.")
    if utility_sensitivity is None:
        blockers.append(f"Missing EVP-7 utility sensitivity analysis: {utility_sensitivity_path.as_posix()}.")
    if utility_sensitivity and utility_sensitivity.get("raw_output_free_check", {}).get("passed") is not True:
        blockers.append("EVP-7 utility sensitivity analysis is not raw-output-free.")
    if utility_sensitivity and utility_sensitivity.get("scenario_count") != 27:
        blockers.append("EVP-7 utility sensitivity analysis does not cover the expected 27 penalty scenarios.")
    if tool_attribution is None:
        blockers.append(f"Missing EVP-7 tool-only attribution analysis: {tool_attribution_path.as_posix()}.")
    if tool_attribution and tool_attribution.get("raw_output_free_check", {}).get("passed") is not True:
        blockers.append("EVP-7 tool-only attribution analysis is not raw-output-free.")
    if tool_attribution and ((tool_attribution.get("comparisons") or {}).get("E6") or {}).get("agreement_count") != 76:
        blockers.append("EVP-7 tool-only attribution analysis does not match the expected E6 agreement count.")
    if qualitative_cases is None:
        blockers.append(f"Missing EVP-7 qualitative case analysis: {qualitative_cases_path.as_posix()}.")
    if qualitative_cases and qualitative_cases.get("raw_output_free_check", {}).get("passed") is not True:
        blockers.append("EVP-7 qualitative case analysis is not raw-output-free.")
    if (
        qualitative_cases
        and qualitative_cases.get("raw_output_free_check", {}).get("reviewer_facing_truth_label_separated") is not True
    ):
        blockers.append("EVP-7 qualitative case analysis does not separate reviewer-facing labels.")
    if qualitative_cases and qualitative_cases.get("case_count") != 6:
        blockers.append("EVP-7 qualitative case analysis does not contain the expected six cases.")
    if summary and metrics.get("run_kind") != "real_llm":
        blockers.append("EVP-7 G5 summary is not marked as a real LLM run.")
    if summary and metrics.get("g5_metric_scaffold") != "passed":
        blockers.append("EVP-7 G5 metric scaffold has not passed.")
    if summary and metrics.get("g5_signal_claim_status") != "real_llm_verifier_signal_observed_on_evp7":
        blockers.append("EVP-7 G5 signal status is not ready for bounded pilot claims.")
    if quality and quality.get("quality_status") not in {"passed", "passed_with_limitations"}:
        blockers.append(f"EVP-7 quality status is `{quality.get('quality_status')}`.")
    if quality and quality.get("raw_outputs_tracked") is not False:
        blockers.append("EVP-7 quality audit does not prove raw outputs stay untracked.")
    if quality and level_counts != required_levels:
        blockers.append(f"EVP-7 level counts are `{level_counts}`, expected `{required_levels}`.")
    missing_docs = [name for name, state in required_docs.items() if not state["exists"]]
    if missing_docs:
        blockers.append(f"Missing EVP-7 tracked docs: {', '.join(missing_docs)}.")
    return {
        "summary_path": summary_path.as_posix(),
        "quality_audit_path": quality_path.as_posix(),
        "claim_traceability_path": claim_traceability_path.as_posix(),
        "utility_sensitivity_path": utility_sensitivity_path.as_posix(),
        "tool_attribution_path": tool_attribution_path.as_posix(),
        "qualitative_cases_path": qualitative_cases_path.as_posix(),
        "ready_for_bounded_pilot_claim": ready,
        "blockers": blockers,
        "required_docs": required_docs,
        "quality_status": quality.get("quality_status") if quality else None,
        "review_count": quality.get("review_count") if quality else None,
        "candidate_count": quality.get("candidate_count") if quality else None,
        "level_counts": level_counts,
        "raw_outputs_tracked": quality.get("raw_outputs_tracked") if quality else None,
        "run_kind": metrics.get("run_kind") if metrics else None,
        "g5_signal_claim_status": metrics.get("g5_signal_claim_status") if metrics else None,
        "invalid_output_rate": summary.get("quality", {}).get("invalid_output_rate") if summary else None,
        "metric_groups": {
            level: {
                "false_accept_rate": (metric_groups.get(level) or {}).get("false_accept_rate"),
                "accepted_precision": (metric_groups.get(level) or {}).get("accepted_precision"),
                "correct_recall": (metric_groups.get(level) or {}).get("correct_recall"),
                "evidence_gain_vs_e0": (metric_groups.get(level) or {}).get("evidence_gain_vs_e0"),
            }
            for level in ["E0", "E2", "E4", "E6"]
        },
        "supported_claims": supported_claims,
        "unsupported_claims": unsupported_claims,
        "quality_checks": {
            name: {
                "passed": item.get("passed"),
                "observed": item.get("observed"),
            }
            for name, item in sorted(quality_check_map.items())
        },
        "claim_traceability": {
            "exists": claim_traceability is not None,
            "passed": claim_traceability.get("passed") if claim_traceability else None,
            "raw_output_free": (
                claim_traceability.get("raw_output_free_check", {}).get("passed")
                if claim_traceability
                else None
            ),
        },
        "utility_sensitivity": {
            "exists": utility_sensitivity is not None,
            "scenario_count": utility_sensitivity.get("scenario_count") if utility_sensitivity else None,
            "raw_output_free": (
                utility_sensitivity.get("raw_output_free_check", {}).get("passed")
                if utility_sensitivity
                else None
            ),
            "dominant_best_level": (
                utility_sensitivity.get("stability_summary", {}).get("dominant_best_level")
                if utility_sensitivity
                else None
            ),
        },
        "tool_attribution": {
            "exists": tool_attribution is not None,
            "raw_output_free": (
                tool_attribution.get("raw_output_free_check", {}).get("passed")
                if tool_attribution
                else None
            ),
            "E6_agreement_count": ((tool_attribution.get("comparisons") or {}).get("E6") or {}).get(
                "agreement_count"
            )
            if tool_attribution
            else None,
            "E6_llm_accept_subset_of_tool_accepts": ((tool_attribution.get("comparisons") or {}).get("E6") or {}).get(
                "llm_accept_subset_of_tool_accepts"
            )
            if tool_attribution
            else None,
            "E6_recovered_tool_false_accepts": (
                (((tool_attribution.get("comparisons") or {}).get("E6") or {}).get("tool_false_accept_recovery") or {})
            ).get("recovered")
            if tool_attribution
            else None,
        },
        "qualitative_cases": {
            "exists": qualitative_cases is not None,
            "case_count": qualitative_cases.get("case_count") if qualitative_cases else None,
            "raw_output_free": (
                qualitative_cases.get("raw_output_free_check", {}).get("passed")
                if qualitative_cases
                else None
            ),
            "reviewer_facing_truth_label_separated": (
                qualitative_cases.get("raw_output_free_check", {}).get("reviewer_facing_truth_label_separated")
                if qualitative_cases
                else None
            ),
            "case_roles": qualitative_cases.get("case_roles") if qualitative_cases else None,
        },
    }


def build_audit(args: argparse.Namespace) -> dict[str, Any]:
    run_dir = Path(args.full_run_dir)
    tool_augmented_run_dir = Path(args.tool_augmented_run_dir)
    evp7 = evp7_g5_state(
        Path(args.evp7_summary),
        Path(args.evp7_quality_audit),
        Path(args.evp7_claim_traceability),
        Path(args.evp7_utility_sensitivity),
        Path(args.evp7_tool_attribution),
        Path(args.evp7_qualitative_cases),
    )
    required_docs = {
        "pilot_report": file_state(Path("docs") / "experiments" / "patch_verification_pilot_report.md"),
        "tool_augmented_full_result": file_state(
            Path("docs") / "experiments" / "tool_augmented_full_run_result.md"
        ),
        "research_definition": file_state(Path("docs") / "paper" / "research_definition.md"),
        "paper_draft": file_state(Path("docs") / "paper" / "patch_verification_draft.md"),
        "paper_outline": file_state(Path("docs") / "paper" / "patch_verification_outline.md"),
        "advisor_workload_response": file_state(Path("docs") / "paper" / "advisor_workload_response_zh.md"),
        "generated_tables_md": file_state(Path("docs") / "paper" / "generated_tables.md"),
        "generated_tables_tex": file_state(Path("docs") / "paper" / "generated_tables.tex"),
        "ieee_preapi_draft": file_state(Path("docs") / "paper" / "ieee_preapi_draft.tex"),
        "ieee_submission_draft": file_state(Path("docs") / "paper" / "ieee_submission_draft.tex"),
        "model_selection_shortlist": file_state(Path("docs") / "experiments" / "model_selection_shortlist.md"),
        "model_selection_protocol": file_state(Path("docs") / "experiments" / "model_selection_protocol.md"),
        "related_work_positioning": file_state(
            Path("docs") / "experiments" / "evp7_related_work_positioning.md"
        ),
        "related_work_ris": file_state(Path("docs") / "references" / "evp7_related_work_references.ris"),
        "submission_checklist": file_state(Path("docs") / "artifact" / "submission_checklist.md"),
        "submission_handoff": file_state(DEFAULT_HANDOFF),
        "submission_freeze_candidate": file_state(
            Path("docs") / "artifact" / "submission_freeze_candidate_20260618.md"
        ),
    }
    pre_api_evidence = {
        "reproducibility_compare": file_state(Path("outputs") / "reproducibility" / "pilot_compare.json"),
        "model_catalog_audit": file_state(Path("outputs") / "model_selection" / "openrouter_catalog_audit.json"),
        "pre_api_handoff": file_state(Path("outputs") / "handoff" / "pre_api_handoff.json"),
    }
    run_files = {
        "api_pilot_report": file_state(run_dir / "api_pilot_report.md"),
        "run_summary": file_state(run_dir / "run_summary.md"),
        "failure_examples_md": file_state(run_dir / "failure_examples.md"),
        "gate_report_md": file_state(run_dir / "gate_report.md"),
    }
    reviews = review_state(run_dir)
    failures = failure_state(run_dir)
    gate = gate_state(run_dir)
    completeness = completeness_state(run_dir)
    tool_reviews = review_state(tool_augmented_run_dir)
    tool_completeness = tool_augmented_completeness_state(tool_augmented_run_dir)
    tool_gate = tool_augmented_gate_state(tool_augmented_run_dir)
    paper_framing = paper_framing_state()
    protocol_state = protocol_current_state()
    protocol_pilot_report = protocol_pilot_report_state()
    final_roadmap = final_roadmap_state()
    submission_handoff = audit_handoff(DEFAULT_HANDOFF)

    required_docs_ready = all(doc["exists"] for doc in required_docs.values())
    minimum_inputs_ready = required_docs_ready and all(
        state["exists"] for state in run_files.values()
    ) and reviews["counts_match"] and completeness["usable_full_run"] and failures["usable_for_paper"] and gate["exists"]
    positive_claim_ready = bool(minimum_inputs_ready and gate["usable_for_positive_claim"])
    tool_augmented_claim_ready = bool(
        required_docs["tool_augmented_full_result"]["exists"]
        and required_docs["paper_draft"]["exists"]
        and tool_reviews["counts_match"]
        and tool_completeness["usable_tool_augmented_full_run"]
        and tool_gate["usable_for_tool_augmented_claim"]
    )
    negative_or_methods_draft_ready = bool(
        required_docs_ready
        and all(state["exists"] for state in pre_api_evidence.values())
        and paper_framing["passed"]
        and protocol_state["passed"]
        and protocol_pilot_report["passed"]
        and final_roadmap["passed"]
    )

    blockers: list[str] = []
    if not reviews["counts_match"]:
        blockers.append("Missing real API reviews/metrics or counts do not match.")
    if not completeness["usable_full_run"]:
        blockers.append("Missing run completeness evidence for a 60-record non-mock full run.")
    if not run_files["api_pilot_report"]["exists"]:
        blockers.append("Missing API pilot report.")
    if not failures["usable_for_paper"]:
        blockers.append("Missing non-mock failure examples.")
    if not gate["exists"]:
        blockers.append("Missing stop/continue gate report.")
    elif gate["verdict"] != "continue":
        blockers.append(f"Gate verdict is `{gate['verdict']}`, so positive claims are not ready.")
    if not paper_framing["passed"]:
        blockers.append(f"Paper framing check failed: {', '.join(paper_framing['blockers'])}.")
    if not protocol_state["passed"]:
        blockers.append(f"Protocol current-state check failed: {', '.join(protocol_state['blockers'])}.")
    if not protocol_pilot_report["passed"]:
        blockers.append(f"Protocol pilot report check failed: {', '.join(protocol_pilot_report['blockers'])}.")
    if not final_roadmap["passed"]:
        blockers.append(f"Final roadmap check failed: {', '.join(final_roadmap['blockers'])}.")
    if not submission_handoff["passed"]:
        blockers.append("Submission handoff boundary audit failed.")

    tool_augmented_blockers: list[str] = []
    if not required_docs["tool_augmented_full_result"]["exists"]:
        tool_augmented_blockers.append("Missing tracked tool-augmented full-run result document.")
    if not tool_reviews["counts_match"]:
        tool_augmented_blockers.append("Missing tool-augmented reviews/metrics or counts do not match.")
    if not tool_completeness["usable_tool_augmented_full_run"]:
        tool_augmented_blockers.append("Missing 30-record non-mock tool-augmented completeness evidence.")
    if not tool_gate["exists"]:
        tool_augmented_blockers.append("Missing tool-augmented full-run gate report.")
    elif not tool_gate["usable_for_tool_augmented_claim"]:
        tool_augmented_blockers.append("Tool-augmented gate is not usable for the conditional tool-assisted claim.")

    return {
        "full_run_dir": run_dir.as_posix(),
        "tool_augmented_run_dir": tool_augmented_run_dir.as_posix(),
        "evp7_g5": evp7,
        "required_docs_ready": required_docs_ready,
        "minimum_inputs_ready": minimum_inputs_ready,
        "positive_claim_ready": positive_claim_ready,
        "prompt_only_positive_claim_ready": positive_claim_ready,
        "tool_augmented_claim_ready": tool_augmented_claim_ready,
        "evp7_bounded_pilot_claim_ready": evp7["ready_for_bounded_pilot_claim"]
        and paper_framing["passed"]
        and protocol_state["passed"]
        and protocol_pilot_report["passed"]
        and final_roadmap["passed"],
        "current_result_claim_ready": (evp7["ready_for_bounded_pilot_claim"] or tool_augmented_claim_ready)
        and paper_framing["passed"]
        and protocol_state["passed"]
        and protocol_pilot_report["passed"]
        and final_roadmap["passed"],
        "submission_package_ready": required_docs_ready
        and (evp7["ready_for_bounded_pilot_claim"] or tool_augmented_claim_ready)
        and paper_framing["passed"]
        and protocol_state["passed"]
        and protocol_pilot_report["passed"]
        and final_roadmap["passed"]
        and submission_handoff["passed"],
        "claim_boundary": (
            "Prompt-only evidence-first remains unsupported by the old full-run gate. "
            "The old tool-augmented positive claim is limited to a conditional tool-assisted verifier. "
            "The current EVP-7 G5 result supports only bounded pilot observations about evidence-level variation."
        ),
        "negative_or_methods_draft_ready": negative_or_methods_draft_ready,
        "paper_framing": paper_framing,
        "protocol_current_state": protocol_state,
        "protocol_pilot_report": protocol_pilot_report,
        "final_roadmap": final_roadmap,
        "submission_handoff": submission_handoff,
        "required_docs": required_docs,
        "pre_api_evidence": pre_api_evidence,
        "run_files": run_files,
        "reviews": reviews,
        "completeness": completeness,
        "failures": failures,
        "gate": gate,
        "tool_augmented_reviews": tool_reviews,
        "tool_augmented_completeness": tool_completeness,
        "tool_augmented_gate": tool_gate,
        "blockers": blockers,
        "tool_augmented_blockers": tool_augmented_blockers,
        "evp7_blockers": evp7["blockers"],
    }


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# Paper Draft Readiness Audit",
        "",
        "## Summary",
        "",
        f"- full run dir: `{audit['full_run_dir']}`",
        f"- tool-augmented run dir: `{audit['tool_augmented_run_dir']}`",
        f"- required docs ready: {bool_mark(audit['required_docs_ready'])}",
        f"- minimum inputs ready: {bool_mark(audit['minimum_inputs_ready'])}",
        f"- prompt-only positive claim ready: {bool_mark(audit['prompt_only_positive_claim_ready'])}",
        f"- tool-augmented claim ready: {bool_mark(audit['tool_augmented_claim_ready'])}",
        f"- EVP-7 bounded pilot claim ready: {bool_mark(audit['evp7_bounded_pilot_claim_ready'])}",
        f"- current result claim ready: {bool_mark(audit['current_result_claim_ready'])}",
        f"- submission package ready: {bool_mark(audit['submission_package_ready'])}",
        f"- methods/negative draft ready: {bool_mark(audit['negative_or_methods_draft_ready'])}",
        f"- claim boundary: {audit['claim_boundary']}",
        "",
        "## Required Docs",
        "",
    ]
    for name, state in audit["required_docs"].items():
        lines.append(f"- `{name}`: {bool_mark(state['exists'])} (`{state['path']}`)")
    lines.extend(["", "## Paper Framing", ""])
    lines.append(f"- passed: {bool_mark(audit['paper_framing']['passed'])}")
    lines.append(f"- title: `{audit['paper_framing']['title']}`")
    for name, passed in audit["paper_framing"]["checks"].items():
        lines.append(f"- `{name}`: {bool_mark(passed)}")
    if audit["paper_framing"]["blockers"]:
        lines.append(f"- blockers: `{', '.join(audit['paper_framing']['blockers'])}`")
    lines.extend(["", "## Protocol Current State", ""])
    lines.append(f"- passed: {bool_mark(audit['protocol_current_state']['passed'])}")
    lines.append(f"- path: `{audit['protocol_current_state']['path']}`")
    for name, passed in audit["protocol_current_state"]["checks"].items():
        lines.append(f"- `{name}`: {bool_mark(passed)}")
    if audit["protocol_current_state"]["blockers"]:
        lines.append(f"- blockers: `{', '.join(audit['protocol_current_state']['blockers'])}`")
    lines.extend(["", "## Protocol Pilot Report", ""])
    lines.append(f"- passed: {bool_mark(audit['protocol_pilot_report']['passed'])}")
    lines.append(f"- path: `{audit['protocol_pilot_report']['path']}`")
    for name, passed in audit["protocol_pilot_report"]["checks"].items():
        lines.append(f"- `{name}`: {bool_mark(passed)}")
    if audit["protocol_pilot_report"]["blockers"]:
        lines.append(f"- blockers: `{', '.join(audit['protocol_pilot_report']['blockers'])}`")
    lines.extend(["", "## Final Roadmap", ""])
    lines.append(f"- passed: {bool_mark(audit['final_roadmap']['passed'])}")
    lines.append(f"- path: `{audit['final_roadmap']['path']}`")
    for name, passed in audit["final_roadmap"]["checks"].items():
        lines.append(f"- `{name}`: {bool_mark(passed)}")
    if audit["final_roadmap"]["blockers"]:
        lines.append(f"- blockers: `{', '.join(audit['final_roadmap']['blockers'])}`")
    lines.extend(["", "## Submission Handoff", ""])
    lines.append(f"- passed: {bool_mark(audit['submission_handoff']['passed'])}")
    lines.append(f"- handoff path: `{audit['submission_handoff']['handoff_path']}`")
    lines.append(f"- next decision packet exists: {bool_mark(audit['submission_handoff']['next_decision_packet_exists'])}")
    lines.append(f"- missing required snippets: {len(audit['submission_handoff']['missing_required_snippets'])}")
    lines.append(f"- forbidden snippet hits: {len(audit['submission_handoff']['forbidden_snippet_hits'])}")
    lines.extend(["", "## Pre-API Evidence", ""])
    for name, state in audit["pre_api_evidence"].items():
        lines.append(f"- `{name}`: {bool_mark(state['exists'])} (`{state['path']}`)")
    lines.extend(["", "## Full-Run Files", ""])
    for name, state in audit["run_files"].items():
        lines.append(f"- `{name}`: {bool_mark(state['exists'])} (`{state['path']}`)")
    lines.extend(
        [
            "",
            "## Reviews",
            "",
            f"- reviews count: {audit['reviews']['reviews_count']}",
            f"- metrics count: {audit['reviews']['metrics_count']}",
            f"- counts match: {bool_mark(audit['reviews']['counts_match'])}",
            "",
            "## Run Completeness",
            "",
            f"- exists: {bool_mark(audit['completeness']['exists'])}",
            f"- passed: {bool_mark(audit['completeness']['passed'])}",
            f"- expected records: {audit['completeness']['expected_records']}",
            f"- review count: {audit['completeness']['review_count']}",
            f"- mock review count: {audit['completeness']['mock_review_count']}",
            f"- usable full run: {bool_mark(audit['completeness']['usable_full_run'])}",
            "",
            "## Tool-Augmented Full Run",
            "",
            f"- reviews count: {audit['tool_augmented_reviews']['reviews_count']}",
            f"- metrics count: {audit['tool_augmented_reviews']['metrics_count']}",
            f"- counts match: {bool_mark(audit['tool_augmented_reviews']['counts_match'])}",
            f"- completeness exists: {bool_mark(audit['tool_augmented_completeness']['exists'])}",
            f"- completeness passed: {bool_mark(audit['tool_augmented_completeness']['passed'])}",
            f"- expected records: {audit['tool_augmented_completeness']['expected_records']}",
            f"- review count: {audit['tool_augmented_completeness']['review_count']}",
            f"- mock review count: {audit['tool_augmented_completeness']['mock_review_count']}",
            f"- gate exists: {bool_mark(audit['tool_augmented_gate']['exists'])}",
            f"- gate passed: {bool_mark(audit['tool_augmented_gate']['passed'])}",
            f"- usable for tool-augmented claim: {bool_mark(audit['tool_augmented_gate']['usable_for_tool_augmented_claim'])}",
            f"- metrics: `{audit['tool_augmented_gate']['metrics']}`",
            "",
            "## EVP-7 G5 Current Result",
            "",
            f"- ready for bounded pilot claim: {bool_mark(audit['evp7_g5']['ready_for_bounded_pilot_claim'])}",
            f"- summary path: `{audit['evp7_g5']['summary_path']}`",
            f"- quality audit path: `{audit['evp7_g5']['quality_audit_path']}`",
            f"- claim traceability path: `{audit['evp7_g5']['claim_traceability_path']}`",
            f"- claim traceability: `{audit['evp7_g5']['claim_traceability']}`",
            f"- utility sensitivity path: `{audit['evp7_g5']['utility_sensitivity_path']}`",
            f"- utility sensitivity: `{audit['evp7_g5']['utility_sensitivity']}`",
            f"- tool attribution path: `{audit['evp7_g5']['tool_attribution_path']}`",
            f"- tool attribution: `{audit['evp7_g5']['tool_attribution']}`",
            f"- qualitative cases path: `{audit['evp7_g5']['qualitative_cases_path']}`",
            f"- qualitative cases: `{audit['evp7_g5']['qualitative_cases']}`",
            f"- quality status: `{audit['evp7_g5']['quality_status']}`",
            f"- review count: {audit['evp7_g5']['review_count']}",
            f"- candidate count: {audit['evp7_g5']['candidate_count']}",
            f"- level counts: `{audit['evp7_g5']['level_counts']}`",
            f"- invalid output rate: {audit['evp7_g5']['invalid_output_rate']}",
            f"- raw outputs tracked: {bool_mark(audit['evp7_g5']['raw_outputs_tracked'])}",
            f"- signal status: `{audit['evp7_g5']['g5_signal_claim_status']}`",
            f"- metric groups: `{audit['evp7_g5']['metric_groups']}`",
            "",
            "## Failure Examples",
            "",
            f"- exists: {bool_mark(audit['failures']['exists'])}",
            f"- mock review count: {audit['failures']['mock_review_count']}",
            f"- bucket counts: `{audit['failures']['bucket_counts']}`",
            "",
            "## Gate",
            "",
            f"- exists: {bool_mark(audit['gate']['exists'])}",
            f"- verdict: `{audit['gate']['verdict']}`",
            f"- usable for positive claim: {bool_mark(audit['gate']['usable_for_positive_claim'])}",
            "",
            "## Blockers",
            "",
        ]
    )
    if audit["blockers"]:
        for blocker in audit["blockers"]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")
    lines.extend(["", "## Tool-Augmented Blockers", ""])
    if audit["tool_augmented_blockers"]:
        for blocker in audit["tool_augmented_blockers"]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")
    lines.extend(["", "## EVP-7 Blockers", ""])
    if audit["evp7_blockers"]:
        for blocker in audit["evp7_blockers"]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit whether the paper draft can move beyond pre-API methods.")
    parser.add_argument("--full-run-dir", default=str(DEFAULT_FULL_RUN_DIR))
    parser.add_argument("--tool-augmented-run-dir", default=str(DEFAULT_TOOL_AUGMENTED_FULL_RUN_DIR))
    parser.add_argument("--evp7-summary", default=str(DEFAULT_EVP7_SUMMARY))
    parser.add_argument("--evp7-quality-audit", default=str(DEFAULT_EVP7_QUALITY_AUDIT))
    parser.add_argument("--evp7-claim-traceability", default=str(DEFAULT_EVP7_CLAIM_TRACEABILITY))
    parser.add_argument("--evp7-utility-sensitivity", default=str(DEFAULT_EVP7_UTILITY_SENSITIVITY))
    parser.add_argument("--evp7-tool-attribution", default=str(DEFAULT_EVP7_TOOL_ATTRIBUTION))
    parser.add_argument("--evp7-qualitative-cases", default=str(DEFAULT_EVP7_QUALITATIVE_CASES))
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = build_audit(args)
    write_json(Path(args.out_json), audit)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(audit), encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
