from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path
from typing import Any


DEFAULT_OUT = Path("artifacts") / "research95_anonymous_artifact.zip"

INCLUDE_ROOT_FILES = [
    ".env.example",
    ".gitignore",
    "README.md",
    "pyproject.toml",
]
INCLUDE_DIRS = [
    "configs",
    "docs",
    "examples",
    "scripts",
    "src",
]
EXCLUDED_PARTS = {
    "__pycache__",
    ".git",
    ".pytest_cache",
    ".tox",
    ".venv",
    "artifacts",
    "data",
    "env",
    "outputs",
    "runs",
    "temp",
    "tmp",
    "venv",
}
EXCLUDED_SUFFIXES = {
    ".key",
    ".pem",
    ".pyc",
    ".pyo",
}
EXCLUDED_NAME_PATTERNS = [
    ".env",
    ".local.json",
]

def should_exclude(path: Path) -> bool:
    parts = set(path.parts)
    if parts.intersection(EXCLUDED_PARTS):
        return True
    if path.suffix in EXCLUDED_SUFFIXES:
        return True
    name = path.name
    if name == ".env":
        return True
    return any(name.endswith(pattern) for pattern in EXCLUDED_NAME_PATTERNS)


def iter_files() -> list[Path]:
    files: list[Path] = []
    for root_file in INCLUDE_ROOT_FILES:
        path = Path(root_file)
        if path.exists() and not should_exclude(path):
            files.append(path)
    for include_dir in INCLUDE_DIRS:
        root = Path(include_dir)
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and not should_exclude(path):
                files.append(path)
    return sorted(set(files), key=lambda value: value.as_posix())


def text_violations(path: Path) -> list[str]:
    if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip"}:
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    violations: list[str] = []
    literal_checks = {
        "openrouter_key_prefix": "".join(["sk-", "or-v1"]),
        "windows_user_path": "".join(["C:", "\\", "Users"]),
        "local_workspace_path": "".join(["D:", "\\", "mgao"]),
        "local_user_name": " ".join(["Ming", "Gao"]),
        "wsl_workspace_path": "/".join(["", "mnt", "d", "mgao"]),
        "local_coder_model_slug": ".".join(["models", "coder", "local"]),
        "local_weak_model_slug": ".".join(["models", "weak", "local"]),
        "local_matched_model_slug": ".".join(["models", "matched", "local"]),
    }
    for label, needle in literal_checks.items():
        if needle in text:
            violations.append(label)
    env_assignment = re.compile(
        "".join(["OPENROUTER", "_API", "_KEY"]) + r"\s*=\s*(?!<your-openrouter-key>)(?!$)[A-Za-z0-9_-]{20,}"
    )
    if env_assignment.search(text):
        violations.append("concrete_openrouter_env_assignment")
    deepseek_env_assignment = re.compile(
        "".join(["DEEPSEEK", "_API", "_KEY"]) + r"\s*=\s*(?!<your-deepseek-key>)(?!$)[A-Za-z0-9_-]{20,}"
    )
    if deepseek_env_assignment.search(text):
        violations.append("concrete_deepseek_env_assignment")
    return violations


def validate_files(files: list[Path]) -> dict[str, Any]:
    violations: list[dict[str, Any]] = []
    for path in files:
        hits = text_violations(path)
        if hits:
            violations.append({"path": path.as_posix(), "hits": hits})
    return {
        "file_count": len(files),
        "violations": violations,
        "safe_to_package": not violations,
    }


