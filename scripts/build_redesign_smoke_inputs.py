from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


DEFAULT_CANDIDATE_IDS = [
    "candidate_0001",
    "candidate_0005",
    "candidate_0006",
    "candidate_0020",
    "candidate_0023",
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number} must contain a JSON object")
        rows.append(value)
    return rows


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def index_by(records: list[dict[str, Any]], field: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for record in records:
        key = str(record[field])
        if key in indexed:
            raise ValueError(f"duplicate {field}: {key}")
        indexed[key] = record
    return indexed


def sanitize_text(text: Any, max_chars: int = 1200) -> str:
    value = str(text or "").replace("\r\n", "\n").replace("\\", "/")
    value = re.sub(r"[A-Za-z]:/[^ \n\r\t]+/research95/", "<repo>/", value)
    value = re.sub(r"[A-Za-z]:/[^ \n\r\t]+/outputs/", "<outputs>/", value)
    value = re.sub(r"<repo>/outputs/patch_verification_pilot_001/workdirs/[^/]+/", "<candidate_workdir>/", value)
    value = re.sub(r"<repo>/", "<repo>/", value)
    value = value.strip()
    if len(value) > max_chars:
        return value[: max_chars - 15].rstrip() + "\n...[truncated]"
    return value


def tool_check_name(oracle_path: str, index: int) -> str:
    stem = Path(oracle_path).stem
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", stem)
    return f"behavior_check_{index}_{safe}"


def summarize_validation(record: dict[str, Any]) -> dict[str, Any]:
    oracle_results = []
    for index, result in enumerate(record.get("oracle_result", {}).get("results", []), start=1):
        oracle_results.append(
            {
                "check": tool_check_name(str(result.get("oracle_path", "unknown")), index),
                "passed": bool(result.get("passed")),
                "exit_code": result.get("exit_code"),
                "stdout_tail": sanitize_text(result.get("stdout_tail", ""), max_chars=500),
                "stderr_tail": sanitize_text(result.get("stderr_tail", ""), max_chars=900),
            }
        )
    return {
        "tool_evidence_version": "tool_evidence_summary_v1",
        "patch_apply": {
            "applied": bool(record.get("patch_applied")),
            "exit_code": record.get("patch_result", {}).get("exit_code"),
            "stderr_tail": sanitize_text(record.get("patch_result", {}).get("stderr_tail", ""), max_chars=600),
        },
        "oracle_execution": {
            "ran": bool(record.get("oracle_ran")),
            "all_checks_passed": bool(record.get("oracle_passed")),
            "checks": oracle_results,
        },
        "interpretation_boundary": (
            "These are tool execution outcomes visible to the verifier. They are not evaluator labels, "
            "but this condition must be reported separately from prompt-only review."
        ),
    }


def build_records(args: argparse.Namespace) -> dict[str, Any]:
    candidates = read_jsonl(Path(args.candidates))
    evidence_packets = read_jsonl(Path(args.evidence_packets))
    validations = read_jsonl(Path(args.validation))

    candidates_by_id = index_by(candidates, "model_candidate_id")
    evidence_by_id = index_by(evidence_packets, "candidate_id")
    validations_by_id = index_by(validations, "model_candidate_id")

    selected_candidates: list[dict[str, Any]] = []
    selected_evidence: list[dict[str, Any]] = []
    missing: list[str] = []
    for candidate_id in args.candidate_id:
        candidate = candidates_by_id.get(candidate_id)
        evidence = evidence_by_id.get(candidate_id)
        validation = validations_by_id.get(candidate_id)
        if not candidate or not evidence or not validation:
            missing.append(candidate_id)
            continue
        selected_candidates.append(candidate)
        augmented = dict(evidence)
        augmented["evidence_packet_version"] = "tool_augmented_evidence_packet_v1"
        augmented["available_evidence_sources"] = sorted(
            set(augmented.get("available_evidence_sources", []))
            | {"patch_apply_status", "oracle_execution_summary"}
        )
        augmented["label_leakage_guard"] = (
            "evaluator labels remain omitted; this packet includes tool execution summaries for a "
            "separate tool-augmented verifier condition"
        )
        augmented["tool_evidence_summary"] = summarize_validation(validation)
        selected_evidence.append(augmented)

    if missing:
        raise ValueError(f"missing candidate/evidence/validation records for: {missing}")

    summary = {
        "record_count": len(selected_candidates),
        "candidate_ids": list(args.candidate_id),
        "conditions": ["tool_augmented_evidence"],
        "all_validated": all(
            validations_by_id[candidate_id].get("validation_status") == "validated"
            for candidate_id in args.candidate_id
        ),
        "oracle_all_passed_count": sum(
            1 for candidate_id in args.candidate_id if validations_by_id[candidate_id].get("oracle_passed")
        ),
        "oracle_failed_count": sum(
            1 for candidate_id in args.candidate_id if not validations_by_id[candidate_id].get("oracle_passed")
        ),
        "boundary": "This is a failure-case-only tool-augmented redesign smoke input, not a replacement for the full run dataset.",
    }
    return {
        "candidates": selected_candidates,
        "evidence_packets": selected_evidence,
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build tool-augmented failure-case redesign smoke inputs.")
    parser.add_argument("--candidates", default="outputs/patch_verification_pilot_001/candidates.jsonl")
    parser.add_argument("--evidence-packets", default="outputs/patch_verification_pilot_001/evidence_packets.jsonl")
    parser.add_argument("--validation", default="outputs/patch_verification_pilot_001/validation.jsonl")
    parser.add_argument("--out-dir", default="outputs/patch_verification_redesign_smoke_001/inputs")
    parser.add_argument("--candidate-id", action="append", default=list(DEFAULT_CANDIDATE_IDS))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = build_records(args)
    out_dir = Path(args.out_dir)
    candidates_out = out_dir / "candidates.jsonl"
    evidence_out = out_dir / "evidence_packets.jsonl"
    summary_out = out_dir / "validation_summary.json"
    write_jsonl(candidates_out, records["candidates"])
    write_jsonl(evidence_out, records["evidence_packets"])
    write_json(summary_out, records["summary"])
    print(
        json.dumps(
            {
                "candidates": candidates_out.as_posix(),
                "evidence_packets": evidence_out.as_posix(),
                "validation_summary": summary_out.as_posix(),
                "record_count": records["summary"]["record_count"],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
