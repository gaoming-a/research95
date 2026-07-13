#!/usr/bin/env python3
"""Audit and summarize the completed DSA v0.3 development pilot.

The tracked outputs contain only hashes, integrity counts, and aggregate
decisions. Provider payloads and response rationales remain under ignored
``outputs/``.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "outputs/dsa_v2_api_pilot_v0_3/request_ledger.jsonl"
MANIFEST = ROOT / "data/protocols/dsa_v2_api_pilot_run_manifest_v0_3.json"
PACKETS = ROOT / "data/protocols/dsa_v2_api_pilot_model_visible_packets_v0_3.jsonl"
PROMPT = ROOT / "prompts/dsa2026_evidence_conditioned_patch_gate_v0_1.md"
REVALIDATION = ROOT / "data/protocols/dsa_v2_api_pilot_evidence_revalidation_v0_1.json"
HASHES = ROOT / "data/protocols/dsa_v2_api_pilot_hash_manifest_v0_3.json"
AUTH = ROOT / "data/protocols/dsa_v2_api_pilot_execution_authorization_v0_3.json"
STANDING = ROOT / "data/protocols/dsa_v2_api_pilot_standing_authorization_v0_1.json"
AUDIT_OUT = ROOT / "data/protocols/dsa_v2_api_pilot_postrun_audit_v0_3.json"
SUMMARY_OUT = ROOT / "data/protocols/dsa_v2_api_pilot_development_summary_v0_3.json"
REPORT_OUT = ROOT / "docs/experiments/dsa_v2_api_pilot_results_v0_3.md"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=False)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def expected_request_body(route: dict[str, Any], rendered: str) -> dict[str, Any]:
    parameters = {
        key: value
        for key, value in route["parameters"].items()
        if key != "stream" and not (isinstance(value, str) and value.startswith("omitted"))
    }
    return {"model": route["model_id"], "messages": [{"role": "user", "content": rendered}], **parameters}


def candidate_roles(revalidation: dict[str, Any]) -> dict[str, str]:
    ordered = sorted(
        (revalidation["roles"][role]["patch_sha256"], role)
        for role in ("positive", "negative")
    )
    return {f"candidate_{index:02d}": role for index, (_, role) in enumerate(ordered, start=1)}


def build() -> tuple[dict[str, Any], dict[str, Any], str]:
    ledger = read_jsonl(LEDGER)
    manifest = read_json(MANIFEST)
    packets = read_jsonl(PACKETS)
    revalidation = read_json(REVALIDATION)
    hashes = read_json(HASHES)
    authorization = read_json(AUTH)
    standing = read_json(STANDING)
    prompt = PROMPT.read_text(encoding="utf-8")
    manifest_by_id = {row["request_id"]: row for row in manifest["requests"]}
    packet_by_id = {row["packet_id"]: row for row in packets}
    route_by_order = {int(row["route_order"]): row for row in manifest["routes"]}
    raw_paths = [attempt["raw_path"] for row in ledger for attempt in row["attempts"]]
    expected_hashes: dict[str, tuple[str, str]] = {}
    for request in manifest["requests"]:
        packet = packet_by_id[request["packet_id"]]["model_visible_packet"]
        rendered = prompt.replace("{{EVIDENCE_PACKET_JSON}}", canonical_json(packet))
        body = expected_request_body(route_by_order[int(request["route_order"])], rendered)
        expected_hashes[request["request_id"]] = (
            sha256_bytes(rendered.encode("utf-8")),
            sha256_bytes(canonical_json(body).encode("utf-8")),
        )
    exact_fields = {"decision", "confidence", "concise_rationale", "evidence_used", "uncertainty"}
    checks = {
        "authorization_matches_aggregate": authorization.get("status") == "author_signed_execute_authorized"
        and authorization.get("aggregate_sha256") == hashes.get("aggregate_sha256")
        and authorization.get("authorized_request_count") == 72,
        "standing_authorization_active": standing.get("status") == "author_signed_active"
        and authorization.get("standing_protocol_sha256") == standing.get("protocol_sha256"),
        "records_exactly_72": len(ledger) == 72,
        "request_ids_unique": len({row["request_id"] for row in ledger}) == 72,
        "request_orders_exact": sorted(row["request_order"] for row in ledger) == list(range(1, 73)),
        "manifest_request_set_exact": {row["request_id"] for row in ledger} == set(manifest_by_id),
        "all_records_valid": all(row["parse_status"] == "valid" for row in ledger),
        "all_response_identities_allowed": all(
            row["response_model_id"] in route_by_order[int(row["route_order"])].get(
                "accepted_response_model_ids", [route_by_order[int(row["route_order"])]["model_id"]]
            ) for row in ledger
        ),
        "all_schema_fields_exact": all(set(row["parsed_response"]) == exact_fields for row in ledger),
        "all_manifest_bindings_match": all(
            row["packet_sha256"] == manifest_by_id[row["request_id"]]["packet_sha256"]
            and row["request_order"] == manifest_by_id[row["request_id"]]["request_order"]
            and row["route_order"] == manifest_by_id[row["request_id"]]["route_order"]
            and row["repeat_index"] == manifest_by_id[row["request_id"]]["repeat_index"]
            for row in ledger
        ),
        "rendered_prompt_and_request_body_hashes_match": all(
            (row["rendered_prompt_sha256"], row["request_body_sha256"]) == expected_hashes[row["request_id"]]
            for row in ledger
        ),
        "raw_paths_unique": len(raw_paths) == len(set(raw_paths)),
        "all_raw_hashes_match": all(
            sha256_file(ROOT / attempt["raw_path"]) == attempt["raw_sha256"]
            for row in ledger for attempt in row["attempts"]
        ),
        "all_single_attempt_http_200": all(
            len(row["attempts"]) == 1 and row["attempts"][0]["http_status"] == 200 for row in ledger
        ),
        "route_balance_24_each": collections.Counter(row["route_order"] for row in ledger) == {1: 24, 2: 24, 3: 24},
        "repeat_balance_24_each": collections.Counter(row["repeat_index"] for row in ledger) == {1: 24, 2: 24, 3: 24},
        "packet_balance_9_each": set(collections.Counter(row["packet_id"] for row in ledger).values()) == {9},
        "openrouter_runtime_route_exact": all(
            row["provider_route_audit"].get("selected_provider") == "Google AI Studio"
            and row["provider_route_audit"].get("attempt") == 1
            and row["provider_route_audit"].get("pipeline_stage_count") == 0
            for row in ledger if row["route_order"] == 3
        ),
    }
    endpoint_attempts = sum(len(row["attempts"]) for row in ledger)
    audit = {
        "audit_id": "dsa_v2_api_pilot_postrun_audit_v0_3",
        "created_date": "2026-07-13",
        "status": "passed_complete_development_only" if all(checks.values()) else "failed",
        "aggregate_sha256": hashes["aggregate_sha256"],
        "standing_protocol_sha256": standing["protocol_sha256"],
        "request_ledger_path": LEDGER.relative_to(ROOT).as_posix(),
        "request_ledger_sha256": sha256_file(LEDGER),
        "activity": {
            "planned_requests": 72,
            "terminal_records": len(ledger),
            "valid_model_outputs": sum(row["parse_status"] == "valid" for row in ledger),
            "endpoint_attempts": endpoint_attempts,
            "requests_with_transport_retry": sum(len(row["attempts"]) > 1 for row in ledger),
            "http_status_counts": dict(sorted(collections.Counter(
                attempt["http_status"] for row in ledger for attempt in row["attempts"]
            ).items())),
        },
        "route_counts": dict(sorted(collections.Counter(row["route_order"] for row in ledger).items())),
        "response_identity_counts": dict(sorted(collections.Counter(row["response_model_id"] for row in ledger).items())),
        "checks": checks,
        "raw_output_policy": "Raw provider responses and rationales remain ignored under outputs/; this tracked audit contains only hashes and aggregate counts.",
        "scientific_boundary": "One mechanically selected legacy pair; development-only and excluded from confirmatory estimates, effect sizes, and paper-facing effectiveness claims.",
    }

    roles = candidate_roles(revalidation)
    observations: dict[tuple[int, str, str], list[dict[str, Any]]] = collections.defaultdict(list)
    for row in ledger:
        packet = packet_by_id[row["packet_id"]]
        role = roles[packet["anonymous_candidate_code"]]
        observations[(int(row["route_order"]), role, packet["condition_code"])].append(row["parsed_response"])
    cells = []
    for (route_order, role, condition), values in sorted(observations.items()):
        counts = collections.Counter(value["decision"] for value in values)
        cells.append({
            "route_order": route_order,
            "provider": route_by_order[route_order]["provider"],
            "model_id": route_by_order[route_order]["model_id"],
            "candidate_role": role,
            "condition": condition,
            "repeats": len(values),
            "decision_counts": {name: counts.get(name, 0) for name in ("accept", "reject", "escalate")},
            "accept_rate": counts.get("accept", 0) / len(values),
            "mean_reported_confidence": sum(float(value["confidence"]) for value in values) / len(values),
            "unanimous_decision": len(counts) == 1,
        })
    cell_index = {(cell["route_order"], cell["candidate_role"], cell["condition"]): cell for cell in cells}
    contrasts = []
    for route_order in sorted(route_by_order):
        for role in ("negative", "positive"):
            c0 = cell_index[(route_order, role, "C0")]["accept_rate"]
            c3 = cell_index[(route_order, role, "C3")]["accept_rate"]
            contrasts.append({
                "route_order": route_order,
                "model_id": route_by_order[route_order]["model_id"],
                "candidate_role": role,
                "c0_accept_rate": c0,
                "c3_accept_rate": c3,
                "development_delta_c3_minus_c0": c3 - c0,
            })
    overall = collections.Counter(row["parsed_response"]["decision"] for row in ledger)
    summary = {
        "summary_id": "dsa_v2_api_pilot_development_summary_v0_3",
        "created_date": "2026-07-13",
        "status": "descriptive_development_only",
        "source_audit_status": audit["status"],
        "task_count": 1,
        "valid_response_count": len(ledger),
        "overall_decision_counts": {name: overall.get(name, 0) for name in ("accept", "reject", "escalate")},
        "repeat_agreement": {
            "unanimous_cells": sum(cell["unanimous_decision"] for cell in cells),
            "total_route_role_condition_cells": len(cells),
        },
        "cells": cells,
        "c0_c3_development_contrasts": contrasts,
        "interpretation": [
            "The end-to-end setting is operational across all three frozen routes: all 72 requests produced schema-valid, identity-valid outputs without retry.",
            "The single legacy pair shows outcome heterogeneity: additional visible evidence does not uniformly suppress acceptance of the hard-negative candidate.",
            "The sample is intentionally development-only and cannot support population effectiveness, confirmatory effect sizes, or paper-facing claims.",
        ],
    }

    def decision_triplet(cell: dict[str, Any]) -> str:
        counts = cell["decision_counts"]
        return f"{counts['accept']}/{counts['reject']}/{counts['escalate']}"

    table = []
    for route_order in sorted(route_by_order):
        for role in ("negative", "positive"):
            values = [decision_triplet(cell_index[(route_order, role, condition)]) for condition in ("C0", "C1", "C2", "C3")]
            contrast = next(item for item in contrasts if item["route_order"] == route_order and item["candidate_role"] == role)
            table.append(
                f"| {route_by_order[route_order]['model_id']} | {role} | "
                + " | ".join(values)
                + f" | {contrast['development_delta_c3_minus_c0']:+.3f} |"
            )
    report = f"""# DSA v0.2 72-call development pilot results v0.3

