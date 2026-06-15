from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from typing import Any


REQUIRED_FILES = [
    "README.md",
    "pyproject.toml",
    ".env.example",
    "configs/api_pilot.example.json",
    "configs/api_tool_augmented_full.example.json",
    "configs/model_selection.example.json",
    "docs/INDEX.md",
    "docs/artifact/anonymous_artifact.md",
    "docs/experiments/tool_augmented_full_run_result.md",
    "docs/experiments/evp7_g5_376_statistical_analysis.md",
    "docs/experiments/model_selection_shortlist.md",
    "docs/paper/patch_verification_draft.md",
    "docs/paper/ieee_submission_draft.tex",
    "docs/figures/README.md",
    "docs/figures/figure_manifest.json",
    "docs/figures/fig1_framework.pdf",
    "docs/figures/fig2_evidence_visibility.pdf",
    "docs/figures/fig3_dataset_composition.pdf",
    "docs/figures/fig4_result_tradeoff.pdf",
    "docs/figures/fig5_claim_boundary.pdf",
    "docs/figures/fig6_evp7_visibility_curve.pdf",
    "docs/figures/imagegen/README.md",
    "docs/figures/imagegen/prompts.md",
    "docs/figures/imagegen/imagegen_framework.png",
    "docs/figures/imagegen/imagegen_evidence_boundary.png",
    "docs/figures/imagegen/imagegen_tradeoff.png",
    "docs/figures/imagegen/imagegen_claim_boundary.png",
    "scripts/build_redesign_smoke_inputs.py",
    "scripts/generate_paper_figures.py",
    "scripts/analyze_evp7_g5_statistics.py",
    "scripts/run_redesign_smoke_workflow.py",
    "scripts/run_no_api_patch_pipeline.py",
    "scripts/write_pre_api_handoff.py",
    "scripts/audit_openrouter_model_catalog.py",
    "scripts/audit_api_run_completeness.py",
    "scripts/audit_api_failure_handling.py",
    "scripts/postprocess_api_pilot_run.py",
    "scripts/write_experiment_run_records.py",
    "ARTIFACT_MANIFEST.json",
    "ARTIFACT_README.md",
]

REQUIRED_README_SNIPPETS = [
    "python scripts\\run_local_quality_gate.py",
    "python scripts\\audit_credential_boundary.py",
    "python scripts\\audit_bootstrap_safety.py",
    "python scripts\\audit_workflow_guard.py",
    "python scripts\\audit_api_failure_handling.py",
    "python scripts\\audit_command_templates.py",
    "python scripts\\write_experiment_run_records.py",
    "python scripts\\write_pre_api_handoff.py",
    "python scripts\\bootstrap_api_prereqs.py",
    "--dry-run --allow-missing-credentials",
    "python scripts\\run_api_pilot_workflow.py --config configs\\api_pilot.local.json --check-only",
    "python scripts\\run_api_pilot_workflow.py --config configs\\api_pilot.local.json --execute",
    "python scripts\\run_api_pilot_workflow.py --config configs\\api_pilot.local.json --run-dir outputs\\patch_verification_api_pilot_002 --limit 0 --execute",
    "python scripts\\postprocess_api_pilot_run.py --run-dir outputs\\patch_verification_api_pilot_002 --expected-candidates 30",
    "python scripts\\build_redesign_smoke_inputs.py --all-candidates",
    "python scripts\\run_redesign_smoke_workflow.py --config outputs\\patch_verification_tool_augmented_full_001\\api_config.local.json --gate-mode full --check-only",
    "python scripts\\run_redesign_smoke_workflow.py --config outputs\\patch_verification_tool_augmented_full_001\\api_config.local.json --gate-mode full --execute",
    "python scripts\\generate_paper_figures.py",
    "python scripts\\analyze_evp7_g5_statistics.py",
    "docs/figures/imagegen/prompts.md",
    "python scripts\\write_ieee_latex_draft.py",
    "tool_augmented_full_gate.json",
    "conditional tool-assisted verifier claim",
    "run_completeness.json",
]


