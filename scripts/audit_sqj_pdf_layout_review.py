from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from PIL import Image


DEFAULT_PDF = Path("outputs/sqj_pdf_compile/sqj_submission_draft.pdf")
DEFAULT_LOG = Path("outputs/sqj_pdf_compile/sqj_submission_draft.log")
DEFAULT_RENDER_DIR = Path("outputs/sqj_pdf_layout_review/pages")
DEFAULT_TEXT = Path("outputs/sqj_pdf_layout_review/sqj_submission_draft.txt")

REQUIRED_TEXT_SNIPPETS = [
    "EVP-8 hidden-evaluator study design",
    "Five-model decision patterns",
    "Cost-observability and result-validity boundary",
    "References",
]

LOG_BLOCKER_PATTERNS = [
    r"No file .*\.bbl",
    r"undefined citations",
    r"Citation `[^']+' .* undefined",
    r"Reference `[^']+' .* undefined",
    r"Overfull \\hbox",
]


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def tail(text: str | None, max_chars: int = 3000) -> str:
    if text is None:
        return ""
    return text[-max_chars:] if len(text) > max_chars else text


def run_command(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        "command": command,
        "exit_code": completed.returncode,
        "stdout_tail": tail(completed.stdout),
        "stderr_tail": tail(completed.stderr),
    }


def poppler_binary(name: str) -> str | None:
    found = shutil.which(name)
    if found and not found.lower().endswith(".cmd"):
        return found
    bundled = (
        Path.home()
        / ".cache"
        / "codex-runtimes"
        / "codex-primary-runtime"
        / "dependencies"
        / "native"
        / "poppler"
        / "Library"
        / "bin"
        / f"{name}.exe"
    )
    if bundled.exists():
        return str(bundled)
    return found


def parse_pdfinfo_pages(stdout: str) -> int | None:
    match = re.search(r"^Pages:\s+(\d+)\s*$", stdout, flags=re.MULTILINE)
    return int(match.group(1)) if match else None


def render_pdf(pdf: Path, render_dir: Path) -> tuple[dict[str, Any], list[Path]]:
    render_dir.mkdir(parents=True, exist_ok=True)
    for old_page in render_dir.glob("sqj_page-*.png"):
        old_page.unlink()
    pdftoppm = poppler_binary("pdftoppm")
    if not pdftoppm:
        return (
            {
                "command": ["pdftoppm"],
                "exit_code": None,
                "stdout_tail": "",
                "stderr_tail": "pdftoppm executable not found",
            },
            [],
        )
    command = [pdftoppm, "-png", "-r", "120", pdf.as_posix(), (render_dir / "sqj_page").as_posix()]
    result = run_command(command)
    pages = sorted(render_dir.glob("sqj_page-*.png"))
    return result, pages


def extract_text(pdf: Path, text_path: Path) -> tuple[dict[str, Any], str]:
    text_path.parent.mkdir(parents=True, exist_ok=True)
    pdftotext = shutil.which("pdftotext")
    if not pdftotext:
        return (
            {
                "command": ["pdftotext"],
                "exit_code": None,
                "stdout_tail": "",
                "stderr_tail": "pdftotext executable not found",
            },
            "",
        )
    result = run_command([pdftotext, pdf.as_posix(), text_path.as_posix()])
    text = text_path.read_text(encoding="utf-8", errors="replace") if text_path.exists() else ""
    return result, text


def image_state(path: Path) -> dict[str, Any]:
    image = Image.open(path).convert("L")
    histogram = image.histogram()
    total_pixels = image.width * image.height
    dark_pixels = sum(histogram[:245])
    mask = image.point(lambda pixel: 0 if pixel > 250 else 255)
    bbox = mask.getbbox()
    touches_edge = False
    if bbox:
        left, top, right, bottom = bbox
        touches_edge = left <= 2 or top <= 2 or right >= image.width - 2 or bottom >= image.height - 2
    return {
        "path": path.as_posix(),
        "width": image.width,
        "height": image.height,
        "dark_ratio": dark_pixels / total_pixels if total_pixels else 0.0,
        "content_bbox": list(bbox) if bbox else None,
        "nonblank": bool(bbox and dark_pixels > 0),
        "content_touches_page_edge": touches_edge,
    }


def log_blockers(log_text: str) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    for pattern in LOG_BLOCKER_PATTERNS:
        for match in re.finditer(pattern, log_text, flags=re.IGNORECASE):
            start = max(0, match.start() - 120)
            end = min(len(log_text), match.end() + 160)
            blockers.append({"pattern": pattern, "context": log_text[start:end].strip()})
    return blockers


