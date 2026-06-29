from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


CHECKLIST = Path("docs/artifact/sqj_submission_checklist.md")
READINESS_PACKET = Path("docs/artifact/sqj_final_freeze_readiness.md")

REQUIRED_BOUNDARY_SNIPPETS = {
    CHECKLIST: [
        "Status: SQJ source package checklist, not final freeze.",
        "This checklist records the current Software Quality Journal (SQJ) submission",
        "route. It does not authorize new experiments, model API calls, cohort",
        "This is not a final submission freeze.",
    ],
    READINESS_PACKET: [
        "Status: SQJ final-freeze readiness packet, not final freeze.",
        "This packet does not authorize submission.",
        "final user authorization to submit",
        "This is a readiness and blocker packet only.",
    ],
}

FORBIDDEN_AUTHORIZATION_SNIPPETS = [
    "This packet authorizes submission.",
    "This checklist authorizes submission.",
    "submission_authorized=true",
    "final submission freeze is complete",
    "Status: final freeze complete.",
    "ready to submit",
    "ready-to-submit",
    "authorized to submit",
    "submission is authorized",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def audit_sqj_final_authorization_gate() -> dict[str, Any]:
    texts = {path: read_text(path) for path in REQUIRED_BOUNDARY_SNIPPETS}
    missing_required = {
        path.as_posix(): [snippet for snippet in snippets if snippet not in texts[path]]
        for path, snippets in REQUIRED_BOUNDARY_SNIPPETS.items()
    }
    forbidden_hits = {
        path.as_posix(): [snippet for snippet in FORBIDDEN_AUTHORIZATION_SNIPPETS if snippet in text]
        for path, text in texts.items()
    }
    source_states = {
        path.as_posix(): {
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else 0,
        }
        for path in REQUIRED_BOUNDARY_SNIPPETS
    }
    submission_authorized = False
    gate_status = "blocked_missing_final_authorization"
    passed = bool(
        all(state["exists"] and int(state["size_bytes"]) > 0 for state in source_states.values())
        and all(not misses for misses in missing_required.values())
        and all(not hits for hits in forbidden_hits.values())
        and gate_status == "blocked_missing_final_authorization"
        and submission_authorized is False
    )
    return {
        "audit_id": "sqj_final_authorization_gate",
        "boundary": (
            "This gate checks whether SQJ final submission authorization is still "
            "an explicit blocker. It does not submit the paper, create a final "
            "artifact, mark final freeze complete, or infer user authorization."
        ),
        "gate_status": gate_status,
        "submission_authorized": submission_authorized,
        "submission_system_accessed": False,
        "api_call_attempted": False,
        "final_artifact_rebuild_complete": False,
        "final_freeze_complete": False,
        "source_states": source_states,
        "missing_required_boundary_snippets": missing_required,
        "forbidden_authorization_hits": forbidden_hits,
        "passed": passed,
    }


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# SQJ Final Authorization Gate",
        "",
        "## Summary",
        "",
        f"- passed: {bool_mark(audit['passed'])}",
        f"- gate status: `{audit['gate_status']}`",
        f"- submission authorized: {bool_mark(audit['submission_authorized'])}",
        f"- submission system accessed: {bool_mark(audit['submission_system_accessed'])}",
        f"- API call attempted: {bool_mark(audit['api_call_attempted'])}",
        f"- final artifact rebuild complete: {bool_mark(audit['final_artifact_rebuild_complete'])}",
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
    lines.extend(["", "## Forbidden Authorization Hits", ""])
    for path, hits in audit["forbidden_authorization_hits"].items():
        lines.append(f"- `{path}`: {len(hits)}")
        for snippet in hits:
            lines.append(f"  - `{snippet}`")
    lines.extend(["", "## Boundary", "", audit["boundary"], ""])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit the SQJ final user authorization blocker gate.")
    parser.add_argument("--out-json", default="outputs/sqj_final_authorization_gate/latest.json")
    parser.add_argument("--out-md", default="outputs/sqj_final_authorization_gate/latest.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = audit_sqj_final_authorization_gate()
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
