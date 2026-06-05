from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


REQUIRED_GITIGNORE_LINES = {
    ".env",
    ".env.*",
    "!.env.example",
    "*.key",
    "*.pem",
    "configs/*.local.json",
}


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_gitignore_lines(path: Path) -> set[str]:
    if not path.exists():
        return set()
    lines = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            lines.add(stripped)
    return lines


def parse_env_values(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def git_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def git_state() -> dict[str, Any]:
    status = git_command(["status", "--short"])
    return {
        "is_repo": status.returncode == 0,
        "error": status.stderr.strip() if status.returncode != 0 else "",
    }


def tracked_secret_files() -> list[str]:
    tracked = git_command(["ls-files", "--", ".env", ".env.*", "configs/*.local.json", "*.key", "*.pem"])
    if tracked.returncode != 0:
        return []
    allowed_templates = {".env.example"}
    return [line for line in tracked.stdout.splitlines() if line.strip() and line.strip() not in allowed_templates]


def check_gitignore() -> dict[str, Any]:
    lines = read_gitignore_lines(Path(".gitignore"))
    missing = sorted(REQUIRED_GITIGNORE_LINES - lines)
    return {
        "passed": not missing,
        "path": ".gitignore",
        "missing_required_lines": missing,
        "required_lines": sorted(REQUIRED_GITIGNORE_LINES),
    }


def check_env_example() -> dict[str, Any]:
    path = Path(".env.example")
    values = parse_env_values(path)
    openrouter_key_value = values.get("OPENROUTER_API_KEY")
    openrouter_base_url = values.get("OPENROUTER_BASE_URL")
    deepseek_key_value = values.get("DEEPSEEK_API_KEY")
    deepseek_base_url = values.get("DEEPSEEK_BASE_URL")
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    passed = bool(
        path.exists()
        and openrouter_key_value == "<your-openrouter-key>"
        and openrouter_base_url == "https://openrouter.ai/api/v1"
        and deepseek_key_value == "<your-deepseek-key>"
        and deepseek_base_url == "https://api.deepseek.com"
        and "Never commit .env" in text
    )
    return {
        "passed": passed,
        "path": path.as_posix(),
        "exists": path.exists(),
        "openrouter_api_key_placeholder_ok": openrouter_key_value == "<your-openrouter-key>",
        "openrouter_base_url_ok": openrouter_base_url == "https://openrouter.ai/api/v1",
        "deepseek_api_key_placeholder_ok": deepseek_key_value == "<your-deepseek-key>",
        "deepseek_base_url_ok": deepseek_base_url == "https://api.deepseek.com",
        "safety_comment_present": "Never commit .env" in text,
    }


def check_env_file_boundary(git: dict[str, Any]) -> dict[str, Any]:
    env_exists = Path(".env").exists()
    tracked = tracked_secret_files() if git["is_repo"] else []
    return {
        "passed": not tracked,
        "env_exists": env_exists,
        "git_repo": git["is_repo"],
        "tracked_secret_files": tracked,
        "note": "If .env exists, it must remain untracked and must never be packaged.",
    }


def build_audit() -> dict[str, Any]:
    git = git_state()
    checks = {
        "gitignore": check_gitignore(),
        "env_example": check_env_example(),
        "env_file_boundary": check_env_file_boundary(git),
    }
    return {
        "passed": all(item["passed"] for item in checks.values()),
        "git": git,
        "checks": checks,
    }


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# Credential Boundary Audit",
        "",
        "## Summary",
        "",
        f"- passed: {bool_mark(audit['passed'])}",
        f"- git repository: {bool_mark(audit['git']['is_repo'])}",
        "",
        "## Checks",
        "",
        "| check | passed | detail |",
        "|---|---:|---|",
    ]
    for name, result in audit["checks"].items():
        detail = json.dumps({key: value for key, value in result.items() if key != "passed"}, ensure_ascii=False, sort_keys=True)
        lines.append(f"| `{name}` | {bool_mark(result['passed'])} | `{detail}` |")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit local credential and secret-file boundaries.")
    parser.add_argument("--out-json", default="outputs/credential_boundary/latest.json")
    parser.add_argument("--out-md", default="outputs/credential_boundary/latest.md")
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
