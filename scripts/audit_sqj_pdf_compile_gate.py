from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


DEFAULT_SOURCE = Path("docs/paper/sqj_submission_draft.tex")
DEFAULT_OUTPUT_DIR = Path("outputs/sqj_pdf_compile")
DEFAULT_TEMPLATE_DIR = Path("outputs/sqj_springer_template/extracted")


def run_command(command: list[str], env: dict[str, str] | None = None) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
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
        "source": "kpsewhich",
        "command": result["command"],
        "exit_code": result["exit_code"],
        "path": path or None,
        "stderr_tail": result["stderr_tail"],
        "stdout_tail": result["stdout_tail"],
    }


def local_template_state(template_dir: Path, class_name: str) -> dict[str, Any]:
    class_files = sorted(path for path in template_dir.rglob(class_name)) if template_dir.exists() else []
    return {
        "available": bool(class_files),
        "source": "local_template_cache",
        "template_dir": template_dir.as_posix(),
        "class_files": [path.as_posix() for path in class_files],
        "texinputs": f"{template_dir.as_posix()}//{os.pathsep}",
    }


def resolve_class_state(class_name: str, template_dir: Path) -> dict[str, Any]:
    kpse_state = kpsewhich_state(class_name)
    local_state = local_template_state(template_dir, class_name)
    if kpse_state["available"]:
        return {
            "available": True,
            "source": "kpsewhich",
            "kpsewhich": kpse_state,
            "local_template_cache": local_state,
            "texinputs": None,
        }
    if local_state["available"]:
        return {
            "available": True,
            "source": "local_template_cache",
            "kpsewhich": kpse_state,
            "local_template_cache": local_state,
            "texinputs": local_state["texinputs"],
        }
    return {
        "available": False,
        "source": "missing",
        "kpsewhich": kpse_state,
        "local_template_cache": local_state,
        "texinputs": None,
    }


def compile_environment(class_state: dict[str, Any], source_dir: Path) -> dict[str, str]:
    texinputs_parts = [f"{source_dir.as_posix()}{os.pathsep}"]
    bibinputs_parts = [f"{source_dir.as_posix()}{os.pathsep}"]
    bstinputs_parts: list[str] = []
    if class_state.get("texinputs"):
        texinputs_parts.append(str(class_state["texinputs"]))
        bstinputs_parts.append(str(class_state["texinputs"]))
    texinputs = "".join(texinputs_parts)
    bibinputs = "".join(bibinputs_parts)
    bstinputs = "".join(bstinputs_parts)
    env = os.environ.copy()
    env["TEXINPUTS"] = f"{texinputs}{env.get('TEXINPUTS', '')}"
    env["BIBINPUTS"] = f"{bibinputs}{env.get('BIBINPUTS', '')}"
    if bstinputs:
        env["BSTINPUTS"] = f"{bstinputs}{env.get('BSTINPUTS', '')}"
    return env


