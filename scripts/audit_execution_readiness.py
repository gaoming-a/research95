from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


DEFAULT_PILOT_DIR = Path("outputs") / "patch_verification_pilot_001"
DEFAULT_LOCAL_CONFIG = Path("configs") / "api_pilot.local.json"
DEFAULT_MODEL_SELECTION = Path("configs") / "model_selection.local.json"


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


def git_status() -> dict[str, Any]:
    completed = subprocess.run(
        ["git", "status", "--short"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        "is_git_repo": completed.returncode == 0,
        "status_short": completed.stdout.strip().splitlines() if completed.returncode == 0 else [],
        "error": completed.stderr.strip() if completed.returncode != 0 else None,
    }


def env_values(env_path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not env_path.exists():
        return values
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def api_key_env_for_provider(api_provider: str) -> str:
    return "DEEPSEEK_API_KEY" if api_provider == "deepseek_official" else "OPENROUTER_API_KEY"


def env_has_api_key(env_path: Path, api_provider: str) -> bool:
    values = env_values(env_path)
    value = values.get(api_key_env_for_provider(api_provider), "")
    return len(value.strip()) > 20 and not value.strip().startswith("<")


def local_config_state(config_path: Path) -> dict[str, Any]:
    config = read_json(config_path)
    if config is None:
        return {
            "exists": False,
            "model_set": False,
            "model": None,
            "model_selection": None,
            "smoke_limit": None,
            "out_dir": None,
        }
    model = str(config.get("model", ""))
    model_set = bool(model) and not model.startswith("<") and "model-slug" not in model.lower()
    return {
        "exists": True,
        "api_provider": config.get("api_provider", "openrouter"),
        "model_set": model_set,
        "model": model if model_set else None,
        "model_selection": config.get("model_selection"),
        "smoke_limit": config.get("smoke_limit"),
        "out_dir": config.get("out_dir"),
    }


def model_selection_state(selection_path: Path, local_config: dict[str, Any]) -> dict[str, Any]:
    selection = read_json(selection_path)
    if selection is None:
        return {
            "path": selection_path.as_posix(),
            "exists": False,
            "selected_model": None,
            "matches_api_config": False,
            "ready": False,
        }
    primary = selection.get("primary_pilot_model", {})
    if not isinstance(primary, dict):
        primary = {}
    selected_model = primary.get("model_id") or primary.get("openrouter_slug")
    selected_provider = primary.get("api_provider", "openrouter")
    selected_model_set = bool(selected_model) and not str(selected_model).startswith("<")
    api_model = local_config.get("model")
    api_provider = local_config.get("api_provider", "openrouter")
    return {
        "path": selection_path.as_posix(),
        "exists": True,
        "selected_model": selected_model if selected_model_set else None,
        "selected_provider": selected_provider,
        "matches_api_config": bool(api_model and selected_model == api_model and selected_provider == api_provider),
        "ready": bool(selected_model_set and (not api_model or selected_model == api_model) and selected_provider == api_provider),
    }


def no_api_state(pilot_dir: Path) -> dict[str, Any]:
    dataset_summary = read_json(pilot_dir / "dataset_summary.json")
    validation_summary = read_json(pilot_dir / "validation_summary.json")
    metrics = read_json(pilot_dir / "metrics.json")

    candidates = count_jsonl(pilot_dir / "candidates.jsonl")
    evidence_packets = count_jsonl(pilot_dir / "evidence_packets.jsonl")
    verifier_outputs = count_jsonl(pilot_dir / "verifier_outputs.jsonl")
    prompt_manifest = count_jsonl(pilot_dir / "api_prompt_dry_run" / "prompt_manifest.jsonl")
    legacy_prompt_manifest = count_jsonl(Path("outputs") / "patch_verification_api_pilot_dry_run_004" / "prompt_manifest.jsonl")

    validation_passed = bool(validation_summary and validation_summary.get("all_validated"))
    api_readiness = bool(dataset_summary and dataset_summary.get("api_readiness", {}).get("ready"))
    counts_match = (
        candidates == evidence_packets
        and candidates == (dataset_summary or {}).get("candidate_count")
        and verifier_outputs == (dataset_summary or {}).get("verifier_output_count")
    )
    metrics_match = bool(
        metrics
        and metrics.get("candidate_count") == candidates
        and metrics.get("verifier_output_count") == verifier_outputs
    )

    return {
        "pilot_dir": pilot_dir.as_posix(),
        "files": {
            "dataset_summary": dataset_summary is not None,
            "validation_summary": validation_summary is not None,
            "metrics": metrics is not None,
            "candidates": candidates is not None,
            "evidence_packets": evidence_packets is not None,
            "verifier_outputs": verifier_outputs is not None,
        },
        "counts": {
            "candidates": candidates,
            "evidence_packets": evidence_packets,
            "verifier_outputs": verifier_outputs,
            "prompt_manifest_in_pilot_dir": prompt_manifest,
            "legacy_prompt_manifest": legacy_prompt_manifest,
        },
        "validation_passed": validation_passed,
        "api_readiness_flag": api_readiness,
        "candidate_evidence_metric_counts_match": bool(counts_match and metrics_match),
        "ready": bool(validation_passed and api_readiness and counts_match and metrics_match),
    }


def determine_next_actions(no_api: dict[str, Any], api: dict[str, Any], git: dict[str, Any]) -> list[str]:
    actions: list[str] = []
    if not no_api["ready"]:
        actions.append("Run `python scripts/run_no_api_patch_pipeline.py --out-dir outputs/patch_verification_pilot_001` and fix any failed gate.")
    if not api["env_has_api_key"]:
        actions.append(f"Create ignored `.env` with `{api['api_key_env']}` before any real API call.")
    if not api["model_selection"]["exists"]:
        actions.append("Choose a concrete model id and rationale, then run `python scripts/bootstrap_api_prereqs.py ... --dry-run --allow-missing-credentials`.")
    elif not api["model_selection"]["ready"]:
        actions.append("Fix `configs/model_selection.local.json` so it contains a concrete model and matches the API config.")
    if not api["local_config"]["exists"]:
        actions.append("After `.env` exists and bootstrap dry-run is correct, run strict `python scripts/bootstrap_api_prereqs.py ...` to write both ignored local configs.")
    elif not api["local_config"]["model_set"]:
        actions.append("Set a concrete model id in `configs/api_pilot.local.json`.")
    if api["env_has_api_key"] and api["local_config"]["exists"] and api["local_config"]["model_set"]:
        actions.append("Run `python scripts/preflight_api_pilot.py --config configs/api_pilot.local.json`.")
    if not git["is_git_repo"]:
        actions.append("Decide whether `research95` should become its own Git repository before claiming GitHub sync.")
    return actions


def build_audit(args: argparse.Namespace) -> dict[str, Any]:
    pilot_dir = Path(args.pilot_dir)
    env_path = Path(args.env)
    config_path = Path(args.local_config)
    model_selection_path = Path(args.model_selection)
    no_api = no_api_state(pilot_dir)
    git = git_status()
    local_config = local_config_state(config_path)
    if local_config.get("api_provider"):
        api_provider = str(local_config["api_provider"])
    elif env_has_api_key(env_path, "deepseek_official"):
        api_provider = "deepseek_official"
    else:
        api_provider = "openrouter"
    api = {
        "env_path": env_path.as_posix(),
        "env_exists": env_path.exists(),
        "api_provider": api_provider,
        "api_key_env": api_key_env_for_provider(api_provider),
        "env_has_api_key": env_has_api_key(env_path, api_provider),
        "env_has_openrouter_key": env_has_api_key(env_path, "openrouter"),
        "env_has_deepseek_key": env_has_api_key(env_path, "deepseek_official"),
        "local_config": local_config,
        "model_selection": model_selection_state(model_selection_path, local_config),
    }
    next_actions = determine_next_actions(no_api, api, git)
    return {
        "overall_ready_for_real_api": bool(
            no_api["ready"]
            and api["env_has_api_key"]
            and api["local_config"]["exists"]
            and api["local_config"]["model_set"]
            and api["model_selection"]["ready"]
        ),
        "no_api": no_api,
        "api": api,
        "git": git,
        "next_actions": next_actions,
    }


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def build_markdown(audit: dict[str, Any]) -> str:
    no_api = audit["no_api"]
    api = audit["api"]
    git = audit["git"]
    lines = [
        "# Research95 Execution Readiness Audit",
        "",
        "## Summary",
        "",
        f"- ready for real API: {bool_mark(audit['overall_ready_for_real_api'])}",
        f"- no-API pipeline ready: {bool_mark(no_api['ready'])}",
        f"- API provider: `{api['api_provider']}`",
        f"- `.env` has provider key `{api['api_key_env']}`: {bool_mark(api['env_has_api_key'])}",
        f"- local API config exists: {bool_mark(api['local_config']['exists'])}",
        f"- local API model set: {bool_mark(api['local_config']['model_set'])}",
        f"- model selection ready: {bool_mark(api['model_selection']['ready'])}",
        f"- git repository: {bool_mark(git['is_git_repo'])}",
        "",
        "## No-API State",
        "",
        f"- pilot dir: `{no_api['pilot_dir']}`",
        f"- counts: `{no_api['counts']}`",
        f"- validation passed: {bool_mark(no_api['validation_passed'])}",
        f"- API readiness flag: {bool_mark(no_api['api_readiness_flag'])}",
        f"- counts match: {bool_mark(no_api['candidate_evidence_metric_counts_match'])}",
        "",
        "## API State",
        "",
        f"- env path: `{api['env_path']}`",
        f"- env exists: {bool_mark(api['env_exists'])}",
        f"- local config: `{api['local_config']}`",
        f"- model selection: `{api['model_selection']}`",
        "",
        "## Git State",
        "",
        f"- is git repo: {bool_mark(git['is_git_repo'])}",
        f"- error: `{git['error']}`",
        "",
        "## Next Actions",
        "",
    ]
    if audit["next_actions"]:
        for action in audit["next_actions"]:
            lines.append(f"- {action}")
    else:
        lines.append("- Run the real API preflight and smoke pilot.")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit execution readiness for the Research95 plan.")
    parser.add_argument("--pilot-dir", default=str(DEFAULT_PILOT_DIR))
    parser.add_argument("--env", default=".env")
    parser.add_argument("--local-config", default=str(DEFAULT_LOCAL_CONFIG))
    parser.add_argument("--model-selection", default=str(DEFAULT_MODEL_SELECTION))
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = build_audit(args)
    write_json(Path(args.out_json), audit)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(audit), encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
