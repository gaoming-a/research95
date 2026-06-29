from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_SOURCE = Path("docs/paper/sqj_submission_draft.tex")

BLOCKER_SNIPPETS = {
    "anonymous_author": "Anonymous",
    "anonymous_email": "anonymous@example.com",
    "competing_interests_unconfirmed": "This statement must be confirmed before submission.",
    "author_contributions_placeholder": "Author contribution statements are placeholders in this draft",
    "funding_not_specified": "Funding information is not specified in this draft",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def audit_sqj_human_inputs_gate(source: Path = DEFAULT_SOURCE) -> dict[str, Any]:
    text = read_text(source)
    normalized_text = normalize_whitespace(text)
    blocker_hits = {
        name: {
            "snippet": snippet,
            "present": normalize_whitespace(snippet) in normalized_text,
        }
        for name, snippet in BLOCKER_SNIPPETS.items()
    }
    present_blockers = [name for name, state in blocker_hits.items() if state["present"]]
    gate_status = "blocked_missing_human_inputs" if present_blockers else "ready"
    return {
        "audit_id": "sqj_human_inputs_gate",
        "boundary": (
            "This gate checks whether human-supplied SQJ submission metadata is still missing. "
            "It does not infer, generate, or replace author, affiliation, funding, competing-interest, "
            "acknowledgement, or contribution statements."
        ),
        "source": source.as_posix(),
        "source_exists": source.exists(),
        "whitespace_normalized_matching": True,
        "blocker_hits": blocker_hits,
        "present_blockers": present_blockers,
        "gate_status": gate_status,
        "human_inputs_complete": gate_status == "ready",
        "final_freeze_complete": False,
        "passed": source.exists(),
    }


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# SQJ Human Inputs Gate",
        "",
        "## Summary",
        "",
        f"- passed: {bool_mark(audit['passed'])}",
        f"- gate status: `{audit['gate_status']}`",
        f"- source exists: {bool_mark(audit['source_exists'])}",
        f"- human inputs complete: {bool_mark(audit['human_inputs_complete'])}",
        f"- final freeze complete: {bool_mark(audit['final_freeze_complete'])}",
        "",
        "## Blockers",
        "",
    ]
    for name, state in audit["blocker_hits"].items():
        lines.append(f"- `{name}`: {bool_mark(state['present'])}")
    lines.extend(["", "## Boundary", "", audit["boundary"], ""])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit human-supplied SQJ submission metadata blockers.")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--out-json", default="outputs/sqj_human_inputs_gate/latest.json")
    parser.add_argument("--out-md", default="outputs/sqj_human_inputs_gate/latest.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = audit_sqj_human_inputs_gate(Path(args.source))
    write_json(Path(args.out_json), audit)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(audit), encoding="utf-8")
    print(json.dumps({"out_json": args.out_json, "out_md": args.out_md, "passed": audit["passed"], "gate_status": audit["gate_status"]}, indent=2))
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
