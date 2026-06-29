from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from scripts.audit_sqj_artifact_gate import audit_sqj_artifact_gate
    from scripts.audit_sqj_availability_boundary import audit_sqj_availability_boundary
    from scripts.audit_sqj_citation_consistency import audit_sqj_citation_consistency
    from scripts.audit_sqj_claim_traceability import audit_sqj_claim_traceability
    from scripts.audit_sqj_final_authorization_gate import audit_sqj_final_authorization_gate
    from scripts.audit_sqj_figure_layout_gate import audit_sqj_figure_layout_gate
    from scripts.audit_sqj_human_decision_packet import audit_sqj_human_decision_packet
    from scripts.audit_sqj_human_inputs_gate import audit_sqj_human_inputs_gate
    from scripts.audit_sqj_pdf_compile_gate import audit_sqj_pdf_compile_gate
    from scripts.audit_sqj_school_recognition_gate import audit_sqj_school_recognition_gate
    from scripts.audit_sqj_submission_checklist import DEFAULT_CHECKLIST, audit_sqj_checklist
except ModuleNotFoundError:
    from audit_sqj_artifact_gate import audit_sqj_artifact_gate
    from audit_sqj_availability_boundary import audit_sqj_availability_boundary
    from audit_sqj_citation_consistency import audit_sqj_citation_consistency
    from audit_sqj_claim_traceability import audit_sqj_claim_traceability
    from audit_sqj_final_authorization_gate import audit_sqj_final_authorization_gate
    from audit_sqj_figure_layout_gate import audit_sqj_figure_layout_gate
    from audit_sqj_human_decision_packet import audit_sqj_human_decision_packet
    from audit_sqj_human_inputs_gate import audit_sqj_human_inputs_gate
    from audit_sqj_pdf_compile_gate import audit_sqj_pdf_compile_gate
    from audit_sqj_school_recognition_gate import audit_sqj_school_recognition_gate
    from audit_sqj_submission_checklist import DEFAULT_CHECKLIST, audit_sqj_checklist


DEFAULT_READINESS_PACKET = Path("docs/artifact/sqj_final_freeze_readiness.md")

REQUIRED_FILES = {
    "readiness_packet": DEFAULT_READINESS_PACKET,
    "sqj_checklist": DEFAULT_CHECKLIST,
    "sqj_human_decision_packet": Path("docs/artifact/sqj_human_decision_packet.md"),
    "sqj_source_draft": Path("docs/paper/sqj_submission_draft.tex"),
    "sqj_references_bib": Path("docs/paper/sqj_references.bib"),
    "sqj_framing": Path("docs/paper/sqj_submission_framing.md"),
    "generated_tables_md": Path("docs/paper/generated_tables.md"),
    "generated_tables_tex": Path("docs/paper/generated_tables.tex"),
    "sqj_availability_boundary_md": Path("docs/experiments/sqj_availability_boundary.md"),
    "sqj_citation_consistency_md": Path("docs/experiments/sqj_citation_consistency.md"),
    "sqj_claim_traceability_json": Path("data/reviews/sqj_claim_traceability.json"),
    "sqj_claim_traceability_md": Path("docs/experiments/sqj_claim_traceability.md"),
    "sqj_figure_manifest": Path("docs/figures/sqj/figure_manifest.json"),
    "sqj_checklist_audit_script": Path("scripts/audit_sqj_submission_checklist.py"),
    "sqj_artifact_gate_script": Path("scripts/audit_sqj_artifact_gate.py"),
    "sqj_availability_boundary_script": Path("scripts/audit_sqj_availability_boundary.py"),
    "sqj_citation_consistency_script": Path("scripts/audit_sqj_citation_consistency.py"),
    "sqj_claim_traceability_script": Path("scripts/audit_sqj_claim_traceability.py"),
    "sqj_final_authorization_gate_script": Path("scripts/audit_sqj_final_authorization_gate.py"),
    "sqj_school_recognition_gate_script": Path("scripts/audit_sqj_school_recognition_gate.py"),
    "sqj_human_inputs_gate_script": Path("scripts/audit_sqj_human_inputs_gate.py"),
    "sqj_human_decision_packet_gate_script": Path("scripts/audit_sqj_human_decision_packet.py"),
    "sqj_pdf_compile_gate_script": Path("scripts/audit_sqj_pdf_compile_gate.py"),
    "sqj_figure_layout_gate_script": Path("scripts/audit_sqj_figure_layout_gate.py"),
    "sqj_source_generator": Path("scripts/write_sqj_latex_draft.py"),
    "sqj_figure_generator": Path("scripts/generate_sqj_figures.py"),
}

