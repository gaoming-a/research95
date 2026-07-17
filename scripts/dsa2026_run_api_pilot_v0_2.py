# ruff: noqa: E402
"""Guarded runner for the DSA 72-call development pilot.

Default and ``--check-only`` modes never read credentials or contact a model.
Execution requires a separate hash-bound author authorization record that does
not exist in the unsigned freeze package. Raw responses remain under ignored
``outputs/`` and the request ledger is append-only.
"""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/dsa2026_run_api_pilot_v0_2.py")

import argparse
import copy
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKETS = ROOT / "data/protocols/dsa_v2_api_pilot_model_visible_packets_v0_2.jsonl"
RUN_MANIFEST = ROOT / "data/protocols/dsa_v2_api_pilot_run_manifest_v0_2.json"
HASH_MANIFEST = ROOT / "data/protocols/dsa_v2_api_pilot_hash_manifest_v0_2.json"
GATE_AUDIT = ROOT / "data/protocols/dsa_v2_api_pilot_gate_audit_v0_2.json"
PROMPT = ROOT / "prompts/dsa2026_evidence_conditioned_patch_gate_v0_1.md"
SCHEMA = ROOT / "data/protocols/dsa_p3_output_schema_v0_1.json"
DEFAULT_CONFIG = ROOT / "configs/dsa_v2_api_pilot_v0_2.example.json"
CHECK_OUT = ROOT / "data/protocols/dsa_v2_api_pilot_runner_check_only_v0_2.json"


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


