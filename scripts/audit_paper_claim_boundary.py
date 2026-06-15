from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = REPO_ROOT / "data" / "reviews" / "evp7_g5_llm_376_full_summary.json"
DEFAULT_QUALITY = REPO_ROOT / "data" / "reviews" / "evp7_g5_376_full_quality_audit.json"
DEFAULT_STATISTICS = REPO_ROOT / "data" / "reviews" / "evp7_g5_376_statistical_analysis.json"
DEFAULT_TABLES_MD = REPO_ROOT / "docs" / "paper" / "generated_tables.md"
DEFAULT_PATCH_DRAFT = REPO_ROOT / "docs" / "paper" / "patch_verification_draft.md"
DEFAULT_IEEE_DRAFT = REPO_ROOT / "docs" / "paper" / "ieee_submission_draft.tex"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "reviews" / "evp7_g5_376_claim_traceability.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp7_g5_376_claim_traceability.md"

BOUNDARY_CUES = {
    "bounded_pilot": ["bounded", "pilot"],
    "not_scale_generalized": ["not scale-generalized", "does not establish cross-model generality"],
    "no_deterministic_superiority": ["deterministic-baseline superiority", "LLM outperforms the deterministic"],
    "no_e6_strict_superiority": ["E6 strict superiority over E4", "E6 strictly improves over E4"],
    "no_billing_equivalence": ["not an external billing statement", "billing equivalence"],
}
RAW_MARKERS = ("raw_" + "response_text", "prompt_" + "text")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def audit(args: argparse.Namespace) -> dict[str, Any]:
    summary_path = Path(args.summary)
    quality_path = Path(args.quality_audit)
    statistics_path = Path(args.statistics)
    tables_path = Path(args.generated_tables_md)
    patch_draft_path = Path(args.patch_draft)
    ieee_draft_path = Path(args.ieee_draft)

    summary = read_json(summary_path)
    quality = read_json(quality_path)
    statistics = read_json(statistics_path)
    tables_md = read_text(tables_path)
    patch_draft = read_text(patch_draft_path)
    ieee_draft = read_text(ieee_draft_path)

    supported_claims = quality.get("supported_claims", [])
    unsupported_claims = quality.get("unsupported_claims", [])
    if not isinstance(supported_claims, list) or not isinstance(unsupported_claims, list):
        raise ValueError("quality audit must contain supported_claims and unsupported_claims lists")

    supported = [
        claim_record(claim, "supported", summary_path, quality_path, statistics_path, tables_md, patch_draft, ieee_draft)
        for claim in supported_claims
    ]
    unsupported = [
        claim_record(claim, "unsupported", summary_path, quality_path, statistics_path, tables_md, patch_draft, ieee_draft)
        for claim in unsupported_claims
    ]
    cue_checks = {
        name: {
            "passed": any(cue.lower() in ieee_draft.lower() for cue in cues),
            "accepted_cues": cues,
        }
        for name, cues in BOUNDARY_CUES.items()
    }
    checks = [
        check("summary_is_current_376_run", summary.get("quality", {}).get("review_count") == 376),
        check("quality_status_bounded", quality.get("quality_status") == "passed_with_limitations"),
        check("statistics_raw_output_free", statistics.get("raw_output_free_check", {}).get("passed") is True),
        check("all_supported_claims_covered", all(record["coverage"]["all_required_docs"] for record in supported)),
        check("all_unsupported_claims_covered", all(record["coverage"]["all_required_docs"] for record in unsupported)),
        check("all_ieee_boundary_cues_present", all(item["passed"] for item in cue_checks.values())),
    ]
    result = {
        "audit_id": "evp7_g5_376_claim_traceability",
        "boundary": (
            "This audit reads only tracked raw-output-free summaries and paper drafts. "
            "It maps current EVP-7 supported and unsupported claims to evidence files "
            "and paper coverage; it does not read or package raw model responses."
        ),
        "inputs": {
            "summary": repo_relative(summary_path),
            "quality_audit": repo_relative(quality_path),
            "statistics": repo_relative(statistics_path),
            "generated_tables_md": repo_relative(tables_path),
            "patch_draft": repo_relative(patch_draft_path),
            "ieee_draft": repo_relative(ieee_draft_path),
        },
        "evidence_sources": [
            repo_relative(summary_path),
            repo_relative(quality_path),
            repo_relative(statistics_path),
            repo_relative(tables_path),
            repo_relative(patch_draft_path),
            repo_relative(ieee_draft_path),
        ],
        "supported_claims": supported,
        "unsupported_claims": unsupported,
        "ieee_boundary_cues": cue_checks,
        "checks": checks,
        "passed": all(item["passed"] for item in checks),
        "raw_output_free_check": {
            "passed": not contains_raw_markers(
                {
                    "supported": supported,
                    "unsupported": unsupported,
                    "cue_checks": cue_checks,
                    "inputs": [
                        repo_relative(summary_path),
                        repo_relative(quality_path),
                        repo_relative(statistics_path),
                        repo_relative(tables_path),
                        repo_relative(patch_draft_path),
                        repo_relative(ieee_draft_path),
                    ],
                }
            ),
            "checked_for_raw_response_fields": True,
        },
    }
    if not result["passed"]:
        raise SystemExit("claim-boundary traceability audit failed")
    if not result["raw_output_free_check"]["passed"]:
        raise SystemExit("claim-boundary traceability output contains raw-output field markers")
    return result


