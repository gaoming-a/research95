from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from scripts.audit_sqj_availability_boundary import audit_sqj_availability_boundary
except ModuleNotFoundError:
    from audit_sqj_availability_boundary import audit_sqj_availability_boundary


DEFAULT_CHECKLIST = Path("docs/artifact/sqj_submission_checklist.md")
SOURCE_DRAFT = Path("docs/paper/sqj_submission_draft.tex")
BIB_FILE = Path("docs/paper/sqj_references.bib")
SOURCE_GENERATOR = Path("scripts/write_sqj_latex_draft.py")
FRAMING_PACKET = Path("docs/paper/sqj_submission_framing.md")
FINAL_FREEZE_READINESS = Path("docs/artifact/sqj_final_freeze_readiness.md")
SQJ_AVAILABILITY_BOUNDARY_MD = Path("docs/experiments/sqj_availability_boundary.md")
SQJ_TEMPLATE_FETCH_MD = Path("docs/experiments/sqj_springer_template_fetch.md")
SQJ_PDF_LAYOUT_REVIEW_MD = Path("docs/experiments/sqj_pdf_layout_review.md")
SQJ_CITATION_CONSISTENCY_MD = Path("docs/experiments/sqj_citation_consistency.md")
CLAIM_TRACEABILITY_JSON = Path("data/reviews/sqj_claim_traceability.json")
CLAIM_TRACEABILITY_MD = Path("docs/experiments/sqj_claim_traceability.md")
TABLES_MD = Path("docs/paper/generated_tables.md")
TABLES_TEX = Path("docs/paper/generated_tables.tex")
SYNTHESIS_JSON = Path("data/protocols/evp8_five_model_synthesis_v0_1.json")
COST_JSON = Path("data/reviews/evp8_cost_accounting_summary.json")
FIGURE_DIR = Path("docs/figures/sqj")
FIGURE_MANIFEST = FIGURE_DIR / "figure_manifest.json"

REQUIRED_FIGURE_IDS = [
    "sqj_fig1_evp8_protocol",
    "sqj_fig2_decision_patterns",
    "sqj_fig3_cost_boundary",
]
REQUIRED_FIGURE_FORMATS = ["pdf", "svg", "png"]

REQUIRED_SNIPPETS = [
    "Status: SQJ source package checklist, not final freeze.",
    "Software Quality Journal (SQJ)",
    "non-OA / subscription route",
    "school/department recognition confirmation",
    "this checklist does not guarantee SQJ recognition",
    "Springer Nature `sn-jnl`",
    "PDF compile gate has passed locally",
    "`compiled`",
    "`post_compile_layout_review_passed`",
    "`docs/experiments/sqj_pdf_layout_review.md`",
    "`docs/figures/sqj/sqj_fig1_evp8_protocol.pdf`",
    "`docs/figures/sqj/sqj_fig2_decision_patterns.pdf`",
    "`docs/figures/sqj/sqj_fig3_cost_boundary.pdf`",
    "`docs/paper/sqj_submission_draft.tex`",
    "`docs/paper/sqj_references.bib`",
    "`docs/experiments/sqj_citation_consistency.md`",
    "`scripts/write_sqj_latex_draft.py`",
    "`docs/paper/sqj_submission_framing.md`",
    "`docs/artifact/sqj_final_freeze_readiness.md`",
    "`docs/artifact/sqj_human_decision_packet.md`",
    "`docs/experiments/sqj_availability_boundary.md`",
    "`docs/experiments/sqj_springer_template_fetch.md`",
    "`data/reviews/sqj_claim_traceability.json`",
    "`docs/experiments/sqj_claim_traceability.md`",
    "Evidence visibility is a first-order experimental variable",
    "model-dependent and non-monotonic",
    "Blocked Kimi attempts are cost/execution-risk evidence only",
    "fresh realistic branch is a two-project source-acquisition negative result",
    "`candidate_artifact_dry_run_ready`",
    "`blocked_missing_final_authorization`",
    "`blocked_missing_school_recognition`",
    "`blocked_missing_human_inputs`",
    "`blocked_missing_human_decisions`",
    "`sqj_availability_boundary`",
    "`sqj_citation_consistency`",
    "`sqj_claim_traceability`",
    "API execution remains frozen",
    "python scripts\\audit_sqj_artifact_gate.py",
    "python scripts\\audit_sqj_availability_boundary.py",
    "python scripts\\fetch_sqj_springer_template.py",
    "python scripts\\audit_sqj_final_authorization_gate.py",
    "python scripts\\audit_sqj_school_recognition_gate.py",
    "python scripts\\audit_sqj_human_inputs_gate.py",
    "python scripts\\audit_sqj_human_decision_packet.py",
    "that LLM superiority over deterministic baselines is supported",
    "that a final evidence-level ranking has been established",
    "that the fresh realistic branch is a three-project verifier-ready main experiment",
    "python scripts\\write_sqj_latex_draft.py --check",
    "python scripts\\audit_sqj_citation_consistency.py",
    "python scripts\\audit_sqj_claim_traceability.py",
    "python scripts\\audit_sqj_submission_checklist.py",
    "python scripts\\audit_sqj_pdf_compile_gate.py",
    "python scripts\\audit_sqj_pdf_layout_review.py",
    "python scripts\\audit_sqj_figure_layout_gate.py",
    "python scripts\\audit_sqj_final_freeze_readiness.py",
    "This is not a final submission freeze.",
]

