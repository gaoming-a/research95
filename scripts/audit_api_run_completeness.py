from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_CANDIDATES = Path("outputs") / "patch_verification_pilot_001" / "candidates.jsonl"


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number} must contain a JSON object")
        rows.append(value)
    return rows


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def raw_paths_state(run_dir: Path, reviews: list[dict[str, Any]]) -> dict[str, Any]:
    missing: list[str] = []
    outside_run_dir: list[str] = []
    invalid_json: list[str] = []
    hash_mismatches: list[dict[str, str | None]] = []
    missing_hashes: list[str] = []
    run_root = run_dir.resolve()
    for record in reviews:
        raw_value = record.get("raw_response_path")
        if not raw_value:
            missing.append("<missing raw_response_path>")
            continue
        raw_path = Path(str(raw_value))
        resolved_raw = raw_path.resolve()
        if run_root not in [resolved_raw, *resolved_raw.parents]:
            outside_run_dir.append(str(raw_value))
        if not raw_path.exists():
            missing.append(str(raw_value))
            continue
        try:
            raw_text = raw_path.read_text(encoding="utf-8")
            json.loads(raw_text)
        except (UnicodeDecodeError, json.JSONDecodeError):
            invalid_json.append(str(raw_value))
            continue
        expected_sha = record.get("raw_response_sha256")
        actual_sha = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
        if not expected_sha:
            missing_hashes.append(str(raw_value))
        elif str(expected_sha) != actual_sha:
            hash_mismatches.append(
                {
                    "raw_response_path": str(raw_value),
                    "expected": str(expected_sha),
                    "actual": actual_sha,
                }
            )
    return {
        "checked": len(reviews),
        "missing": missing,
        "outside_run_dir": outside_run_dir,
        "invalid_json": invalid_json,
        "missing_hashes": missing_hashes,
        "hash_mismatches": hash_mismatches,
        "all_present": not missing,
        "all_under_run_dir": not outside_run_dir,
        "all_valid_json": not invalid_json,
        "all_hashes_present": not missing_hashes,
        "all_hashes_match": not hash_mismatches,
        "run_dir": run_dir.as_posix(),
    }


def review_schema_state(reviews: list[dict[str, Any]]) -> dict[str, Any]:
    required_fields = [
        "patch_id",
        "model_candidate_id",
        "verifier_id",
        "condition",
        "decision",
        "confidence",
        "claims",
        "raw_response_path",
        "raw_response_sha256",
        "model",
        "prompt_version",
        "run_date_utc",
        "usage",
    ]
    allowed_decisions = {"accept", "reject", "escalate", "invalid_output"}
    missing_fields: list[dict[str, Any]] = []
    invalid_decisions: list[dict[str, Any]] = []
    invalid_confidence: list[dict[str, Any]] = []
    for index, record in enumerate(reviews, start=1):
        missing = [field for field in required_fields if field not in record or record.get(field) in (None, "")]
        if missing:
            missing_fields.append({"index": index, "missing": missing})
        if record.get("decision") not in allowed_decisions:
            invalid_decisions.append({"index": index, "decision": record.get("decision")})
        confidence = record.get("confidence")
        if not isinstance(confidence, (int, float)) or not 0.0 <= float(confidence) <= 1.0:
            invalid_confidence.append({"index": index, "confidence": confidence})
    return {
        "required_fields": required_fields,
        "missing_fields": missing_fields,
        "invalid_decisions": invalid_decisions,
        "invalid_confidence": invalid_confidence,
        "passed": not missing_fields and not invalid_decisions and not invalid_confidence,
    }


