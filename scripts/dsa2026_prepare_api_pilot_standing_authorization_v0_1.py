#!/usr/bin/env python3
"""Audit and activate the one-signature DSA development-pilot authority.

Proposal modes never read API credentials or contact a model. Activation requires
the author's exact hash-bound declaration file and only materializes local JSON
authorization records; it also does not read credentials or call a model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "data/protocols/dsa_v2_api_pilot_standing_execution_protocol_v0_1.json"
AUDIT = ROOT / "data/protocols/dsa_v2_api_pilot_standing_execution_audit_v0_1.json"
SIGNOFF = ROOT / "docs/experiments/dsa_v2_api_pilot_standing_authorization_signoff_v0_1.md"
DECLARATION = ROOT / "data/protocols/dsa_v2_api_pilot_standing_authorization_declaration_v0_1.txt"
ACTIVE = ROOT / "data/protocols/dsa_v2_api_pilot_standing_authorization_v0_1.json"
V03_AUTH = ROOT / "data/protocols/dsa_v2_api_pilot_execution_authorization_v0_3.json"
V03_CONFIG = ROOT / "configs/dsa_v2_api_pilot_v0_3.example.json"
V03_HASHES = ROOT / "data/protocols/dsa_v2_api_pilot_hash_manifest_v0_3.json"
V03_MANIFEST = ROOT / "data/protocols/dsa_v2_api_pilot_run_manifest_v0_3.json"
V03_OUTPUT = ROOT / "outputs/dsa_v2_api_pilot_v0_3"
V02_TERMINAL = ROOT / "data/protocols/dsa_v2_api_pilot_v0_2_terminal_audit.json"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def normalized_schedule(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    fields = ("request_order", "packet_id", "packet_sha256", "route_order", "repeat_index", "canary")
    return [{field: row[field] for field in fields} for row in manifest["requests"]]


def build_audit() -> dict[str, Any]:
    protocol = read_json(PROTOCOL)
    baseline = protocol["baseline"]
    manifest = read_json(V03_MANIFEST)
    hashes = read_json(V03_HASHES)
    terminal = read_json(V02_TERMINAL)
    revalidation = read_json(ROOT / baseline["evidence_revalidation_path"])
    routes_sha = sha256_bytes(canonical_json(manifest["routes"]))
    schedule_sha = sha256_bytes(canonical_json(normalized_schedule(manifest)))
    checks = {
        "protocol_is_unsigned_immutable_candidate": protocol.get("status") == "immutable_candidate_pending_author_signature",
        "current_v0_3_aggregate_bound": hashes.get("aggregate_sha256") == baseline["current_candidate_aggregate_sha256"],
        "selection_rule_bound": revalidation.get("selection", {}).get("selection_sha256") == baseline["selection_sha256"],
        "evidence_revalidation_hash_bound": sha256_file(ROOT / baseline["evidence_revalidation_path"]) == baseline["evidence_revalidation_sha256"],
        "packets_hash_bound": sha256_file(ROOT / baseline["model_visible_packets_path"]) == baseline["model_visible_packets_sha256"],
        "prompt_hash_bound": sha256_file(ROOT / baseline["prompt_path"]) == baseline["prompt_sha256"],
        "schema_hash_bound": sha256_file(ROOT / baseline["schema_path"]) == baseline["schema_sha256"],
        "routes_canonical_hash_bound": routes_sha == baseline["routes_canonical_sha256"],
        "schedule_canonical_hash_bound": schedule_sha == baseline["schedule_canonical_sha256"],
        "factorial_bound": len(manifest["requests"]) == baseline["request_count"] == 72
        and sum(bool(row["canary"]) for row in manifest["requests"]) == baseline["canary_count"] == 8
        and manifest.get("factorial", {}).get("stateless_repeats") == baseline["repeat_count"] == 3,
        "development_boundary_bound": manifest.get("scientific_boundary", {}).get("development_only") is True
        and manifest.get("scientific_boundary", {}).get("confirmatory_exclusion") is True,
        "v0_2_terminal_preserved": terminal.get("execution", {}).get("http_requests") == 8
        and terminal.get("execution", {}).get("valid_model_outputs") == 0
        and terminal.get("execution", {}).get("remaining_requests_started") == 0,
        "active_records_absent_before_signature": not ACTIVE.exists() and not V03_AUTH.exists(),
        "v0_3_output_absent": not V03_OUTPUT.exists(),
        "v0_3_api_not_authorized": hashes.get("api_call_authorized") is False
        and manifest.get("model_api_calls") == 0,
        "allowed_repairs_are_bounded": len(protocol.get("execution_only_repairs", [])) == 6,
        "conformance_and_pause_rules_present": len(protocol.get("mandatory_conformance_before_each_derived_authorization", [])) == 11
        and len(protocol.get("requires_new_author_decision", [])) == 6,
    }
    protocol_sha = sha256_file(PROTOCOL)
    return {
        "audit_id": "dsa_v2_api_pilot_standing_execution_audit_v0_1",
        "created_date": "2026-07-13",
        "status": "passed_pending_single_author_signature" if all(checks.values()) else "failed",
        "protocol_path": PROTOCOL.relative_to(ROOT).as_posix(),
        "protocol_sha256": protocol_sha,
        "current_candidate_aggregate_sha256": hashes["aggregate_sha256"],
        "checks": checks,
        "activity": {"api_keys_read": 0, "model_api_calls": 0, "network_requests": 0},
        "next_action": "Obtain one hash-bound author signature; then activate standing authority and derive the v0.3 execution record without another aggregate signature.",
    }


def signoff_text(audit: dict[str, Any]) -> str:
    return f"""# DSA v0.2 development pilot 一次性持续执行授权签核包 v0.1