def forbidden_reason(name: str) -> str | None:
    parts = set(Path(name).parts)
    for part in ["outputs", "data", "tmp", "temp", "runs", "artifacts", ".git", "__pycache__"]:
        if part in parts:
            return f"forbidden_path_part:{part}"
    path = Path(name)
    if path.name == ".env":
        return "real_env_file"
    if path.name.startswith(".env.") and path.name != ".env.example":
        return "env_variant"
    if path.name.endswith(".local.json"):
        return "local_config"
    if path.suffix in {".key", ".pem", ".pyc", ".pyo"}:
        return f"forbidden_suffix:{path.suffix}"
    return None


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def audit_zip(zip_path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(zip_path) as archive:
        names = sorted(archive.namelist())
        manifest = json.loads(archive.read("ARTIFACT_MANIFEST.json").decode("utf-8")) if "ARTIFACT_MANIFEST.json" in names else {}
        artifact_readme = archive.read("ARTIFACT_README.md").decode("utf-8") if "ARTIFACT_README.md" in names else ""
    packaged_files = [name for name in names if name not in {"ARTIFACT_MANIFEST.json", "ARTIFACT_README.md"}]
    manifest_files = sorted(manifest.get("files", [])) if isinstance(manifest, dict) else []
    forbidden = [{"path": name, "reason": forbidden_reason(name)} for name in names if forbidden_reason(name)]
    missing_required = [name for name in REQUIRED_FILES if name not in names]
    missing_readme_snippets = [snippet for snippet in REQUIRED_README_SNIPPETS if snippet not in artifact_readme]
    return {
        "artifact": zip_path.as_posix(),
        "zip_entry_count": len(names),
        "packaged_file_count": len(packaged_files),
        "manifest_file_count": manifest.get("file_count") if isinstance(manifest, dict) else None,
        "manifest_matches_zip": manifest_files == sorted(packaged_files),
        "missing_required": missing_required,
        "missing_readme_snippets": missing_readme_snippets,
        "forbidden_entries": forbidden,
        "safe": not missing_required and not missing_readme_snippets and not forbidden and manifest_files == sorted(packaged_files),
    }


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# Anonymous Artifact Audit",
        "",
        "## Summary",
        "",
        f"- artifact: `{audit['artifact']}`",
        f"- safe: {bool_mark(audit['safe'])}",
        f"- zip entries: {audit['zip_entry_count']}",
        f"- packaged files: {audit['packaged_file_count']}",
        f"- manifest file count: {audit['manifest_file_count']}",
        f"- manifest matches zip: {bool_mark(audit['manifest_matches_zip'])}",
        f"- missing required files: {len(audit['missing_required'])}",
        f"- missing README snippets: {len(audit['missing_readme_snippets'])}",
        f"- forbidden entries: {len(audit['forbidden_entries'])}",
        "",
    ]
    if audit["missing_required"]:
        lines.extend(["## Missing Required Files", ""])
        for name in audit["missing_required"]:
            lines.append(f"- `{name}`")
        lines.append("")
    if audit["missing_readme_snippets"]:
        lines.extend(["## Missing README Snippets", ""])
        for snippet in audit["missing_readme_snippets"]:
            lines.append(f"- `{snippet}`")
        lines.append("")
    if audit["forbidden_entries"]:
        lines.extend(["## Forbidden Entries", ""])
        for item in audit["forbidden_entries"]:
            lines.append(f"- `{item['path']}`: {item['reason']}")
        lines.append("")
    lines.extend(
        [
            "## Boundary",
            "",
            "This audit validates package structure and exclusion rules. It does not validate real API reproducibility because raw API outputs are intentionally excluded.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit the anonymous artifact zip structure.")
    parser.add_argument("--artifact", default="artifacts/research95_anonymous_artifact.zip")
    parser.add_argument("--out-json", default="artifacts/research95_anonymous_artifact_audit.json")
    parser.add_argument("--out-md", default="artifacts/research95_anonymous_artifact_audit.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = audit_zip(Path(args.artifact))
    write_json(Path(args.out_json), audit)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(audit), encoding="utf-8")
    print(json.dumps({"out_json": args.out_json, "out_md": args.out_md, "safe": audit["safe"]}, ensure_ascii=False, indent=2, sort_keys=True))
    if not audit["safe"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
