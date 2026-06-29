from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SOURCE_DRAFT = Path("docs/paper/sqj_submission_draft.tex")
CHECKLIST = Path("docs/artifact/sqj_submission_checklist.md")
FINAL_FREEZE_READINESS = Path("docs/artifact/sqj_final_freeze_readiness.md")

DRAFT_REQUIRED_SNIPPETS = [
    r"\bmhead{Data availability}",
    r"\bmhead{Code availability}",
    "tracked raw-output-free summaries",
    "paper tables in the project repository",
    "Raw model responses, local API",
    "configuration, and ignored execution logs are excluded from the tracked",
    "artifact boundary.",
    r"\verb|python scripts\write_sqj_latex_draft.py --check|",
    r"\verb|docs/paper/sqj_submission_draft.tex|",
]

PACKAGE_REQUIRED_SNIPPETS = {
    CHECKLIST: [
        "Status: SQJ source package checklist, not final freeze.",
        "No raw model responses, `.env`, local configs, `outputs/`, `artifacts/`, or",
        "benchmark checkouts are committed.",
        "`candidate_artifact_dry_run_ready`",
        "`blocked_missing_final_authorization`",
        "This is not a final submission freeze.",
    ],
    FINAL_FREEZE_READINESS: [
        "Status: SQJ final-freeze readiness packet, not final freeze.",
        "This packet does not authorize submission.",
        "No model API calls are authorized.",
        "final artifact package rebuild and audit",
        "`candidate_artifact_dry_run_ready`",
        "`blocked_missing_final_authorization`",
        "This is a readiness and blocker packet only.",
    ],
}

FORBIDDEN_SNIPPETS = [
    "raw model responses are tracked",
    "raw responses are included",
    ".env is committed",
    "local configs are committed",
    "outputs/ are committed",
    "artifacts/ are committed",
    "Status: final freeze complete.",
    "This packet authorizes submission.",
    "final submission freeze is complete",
    "ready-to-submit",
    "ready to submit",
    "final artifact rebuild complete: yes",
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


def missing_snippets(text: str, snippets: list[str]) -> list[str]:
    return [snippet for snippet in snippets if snippet not in text]


def forbidden_hits(text_by_path: dict[Path, str]) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {}
    for path, text in text_by_path.items():
        path_hits = [snippet for snippet in FORBIDDEN_SNIPPETS if snippet in text]
        if path_hits:
            hits[path.as_posix()] = path_hits
    return hits


def audit_sqj_availability_boundary() -> dict[str, Any]:
    texts = {
        SOURCE_DRAFT: read_text(SOURCE_DRAFT),
        CHECKLIST: read_text(CHECKLIST),
        FINAL_FREEZE_READINESS: read_text(FINAL_FREEZE_READINESS),
    }
    draft_missing = missing_snippets(texts[SOURCE_DRAFT], DRAFT_REQUIRED_SNIPPETS)
    package_missing = {
        path.as_posix(): missing_snippets(texts[path], snippets)
        for path, snippets in PACKAGE_REQUIRED_SNIPPETS.items()
    }
    package_missing = {path: misses for path, misses in package_missing.items() if misses}
    forbidden = forbidden_hits(texts)
    raw_outputs_excluded = not draft_missing and not package_missing and not forbidden
    result = {
        "audit_id": "sqj_availability_boundary",
        "gate_status": "sqj_availability_boundary_ready" if raw_outputs_excluded else "failed_availability_boundary",
        "sources": {
            "source_draft": file_state(SOURCE_DRAFT),
            "checklist": file_state(CHECKLIST),
            "final_freeze_readiness": file_state(FINAL_FREEZE_READINESS),
        },
        "data_availability_present": r"\bmhead{Data availability}" in texts[SOURCE_DRAFT],
        "code_availability_present": r"\bmhead{Code availability}" in texts[SOURCE_DRAFT],
        "draft_missing_required_snippets": draft_missing,
        "package_missing_required_snippets": package_missing,
        "forbidden_snippet_hits": forbidden,
        "raw_outputs_excluded": raw_outputs_excluded,
        "local_secrets_excluded": not package_missing and not forbidden,
        "submission_authorized": False,
        "final_artifact_rebuild_complete": False,
        "final_freeze_complete": False,
        "api_call_attempted": False,
        "raw_model_outputs_read": False,
    }
    result["passed"] = bool(
        all(state["exists"] and int(state["size_bytes"]) > 0 for state in result["sources"].values())
        and result["data_availability_present"]
        and result["code_availability_present"]
        and not draft_missing
        and not package_missing
        and not forbidden
        and result["raw_outputs_excluded"]
        and result["local_secrets_excluded"]
        and result["submission_authorized"] is False
        and result["final_artifact_rebuild_complete"] is False
        and result["final_freeze_complete"] is False
        and result["api_call_attempted"] is False
        and result["raw_model_outputs_read"] is False
    )
    return result


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# SQJ Availability Boundary Audit",
        "",
        "## Summary",
        "",
        f"- passed: {bool_mark(audit['passed'])}",
        f"- gate status: `{audit['gate_status']}`",
        f"- data availability present: {bool_mark(audit['data_availability_present'])}",
        f"- code availability present: {bool_mark(audit['code_availability_present'])}",
        f"- raw outputs excluded: {bool_mark(audit['raw_outputs_excluded'])}",
        f"- local secrets excluded: {bool_mark(audit['local_secrets_excluded'])}",
        f"- submission authorized: {bool_mark(audit['submission_authorized'])}",
        f"- final artifact rebuild complete: {bool_mark(audit['final_artifact_rebuild_complete'])}",
        f"- final freeze complete: {bool_mark(audit['final_freeze_complete'])}",
        f"- API call attempted: {bool_mark(audit['api_call_attempted'])}",
        f"- raw model outputs read: {bool_mark(audit['raw_model_outputs_read'])}",
        f"- draft missing snippets: {len(audit['draft_missing_required_snippets'])}",
        f"- package missing snippet groups: {len(audit['package_missing_required_snippets'])}",
        f"- forbidden snippet files: {len(audit['forbidden_snippet_hits'])}",
        "",
        "## Sources",
        "",
    ]
    for name, state in audit["sources"].items():
        lines.append(f"- `{name}`: exists={bool_mark(state['exists'])}, size={state['size_bytes']}, path=`{state['path']}`")
    if audit["draft_missing_required_snippets"]:
        lines.extend(["", "## Draft Missing Required Snippets", ""])
        for snippet in audit["draft_missing_required_snippets"]:
            lines.append(f"- `{snippet}`")
    if audit["package_missing_required_snippets"]:
        lines.extend(["", "## Package Missing Required Snippets", ""])
        for path, snippets in audit["package_missing_required_snippets"].items():
            lines.append(f"- `{path}`")
            for snippet in snippets:
                lines.append(f"  - `{snippet}`")
    if audit["forbidden_snippet_hits"]:
        lines.extend(["", "## Forbidden Snippet Hits", ""])
        for path, snippets in audit["forbidden_snippet_hits"].items():
            lines.append(f"- `{path}`")
            for snippet in snippets:
                lines.append(f"  - `{snippet}`")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This audit checks SQJ data/code availability wording and source-package boundaries only. It does not call model APIs, read raw model outputs, build a final artifact, authorize submission, or mark final freeze complete.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit SQJ data/code availability and artifact boundary wording.")
    parser.add_argument("--out-json", default="outputs/sqj_availability_boundary/latest.json")
    parser.add_argument("--out-md", default="docs/experiments/sqj_availability_boundary.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = audit_sqj_availability_boundary()
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
