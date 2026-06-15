from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


def run_git(args: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        "cwd": "<repo_root>" if cwd == Path.cwd() else cwd.as_posix(),
        "args": args,
        "exit_code": completed.returncode,
        "passed": completed.returncode == 0,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def parse_remote_stdout(stdout: str) -> list[dict[str, str]]:
    remotes: list[dict[str, str]] = []
    for line in stdout.splitlines():
        parts = line.split()
        if len(parts) >= 3:
            remotes.append({"name": parts[0], "url": parts[1], "kind": parts[2].strip("()")})
    return remotes


def parse_status_branch(stdout: str) -> dict[str, Any]:
    lines = stdout.splitlines()
    branch_header = lines[0] if lines and lines[0].startswith("## ") else ""
    dirty_lines = [line for line in lines if not line.startswith("## ")]
    upstream = None
    ahead = 0
    behind = 0
    if "..." in branch_header:
        upstream_part = branch_header.split("...", 1)[1]
        upstream = upstream_part.split(" ", 1)[0].strip()
    ahead_match = re.search(r"ahead (\d+)", branch_header)
    behind_match = re.search(r"behind (\d+)", branch_header)
    if ahead_match:
        ahead = int(ahead_match.group(1))
    if behind_match:
        behind = int(behind_match.group(1))
    return {
        "branch_header": branch_header,
        "upstream": upstream,
        "ahead": ahead,
        "behind": behind,
        "dirty_lines": dirty_lines,
        "clean": not dirty_lines,
    }


def build_packet(args: argparse.Namespace) -> dict[str, Any]:
    current_root = Path.cwd()
    old_root = Path(args.old_repo).resolve()
    current_git = run_git(["status", "--short", "--branch"], current_root)
    current_status = parse_status_branch(current_git["stdout"]) if current_git["passed"] else {}
    current_remote = run_git(["remote", "-v"], current_root)
    current_remotes = parse_remote_stdout(current_remote.get("stdout", "")) if current_remote["passed"] else []
    current_has_remote = bool(current_remotes)
    old_git_exists = old_root.exists() and (old_root / ".git").exists()
    old_status = run_git(["status", "--short"], old_root) if old_git_exists else {}
    old_remote = run_git(["remote", "-v"], old_root) if old_git_exists else {}
    old_remotes = parse_remote_stdout(old_remote.get("stdout", "")) if old_remote else []
    sync_ready = bool(
        current_git["passed"]
        and current_has_remote
        and current_status.get("clean")
        and current_status.get("upstream")
        and current_status.get("ahead") == 0
        and current_status.get("behind") == 0
    )
    requires_human_decision = not sync_ready

    return {
        "current_workspace": "<repo_root>",
        "current_is_git_repo": current_git["passed"],
        "current_has_remote": current_has_remote,
        "current_status_short": current_git["stdout"].splitlines() if current_git["passed"] and current_git["stdout"] else [],
        "current_status_branch": current_status.get("branch_header"),
        "current_status_clean": bool(current_status.get("clean")),
        "current_upstream": current_status.get("upstream"),
        "current_ahead": current_status.get("ahead", 0),
        "current_behind": current_status.get("behind", 0),
        "current_dirty_lines": current_status.get("dirty_lines", []),
        "current_git_error": current_git["stderr"] if not current_git["passed"] else None,
        "current_remote_available": current_remote["passed"],
        "current_remotes": current_remotes,
        "old_repo_checked": "<old_repo>",
        "old_repo_exists": old_root.exists(),
        "old_repo_is_git_repo": old_git_exists,
        "old_repo_status_clean": old_status.get("passed") is True and not old_status.get("stdout"),
        "old_repo_remotes": old_remotes,
        "requires_human_decision": requires_human_decision,
        "sync_ready": sync_ready,
        "required_decision": (
            "Confirm whether to push the local commits to the configured research95 "
            "remote now, or intentionally defer GitHub sync and keep the local "
            "ahead state visible in handoff."
        ),
        "decision_record_template": {
            "push_current_branch": "<yes/no>",
            "defer_reason": "<one sentence if no>",
            "github_remote_url": "<configured-github-repo-url>",
            "reason": "<one sentence>",
        },
        "staging_allowlist": [
            ".gitignore",
            ".env.example",
            "README.md",
            "pyproject.toml",
            "configs",
            "docs",
            "examples",
            "scripts",
            "src",
        ],
        "safe_command_template_after_decision": [
            "git status --short --branch",
            "git remote -v",
            "git check-ignore -v .env configs/api_pilot.local.json configs/model_selection.local.json outputs artifacts data tmp",
            "git status --short --ignored",
            "git diff --cached --check",
            "git log --oneline --decorate origin/main..HEAD",
            "git push origin main",
        ],
        "post_sync_acceptance": [
            "git status --short reports no unexpected tracked local files.",
            "git remote -v shows the user-confirmed remote.",
            "git ls-files does not include .env, configs/*.local.json, outputs/, data/, tmp/, artifacts/, or benchmark checkouts.",
            "git status --short --branch reports no local ahead or behind state.",
            "The pushed branch is visible on GitHub before claiming sync complete.",
        ],
        "forbidden": [
            "Do not commit .env, configs/*.local.json, outputs/, data/, tmp/, artifacts/, or benchmark checkouts.",
            "Do not change the configured research95 remote unless the user explicitly confirms it.",
            "Do not run git add . for this workspace.",
            "Do not claim GitHub sync until git status --short --branch shows no ahead or behind state after push.",
        ],
    }


def build_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Git Sync Packet",
        "",
        "## Status",
        "",
        f"- current workspace: `{packet['current_workspace']}`",
        f"- current is git repo: {bool_mark(packet['current_is_git_repo'])}",
        f"- current remote available: {bool_mark(packet['current_remote_available'])}",
        f"- current has remote: {bool_mark(packet['current_has_remote'])}",
        f"- current status: `{packet['current_status_branch']}`",
        f"- current status clean: {bool_mark(packet['current_status_clean'])}",
        f"- current upstream: `{packet['current_upstream']}`",
        f"- current ahead: `{packet['current_ahead']}`",
        f"- current behind: `{packet['current_behind']}`",
        f"- sync ready: {bool_mark(packet['sync_ready'])}",
        f"- old repo checked: `{packet['old_repo_checked']}`",
        f"- old repo is git repo: {bool_mark(packet['old_repo_is_git_repo'])}",
        f"- old repo status clean: {bool_mark(packet['old_repo_status_clean'])}",
        f"- requires human decision: {bool_mark(packet['requires_human_decision'])}",
        "",
        "## Required Decision",
        "",
        packet["required_decision"],
        "",
        "## Old Repo Remotes",
        "",
    ]
    if packet["old_repo_remotes"]:
        for remote in packet["old_repo_remotes"]:
            lines.append(f"- `{remote['name']}` `{remote['kind']}`: `{remote['url']}`")
    else:
        lines.append("- None found.")
    lines.extend(["", "## Current Remotes", ""])
    if packet["current_remotes"]:
        for remote in packet["current_remotes"]:
            lines.append(f"- `{remote['name']}` `{remote['kind']}`: `{remote['url']}`")
    else:
        lines.append("- None found.")
    lines.extend(["", "## Decision Record Template", ""])
    for key, value in packet["decision_record_template"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Staging Allowlist", ""])
    for item in packet["staging_allowlist"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Command Template After Decision", ""])
    for command in packet["safe_command_template_after_decision"]:
        lines.extend(["```powershell", command, "```", ""])
    lines.extend(["## Post-Sync Acceptance", ""])
    for item in packet["post_sync_acceptance"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.extend(["## Forbidden", ""])
    for item in packet["forbidden"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write a Git sync decision packet for the clean workspace.")
    parser.add_argument("--old-repo", default="../research")
    parser.add_argument("--out-json", default="outputs/handoff/git_sync_packet.json")
    parser.add_argument("--out-md", default="outputs/handoff/git_sync_packet.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    packet = build_packet(args)
    write_json(Path(args.out_json), packet)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(packet), encoding="utf-8")
    print(
        json.dumps(
            {
                "out_json": args.out_json,
                "out_md": args.out_md,
                "current_is_git_repo": packet["current_is_git_repo"],
                "requires_human_decision": packet["requires_human_decision"],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
