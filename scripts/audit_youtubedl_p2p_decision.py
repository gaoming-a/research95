from __future__ import annotations

import argparse
import json
import re
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


def parse_decision_packet(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    recommended_match = re.search(r"Recommended first representative:\s*`([^`]+)`", text)
    command_task_match = re.search(r"--task-id\s+([^\s`]+)", text)
    manifest_match = re.search(r"--manifest-out\s+([^\s`]+)", text)
    return {
        "path": path.as_posix(),
        "recommended_task_id": recommended_match.group(1) if recommended_match else None,
        "command_task_id": command_task_match.group(1) if command_task_match else None,
        "manifest_out": manifest_match.group(1) if manifest_match else None,
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

    checks = {
        "has_candidates": bool(static_rows),
        "recommended_matches_lowest_static_cost": bool(lowest and recommended == lowest["task_id"]),
        "command_task_matches_recommended": bool(recommended and command_task == recommended),
        "recommended_manifest_not_already_tracked": not manifest_exists,
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
        f"- lowest static-cost task: `{(audit['lowest_static_cost_candidate'] or {}).get('task_id')}`",
        "",
        "## Checks",
        "",
    ]
    for key, value in audit["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
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