def artifact_readme(manifest: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Research95 Anonymous Artifact",
            "",
            "This package contains source code, configuration templates, prompts, schemas, plans, and paper/dataset documentation for the patch-verification study.",
            "",
            "It intentionally excludes local credentials, raw API outputs, benchmark checkouts, temporary workdirs, and generated archives.",
            "",
            "## Reproduce The No-API Pipeline",
            "",
            "```powershell",
            "python scripts\\run_no_api_patch_pipeline.py --out-dir outputs\\patch_verification_pilot_repro_001",
            "```",
            "",
            "## Local Quality And Readiness",
            "",
            "```powershell",
            "python scripts\\run_local_quality_gate.py --out-json outputs\\local_quality_gate\\latest.json --out-md outputs\\local_quality_gate\\latest.md",
            "python scripts\\audit_execution_readiness.py --out-json outputs\\readiness_audit\\latest.json --out-md outputs\\readiness_audit\\latest.md",
            "python scripts\\audit_ai_plan_progress.py --out-json outputs\\plan_progress\\latest.json --out-md outputs\\plan_progress\\latest.md",
            "python scripts\\audit_goal_completion.py --out-json outputs\\goal_completion\\latest.json --out-md outputs\\goal_completion\\latest.md",
            "python scripts\\audit_paper_readiness.py --out-json outputs\\paper_readiness\\latest.json --out-md outputs\\paper_readiness\\latest.md",
            "python scripts\\audit_submission_handoff.py --out-json outputs\\submission_handoff_audit\\latest.json --out-md outputs\\submission_handoff_audit\\latest.md",
            "python scripts\\write_experiment_run_records.py --out-json outputs\\experiment_run_records\\latest.json --out-md outputs\\experiment_run_records\\latest.md",
            "```",
            "",
            "## Safety Gates",
            "",
            "```powershell",
            "python scripts\\audit_credential_boundary.py --out-json outputs\\credential_boundary\\latest.json --out-md outputs\\credential_boundary\\latest.md",
            "python scripts\\audit_bootstrap_safety.py --out-json outputs\\bootstrap_safety\\latest.json --out-md outputs\\bootstrap_safety\\latest.md",
            "python scripts\\audit_workflow_guard.py --out-json outputs\\workflow_guard\\latest.json --out-md outputs\\workflow_guard\\latest.md",
            "python scripts\\audit_api_failure_handling.py --out-json outputs\\api_failure_handling\\latest.json --out-md outputs\\api_failure_handling\\latest.md",
            "python scripts\\audit_command_templates.py --out-json outputs\\command_templates\\latest.json --out-md outputs\\command_templates\\latest.md",
            "```",
            "",
            "## Pre-API Handoff",
            "",
            "```powershell",
            "python scripts\\write_pre_api_handoff.py --out-json outputs\\handoff\\pre_api_handoff.json --out-md outputs\\handoff\\pre_api_handoff.md",
            "```",
            "",
            "## Real API Runs",
            "",
            "Real API runs currently use the DeepSeek official API. They require an untracked `.env` containing `DEEPSEEK_API_KEY` and ignored local configs generated from a concrete provider model id.",
            "",
            "```powershell",
            "python scripts\\bootstrap_api_prereqs.py --model deepseek-v4-pro --api-provider deepseek_official --provider DeepSeek --selection-source \"DeepSeek official API docs and user-confirmed primary model\" --selection-source-url https://api-docs.deepseek.com --capability-source \"DeepSeek official V4 model family\" --capability-band \"single documented primary pilot model\" --reason \"Use DeepSeek V4 Pro through the official DeepSeek API for a within-model llm_only versus evidence_first comparison, controlling base-model capability.\" --dry-run --allow-missing-credentials",
            "python scripts\\bootstrap_api_prereqs.py --model deepseek-v4-pro --api-provider deepseek_official --provider DeepSeek --selection-source \"DeepSeek official API docs and user-confirmed primary model\" --selection-source-url https://api-docs.deepseek.com --capability-source \"DeepSeek official V4 model family\" --capability-band \"single documented primary pilot model\" --reason \"Use DeepSeek V4 Pro through the official DeepSeek API for a within-model llm_only versus evidence_first comparison, controlling base-model capability.\"",
            "python scripts\\run_api_pilot_workflow.py --config configs\\api_pilot.local.json --check-only --summary-out outputs\\api_workflow_check\\latest.json",
            "python scripts\\run_api_pilot_workflow.py --config configs\\api_pilot.local.json --execute",
            "python scripts\\run_api_pilot_workflow.py --config configs\\api_pilot.local.json --run-dir outputs\\patch_verification_api_pilot_002 --limit 0 --execute",
            "python scripts\\postprocess_api_pilot_run.py --run-dir outputs\\patch_verification_api_pilot_002 --expected-candidates 30",
            "python scripts\\build_redesign_smoke_inputs.py --all-candidates --out-dir outputs\\patch_verification_tool_augmented_full_001\\inputs",
            "python scripts\\run_redesign_smoke_workflow.py --config outputs\\patch_verification_tool_augmented_full_001\\api_config.local.json --gate-mode full --check-only --summary-out outputs\\tool_augmented_full_workflow\\check_only.json",
            "python scripts\\run_redesign_smoke_workflow.py --config outputs\\patch_verification_tool_augmented_full_001\\api_config.local.json --gate-mode full --execute --summary-out outputs\\tool_augmented_full_workflow\\executed.json",
            "```",
            "",
            "Do not run the strict bootstrap command until `.env` exists and the dry-run output has been checked. Do not treat dry-run or mock outputs as model results. Prompt-only full-run paper claims require `run_completeness.json` with 60 non-mock records. The revised positive claim is separate: it requires a 30-record non-mock `tool_augmented_evidence` run with `tool_augmented_full_gate.json` passing. This is a conditional tool-assisted verifier claim, not a prompt-only model-ability claim.",
            "",
            "## Paper Draft",
            "",
            "The current paper framing is `Evidence Visibility Matters: A Systematic Study of LLM-Based Verification for Candidate Patches`. The canonical roadmap is `docs/plans/final_paper_roadmap_zh.md`; the active protocol entry is `docs/protocol/evidence_visibility_protocol.md`; the protocol pilot report is `docs/experiments/evp7_protocol_pilot.md`. Together they record the current 21-task / 98-candidate / 392-packet EVP-7 structural state, the historical 20-task / 94-candidate / 376-record real G5 run boundary, and the visible/hidden evidence boundary.",
            "",
            "The final submission checklist is `docs/artifact/submission_checklist.md`. It records the current paper package, required seven PDF figures, claim-boundary evidence, rebuild commands, audit commands, anonymous artifact commands, exclusion boundary, and ready-to-submit criteria. The no-API submission handoff is `docs/artifact/submission_handoff_20260618.md`; it records the latest PDF/artifact rebuild, readiness audits, default next action, and forbidden experiment actions without explicit user confirmation. The advisor-facing workload response is `docs/paper/advisor_workload_response_zh.md`; it explains why the current paper package is a candidate-patch verification pipeline rather than only a prompt comparison while preserving the bounded EVP-7 claim boundary.",
            "",
            "```powershell",
            "python scripts\\analyze_evp7_g5_statistics.py",
            "python scripts\\analyze_evp7_utility_sensitivity.py",
            "python scripts\\audit_paper_claim_boundary.py",
            "python scripts\\write_paper_tables.py",
            "python scripts\\generate_paper_figures.py",
            "python scripts\\write_ieee_latex_draft.py",
            "pdflatex -interaction=nonstopmode -halt-on-error -output-directory=outputs\\latex_build docs\\paper\\ieee_submission_draft.tex",
            "```",
            "",
            "The generated `docs/paper/ieee_submission_draft.tex` is the current IEEEtran submission draft. It references seven PDF figures from `docs/figures/`, including `docs/figures/fig7_decision_metric_flow.pdf`. The `docs/figures/imagegen/prompts.md` file records optional raster visual-candidate prompts for graphical abstracts or slides; those PNGs are not replacements for exact numeric/vector evidence figures. The old `docs/paper/ieee_preapi_draft.tex` is retained only as historical pre-API context.",
            "",
            "## Manifest Summary",
            "",
            f"- packaged files: {manifest['file_count']}",
            f"- validation safe to package: {manifest['validation']['safe_to_package']}",
            "",
        ]
    )


