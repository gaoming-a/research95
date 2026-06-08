from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            value = json.loads(stripped)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number} is not a JSON object")
            records.append(value)
    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def index_by(records: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for record in records:
        value = str(record[key])
        if value in indexed:
            raise ValueError(f"duplicate {key}: {value}")
        indexed[value] = record
    return indexed


def claim(patch_id: str, verifier_id: str, text: str, evidence: list[str], status: str) -> dict[str, Any]:
    return {
        "claim_id": f"{patch_id}__{verifier_id}__claim_001",
        "claim": text,
        "evidence": evidence,
        "evidence_status": status,
    }


def apply_only_decision(validation: dict[str, Any]) -> tuple[str, str, list[str], str]:
    if not validation.get("patch_applied"):
        return (
            "reject",
            "Patch does not apply cleanly.",
            ["patch_apply.applied=false"],
            "visible_tool_rule",
        )
    return (
        "escalate",
        "Patch applies, but patch-apply evidence alone is insufficient for merge acceptance.",
        ["patch_apply.applied=true"],
        "visible_tool_rule",
    )


def validation_summary_decision(validation: dict[str, Any]) -> tuple[str, str, list[str], str]:
    if not validation.get("patch_applied"):
        return (
            "reject",
            "Patch does not apply cleanly.",
            ["patch_apply.applied=false"],
            "validation_summary_rule",
        )
    if not validation.get("oracle_ran"):
        return (
            "escalate",
            "Patch applies, but executable validation did not run.",
            ["patch_apply.applied=true", "oracle_execution.ran=false"],
            "validation_summary_rule",
        )
    if validation.get("oracle_passed"):
        return (
            "accept",
            "Patch applies and all retained executable validation checks passed.",
            ["patch_apply.applied=true", "oracle_execution.passed=true"],
            "validation_summary_rule",
        )
    return (
        "reject",
        "Patch applies but retained executable validation reported failing behavior.",
        ["patch_apply.applied=true", "oracle_execution.passed=false"],
        "validation_summary_rule",
    )


def build_records(candidates: list[dict[str, Any]], validations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    validations_by_patch_id = index_by(validations, "patch_id")
    records: list[dict[str, Any]] = []
    rules = [
        ("tool_only_apply_only", "no_api_tool_only_apply_only", apply_only_decision),
        (
            "tool_only_validation_summary",
            "no_api_tool_only_validation_summary",
            validation_summary_decision,
        ),
    ]
    for candidate in candidates:
        patch_id = str(candidate["patch_id"])
        if patch_id not in validations_by_patch_id:
            raise ValueError(f"missing validation record for patch_id: {patch_id}")
        validation = validations_by_patch_id[patch_id]
        for verifier_id, condition, decision_fn in rules:
            decision, text, evidence, evidence_status = decision_fn(validation)
            records.append(
                {
                    "patch_id": patch_id,
                    "model_candidate_id": candidate.get("model_candidate_id"),
                    "verifier_id": verifier_id,
                    "condition": condition,
                    "decision": decision,
                    "confidence": 1.0,
                    "claims": [claim(patch_id, verifier_id, text, evidence, evidence_status)],
                    "raw_response_path": None,
                    "cost_usd": 0.0,
                    "invalid_reason": None,
                }
            )
    return records


def build_summary(records: list[dict[str, Any]], validation_records: list[dict[str, Any]]) -> dict[str, Any]:
    decision_counts_by_condition: dict[str, dict[str, int]] = {}
    for condition in sorted({str(record["condition"]) for record in records}):
        decision_counts_by_condition[condition] = dict(
            sorted(Counter(str(record["decision"]) for record in records if record["condition"] == condition).items())
        )
    return {
        "record_count": len(records),
        "conditions": sorted({str(record["condition"]) for record in records}),
        "decision_counts_by_condition": decision_counts_by_condition,
        "validation_record_count": len(validation_records),
        "boundary": {
            "tool_only_apply_only": (
                "Uses only patch-apply status. It is a realistic but weak visible-tool baseline; "
                "clean application alone is not enough to accept a patch."
            ),
            "tool_only_validation_summary": (
                "Uses retained executable validation summary from the current pilot. It is a "
                "tool-summary/oracle-style baseline for this pilot and must not be described as "
                "a hidden-evaluator-free realistic merge gate until visible and hidden tests are separated."
            ),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build deterministic tool-only patch-verification baselines.")
    parser.add_argument("--candidates", default="outputs/patch_verification_pilot_001/candidates.jsonl")
    parser.add_argument("--validation", default="outputs/patch_verification_pilot_001/validation.jsonl")
    parser.add_argument("--out", default="outputs/tool_only_baseline/tool_only_verifier_outputs.jsonl")
    parser.add_argument("--summary-out", default="outputs/tool_only_baseline/tool_only_summary.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candidates = read_jsonl(Path(args.candidates))
    validations = read_jsonl(Path(args.validation))
    records = build_records(candidates, validations)
    write_jsonl(Path(args.out), records)
    summary = build_summary(records, validations)
    write_json(Path(args.summary_out), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
