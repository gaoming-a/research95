from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_SOURCE_ROOT = Path("..") / "research" / "data" / "real_bugs" / "bugsinpy_workspace"


def run_step(command: list[str]) -> None:
    print(f"\n$ {' '.join(command)}", flush=True)
    subprocess.run(command, check=True)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def count_jsonl(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require_gate(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"pipeline gate failed: {message}")


def build_dry_run_config(out_dir: Path, dry_run_dir: Path, config_path: Path) -> None:
    write_json(
        config_path,
        {
            "run_id": f"{out_dir.name}_dry_run",
            "model": "<openrouter-model-slug>",
            "conditions": ["llm_only", "evidence_first"],
            "temperature": 0.0,
            "max_tokens": 1200,
            "smoke_limit": 0,
            "candidates": (out_dir / "candidates.jsonl").as_posix(),
            "evidence_packets": (out_dir / "evidence_packets.jsonl").as_posix(),
            "validation_summary": (out_dir / "validation_summary.json").as_posix(),
            "out_dir": dry_run_dir.as_posix(),
            "env": ".env",
        },
    )


def validate_outputs(out_dir: Path, dry_run_dir: Path) -> dict[str, Any]:
    dataset_summary = read_json(out_dir / "dataset_summary.json")
    validation_summary = read_json(out_dir / "validation_summary.json")
    metrics = read_json(out_dir / "metrics.json")
    prompt_count = count_jsonl(dry_run_dir / "prompt_manifest.jsonl")

    require_gate(dataset_summary.get("candidate_count") == 30, "candidate_count must be 30")
    require_gate(dataset_summary.get("verifier_output_count") == 90, "verifier_output_count must be 90")
    require_gate(
        bool(dataset_summary.get("api_readiness", {}).get("ready")),
        "dataset api_readiness.ready must be true",
    )
    require_gate(bool(validation_summary.get("all_validated")), "candidate validation must pass")
    require_gate(metrics.get("candidate_count") == 30, "metrics candidate_count must be 30")
    require_gate(metrics.get("verifier_output_count") == 90, "metrics verifier_output_count must be 90")
    require_gate(prompt_count == 60, "prompt dry-run must render 60 prompts")

    return {
        "out_dir": out_dir.as_posix(),
        "dry_run_dir": dry_run_dir.as_posix(),
        "candidate_count": dataset_summary["candidate_count"],
        "verifier_output_count": dataset_summary["verifier_output_count"],
        "prompt_count": prompt_count,
        "all_validated": validation_summary["all_validated"],
        "api_readiness": dataset_summary["api_readiness"],
        "report": (out_dir / "pilot_report.md").as_posix(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the complete no-API patch-verification pipeline.")
    parser.add_argument(
        "--out-dir",
        default="outputs/patch_verification_pilot_001",
        help="Output directory for dataset, metrics, validation, and report files.",
    )
    parser.add_argument(
        "--source-workspace-root",
        default=str(DEFAULT_SOURCE_ROOT),
        help="Root containing retained BugsInPy buggy/fixed checkouts.",
    )
    parser.add_argument(
        "--dry-run-dir",
        help="Prompt dry-run output directory. Defaults to <out-dir>/api_prompt_dry_run.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    dry_run_dir = Path(args.dry_run_dir) if args.dry_run_dir else out_dir / "api_prompt_dry_run"
    source_root = Path(args.source_workspace_root)
    config_path = out_dir / "api_pilot_dry_run_config.json"

    run_step(
        [
            sys.executable,
            "scripts/build_patch_verification_dataset.py",
            "--out-dir",
            str(out_dir),
            "--source-workspace-root",
            str(source_root),
        ]
    )
    run_step(
        [
            sys.executable,
            "scripts/analyze_patch_verification.py",
            "--candidates",
            str(out_dir / "candidates.jsonl"),
            "--verifier-outputs",
            str(out_dir / "verifier_outputs.jsonl"),
            "--out",
            str(out_dir / "metrics.json"),
        ]
    )
    run_step(
        [
            sys.executable,
            "scripts/validate_patch_candidates.py",
            "--candidates",
            str(out_dir / "candidates.jsonl"),
            "--source-workspace-root",
            str(source_root),
            "--workdir-root",
            str(out_dir / "workdirs"),
            "--out",
            str(out_dir / "validation.jsonl"),
            "--summary-out",
            str(out_dir / "validation_summary.json"),
        ]
    )

    build_dry_run_config(out_dir, dry_run_dir, config_path)
    run_step(
        [
            sys.executable,
            "scripts/preflight_api_pilot.py",
            "--config",
            str(config_path),
            "--allow-missing-credentials",
        ]
    )
    run_step(
        [
            sys.executable,
            "scripts/run_patch_verification_api_pilot.py",
            "--config",
            str(config_path),
            "--dry-run",
        ]
    )
    run_step(
        [
            sys.executable,
            "scripts/summarize_patch_verification_pilot.py",
            "--dataset-summary",
            str(out_dir / "dataset_summary.json"),
            "--validation-summary",
            str(out_dir / "validation_summary.json"),
            "--metrics",
            str(out_dir / "metrics.json"),
            "--prompt-manifest",
            str(dry_run_dir / "prompt_manifest.jsonl"),
            "--out",
            str(out_dir / "pilot_report.md"),
        ]
    )

    summary = validate_outputs(out_dir, dry_run_dir)
    write_json(out_dir / "pipeline_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