def write_zip(files: list[Path], out: Path, manifest: dict[str, Any]) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fixed_date = (2026, 1, 1, 0, 0, 0)
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            info = zipfile.ZipInfo(path.as_posix(), fixed_date)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
        for name, content in {
            "ARTIFACT_MANIFEST.json": json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            "ARTIFACT_README.md": artifact_readme(manifest),
        }.items():
            info = zipfile.ZipInfo(name, fixed_date)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare an anonymous supplemental artifact package.")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--manifest-out", default="artifacts/research95_anonymous_artifact_manifest.json")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    files = iter_files()
    validation = validate_files(files)
    manifest = {
        "artifact_name": "research95_anonymous_artifact",
        "file_count": len(files),
        "included_roots": INCLUDE_ROOT_FILES + INCLUDE_DIRS,
        "excluded_parts": sorted(EXCLUDED_PARTS),
        "files": [path.as_posix() for path in files],
        "validation": validation,
    }
    if not validation["safe_to_package"]:
        print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
        raise SystemExit("artifact validation failed; refusing to package")
    manifest_out = Path(args.manifest_out)
    write_json(manifest_out, manifest)
    if not args.dry_run:
        write_zip(files, Path(args.out), manifest)
    print(
        json.dumps(
            {
                "artifact": None if args.dry_run else args.out,
                "dry_run": args.dry_run,
                "file_count": len(files),
                "manifest": args.manifest_out,
                "safe_to_package": validation["safe_to_package"],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