FORBIDDEN_SNIPPETS = [
    "final submission freeze is complete",
    "model API calls are authorized",
    "raw model responses are tracked",
]

SOURCE_REQUIRED_SNIPPETS = [
    r"\documentclass[pdflatex,sn-basic]{sn-jnl}",
    r"\abstract{",
    r"\keywords{",
    "Evidence visibility is a first-order experimental variable",
    "model-dependent and non-monotonic",
    "blocked Kimi attempts",
    r"\subsection{Fresh Realistic Hard-Negative Acquisition}",
    "two-project source-acquisition negative result",
    "ready_for_verifier_api=false",
    r"\input{generated_tables.tex}",
    "sqj_fig1_evp8_protocol.pdf",
    "sqj_fig2_decision_patterns.pdf",
    "sqj_fig3_cost_boundary.pdf",
    r"\bmhead{Data availability}",
    r"\bmhead{Code availability}",
    r"\bmhead{Competing interests}",
    r"\bmhead{Author contributions}",
    r"\bmhead{Funding}",
    r"\bibliography{sqj_references}",
]

SOURCE_FORBIDDEN_SNIPPETS = [
    "We prove that LLM verifiers outperform deterministic baselines",
    "LLM verifiers are superior to deterministic baselines",
    "E6 strictly improves over E4",
    "the optimal evidence level",
    "scale-generalized conclusion",
    "three-project verifier-ready main experiment",
    "practical autonomous patch verification",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def file_state(path: Path) -> dict[str, Any]:
    return {
        "path": path.as_posix(),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
    }


def figure_states() -> dict[str, dict[str, dict[str, Any]]]:
    states: dict[str, dict[str, dict[str, Any]]] = {}
    for figure_id in REQUIRED_FIGURE_IDS:
        states[figure_id] = {}
        for suffix in REQUIRED_FIGURE_FORMATS:
            states[figure_id][suffix] = file_state(FIGURE_DIR / f"{figure_id}.{suffix}")
    return states


def all_figures_ready(states: dict[str, dict[str, dict[str, Any]]]) -> bool:
    return all(
        format_state["exists"] and int(format_state["size_bytes"]) > 0
        for formats in states.values()
        for format_state in formats.values()
    )


def synthesis_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": path.as_posix(), "exists": False, "passed": False, "status": None}
    value = read_json(path)
    return {
        "path": path.as_posix(),
        "exists": True,
        "passed": value.get("synthesis_status") == "passed",
        "status": value.get("synthesis_status"),
        "api_call_attempted": value.get("api_call_attempted"),
        "raw_outputs_read": value.get("raw_outputs_read"),
    }


def cost_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": path.as_posix(), "exists": False, "passed": False, "api_freeze": None}
    value = read_json(path)
    decision = value.get("decision", {}) if isinstance(value.get("decision"), dict) else {}
    totals = value.get("totals", {}) if isinstance(value.get("totals"), dict) else {}
    return {
        "path": path.as_posix(),
        "exists": True,
        "passed": value.get("passed") is True and decision.get("api_freeze") is True,
        "api_freeze": decision.get("api_freeze"),
        "passed_result_usd_excluding_qwen": totals.get("passed_result_usd_excluding_qwen"),
        "blocked_attempt_usd": totals.get("blocked_attempt_usd"),
    }


def audit_sqj_checklist(path: Path) -> dict[str, Any]:
    checklist_text = read_text(path)
    source_text = read_text(SOURCE_DRAFT)
    missing_required_snippets = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in checklist_text]
    forbidden_snippet_hits = [snippet for snippet in FORBIDDEN_SNIPPETS if snippet in checklist_text]
    source_missing_snippets = [snippet for snippet in SOURCE_REQUIRED_SNIPPETS if snippet not in source_text]
    source_forbidden_hits = [snippet for snippet in SOURCE_FORBIDDEN_SNIPPETS if snippet in source_text]
    figures = figure_states()
    availability_boundary = audit_sqj_availability_boundary()
    synthesis = synthesis_state(SYNTHESIS_JSON)
    cost = cost_state(COST_JSON)
    required_files = {
        "checklist": file_state(path),
        "source_draft": file_state(SOURCE_DRAFT),
        "bib_file": file_state(BIB_FILE),
        "source_generator": file_state(SOURCE_GENERATOR),
        "framing_packet": file_state(FRAMING_PACKET),
        "final_freeze_readiness": file_state(FINAL_FREEZE_READINESS),
        "availability_boundary_md": file_state(SQJ_AVAILABILITY_BOUNDARY_MD),
        "springer_template_fetch_md": file_state(SQJ_TEMPLATE_FETCH_MD),
        "pdf_layout_review_md": file_state(SQJ_PDF_LAYOUT_REVIEW_MD),
        "citation_consistency_md": file_state(SQJ_CITATION_CONSISTENCY_MD),
        "claim_traceability_json": file_state(CLAIM_TRACEABILITY_JSON),
        "claim_traceability_md": file_state(CLAIM_TRACEABILITY_MD),
        "tables_md": file_state(TABLES_MD),
        "tables_tex": file_state(TABLES_TEX),
        "figure_manifest": file_state(FIGURE_MANIFEST),
    }
    result = {
        "checklist_path": path.as_posix(),
        "checklist_exists": path.exists(),
        "missing_required_snippets": missing_required_snippets,
        "forbidden_snippet_hits": forbidden_snippet_hits,
        "source_missing_snippets": source_missing_snippets,
        "source_forbidden_hits": source_forbidden_hits,
        "required_files": required_files,
        "figures": figures,
        "figures_complete": all_figures_ready(figures),
        "availability_boundary": availability_boundary,
        "synthesis": synthesis,
        "cost_accounting": cost,
        "compile_gate": "compiled_local_template_cache",
        "api_call_attempted": False,
    }
    result["passed"] = bool(
        path.exists()
        and not missing_required_snippets
        and not forbidden_snippet_hits
        and SOURCE_DRAFT.exists()
        and not source_missing_snippets
        and not source_forbidden_hits
        and all(state["exists"] for state in required_files.values())
        and result["figures_complete"]
        and availability_boundary["passed"]
        and availability_boundary["gate_status"] == "sqj_availability_boundary_ready"
        and synthesis["passed"]
        and synthesis.get("api_call_attempted") is False
        and synthesis.get("raw_outputs_read") is False
        and cost["passed"]
    )
    return result


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# SQJ Submission Checklist Audit",
        "",
        "## Summary",
        "",
        f"- passed: {bool_mark(audit['passed'])}",
        f"- checklist exists: {bool_mark(audit['checklist_exists'])}",
        f"- figures complete: {bool_mark(audit['figures_complete'])}",
        f"- availability boundary passed: {bool_mark(audit['availability_boundary']['passed'])}",
        f"- availability boundary status: `{audit['availability_boundary']['gate_status']}`",
        f"- synthesis passed: {bool_mark(audit['synthesis']['passed'])}",
        f"- cost accounting passed: {bool_mark(audit['cost_accounting']['passed'])}",
        f"- compile gate: `{audit['compile_gate']}`",
        f"- API call attempted: {bool_mark(audit['api_call_attempted'])}",
        f"- missing required snippets: {len(audit['missing_required_snippets'])}",
        f"- forbidden snippet hits: {len(audit['forbidden_snippet_hits'])}",
        f"- source missing snippets: {len(audit['source_missing_snippets'])}",
        f"- source forbidden hits: {len(audit['source_forbidden_hits'])}",
        "",
        "## Required Files",
        "",
    ]
    for name, state in audit["required_files"].items():
        lines.append(f"- `{name}`: {bool_mark(state['exists'])} (`{state['path']}`)")
    lines.extend(["", "## Figures", ""])
    for figure_id, formats in audit["figures"].items():
        status = ", ".join(f"{suffix}={bool_mark(state['exists'])}" for suffix, state in formats.items())
        lines.append(f"- `{figure_id}`: {status}")
    if audit["missing_required_snippets"]:
        lines.extend(["", "## Missing Required Snippets", ""])
        for snippet in audit["missing_required_snippets"]:
            lines.append(f"- `{snippet}`")
    if audit["forbidden_snippet_hits"]:
        lines.extend(["", "## Forbidden Snippet Hits", ""])
        for snippet in audit["forbidden_snippet_hits"]:
            lines.append(f"- `{snippet}`")
    if audit["source_missing_snippets"]:
        lines.extend(["", "## Source Missing Snippets", ""])
        for snippet in audit["source_missing_snippets"]:
            lines.append(f"- `{snippet}`")
    if audit["source_forbidden_hits"]:
        lines.extend(["", "## Source Forbidden Hits", ""])
        for snippet in audit["source_forbidden_hits"]:
            lines.append(f"- `{snippet}`")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This audit validates the tracked SQJ source-package checklist. It does not call model APIs, compile the PDF, download Springer template files, or mark the package as a final submission freeze.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit the SQJ source-package submission checklist.")
    parser.add_argument("--checklist", default=str(DEFAULT_CHECKLIST))
    parser.add_argument("--out-json", default="outputs/sqj_submission_checklist_audit/latest.json")
    parser.add_argument("--out-md", default="outputs/sqj_submission_checklist_audit/latest.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = audit_sqj_checklist(Path(args.checklist))
    write_json(Path(args.out_json), audit)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(audit), encoding="utf-8")
    print(json.dumps({"out_json": args.out_json, "out_md": args.out_md, "passed": audit["passed"]}, indent=2))
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
