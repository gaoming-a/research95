from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_FREEZE_CANDIDATE = Path("docs/artifact/submission_freeze_candidate_20260618.md")

REQUIRED_SNIPPETS = [
    "This packet records the current no-API freeze candidate",
    "It is not a final freeze decision and does not\nauthorize model calls, cohort expansion, or evidence-level changes.",
    "Paper route: bounded EVP-7 four-anchor evidence-visibility pilot.",
    "Evidence levels: E0/E2/E4/E6 only.",
    "Structural/no-API pipeline: 21 tasks, 6 projects, 98 candidates, and 392",
    "Paper-facing real verifier run: 20 tasks, 94 candidates, and 376 DeepSeek G5",
    "Latest artifact readiness boundary: 303 packaged tracked files, audit",
    "It does not freeze the current 7-page IEEE PDF as the final submission draft.",
    "It does not approve second-model replication.",
    "It does not approve 30-50 bug expansion.",
    "It does not insert E1/E3/E5 into the current EVP-7 artifacts.",
    "It does not claim that the LLM beats the deterministic tool-only baseline.",
    "Before this candidate becomes the final submission package, confirm:",
    "Whether the current 7-page IEEE PDF should be frozen as the submission draft.",
    "If no new decision is given, continue only no-API paper-submission maintenance:",
]

FORBIDDEN_SNIPPETS = [
    "This packet records the final freeze decision",
    "authorizes model calls",
    "authorizes API calls",
    "second-model replication is approved",
    "30-50 bug expansion is approved",
    "E1/E3/E5 are current EVP-7",
    "current 7-page IEEE PDF is frozen as the final submission draft",
    "target venue is confirmed",
    "The LLM beats the deterministic tool-only baseline",
    "claim that the LLM beats the deterministic tool-only baseline is supported",
]


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def audit_freeze_candidate(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    missing_snippets = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
    forbidden_hits = [snippet for snippet in FORBIDDEN_SNIPPETS if snippet in text]
    result = {
        "freeze_candidate_path": path.as_posix(),
        "freeze_candidate_exists": path.exists(),
        "missing_required_snippets": missing_snippets,
        "forbidden_snippet_hits": forbidden_hits,
    }
    result["passed"] = bool(path.exists() and not missing_snippets and not forbidden_hits)
    return result


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# Submission Freeze Candidate Audit",
        "",
        "## Summary",
        "",
        f"- passed: {bool_mark(audit['passed'])}",
        f"- freeze candidate exists: {bool_mark(audit['freeze_candidate_exists'])}",
        f"- missing required snippets: {len(audit['missing_required_snippets'])}",
        f"- forbidden snippet hits: {len(audit['forbidden_snippet_hits'])}",
        "",
    ]
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
    lines.extend(
        [
            "## Boundary",
            "",
            "This audit checks the tracked freeze-candidate package boundary. It does not call model APIs, expand the cohort, alter evidence levels, or validate ignored generated artifacts.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit the no-API submission freeze-candidate boundary.")
    parser.add_argument("--freeze-candidate", default=str(DEFAULT_FREEZE_CANDIDATE))
    parser.add_argument("--out-json", default="outputs/submission_freeze_candidate_audit/latest.json")
    parser.add_argument("--out-md", default="outputs/submission_freeze_candidate_audit/latest.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = audit_freeze_candidate(Path(args.freeze_candidate))
    write_json(Path(args.out_json), audit)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(audit), encoding="utf-8")
    print(json.dumps({"out_json": args.out_json, "out_md": args.out_md, "passed": audit["passed"]}, indent=2))
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
