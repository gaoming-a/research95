#!/usr/bin/env python3
"""Resolve the unique next V2-P2 task from immutable ledger/source inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ORDER = ROOT / "data/protocols/dsa_v2_p1_source_order_v0_1.json"
PROTOCOL = ROOT / "data/protocols/dsa_v2_p1_construction_protocol_v0_1.json"
SOURCE_FRAME = ROOT / "data/protocols/dsa_p2_source_frame_v0_1.json"
AUTHORIZATION = ROOT / "data/protocols/dsa_v2_p2_continuous_authorization_v0_1.json"
OUT = ROOT / "data/protocols/dsa_v2_p2_cursor_task_config_v0_1.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")).hexdigest()


def latest_ledger() -> tuple[Path, dict[str, Any]]:
    paths = []
    for path in (ROOT / "data/protocols").glob("dsa_v2_p2_terminal_ledger_v0_*.json"):
        match = re.fullmatch(r"dsa_v2_p2_terminal_ledger_v0_(\d+)\.json", path.name)
        if match:
            paths.append((int(match.group(1)), path))
    if not paths:
        raise FileNotFoundError("no V2-P2 terminal ledger")
    _, path = max(paths)
    return path, read_json(path)


def build() -> dict[str, Any]:
    ledger_path, ledger = latest_ledger()
    source = read_json(SOURCE_ORDER)
    protocol = read_json(PROTOCOL)
    frame = read_json(SOURCE_FRAME)
    auth = read_json(AUTHORIZATION)
    order = ledger["next_order"]
    if ledger["next_task_started"] or order != len(ledger["records"]) + 1:
        raise ValueError("ledger is not a unique unstarted contiguous cursor")
    record = source["records"][order - 1]
    if record["order"] != order or record["task_id"] != ledger["next_task_id"]:
        raise ValueError("ledger/source-order cursor drift")
    frame_record = next(item for item in frame["records"] if item["task_id"] == record["task_id"])
    locks = protocol["project_environment_recipe_policy"]["candidate_independent_base"]["python_explicit_locks"]
    lock = next(item for item in locks if item["python_version"] == record["python_version"])
    scope_auth = read_json(ROOT / "data/protocols/dsa_v2_p1_test_scope_amendment_v0_1.json")
    scope = next(item for item in scope_auth["amendments"] if item["project"] == record["project"])
    if auth["status"] != "author_signed_active" or not auth["authorization"]["continuous_v2_p2"]:
        raise PermissionError("continuous authorization is not active")
    value = {
        "config_id": "dsa_v2_p2_cursor_task_config_v0_1",
        "created_date": "2026-07-12",
        "status": "unique_next_task_resolved",
        "ledger_path": ledger_path.relative_to(ROOT).as_posix(),
        "ledger_sha256": canonical_sha(ledger),
        "attempted_tasks": ledger["attempted_tasks"],
        "qualified_pairs": ledger["qualified_pairs"],
        "task": record,
        "repository": frame_record["project_repository"],
        "python_lock": lock,
        "project_test_scope": scope,
        "runtime_namespace": f"order_{order:03d}_{record['task_id']}",
        "next_task_started": False,
        "model_api_calls": 0,
    }
    value["config_sha256"] = canonical_sha(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    content = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUT.write_text(content, encoding="utf-8", newline="\n")
    elif not OUT.is_file() or OUT.read_text(encoding="utf-8") != content:
        raise SystemExit("stale cursor task config")
    print(json.dumps({"status": value["status"], "order": value["task"]["order"], "task_id": value["task"]["task_id"], "qualified_pairs": value["qualified_pairs"], "model_api_calls": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
