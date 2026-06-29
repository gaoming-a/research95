from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


CHECKLIST = Path("docs/artifact/sqj_submission_checklist.md")
READINESS_PACKET = Path("docs/artifact/sqj_final_freeze_readiness.md")

REQUIRED_BOUNDARY_SNIPPETS = {
    CHECKLIST: [
        "School requirement route: school/department recognition confirmation is",
        "this checklist does not guarantee SQJ recognition",
        "Confirmation must check the publication-year CCF list, school category",
        "high-risk or warning-list status",
    ],
    READINESS_PACKET: [
        "school/department recognition confirmation for SQJ under the publication-year",
        "that school recognition is guaranteed",
        "Confirm whether SQJ is recognized by the school/department",
    ],
}

FORBIDDEN_CONFIRMED_SNIPPETS = [
    "SQJ recognition is confirmed",
    "school recognition is guaranteed.",
    "school recognition has been confirmed",
    "school/department recognition is complete",
    "school/department recognition confirmation is complete",
    "recognition_confirmed=true",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def audit_sqj_school_recognition_gate() -> dict[str, Any]:
    texts = {path: read_text(path) for path in REQUIRED_BOUNDARY_SNIPPETS}
    missing_required = {
        path.as_posix(): [snippet for snippet in snippets if snippet not in texts[path]]
        for path, snippets in REQUIRED_BOUNDARY_SNIPPETS.items()
    }
    forbidden_hits = {
        path.as_posix(): [snippet for snippet in FORBIDDEN_CONFIRMED_SNIPPETS if snippet in text]
        for path, text in texts.items()
    }
    source_states = {
        path.as_posix(): {
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else 0,
        }
        for path in REQUIRED_BOUNDARY_SNIPPETS
    }
    recognition_confirmed = False
    gate_status = "blocked_missing_school_recognition"
    passed = bool(
        all(state["exists"] and int(state["size_bytes"]) > 0 for state in source_states.values())
        and all(not misses for misses in missing_required.values())
        and all(not hits for hits in forbidden_hits.values())
        and gate_status == "blocked_missing_school_recognition"
        and recognition_confirmed is False
    )
    return {
        "audit_id": "sqj_school_recognition_gate",
        "boundary": (
            "This gate checks whether the SQJ school/department recognition decision "
            "is still an explicit external blocker. It does not query school policy, "
            "infer recognition, approve APC/OA route, or authorize submission."
        ),
        "gate_status": gate_status,
        "recognition_confirmed": recognition_confirmed,
        "school_policy_checked": False,
        "api_call_attempted": False,
        "web_lookup_attempted": False,
        "final_freeze_complete": False,
        "source_states": source_states,
        "missing_required_boundary_snippets": missing_required,
        "forbidden_confirmation_hits": forbidden_hits,
        "passed": passed,
    }


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# SQJ School Recognition Gate",
        "",
        "## Summary",
        "",
        f"- passed: {bool_mark(audit['passed'])}",
        f"- gate status: `{audit['gate_status']}`",
        f"- recognition confirmed: {bool_mark(audit['recognition_confirmed'])}",
        f"- school policy checked: {bool_mark(audit['school_policy_checked'])}",
        f"- API call attempted: {bool_mark(audit['api_call_attempted'])}",
        f"- web lookup attempted: {bool_mark(audit['web_lookup_attempted'])}",
        f"- final freeze complete: {bool_mark(audit['final_freeze_complete'])}",
        "",
        "## Sources",
        "",
    ]
    for path, state in audit["source_states"].items():
        lines.append(f"- `{path}`: exists={bool_mark(state['exists'])}, size={state['size_bytes']}")
    lines.extend(["", "## Missing Required Boundary Snippets", ""])
    for path, misses in audit["missing_required_boundary_snippets"].items():
        lines.append(f"- `{path}`: {len(misses)}")
        for snippet in misses:
            lines.append(f"  - `{snippet}`")
    lines.extend(["", "## Forbidden Confirmation Hits", ""])
    for path, hits in audit["forbidden_confirmation_hits"].items():
        lines.append(f"- `{path}`: {len(hits)}")
        for snippet in hits:
            lines.append(f"  - `{snippet}`")
    lines.extend(["", "## Boundary", "", audit["boundary"], ""])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit the SQJ school-recognition blocker gate.")
    parser.add_argument("--out-json", default="outputs/sqj_school_recognition_gate/latest.json")
    parser.add_argument("--out-md", default="outputs/sqj_school_recognition_gate/latest.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = audit_sqj_school_recognition_gate()
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
