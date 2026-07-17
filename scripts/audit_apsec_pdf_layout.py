# ruff: noqa: E402
"""Audit the compiled APSEC IEEEtran PDF rendering and submission boundaries."""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/audit_apsec_pdf_layout.py")

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PDF = REPO_ROOT / "docs" / "paper" / "apsec_ieeetran_draft.pdf"
DEFAULT_TEX = REPO_ROOT / "docs" / "paper" / "apsec_ieeetran_draft.tex"
DEFAULT_RENDER_DIR = REPO_ROOT / "tmp" / "pdfs" / "apsec_ieeetran_layout_audit"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "reviews" / "apsec_pdf_layout_audit_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "paper" / "apsec_pdf_layout_audit_v0_1.md"

FORBIDDEN_CURRENT_WORDING = [
    "source-acquisition boundary",
    "did not pass its readiness gate",
    "failed the predeclared",
    "Reference Support Records",
]


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def find_executable(name: str) -> str | None:
    direct = shutil.which(name)
    if direct and direct.lower().endswith(".exe"):
        return direct
    where = subprocess.run(["where.exe", name], text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for line in where.stdout.splitlines():
        candidate = line.strip()
        if candidate.lower().endswith(".exe"):
            return candidate
    return direct


def run(command: list[str]) -> dict[str, Any]:
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    return {
        "command": " ".join(command[:1] + command[1:]),
        "exit_code": result.returncode,
        "stdout": result.stdout,
    }


def pdf_page_count(pdfinfo_text: str) -> int | None:
    for line in pdfinfo_text.splitlines():
        if line.startswith("Pages:"):
            try:
                return int(line.split(":", 1)[1].strip())
            except ValueError:
                return None
    return None


def render_pdf(pdf: Path, render_dir: Path) -> dict[str, Any]:
    render_dir.mkdir(parents=True, exist_ok=True)
    for old in render_dir.glob("page-*.png"):
        old.unlink()
    pdftoppm = find_executable("pdftoppm")
    if not pdftoppm:
        return {"render_attempted": False, "render_exit_code": None, "rendered_pages": []}
    prefix = render_dir / "page"
    result = run([pdftoppm, "-png", "-r", "90", str(pdf), str(prefix)])
    pages = sorted(render_dir.glob("page-*.png"))
    return {
        "render_attempted": True,
        "render_exit_code": result["exit_code"],
        "rendered_pages": [rel(path) for path in pages],
        "rendered_page_count": len(pages),
        "render_tool": Path(pdftoppm).name,
    }


def image_nonwhite_fraction(path: Path) -> float:
    image = Image.open(path).convert("L")
    histogram = image.histogram()
    nonwhite = sum(histogram[:245])
    total = sum(histogram)
    return round(nonwhite / max(total, 1), 6)


def build_audit(pdf: Path, tex: Path, render_dir: Path) -> dict[str, Any]:
    pdfinfo = find_executable("pdfinfo")
    pdfinfo_result = run([pdfinfo, str(pdf)]) if pdfinfo else {"exit_code": None, "stdout": ""}
    pages = pdf_page_count(pdfinfo_result["stdout"])
    render = render_pdf(pdf, render_dir)
    rendered_paths = [REPO_ROOT / path for path in render.get("rendered_pages", [])]
    page_density = {
        rel(path): image_nonwhite_fraction(path)
        for path in rendered_paths
        if path.exists()
    }
    tex_text = tex.read_text(encoding="utf-8") if tex.exists() else ""
    forbidden_hits = [wording for wording in FORBIDDEN_CURRENT_WORDING if wording in tex_text]
    checks = [
        {"check": "compiled_pdf_exists", "passed": pdf.exists(), "detail": rel(pdf)},
        {"check": "pdfinfo_pages_within_apsec_limit", "passed": pages is not None and pages <= 10, "detail": pages},
        {
            "check": "rendered_page_count_matches_pdfinfo",
            "passed": render.get("rendered_page_count") == pages,
            "detail": {"pdfinfo_pages": pages, "rendered_pages": render.get("rendered_page_count")},
        },
        {
            "check": "rendered_pages_nonblank",
            "passed": bool(page_density) and all(value > 0.01 for value in page_density.values()),
            "detail": page_density,
        },
        {
            "check": "source_author_block_anonymous",
            "passed": "Anonymous Authors" in tex_text and "Anonymous Institution" in tex_text,
            "detail": "author block",
        },
        {"check": "old_apsec_wording_absent", "passed": not forbidden_hits, "detail": forbidden_hits},
    ]
    return {
        "audit_id": "apsec_pdf_layout_audit_v0_1",
        "status": "passed" if all(item["passed"] for item in checks) else "needs_revision",
        "scope": {
            "api_call_attempted": False,
            "raw_outputs_read": False,
            "pdf": rel(pdf),
            "tex": rel(tex),
            "render_dir": rel(render_dir),
        },
        "pdfinfo_pages": pages,
        "render": render,
        "checks": checks,
        "remaining_risks": [
            "This audit verifies renderability and obvious blank-page/layout failures; final camera-ready visual polish still needs human inspection.",
            "The compiled PDF remains a draft package, not a final submission artifact.",
        ],
    }


def render_md(audit: dict[str, Any]) -> str:
    lines = [
        "# APSEC PDF layout audit",
        "",
        f"- status: `{audit['status']}`",
        f"- pdf: `{audit['scope']['pdf']}`",
        f"- pdf pages: `{audit['pdfinfo_pages']}`",
        f"- render dir: `{audit['scope']['render_dir']}`",
        "",
        "## Checks",
        "",
        "| check | passed | detail |",
        "| --- | ---: | --- |",
    ]
    for item in audit["checks"]:
        detail = json.dumps(item["detail"], ensure_ascii=False, sort_keys=True)
        lines.append(f"| `{item['check']}` | {str(item['passed']).lower()} | `{detail}` |")
    lines.extend(["", "## Remaining Risks", ""])
    lines.extend(f"- {risk}" for risk in audit["remaining_risks"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--tex", type=Path, default=DEFAULT_TEX)
    parser.add_argument("--render-dir", type=Path, default=DEFAULT_RENDER_DIR)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    audit = build_audit(args.pdf, args.tex, args.render_dir)
    json_text = json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    md_text = render_md(audit)
    if args.check:
        existing_json = args.out_json.read_text(encoding="utf-8") if args.out_json.exists() else ""
        existing_md = args.out_md.read_text(encoding="utf-8") if args.out_md.exists() else ""
        if existing_json != json_text or existing_md != md_text:
            raise SystemExit("APSEC PDF layout audit outputs are stale")
        print("APSEC PDF layout audit outputs are current")
        return 0 if audit["status"] == "passed" else 1

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json_text, encoding="utf-8")
    args.out_md.write_text(md_text, encoding="utf-8")
    print(f"wrote {rel(args.out_json)}")
    print(f"wrote {rel(args.out_md)}")
    return 0 if audit["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
