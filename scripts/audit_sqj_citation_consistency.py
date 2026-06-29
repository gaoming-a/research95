from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_SOURCE = Path("docs/paper/sqj_submission_draft.tex")
DEFAULT_BIB = Path("docs/paper/sqj_references.bib")
DEFAULT_JSON_OUT = Path("outputs/sqj_citation_consistency/latest.json")
DEFAULT_MD_OUT = Path("docs/experiments/sqj_citation_consistency.md")

CITE_PATTERN = re.compile(r"\\cite\{([^}]+)\}")
BIB_ENTRY_PATTERN = re.compile(r"@\w+\s*\{\s*([^,\s]+)", re.IGNORECASE)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def file_state(path: Path) -> dict[str, Any]:
    return {
        "path": path.as_posix(),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
    }


def parse_cite_keys(source_text: str) -> list[str]:
    keys: list[str] = []
    for match in CITE_PATTERN.finditer(source_text):
        keys.extend(key.strip() for key in match.group(1).split(",") if key.strip())
    return keys


def parse_bib_keys(bib_text: str) -> list[str]:
    return [match.group(1).strip() for match in BIB_ENTRY_PATTERN.finditer(bib_text)]


def audit_sqj_citation_consistency(source: Path = DEFAULT_SOURCE, bib: Path = DEFAULT_BIB) -> dict[str, Any]:
    source_text = read_text(source)
    bib_text = read_text(bib)
    cite_keys = parse_cite_keys(source_text)
    bib_keys = parse_bib_keys(bib_text)
    cite_key_counts = Counter(cite_keys)
    bib_key_counts = Counter(bib_keys)
    cite_key_set = set(cite_keys)
    bib_key_set = set(bib_keys)
    missing_cite_keys = sorted(cite_key_set - bib_key_set)
    uncited_bib_keys = sorted(bib_key_set - cite_key_set)
    duplicate_bib_keys = sorted(key for key, count in bib_key_counts.items() if count > 1)
    duplicate_cite_keys = sorted(key for key, count in cite_key_counts.items() if count > 1)
    bibliography_present = r"\bibliography{sqj_references}" in source_text
    consistency_passed = bool(
        source.exists()
        and bib.exists()
        and cite_keys
        and bib_keys
        and bibliography_present
        and not missing_cite_keys
        and not uncited_bib_keys
        and not duplicate_bib_keys
    )
    return {
        "audit_id": "sqj_citation_consistency",
        "boundary": (
            "This gate checks source-level citation and BibTeX key consistency "
            "for the SQJ draft. It does not fetch references, add citations, "
            "run BibTeX, compile the PDF, or mark final freeze complete."
        ),
        "source": file_state(source),
        "bib": file_state(bib),
        "cite_keys": sorted(cite_key_set),
        "bib_keys": sorted(bib_key_set),
        "cite_key_count": len(cite_keys),
        "unique_cite_key_count": len(cite_key_set),
        "bib_entry_count": len(bib_keys),
        "unique_bib_key_count": len(bib_key_set),
        "missing_cite_keys": missing_cite_keys,
        "uncited_bib_keys": uncited_bib_keys,
        "duplicate_bib_keys": duplicate_bib_keys,
        "duplicate_cite_keys": duplicate_cite_keys,
        "bibliography_present": bibliography_present,
        "citation_consistency_passed": consistency_passed,
        "api_call_attempted": False,
        "web_lookup_attempted": False,
        "pdf_compile_attempted": False,
        "final_freeze_complete": False,
        "passed": consistency_passed,
    }


def render_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# SQJ Citation Consistency Audit",
        "",
        "## Summary",
        "",
        f"- passed: {bool_mark(audit['passed'])}",
        f"- citation consistency passed: {bool_mark(audit['citation_consistency_passed'])}",
        f"- source exists: {bool_mark(audit['source']['exists'])}",
        f"- bibliography exists: {bool_mark(audit['bib']['exists'])}",
        f"- bibliography command present: {bool_mark(audit['bibliography_present'])}",
        f"- unique cite keys: {audit['unique_cite_key_count']}",
        f"- unique BibTeX keys: {audit['unique_bib_key_count']}",
        f"- missing cite keys: {len(audit['missing_cite_keys'])}",
        f"- uncited BibTeX keys: {len(audit['uncited_bib_keys'])}",
        f"- duplicate BibTeX keys: {len(audit['duplicate_bib_keys'])}",
        f"- API call attempted: {bool_mark(audit['api_call_attempted'])}",
        f"- web lookup attempted: {bool_mark(audit['web_lookup_attempted'])}",
        f"- PDF compile attempted: {bool_mark(audit['pdf_compile_attempted'])}",
        f"- final freeze complete: {bool_mark(audit['final_freeze_complete'])}",
        "",
        "## Cite Keys",
        "",
    ]
    for key in audit["cite_keys"]:
        lines.append(f"- `{key}`")
    lines.extend(["", "## BibTeX Keys", ""])
    for key in audit["bib_keys"]:
        lines.append(f"- `{key}`")
    if audit["missing_cite_keys"]:
        lines.extend(["", "## Missing Cite Keys", ""])
        for key in audit["missing_cite_keys"]:
            lines.append(f"- `{key}`")
    if audit["uncited_bib_keys"]:
        lines.extend(["", "## Uncited BibTeX Keys", ""])
        for key in audit["uncited_bib_keys"]:
            lines.append(f"- `{key}`")
    if audit["duplicate_bib_keys"]:
        lines.extend(["", "## Duplicate BibTeX Keys", ""])
        for key in audit["duplicate_bib_keys"]:
            lines.append(f"- `{key}`")
    lines.extend(["", "## Boundary", "", audit["boundary"], ""])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit SQJ citation and BibTeX key consistency.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--bib", type=Path, default=DEFAULT_BIB)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_MD_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audit = audit_sqj_citation_consistency(args.source, args.bib)
    write_json(args.out_json, audit)
    write_text(args.out_md, render_markdown(audit))
    print(json.dumps({"out_json": args.out_json.as_posix(), "out_md": args.out_md.as_posix(), "passed": audit["passed"]}, indent=2))
    if not audit["passed"]:
        raise SystemExit(1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