def audit_sqj_pdf_compile_gate(
    source: Path = DEFAULT_SOURCE,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    template_dir: Path = DEFAULT_TEMPLATE_DIR,
) -> dict[str, Any]:
    source_exists = source.exists()
    pdflatex_path = shutil.which("pdflatex")
    bibtex_path = shutil.which("bibtex")
    class_state = resolve_class_state("sn-jnl.cls", template_dir)
    compile_runs: list[dict[str, Any]] = []
    bibtex_run: dict[str, Any] | None = None
    output_pdf = output_dir / f"{source.stem}.pdf"
    output_bbl = output_dir / f"{source.stem}.bbl"

    if not source_exists:
        gate_status = "failed_missing_source"
        compile_attempted = False
        bibtex_attempted = False
        passed = False
    elif not class_state["available"]:
        gate_status = "blocked_missing_sn_jnl_cls"
        compile_attempted = False
        bibtex_attempted = False
        passed = True
    elif not pdflatex_path:
        gate_status = "blocked_missing_pdflatex"
        compile_attempted = False
        bibtex_attempted = False
        passed = True
    elif not bibtex_path:
        gate_status = "blocked_missing_bibtex"
        compile_attempted = False
        bibtex_attempted = False
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
        env = compile_environment(class_state, source.parent)
        bibtex_command = ["bibtex", (output_dir / source.stem).as_posix()]
        compile_runs = [run_command(command, env=env)]
        bibtex_run = run_command(bibtex_command, env=env)
        compile_runs.extend([run_command(command, env=env), run_command(command, env=env)])
        compile_attempted = True
        bibtex_attempted = True
        passed = bool(
            all(run["exit_code"] == 0 for run in compile_runs)
            and bibtex_run["exit_code"] == 0
            and output_pdf.exists()
            and output_pdf.stat().st_size > 0
            and output_bbl.exists()
            and output_bbl.stat().st_size > 0
        )
        gate_status = "compiled" if passed else "failed_compile"

    return {
        "audit_id": "sqj_pdf_compile_gate",
        "boundary": (
            "This gate checks whether the SQJ Springer Nature sn-jnl source can be compiled. "
            "Missing TeX tools or sn-jnl.cls are explicit blockers. A compiled gate requires "
            "BibTeX-resolved references and does not mark final freeze complete."
        ),
        "source": source.as_posix(),
        "source_exists": source_exists,
        "output_dir": output_dir.as_posix(),
        "output_pdf": output_pdf.as_posix(),
        "pdflatex_available": bool(pdflatex_path),
        "pdflatex_path": pdflatex_path,
        "bibtex_available": bool(bibtex_path),
        "bibtex_path": bibtex_path,
        "sn_jnl_cls": class_state,
        "compile_attempted": compile_attempted,
        "bibtex_attempted": bibtex_attempted,
        "compile_runs": compile_runs,
        "bibtex_run": bibtex_run,
        "gate_status": gate_status,
        "pdf_exists": output_pdf.exists(),
        "pdf_size_bytes": output_pdf.stat().st_size if output_pdf.exists() else 0,
        "bbl_exists": output_bbl.exists(),
        "bbl_size_bytes": output_bbl.stat().st_size if output_bbl.exists() else 0,
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
        f"- bibtex available: {bool_mark(audit['bibtex_available'])}",
        f"- sn-jnl.cls available: {bool_mark(audit['sn_jnl_cls']['available'])}",
        f"- sn-jnl.cls source: `{audit['sn_jnl_cls']['source']}`",
        f"- compile attempted: {bool_mark(audit['compile_attempted'])}",
        f"- bibtex attempted: {bool_mark(audit['bibtex_attempted'])}",
        f"- PDF compile passed: {bool_mark(audit['pdf_compile_passed'])}",
        f"- BBL exists: {bool_mark(audit['bbl_exists'])}",
        f"- final freeze complete: {bool_mark(audit['final_freeze_complete'])}",
        "",
        "## Boundary",
        "",
        audit["boundary"],
        "",
    ]
    kpse_state = audit["sn_jnl_cls"].get("kpsewhich", audit["sn_jnl_cls"])
    if kpse_state.get("stderr_tail"):
        lines.extend(["## kpsewhich stderr tail", "", "```text", kpse_state["stderr_tail"], "```", ""])
    if audit["compile_runs"]:
        lines.extend(["## Compile Runs", ""])
        for index, run in enumerate(audit["compile_runs"], start=1):
            lines.append(f"- run {index}: exit code `{run['exit_code']}`")
    if audit["bibtex_run"]:
        lines.extend(["", "## BibTeX Run", "", f"- exit code `{audit['bibtex_run']['exit_code']}`"])
        tail_text = audit["bibtex_run"]["stderr_tail"] or audit["bibtex_run"]["stdout_tail"]
        if tail_text:
            lines.extend(["", "```text", tail_text, "```", ""])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit the SQJ sn-jnl PDF compile gate.")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--template-dir", default=str(DEFAULT_TEMPLATE_DIR))
    parser.add_argument("--out-json", default="outputs/sqj_pdf_compile_gate/latest.json")
    parser.add_argument("--out-md", default="outputs/sqj_pdf_compile_gate/latest.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = audit_sqj_pdf_compile_gate(Path(args.source), Path(args.output_dir), Path(args.template_dir))
    write_json(Path(args.out_json), audit)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(audit), encoding="utf-8")
    print(json.dumps({"out_json": args.out_json, "out_md": args.out_md, "passed": audit["passed"], "gate_status": audit["gate_status"]}, indent=2))
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
