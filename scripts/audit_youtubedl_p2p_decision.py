from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from static_unittest_p2p_preflight import build_summary


DEFAULT_PROBE_RESULTS = Path("data") / "tasks" / "evp7_controlled_probe_results.json"
DEFAULT_DECISION_PACKET = Path("docs") / "experiments" / "evp7_youtubedl_p2p_decision_packet_20260613.md"
DEFAULT_STATIC_EXCLUDE_TOKENS = ["YoutubeDL(", "download(", "urlopen", "http://", "https://"]


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def youtube_dl_candidates(probe_results: Path) -> list[dict[str, Any]]:
    payload = read_json(probe_results)
    results = payload.get("results", [])
    if not isinstance(results, list):
        raise ValueError(f"{probe_results} must contain a list at results")
    candidates = [
        item
        for item in results
        if isinstance(item, dict)
        and item.get("project") == "youtube-dl"
        and item.get("probe_status") == "f2p_established_p2p_not_attempted"
    ]
    return sorted(candidates, key=lambda item: str(item["task_id"]))


def static_summary(task_id: str, source_workspace_root: str, tokens: list[str]) -> dict[str, Any]:
    args = SimpleNamespace(
        task_id=task_id,
        project="youtube-dl",
        source_workspace_root=source_workspace_root,
        unittest_start_dir="test",
        unittest_pattern="test*.py",
        static_exclude_token=tokens,
    )
    return build_summary(args)


def checkout_root(source_workspace_root: str, task_id: str, version: str) -> Path:
    bug_dir = task_id.replace("bugsinpy_", "")
    return Path(source_workspace_root) / bug_dir / version / "youtube-dl"


def parse_decision_packet(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    recommended_match = re.search(r"Recommended first representative:\s*`([^`]+)`", text)
    command_match = re.search(r"```powershell\s*(.*?)```", text, flags=re.DOTALL)
    command = command_match.group(1).strip() if command_match else ""
    command_flags = parse_powershell_command_flags(command)
    return {
        "path": path.as_posix(),
        "recommended_task_id": recommended_match.group(1) if recommended_match else None,
        "command": command,
        "command_flags": command_flags,
        "command_task_id": single_flag_value(command_flags, "task-id"),
        "command_fail_to_pass_nodeid": single_flag_value(command_flags, "fail-to-pass-nodeid"),
        "manifest_out": single_flag_value(command_flags, "manifest-out"),
    }


def parse_powershell_command_flags(command: str) -> dict[str, Any]:
    normalized = command.replace("`", " ")
    tokens = shlex.split(normalized, posix=False)
    flags: dict[str, Any] = {}
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if not token.startswith("--"):
            index += 1
            continue
        name = token[2:]
        if index + 1 >= len(tokens) or tokens[index + 1].startswith("--"):
            value: Any = True
            index += 1
        else:
            value = tokens[index + 1].strip("\"'")
            index += 2
        if name in flags:
            if not isinstance(flags[name], list):
                flags[name] = [flags[name]]
            flags[name].append(value)
        else:
            flags[name] = value
    return flags


def single_flag_value(flags: dict[str, Any], name: str) -> str | None:
    value = flags.get(name)
    if isinstance(value, list):
        return str(value[-1]) if value else None
    if value is True or value is None:
        return None
    return str(value)


def expected_fail_to_pass_nodeid(candidate: dict[str, Any] | None) -> str | None:
    if not candidate:
        return None
    run_command = str(candidate.get("run_command") or "").strip()
    if not run_command:
        return None
    return run_command.split()[-1]


def p2p_command_packet(
    task_id: str | None,
    fail_to_pass_nodeid: str | None,
    static_exclude_tokens: list[str],
    manifest_out: str | None,
) -> dict[str, Any]:
    if not task_id or not fail_to_pass_nodeid:
        return {"approval_required": True, "command": None, "argv": []}
    out_dir = f"outputs\\p2p_scope_builds\\{task_id}"
    manifest = manifest_out or f"data\\p2p_scopes\\{task_id}_p2p_broad.json"
    argv = [
        "python",
        "scripts\\build_pass_to_pass_scope.py",
        "--task-id",
        task_id,
        "--project",
        "youtube-dl",
        "--test-framework",
        "unittest",
        "--unittest-start-dir",
        "test",
        "--unittest-pattern",
        "test_*.py",
        "--fail-to-pass-nodeid",
        fail_to_pass_nodeid,
        "--scope-type",
        "project_level_p2p_broad",
        "--runs",
        "3",
        "--timeout-seconds",
        "30",
        "--batch-timeout-seconds",
        "1800",
        "--batch-size",
        "50",
        "--batch-first",
    ]
    for token in static_exclude_tokens:
        argv.extend(["--static-exclude-token", token])
    argv.extend(["--out-dir", out_dir, "--manifest-out", manifest])
    command_lines = [
        "python scripts\\build_pass_to_pass_scope.py `",
        f"  --task-id {task_id} `",
        "  --project youtube-dl `",
        "  --test-framework unittest `",
        "  --unittest-start-dir test `",
        '  --unittest-pattern "test_*.py" `',
        f'  --fail-to-pass-nodeid "{fail_to_pass_nodeid}" `',
        "  --scope-type project_level_p2p_broad `",
        "  --runs 3 `",
        "  --timeout-seconds 30 `",
        "  --batch-timeout-seconds 1800 `",
        "  --batch-size 50 `",
        "  --batch-first `",
    ]
    for index, token in enumerate(static_exclude_tokens):
        suffix = " `" if index < len(static_exclude_tokens) - 1 else " `"
        command_lines.append(f'  --static-exclude-token "{token}"{suffix}')
    command_lines.extend([f"  --out-dir {out_dir} `", f"  --manifest-out {manifest}"])
    return {
        "approval_required": True,
        "command": "\n".join(command_lines),
        "argv": argv,
        "expected_flags": {
            "task-id": task_id,
            "project": "youtube-dl",
            "test-framework": "unittest",
            "unittest-start-dir": "test",
            "unittest-pattern": "test_*.py",
            "fail-to-pass-nodeid": fail_to_pass_nodeid,
            "scope-type": "project_level_p2p_broad",
            "runs": "3",
            "timeout-seconds": "30",
            "batch-timeout-seconds": "1800",
            "batch-size": "50",
            "batch-first": True,
            "static-exclude-token": static_exclude_tokens,
            "out-dir": out_dir,
            "manifest-out": manifest,
        },
        "out_dir": out_dir,
        "manifest_out": manifest,
    }


def flags_match_expected(actual: dict[str, Any], expected: dict[str, Any]) -> bool:
    for name, expected_value in expected.items():
        actual_value = actual.get(name)
        if isinstance(expected_value, list):
            if actual_value != expected_value:
                return False
        elif actual_value != expected_value:
            return False
    return True


def run_builder_dry_run(command_packet: dict[str, Any]) -> dict[str, Any]:
    argv = command_packet.get("argv") or []
    if not argv:
        return {"returncode": None, "parsed": None, "error": "missing command argv"}
    command = [sys.executable, *argv[1:], "--dry-run"]
    completed = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
    )
    parsed = None
    parse_error = None
    if completed.stdout.strip():
        try:
            parsed = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            parse_error = str(exc)
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "parsed": parsed,
        "parse_error": parse_error,
    }


