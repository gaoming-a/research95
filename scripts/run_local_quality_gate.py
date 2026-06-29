from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


SENSITIVE_PATTERN = "|".join(
    [
        "".join(["sk-", "or-v1"]),
        "".join(["bd7d", "b20e"]),
        "".join(["907d", "eb9e"]),
        "".join(["3230", "70ae"]),
        "".join(["OPENROUTER", "_API", "_KEY"]) + r".*[A-Za-z0-9_-]{20,}",
        "".join(["DEEPSEEK", "_API", "_KEY"]) + r"\s*=\s*(?!<your-deepseek-key>)(?!$)[A-Za-z0-9_-]{20,}",
        "".join(["D:", r"\\", "mgao"]),
        "".join(["C:", r"\\", "Users"]),
        " ".join(["Ming", "Gao"]),
        "/".join(["", "mnt", "d", "mgao"]),
        r"models\.coder\.local",
        r"models\.weak\.local",
        r"models\.matched\.local",
    ]
)


def run_command(command: list[str], allow_exit_codes: set[int] | None = None) -> dict[str, Any]:
    allowed = allow_exit_codes or {0}
    completed = subprocess.run(
        command,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        "command": command,
        "exit_code": completed.returncode,
        "passed": completed.returncode in allowed,
        "stdout_tail": tail(completed.stdout),
        "stderr_tail": tail(completed.stderr),
    }


def tail(text: str | None, max_chars: int = 3000) -> str:
    if text is None:
        return ""
    return text[-max_chars:] if len(text) > max_chars else text