def resolve(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def load_surfaces() -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    manifest = read_json(RUN_MANIFEST)
    packets = read_jsonl(PACKETS)
    hashes = read_json(HASH_MANIFEST)
    audit = read_json(GATE_AUDIT)
    return manifest, packets, hashes, audit


def verify_schema(value: Any) -> tuple[bool, str]:
    if not isinstance(value, dict):
        return False, "response is not an object"
    required = {"decision", "confidence", "concise_rationale", "evidence_used", "uncertainty"}
    if set(value) != required:
        return False, "response fields are not exact"
    if value["decision"] not in {"accept", "reject", "escalate"}:
        return False, "invalid decision"
    if isinstance(value["confidence"], bool) or not isinstance(value["confidence"], (int, float)):
        return False, "confidence is not numeric"
    if not 0 <= value["confidence"] <= 1:
        return False, "confidence outside [0,1]"
    if not isinstance(value["concise_rationale"], str) or not 1 <= len(value["concise_rationale"]) <= 1200:
        return False, "invalid concise_rationale"
    if not isinstance(value["evidence_used"], list) or not 1 <= len(value["evidence_used"]) <= 12:
        return False, "invalid evidence_used"
    if not all(isinstance(item, str) and 1 <= len(item) <= 240 for item in value["evidence_used"]):
        return False, "invalid evidence_used item"
    if not isinstance(value["uncertainty"], str) or not 1 <= len(value["uncertainty"]) <= 600:
        return False, "invalid uncertainty"
    return True, "valid"


def check_only(config: dict[str, Any]) -> dict[str, Any]:
    manifest, packets, hashes, audit = load_surfaces()
    packet_by_id = {row["packet_id"]: row for row in packets}
    file_checks = {}
    for row in hashes["files"]:
        path = resolve(row["path"])
        file_checks[row["path"]] = path.exists() and sha256_file(path) == row["sha256"]
    prompt = PROMPT.read_text(encoding="utf-8")
    rendered = []
    nested_only = True
    for request in manifest["requests"]:
        row = packet_by_id[request["packet_id"]]
        packet = row["model_visible_packet"]
        packet_sha = sha256_bytes(canonical_json(packet).encode("utf-8"))
        nested_only = nested_only and packet_sha == request["packet_sha256"]
        rendered.append(prompt.replace("{{EVIDENCE_PACKET_JSON}}", canonical_json(packet)))
    credential_names = config.get("credential_env", {})
    valid_fixture = {
        "decision": "escalate",
        "confidence": 0.5,
        "concise_rationale": "The supplied evidence is incomplete.",
        "evidence_used": ["A candidate diff is present."],
        "uncertainty": "No executable evidence is present.",
    }
    invalid_fixtures = [
        {**valid_fixture, "extra": "forbidden"},
        {key: value for key, value in valid_fixture.items() if key != "uncertainty"},
        {**valid_fixture, "decision": "approve"},
        {**valid_fixture, "confidence": True},
        {**valid_fixture, "evidence_used": []},
    ]
    route_requests = [request_body(route, rendered[0]) for route in manifest["routes"]]
    route_headers = [item[0] for item in route_requests]
    route_bodies = [item[1] for item in route_requests]
    openrouter_route = manifest["routes"][2]
    schema_core = read_json(SCHEMA)
    for metadata_key in ("$schema", "$id", "title"):
        schema_core.pop(metadata_key, None)
    openrouter_valid = {
        "model": "google/gemini-3.5-flash",
        "choices": [{"message": {"content": json.dumps(valid_fixture)}}],
        "openrouter_metadata": {
            "requested": "google/gemini-3.5-flash",
            "strategy": "direct",
            "attempt": 1,
            "endpoints": {"available": [{
                "provider": "Google AI Studio",
                "model": "google/gemini-3.5-flash-20260519",
                "selected": True,
            }]},
            "attempts": [{
                "provider": "Google AI Studio",
                "model": "google/gemini-3.5-flash-20260519",
                "status": 200,
            }],
            "pipeline": [],
        },
    }
    try:
        extract_response(openrouter_route, openrouter_valid)
        openrouter_fixture_valid = True
    except (KeyError, TypeError, ValueError):
        openrouter_fixture_valid = False
    openrouter_bad = []
    for mutation in ("wrong_model", "wrong_provider", "fallback_attempt", "pipeline_mutation"):
        fixture = copy.deepcopy(openrouter_valid)
        if mutation == "wrong_model":
            fixture["model"] = "google/gemini-3.5-flash:free"
        elif mutation == "wrong_provider":
            fixture["openrouter_metadata"]["endpoints"]["available"][0]["provider"] = "Google Vertex"
        elif mutation == "fallback_attempt":
            fixture["openrouter_metadata"]["attempt"] = 2
        else:
            fixture["openrouter_metadata"]["pipeline"] = [{"type": "response_healing"}]
        try:
            extract_response(openrouter_route, fixture)
            openrouter_bad.append(False)
        except (KeyError, TypeError, ValueError):
            openrouter_bad.append(True)
    checks = {
        "hash_manifest_status_pending_signoff": hashes.get("status") == "candidate_freeze_pending_author_signoff",
        "all_authoritative_hashes_match": all(file_checks.values()),
        "gate_audit_passed": audit.get("status") == "passed_pending_author_signoff",
        "run_manifest_no_api": manifest.get("api_call_authorized") is False and manifest.get("model_api_calls") == 0,
        "packets_exactly_8": len(packets) == 8 and len(packet_by_id) == 8,
        "requests_exactly_72": len(manifest.get("requests", [])) == 72,
        "canary_exactly_8": sum(bool(row.get("canary")) for row in manifest["requests"]) == 8,
        "runner_passes_only_nested_model_visible_packet": nested_only,
        "rendered_prompt_count_72": len(rendered) == 72,
        "rendered_placeholders_absent": all("{{EVIDENCE_PACKET_JSON}}" not in text for text in rendered),
        "outer_packet_metadata_not_rendered": all(
            token not in text
            for text in rendered
            for token in ("candidate_01", "candidate_02", '"condition_code"', '"packet_id"')
        ),
        "schema_file_matches_manifest": sha256_file(SCHEMA) == manifest["schema"]["sha256"],
        "schema_accepts_valid_fixture": verify_schema(valid_fixture)[0] is True,
        "schema_rejects_adversarial_fixtures": all(verify_schema(value)[0] is False for value in invalid_fixtures),
        "three_provider_request_bodies_build": len(route_bodies) == 3,
        "openrouter_request_route_is_pinned": route_bodies[2].get("provider") == {
            "only": ["google-ai-studio/priority"],
            "allow_fallbacks": False,
            "require_parameters": True,
        },
        "openrouter_router_metadata_opted_in": route_headers[2].get("X-OpenRouter-Metadata") == "enabled",
        "openrouter_reasoning_is_minimal_and_excluded": route_bodies[2].get("reasoning") == {
            "effort": "minimal",
            "exclude": True,
        },
        "openrouter_strict_schema_matches_frozen_core": route_bodies[2].get("response_format") == {
            "type": "json_schema",
            "json_schema": {
                "name": "dsa_patch_gate_response",
                "strict": True,
                "schema": schema_core,
            },
        },
        "openrouter_identity_allowlist_exact": openrouter_route.get("accepted_response_model_ids") == [
            "google/gemini-3.5-flash",
            "google/gemini-3.5-flash-20260519",
        ],
        "openrouter_runtime_metadata_fixture_valid": openrouter_fixture_valid,
        "openrouter_runtime_metadata_adversarial_rejected": all(openrouter_bad),
        "request_bodies_contain_no_credentials": all("api_key" not in canonical_json(body).lower() for body in route_bodies),
        "credential_names_only": set(credential_names) == {"1", "2", "3"}
        and all(isinstance(value, str) and value.endswith("API_KEY") for value in credential_names.values()),
        "authorization_record_absent_before_signoff": not resolve(config["authorization_record"]).exists(),
        "api_keys_not_read": True,
        "model_api_calls_zero": True,
    }
    return {
        "check_id": "dsa_v2_api_pilot_runner_check_only_v0_2",
        "created_date": "2026-07-13",
        "status": "passed_no_api_author_signoff_pending" if all(checks.values()) else "failed",
        "checks": checks,
        "file_hash_checks": file_checks,
        "rendered_prompt_max_utf8_bytes": max(len(text.encode("utf-8")) for text in rendered),
        "activity": {"api_keys_read": 0, "model_api_calls": 0, "network_requests": 0},
        "next_action": "Obtain hash-bound author sign-off before creating the execution authorization record.",
    }


def authorization(config: dict[str, Any], hashes: dict[str, Any]) -> dict[str, Any]:
    path = resolve(config["authorization_record"])
    if not path.exists():
        raise SystemExit("execution blocked: author authorization record is absent")
    value = read_json(path)
    if value.get("status") != "author_signed_execute_authorized":
        raise SystemExit("execution blocked: author authorization status is not signed")
    if value.get("aggregate_sha256") != hashes.get("aggregate_sha256"):
        raise SystemExit("execution blocked: authorization hash does not bind the frozen package")
    if value.get("authorized_request_count") != 72 or value.get("development_only") is not True:
        raise SystemExit("execution blocked: authorization scope mismatch")
    return value


def read_credentials(config: dict[str, Any]) -> dict[int, str]:
    credentials = {}
    for route, name in config["credential_env"].items():
        value = os.environ.get(name, "").strip()
        if not value:
            raise SystemExit(f"execution blocked: missing credential environment variable {name}")
        credentials[int(route)] = value
    return credentials


def request_body(route: dict[str, Any], rendered_prompt: str) -> tuple[dict[str, str], dict[str, Any]]:
    parameters = dict(route["parameters"])
    parameters.pop("stream", None)
    headers = {"Content-Type": "application/json"}
    if route["api_style"] == "OpenRouter Chat Completions":
        headers["X-OpenRouter-Metadata"] = "enabled"
    return headers, {
        "model": route["model_id"],
        "messages": [{"role": "user", "content": rendered_prompt}],
        **parameters,
    }


def extract_response(route: dict[str, Any], payload: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    identity = str(payload.get("model") or "")
    text = str(payload["choices"][0]["message"]["content"])
    allowed_ids = route.get("accepted_response_model_ids", [route["model_id"]])
    if identity not in allowed_ids:
        raise ValueError(f"identity mismatch: {identity!r}")
    route_audit: dict[str, Any] = {}
    if route["api_style"] == "OpenRouter Chat Completions":
        metadata = payload.get("openrouter_metadata")
        if not isinstance(metadata, dict):
            raise ValueError("OpenRouter routing metadata is absent")
        selected = [
            item for item in metadata.get("endpoints", {}).get("available", [])
            if isinstance(item, dict) and item.get("selected") is True
        ]
        attempts = metadata.get("attempts", [])
        pipeline = metadata.get("pipeline", [])
        if metadata.get("requested") != route["model_id"] or metadata.get("strategy") != "direct":
            raise ValueError("OpenRouter requested model or strategy drift")
        if metadata.get("attempt") != 1 or len(selected) != 1:
            raise ValueError("OpenRouter provider fallback or selection ambiguity")
        if selected[0].get("provider") != route["expected_provider_name"]:
            raise ValueError("OpenRouter provider identity mismatch")
        if selected[0].get("model") not in allowed_ids:
            raise ValueError("OpenRouter selected model identity mismatch")
        if attempts and (len(attempts) != 1 or attempts[0].get("provider") != route["expected_provider_name"]
                         or attempts[0].get("status") != 200):
            raise ValueError("OpenRouter attempts show fallback or provider drift")
        if pipeline:
            raise ValueError("OpenRouter pipeline transformed the request or response")
        route_audit = {
            "requested": metadata["requested"],
            "strategy": metadata["strategy"],
            "attempt": metadata["attempt"],
            "selected_provider": selected[0]["provider"],
            "selected_model": selected[0]["model"],
            "pipeline_stage_count": 0,
        }
    return identity, text, route_audit


def call(route: dict[str, Any], credential: str, rendered_prompt: str, timeout: int) -> tuple[int, bytes]:
    headers, body = request_body(route, rendered_prompt)
    headers["Authorization"] = f"Bearer {credential}"
    request = urllib.request.Request(
        route["endpoint"],
        data=canonical_json(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return int(response.status), response.read()
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read()
    except (urllib.error.URLError, TimeoutError) as exc:
        return 0, str(exc).encode("utf-8", errors="replace")


def load_completed(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    completed = {}
    for row in read_jsonl(path):
        request_id = str(row["request_id"])
        if request_id in completed:
            raise SystemExit(f"append-only ledger contains duplicate request id {request_id}")
        completed[request_id] = row
    return completed


def execute(config: dict[str, Any], canary_only: bool) -> None:
    manifest, packets, hashes, audit = load_surfaces()
    preflight = check_only(config)
    preflight_failures = [
        name for name, passed in preflight["checks"].items()
        if not passed and name != "authorization_record_absent_before_signoff"
    ]
    if preflight_failures:
        raise SystemExit(f"execution blocked: frozen-surface preflight failed: {preflight_failures}")
    authorization(config, hashes)
    if audit.get("status") != "passed_pending_author_signoff":
        raise SystemExit("execution blocked: freeze audit is not passed")
    credentials = read_credentials(config)
    packet_by_id = {row["packet_id"]: row["model_visible_packet"] for row in packets}
    route_by_order = {int(row["route_order"]): row for row in manifest["routes"]}
    output_dir = resolve(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = output_dir / "request_ledger.jsonl"
    raw_dir = output_dir / "raw_provider_responses"
    raw_dir.mkdir(parents=True, exist_ok=True)
    completed = load_completed(ledger_path)
    prompt = PROMPT.read_text(encoding="utf-8")
    timeout = int(config.get("request_timeout_seconds", 180))

    canary_rows = [row for row in manifest["requests"] if row["canary"]]
    if not canary_only:
        canary_ids = {row["request_id"] for row in canary_rows}
        if not canary_ids.issubset(completed):
            raise SystemExit("full execution blocked: all eight canary records must exist first")
        canary_valid = all(
            completed[request_id].get("parse_status") == "valid"
            and completed[request_id].get("response_model_id") == completed[request_id].get("configured_model_id")
            for request_id in canary_ids
        )
        if not canary_valid:
            raise SystemExit("full execution blocked: canary execution validity gate failed")
    target = canary_rows if canary_only else manifest["requests"]
    with ledger_path.open("a", encoding="utf-8") as handle:
        for item in target:
            if item["request_id"] in completed:
                continue
            route = route_by_order[int(item["route_order"])]
            packet = packet_by_id[item["packet_id"]]
            rendered = prompt.replace("{{EVIDENCE_PACKET_JSON}}", canonical_json(packet))
            rendered_sha256 = sha256_bytes(rendered.encode("utf-8"))
            _, frozen_body = request_body(route, rendered)
            request_body_sha256 = sha256_bytes(canonical_json(frozen_body).encode("utf-8"))
            attempts = []
            final_record = None
            for attempt_index in range(1, 4):
                status, raw = call(route, credentials[int(item["route_order"])], rendered, timeout)
                raw_sha = sha256_bytes(raw)
                raw_path = raw_dir / f"{item['request_id']}_attempt_{attempt_index}.json"
                if raw_path.exists():
                    raise SystemExit(f"append-only raw response path already exists: {raw_path}")
                raw_path.write_bytes(raw)
                retryable = status == 0 or status == 429 or 500 <= status <= 599 or (status == 200 and not raw)
                attempts.append({
                    "attempt_index": attempt_index,
                    "http_status": status,
                    "raw_sha256": raw_sha,
                    "raw_path": raw_path.relative_to(ROOT).as_posix(),
                })
                if retryable and attempt_index < 3:
                    time.sleep(attempt_index)
                    continue
                parse_status = "transport_failure"
                identity = ""
                route_audit: dict[str, Any] = {}
                parsed_value = None
                error = ""
                if status == 200 and raw:
                    try:
                        provider_payload = json.loads(raw.decode("utf-8"))
                        identity, text, route_audit = extract_response(route, provider_payload)
                        parsed_value = json.loads(text.strip())
                        valid, error = verify_schema(parsed_value)
                        parse_status = "valid" if valid else "schema_invalid"
                    except Exception as exc:  # strict terminal parsing; never salvaged or retried
                        error = str(exc)
                        parse_status = "parse_or_identity_invalid"
                final_record = {
                    "request_id": item["request_id"],
                    "request_order": item["request_order"],
                    "route_order": item["route_order"],
                    "repeat_index": item["repeat_index"],
                    "packet_id": item["packet_id"],
                    "packet_sha256": item["packet_sha256"],
                    "rendered_prompt_sha256": rendered_sha256,
                    "request_body_sha256": request_body_sha256,
                    "configured_model_id": route["model_id"],
                    "response_model_id": identity,
                    "provider_route_audit": route_audit if status == 200 and raw else {},
                    "parse_status": parse_status,
                    "parsed_response": parsed_value,
                    "error": error,
                    "attempts": attempts,
                }
                break
            if final_record is None:
                raise RuntimeError("unreachable: request produced no terminal record")
            handle.write(json.dumps(final_record, ensure_ascii=False, sort_keys=True) + "\n")
            handle.flush()
            completed[item["request_id"]] = final_record
            if final_record["parse_status"] in {"parse_or_identity_invalid", "schema_invalid"}:
                raise SystemExit(f"hard stop at request {item['request_id']}: {final_record['error']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check-only", action="store_true")
    mode.add_argument("--execute-canary", action="store_true")
    mode.add_argument("--execute-all", action="store_true")
    args = parser.parse_args()
    config = read_json(args.config)
    if args.execute_canary or args.execute_all:
        execute(config, canary_only=args.execute_canary)
        return 0
    value = check_only(config)
    CHECK_OUT.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": value["status"], "api_keys_read": 0, "model_api_calls": 0}, sort_keys=True))
    return 0 if value["status"] == "passed_no_api_author_signoff_pending" else 1


if __name__ == "__main__":
    raise SystemExit(main())
