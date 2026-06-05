from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


STATUS_COMPLETE = "complete"
STATUS_BLOCKED = "blocked"
STATUS_PENDING = "pending"
STATUS_INCOMPLETE = "incomplete"
STATUS_PARTIAL = "partial"


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def count_jsonl(path: Path) -> int | None:
    if not path.exists():
        return None
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def stage(stage_id: str, name: str, status: str, evidence: list[str], next_action: str | None = None) -> dict[str, Any]:
    return {
        "id": stage_id,
        "name": name,
        "status": status,
        "evidence": evidence,
        "next_action": next_action,
    }


def readiness_state() -> dict[str, Any]:
    return read_json(Path("outputs") / "readiness_audit" / "latest.json") or {}


def local_quality_state() -> dict[str, Any]:
    return read_json(Path("outputs") / "local_quality_gate" / "latest.json") or {}


def paper_state() -> dict[str, Any]:
    return read_json(Path("outputs") / "paper_readiness" / "latest.json") or {}


def file_exists(path: str) -> bool:
    return Path(path).exists()


def build_progress() -> dict[str, Any]:
    readiness = readiness_state()
    quality = local_quality_state()
    paper = paper_state()
    pipeline_summary = read_json(Path("outputs") / "patch_verification_pilot_repro_001" / "pipeline_summary.json")
    repro_compare = read_json(Path("outputs") / "reproducibility" / "pilot_compare.json")
    workflow_check = read_json(Path("outputs") / "api_workflow_check" / "latest.json")
    artifact_manifest = read_json(Path("artifacts") / "research95_anonymous_artifact_manifest_dry_run.json")

    no_api = readiness.get("no_api", {}) if isinstance(readiness, dict) else {}
    api = readiness.get("api", {}) if isinstance(readiness, dict) else {}
    git = readiness.get("git", {}) if isinstance(readiness, dict) else {}
    local_config = api.get("local_config", {}) if isinstance(api, dict) else {}
    model_selection = api.get("model_selection", {}) if isinstance(api, dict) else {}
    api_provider = api.get("api_provider", "unknown") if isinstance(api, dict) else "unknown"
    api_key_env = api.get("api_key_env", "provider API key") if isinstance(api, dict) else "provider API key"

    stages: list[dict[str, Any]] = []

    stages.append(
        stage(
            "0",
            "状态审计",
            STATUS_COMPLETE if readiness else STATUS_INCOMPLETE,
            [
                "outputs/readiness_audit/latest.json exists" if readiness else "missing outputs/readiness_audit/latest.json",
                f"no_api_ready={no_api.get('ready')}",
                f"overall_ready_for_real_api={readiness.get('overall_ready_for_real_api')}",
            ],
            None if readiness else "Run scripts/audit_execution_readiness.py.",
        )
    )

    no_api_complete = bool(
        pipeline_summary
        and pipeline_summary.get("candidate_count") == 30
        and pipeline_summary.get("verifier_output_count") == 90
        and pipeline_summary.get("all_validated") is True
        and pipeline_summary.get("prompt_count") == 60
    )
    stages.append(
        stage(
            "1",
            "no-API pipeline 复现",
            STATUS_COMPLETE if no_api_complete else STATUS_INCOMPLETE,
            [
                f"candidate_count={pipeline_summary.get('candidate_count') if pipeline_summary else None}",
                f"verifier_output_count={pipeline_summary.get('verifier_output_count') if pipeline_summary else None}",
                f"all_validated={pipeline_summary.get('all_validated') if pipeline_summary else None}",
                f"prompt_count={pipeline_summary.get('prompt_count') if pipeline_summary else None}",
            ],
            None if no_api_complete else "Run scripts/run_no_api_patch_pipeline.py.",
        )
    )

    repro_complete = bool(repro_compare and repro_compare.get("matched") is True)
    stages.append(
        stage(
            "2",
            "deterministic 输出可复现性对比",
            STATUS_COMPLETE if repro_complete else STATUS_INCOMPLETE,
            [
                f"matched={repro_compare.get('matched') if repro_compare else None}",
                f"checked_file_count={repro_compare.get('checked_file_count') if repro_compare else None}",
                f"mismatches={len(repro_compare.get('mismatches', [])) if repro_compare else None}",
            ],
            None if repro_complete else "Run scripts/write_reproducibility_manifest.py for original and repro runs.",
        )
    )

    model_ready = bool(model_selection.get("ready"))
    stages.append(
        stage(
            "3",
            "模型选择 local config",
            STATUS_COMPLETE if model_ready else STATUS_BLOCKED,
            [
                f"configs/model_selection.local.json exists={model_selection.get('exists')}",
                f"selected_model={model_selection.get('selected_model')}",
                f"ready={model_selection.get('ready')}",
            ],
            None
            if model_ready
            else "Human must provide a concrete provider model id and selection rationale, then run scripts/bootstrap_api_prereqs.py --api-provider deepseek_official --dry-run --allow-missing-credentials.",
        )
    )

    api_config_ready = bool(api.get("env_has_api_key") and local_config.get("exists") and local_config.get("model_set"))
    stages.append(
        stage(
            "4",
            "API local config 与 preflight 前置条件",
            STATUS_COMPLETE if api_config_ready and readiness.get("overall_ready_for_real_api") else STATUS_BLOCKED,
            [
                f".env exists={api.get('env_exists')}",
                f"api_provider={api_provider}",
                f".env has {api_key_env}={api.get('env_has_api_key')}",
                f"api local config exists={local_config.get('exists')}",
                f"api model set={local_config.get('model_set')}",
                f"overall_ready_for_real_api={readiness.get('overall_ready_for_real_api')}",
            ],
            None
            if api_config_ready and readiness.get("overall_ready_for_real_api")
            else "Create .env with the provider key, confirm bootstrap dry-run, then run strict scripts/bootstrap_api_prereqs.py to write both local configs and preflight.",
        )
    )

    check_only_passed = bool(
        workflow_check
        and workflow_check.get("mode") == "check_only"
        and workflow_check.get("model_call_attempted") is False
        and workflow_check.get("api_ready") is True
    )
    check_only_seen = bool(workflow_check and workflow_check.get("model_call_attempted") is False)
    stages.append(
        stage(
            "5",
            "guarded workflow check-only",
            STATUS_COMPLETE if check_only_passed else STATUS_BLOCKED if not api_config_ready else STATUS_INCOMPLETE,
            [
                f"check_only_seen={check_only_seen}",
                f"api_ready={workflow_check.get('api_ready') if workflow_check else None}",
                f"model_call_attempted={workflow_check.get('model_call_attempted') if workflow_check else None}",
            ],
            None if check_only_passed else "Run scripts/run_api_pilot_workflow.py --check-only after API prerequisites are present.",
        )
    )

    smoke_run_dir = Path("outputs") / "patch_verification_api_pilot_001_tokens4096"
    smoke_reviews = count_jsonl(smoke_run_dir / "reviews.jsonl")
    smoke_metrics = read_json(smoke_run_dir / "metrics.json")
    smoke_completeness = read_json(smoke_run_dir / "run_completeness.json")
    smoke_groups = (smoke_metrics or {}).get("groups", {}) if isinstance(smoke_metrics, dict) else {}
    smoke_invalid_rates = [
        group.get("invalid_output_rate")
        for group in smoke_groups.values()
        if isinstance(group, dict) and group.get("invalid_output_rate") is not None
    ]
    smoke_invalid_ok = bool(smoke_invalid_rates and max(float(value) for value in smoke_invalid_rates) <= 0.2)
    smoke_real = bool(
        smoke_reviews == 4
        and smoke_metrics
        and smoke_metrics.get("mock_review_count", 0) == 0
        and smoke_completeness
        and smoke_completeness.get("passed") is True
        and smoke_invalid_ok
    )
    stages.append(
        stage(
            "6",
            "真实 API smoke run",
            STATUS_COMPLETE if smoke_real else STATUS_BLOCKED,
            [
                f"run_dir={smoke_run_dir.as_posix()}",
                f"reviews={smoke_reviews}",
                f"mock_review_count={smoke_metrics.get('mock_review_count') if smoke_metrics else None}",
                f"run_completeness_passed={smoke_completeness.get('passed') if smoke_completeness else None}",
                f"invalid_output_rates={smoke_invalid_rates}",
            ],
            None
            if smoke_real
            else "Run a 2-candidate real API smoke after Stage 5 passes; require completeness and invalid_output_rate <= 0.2 before full run.",
        )
    )

    full_reviews = count_jsonl(Path("outputs") / "patch_verification_api_pilot_002" / "reviews.jsonl")
    full_metrics = read_json(Path("outputs") / "patch_verification_api_pilot_002" / "metrics.json")
    full_real = bool(full_reviews == 60 and full_metrics and full_metrics.get("mock_review_count", 0) == 0)
    stages.append(
        stage(
            "7",
            "真实 API full run",
            STATUS_COMPLETE if full_real else STATUS_PENDING if smoke_real else STATUS_BLOCKED,
            [
                f"reviews={full_reviews}",
                f"mock_review_count={full_metrics.get('mock_review_count') if full_metrics else None}",
            ],
            None
            if full_real
            else "Run a 30-candidate full API run after smoke passes with scripts/run_api_pilot_workflow.py --run-dir outputs/patch_verification_api_pilot_002 --limit 0 --execute.",
        )
    )

    full_run_dir = Path("outputs") / "patch_verification_api_pilot_002"
    run_completeness = read_json(full_run_dir / "run_completeness.json")
    run_completeness_passed = bool(
        run_completeness
        and run_completeness.get("passed") is True
        and run_completeness.get("expected_records") == 60
        and run_completeness.get("review_count") == 60
        and run_completeness.get("mock_review_count") == 0
    )
    postprocess_complete = all(
        (full_run_dir / name).exists()
        for name in [
            "api_pilot_report.md",
            "failure_examples.json",
            "failure_examples.md",
            "gate_report.json",
            "gate_report.md",
            "run_completeness.json",
            "run_completeness.md",
            "paper_readiness.json",
            "paper_readiness.md",
            "postprocess_summary.json",
        ]
    ) and run_completeness_passed
    stages.append(
        stage(
            "8",
            "full run 后处理",
            STATUS_COMPLETE if postprocess_complete else STATUS_PENDING if full_real else STATUS_BLOCKED,
            [
                f"postprocess_files_complete={postprocess_complete}",
                f"run_completeness_passed={run_completeness_passed}",
                f"expected_records={run_completeness.get('expected_records') if run_completeness else None}",
                f"review_count={run_completeness.get('review_count') if run_completeness else None}",
                f"mock_review_count={run_completeness.get('mock_review_count') if run_completeness else None}",
            ],
            None
            if postprocess_complete
            else "Run scripts/postprocess_api_pilot_run.py --run-dir outputs/patch_verification_api_pilot_002 --expected-candidates 30 on the full real API run directory.",
        )
    )

    gate = read_json(full_run_dir / "gate_report.json")
    verdict = gate.get("verdict") if gate else None
    tool_augmented_run_dir = Path("outputs") / "patch_verification_tool_augmented_full_001"
    tool_augmented_gate = read_json(tool_augmented_run_dir / "tool_augmented_full_gate.json")
    tool_augmented_gate_passed = bool(
        tool_augmented_gate
        and tool_augmented_gate.get("passed") is True
        and tool_augmented_gate.get("mock_review_count") == 0
        and (tool_augmented_gate.get("condition_counts") or {}) == {"tool_augmented_evidence": 30}
    )
    prompt_only_gate_interpreted = bool(gate and verdict == "stop_or_redesign" and gate.get("mock_review_count") == 0)
    stages.append(
        stage(
            "9",
            "结果 gate 判定与 redesign 分流",
            STATUS_COMPLETE
            if (verdict == "continue" or (prompt_only_gate_interpreted and tool_augmented_gate_passed))
            else STATUS_PENDING
            if gate
            else STATUS_BLOCKED,
            [
                f"prompt_only_verdict={verdict}",
                f"prompt_only_mock_review_count={gate.get('mock_review_count') if gate else None}",
                f"tool_augmented_gate_passed={tool_augmented_gate_passed}",
                f"tool_augmented_mock_review_count={tool_augmented_gate.get('mock_review_count') if tool_augmented_gate else None}",
            ],
            None
            if (verdict == "continue" or (prompt_only_gate_interpreted and tool_augmented_gate_passed))
            else "Interpret gate_report.json and tool_augmented_full_gate.json before writing claims.",
        )
    )

    failures = read_json(full_run_dir / "failure_examples.json")
    failures_ready = bool(failures and failures.get("mock_review_count") == 0)
    stages.append(
        stage(
            "10",
            "failure analysis",
            STATUS_COMPLETE if failures_ready else STATUS_PENDING if full_real else STATUS_BLOCKED,
            [
                f"failure_examples_exists={bool(failures)}",
                f"mock_review_count={failures.get('mock_review_count') if failures else None}",
                f"bucket_counts={failures.get('bucket_counts') if failures else None}",
            ],
            None if failures_ready else "Extract and manually inspect real API failure examples.",
        )
    )

    prompt_only_positive_ready = bool(paper.get("prompt_only_positive_claim_ready", paper.get("positive_claim_ready")))
    tool_augmented_positive_ready = bool(paper.get("tool_augmented_claim_ready"))
    methods_ready = bool(paper.get("negative_or_methods_draft_ready"))
    stages.append(
        stage(
            "11",
            "论文 readiness 与正文更新",
            STATUS_COMPLETE if tool_augmented_positive_ready and methods_ready else STATUS_PARTIAL if methods_ready else STATUS_INCOMPLETE,
            [
                f"prompt_only_positive_claim_ready={prompt_only_positive_ready}",
                f"tool_augmented_claim_ready={tool_augmented_positive_ready}",
                f"methods_or_negative_draft_ready={paper.get('negative_or_methods_draft_ready')}",
                f"claim_boundary={paper.get('claim_boundary')}",
            ],
            None
            if tool_augmented_positive_ready and methods_ready
            else "Keep prompt-only as a negative result and only use the tool-augmented gate for the conditional tool-assisted claim.",
        )
    )

    artifact_ready = bool(artifact_manifest and artifact_manifest.get("blocked") is not True)
    stages.append(
        stage(
            "12",
            "匿名 artifact",
            STATUS_PARTIAL if artifact_ready and not full_real else STATUS_COMPLETE if artifact_ready and full_real else STATUS_INCOMPLETE,
            [
                f"artifact_manifest_exists={bool(artifact_manifest)}",
                f"full_real_api_available={full_real}",
            ],
            "Regenerate artifact after real API outputs are summarized; keep raw outputs excluded."
            if artifact_ready and not full_real
            else None,
        )
    )

    quality_complete = bool(quality.get("passed"))
    stages.append(
        stage(
            "13",
            "本地质量门",
            STATUS_COMPLETE if quality_complete else STATUS_INCOMPLETE,
            [
                f"passed={quality.get('passed')}",
                f"compile_passed={(quality.get('compile') or {}).get('passed')}",
                f"sensitive_scan_passed={(quality.get('sensitive_scan') or {}).get('passed')}",
            ],
            None if quality_complete else "Run scripts/run_local_quality_gate.py and fix failures.",
        )
    )

    counts: dict[str, int] = {}
    for item in stages:
        counts[item["status"]] = counts.get(item["status"], 0) + 1

    next_actions = []
    for item in stages:
        if item["status"] != STATUS_COMPLETE and item.get("next_action"):
            next_actions.append({"stage": item["id"], "action": item["next_action"]})
            if len(next_actions) >= 5:
                break

    return {
        "plan": "docs/plans/ai_agent_experiment_execution_plan_zh.md",
        "stage_counts": counts,
        "stages": stages,
        "next_actions": next_actions,
        "ready_for_real_api": bool(readiness.get("overall_ready_for_real_api")),
        "prompt_only_positive_paper_claim_ready": prompt_only_positive_ready,
        "tool_augmented_paper_claim_ready": tool_augmented_positive_ready,
        "positive_paper_claim_ready": tool_augmented_positive_ready,
        "git_repo": bool(git_state(readiness)),
    }