REQUIRED_SNIPPETS = [
    "Status: SQJ final-freeze readiness packet, not final freeze.",
    "This packet does not authorize submission.",
    "No model API calls are authorized.",
    "Current Ready Source Package",
    "`docs/paper/sqj_submission_draft.tex`",
    "`docs/paper/sqj_references.bib`",
    "`docs/experiments/sqj_availability_boundary.md`",
    "`docs/experiments/sqj_citation_consistency.md`",
    "`docs/figures/sqj/`",
    "`docs/artifact/sqj_submission_checklist.md`",
    "`docs/artifact/sqj_human_decision_packet.md`",
    "`data/reviews/sqj_claim_traceability.json`",
    "`docs/experiments/sqj_claim_traceability.md`",
    "`scripts/audit_sqj_submission_checklist.py`",
    "`scripts/audit_sqj_artifact_gate.py`",
    "`scripts/audit_sqj_availability_boundary.py`",
    "`scripts/audit_sqj_citation_consistency.py`",
    "`scripts/audit_sqj_claim_traceability.py`",
    "`scripts/audit_sqj_final_authorization_gate.py`",
    "`scripts/audit_sqj_school_recognition_gate.py`",
    "`scripts/audit_sqj_human_inputs_gate.py`",
    "`scripts/audit_sqj_human_decision_packet.py`",
    "`scripts/audit_sqj_pdf_compile_gate.py`",
    "`scripts/audit_sqj_figure_layout_gate.py`",
    "school/department recognition confirmation",
    "`blocked_missing_school_recognition`",
    "fresh realistic branch is a two-project source-acquisition negative result",
    "`sn-jnl.cls`",
    "`blocked_missing_sn_jnl_cls`",
    "`blocked_pending_pdf_compile`",
    "author information, funding, acknowledgements, and competing-interest",
    "`blocked_missing_human_inputs`",
    "`blocked_missing_human_decisions`",
    "final artifact package rebuild and audit",
    "`candidate_artifact_dry_run_ready`",
    "`sqj_availability_boundary`",
    "`sqj_citation_consistency`",
    "`sqj_claim_traceability`",
    "`blocked_missing_final_authorization`",
    "python scripts\\write_paper_tables.py",
    "python scripts\\generate_sqj_figures.py",
    "python scripts\\write_sqj_latex_draft.py --check",
    "python scripts\\audit_sqj_availability_boundary.py",
    "python scripts\\audit_sqj_citation_consistency.py",
    "python scripts\\audit_sqj_claim_traceability.py",
    "python scripts\\audit_sqj_submission_checklist.py",
    "python scripts\\audit_sqj_artifact_gate.py",
    "python scripts\\audit_sqj_final_authorization_gate.py",
    "python scripts\\audit_sqj_school_recognition_gate.py",
    "python scripts\\audit_sqj_human_inputs_gate.py",
    "python scripts\\audit_sqj_human_decision_packet.py",
    "python scripts\\audit_sqj_pdf_compile_gate.py",
    "python scripts\\audit_sqj_figure_layout_gate.py",
    "python scripts\\audit_sqj_final_freeze_readiness.py",
    "This is a readiness and blocker packet only.",
]

