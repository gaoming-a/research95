#!/usr/bin/env python3
"""Freeze the author-signed V2-P1 project test-scope amendment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "data/protocols/dsa_v2_p1_test_scope_amendment_proposal_v0_1.json"
DECLARATION = ROOT / "data/protocols/dsa_v2_p1_test_scope_amendment_author_declaration_v0_1.txt"
OUT = ROOT / "data/protocols/dsa_v2_p1_test_scope_amendment_v0_1.json"
EXPECTED_AMENDMENTS_SHA256 = "b5778a7c95042d5475d333842c5b8a486a2798a7586d74a20a84e30487ddef94"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def canonical_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")


def build() -> dict[str, Any]:
    proposal = read_json(PROPOSAL)
    declaration = canonical_text(DECLARATION)
    required = (
        "我，高明，签核 V2-P1 清单及其 SHA-256 所绑定的全部8项",
        "授权自动执行 V2-P1 至 V2-P2",
        "仅在 V2-P3 最终冻结处或硬停止条件下暂停",
    )
    if not all(item in declaration for item in required):
        raise ValueError("author declaration does not contain the signed authorization")
    if proposal.get("amendments_sha256") != EXPECTED_AMENDMENTS_SHA256:
        raise ValueError("test-scope amendment proposal hash drift")
    value = {
        "amendment_id": "dsa_v2_p1_test_scope_amendment_v0_1",
        "created_date": "2026-07-12",
        "status": "author_signed_immutable",
        "author": "高明",
        "author_declaration_path": DECLARATION.relative_to(ROOT).as_posix(),
        "author_declaration_sha256": hashlib.sha256(declaration.encode("utf-8")).hexdigest(),
        "proposal_path": PROPOSAL.relative_to(ROOT).as_posix(),
        "proposal_sha256": hashlib.sha256(canonical_text(PROPOSAL).encode("utf-8")).hexdigest(),
        "amendments_sha256": proposal["amendments_sha256"],
        "derivation_rule": proposal["derivation_rule"],
        "amendments": proposal["amendments"],
        "authorization": {
            "real_v2_p2_order_1": True,
            "real_v2_p2_all_orders": True,
            "pause_at_v2_p3_final_freeze": True,
            "pause_at_hard_stop": True,
            "v2_p3": False,
            "prompt": False,
            "model_api": False,
        },
        "original_v2_p1_manifest_aggregate_sha256": proposal["v2_p1_manifest_aggregate_sha256"],
        "original_v2_p1_source_order_sha256": proposal["source_order_sha256"],
        "boundary": "This additive author-signed amendment completes the missing project test scopes without changing any original V2-P1 file or authorizing V2-P3, prompt changes, credential access, or model API calls.",
    }
    value["amendment_record_sha256"] = hashlib.sha256(
        json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()
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
        raise SystemExit("stale or missing signed V2-P1 test-scope amendment")
    print(json.dumps({
        "status": value["status"],
        "author": value["author"],
        "amendments_sha256": value["amendments_sha256"],
        "real_v2_p2_all_orders": value["authorization"]["real_v2_p2_all_orders"],
        "model_api_calls": 0,
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
