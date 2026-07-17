# ruff: noqa: E402
#!/usr/bin/env python3
"""Freeze the author-signed general V2-P2 dangling-docs symlink rule."""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/dsa2026_freeze_v2_p2_dangling_docs_symlink_amendment.py")

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "data/protocols/dsa_v2_p2_dangling_docs_symlink_amendment_proposal_v0_1.json"
DECLARATION = ROOT / "data/protocols/dsa_v2_p2_dangling_docs_symlink_amendment_author_declaration_v0_1.txt"
OUT = ROOT / "data/protocols/dsa_v2_p2_dangling_docs_symlink_amendment_v0_1.json"
EXPECTED_MANIFEST_SHA256 = "6d07262076da1d29f9fdc4edb7e837ca35d38094f8ab1a90082a2a2be2674847"


def canonical_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")


def canonical_json_sha(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def build() -> dict[str, Any]:
    proposal = read_json(PROPOSAL)
    declaration = canonical_text(DECLARATION)
    required = (
        "高明",
        EXPECTED_MANIFEST_SHA256,
        "完全一致的13个 dangling documentation",
        "全部零交集",
        "仅从 Windows",
        "任何其他 dangling link",
        "后续全部 V2-P2 orders 的通用 source-materialization rule",
        "独立 hash manifest",
        "任一 predicate 不通过即 hard stop",
        "不授权进入 V2-P3",
        "不授权读取 API key 或调用模型 API",
    )
    if not all(item in declaration for item in required):
        raise ValueError("author declaration does not contain the complete signed rule and boundaries")
    if proposal.get("dangling_manifest_sha256") != EXPECTED_MANIFEST_SHA256:
        raise ValueError("dangling-docs manifest hash drift")
    checks = proposal.get("checks", {})
    required_checks = (
        "all_dangling_are_symbolic_docs_paths",
        "both_official_archives_inspected",
        "cursor_is_unstarted_order3_black4",
        "dangling_identity_equal_across_commits",
        "no_changed_source_intersection",
        "no_declared_test_intersection",
        "no_package_build_metadata_intersection",
        "no_real_activity_or_outcome_used",
    )
    if not all(checks.get(name) is True for name in required_checks):
        raise ValueError("proposal mechanical predicates do not all pass")
    value: dict[str, Any] = {
        "amendment_id": "dsa_v2_p2_dangling_docs_symlink_amendment_v0_1",
        "created_date": "2026-07-12",
        "status": "author_signed_immutable",
        "author": "高明",
        "author_declaration_path": DECLARATION.relative_to(ROOT).as_posix(),
        "author_declaration_sha256": hashlib.sha256(declaration.encode("utf-8")).hexdigest(),
        "proposal_path": PROPOSAL.relative_to(ROOT).as_posix(),
        "proposal_sha256": hashlib.sha256(canonical_text(PROPOSAL).encode("utf-8")).hexdigest(),
        "black_4_manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "black_4_archive_sha256s": [archive["archive_sha256"] for archive in proposal["archives"]],
        "black_4_dangling_manifest": proposal["dangling_manifest"],
        "rule": proposal["rule"],
        "mechanical_predicates": {
            "normalized_path_strictly_under_docs": True,
            "symbolic_link": True,
            "no_changed_source_intersection": True,
            "no_declared_test_intersection": True,
            "no_project_test_root_intersection": True,
            "no_package_build_metadata_intersection": True,
            "independent_hash_manifest_required_per_future_task": True,
        },
        "authorization": {
            "black_4_source_extraction": True,
            "general_v2_p2_source_materialization_rule": True,
            "automatic_application_only_when_all_predicates_pass": True,
            "hard_stop_when_any_predicate_fails": True,
            "environment_policy_change": False,
            "candidate_qualification_change": False,
            "hidden_oracle_change": False,
            "prompt_or_schema_or_statistics_change": False,
            "v2_p3": False,
            "api_key_access": False,
            "model_api": False,
        },
        "boundary": "Only unmaterializable dangling documentation symlinks satisfying every frozen mechanical predicate may be omitted from a Windows build/test tree; all other cases hard-stop.",
    }
    value["amendment_record_sha256"] = canonical_json_sha(value)
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
        raise SystemExit("stale or missing signed V2-P2 dangling-docs amendment")
    print(json.dumps({
        "status": value["status"],
        "manifest_sha256": value["black_4_manifest_sha256"],
        "general_v2_p2_rule": value["authorization"]["general_v2_p2_source_materialization_rule"],
        "black_4_source_extraction": value["authorization"]["black_4_source_extraction"],
        "model_api_calls": 0,
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