日期：2026-07-13
状态：`COMPLETE / INTEGRITY PASS / DEVELOPMENT ONLY`

## 执行完整性

- frozen requests：72；terminal records：{len(ledger)}；valid model outputs：{sum(row['parse_status'] == 'valid' for row in ledger)}；
- endpoint attempts：{endpoint_attempts}；transport retries：{sum(len(row['attempts']) > 1 for row in ledger)}；HTTP 200：{sum(attempt['http_status'] == 200 for row in ledger for attempt in row['attempts'])}；
- 三条 route 各24条，三个 repeat 各24条，8个 packets 各9条；
- ledger SHA-256：`{sha256_file(LEDGER)}`；全部 raw hashes、schema、identity、prompt/body hash 和 manifest binding 通过；
- raw provider payload 与 rationale 保留在 ignored `outputs/`，未进入 tracked summary。

## 描述性结果

单元格为三个 repeat 的 `accept/reject/escalate` 计数。`Delta` 是同一 development pair
内 C3 与 C0 的 accept-rate 差，不是确认性效果量。

| model | candidate role | C0 A/R/E | C1 A/R/E | C2 A/R/E | C3 A/R/E | Delta C3-C0 |
|---|---|---:|---:|---:|---:|---:|
{chr(10).join(table)}

- 24个 route × role × condition 单元中，{sum(cell['unanimous_decision'] for cell in cells)}个三次重复完全一致；
- Qwen 对 negative 在 C1 转为 escalate，但 C2/C3 再次全部 accept；
- DeepSeek 对 positive 与 negative 的 C0--C3 均全部 accept；
- Gemini 对 positive 随证据增加趋向 accept，但对 negative 的 C2/C3 仍出现 accept；
- 因此 runner/prompt/schema/route 链路已被真实调用验证，但该单 pair 并未显示“更多证据
  一定减少错误接受”的稳定模式。

## 边界

这是一个机械选择旧证据 pair 的 development pilot，永久排除于确认性 cohort、
`Delta_minus`/`Delta_plus` 估计、样本量与 paper-facing effectiveness claim。结果方向没有
触发重跑、prompt/schema 修改、换模型或 route fallback。
"""
    return audit, summary, report


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    audit, summary, report = build()
    if audit["status"] != "passed_complete_development_only":
        raise SystemExit("post-run integrity audit failed")
    artifacts = {
        AUDIT_OUT: json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        SUMMARY_OUT: json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        REPORT_OUT: report,
    }
    if args.write:
        for path, content in artifacts.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    else:
        for path, content in artifacts.items():
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                raise SystemExit(f"stale post-run artifact: {path}")
    print(json.dumps({
        "status": audit["status"],
        "valid_model_outputs": audit["activity"]["valid_model_outputs"],
        "endpoint_attempts": audit["activity"]["endpoint_attempts"],
        "transport_retries": audit["activity"]["requests_with_transport_retry"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
