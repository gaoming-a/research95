from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_HANDOFF = Path("docs/artifact/submission_handoff_20260618.md")
NEXT_DECISION_PACKET = Path("docs/experiments/evp7_next_decision_packet_20260618.md")

REQUIRED_SNIPPETS = [
    "This handoff records the current no-API submission state.",
    "It does not authorize\nnew model calls, cohort expansion, or evidence-level changes.",
    "Supported claim: bounded evidence-visibility pilot observations.",
    "Structural/no-API cohort: 21 tasks, 6 projects, 98 candidates, 392",
    "Paper-facing real DeepSeek G5 run: 20 tasks, 94 candidates, 376 records.",
    "Evidence levels: E0/E2/E4/E6 only.",
    "E1/E3/E5 are future EVP-8 /\n  EVP-7-v2 work",
    "the old prompt-only evidence-first gate remains\n  `stop_or_redesign`",
    "Use `docs/experiments/evp7_next_decision_packet_20260618.md` before any\nexperimental continuation.",
    "continue only no-API paper-submission maintenance;",
    "no second-model API calls;",
    "no cohort expansion;",
    "no E1/E3/E5 insertion;",
    "no new verifier design run;",
    "no claim that the LLM beats deterministic tool-only baselines.",
]

FORBIDDEN_SNIPPETS = [
    "E1/E3/E5 are current EVP-7",
    "full E0-E6 ladder is current EVP-7",
    "second-model API calls are allowed",
    "cohort expansion is allowed",
    "The LLM beats deterministic tool-only baselines",
    "claim that the LLM beats deterministic tool-only baselines is supported",
]


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def audit_handoff(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    missing_snippets = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
    forbidden_hits = [snippet for snippet in FORBIDDEN_SNIPPETS if snippet in text]
    result = {
        "handoff_path": path.as_posix(),
        "handoff_exists": path.exists(),
        "next_decision_packet": NEXT_DECISION_PACKET.as_posix(),
        "next_decision_packet_exists": NEXT_DECISION_PACKET.exists(),
        "missing_required_snippets": missing_snippets,
        "forbidden_snippet_hits": forbidden_hits,
    }
    result["passed"] = bool(
        result["handoff_exists"]
        and result["next_decision_packet_exists"]
        and not missing_snippets
        and not forbidden_hits
    )
    return result


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# Submission Handoff Audit",
        "",
        "## Summary",
        "",
        f"- passed: {bool_mark(audit['passed'])}",
        f"- handoff exists: {bool_mark(audit['handoff_exists'])}",
        f"- next decision packet exists: {bool_mark(audit['next_decision_packet_exists'])}",
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
            "This audit checks the tracked no-API submission handoff contract. It does not call model APIs, expand the cohort, or validate ignored generated artifacts.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit the no-API submission handoff boundary.")
    parser.add_argument("--handoff", default=str(DEFAULT_HANDOFF))
    parser.add_argument("--out-json", default="outputs/submission_handoff_audit/latest.json")
    parser.add_argument("--out-md", default="outputs/submission_handoff_audit/latest.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = audit_handoff(Path(args.handoff))
    write_json(Path(args.out_json), audit)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(audit), encoding="utf-8")
    print(json.dumps({"out_json": args.out_json, "out_md": args.out_md, "passed": audit["passed"]}, indent=2))
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
