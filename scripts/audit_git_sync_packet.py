from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from write_git_sync_packet import build_packet


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def build_audit(old_repo: str) -> dict[str, Any]:
    packet = build_packet(argparse.Namespace(old_repo=old_repo))
    commands = packet.get("safe_command_template_after_decision", [])
    staging_allowlist = packet.get("staging_allowlist", [])
    forbidden = packet.get("forbidden", [])

    try:
        check_ignore_index = commands.index(
            "git check-ignore -v .env configs/api_pilot.local.json configs/model_selection.local.json outputs artifacts data tmp"
        )
    except ValueError:
        check_ignore_index = -1
    try:
        status_branch_index = commands.index("git status --short --branch")
    except ValueError:
        status_branch_index = -1
    try:
        log_ahead_index = commands.index("git log --oneline --decorate origin/main..HEAD")
    except ValueError:
        log_ahead_index = -1

    checks = {
        "requires_human_decision_when_not_sync_ready": packet["requires_human_decision"] is (not packet["sync_ready"]),
        "decision_template_present": all(
            key in packet.get("decision_record_template", {})
            for key in ["push_current_branch", "defer_reason", "github_remote_url", "reason"]
        ),
        "ahead_behind_fields_present": all(
            key in packet
            for key in ["current_status_branch", "current_upstream", "current_ahead", "current_behind", "current_status_clean"]
        ),
        "ahead_requires_human_decision": not packet.get("current_ahead") or packet["requires_human_decision"],
        "sync_ready_requires_zero_ahead_behind": (not packet["sync_ready"])
        or (packet.get("current_ahead") == 0 and packet.get("current_behind") == 0),
        "staging_allowlist_present": all(
            item in staging_allowlist for item in [".gitignore", ".env.example", "README.md", "configs", "docs", "scripts", "src"]
        ),
        "no_dot_add_template": all(command.strip() != "git add ." for command in commands),
        "no_secret_paths_in_allowlist": ".env" not in staging_allowlist and "configs/*.local.json" not in staging_allowlist,
        "status_branch_before_push": status_branch_index >= 0 and status_branch_index < len(commands) - 1,
        "ignore_check_before_push": check_ignore_index >= 0 and check_ignore_index < len(commands) - 1,
        "ahead_log_before_push": log_ahead_index >= 0 and log_ahead_index < len(commands) - 1,
        "push_is_last": bool(commands) and commands[-1] == "git push origin main",
        "post_sync_acceptance_present": len(packet.get("post_sync_acceptance", [])) >= 4,
        "forbidden_mentions_remote_change": any("remote" in item and "confirms" in item for item in forbidden),
        "forbidden_mentions_dot_add": any("git add ." in item for item in forbidden),
        "forbidden_mentions_ahead_state": any("ahead or behind" in item for item in forbidden),
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "packet_summary": {
            "current_is_git_repo": packet["current_is_git_repo"],
            "current_has_remote": packet["current_has_remote"],
            "current_upstream": packet.get("current_upstream"),
            "current_ahead": packet.get("current_ahead"),
            "current_behind": packet.get("current_behind"),
            "sync_ready": packet["sync_ready"],
            "requires_human_decision": packet["requires_human_decision"],
            "old_repo_is_git_repo": packet["old_repo_is_git_repo"],
        },
    }


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# Git Sync Packet Audit",
        "",
        "## Summary",
        "",
        f"- passed: {bool_mark(audit['passed'])}",
        f"- current is git repo: {bool_mark(audit['packet_summary']['current_is_git_repo'])}",
        f"- current has remote: {bool_mark(audit['packet_summary']['current_has_remote'])}",
        f"- current upstream: `{audit['packet_summary']['current_upstream']}`",
        f"- current ahead: `{audit['packet_summary']['current_ahead']}`",
        f"- current behind: `{audit['packet_summary']['current_behind']}`",
        f"- sync ready: {bool_mark(audit['packet_summary']['sync_ready'])}",
        f"- requires human decision: {bool_mark(audit['packet_summary']['requires_human_decision'])}",
        f"- old repo is git repo: {bool_mark(audit['packet_summary']['old_repo_is_git_repo'])}",
        "",
        "## Checks",
        "",
        "| check | passed |",
        "|---|---:|",
    ]
    for name, passed in audit["checks"].items():
        lines.append(f"| `{name}` | {bool_mark(passed)} |")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit the Git sync decision packet safety rules.")
    parser.add_argument("--old-repo", default="../research")
    parser.add_argument("--out-json", default="outputs/git_sync_packet_audit/latest.json")
    parser.add_argument("--out-md", default="outputs/git_sync_packet_audit/latest.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = build_audit(args.old_repo)
    write_json(Path(args.out_json), audit)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(audit), encoding="utf-8")
    print(json.dumps({"out_json": args.out_json, "out_md": args.out_md, "passed": audit["passed"]}, ensure_ascii=False, indent=2))
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
