from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from scripts.audit_sqj_pdf_compile_gate import audit_sqj_pdf_compile_gate
    from scripts.audit_sqj_pdf_layout_review import audit_sqj_pdf_layout_review
except ModuleNotFoundError:
    from audit_sqj_pdf_compile_gate import audit_sqj_pdf_compile_gate
    from audit_sqj_pdf_layout_review import audit_sqj_pdf_layout_review


SOURCE_DRAFT = Path("docs/paper/sqj_submission_draft.tex")
FIGURE_DIR = Path("docs/figures/sqj")
REQUIRED_FORMATS = ["pdf", "svg", "png"]
REQUIRED_FIGURES = [
    {
        "id": "sqj_fig1_evp8_protocol",
        "label": "fig:sqj-evp8-protocol",
        "caption_snippet": "EVP-8 hidden-evaluator study design",
    },
    {
        "id": "sqj_fig2_decision_patterns",
        "label": "fig:sqj-decision-patterns",
        "caption_snippet": "Five-model decision patterns",
    },
    {
        "id": "sqj_fig3_cost_boundary",
        "label": "fig:sqj-cost-boundary",
        "caption_snippet": "Cost-observability and result-validity boundary",
    },
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


def figure_state(figure: dict[str, str], source_text: str) -> dict[str, Any]:
    figure_id = figure["id"]
    formats = {
        suffix: file_state(FIGURE_DIR / f"{figure_id}.{suffix}")
        for suffix in REQUIRED_FORMATS
    }
    include_path = f"docs/figures/sqj/{figure_id}.pdf"
    return {
        "id": figure_id,
        "formats": formats,
        "all_formats_present": all(
            state["exists"] and int(state["size_bytes"]) > 0
            for state in formats.values()
        ),
        "includegraphics_present": include_path in source_text,
        "caption_present": figure["caption_snippet"] in source_text,
        "label_present": rf"\label{{{figure['label']}}}" in source_text,
        "expected_includegraphics_path": include_path,
        "expected_caption_snippet": figure["caption_snippet"],
        "expected_label": figure["label"],
    }


def audit_sqj_figure_layout_gate(source: Path = SOURCE_DRAFT) -> dict[str, Any]:
    source_text = read_text(source)
    figures = [figure_state(figure, source_text) for figure in REQUIRED_FIGURES]
    missing_or_incomplete = [
        state["id"]
        for state in figures
        if not (
            state["all_formats_present"]
            and state["includegraphics_present"]
            and state["caption_present"]
            and state["label_present"]
        )
    ]
    pdf_compile_gate = audit_sqj_pdf_compile_gate()
    pdf_layout_review = audit_sqj_pdf_layout_review() if pdf_compile_gate["pdf_compile_passed"] else None
    figure_source_ready = bool(source.exists() and not missing_or_incomplete)

    if not source.exists():
        gate_status = "failed_missing_source"
        passed = False
    elif missing_or_incomplete:
        gate_status = "failed_missing_figure_source_or_assets"
        passed = False
    elif not pdf_compile_gate["pdf_compile_passed"]:
        gate_status = "blocked_pending_pdf_compile"
        passed = True
    elif not pdf_layout_review or not pdf_layout_review["passed"]:
        gate_status = "failed_post_compile_layout_review"
        passed = False
    else:
        gate_status = "post_compile_layout_review_passed"
        passed = True

    return {
        "audit_id": "sqj_figure_layout_gate",
        "boundary": (
            "This gate verifies SQJ figure assets and LaTeX figure references at "
            "source level. It does not compile the PDF or complete the visual "
            "layout review itself; after the PDF compile gate passes, it delegates "
            "the compiled-PDF layout and reference checks to sqj_pdf_layout_review."
        ),
        "source": source.as_posix(),
        "source_exists": source.exists(),
        "figures": figures,
        "missing_or_incomplete_figures": missing_or_incomplete,
        "figure_source_ready": figure_source_ready,
        "pdf_compile_gate_status": pdf_compile_gate["gate_status"],
        "pdf_compile_passed": pdf_compile_gate["pdf_compile_passed"],
        "pdf_layout_review": pdf_layout_review,
        "figure_layout_audit_complete": gate_status == "post_compile_layout_review_passed",
        "api_call_attempted": False,
        "compile_attempted": False,
        "final_freeze_complete": False,
        "gate_status": gate_status,
        "passed": passed,
    }


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# SQJ Figure Layout Gate",
        "",
        "## Summary",
        "",
        f"- passed: {bool_mark(audit['passed'])}",
        f"- gate status: `{audit['gate_status']}`",
        f"- source exists: {bool_mark(audit['source_exists'])}",
        f"- figure source ready: {bool_mark(audit['figure_source_ready'])}",
        f"- PDF compile gate status: `{audit['pdf_compile_gate_status']}`",
        f"- PDF compile passed: {bool_mark(audit['pdf_compile_passed'])}",
        f"- PDF layout review passed: {bool_mark(audit['pdf_layout_review'] and audit['pdf_layout_review']['passed'])}",
        f"- figure layout audit complete: {bool_mark(audit['figure_layout_audit_complete'])}",
        f"- API call attempted: {bool_mark(audit['api_call_attempted'])}",
        f"- compile attempted: {bool_mark(audit['compile_attempted'])}",
        f"- final freeze complete: {bool_mark(audit['final_freeze_complete'])}",
        f"- missing or incomplete figures: {len(audit['missing_or_incomplete_figures'])}",
        "",
        "## Figures",
        "",
    ]
    for figure in audit["figures"]:
        format_status = ", ".join(
            f"{suffix}={bool_mark(state['exists'] and int(state['size_bytes']) > 0)}"
            for suffix, state in figure["formats"].items()
        )
        lines.append(
            f"- `{figure['id']}`: {format_status}; "
            f"includegraphics={bool_mark(figure['includegraphics_present'])}; "
            f"caption={bool_mark(figure['caption_present'])}; "
            f"label={bool_mark(figure['label_present'])}"
        )
    lines.extend(["", "## Boundary", "", audit["boundary"], ""])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit the SQJ source-level figure layout gate.")
    parser.add_argument("--source", default=str(SOURCE_DRAFT))
    parser.add_argument("--out-json", default="outputs/sqj_figure_layout_gate/latest.json")
    parser.add_argument("--out-md", default="outputs/sqj_figure_layout_gate/latest.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = audit_sqj_figure_layout_gate(Path(args.source))
    write_json(Path(args.out_json), audit)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(audit), encoding="utf-8")
    print(json.dumps({"out_json": args.out_json, "out_md": args.out_md, "passed": audit["passed"], "gate_status": audit["gate_status"]}, indent=2))
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
