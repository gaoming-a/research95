# ruff: noqa: E402
#!/usr/bin/env python3
"""Freeze the author's continuous V2-P2 execution authorization."""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/dsa2026_freeze_v2_p2_continuous_authorization.py")

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECLARATION = ROOT / "data/protocols/dsa_v2_p2_continuous_authorization_v0_1.txt"
LEDGER = ROOT / "data/protocols/dsa_v2_p2_terminal_ledger_v0_2.json"
OUT = ROOT / "data/protocols/dsa_v2_p2_continuous_authorization_v0_1.json"


def canonical_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")


def canonical_json_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")).hexdigest()


def build() -> dict[str, object]:
    declaration = canonical_text(DECLARATION)
    required = (
        "连续自动执行全部 V2-P2 orders",
        "普通 task failure 自动记录并继续",
        "达到30个 qualified pairs",
        "V2-P3 最终冻结包",
        "hash-bound 作者签核后",
        "V2-P5 模型",
        "预注册 hard stop",
        "公开发布或",
        "投稿前暂停",
    )
    if not all(value in declaration for value in required):
        raise ValueError("continuous authorization declaration is incomplete")
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    if ledger["next_order"] != 3 or ledger["next_task_id"] != "bugsinpy_black_4" or ledger["next_task_started"]:
        raise ValueError("continuous authorization cursor anchor drift")
    return {
        "authorization_id": "dsa_v2_p2_continuous_authorization_v0_1",
        "created_date": "2026-07-12",
        "status": "author_signed_active",
        "author": "高明",
        "declaration_path": DECLARATION.relative_to(ROOT).as_posix(),
        "declaration_sha256": hashlib.sha256(declaration.encode("utf-8")).hexdigest(),
        "cursor_ledger_path": LEDGER.relative_to(ROOT).as_posix(),
        "cursor_ledger_sha256": canonical_json_sha(ledger),
        "start_order": 3,
        "start_task_id": "bugsinpy_black_4",
        "authorization": {
            "continuous_v2_p2": True,
            "ordinary_task_failure_continue": True,
            "local_checkpoint_commits": True,
            "generate_v2_p3_at_30_pairs": True,
            "pause_for_v2_p3_author_hash_signoff": True,
            "v2_p4_to_v2_p6_after_v2_p3_signoff": True,
            "model_api_before_v2_p3_signoff": False,
            "public_release_without_confirmation": False,
            "submission_without_confirmation": False,
        },
        "hard_stops": ["source-exhaustion-before-30-pairs", "frozen-content-drift", "other-preregistered-hard-stop"],
        "boundary": "This record authorizes local V2-P2 continuation only until the V2-P3 author-signoff gate; it does not itself authorize a model API call.",
    }


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
        raise SystemExit("stale continuous authorization record")
    print(json.dumps({"status": value["status"], "start_order": 3, "model_api_authorized_now": False}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