状态：`UNSIGNED / NO API / SINGLE SIGNATURE PENDING`

协议 SHA-256：

`{audit['protocol_sha256']}`

当前首个自动派生执行包：v0.3 aggregate
`{audit['current_candidate_aggregate_sha256']}`。

建议作者只签署以下一次性声明。签署后，当前 v0.3 和以后严格通过协议 conformance
Gate 的纯执行链修复版本不再逐 aggregate 请求作者签核。

> 我，高明，签核 DSA v0.2 development pilot standing execution protocol v0.1，
> 协议 SHA-256 为 `{audit['protocol_sha256']}`。我授权执行当前 v0.3 72-call
> development pilot，先运行8-call canary，通过执行完整性 Gate 后自动完成剩余64次；
> 并授权以后仅在 pair、packets、prompt/schema、三条 exact routes、72-request schedule、
> repeats、development-only exclusion 和 no-outcome-rerun 全部机械不变时，对请求序列化、
> credential injection、transport、append-only persistence、deterministic parsing/validation
> 和 audit 实现进行版本化修复，自动生成新 aggregate、conformance audit 与派生执行授权，
> 无需再次由我逐版本签核。推理前且0个有效模型输出的请求可在新版本/新 request domain
> 下重发；保留的 HTTP 200 raw response 必须优先离线重解析；任何已有有效模型输出不得
> 重跑，模型答案方向不得触发重跑、修改或换路线。只有科学表面变化、无法归类的执行错误、
> hidden leakage、hash/ledger/raw-output 完整性失败、公开发布或投稿时暂停由我决定。
> 该授权不允许 pilot 进入确认性 cohort、效果量或 paper-facing effectiveness claim，
> 不授权启动 order63，也不授权绕过任何 hard stop。
"""


def write_or_check(write: bool) -> dict[str, Any]:
    audit = build_audit()
    if audit["status"] != "passed_pending_single_author_signature":
        raise SystemExit("standing authorization proposal audit failed")
    audit_content = json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    signoff_content = signoff_text(audit)
    if write:
        AUDIT.write_text(audit_content, encoding="utf-8", newline="\n")
        SIGNOFF.write_text(signoff_content, encoding="utf-8", newline="\n")
    else:
        if not AUDIT.is_file() or AUDIT.read_text(encoding="utf-8") != audit_content:
            raise SystemExit("stale standing authorization audit")
        if not SIGNOFF.is_file() or SIGNOFF.read_text(encoding="utf-8") != signoff_content:
            raise SystemExit("stale standing authorization signoff package")
    return audit


def activate() -> None:
    audit = write_or_check(False)
    if not DECLARATION.is_file():
        raise SystemExit("activation blocked: author declaration is absent")
    declaration = DECLARATION.read_text(encoding="utf-8").replace("\r\n", "\n").strip()
    required = (
        "我，高明，签核",
        audit["protocol_sha256"],
        "standing execution protocol v0.1",
        "72-call",
        "无需再次由我逐版本签核",
        "任何已有有效模型输出不得",
        "科学表面变化",
        "公开发布或投稿",
    )
    if not all(item in declaration for item in required):
        raise SystemExit("activation blocked: declaration does not contain the frozen standing scope")
    active = {
        "authorization_id": "dsa_v2_api_pilot_standing_authorization_v0_1",
        "created_date": "2026-07-13",
        "status": "author_signed_active",
        "author": "高明",
        "protocol_path": PROTOCOL.relative_to(ROOT).as_posix(),
        "protocol_sha256": audit["protocol_sha256"],
        "declaration_path": DECLARATION.relative_to(ROOT).as_posix(),
        "declaration_sha256": sha256_bytes(declaration.encode("utf-8")),
        "activation_script_sha256": sha256_file(Path(__file__).resolve()),
        "current_candidate_aggregate_sha256": audit["current_candidate_aggregate_sha256"],
        "boundary": "Active only for packages that pass the signed protocol's scientific-surface conformance gate.",
    }
    derived = {
        "authorization_id": "dsa_v2_api_pilot_execution_authorization_v0_3",
        "status": "author_signed_execute_authorized",
        "signed_by": "高明",
        "aggregate_sha256": audit["current_candidate_aggregate_sha256"],
        "authorized_request_count": 72,
        "development_only": True,
        "standing_authorization_id": active["authorization_id"],
        "standing_protocol_sha256": active["protocol_sha256"],
        "scope": {
            "authorizes_api_key_read": True,
            "authorizes_exact_frozen_routes": True,
            "authorizes_transport_only_retry": True,
            "forbids_outcome_rerun": True,
            "forbids_prompt_schema_or_route_change": True,
            "forbids_order63_start": True,
            "forbids_confirmatory_use": True,
            "forbids_public_release_or_submission": True,
        },
    }
    ACTIVE.write_text(json.dumps(active, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    V03_AUTH.write_text(json.dumps(derived, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "activated", "api_keys_read": 0, "model_api_calls": 0}, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write-proposal", action="store_true")
    mode.add_argument("--check-proposal", action="store_true")
    mode.add_argument("--activate", action="store_true")
    args = parser.parse_args()
    if args.activate:
        activate()
        return
    audit = write_or_check(args.write_proposal)
    print(json.dumps({
        "status": audit["status"],
        "protocol_sha256": audit["protocol_sha256"],
        "api_keys_read": 0,
        "model_api_calls": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