def git_state(readiness: dict[str, Any]) -> bool:
    git = readiness.get("git", {}) if isinstance(readiness, dict) else {}
    return bool(git.get("is_git_repo"))


def build_markdown(progress: dict[str, Any]) -> str:
    lines = [
        "# AI Plan Progress Audit",
        "",
        "## Summary",
        "",
        f"- plan: `{progress['plan']}`",
        f"- ready for real API: {bool_mark(progress['ready_for_real_api'])}",
        f"- prompt-only positive paper claim ready: {bool_mark(progress['prompt_only_positive_paper_claim_ready'])}",
        f"- tool-augmented paper claim ready: {bool_mark(progress['tool_augmented_paper_claim_ready'])}",
        f"- git repository: {bool_mark(progress['git_repo'])}",
        f"- stage counts: `{progress['stage_counts']}`",
        "",
        "## Stages",
        "",
        "| stage | status | name | evidence | next action |",
        "|---|---|---|---|---|",
    ]
    for item in progress["stages"]:
        evidence = "<br>".join(str(value) for value in item["evidence"])
        next_action = item["next_action"] or ""
        lines.append(f"| {item['id']} | `{item['status']}` | {item['name']} | {evidence} | {next_action} |")
    lines.extend(["", "## Next Actions", ""])
    if progress["next_actions"]:
        for item in progress["next_actions"]:
            lines.append(f"- Stage {item['stage']}: {item['action']}")
    else:
        lines.append("- None.")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit progress against the AI execution plan.")
    parser.add_argument("--out-json", default="outputs/plan_progress/latest.json")
    parser.add_argument("--out-md", default="outputs/plan_progress/latest.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    progress = build_progress()
    write_json(Path(args.out_json), progress)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(progress), encoding="utf-8")
    print(json.dumps({"out_json": args.out_json, "out_md": args.out_md, "stage_counts": progress["stage_counts"]}, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
