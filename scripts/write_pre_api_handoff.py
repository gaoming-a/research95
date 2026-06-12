from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


READINESS_JSON = Path("outputs") / "readiness_audit" / "latest.json"
READINESS_MD = Path("outputs") / "readiness_audit" / "latest.md"
PAPER_JSON = Path("outputs") / "paper_readiness" / "latest.json"
PAPER_MD = Path("outputs") / "paper_readiness" / "latest.md"
PLAN_JSON = Path("outputs") / "plan_progress" / "latest.json"
PLAN_MD = Path("outputs") / "plan_progress" / "latest.md"
GOAL_JSON = Path("outputs") / "goal_completion" / "latest.json"
GOAL_MD = Path("outputs") / "goal_completion" / "latest.md"
HUMAN_JSON = Path("outputs") / "handoff" / "human_input_packet.json"
HUMAN_MD = Path("outputs") / "handoff" / "human_input_packet.md"
GIT_JSON = Path("outputs") / "handoff" / "git_sync_packet.json"
GIT_MD = Path("outputs") / "handoff" / "git_sync_packet.md"
GIT_AUDIT_JSON = Path("outputs") / "git_sync_packet_audit" / "latest.json"
GIT_AUDIT_MD = Path("outputs") / "git_sync_packet_audit" / "latest.md"
MODEL_CATALOG_JSON = Path("outputs") / "model_selection" / "openrouter_catalog_audit.json"
MODEL_CATALOG_MD = Path("outputs") / "model_selection" / "openrouter_catalog_audit.md"
REPRO_REF = Path("outputs") / "reproducibility" / "pilot_001_manifest.json"
REPRO_CAND = Path("outputs") / "reproducibility" / "pilot_repro_001_manifest.json"
REPRO_COMPARE = Path("outputs") / "reproducibility" / "pilot_compare.json"
REPRO_COMPARE_MD = Path("outputs") / "reproducibility" / "pilot_compare.md"
RUN_RECORDS_JSON = Path("outputs") / "experiment_run_records" / "latest.json"
RUN_RECORDS_MD = Path("outputs") / "experiment_run_records" / "latest.md"


def tail(text: str, max_chars: int = 2000) -> str:
    return text[-max_chars:] if len(text) > max_chars else text


def display_command(command: list[str]) -> list[str]:
    if command and Path(command[0]) == Path(sys.executable):
        return ["python", *command[1:]]
    return command


def run_command(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        "command": display_command(command),
        "exit_code": completed.returncode,
        "passed": completed.returncode == 0,
        "stdout_tail": tail(completed.stdout),
        "stderr_tail": tail(completed.stderr),
    }


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def build_handoff(command_results: list[dict[str, Any]]) -> dict[str, Any]:
    readiness = read_json(READINESS_JSON)
    paper = read_json(PAPER_JSON)
    plan = read_json(PLAN_JSON)
    goal = read_json(GOAL_JSON)
    human = read_json(HUMAN_JSON)
    git_packet = read_json(GIT_JSON)
    git_audit = read_json(GIT_AUDIT_JSON)
    model_catalog = read_json(MODEL_CATALOG_JSON)
    repro = read_json(REPRO_COMPARE)

    no_api = readiness.get("no_api", {}) if isinstance(readiness, dict) else {}
    return {
        "commands_passed": all(item["passed"] for item in command_results),
        "command_results": command_results,
        "ready_for_real_api": bool(readiness.get("overall_ready_for_real_api")),
        "no_api_ready": bool(no_api.get("ready")),
        "reproducibility_matched": bool(repro.get("matched")),
        "stage_counts": plan.get("stage_counts", {}),
        "full_goal_complete": bool(goal.get("complete")),
        "missing_goal_requirements": goal.get("missing_required", []),
        "missing_required_input_ids": human.get("missing_required_input_ids", []),
        "positive_paper_claim_ready": bool(paper.get("positive_claim_ready")),
        "prompt_only_positive_paper_claim_ready": bool(paper.get("positive_claim_ready")),
        "tool_augmented_claim_ready": bool(paper.get("tool_augmented_claim_ready")),
        "methods_or_negative_draft_ready": bool(paper.get("negative_or_methods_draft_ready")),
        "git_repo": bool(plan.get("git_repo")),
        "git_requires_human_decision": bool(git_packet.get("requires_human_decision")),
        "git_sync_packet_audit_passed": bool(git_audit.get("passed")),
        "model_catalog_all_available": bool(model_catalog.get("all_available")),
        "authoritative_reports": {
            "readiness": READINESS_MD.as_posix(),
            "plan_progress": PLAN_MD.as_posix(),
            "experiment_run_records": RUN_RECORDS_MD.as_posix(),
            "goal_completion": GOAL_MD.as_posix(),
            "human_input_packet": HUMAN_MD.as_posix(),
            "git_sync_packet": GIT_MD.as_posix(),
            "git_sync_packet_audit": GIT_AUDIT_MD.as_posix(),
            "model_catalog_audit": MODEL_CATALOG_MD.as_posix(),
            "reproducibility_compare": REPRO_COMPARE_MD.as_posix(),
            "paper_readiness": PAPER_MD.as_posix(),
        },
    }


