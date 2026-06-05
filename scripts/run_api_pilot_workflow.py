from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


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


def run_command(command: list[str], allow_failure: bool = False) -> subprocess.CompletedProcess[str]:
    print(f"\n$ {' '.join(command)}", flush=True)
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    if completed.returncode != 0 and not allow_failure:
        raise subprocess.CalledProcessError(completed.returncode, command)
    return completed


def load_preflight(config: Path, allow_missing_credentials: bool) -> dict[str, Any]:
    command = [sys.executable, "scripts/preflight_api_pilot.py", "--config", str(config)]
    if allow_missing_credentials:
        command.append("--allow-missing-credentials")
    completed = run_command(command, allow_failure=True)
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"preflight did not return JSON: {exc}") from exc


def require_api_ready(preflight: dict[str, Any]) -> None:
    if not preflight.get("api_ready"):
        failed = [
            {
                "check": check.get("check"),
                "detail": check.get("detail"),
                "path": check.get("path"),
            }
            for check in preflight.get("checks", [])
            if not check.get("passed")
        ]
        raise SystemExit(
            "API workflow stopped before any model call because preflight failed:\n"
            + json.dumps(failed, ensure_ascii=False, indent=2, sort_keys=True)
        )


def expected_candidates_for_run(config: dict[str, Any], limit_override: int | None) -> int:
    evidence_count = count_jsonl(Path(config["evidence_packets"]))
    if limit_override is not None:
        return evidence_count if limit_override == 0 else min(limit_override, evidence_count)
    smoke_limit = int(config.get("smoke_limit") or 0)
    return evidence_count if smoke_limit == 0 else min(smoke_limit, evidence_count)


def run_model_selection_validation(
    config_path: Path,
    config: dict[str, Any],
    run_dir: Path,
    allow_failure: bool,
) -> dict[str, Any] | None:
    selection = config.get("model_selection")
    if not selection:
        return None
    selection_path = Path(selection)
    out = run_dir / "model_selection_validation.json"
    command = [
        sys.executable,
        "scripts/validate_model_selection.py",
        "--selection",
        str(selection_path),
        "--api-config",
        str(config_path),
        "--out",
        str(out),
    ]
    completed = run_command(command, allow_failure=allow_failure)
    if out.exists():
        return read_json(out)
    return {
        "passed": False,
        "returncode": completed.returncode,
        "selection": str(selection_path),
        "out": out.as_posix(),
    }


def workflow(args: argparse.Namespace) -> dict[str, Any]:
    config_path = Path(args.config)
    config = read_json(config_path)
    run_dir = Path(args.run_dir or config["out_dir"])
    limit_override = args.limit

    model_selection_validation = run_model_selection_validation(
        config_path=config_path,
        config=config,
        run_dir=run_dir,
        allow_failure=args.check_only,
    )
    preflight = load_preflight(config_path, allow_missing_credentials=args.check_only)
    if args.check_only:
        summary = {
            "mode": "check_only",
            "config": str(config_path),
            "run_dir": run_dir.as_posix(),
            "limit_override": limit_override,
            "api_ready": preflight.get("api_ready"),
            "dry_run_ready": preflight.get("dry_run_ready"),
            "model_selection_validation": model_selection_validation,
            "model_call_attempted": False,
        }
        if args.summary_out:
            write_json(Path(args.summary_out), summary)
        print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
        return summary

    require_api_ready(preflight)
    if not args.execute:
        raise SystemExit("Preflight passed, but --execute is required before making real API calls.")

    if (run_dir / "reviews.jsonl").exists() and not args.allow_existing_output:
        raise SystemExit(
            f"Refusing to overwrite existing API review outputs in {run_dir}. "
            "Choose a new --run-dir or pass --allow-existing-output intentionally."
        )

    run_command_args = [
        sys.executable,
        "scripts/run_patch_verification_api_pilot.py",
        "--config",
        str(config_path),
        "--allow-direct-api-run",
    ]
    if args.run_dir:
        run_command_args.extend(["--out-dir", str(run_dir)])
    if limit_override is not None:
        run_command_args.extend(["--limit", str(limit_override)])
    run_command(run_command_args)
    expected_candidates = expected_candidates_for_run(config, limit_override)
    run_command(
        [
            sys.executable,
            "scripts/postprocess_api_pilot_run.py",
            "--run-dir",
            str(run_dir),
            "--expected-candidates",
            str(expected_candidates),
        ]
    )

    postprocess_summary = read_json(run_dir / "postprocess_summary.json")
    summary = {
        "mode": "executed",
        "config": str(config_path),
        "run_dir": run_dir.as_posix(),
        "limit_override": limit_override,
        "expected_candidates": expected_candidates,
        "api_ready": True,
        "model_selection_validation": model_selection_validation,
        "model_call_attempted": True,
        "postprocess_summary": postprocess_summary,
    }
    if args.summary_out:
        write_json(Path(args.summary_out), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the guarded API pilot workflow.")
    parser.add_argument("--config", required=True, help="Local API pilot config.")
    parser.add_argument("--run-dir", help="Override run directory for postprocess summary lookup.")
    parser.add_argument("--limit", type=int, help="Override candidate limit for the API runner. Use 0 for a full run.")
    parser.add_argument("--summary-out", help="Optional workflow summary JSON output.")
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Run preflight only. Allows missing credentials and never calls the model API.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Required to make real API calls after strict preflight passes.",
    )
    parser.add_argument(
        "--allow-existing-output",
        action="store_true",
        help="Allow executing when <run-dir>/reviews.jsonl already exists.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    workflow(args)


if __name__ == "__main__":
    main()