def audit_sqj_pdf_layout_review(
    pdf: Path = DEFAULT_PDF,
    log_path: Path = DEFAULT_LOG,
    render_dir: Path = DEFAULT_RENDER_DIR,
    text_path: Path = DEFAULT_TEXT,
) -> dict[str, Any]:
    pdfinfo = poppler_binary("pdfinfo")
    pdfinfo_run = run_command([pdfinfo, pdf.as_posix()]) if pdfinfo and pdf.exists() else None
    page_count = parse_pdfinfo_pages(pdfinfo_run["stdout_tail"]) if pdfinfo_run else None
    render_run, rendered_pages = render_pdf(pdf, render_dir) if pdf.exists() else (None, [])
    text_run, extracted_text = extract_text(pdf, text_path) if pdf.exists() else (None, "")
    page_states = [image_state(page) for page in rendered_pages]
    log_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    missing_text_snippets = [snippet for snippet in REQUIRED_TEXT_SNIPPETS if snippet not in extracted_text]
    blockers = log_blockers(log_text)
    pages_touching_edge = [state for state in page_states if state["content_touches_page_edge"]]
    blank_pages = [state for state in page_states if not state["nonblank"]]

    layout_review_complete = bool(
        pdf.exists()
        and page_count
        and len(page_states) == page_count
        and not blank_pages
        and not pages_touching_edge
        and not missing_text_snippets
        and not blockers
    )
    if not pdf.exists():
        gate_status = "failed_missing_pdf"
        passed = False
    elif not layout_review_complete:
        gate_status = "failed_pdf_layout_or_reference_review"
        passed = False
    else:
        gate_status = "post_compile_layout_review_passed"
        passed = True

    return {
        "audit_id": "sqj_pdf_layout_review",
        "boundary": (
            "This gate reviews the compiled SQJ PDF rendering, figure/caption text, "
            "reference resolution, and obvious page-edge overflow. It does not "
            "authorize final freeze, artifact release, school recognition, or submission."
        ),
        "pdf": pdf.as_posix(),
        "pdf_exists": pdf.exists(),
        "pdf_size_bytes": pdf.stat().st_size if pdf.exists() else 0,
        "log": log_path.as_posix(),
        "log_exists": log_path.exists(),
        "render_dir": render_dir.as_posix(),
        "text_path": text_path.as_posix(),
        "page_count": page_count,
        "rendered_page_count": len(page_states),
        "pdfinfo_run": pdfinfo_run,
        "render_run": render_run,
        "text_run": text_run,
        "page_states": page_states,
        "blank_pages": blank_pages,
        "pages_touching_edge": pages_touching_edge,
        "missing_text_snippets": missing_text_snippets,
        "log_blockers": blockers,
        "layout_review_complete": layout_review_complete,
        "api_call_attempted": False,
        "final_freeze_complete": False,
        "gate_status": gate_status,
        "passed": passed,
    }


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# SQJ PDF Layout Review",
        "",
        "## Summary",
        "",
        f"- passed: {bool_mark(audit['passed'])}",
        f"- gate status: `{audit['gate_status']}`",
        f"- PDF exists: {bool_mark(audit['pdf_exists'])}",
        f"- page count: `{audit['page_count']}`",
        f"- rendered page count: `{audit['rendered_page_count']}`",
        f"- blank pages: `{len(audit['blank_pages'])}`",
        f"- pages touching edge: `{len(audit['pages_touching_edge'])}`",
        f"- missing text snippets: `{len(audit['missing_text_snippets'])}`",
        f"- log blockers: `{len(audit['log_blockers'])}`",
        f"- layout review complete: {bool_mark(audit['layout_review_complete'])}",
        f"- API call attempted: {bool_mark(audit['api_call_attempted'])}",
        f"- final freeze complete: {bool_mark(audit['final_freeze_complete'])}",
        "",
        "## Boundary",
        "",
        audit["boundary"],
        "",
    ]
    if audit["pages_touching_edge"]:
        lines.extend(["## Pages Touching Edge", ""])
        for state in audit["pages_touching_edge"]:
            lines.append(f"- `{state['path']}` bbox={state['content_bbox']}")
        lines.append("")
    if audit["missing_text_snippets"]:
        lines.extend(["## Missing Text Snippets", ""])
        for snippet in audit["missing_text_snippets"]:
            lines.append(f"- `{snippet}`")
        lines.append("")
    if audit["log_blockers"]:
        lines.extend(["## Log Blockers", ""])
        for blocker in audit["log_blockers"]:
            lines.append(f"- pattern `{blocker['pattern']}`")
        lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit the compiled SQJ PDF layout and references.")
    parser.add_argument("--pdf", default=str(DEFAULT_PDF))
    parser.add_argument("--log", default=str(DEFAULT_LOG))
    parser.add_argument("--render-dir", default=str(DEFAULT_RENDER_DIR))
    parser.add_argument("--text", default=str(DEFAULT_TEXT))
    parser.add_argument("--out-json", default="outputs/sqj_pdf_layout_review/latest.json")
    parser.add_argument("--out-md", default="docs/experiments/sqj_pdf_layout_review.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = audit_sqj_pdf_layout_review(Path(args.pdf), Path(args.log), Path(args.render_dir), Path(args.text))
    write_json(Path(args.out_json), audit)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(audit), encoding="utf-8")
    print(
        json.dumps(
            {
                "out_json": args.out_json,
                "out_md": args.out_md,
                "passed": audit["passed"],
                "gate_status": audit["gate_status"],
            },
            indent=2,
        )
    )
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
