"""Generate an APSEC-oriented IEEEtran draft package from the Markdown rewrite.

The conversion is intentionally conservative: it preserves the current claims,
turns citation keys into BibTeX-backed IEEE citations, converts Markdown tables
into LaTeX tables, and writes a page-budget audit. It does not claim that the
resulting source is a final submission PDF.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MD_IN = REPO_ROOT / "docs" / "paper" / "apsec_technical_track_rewrite_v0_1.md"
DEFAULT_CLAIM_MAP = REPO_ROOT / "data" / "reviews" / "final_manuscript_claim_map_v0_1.json"
DEFAULT_TEX_OUT = REPO_ROOT / "docs" / "paper" / "apsec_ieeetran_draft.tex"
DEFAULT_BIB_OUT = REPO_ROOT / "docs" / "paper" / "apsec_references.bib"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "reviews" / "apsec_page_budget_audit_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "paper" / "apsec_page_budget_audit_v0_1.md"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def latex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def restore_latex_commands(text: str) -> str:
    text = re.sub(r"\\textbackslash\{\}\s*cite\\\{([^}]*)\\\}", r"\\cite{\1}", text)
    text = re.sub(
        r"\\cite\{([^}]*)\}",
        lambda match: r"\cite{" + match.group(1).replace(r"\_", "_") + "}",
        text,
    )
    text = text.replace(r"\textbackslash{}%", r"\%")
    return text


def convert_citations(text: str, citation_keys: set[str]) -> str:
    def repl(match: re.Match[str]) -> str:
        body = match.group(1)
        parts = [part.strip() for part in body.split(";")]
        if parts and all(part in citation_keys for part in parts):
            return r"\cite{" + ",".join(parts) + "}"
        return match.group(0)

    return re.sub(r"\[([A-Za-z0-9_;,\-\s]+)\]", repl, text)


def split_table_row(line: str) -> list[str]:
    stripped = line.strip().strip("|")
    return [cell.strip() for cell in stripped.split("|")]


def is_separator_row(cells: list[str]) -> bool:
    return all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def table_to_latex(lines: list[str], table_index: int) -> str:
    rows = [split_table_row(line) for line in lines if line.strip().startswith("|")]
    if len(rows) < 2:
        return "\n".join(latex_escape(line) for line in lines)
    header = rows[0]
    data_rows = rows[2:] if is_separator_row(rows[1]) else rows[1:]
    col_spec = "l" + "X" * max(len(header) - 1, 0)

    def row(cells: list[str]) -> str:
        padded = cells + [""] * (len(header) - len(cells))
        return " & ".join(latex_escape(cell) for cell in padded[: len(header)]) + r" \\"

    latex_lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\scriptsize",
        rf"\caption{{Converted APSEC draft table {table_index}.}}",
        rf"\label{{tab:apsec-converted-{table_index}}}",
        rf"\begin{{tabularx}}{{\textwidth}}{{{col_spec}}}",
        r"\toprule",
        row(header),
        r"\midrule",
    ]
    latex_lines.extend(row(data_row) for data_row in data_rows)
    latex_lines.extend([r"\bottomrule", r"\end{tabularx}", r"\end{table*}"])
    return "\n".join(latex_lines)


def convert_inline_markdown(text: str) -> str:
    placeholders: list[str] = []

    def protect(value: str) -> str:
        token = f"@@LATEX_PLACEHOLDER_{len(placeholders)}@@"
        placeholders.append(value)
        return token

    text = re.sub(
        r"`([^`]+)`",
        lambda m: protect(r"\texttt{" + latex_escape(m.group(1)) + "}"),
        text,
    )
    text = re.sub(
        r"\*\*([^*]+)\*\*",
        lambda m: protect(r"\textbf{" + latex_escape(m.group(1)) + "}"),
        text,
    )
    escaped = restore_latex_commands(latex_escape(text))
    for index, value in enumerate(placeholders):
        escaped = escaped.replace(f"@@LATEX\_PLACEHOLDER\_{index}@@", value)
    return escaped


def figure_to_latex(line: str, figure_index: int) -> str | None:
    match = re.match(r"!\[(.*?)\]\((.*?)\)", line.strip())
    if not match:
        return None
    caption = latex_escape(match.group(1).strip() or f"APSEC figure {figure_index}")
    path = match.group(2).strip()
    return "\n".join(
        [
            r"\begin{figure}[t]",
            r"\centering",
            rf"\includegraphics[width=\columnwidth]{{{path}}}",
            rf"\caption{{{caption}}}",
            rf"\label{{fig:apsec-{figure_index}}}",
            r"\end{figure}",
        ]
    )


def markdown_to_latex(markdown: str, citation_keys: set[str]) -> tuple[str, dict[str, int]]:
    markdown = convert_citations(markdown, citation_keys)
    lines = markdown.splitlines()
    output: list[str] = []
    table_index = 0
    figure_index = 0
    i = 0
    in_abstract = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("Draft status:") or stripped.startswith("Target format note:"):
            i += 1
            continue

        if stripped.startswith("|"):
            table_lines: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            table_index += 1
            output.append(table_to_latex(table_lines, table_index))
            continue

        figure = figure_to_latex(stripped, figure_index + 1)
        if figure:
            figure_index += 1
            output.append(figure)
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i < len(lines) and re.match(r"\*\*Figure \d+\.", lines[i].strip()):
                i += 1
            continue

        if stripped == "## Abstract":
            output.append(r"\begin{abstract}")
            in_abstract = True
            i += 1
            continue

        if stripped.startswith("## ") and in_abstract:
            output.append(r"\end{abstract}")
            in_abstract = False

        if stripped.startswith("# "):
            i += 1
            continue
        if stripped.startswith("## "):
            title = re.sub(r"^\d+\.\s*", "", stripped[3:].strip())
            output.append(rf"\section{{{latex_escape(title)}}}")
        elif stripped.startswith("### "):
            title = re.sub(r"^\d+\.\d+\s*", "", stripped[4:].strip())
            output.append(rf"\subsection{{{latex_escape(title)}}}")
        elif stripped.startswith("- "):
            bullet_lines = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                bullet_lines.append(r"\item " + convert_inline_markdown(lines[i].strip()[2:]))
                i += 1
            output.append(r"\begin{itemize}")
            output.extend(bullet_lines)
            output.append(r"\end{itemize}")
            continue
        elif not stripped:
            output.append("")
        else:
            output.append(convert_inline_markdown(stripped))
        i += 1

    if in_abstract:
        output.append(r"\end{abstract}")

    stats = {
        "converted_table_count": table_index,
        "converted_figure_count": figure_index,
    }
    return "\n".join(output), stats


def bibtex_entry(record: dict[str, str]) -> str:
    key = record["key"]
    reference = record["reference"]
    title_match = re.search(r'"([^"]+)"', reference)
    title = title_match.group(1) if title_match else reference.split(".")[0]
    author = reference[: title_match.start()].strip().rstrip(".") if title_match else "Unknown"
    if author.endswith(" et al"):
        author = author[:-6] + " and others"
    author = author.replace(", and ", " and ").replace(", ", " and ")
    year_match = re.search(r"\b(19|20)\d{2}\b", reference)
    year = year_match.group(0) if year_match else "n.d."
    doi_match = re.search(r"DOI:\s*([^\s.]+(?:\.[^\s.]+)*)", reference)
    doi_line = f"  doi = {{{bibtex_escape(doi_match.group(1).rstrip('.'))}}},\n" if doi_match else ""
    venue = ""
    if title_match:
        after_title = reference[title_match.end() :].strip().lstrip(".").strip()
        venue = re.sub(r"DOI:\s*.*$", "", after_title).strip().rstrip(".")
    howpublished_line = f"  howpublished = {{{bibtex_escape(venue)}}},\n" if venue else ""
    return (
        f"@misc{{{key},\n"
        f"  author = {{{bibtex_escape(author)}}},\n"
        f"  title = {{{bibtex_escape(title)}}},\n"
        f"{howpublished_line}"
        f"  year = {{{bibtex_escape(year)}}},\n"
        f"{doi_line}"
        f"}}\n"
    )


def bibtex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
    }
    return "".join(replacements.get(char, char) for char in value)


def build_tex(body: str) -> str:
    return "\n".join(
        [
            r"\documentclass[conference]{IEEEtran}",
            "",
            r"\usepackage{booktabs}",
            r"\usepackage{graphicx}",
            r"\usepackage{tabularx}",
            r"\usepackage{url}",
            r"\usepackage[hidelinks]{hyperref}",
            "",
            r"\title{Evidence Visibility Shapes Risk Behavior in a Controlled LLM Patch-Verifier Study}",
            r"\author{\IEEEauthorblockN{Anonymous Authors}\IEEEauthorblockA{Anonymous Institution}}",
            "",
            r"\begin{document}",
            r"\maketitle",
            "",
            body,
            "",
            r"\bibliographystyle{IEEEtran}",
            r"\bibliography{apsec_references}",
            r"\end{document}",
            "",
        ]
    )


def word_count(markdown: str) -> int:
    cleaned = re.sub(r"```.*?```", " ", markdown, flags=re.DOTALL)
    cleaned = re.sub(r"\|.*\|", " ", cleaned)
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9\-_/]*", cleaned))


def build_audit(
    markdown: str,
    tex_text: str,
    bib_text: str,
    stats: dict[str, int],
    reference_count: int,
) -> dict[str, Any]:
    words = word_count(markdown)
    estimated_text_pages = words / 850.0
    float_pages = (stats["converted_table_count"] * 0.22) + (stats["converted_figure_count"] * 0.28)
    reference_pages = max(reference_count / 18.0, 0.5)
    estimated_pages = estimated_text_pages + float_pages + reference_pages
    compile_summary = read_compile_summary()
    checks = [
        {
            "check": "ieeetran_source_generated",
            "passed": r"\documentclass[conference]{IEEEtran}" in tex_text,
        },
        {
            "check": "bibtex_generated",
            "passed": reference_count > 0 and "@misc{" in bib_text,
        },
        {
            "check": "citation_keys_converted_to_cite_commands",
            "passed": r"\cite{" in tex_text and "Reference Support Records" not in tex_text,
        },
        {
            "check": "page_budget_estimate_within_apsec_technical_limit",
            "passed": estimated_pages <= 10.0,
        },
        {
            "check": "final_pdf_not_claimed",
            "passed": True,
        },
    ]
    return {
        "artifact_id": "apsec_page_budget_audit_v0_1",
        "date": "2026-07-06",
        "status": "passed" if all(check["passed"] for check in checks) else "needs_revision",
        "target": {
            "format": "anonymous IEEEtran conference draft",
            "assumed_apsec_technical_page_limit": 10,
            "note": "Estimate only; final status requires local LaTeX compilation and visual page inspection.",
        },
        "counts": {
            "word_count_excluding_tables": words,
            "converted_table_count": stats["converted_table_count"],
            "converted_figure_count": stats["converted_figure_count"],
            "reference_count": reference_count,
            "estimated_pages": round(estimated_pages, 2),
            "compiled_pdf_pages": compile_summary["compiled_pdf_pages"],
        },
        "compile_summary": compile_summary,
        "checks": checks,
        "outputs": {
            "tex": rel(DEFAULT_TEX_OUT),
            "bib": rel(DEFAULT_BIB_OUT),
            "audit_json": rel(DEFAULT_JSON_OUT),
            "audit_md": rel(DEFAULT_MD_OUT),
        },
        "remaining_formatting_risks": [
            "Converted table captions are mechanical and should be manually shortened before submission.",
            "Compiled PDF still has table-width overfull/underfull warnings that need manual layout repair.",
            "Final double-blind compliance still requires visual inspection.",
            "BibTeX entries compile but should be normalized to venue-quality fields.",
            "The current package is a draft source conversion, not a submitted or camera-ready PDF.",
        ],
    }


def read_compile_summary() -> dict[str, Any]:
    log_path = DEFAULT_TEX_OUT.with_suffix(".log")
    pdf_path = DEFAULT_TEX_OUT.with_suffix(".pdf")
    summary: dict[str, Any] = {
        "compiled_pdf_present": pdf_path.exists(),
        "compiled_pdf_pages": None,
        "log_present": log_path.exists(),
        "undefined_references_in_latest_log": None,
        "overfull_hbox_count_in_latest_log": None,
        "underfull_hbox_count_in_latest_log": None,
    }
    if not log_path.exists():
        return summary
    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    page_match = re.search(r"Output written on .*?\((\d+) pages?,", log_text)
    if page_match:
        summary["compiled_pdf_pages"] = int(page_match.group(1))
    summary["undefined_references_in_latest_log"] = "undefined references" in log_text.lower()
    summary["overfull_hbox_count_in_latest_log"] = log_text.count("Overfull \\hbox")
    summary["underfull_hbox_count_in_latest_log"] = log_text.count("Underfull \\hbox")
    return summary


def write_audit_md(audit: dict[str, Any], path: Path) -> None:
    counts = audit["counts"]
    lines = [
        "# APSEC IEEEtran and page-budget audit",
        "",
        f"Status: `{audit['status']}`",
        "",
        "## Counts",
        "",
        "| item | value |",
        "| --- | ---: |",
        f"| word count excluding tables | {counts['word_count_excluding_tables']} |",
        f"| converted tables | {counts['converted_table_count']} |",
        f"| converted figures | {counts['converted_figure_count']} |",
        f"| references | {counts['reference_count']} |",
        f"| estimated pages | {counts['estimated_pages']} |",
        f"| compiled PDF pages | {counts['compiled_pdf_pages'] or 'n/a'} |",
        "",
        "## Compile Summary",
        "",
        f"- compiled PDF present: `{str(audit['compile_summary']['compiled_pdf_present']).lower()}`",
        f"- undefined references in latest log: `{audit['compile_summary']['undefined_references_in_latest_log']}`",
        f"- overfull hbox count in latest log: `{audit['compile_summary']['overfull_hbox_count_in_latest_log']}`",
        f"- underfull hbox count in latest log: `{audit['compile_summary']['underfull_hbox_count_in_latest_log']}`",
        "",
        "## Checks",
        "",
        "| check | passed |",
        "| --- | --- |",
    ]
    lines.extend(f"| {check['check']} | {str(check['passed']).lower()} |" for check in audit["checks"])
    lines.extend(["", "## Remaining Formatting Risks", ""])
    lines.extend(f"- {risk}" for risk in audit["remaining_formatting_risks"])
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--md-in", type=Path, default=DEFAULT_MD_IN)
    parser.add_argument("--claim-map", type=Path, default=DEFAULT_CLAIM_MAP)
    parser.add_argument("--tex-out", type=Path, default=DEFAULT_TEX_OUT)
    parser.add_argument("--bib-out", type=Path, default=DEFAULT_BIB_OUT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    markdown = args.md_in.read_text(encoding="utf-8")
    claim_map = read_json(args.claim_map)
    references = claim_map["reference_records"]
    citation_keys = {record["key"] for record in references}
    body, stats = markdown_to_latex(markdown, citation_keys)
    tex_text = build_tex(body)
    bib_text = "\n\n".join(bibtex_entry(record).rstrip() for record in references) + "\n"
    audit = build_audit(markdown, tex_text, bib_text, stats, len(references))
    json_text = json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n"

    existing = {
        "tex": args.tex_out.read_text(encoding="utf-8") if args.tex_out.exists() else None,
        "bib": args.bib_out.read_text(encoding="utf-8") if args.bib_out.exists() else None,
        "json": args.json_out.read_text(encoding="utf-8") if args.json_out.exists() else None,
        "md": args.md_out.read_text(encoding="utf-8") if args.md_out.exists() else None,
    }

    args.tex_out.parent.mkdir(parents=True, exist_ok=True)
    args.bib_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.tex_out.write_text(tex_text, encoding="utf-8")
    args.bib_out.write_text(bib_text, encoding="utf-8")
    args.json_out.write_text(json_text, encoding="utf-8")
    write_audit_md(audit, args.md_out)

    if args.check:
        if existing["tex"] is not None and existing["tex"] != tex_text:
            raise SystemExit(f"{rel(args.tex_out)} is not current")
        if existing["bib"] is not None and existing["bib"] != bib_text:
            raise SystemExit(f"{rel(args.bib_out)} is not current")
        if existing["json"] is not None and existing["json"] != json_text:
            raise SystemExit(f"{rel(args.json_out)} is not current")
        current_md = args.md_out.read_text(encoding="utf-8")
        if existing["md"] is not None and existing["md"] != current_md:
            raise SystemExit(f"{rel(args.md_out)} is not current")
        if any(value is None for value in existing.values()):
            raise SystemExit("APSEC IEEEtran package outputs were missing before --check")
        if audit["status"] != "passed":
            raise SystemExit(f"APSEC IEEEtran package audit status is {audit['status']}")
        print("APSEC IEEEtran package outputs are current")
    else:
        print(f"wrote {rel(args.tex_out)}")
        print(f"wrote {rel(args.bib_out)}")
        print(f"wrote {rel(args.json_out)}")
        print(f"wrote {rel(args.md_out)}")


if __name__ == "__main__":
    main()