FORBIDDEN_SNIPPETS = [
    "Status: final freeze complete.",
    "This packet authorizes submission.",
    "school recognition is guaranteed.",
    "Open Access is approved.",
    "APC payment is approved.",
    "PDF compile gate has passed.",
    "sn-jnl.cls is available locally.",
    "new model API calls can run now",
    "fresh realistic branch is a three-project verifier-ready main experiment",
    "full-file generation repair demonstrates practical autonomous patch verification",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


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


def audit_sqj_final_freeze_readiness(path: Path) -> dict[str, Any]:
    packet_text = read_text(path)
    required_files = {
        name: file_state(file_path if name != "readiness_packet" else path)
        for name, file_path in REQUIRED_FILES.items()
    }
    missing_required_snippets = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in packet_text]
    forbidden_snippet_hits = [snippet for snippet in FORBIDDEN_SNIPPETS if snippet in packet_text]
    zero_byte_files = [
        name
        for name, state in required_files.items()
        if state["exists"] and int(state["size_bytes"]) <= 0
    ]
    sqj_checklist = audit_sqj_checklist(DEFAULT_CHECKLIST)
    availability_boundary = audit_sqj_availability_boundary()
    citation_consistency = audit_sqj_citation_consistency()
    claim_traceability = audit_sqj_claim_traceability()
    artifact_gate = audit_sqj_artifact_gate()
    final_authorization_gate = audit_sqj_final_authorization_gate()
    school_recognition_gate = audit_sqj_school_recognition_gate()
    human_inputs_gate = audit_sqj_human_inputs_gate()
    human_decision_packet = audit_sqj_human_decision_packet()
    pdf_compile_gate = audit_sqj_pdf_compile_gate()
    figure_layout_gate = audit_sqj_figure_layout_gate()
    external_blockers_declared = all(
        snippet in packet_text
        for snippet in [
            "school/department recognition confirmation",
            "local or CI PDF compilation after `sn-jnl.cls` is available",
            "final artifact package rebuild and audit",
            "final user authorization to submit",
            "SQJ human-decision packet",
            "current figure-layout gate status `blocked_pending_pdf_compile`",
        ]
    )
    result = {
        "readiness_packet_path": path.as_posix(),
        "readiness_packet_exists": path.exists(),
        "required_files": required_files,
        "missing_required_snippets": missing_required_snippets,
        "forbidden_snippet_hits": forbidden_snippet_hits,
        "zero_byte_files": zero_byte_files,
        "sqj_submission_checklist": sqj_checklist,
        "sqj_availability_boundary": availability_boundary,
        "sqj_citation_consistency": citation_consistency,
        "sqj_claim_traceability": claim_traceability,
        "sqj_artifact_gate": artifact_gate,
        "sqj_final_authorization_gate": final_authorization_gate,
        "sqj_school_recognition_gate": school_recognition_gate,
        "sqj_human_inputs_gate": human_inputs_gate,
        "sqj_human_decision_packet": human_decision_packet,
        "sqj_pdf_compile_gate": pdf_compile_gate,
        "sqj_figure_layout_gate": figure_layout_gate,
        "external_blockers_declared": external_blockers_declared,
        "api_call_attempted": False,
        "compile_attempted": False,
        "final_freeze_complete": False,
    }
    result["passed"] = bool(
        path.exists()
        and not missing_required_snippets
        and not forbidden_snippet_hits
        and not zero_byte_files
        and all(state["exists"] for state in required_files.values())
        and sqj_checklist["passed"]
        and availability_boundary["passed"]
        and availability_boundary["gate_status"] == "sqj_availability_boundary_ready"
        and citation_consistency["passed"]
        and claim_traceability["passed"]
        and claim_traceability["raw_output_free_check"]["passed"]
        and artifact_gate["passed"]
        and final_authorization_gate["passed"]
        and school_recognition_gate["passed"]
        and human_inputs_gate["passed"]
        and human_decision_packet["passed"]
        and pdf_compile_gate["passed"]
        and figure_layout_gate["passed"]
        and external_blockers_declared
    )
    return result


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# SQJ Final-Freeze Readiness Audit",
        "",
        "## Summary",
        "",
        f"- passed: {bool_mark(audit['passed'])}",
        f"- readiness packet exists: {bool_mark(audit['readiness_packet_exists'])}",
            f"- SQJ checklist passed: {bool_mark(audit['sqj_submission_checklist']['passed'])}",
            f"- SQJ availability boundary status: `{audit['sqj_availability_boundary']['gate_status']}`",
            f"- SQJ availability boundary passed: {bool_mark(audit['sqj_availability_boundary']['passed'])}",
            f"- SQJ citation consistency passed: {bool_mark(audit['sqj_citation_consistency']['passed'])}",
            f"- SQJ claim traceability passed: {bool_mark(audit['sqj_claim_traceability']['passed'])}",
            f"- SQJ claim traceability raw-output-free: {bool_mark(audit['sqj_claim_traceability']['raw_output_free_check']['passed'])}",
            f"- SQJ artifact gate status: `{audit['sqj_artifact_gate']['gate_status']}`",
            f"- SQJ artifact dry-run only: {bool_mark(audit['sqj_artifact_gate']['dry_run_only'])}",
            f"- SQJ final-authorization gate status: `{audit['sqj_final_authorization_gate']['gate_status']}`",
            f"- SQJ submission authorized: {bool_mark(audit['sqj_final_authorization_gate']['submission_authorized'])}",
            f"- SQJ school-recognition gate status: `{audit['sqj_school_recognition_gate']['gate_status']}`",
            f"- SQJ recognition confirmed: {bool_mark(audit['sqj_school_recognition_gate']['recognition_confirmed'])}",
            f"- SQJ human-input gate status: `{audit['sqj_human_inputs_gate']['gate_status']}`",
            f"- SQJ human inputs complete: {bool_mark(audit['sqj_human_inputs_gate']['human_inputs_complete'])}",
            f"- SQJ human-decision packet status: `{audit['sqj_human_decision_packet']['gate_status']}`",
            f"- SQJ human decisions complete: {bool_mark(audit['sqj_human_decision_packet']['human_decisions_complete'])}",
            f"- SQJ PDF compile gate status: `{audit['sqj_pdf_compile_gate']['gate_status']}`",
            f"- SQJ PDF compile passed: {bool_mark(audit['sqj_pdf_compile_gate']['pdf_compile_passed'])}",
            f"- SQJ figure-layout gate status: `{audit['sqj_figure_layout_gate']['gate_status']}`",
            f"- SQJ figure layout audit complete: {bool_mark(audit['sqj_figure_layout_gate']['figure_layout_audit_complete'])}",
            f"- external blockers declared: {bool_mark(audit['external_blockers_declared'])}",
        f"- API call attempted: {bool_mark(audit['api_call_attempted'])}",
        f"- compile attempted: {bool_mark(audit['compile_attempted'])}",
        f"- final freeze complete: {bool_mark(audit['final_freeze_complete'])}",
        f"- missing required snippets: {len(audit['missing_required_snippets'])}",
        f"- forbidden snippet hits: {len(audit['forbidden_snippet_hits'])}",
        f"- zero-byte files: {len(audit['zero_byte_files'])}",
        "",
        "## Required Files",
        "",
    ]
    for name, state in audit["required_files"].items():
        lines.append(
            f"- `{name}`: {bool_mark(state['exists'])}, "
            f"{state['size_bytes']} bytes (`{state['path']}`)"
        )
    if audit["missing_required_snippets"]:
        lines.extend(["", "## Missing Required Snippets", ""])
        for snippet in audit["missing_required_snippets"]:
            lines.append(f"- `{snippet}`")
    if audit["forbidden_snippet_hits"]:
        lines.extend(["", "## Forbidden Snippet Hits", ""])
        for snippet in audit["forbidden_snippet_hits"]:
            lines.append(f"- `{snippet}`")
    if audit["zero_byte_files"]:
        lines.extend(["", "## Zero-Byte Files", ""])
        for name in audit["zero_byte_files"]:
            lines.append(f"- `{name}`")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This audit checks whether the SQJ readiness/blocker packet is internally consistent. It does not authorize submission, call model APIs, compile the PDF, or mark final freeze complete.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit the SQJ final-freeze readiness packet.")
    parser.add_argument("--packet", default=str(DEFAULT_READINESS_PACKET))
    parser.add_argument("--out-json", default="outputs/sqj_final_freeze_readiness/latest.json")
    parser.add_argument("--out-md", default="outputs/sqj_final_freeze_readiness/latest.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = audit_sqj_final_freeze_readiness(Path(args.packet))
    write_json(Path(args.out_json), audit)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(audit), encoding="utf-8")
    print(json.dumps({"out_json": args.out_json, "out_md": args.out_md, "passed": audit["passed"]}, indent=2))
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