def claim_record(
    claim: str,
    status: str,
    summary_path: Path,
    quality_path: Path,
    statistics_path: Path,
    tables_md: str,
    patch_draft: str,
    ieee_draft: str,
) -> dict[str, Any]:
    needle = claim.lower()
    coverage = {
        "quality_audit": True,
        "generated_tables_md": needle in tables_md.lower(),
        "patch_draft": coverage_by_keywords(claim, patch_draft),
        "ieee_draft": coverage_by_keywords(claim, ieee_draft),
    }
    return {
        "claim": claim,
        "status": status,
        "evidence_sources": [
            repo_relative(summary_path),
            repo_relative(quality_path),
            repo_relative(statistics_path),
        ],
        "coverage": {
            **coverage,
            "all_required_docs": all(coverage.values()),
        },
    }


def coverage_by_keywords(claim: str, text: str) -> bool:
    text_lower = text.lower()
    claim_lower = claim.lower()
    if claim_lower in text_lower:
        return True
    keyword_sets = [
        ("raw-output-free", "real deepseek"),
        ("evidence-level", "variation"),
        ("zero observed false accepts", "accepted precision"),
        ("correct recall", "evidence gain"),
        ("scale-generalized",),
        ("deterministic", "baseline"),
        ("e6", "strict", "e4"),
        ("billing", "statement"),
    ]
    claim_tokens = claim_lower.replace("-", " ").split()
    for keywords in keyword_sets:
        if all(keyword in claim_lower for keyword in keywords) and all(keyword in text_lower for keyword in keywords):
            return True
        normalized_keywords = [keyword.replace("-", " ") for keyword in keywords]
        if all(keyword in " ".join(claim_tokens) for keyword in normalized_keywords) and all(
            keyword in text_lower.replace("-", " ") for keyword in normalized_keywords
        ):
            return True
    return False


def check(name: str, passed: bool) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed)}


def contains_raw_markers(value: Any) -> bool:
    serialized = json.dumps(value, ensure_ascii=False)
    return any(marker in serialized for marker in RAW_MARKERS)


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# EVP-7 G5 376-Record Claim Traceability",
        "",
        result["boundary"],
        "",
        "## Summary",
        "",
        f"- passed: {bool_mark(result['passed'])}",
        f"- raw-output-free check passed: {bool_mark(result['raw_output_free_check']['passed'])}",
        "",
        "## Checks",
        "",
        "| check | passed |",
        "|---|---:|",
    ]
    for item in result["checks"]:
        lines.append(f"| `{item['check']}` | {str(item['passed']).lower()} |")
    lines.extend(
        [
            "",
            "## Supported Claims",
            "",
            "| claim | generated tables | markdown draft | IEEE draft | evidence sources |",
            "|---|---:|---:|---:|---|",
        ]
    )
    for record in result["supported_claims"]:
        lines.append(claim_row(record))
    lines.extend(
        [
            "",
            "## Unsupported Claims",
            "",
            "| claim | generated tables | markdown draft | IEEE draft | evidence sources |",
            "|---|---:|---:|---:|---|",
        ]
    )
    for record in result["unsupported_claims"]:
        lines.append(claim_row(record))
    lines.extend(
        [
            "",
            "## IEEE Boundary Cues",
            "",
            "| cue | passed | accepted cues |",
            "|---|---:|---|",
        ]
    )
    for name, cue in result["ieee_boundary_cues"].items():
        lines.append(f"| `{name}` | {str(cue['passed']).lower()} | `{json.dumps(cue['accepted_cues'])}` |")
    lines.append("")
    return "\n".join(lines)


def claim_row(record: dict[str, Any]) -> str:
    coverage = record["coverage"]
    sources = ", ".join(f"`{source}`" for source in record["evidence_sources"])
    return (
        f"| {record['claim']} | {str(coverage['generated_tables_md']).lower()} | "
        f"{str(coverage['patch_draft']).lower()} | {str(coverage['ieee_draft']).lower()} | {sources} |"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit EVP-7 paper claim-boundary traceability.")
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--quality-audit", type=Path, default=DEFAULT_QUALITY)
    parser.add_argument("--statistics", type=Path, default=DEFAULT_STATISTICS)
    parser.add_argument("--generated-tables-md", type=Path, default=DEFAULT_TABLES_MD)
    parser.add_argument("--patch-draft", type=Path, default=DEFAULT_PATCH_DRAFT)
    parser.add_argument("--ieee-draft", type=Path, default=DEFAULT_IEEE_DRAFT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = audit(args)
    write_json(args.json_out, result)
    write_text(args.md_out, render_markdown(result))
    print(
        json.dumps(
            {
                "out_json": repo_relative(args.json_out),
                "out_md": repo_relative(args.md_out),
                "passed": result["passed"],
                "raw_output_free": result["raw_output_free_check"]["passed"],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
