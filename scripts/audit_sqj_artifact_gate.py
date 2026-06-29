from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from scripts.prepare_anonymous_artifact import iter_files, validate_files
except ModuleNotFoundError:
    from prepare_anonymous_artifact import iter_files, validate_files


REQUIRED_SQJ_FILES = [
    Path("docs/paper/sqj_submission_draft.tex"),
    Path("docs/paper/sqj_submission_framing.md"),
    Path("docs/paper/sqj_references.bib"),
    Path("docs/artifact/sqj_submission_checklist.md"),
    Path("docs/artifact/sqj_final_freeze_readiness.md"),
    Path("docs/figures/sqj/figure_manifest.json"),
    Path("scripts/write_sqj_latex_draft.py"),
    Path("scripts/audit_sqj_artifact_gate.py"),
    Path("scripts/audit_sqj_school_recognition_gate.py"),
    Path("scripts/audit_sqj_submission_checklist.py"),
    Path("scripts/audit_sqj_final_freeze_readiness.py"),
    Path("scripts/audit_sqj_human_inputs_gate.py"),
    Path("scripts/audit_sqj_pdf_compile_gate.py"),
]


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def audit_sqj_artifact_gate() -> dict[str, Any]:
    files = iter_files()
    included = {path.as_posix() for path in files}
    validation = validate_files(files)
    required_states = {
        path.as_posix(): {
            "exists": path.exists(),
            "included": path.as_posix() in included,
            "size_bytes": path.stat().st_size if path.exists() else 0,
        }
        for path in REQUIRED_SQJ_FILES
    }
    missing_required = [
        path
        for path, state in required_states.items()
        if not state["exists"] or not state["included"] or int(state["size_bytes"]) <= 0
    ]
    safe_to_package = bool(validation.get("safe_to_package"))
    gate_status = "candidate_artifact_dry_run_ready" if safe_to_package and not missing_required else "blocked_artifact_candidate"
    return {
        "audit_id": "sqj_artifact_gate",
        "boundary": (
            "This gate checks whether the current tracked SQJ source package is safe "
            "for an anonymous artifact dry run. It does not create a final artifact ZIP, "
            "mark final freeze complete, or authorize submission."
        ),
        "dry_run_only": True,
        "final_artifact_rebuild_complete": False,
        "final_freeze_complete": False,
        "file_count": len(files),
        "required_sqj_files": required_states,
        "missing_required": missing_required,
        "validation": validation,
        "safe_to_package": safe_to_package,
        "gate_status": gate_status,
        "passed": gate_status == "candidate_artifact_dry_run_ready",
    }


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# SQJ Artifact Gate",
        "",
        "## Summary",
        "",
        f"- passed: {bool_mark(audit['passed'])}",
        f"- gate status: `{audit['gate_status']}`",
        f"- dry run only: {bool_mark(audit['dry_run_only'])}",
        f"- final artifact rebuild complete: {bool_mark(audit['final_artifact_rebuild_complete'])}",
        f"- final freeze complete: {bool_mark(audit['final_freeze_complete'])}",
        f"- file count: {audit['file_count']}",
        f"- safe to package: {bool_mark(audit['safe_to_package'])}",
        f"- missing required SQJ files: {len(audit['missing_required'])}",
        f"- validation violations: {len(audit['validation']['violations'])}",
        "",
        "## Required SQJ Files",
        "",
    ]
    for path, state in audit["required_sqj_files"].items():
        lines.append(
            f"- `{path}`: exists={bool_mark(state['exists'])}, "
            f"included={bool_mark(state['included'])}, size={state['size_bytes']}"
        )
    lines.extend(["", "## Boundary", "", audit["boundary"], ""])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit the SQJ anonymous artifact candidate gate.")
    parser.add_argument("--out-json", default="outputs/sqj_artifact_gate/latest.json")
    parser.add_argument("--out-md", default="outputs/sqj_artifact_gate/latest.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = audit_sqj_artifact_gate()
    write_json(Path(args.out_json), audit)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(audit), encoding="utf-8")
    print(json.dumps({"out_json": args.out_json, "out_md": args.out_md, "passed": audit["passed"], "gate_status": audit["gate_status"]}, indent=2))
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
