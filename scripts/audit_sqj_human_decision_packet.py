from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_PACKET = Path("docs/artifact/sqj_human_decision_packet.md")

REQUIRED_DECISION_IDS = [
    "school_recognition",
    "author_identity",
    "funding_acknowledgements",
    "competing_interests",
    "author_contributions",
    "springer_template",
    "post_compile_layout_review",
    "final_artifact_rebuild",
    "final_submission_authorization",
]

REQUIRED_SNIPPETS = [
    "Status: SQJ human-decision packet, not final freeze.",
    "This packet lists the human decisions and external inputs still required",
    "It does not authorize submission, model API calls, PDF compilation, or",
    "`blocked_missing_school_recognition`",
    "`blocked_missing_human_inputs`",
    "`blocked_missing_sn_jnl_cls`",
    "`blocked_pending_pdf_compile`",
    "`candidate_artifact_dry_run_ready`",
    "`blocked_missing_final_authorization`",
    "Submission authorized: `false`.",
    "Human decisions complete: `false`.",
    "Final freeze complete: `false`.",
    "PDF compile passed: `false`.",
    "Model API calls authorized by this packet: `false`.",
    "Artifact release authorized by this packet: `false`.",
    "Do not use broad API authorization as submission authorization.",
    "python scripts\\audit_sqj_human_decision_packet.py",
]

FORBIDDEN_SNIPPETS = [
    "Submission authorized: `true`",
    "Human decisions complete: `true`",
    "Final freeze complete: `true`",
    "PDF compile passed: `true`",
    "Model API calls authorized by this packet: `true`",
    "Artifact release authorized by this packet: `true`",
    "Status: SQJ human-decision packet, final freeze complete.",
    "Status: ready-to-submit.",
    "SQJ recognition confirmed: `true`",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def audit_sqj_human_decision_packet(path: Path = DEFAULT_PACKET) -> dict[str, Any]:
    text = read_text(path)
    missing_decision_ids = [decision_id for decision_id in REQUIRED_DECISION_IDS if f"`{decision_id}`" not in text]
    missing_required_snippets = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
    forbidden_snippet_hits = [snippet for snippet in FORBIDDEN_SNIPPETS if snippet in text]
    packet_complete = bool(path.exists() and not missing_decision_ids and not missing_required_snippets)
    gate_status = "blocked_missing_human_decisions" if packet_complete and not forbidden_snippet_hits else "failed_human_decision_packet"
    return {
        "audit_id": "sqj_human_decision_packet",
        "boundary": (
            "This gate checks that the SQJ human-decision packet lists required "
            "external inputs without claiming that submission, PDF compilation, "
            "artifact release, school recognition, or final freeze is complete."
        ),
        "packet": path.as_posix(),
        "packet_exists": path.exists(),
        "packet_size_bytes": path.stat().st_size if path.exists() else 0,
        "required_decision_ids": REQUIRED_DECISION_IDS,
        "missing_decision_ids": missing_decision_ids,
        "missing_required_snippets": missing_required_snippets,
        "forbidden_snippet_hits": forbidden_snippet_hits,
        "human_decisions_complete": False,
        "submission_authorized": False,
        "pdf_compile_passed": False,
        "artifact_release_authorized": False,
        "api_call_attempted": False,
        "final_freeze_complete": False,
        "gate_status": gate_status,
        "passed": gate_status == "blocked_missing_human_decisions",
    }


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# SQJ Human Decision Packet Audit",
        "",
        "## Summary",
        "",
        f"- passed: {bool_mark(audit['passed'])}",
        f"- gate status: `{audit['gate_status']}`",
        f"- packet exists: {bool_mark(audit['packet_exists'])}",
        f"- human decisions complete: {bool_mark(audit['human_decisions_complete'])}",
        f"- submission authorized: {bool_mark(audit['submission_authorized'])}",
        f"- PDF compile passed: {bool_mark(audit['pdf_compile_passed'])}",
        f"- artifact release authorized: {bool_mark(audit['artifact_release_authorized'])}",
        f"- API call attempted: {bool_mark(audit['api_call_attempted'])}",
        f"- final freeze complete: {bool_mark(audit['final_freeze_complete'])}",
        f"- missing decision ids: {len(audit['missing_decision_ids'])}",
        f"- missing required snippets: {len(audit['missing_required_snippets'])}",
        f"- forbidden snippet hits: {len(audit['forbidden_snippet_hits'])}",
        "",
        "## Boundary",
        "",
        audit["boundary"],
        "",
    ]
    if audit["missing_decision_ids"]:
        lines.extend(["## Missing Decision IDs", ""])
        for decision_id in audit["missing_decision_ids"]:
            lines.append(f"- `{decision_id}`")
        lines.append("")
    if audit["missing_required_snippets"]:
        lines.extend(["## Missing Required Snippets", ""])
        for snippet in audit["missing_required_snippets"]:
            lines.append(f"- `{snippet}`")
        lines.append("")
    if audit["forbidden_snippet_hits"]:
        lines.extend(["## Forbidden Snippet Hits", ""])
        for snippet in audit["forbidden_snippet_hits"]:
            lines.append(f"- `{snippet}`")
        lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit the SQJ human-decision packet.")
    parser.add_argument("--packet", default=str(DEFAULT_PACKET))
    parser.add_argument("--out-json", default="outputs/sqj_human_decision_packet/latest.json")
    parser.add_argument("--out-md", default="outputs/sqj_human_decision_packet/latest.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = audit_sqj_human_decision_packet(Path(args.packet))
    write_json(Path(args.out_json), audit)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(audit), encoding="utf-8")
    print(json.dumps({"out_json": args.out_json, "out_md": args.out_md, "passed": audit["passed"], "gate_status": audit["gate_status"]}, indent=2))
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
