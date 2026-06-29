from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from scripts.audit_sqj_pdf_compile_gate import audit_sqj_pdf_compile_gate
    from scripts.audit_sqj_submission_checklist import DEFAULT_CHECKLIST, audit_sqj_checklist
except ModuleNotFoundError:
    from audit_sqj_pdf_compile_gate import audit_sqj_pdf_compile_gate
    from audit_sqj_submission_checklist import DEFAULT_CHECKLIST, audit_sqj_checklist


DEFAULT_READINESS_PACKET = Path("docs/artifact/sqj_final_freeze_readiness.md")

REQUIRED_FILES = {
    "readiness_packet": DEFAULT_READINESS_PACKET,
    "sqj_checklist": DEFAULT_CHECKLIST,
    "sqj_source_draft": Path("docs/paper/sqj_submission_draft.tex"),
    "sqj_references_bib": Path("docs/paper/sqj_references.bib"),
    "sqj_framing": Path("docs/paper/sqj_submission_framing.md"),
    "generated_tables_md": Path("docs/paper/generated_tables.md"),
    "generated_tables_tex": Path("docs/paper/generated_tables.tex"),
    "sqj_figure_manifest": Path("docs/figures/sqj/figure_manifest.json"),
    "sqj_checklist_audit_script": Path("scripts/audit_sqj_submission_checklist.py"),
    "sqj_pdf_compile_gate_script": Path("scripts/audit_sqj_pdf_compile_gate.py"),
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
    "`docs/figures/sqj/`",
    "`docs/artifact/sqj_submission_checklist.md`",
    "`scripts/audit_sqj_submission_checklist.py`",
    "`scripts/audit_sqj_pdf_compile_gate.py`",
    "school/department recognition confirmation",
    "fresh realistic branch is a two-project source-acquisition negative result",
    "`sn-jnl.cls`",
    "`blocked_missing_sn_jnl_cls`",
    "author information, funding, acknowledgements, and competing-interest",
    "final artifact package rebuild and audit",
    "python scripts\\write_paper_tables.py",
    "python scripts\\generate_sqj_figures.py",
    "python scripts\\write_sqj_latex_draft.py --check",
    "python scripts\\audit_sqj_submission_checklist.py",
    "python scripts\\audit_sqj_pdf_compile_gate.py",
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
    pdf_compile_gate = audit_sqj_pdf_compile_gate()
    external_blockers_declared = all(
        snippet in packet_text
        for snippet in [
            "school/department recognition confirmation",
            "local or CI PDF compilation after `sn-jnl.cls` is available",
            "final artifact package rebuild and audit",
            "final user authorization to submit",
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
        "sqj_pdf_compile_gate": pdf_compile_gate,
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
        and pdf_compile_gate["passed"]
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
            f"- SQJ PDF compile gate status: `{audit['sqj_pdf_compile_gate']['gate_status']}`",
            f"- SQJ PDF compile passed: {bool_mark(audit['sqj_pdf_compile_gate']['pdf_compile_passed'])}",
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