def remove_pycache() -> int:
    count = 0
    for path in Path(".").rglob("__pycache__"):
        if path.is_dir():
            shutil.rmtree(path)
            count += 1
    return count


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def build_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Local Quality Gate",
        "",
        "## Summary",
        "",
        f"- passed: {bool_mark(summary['passed'])}",
        f"- compile passed: {bool_mark(summary['compile']['passed'])}",
        f"- sensitive scan passed: {bool_mark(summary['sensitive_scan']['passed'])}",
        f"- credential boundary passed: {bool_mark(summary['credential_boundary']['passed'])}",
        f"- bootstrap safety passed: {bool_mark(summary['bootstrap_safety']['passed'])}",
        f"- workflow guard passed: {bool_mark(summary['workflow_guard']['passed'])}",
        f"- API failure handling passed: {bool_mark(summary['api_failure_handling']['passed'])}",
        f"- command templates passed: {bool_mark(summary['command_templates']['passed'])}",
        f"- experiment run records passed: {bool_mark(summary['experiment_run_records']['passed'])}",
        f"- git sync packet audit passed: {bool_mark(summary['git_sync_packet_audit']['passed'])}",
        f"- submission handoff audit passed: {bool_mark(summary['submission_handoff_audit']['passed'])}",
        f"- submission freeze-candidate audit passed: {bool_mark(summary['submission_freeze_candidate_audit']['passed'])}",
        f"- SQJ submission checklist audit passed: {bool_mark(summary['sqj_submission_checklist_audit']['passed'])}",
        f"- SQJ artifact gate passed: {bool_mark(summary['sqj_artifact_gate']['passed'])}",
        f"- SQJ final-authorization gate passed: {bool_mark(summary['sqj_final_authorization_gate']['passed'])}",
        f"- SQJ school-recognition gate passed: {bool_mark(summary['sqj_school_recognition_gate']['passed'])}",
        f"- SQJ human-input gate passed: {bool_mark(summary['sqj_human_inputs_gate']['passed'])}",
        f"- SQJ human-decision packet passed: {bool_mark(summary['sqj_human_decision_packet']['passed'])}",
        f"- SQJ PDF compile gate passed: {bool_mark(summary['sqj_pdf_compile_gate']['passed'])}",
        f"- SQJ figure-layout gate passed: {bool_mark(summary['sqj_figure_layout_gate']['passed'])}",
        f"- SQJ final-freeze readiness audit passed: {bool_mark(summary['sqj_final_freeze_readiness_audit']['passed'])}",
        f"- artifact dry-run passed: {bool_mark(summary['artifact_dry_run']['passed'])}",
        f"- artifact zip audit passed: {bool_mark(summary['artifact_zip_audit']['passed'])}",
        f"- pycache directories removed: {summary['pycache_removed']}",
        f"- ready for real API: {bool_mark(summary['readiness']['overall_ready_for_real_api'])}",
        f"- prompt-only positive paper claim ready: {bool_mark(summary['paper_readiness'].get('prompt_only_positive_claim_ready', summary['paper_readiness'].get('positive_claim_ready')))}",
        f"- tool-augmented paper claim ready: {bool_mark(summary['paper_readiness'].get('tool_augmented_claim_ready'))}",
        f"- full goal complete: {bool_mark(summary['goal_completion']['complete'])}",
        f"- plan stage counts: `{summary['plan_progress'].get('stage_counts', {})}`",
        "",
        "## Notes",
        "",
        "API readiness, Git readiness, and full goal completion are reported as state, not local quality failures. Real API calls still require `.env`, model selection, and local API config.",
        "",
    ]
    if not summary["passed"]:
        lines.extend(["## Failed Checks", ""])
        for name in [
            "compile",
            "sensitive_scan",
            "credential_boundary",
            "bootstrap_safety",
            "workflow_guard",
            "api_failure_handling",
            "command_templates",
            "experiment_run_records",
            "git_sync_packet_audit",
            "submission_handoff_audit",
            "submission_freeze_candidate_audit",
            "sqj_submission_checklist_audit",
            "sqj_artifact_gate",
            "sqj_final_authorization_gate",
            "sqj_school_recognition_gate",
            "sqj_human_inputs_gate",
            "sqj_human_decision_packet",
            "sqj_pdf_compile_gate",
            "sqj_figure_layout_gate",
            "sqj_final_freeze_readiness_audit",
            "artifact_dry_run",
            "artifact_zip_audit",
        ]:
            check = summary[name]
            if not check["passed"]:
                lines.append(f"- `{name}` exit code: {check['exit_code']}")
        lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local no-API quality checks for Research95.")
    parser.add_argument("--out-json", default="outputs/local_quality_gate/latest.json")
    parser.add_argument("--out-md", default="outputs/local_quality_gate/latest.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    compile_result = run_command([sys.executable, "-m", "compileall", "src", "scripts"])
    pycache_removed = remove_pycache()
    sensitive_scan = run_command(
        [
            "rg",
            "-a",
            "-n",
            SENSITIVE_PATTERN,
            ".",
            "--pcre2",
            "--glob",
            "!outputs/**",
            "--glob",
            "!data/**",
            "--glob",
            "!tmp/**",
            "--glob",
            "!.env",
            "--glob",
            "!.env.*",
            "--glob",
            "!configs/*.local.json",
            "--glob",
            "!artifacts/**",
        ],
        allow_exit_codes={1},
    )
    credential_boundary = run_command(
        [
            sys.executable,
            "scripts/audit_credential_boundary.py",
            "--out-json",
            "outputs/credential_boundary/latest.json",
            "--out-md",
            "outputs/credential_boundary/latest.md",
        ]
    )
    bootstrap_safety = run_command(
        [
            sys.executable,
            "scripts/audit_bootstrap_safety.py",
            "--out-json",
            "outputs/bootstrap_safety/latest.json",
            "--out-md",
            "outputs/bootstrap_safety/latest.md",
        ]
    )
    command_templates = run_command(
        [
            sys.executable,
            "scripts/audit_command_templates.py",
            "--out-json",
            "outputs/command_templates/latest.json",
            "--out-md",
            "outputs/command_templates/latest.md",
        ]
    )
    experiment_run_records = run_command(
        [
            sys.executable,
            "scripts/write_experiment_run_records.py",
            "--out-json",
            "outputs/experiment_run_records/latest.json",
            "--out-md",
            "outputs/experiment_run_records/latest.md",
        ]
    )
    workflow_guard = run_command(
        [
            sys.executable,
            "scripts/audit_workflow_guard.py",
            "--out-json",
            "outputs/workflow_guard/latest.json",
            "--out-md",
            "outputs/workflow_guard/latest.md",
        ]
    )
    api_failure_handling = run_command(
        [
            sys.executable,
            "scripts/audit_api_failure_handling.py",
            "--out-json",
            "outputs/api_failure_handling/latest.json",
            "--out-md",
            "outputs/api_failure_handling/latest.md",
        ]
    )
    git_sync_packet_audit = run_command(
        [
            sys.executable,
            "scripts/audit_git_sync_packet.py",
            "--out-json",
            "outputs/git_sync_packet_audit/latest.json",
            "--out-md",
            "outputs/git_sync_packet_audit/latest.md",
        ]
    )
    submission_handoff_audit = run_command(
        [
            sys.executable,
            "scripts/audit_submission_handoff.py",
            "--out-json",
            "outputs/submission_handoff_audit/latest.json",
            "--out-md",
            "outputs/submission_handoff_audit/latest.md",
        ]
    )
    submission_freeze_candidate_audit = run_command(
        [
            sys.executable,
            "scripts/audit_submission_freeze_candidate.py",
            "--out-json",
            "outputs/submission_freeze_candidate_audit/latest.json",
            "--out-md",
            "outputs/submission_freeze_candidate_audit/latest.md",
        ]
    )
    sqj_submission_checklist_audit = run_command(
        [
            sys.executable,
            "scripts/audit_sqj_submission_checklist.py",
            "--out-json",
            "outputs/sqj_submission_checklist_audit/latest.json",
            "--out-md",
            "outputs/sqj_submission_checklist_audit/latest.md",
        ]
    )
    sqj_artifact_gate = run_command(
        [
            sys.executable,
            "scripts/audit_sqj_artifact_gate.py",
            "--out-json",
            "outputs/sqj_artifact_gate/latest.json",
            "--out-md",
            "outputs/sqj_artifact_gate/latest.md",
        ]
    )
    sqj_final_authorization_gate = run_command(
        [
            sys.executable,
            "scripts/audit_sqj_final_authorization_gate.py",
            "--out-json",
            "outputs/sqj_final_authorization_gate/latest.json",
            "--out-md",
            "outputs/sqj_final_authorization_gate/latest.md",
        ]
    )
    sqj_school_recognition_gate = run_command(
        [
            sys.executable,
            "scripts/audit_sqj_school_recognition_gate.py",
            "--out-json",
            "outputs/sqj_school_recognition_gate/latest.json",
            "--out-md",
            "outputs/sqj_school_recognition_gate/latest.md",
        ]
    )
    sqj_human_inputs_gate = run_command(
        [
            sys.executable,
            "scripts/audit_sqj_human_inputs_gate.py",
            "--out-json",
            "outputs/sqj_human_inputs_gate/latest.json",
            "--out-md",
            "outputs/sqj_human_inputs_gate/latest.md",
        ]
    )
    sqj_human_decision_packet = run_command(
        [
            sys.executable,
            "scripts/audit_sqj_human_decision_packet.py",
            "--out-json",
            "outputs/sqj_human_decision_packet/latest.json",
            "--out-md",
            "outputs/sqj_human_decision_packet/latest.md",
        ]
    )
    sqj_pdf_compile_gate = run_command(
        [
            sys.executable,
            "scripts/audit_sqj_pdf_compile_gate.py",
            "--out-json",
            "outputs/sqj_pdf_compile_gate/latest.json",
            "--out-md",
            "outputs/sqj_pdf_compile_gate/latest.md",
        ]
    )
    sqj_figure_layout_gate = run_command(
        [
            sys.executable,
            "scripts/audit_sqj_figure_layout_gate.py",
            "--out-json",
            "outputs/sqj_figure_layout_gate/latest.json",
            "--out-md",
            "outputs/sqj_figure_layout_gate/latest.md",
        ]
    )
    sqj_final_freeze_readiness_audit = run_command(
        [
            sys.executable,
            "scripts/audit_sqj_final_freeze_readiness.py",
            "--out-json",
            "outputs/sqj_final_freeze_readiness/latest.json",
            "--out-md",
            "outputs/sqj_final_freeze_readiness/latest.md",
        ]
    )
    readiness_json = Path("outputs/readiness_audit/latest.json")
    readiness_md = Path("outputs/readiness_audit/latest.md")
    readiness_run = run_command(
        [
            sys.executable,
            "scripts/audit_execution_readiness.py",
            "--out-json",
            str(readiness_json),
            "--out-md",
            str(readiness_md),
        ]
    )
    paper_json = Path("outputs/paper_readiness/latest.json")
    paper_md = Path("outputs/paper_readiness/latest.md")
    paper_run = run_command(
        [
            sys.executable,
            "scripts/audit_paper_readiness.py",
            "--out-json",
            str(paper_json),
            "--out-md",
            str(paper_md),
        ]
    )
    plan_json = Path("outputs/plan_progress/latest.json")
    plan_md = Path("outputs/plan_progress/latest.md")
    plan_progress_run = run_command(
        [
            sys.executable,
            "scripts/audit_ai_plan_progress.py",
            "--out-json",
            str(plan_json),
            "--out-md",
            str(plan_md),
        ]
    )
    artifact_dry_run = run_command(
        [
            sys.executable,
            "scripts/prepare_anonymous_artifact.py",
            "--dry-run",
            "--manifest-out",
            "artifacts/research95_anonymous_artifact_manifest_dry_run.json",
        ]
    )
    artifact_zip = Path("artifacts/research95_anonymous_artifact.zip")
    artifact_zip_audit = (
        run_command(
            [
                sys.executable,
                "scripts/audit_anonymous_artifact.py",
                "--artifact",
                str(artifact_zip),
                "--out-json",
                "artifacts/research95_anonymous_artifact_audit.json",
                "--out-md",
                "artifacts/research95_anonymous_artifact_audit.md",
            ]
        )
        if artifact_zip.exists()
        else {
            "command": [],
            "exit_code": 0,
            "passed": True,
            "stdout_tail": "artifact zip not present; skipped",
            "stderr_tail": "",
        }
    )
    goal_json = Path("outputs/goal_completion/latest.json")
    goal_md = Path("outputs/goal_completion/latest.md")
    goal_completion_run = run_command(
        [
            sys.executable,
            "scripts/audit_goal_completion.py",
            "--out-json",
            str(goal_json),
            "--out-md",
            str(goal_md),
        ]
    )

    summary = {
        "passed": bool(
            compile_result["passed"]
            and sensitive_scan["passed"]
            and credential_boundary["passed"]
            and bootstrap_safety["passed"]
            and workflow_guard["passed"]
            and api_failure_handling["passed"]
            and command_templates["passed"]
            and experiment_run_records["passed"]
            and git_sync_packet_audit["passed"]
            and submission_handoff_audit["passed"]
            and submission_freeze_candidate_audit["passed"]
            and sqj_submission_checklist_audit["passed"]
            and sqj_artifact_gate["passed"]
            and sqj_final_authorization_gate["passed"]
            and sqj_school_recognition_gate["passed"]
            and sqj_human_inputs_gate["passed"]
            and sqj_human_decision_packet["passed"]
            and sqj_pdf_compile_gate["passed"]
            and sqj_figure_layout_gate["passed"]
            and sqj_final_freeze_readiness_audit["passed"]
            and artifact_dry_run["passed"]
            and artifact_zip_audit["passed"]
        ),
        "compile": compile_result,
        "pycache_removed": pycache_removed,
        "sensitive_scan": sensitive_scan,
        "credential_boundary": credential_boundary,
        "bootstrap_safety": bootstrap_safety,
        "workflow_guard": workflow_guard,
        "api_failure_handling": api_failure_handling,
        "command_templates": command_templates,
        "experiment_run_records": experiment_run_records,
        "git_sync_packet_audit": git_sync_packet_audit,
        "submission_handoff_audit": submission_handoff_audit,
        "submission_freeze_candidate_audit": submission_freeze_candidate_audit,
        "sqj_submission_checklist_audit": sqj_submission_checklist_audit,
        "sqj_artifact_gate": sqj_artifact_gate,
        "sqj_final_authorization_gate": sqj_final_authorization_gate,
        "sqj_school_recognition_gate": sqj_school_recognition_gate,
        "sqj_human_inputs_gate": sqj_human_inputs_gate,
        "sqj_human_decision_packet": sqj_human_decision_packet,
        "sqj_pdf_compile_gate": sqj_pdf_compile_gate,
        "sqj_figure_layout_gate": sqj_figure_layout_gate,
        "sqj_final_freeze_readiness_audit": sqj_final_freeze_readiness_audit,
        "readiness_run": readiness_run,
        "paper_readiness_run": paper_run,
        "plan_progress_run": plan_progress_run,
        "artifact_dry_run": artifact_dry_run,
        "artifact_zip_audit": artifact_zip_audit,
        "goal_completion_run": goal_completion_run,
        "readiness": read_json(readiness_json) if readiness_json.exists() else {},
        "paper_readiness": read_json(paper_json) if paper_json.exists() else {},
        "plan_progress": read_json(plan_json) if plan_json.exists() else {},
        "goal_completion": read_json(goal_json) if goal_json.exists() else {},
    }
    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    write_json(out_json, summary)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(summary), encoding="utf-8")
    print(json.dumps({"out_json": str(out_json), "out_md": str(out_md), "passed": summary["passed"]}, indent=2))
    if not summary["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
