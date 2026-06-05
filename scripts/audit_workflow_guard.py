from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


WORK_DIR = Path("outputs") / "workflow_guard"
RUN_DIR = WORK_DIR / "api_run"
DRY_FULL_RUN_DIR = WORK_DIR / "dry_full_run"
MOCK_SMOKE_RUN_DIR = WORK_DIR / "mock_smoke_run"
DIRECT_REAL_RUN_DIR = WORK_DIR / "direct_real_run"
CONFIG_PATH = WORK_DIR / "api_pilot.local.json"
SUMMARY_PATH = WORK_DIR / "check_only_summary.json"


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def display_command(command: list[str]) -> list[str]:
    if command and Path(command[0]) == Path(sys.executable):
        return ["python", *command[1:]]
    return command


def run_command(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {
        "command": display_command(command),
        "exit_code": completed.returncode,
        "stdout_tail": completed.stdout[-2000:],
        "stderr_tail": completed.stderr[-2000:],
    }


def clean_work_dir() -> None:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    WORK_DIR.mkdir(parents=True, exist_ok=True)


def write_placeholder_config() -> None:
    write_json(
        CONFIG_PATH,
        {
            "run_id": "workflow_guard",
            "api_provider": "deepseek_official",
            "model": "<provider-model-id>",
            "conditions": ["llm_only", "evidence_first"],
            "temperature": 0.0,
            "max_tokens": 1200,
            "smoke_limit": 2,
            "candidates": "outputs/patch_verification_pilot_001/candidates.jsonl",
            "evidence_packets": "outputs/patch_verification_pilot_001/evidence_packets.jsonl",
            "validation_summary": "outputs/patch_verification_pilot_001/validation_summary.json",
            "model_selection": "outputs/workflow_guard/model_selection.local.json",
            "out_dir": RUN_DIR.as_posix(),
            "env": "outputs/workflow_guard/.env.missing",
        },
    )


def output_files_created() -> list[str]:
    if not RUN_DIR.exists():
        return []
    created: list[str] = []
    for path in RUN_DIR.rglob("*"):
        if path.is_file():
            created.append(path.as_posix())
    return sorted(created)


def count_jsonl(path: Path) -> int | None:
    if not path.exists():
        return None
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def build_audit() -> dict[str, Any]:
    clean_work_dir()
    write_placeholder_config()

    check_only = run_command(
        [
            sys.executable,
            "scripts/run_api_pilot_workflow.py",
            "--config",
            str(CONFIG_PATH),
            "--check-only",
            "--summary-out",
            str(SUMMARY_PATH),
        ]
    )
    check_only_summary = read_json(SUMMARY_PATH)
    files_after_check_only = output_files_created()

    strict_without_execute = run_command(
        [
            sys.executable,
            "scripts/run_api_pilot_workflow.py",
            "--config",
            str(CONFIG_PATH),
        ]
    )
    files_after_strict = output_files_created()

    full_limit_override_dry_run = run_command(
        [
            sys.executable,
            "scripts/run_patch_verification_api_pilot.py",
            "--config",
            str(CONFIG_PATH),
            "--dry-run",
            "--out-dir",
            str(DRY_FULL_RUN_DIR),
            "--limit",
            "0",
        ]
    )
    full_limit_prompt_count = count_jsonl(DRY_FULL_RUN_DIR / "prompt_manifest.jsonl")
    direct_real_without_workflow = run_command(
        [
            sys.executable,
            "scripts/run_patch_verification_api_pilot.py",
            "--config",
            str(CONFIG_PATH),
            "--out-dir",
            str(DIRECT_REAL_RUN_DIR),
        ]
    )
    direct_real_files = sorted(path.as_posix() for path in DIRECT_REAL_RUN_DIR.rglob("*") if path.is_file()) if DIRECT_REAL_RUN_DIR.exists() else []
    mock_smoke_run = run_command(
        [
            sys.executable,
            "scripts/run_patch_verification_api_pilot.py",
            "--config",
            str(CONFIG_PATH),
            "--out-dir",
            str(MOCK_SMOKE_RUN_DIR),
            "--limit",
            "2",
            "--mock-policy",
            "patch_surface",
        ]
    )
    mock_postprocess = run_command(
        [
            sys.executable,
            "scripts/postprocess_api_pilot_run.py",
            "--run-dir",
            str(MOCK_SMOKE_RUN_DIR),
            "--expected-candidates",
            "2",
            "--allow-mock",
        ]
    )
    mock_completeness = read_json(MOCK_SMOKE_RUN_DIR / "run_completeness.json")
    mock_gate = read_json(MOCK_SMOKE_RUN_DIR / "gate_report.json")

    forbidden_outputs = [
        path
        for path in files_after_strict
        if path.endswith("reviews.jsonl") or "/raw/" in path.replace("\\", "/")
    ]
    passed = bool(
        check_only["exit_code"] == 0
        and check_only_summary
        and check_only_summary.get("mode") == "check_only"
        and check_only_summary.get("model_call_attempted") is False
        and strict_without_execute["exit_code"] != 0
        and full_limit_override_dry_run["exit_code"] == 0
        and full_limit_prompt_count == 60
        and direct_real_without_workflow["exit_code"] != 0
        and not any(path.endswith("reviews.jsonl") or "/raw/" in path.replace("\\", "/") for path in direct_real_files)
        and mock_smoke_run["exit_code"] == 0
        and mock_postprocess["exit_code"] == 0
        and mock_completeness
        and mock_completeness.get("passed") is True
        and mock_completeness.get("expected_records") == 4
        and mock_gate
        and mock_gate.get("verdict") == "not_evidence"
        and not forbidden_outputs
    )

    return {
        "passed": passed,
        "work_dir": WORK_DIR.as_posix(),
        "check_only": {
            **check_only,
            "summary": check_only_summary,
            "passed": bool(
                check_only["exit_code"] == 0
                and check_only_summary
                and check_only_summary.get("model_call_attempted") is False
            ),
        },
        "strict_without_execute": {
            **strict_without_execute,
            "passed": strict_without_execute["exit_code"] != 0 and not forbidden_outputs,
        },
        "full_limit_override_dry_run": {
            **full_limit_override_dry_run,
            "prompt_manifest": (DRY_FULL_RUN_DIR / "prompt_manifest.jsonl").as_posix(),
            "prompt_count": full_limit_prompt_count,
            "passed": full_limit_override_dry_run["exit_code"] == 0 and full_limit_prompt_count == 60,
        },
        "direct_real_runner_guard": {
            **direct_real_without_workflow,
            "created_files": direct_real_files,
            "passed": bool(
                direct_real_without_workflow["exit_code"] != 0
                and not any(path.endswith("reviews.jsonl") or "/raw/" in path.replace("\\", "/") for path in direct_real_files)
            ),
        },
        "mock_smoke_postprocess": {
            "run": mock_smoke_run,
            "postprocess": mock_postprocess,
            "completeness": mock_completeness,
            "gate": mock_gate,
            "passed": bool(
                mock_smoke_run["exit_code"] == 0
                and mock_postprocess["exit_code"] == 0
                and mock_completeness
                and mock_completeness.get("passed") is True
                and mock_completeness.get("expected_records") == 4
                and mock_gate
                and mock_gate.get("verdict") == "not_evidence"
            ),
        },
        "forbidden_outputs": forbidden_outputs,
        "created_files": files_after_strict,
        "boundary": "This audit uses placeholder local config under outputs/ and must not call model APIs.",
    }


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# Workflow Guard Audit",
        "",
        "## Summary",
        "",
        f"- passed: {bool_mark(audit['passed'])}",
        f"- work dir: `{audit['work_dir']}`",
        f"- check-only no model call: {bool_mark(audit['check_only']['passed'])}",
        f"- strict missing-prereq path stopped before outputs: {bool_mark(audit['strict_without_execute']['passed'])}",
        f"- full limit override dry-run: {bool_mark(audit['full_limit_override_dry_run']['passed'])}",
        f"- direct real runner guarded: {bool_mark(audit['direct_real_runner_guard']['passed'])}",
        f"- mock smoke postprocess completeness: {bool_mark(audit['mock_smoke_postprocess']['passed'])}",
        f"- forbidden outputs: {len(audit['forbidden_outputs'])}",
        "",
        "## Boundary",
        "",
        audit["boundary"],
        "",
    ]
    if audit["forbidden_outputs"]:
        lines.extend(["## Forbidden Outputs", ""])
        for path in audit["forbidden_outputs"]:
            lines.append(f"- `{path}`")
        lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit guarded API workflow behavior without model calls.")
    parser.add_argument("--out-json", default="outputs/workflow_guard/latest.json")
    parser.add_argument("--out-md", default="outputs/workflow_guard/latest.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = build_audit()
    write_json(Path(args.out_json), audit)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(audit), encoding="utf-8")
    print(json.dumps({"out_json": args.out_json, "out_md": args.out_md, "passed": audit["passed"]}, ensure_ascii=False, indent=2))
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
