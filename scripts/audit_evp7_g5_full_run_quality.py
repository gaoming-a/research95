"""Audit the tracked EVP-7 G5 full-run summary without reading raw outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = REPO_ROOT / "data" / "reviews" / "evp7_g5_llm_full_run_summary.json"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "reviews" / "evp7_g5_full_run_quality_audit.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp7_g5_full_run_quality_audit.md"

EXPECTED_REVIEW_COUNT = 200
EXPECTED_CANDIDATES_PER_LEVEL = 50
EXPECTED_INVALID_COUNT = 1
EXPECTED_INVALID_RATE = 0.005


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def build_audit(summary: dict[str, Any]) -> dict[str, Any]:
    quality = summary["quality"]
    metrics = summary["metrics"]
    groups = metrics["metric_groups"]

    checks = [
        _check("review_count", quality.get("review_count") == EXPECTED_REVIEW_COUNT, quality.get("review_count")),
        _check("unique_review_ids", quality.get("unique_review_ids") == EXPECTED_REVIEW_COUNT, quality.get("unique_review_ids")),
        _check("raw_outputs_not_tracked", quality.get("raw_outputs_tracked") is False, quality.get("raw_outputs_tracked")),
        _check("invalid_output_count", quality.get("invalid_output_count") == EXPECTED_INVALID_COUNT, quality.get("invalid_output_count")),
        _check("invalid_output_rate", quality.get("invalid_output_rate") == EXPECTED_INVALID_RATE, quality.get("invalid_output_rate")),
        _check(
            "g5_signal_observed",
            metrics.get("g5_signal_claim_status") == "real_llm_verifier_signal_observed_on_evp7",
            metrics.get("g5_signal_claim_status"),
        ),
    ]
    for level in ("E0", "E2", "E4", "E6"):
        group = groups[level]
        checks.append(_check(f"{level}_record_count", group.get("record_count") == EXPECTED_CANDIDATES_PER_LEVEL, group.get("record_count")))
    for level in ("E4", "E6"):
        group = groups[level]
        checks.extend(
            [
                _check(f"{level}_false_accept_rate_zero", group.get("false_accept_rate") == 0.0, group.get("false_accept_rate")),
                _check(f"{level}_accepted_precision_one", group.get("accepted_precision") == 1.0, group.get("accepted_precision")),
                _check(f"{level}_correct_recall_positive", float(group.get("correct_recall") or 0.0) > 0.0, group.get("correct_recall")),
                _check(f"{level}_evidence_gain_positive", float(group.get("evidence_gain_vs_e0") or 0.0) > 0.0, group.get("evidence_gain_vs_e0")),
            ]
        )

    return {
        "audit_id": "evp7_g5_200_quality_audit",
        "cohort_id": summary.get("cohort_id"),
        "input_summary": _display(DEFAULT_SUMMARY),
        "api_call_attempted": False,
        "raw_outputs_read": False,
        "raw_outputs_tracked": quality.get("raw_outputs_tracked"),
        "quality_status": "passed_with_limitations" if all(item["passed"] for item in checks) else "not_passed",
        "checks": checks,
        "supported_claims": [
            "The current EVP-7 9-task/50-candidate/200-packet run observed evidence-visibility signal in real DeepSeek verifier outputs.",
            "E4/E6 preserved zero observed false accepts and accepted precision 1.0.",
            "E4/E6 improved correct recall over E0 and produced positive Evidence Gain versus E0.",
        ],
        "unsupported_claims": [
            "Scale-generalized paper claims beyond EVP-7.",
            "A claim that the LLM outperforms the deterministic visible-test tool-only baseline.",
            "A claim that E6 strictly improves over E4 in this run.",
            "A claim that DeepSeek cost is known from runner output.",
        ],
        "limitations": [
            "One E4 record is schema-invalid.",
            "E4 correct recall is 0.111111 and E6 correct recall is 0.222222, below the deterministic visible-test tool-only baseline recall of 0.888889.",
            "Runner-reported cost is 0.0 because DeepSeek response usage did not expose billable cost in the stored field.",
            "The cohort remains a pilot-scale 9-task BugsInPy slice.",
        ],
    }


def _check(name: str, passed: bool, observed: Any) -> dict[str, Any]:
    return {"check": name, "passed": passed, "observed": observed}


def render_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# EVP-7 G5 Full-Run Quality Audit",
        "",
        "This audit reads only the tracked raw-output-free full-run summary. It does not read or copy raw model responses.",
        "",
        "## Status",
        "",
        f"- Quality status: `{audit['quality_status']}`",
        f"- API call attempted by audit: {str(audit['api_call_attempted']).lower()}",
        f"- Raw outputs read by audit: {str(audit['raw_outputs_read']).lower()}",
        f"- Raw outputs tracked: {str(audit['raw_outputs_tracked']).lower()}",
        "",
        "## Checks",
        "",
        "| Check | Passed | Observed |",
        "| --- | --- | --- |",
    ]
    for check in audit["checks"]:
        lines.append(f"| `{check['check']}` | {str(check['passed']).lower()} | `{check['observed']}` |")

    lines.extend(["", "## Supported Claims", ""])
    lines.extend(f"- {claim}" for claim in audit["supported_claims"])
    lines.extend(["", "## Unsupported Claims", ""])
    lines.extend(f"- {claim}" for claim in audit["unsupported_claims"])
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in audit["limitations"])
    lines.append("")
    return "\n".join(lines)


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _display(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    summary = read_json(args.summary)
    audit = build_audit(summary)
    write_json(args.json_out, audit)
    write_text(args.md_out, render_markdown(audit))
    print(json.dumps(audit, ensure_ascii=False, sort_keys=True))
    if args.check and audit["quality_status"] != "passed_with_limitations":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
