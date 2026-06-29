"""Audit the no-API realistic agent-patch generation dry-run.

The dry-run output directory is ignored. This script reads only the prompt
manifest hashes and aggregate summary, then writes tracked JSON/Markdown
without prompt text, patch diffs, raw responses, or provider response objects.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DRY_RUN_DIR = REPO_ROOT / "outputs" / "evp8_realistic_agent_generation_dryrun_primary_001"
TARGET_MATRIX = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_source_target_matrix_v0_1.json"
DEFAULT_JSON_OUT = REPO_ROOT / "data" / "protocols" / "evp8_realistic_agent_generation_dry_run_audit_v0_1.json"
DEFAULT_MD_OUT = REPO_ROOT / "docs" / "experiments" / "evp8_realistic_agent_generation_dry_run_audit_v0_1.md"

FORBIDDEN_PROMPT_MANIFEST_KEYS = {
    "prompt",
    "prompt_text",
    "rendered_prompt",
    "patch_text",
    "raw_response",
    "provider_response",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{display_path(path)} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{display_path(path)}:{line_no} must contain a JSON object")
        rows.append(value)
    return rows


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def display_path(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def version_from_path(path: Path) -> str:
    if "_v0_" in path.stem:
        suffix = path.stem.rsplit("_v0_", 1)[1].split("_", 1)[0]
        return f"v0.{suffix}"
    return "v0.1"


def check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def parse_expected_task_counts(values: list[str] | None) -> dict[str, int] | None:
    if not values:
        return None
    counts: dict[str, int] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"expected task count must use task_id=count format: {value}")
        task_id, raw_count = value.split("=", 1)
        counts[task_id] = int(raw_count)
    return dict(sorted(counts.items()))


def audit(
    dry_run_dir: Path,
    expected_prompt_count_override: int | None = None,
    expected_task_counts_override: dict[str, int] | None = None,
) -> dict[str, Any]:
    target_matrix = read_json(TARGET_MATRIX)
    summary_path = dry_run_dir / "generation_summary.json"
    prompt_manifest_path = dry_run_dir / "prompt_manifest.jsonl"
    summary = read_json(summary_path)
    prompts = read_jsonl(prompt_manifest_path)
    target_tasks = {row["task_id"]: row for row in target_matrix["targets"]}
    task_counts = Counter(str(row.get("task_id")) for row in prompts)
    variant_pairs = {(str(row.get("task_id")), int(row.get("variant_index", 0))) for row in prompts}
    forbidden_keys = sorted({key for row in prompts for key in row if key in FORBIDDEN_PROMPT_MANIFEST_KEYS})
    label_checks = Counter(str(row.get("label_leakage_check") or "missing") for row in prompts)
    prompt_hash_missing = sum(1 for row in prompts if not row.get("prompt_sha256"))
    prompt_chars_missing = sum(1 for row in prompts if not row.get("prompt_chars"))
    expected_prompt_count = expected_prompt_count_override or int(target_matrix["target_summary"]["planned_generation_slots"])
    expected_task_counts = expected_task_counts_override or {
        task_id: int(row["planned_generation_slots"]) for task_id, row in target_tasks.items()
    }
    raw_dir = dry_run_dir / "raw"
    candidates_pending = dry_run_dir / "candidates.pending.jsonl"
    evidence_pending = dry_run_dir / "evidence_packets.pending.jsonl"
    checks = [
        check("target_matrix_passed", target_matrix.get("target_matrix_status") == "passed", target_matrix.get("target_matrix_status")),
        check("dry_run_summary_declares_dry_run", summary.get("dry_run") is True, summary.get("dry_run")),
        check("api_call_not_attempted", summary.get("dry_run") is True, False),
        check("patch_generation_not_attempted", int(summary.get("candidate_count", -1)) == 0, summary.get("candidate_count")),
        check("prompt_count_matches_target", len(prompts) == expected_prompt_count, {"actual": len(prompts), "expected": expected_prompt_count}),
        check("summary_prompt_count_matches_manifest", int(summary.get("prompt_count", -1)) == len(prompts), summary.get("prompt_count")),
        check("target_task_coverage_complete", set(task_counts) == set(expected_task_counts), sorted(task_counts)),
        check("per_task_variant_counts_match", dict(task_counts) == expected_task_counts, dict(task_counts)),
        check("variant_pairs_unique", len(variant_pairs) == len(prompts), len(variant_pairs)),
        check("label_leakage_checks_passed", label_checks == Counter({"passed": len(prompts)}), dict(label_checks)),
        check("prompt_hash_present_for_all", prompt_hash_missing == 0, prompt_hash_missing),
        check("prompt_char_count_present_for_all", prompt_chars_missing == 0, prompt_chars_missing),
        check("forbidden_prompt_manifest_keys_absent", not forbidden_keys, forbidden_keys),
        check("raw_response_dir_absent", not raw_dir.exists(), display_path(raw_dir)),
        check("candidates_pending_absent_or_empty", (not candidates_pending.exists()) or candidates_pending.stat().st_size == 0, display_path(candidates_pending)),
        check("evidence_packets_pending_absent_or_empty", (not evidence_pending.exists()) or evidence_pending.stat().st_size == 0, display_path(evidence_pending)),
    ]
    return {
        "analysis_id": "evp8_realistic_agent_generation_dry_run_audit_v0_1",
        "date": "2026-06-29",
        "scope": {
            "api_call_attempted": False,
            "raw_model_outputs_read": False,
            "prompt_text_stored": False,
            "patch_text_stored": False,
            "candidate_manifest_created": False,
        },
        "inputs": {
            "dry_run_dir": display_path(dry_run_dir),
            "generation_summary": display_path(summary_path),
            "prompt_manifest": display_path(prompt_manifest_path),
            "target_matrix": display_path(TARGET_MATRIX),
        },
        "summary": {
            "run_id": summary.get("run_id"),
            "model": summary.get("model"),
            "api_provider": summary.get("api_provider"),
            "prompt_version": summary.get("prompt_version"),
            "prompt_count": len(prompts),
            "candidate_count": summary.get("candidate_count"),
            "task_counts": dict(sorted(task_counts.items())),
        },
        "checks": checks,
        "audit_status": "passed" if all(row["passed"] for row in checks) else "failed",
        "next_gate": (
            "Explicit generation API authorization is required before replacing --dry-run with --execute. "
            "Generated candidates must then be validated and relabeled before any realistic verifier cohort is built."
        ),
    }


def write_markdown(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = result["summary"]
    version = version_from_path(path)
    lines = [
        f"# EVP-8 Realistic Agent Generation Dry-Run Audit {version}",
        "",
        "Date: 2026-06-29",
        "",
        "This audit summarizes the no-API generation dry-run. It stores prompt",
        "hash/count metadata only, not prompt text, patch diffs, raw responses, or",
        "provider response objects.",
        "",
        "## Summary",
        "",
        f"- audit status: `{result['audit_status']}`",
        f"- run id: `{summary['run_id']}`",
        f"- model: `{summary['model']}`",
        f"- provider: `{summary['api_provider']}`",
        f"- prompt version: `{summary['prompt_version']}`",
        f"- prompt count: {summary['prompt_count']}",
        f"- candidate count: {summary['candidate_count']}",
        "",
        "Task prompt counts:",
        "",
    ]
    for task_id, count in summary["task_counts"].items():
        lines.append(f"- `{task_id}`: {count}")
    lines += [
        "",
        "## Checks",
        "",
    ]
    for row in result["checks"]:
        lines.append(f"- {row['check']}: {'passed' if row['passed'] else 'failed'} ({row['detail']})")
    lines += [
        "",
        "## Next Gate",
        "",
        result["next_gate"],
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run-dir", type=Path, default=DEFAULT_DRY_RUN_DIR)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--expected-prompt-count", type=int, default=None)
    parser.add_argument("--expected-task-count", action="append", default=None)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = audit(
        args.dry_run_dir,
        expected_prompt_count_override=args.expected_prompt_count,
        expected_task_counts_override=parse_expected_task_counts(args.expected_task_count),
    )
    write_json(args.out_json, result)
    write_markdown(args.out_md, result)
    if args.check and result["audit_status"] != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