def build_markdown(handoff: dict[str, Any]) -> str:
    reports = handoff["authoritative_reports"]
    lines = [
        "# Pre-API Execution Handoff",
        "",
        "## Summary",
        "",
        f"- local handoff commands passed: {bool_mark(handoff['commands_passed'])}",
        f"- no-API ready: {bool_mark(handoff['no_api_ready'])}",
        f"- reproducibility matched: {bool_mark(handoff['reproducibility_matched'])}",
        f"- ready for real API: {bool_mark(handoff['ready_for_real_api'])}",
        f"- prompt-only positive paper claim ready: {bool_mark(handoff['prompt_only_positive_paper_claim_ready'])}",
        f"- tool-augmented conditional claim ready: {bool_mark(handoff['tool_augmented_claim_ready'])}",
        f"- methods/negative draft ready: {bool_mark(handoff['methods_or_negative_draft_ready'])}",
        f"- full goal complete: {bool_mark(handoff['full_goal_complete'])}",
        f"- git repository: {bool_mark(handoff['git_repo'])}",
        f"- git decision required: {bool_mark(handoff['git_requires_human_decision'])}",
        f"- git sync packet audit passed: {bool_mark(handoff['git_sync_packet_audit_passed'])}",
        f"- model catalog slugs available: {bool_mark(handoff['model_catalog_all_available'])}",
        f"- stage counts: `{handoff['stage_counts']}`",
        "",
        "## Missing Required Inputs",
        "",
    ]
    if handoff["missing_required_input_ids"]:
        for item in handoff["missing_required_input_ids"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- None.")
    lines.extend(["", "## Missing Goal Requirements", ""])
    if handoff["missing_goal_requirements"]:
        for item in handoff["missing_goal_requirements"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Reports",
            "",
            f"- readiness: `{reports['readiness']}`",
            f"- plan progress: `{reports['plan_progress']}`",
            f"- experiment run records: `{reports['experiment_run_records']}`",
            f"- goal completion: `{reports['goal_completion']}`",
            f"- human input packet: `{reports['human_input_packet']}`",
            f"- git sync packet: `{reports['git_sync_packet']}`",
            f"- git sync packet audit: `{reports['git_sync_packet_audit']}`",
            f"- model catalog audit: `{reports['model_catalog_audit']}`",
            f"- reproducibility comparison: `{reports['reproducibility_compare']}`",
            f"- paper readiness: `{reports['paper_readiness']}`",
            "",
            "## Boundary",
            "",
            "This handoff performs local audits only. It does not call model APIs and does not make paper claims from dry-run or mock outputs.",
            "",
            "## Command Status",
            "",
            "| command | passed | exit code |",
            "|---|---|---:|",
        ]
    )
    for result in handoff["command_results"]:
        command = " ".join(result["command"])
        lines.append(f"| `{command}` | {bool_mark(result['passed'])} | {result['exit_code']} |")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a local pre-API handoff report.")
    parser.add_argument("--out-json", default="outputs/handoff/pre_api_handoff.json")
    parser.add_argument("--out-md", default="outputs/handoff/pre_api_handoff.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    commands = [
        [
            sys.executable,
            "scripts/audit_execution_readiness.py",
            "--out-json",
            str(READINESS_JSON),
            "--out-md",
            str(READINESS_MD),
        ],
        [
            sys.executable,
            "scripts/write_reproducibility_manifest.py",
            "--run-dir",
            "outputs/patch_verification_pilot_001",
            "--out",
            str(REPRO_REF),
        ],
        [
            sys.executable,
            "scripts/write_reproducibility_manifest.py",
            "--run-dir",
            "outputs/patch_verification_pilot_repro_001",
            "--out",
            str(REPRO_CAND),
            "--compare-to",
            str(REPRO_REF),
            "--compare-out",
            str(REPRO_COMPARE),
            "--compare-md",
            str(REPRO_COMPARE_MD),
        ],
        [
            sys.executable,
            "scripts/audit_paper_readiness.py",
            "--out-json",
            str(PAPER_JSON),
            "--out-md",
            str(PAPER_MD),
        ],
        [
            sys.executable,
            "scripts/audit_ai_plan_progress.py",
            "--out-json",
            str(PLAN_JSON),
            "--out-md",
            str(PLAN_MD),
        ],
        [
            sys.executable,
            "scripts/write_experiment_run_records.py",
            "--out-json",
            str(RUN_RECORDS_JSON),
            "--out-md",
            str(RUN_RECORDS_MD),
        ],
        [
            sys.executable,
            "scripts/audit_goal_completion.py",
            "--out-json",
            str(GOAL_JSON),
            "--out-md",
            str(GOAL_MD),
        ],
        [
            sys.executable,
            "scripts/write_human_input_packet.py",
            "--out-json",
            str(HUMAN_JSON),
            "--out-md",
            str(HUMAN_MD),
        ],
        [
            sys.executable,
            "scripts/write_git_sync_packet.py",
            "--out-json",
            str(GIT_JSON),
            "--out-md",
            str(GIT_MD),
        ],
        [
            sys.executable,
            "scripts/audit_git_sync_packet.py",
            "--out-json",
            str(GIT_AUDIT_JSON),
            "--out-md",
            str(GIT_AUDIT_MD),
        ],
        [
            sys.executable,
            "scripts/audit_openrouter_model_catalog.py",
            "--model",
            "anthropic/claude-sonnet-4.6",
            "--model",
            "openai/gpt-5.1-codex",
            "--model",
            "openai/gpt-5.2",
            "--model",
            "deepseek/deepseek-v3.2",
            "--model",
            "qwen/qwen3-coder-next",
            "--model",
            "z-ai/glm-5",
            "--out-json",
            str(MODEL_CATALOG_JSON),
            "--out-md",
            str(MODEL_CATALOG_MD),
        ],
    ]
    results = [run_command(command) for command in commands]
    handoff = build_handoff(results)
    write_json(Path(args.out_json), handoff)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(handoff), encoding="utf-8")
    print(
        json.dumps(
            {
                "out_json": args.out_json,
                "out_md": args.out_md,
                "commands_passed": handoff["commands_passed"],
                "ready_for_real_api": handoff["ready_for_real_api"],
                "missing_required_input_ids": handoff["missing_required_input_ids"],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    if not handoff["commands_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
