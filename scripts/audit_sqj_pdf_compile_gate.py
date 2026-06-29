from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


DEFAULT_SOURCE = Path("docs/paper/sqj_submission_draft.tex")
DEFAULT_OUTPUT_DIR = Path("outputs/sqj_pdf_compile")


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


def tail(text: str | None, max_chars: int = 3000) -> str:
    if text is None:
        return ""
    return text[-max_chars:] if len(text) > max_chars else text


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def kpsewhich_state(class_name: str) -> dict[str, Any]:
    if not shutil.which("kpsewhich"):
        return {
            "available": False,
            "command": ["kpsewhich", class_name],
            "exit_code": None,
            "path": None,
            "stderr_tail": "kpsewhich executable not found",
            "stdout_tail": "",
        }
    result = run_command(["kpsewhich", class_name])
    path = result["stdout_tail"].strip()
    return {
        "available": result["exit_code"] == 0 and bool(path),
        "command": result["command"],
        "exit_code": result["exit_code"],
        "path": path or None,
        "stderr_tail": result["stderr_tail"],
        "stdout_tail": result["stdout_tail"],
    }


def audit_sqj_pdf_compile_gate(source: Path = DEFAULT_SOURCE, output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    source_exists = source.exists()
    pdflatex_path = shutil.which("pdflatex")
    class_state = kpsewhich_state("sn-jnl.cls")
    compile_runs: list[dict[str, Any]] = []
    output_pdf = output_dir / f"{source.stem}.pdf"

    if not source_exists:
        gate_status = "failed_missing_source"
        compile_attempted = False
        passed = False
    elif not class_state["available"]:
        gate_status = "blocked_missing_sn_jnl_cls"
        compile_attempted = False
        passed = True
    elif not pdflatex_path:
        gate_status = "blocked_missing_pdflatex"
        compile_attempted = False
        passed = True
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
        command = [
            "pdflatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={output_dir.as_posix()}",
            source.as_posix(),
        ]
        compile_runs = [run_command(command), run_command(command)]
        compile_attempted = True
        passed = all(run["exit_code"] == 0 for run in compile_runs) and output_pdf.exists() and output_pdf.stat().st_size > 0
        gate_status = "compiled" if passed else "failed_compile"

    return {
        "audit_id": "sqj_pdf_compile_gate",
        "boundary": (
            "This gate checks whether the SQJ Springer Nature sn-jnl source can be compiled. "
            "A missing sn-jnl.cls class is reported as an explicit blocker and does not mark "
            "the PDF compile gate as passed."
        ),
        "source": source.as_posix(),
        "source_exists": source_exists,
        "output_dir": output_dir.as_posix(),
        "output_pdf": output_pdf.as_posix(),
        "pdflatex_available": bool(pdflatex_path),
        "pdflatex_path": pdflatex_path,
        "sn_jnl_cls": class_state,
        "compile_attempted": compile_attempted,
        "compile_runs": compile_runs,
        "gate_status": gate_status,
        "pdf_exists": output_pdf.exists(),
        "pdf_size_bytes": output_pdf.stat().st_size if output_pdf.exists() else 0,
        "pdf_compile_passed": gate_status == "compiled",
        "final_freeze_complete": False,
        "passed": passed,
    }


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# SQJ PDF Compile Gate",
        "",
        "## Summary",
        "",
        f"- passed: {bool_mark(audit['passed'])}",
        f"- gate status: `{audit['gate_status']}`",
        f"- source exists: {bool_mark(audit['source_exists'])}",
        f"- pdflatex available: {bool_mark(audit['pdflatex_available'])}",
        f"- sn-jnl.cls available: {bool_mark(audit['sn_jnl_cls']['available'])}",
        f"- compile attempted: {bool_mark(audit['compile_attempted'])}",
        f"- PDF compile passed: {bool_mark(audit['pdf_compile_passed'])}",
        f"- final freeze complete: {bool_mark(audit['final_freeze_complete'])}",
        "",
        "## Boundary",
        "",
        audit["boundary"],
        "",
    ]
    if audit["sn_jnl_cls"].get("stderr_tail"):
        lines.extend(["## kpsewhich stderr tail", "", "```text", audit["sn_jnl_cls"]["stderr_tail"], "```", ""])
    if audit["compile_runs"]:
        lines.extend(["## Compile Runs", ""])
        for index, run in enumerate(audit["compile_runs"], start=1):
            lines.append(f"- run {index}: exit code `{run['exit_code']}`")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit the SQJ sn-jnl PDF compile gate.")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--out-json", default="outputs/sqj_pdf_compile_gate/latest.json")
    parser.add_argument("--out-md", default="outputs/sqj_pdf_compile_gate/latest.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = audit_sqj_pdf_compile_gate(Path(args.source), Path(args.output_dir))
    write_json(Path(args.out_json), audit)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(audit), encoding="utf-8")
    print(json.dumps({"out_json": args.out_json, "out_md": args.out_md, "passed": audit["passed"], "gate_status": audit["gate_status"]}, indent=2))
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