def build_audit(args: argparse.Namespace) -> dict[str, Any]:
    run_dir = Path(args.run_dir)
    candidates = read_jsonl(Path(args.candidates))
    reviews_path = run_dir / "reviews.jsonl"
    metrics_path = run_dir / "metrics.json"
    run_summary_path = run_dir / "run_summary.md"
    run_error_path = run_dir / "run_error.json"
    reviews = read_jsonl(reviews_path)
    metrics = read_json(metrics_path)
    conditions = list(args.conditions)
    expected_candidates = args.expected_candidates
    if expected_candidates is None and args.default_full:
        expected_candidates = len(candidates)
    expected_records = args.expected_records
    if expected_records is None and expected_candidates is not None:
        expected_records = expected_candidates * len(conditions)

    condition_counts = Counter(str(record.get("condition", "unknown")) for record in reviews)
    candidate_ids = {
        str(record.get("model_candidate_id") or record.get("candidate_id") or "")
        for record in reviews
        if record.get("model_candidate_id") or record.get("candidate_id")
    }
    mock_count = sum(1 for record in reviews if record.get("mock_run"))
    metrics_count = metrics.get("verifier_output_count") if metrics else None
    raw_paths = raw_paths_state(run_dir, reviews)
    review_schema = review_schema_state(reviews)

    checks = {
        "no_run_error_file": not run_error_path.exists(),
        "reviews_file_exists": reviews_path.exists(),
        "metrics_file_exists": metrics_path.exists(),
        "run_summary_exists": run_summary_path.exists(),
        "metrics_count_matches_reviews": metrics_count == len(reviews),
        "expected_record_count_matches": expected_records is None or len(reviews) == expected_records,
        "expected_candidate_count_matches": expected_candidates is None or len(candidate_ids) == expected_candidates,
        "conditions_match_expected": sorted(condition_counts) == sorted(conditions),
        "condition_counts_match_expected_candidates": (
            expected_candidates is None
            or all(condition_counts.get(condition, 0) == expected_candidates for condition in conditions)
        ),
        "mock_boundary_respected": args.allow_mock or mock_count == 0,
        "raw_response_paths_exist": raw_paths["all_present"],
        "raw_response_paths_under_run_dir": raw_paths["all_under_run_dir"],
        "raw_response_json_valid": raw_paths["all_valid_json"],
        "raw_response_hashes_present": raw_paths["all_hashes_present"],
        "raw_response_hashes_match": raw_paths["all_hashes_match"],
        "review_schema_complete": review_schema["passed"],
    }
    return {
        "passed": all(checks.values()),
        "run_dir": run_dir.as_posix(),
        "expected_candidates": expected_candidates,
        "expected_records": expected_records,
        "review_count": len(reviews),
        "unique_reviewed_candidates": len(candidate_ids),
        "metrics_count": metrics_count,
        "mock_review_count": mock_count,
        "run_error_path": run_error_path.as_posix(),
        "conditions": dict(sorted(condition_counts.items())),
        "raw_paths": raw_paths,
        "review_schema": review_schema,
        "checks": checks,
    }


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# API Run Completeness Audit",
        "",
        "## Summary",
        "",
        f"- passed: {bool_mark(audit['passed'])}",
        f"- run dir: `{audit['run_dir']}`",
        f"- expected candidates: {audit['expected_candidates']}",
        f"- expected records: {audit['expected_records']}",
        f"- review count: {audit['review_count']}",
        f"- unique reviewed candidates: {audit['unique_reviewed_candidates']}",
        f"- metrics count: {audit['metrics_count']}",
        f"- mock review count: {audit['mock_review_count']}",
        f"- conditions: `{audit['conditions']}`",
        "",
        "## Checks",
        "",
        "| check | passed |",
        "|---|---:|",
    ]
    for name, passed in audit["checks"].items():
        lines.append(f"| `{name}` | {bool_mark(passed)} |")
    if audit["raw_paths"]["missing"]:
        lines.extend(["", "## Missing Raw Responses", ""])
        for path in audit["raw_paths"]["missing"]:
            lines.append(f"- `{path}`")
    if audit["raw_paths"]["outside_run_dir"]:
        lines.extend(["", "## Raw Responses Outside Run Dir", ""])
        for path in audit["raw_paths"]["outside_run_dir"]:
            lines.append(f"- `{path}`")
    if audit["raw_paths"]["hash_mismatches"]:
        lines.extend(["", "## Raw Response Hash Mismatches", ""])
        for item in audit["raw_paths"]["hash_mismatches"]:
            lines.append(f"- `{item['raw_response_path']}` expected `{item['expected']}` actual `{item['actual']}`")
    if audit["review_schema"]["missing_fields"]:
        lines.extend(["", "## Review Schema Missing Fields", ""])
        for item in audit["review_schema"]["missing_fields"][:20]:
            lines.append(f"- record {item['index']}: `{item['missing']}`")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit API run completeness for smoke or full patch-verification runs.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--candidates", default=str(DEFAULT_CANDIDATES))
    parser.add_argument("--conditions", nargs="+", default=["llm_only", "evidence_first"])
    parser.add_argument("--expected-candidates", type=int)
    parser.add_argument("--expected-records", type=int)
    parser.add_argument("--default-full", action="store_true", help="Expect all candidates if --expected-candidates is omitted.")
    parser.add_argument("--allow-mock", action="store_true", help="Allow mock reviewer records.")
    parser.add_argument("--out-json", help="Defaults to <run-dir>/run_completeness.json.")
    parser.add_argument("--out-md", help="Defaults to <run-dir>/run_completeness.md.")
    parser.add_argument("--require-complete", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = build_audit(args)
    out_json = Path(args.out_json) if args.out_json else Path(args.run_dir) / "run_completeness.json"
    out_md = Path(args.out_md) if args.out_md else Path(args.run_dir) / "run_completeness.md"
    write_json(out_json, audit)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(audit), encoding="utf-8")
    print(json.dumps({"out_json": str(out_json), "out_md": str(out_md), "passed": audit["passed"]}, ensure_ascii=False, indent=2))
    if args.require_complete and not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