def build_audit(args: argparse.Namespace) -> dict[str, Any]:
    candidates = youtube_dl_candidates(Path(args.probe_results))
    static_rows = []
    for candidate in candidates:
        summary = static_summary(str(candidate["task_id"]), args.source_workspace_root, args.static_exclude_token)
        comparison = summary["remaining_set_comparison"]
        row = {
            "task_id": candidate["task_id"],
            "run_command": candidate.get("run_command"),
            "buggy_methods": summary["buggy"]["total_test_methods_static"],
            "fixed_methods": summary["fixed"]["total_test_methods_static"],
            "buggy_remaining": summary["buggy"]["remaining_after_static_exclusions"],
            "fixed_remaining": summary["fixed"]["remaining_after_static_exclusions"],
            "common_remaining": comparison["common_count"],
            "buggy_only": comparison["buggy_only_count"],
            "fixed_only": comparison["fixed_only_count"],
        }
        static_rows.append(row)

    lowest = min(static_rows, key=lambda row: (row["common_remaining"], row["task_id"])) if static_rows else None
    packet = parse_decision_packet(Path(args.decision_packet))
    recommended = packet["recommended_task_id"]
    command_task = packet["command_task_id"]
    manifest_out = packet["manifest_out"]
    manifest_exists = Path(manifest_out).exists() if manifest_out else False
    recommended_candidate = next((candidate for candidate in candidates if candidate.get("task_id") == recommended), None)
    expected_f2p_nodeid = expected_fail_to_pass_nodeid(recommended_candidate)
    command_packet = p2p_command_packet(recommended, expected_f2p_nodeid, args.static_exclude_token, manifest_out)
    builder_dry_run = run_builder_dry_run(command_packet)
    builder_dry_run_parsed = builder_dry_run.get("parsed") or {}
    buggy_checkout = checkout_root(args.source_workspace_root, recommended, "buggy") if recommended else None
    fixed_checkout = checkout_root(args.source_workspace_root, recommended, "fixed") if recommended else None

    checks = {
        "has_candidates": bool(static_rows),
        "recommended_matches_lowest_static_cost": bool(lowest and recommended == lowest["task_id"]),
        "command_task_matches_recommended": bool(recommended and command_task == recommended),
        "command_fail_to_pass_matches_probe": bool(expected_f2p_nodeid and packet["command_fail_to_pass_nodeid"] == expected_f2p_nodeid),
        "decision_packet_command_flags_match_expected": flags_match_expected(
            packet["command_flags"],
            command_packet["expected_flags"],
        ),
        "recommended_buggy_checkout_exists": bool(buggy_checkout and buggy_checkout.exists()),
        "recommended_fixed_checkout_exists": bool(fixed_checkout and fixed_checkout.exists()),
        "recommended_manifest_not_already_tracked": not manifest_exists,
        "command_packet_requires_approval": bool(command_packet["approval_required"]),
        "builder_dry_run_completed": builder_dry_run["returncode"] == 0 and isinstance(builder_dry_run.get("parsed"), dict),
        "builder_dry_run_no_test_execution": builder_dry_run_parsed.get("will_execute_tests") is False,
        "builder_dry_run_no_manifest_write": builder_dry_run_parsed.get("will_write_manifest") is False,
        "builder_dry_run_no_output_dir_creation": builder_dry_run_parsed.get("will_create_output_dir") is False,
        "builder_dry_run_manifest_absent": builder_dry_run_parsed.get("manifest_out_exists") is False
        and not Path(str(command_packet.get("manifest_out"))).exists(),
        "builder_dry_run_scope_matches_expected": builder_dry_run_parsed.get("test_paths") == ["test"]
        and builder_dry_run_parsed.get("fail_to_pass_nodeids") == [expected_f2p_nodeid],
        "all_buggy_fixed_remaining_sets_match": all(row["buggy_only"] == 0 and row["fixed_only"] == 0 for row in static_rows),
    }
    return {
        "mode": "static_no_run_decision_audit",
        "executed_tests": False,
        "created_p2p_manifest": False,
        "probe_results": Path(args.probe_results).as_posix(),
        "decision_packet": packet,
        "static_exclude_tokens": args.static_exclude_token,
        "candidate_count": len(static_rows),
        "static_rows": static_rows,
        "lowest_static_cost_candidate": lowest,
        "recommended_probe": recommended_candidate,
        "expected_fail_to_pass_nodeid": expected_f2p_nodeid,
        "recommended_checkouts": {
            "buggy": str(buggy_checkout) if buggy_checkout else None,
            "fixed": str(fixed_checkout) if fixed_checkout else None,
        },
        "command_packet": command_packet,
        "builder_dry_run": builder_dry_run,
        "checks": checks,
        "passed": all(checks.values()),
    }


def markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# youtube-dl P2P Decision Audit",
        "",
        f"- mode: `{audit['mode']}`",
        f"- executed tests: `{audit['executed_tests']}`",
        f"- created P2P manifest: `{audit['created_p2p_manifest']}`",
        f"- passed: `{audit['passed']}`",
        f"- recommended task: `{audit['decision_packet']['recommended_task_id']}`",
        f"- command task: `{audit['decision_packet']['command_task_id']}`",
        f"- command fail-to-pass nodeid: `{audit['decision_packet']['command_fail_to_pass_nodeid']}`",
        f"- expected fail-to-pass nodeid: `{audit['expected_fail_to_pass_nodeid']}`",
        f"- lowest static-cost task: `{(audit['lowest_static_cost_candidate'] or {}).get('task_id')}`",
        f"- approval required before execution: `{audit['command_packet']['approval_required']}`",
        f"- builder dry-run returncode: `{audit['builder_dry_run']['returncode']}`",
        "",
        "## Checks",
        "",
    ]
    for key, value in audit["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Command Packet", "", "```powershell", audit["command_packet"]["command"] or "", "```"])
    lines.extend(["", "## Static Rows", "", "| Task | Methods | Remaining | Diff |", "| --- | ---: | ---: | ---: |"])
    for row in audit["static_rows"]:
        diff = row["buggy_only"] + row["fixed_only"]
        lines.append(f"| `{row['task_id']}` | {row['buggy_methods']} | {row['common_remaining']} | {diff} |")
    lines.append("")
    return "\n".join(lines)


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit the youtube-dl P2P representative decision without running P2P.")
    parser.add_argument("--probe-results", default=str(DEFAULT_PROBE_RESULTS))
    parser.add_argument("--decision-packet", default=str(DEFAULT_DECISION_PACKET))
    parser.add_argument("--source-workspace-root", default=str(Path("..") / "research" / "data" / "real_bugs" / "bugsinpy_workspace"))
    parser.add_argument("--static-exclude-token", action="append", default=DEFAULT_STATIC_EXCLUDE_TOKENS)
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = build_audit(args)
    write_json(Path(args.out_json), audit)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(markdown(audit), encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True))
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
