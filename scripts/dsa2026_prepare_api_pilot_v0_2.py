# ruff: noqa: E402
"""Prepare and audit the no-API DSA 72-call development pilot.

The script has three explicit modes:

* ``--revalidate`` executes only local Docker checks for the mechanically
  selected legacy pair and writes a sanitized evidence record.
* ``--write`` derives the model-visible packets, the 72-request schedule,
  hash manifest, gate audit, report, and unsigned author sign-off packet.
* ``--check`` reproduces every derived artifact without Docker or API access.

No mode reads an API key or calls a model endpoint.
"""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/dsa2026_prepare_api_pilot_v0_2.py")

import argparse
import copy
import hashlib
import json
import shutil
import subprocess
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CREATED_DATE = "2026-07-13"
PILOT_ID = "dsa_v2_api_pilot_v0_2"
PAIR_DOMAIN = "dsa72-pair-v0.1\0"
P2P_DOMAIN = "dsa72-p2p-v0.1\0"
REQUEST_DOMAIN = "dsa72-request-v0.2\0"
IMAGE_TAG = "dsa2026-api-pilot:v0_1"

LEDGER = ROOT / "data/protocols/dsa_v2_p2_terminal_ledger_v0_62.json"
CANDIDATES = ROOT / "data/patches/evp7_candidates.jsonl"
VISIBLE = ROOT / "data/evidence/evp7_visible_test_outcomes.jsonl"
PROMPT = ROOT / "prompts/dsa2026_evidence_conditioned_patch_gate_v0_1.md"
SCHEMA = ROOT / "data/protocols/dsa_p3_output_schema_v0_1.json"
CONTRACT = ROOT / "data/protocols/dsa_p3_evidence_contract_v0_1.json"
MODEL_FREEZE = ROOT / "data/protocols/dsa_p3_model_freeze_v0_1.json"
ROUTE_VERIFICATION = ROOT / "data/protocols/dsa_v2_api_pilot_public_route_verification_v0_2.json"
ROUTE_OVERRIDE = ROOT / "data/protocols/dsa_v2_api_pilot_openrouter_route_override_v0_2.json"
CATALOG_SNAPSHOT = ROOT / "data/protocols/dsa_v2_api_pilot_openrouter_catalog_snapshot_v0_2.json"
REVOCATION = ROOT / "data/protocols/dsa_v2_api_pilot_execution_authorization_revocation_v0_1.json"
OLD_AUTHORIZATION = ROOT / "data/protocols/dsa_v2_api_pilot_execution_authorization_v0_1.json"
DOCKERFILE = ROOT / "docker/dsa72_pilot/Dockerfile"

REVALIDATION = ROOT / "data/protocols/dsa_v2_api_pilot_evidence_revalidation_v0_1.json"
PACKETS = ROOT / "data/protocols/dsa_v2_api_pilot_model_visible_packets_v0_2.jsonl"
RUN_MANIFEST = ROOT / "data/protocols/dsa_v2_api_pilot_run_manifest_v0_2.json"
HASH_MANIFEST = ROOT / "data/protocols/dsa_v2_api_pilot_hash_manifest_v0_2.json"
GATE_AUDIT = ROOT / "data/protocols/dsa_v2_api_pilot_gate_audit_v0_2.json"
REPORT = ROOT / "docs/experiments/dsa_v2_api_pilot_freeze_v0_2.md"
SIGNOFF = ROOT / "docs/experiments/dsa_v2_api_pilot_author_signoff_v0_2.md"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=False)


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def jsonl_text(rows: list[dict[str, Any]]) -> str:
    return "".join(canonical_json(row) + "\n" for row in rows)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def select_pair() -> dict[str, Any]:
    candidates = read_jsonl(CANDIDATES)
    visible = {row["candidate_id"]: row for row in read_jsonl(VISIBLE)}
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in candidates:
        by_task[str(row["task_id"])].append(row)

    pairs: list[dict[str, Any]] = []
    for task_id, rows in by_task.items():
        positives = [
            row for row in rows
            if row.get("expected_outcome") == "correct"
            and row.get("validation_summary", {}).get("retained_oracle_passed") is True
            and row.get("validation_summary", {}).get("p2p_broad_status") == "passed"
        ]
        negatives = [
            row for row in rows
            if row.get("expected_outcome") != "correct"
            and row.get("validation_summary", {}).get("retained_oracle_ran") is True
            and row.get("validation_summary", {}).get("retained_oracle_passed") is False
            and visible.get(row["evp7_candidate_id"], {}).get("visible_run_summary", {}).get("passed") is True
        ]
        for positive in positives:
            for negative in negatives:
                preimage = (
                    PAIR_DOMAIN + task_id + "\0" + positive["patch_sha256"] + "\0" + negative["patch_sha256"]
                )
                pairs.append({
                    "selection_sha256": sha256_text(preimage),
                    "selection_preimage_domain": "dsa72-pair-v0.1",
                    "task_id": task_id,
                    "positive": positive,
                    "negative": negative,
                })
    if not pairs:
        raise RuntimeError("no mechanically eligible legacy pair")
    pairs.sort(key=lambda row: row["selection_sha256"])
    selected = pairs[0]
    selected["eligible_pair_count"] = len(pairs)
    return selected


def validation_directory(candidate: dict[str, Any]) -> Path:
    validation = Path(candidate["source_files"]["validation_jsonl"])
    return ROOT / validation.parent


def workdir(candidate: dict[str, Any]) -> Path:
    source_id = str(candidate["source_model_candidate_id"])
    return validation_directory(candidate) / "p2p_workdirs" / source_id


def p2p_nodes(selected: dict[str, Any]) -> list[str]:
    manifest_path = ROOT / selected["positive"]["source_files"]["p2p_manifest"]
    manifest = read_json(manifest_path)
    ranked = sorted(
        (sha256_text(P2P_DOMAIN + str(node)), str(node))
        for node in manifest["p2p_broad_tests"]
    )
    return [node for _, node in ranked[:3]]


def image_id() -> str:
    result = subprocess.run(
        ["docker", "image", "inspect", IMAGE_TAG, "--format", "{{.Id}}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0 or not result.stdout.strip().startswith("sha256:"):
        raise RuntimeError(f"missing pilot image {IMAGE_TAG}; build {relative(DOCKERFILE)} first")
    return result.stdout.strip()


def docker_run(mount: Path | None, command: list[str]) -> dict[str, Any]:
    args = ["docker", "run", "--rm", "--network", "none"]
    if mount is not None:
        args += ["--mount", f"type=bind,source={mount},target=/workspace", "-w", "/workspace"]
    args += [IMAGE_TAG, *command]
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return {
        "command": " ".join(command),
        "exit_code": result.returncode,
        "stdout": result.stdout.replace("\r\n", "\n"),
        "stderr": result.stderr.replace("\r\n", "\n"),
    }


def excerpt(result: dict[str, Any], success_marker: str | None = None) -> str:
    combined = (str(result.get("stdout") or "") + "\n" + str(result.get("stderr") or "")).strip()
    if success_marker and success_marker in combined:
        return success_marker
    lines = [line.strip() for line in combined.splitlines() if line.strip()]
    return lines[-1][:500] if lines else "command completed without diagnostics"


def dependency_lock_sha(candidate_dir: Path) -> str:
    paths = [candidate_dir / "bugsinpy_requirements.txt", candidate_dir / "setup.py"]
    records = "".join(f"{path.name}\0{sha256_file(path)}\n" for path in paths)
    return sha256_text(records)


def check_record(code: str, kind: str, result: dict[str, Any], marker: str | None = None, test: str | None = None) -> dict[str, Any]:
    record = {
        "check_code": code,
        "check_kind": kind,
        "command": result["command"],
        "exit_code": result["exit_code"],
        "outcome": "passed" if result["exit_code"] == 0 else "failed",
        "output_excerpt": excerpt(result, marker),
        "stdout_sha256": sha256_text(result["stdout"]),
        "stderr_sha256": sha256_text(result["stderr"]),
    }
    if test is not None:
        record["test_name"] = test
    return record


def revalidate() -> dict[str, Any]:
    selected = select_pair()
    nodes = p2p_nodes(selected)
    digest = image_id()
    runtime_result = docker_run(None, ["python", "--version"])
    if runtime_result["exit_code"] != 0:
        raise RuntimeError("pilot image runtime probe failed")

    role_records: dict[str, Any] = {}
    containers_started = 1
    for role in ("positive", "negative"):
        candidate = selected[role]
        source = workdir(candidate)
        if not source.exists():
            raise RuntimeError(f"missing legacy workdir: {source}")
        patch = source / ".candidate.patch"
        if sha256_file(patch) != candidate["patch_sha256"]:
            raise RuntimeError(f"patch hash mismatch for {role}")
        with tempfile.TemporaryDirectory(prefix=f"dsa72_{role}_") as temp:
            copied = Path(temp) / "workspace"
            shutil.copytree(source, copied)
            prepare = docker_run(copied, ["git", "apply", "--ignore-space-change", "--reverse", ".candidate.patch"])
            containers_started += 1
            if prepare["exit_code"] != 0:
                raise RuntimeError(f"cannot restore buggy baseline for {role}: {prepare['stderr']}")
            patch_check = docker_run(
                copied,
                ["sh", "-lc", "git apply --ignore-space-change --check .candidate.patch && printf patch_check_passed"],
            )
            containers_started += 1
            apply_result = docker_run(copied, ["git", "apply", "--ignore-space-change", ".candidate.patch"])
            containers_started += 1
            if apply_result["exit_code"] != 0:
                raise RuntimeError(f"cannot apply selected patch for {role}: {apply_result['stderr']}")
            syntax = docker_run(
                copied,
                ["python", "-c", "import ast,pathlib; ast.parse(pathlib.Path('youtube_dl/utils.py').read_text()); print('syntax_passed')"],
            )
            containers_started += 1
            f2p_name = "test.test_utils.TestUtil.test_get_element_by_attribute"
            f2p = docker_run(copied, ["python", "-W", "ignore::SyntaxWarning", "-m", "unittest", f2p_name])
            containers_started += 1
            regression = []
            for index, node in enumerate(nodes, start=1):
                result = docker_run(copied, ["python", "-W", "ignore::SyntaxWarning", "-m", "unittest", node])
                containers_started += 1
                regression.append(check_record(f"p2p_{index:02d}", "visible_p2p", result, "OK", node))

        basic = [
            check_record("basic_01", "patch_apply", patch_check, "patch_check_passed"),
            check_record("basic_02", "syntax_or_import_or_static", syntax, "syntax_passed"),
        ]
        f2p_records = [check_record("f2p_01", "visible_f2p", f2p, "OK", f2p_name)]
        all_checks = basic + f2p_records + regression
        role_records[role] = {
            "legacy_candidate_id": candidate["evp7_candidate_id"],
            "source_model_candidate_id": candidate["source_model_candidate_id"],
            "patch_sha256": candidate["patch_sha256"],
            "dependency_lock_sha256": dependency_lock_sha(source),
            "basic_checks": basic,
            "visible_f2p_checks": f2p_records,
            "visible_p2p_checks": regression,
            "all_checks_passed": all(row["outcome"] == "passed" for row in all_checks),
        }

    return {
        "revalidation_id": "dsa_v2_api_pilot_evidence_revalidation_v0_1",
        "created_date_semantics": "artifact protocol date; executed_at_utc is the actual run timestamp",
        "created_date": CREATED_DATE,
        "executed_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "passed" if all(row["all_checks_passed"] for row in role_records.values()) else "failed",
        "purpose": "Development-only evidence revalidation; excluded from confirmatory estimates.",
        "selection": {
            "rule": "minimum SHA-256 over domain, task id, positive patch hash, and negative patch hash",
            "selection_sha256": selected["selection_sha256"],
            "eligible_pair_count": selected["eligible_pair_count"],
            "task_id": selected["task_id"],
        },
        "environment": {
            "runtime": runtime_result["stdout"].strip() or runtime_result["stderr"].strip(),
            "environment_image_sha256": digest.removeprefix("sha256:"),
            "dockerfile_sha256": sha256_file(DOCKERFILE),
            "network_mode": "none",
        },
        "p2p_selection": {
            "rule": "first three SHA-256 ranks under dsa72-p2p-v0.1 domain",
            "nodeids": nodes,
        },
        "roles": role_records,
        "activity": {
            "containers_started": containers_started,
            "model_api_calls": 0,
            "api_keys_read": 0,
            "prompt_renders": 0,
        },
    }


def anonymize_diff(value: str) -> str:
    return value.replace("youtube_dl/utils.py", "module_A.py")


def code_context(candidate: dict[str, Any]) -> str:
    lines = (workdir(candidate) / "youtube_dl/utils.py").read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[359:382])


def model_visible_command(value: str) -> str:
    return value.replace("youtube_dl/utils.py", "module_A.py")


def visible_check(value: dict[str, Any]) -> dict[str, Any]:
    keys = ["check_code", "check_kind", "command", "exit_code", "outcome", "output_excerpt"]
    result = {key: value[key] for key in keys}
    if "test_name" in value:
        result["test_name"] = value["test_name"]
    result["command"] = model_visible_command(str(result["command"]))
    return result


def packet_rows(revalidation: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, str]]:
    selected = select_pair()
    environment_base = revalidation["environment"]
    candidates = [(selected[role]["patch_sha256"], role, selected[role]) for role in ("positive", "negative")]
    candidates.sort()
    anonymous = {role: f"candidate_{index:02d}" for index, (_, role, _) in enumerate(candidates, start=1)}
    rows: list[dict[str, Any]] = []
    packet_hashes: dict[str, str] = {}
    for _, role, candidate in candidates:
        evidence = revalidation["roles"][role]
        env = {
            "runtime": environment_base["runtime"],
            "dependency_lock_sha256": evidence["dependency_lock_sha256"],
            "environment_image_sha256": environment_base["environment_image_sha256"],
        }
        c0 = {
            "change_request": {
                "neutral_description": (
                    "An HTML attribute lookup helper should handle valueless attributes that appear "
                    "before or after the target attribute. Assess the submitted change."
                ),
                "candidate_diff": anonymize_diff(candidate["patch_text"]),
                "code_context": [{
                    "path_code": "module_A.py",
                    "language": "python",
                    "content": code_context(candidate),
                }],
            }
        }
        c1 = copy.deepcopy(c0)
        c1["executable_basic"] = {
            "environment": copy.deepcopy(env),
            "checks": [visible_check(row) for row in evidence["basic_checks"]],
        }
        c2 = copy.deepcopy(c1)
        c2["visible_f2p"] = {
            "environment": copy.deepcopy(env),
            "checks": [visible_check(row) for row in evidence["visible_f2p_checks"]],
        }
        c3 = copy.deepcopy(c2)
        c3["visible_p2p"] = {
            "environment": copy.deepcopy(env),
            "checks": [visible_check(row) for row in evidence["visible_p2p_checks"]],
        }
        for condition, packet in (("C0", c0), ("C1", c1), ("C2", c2), ("C3", c3)):
            packet_id = f"{anonymous[role]}_{condition.lower()}"
            serialized = canonical_json(packet)
            packet_hashes[packet_id] = sha256_text(serialized)
            rows.append({
                "packet_id": packet_id,
                "anonymous_candidate_code": anonymous[role],
                "condition_code": condition,
                "model_visible_packet_sha256": packet_hashes[packet_id],
                "model_visible_packet": packet,
            })
    return rows, packet_hashes


def walk_strings(value: Any) -> list[str]:
    if isinstance(value, dict):
        return [str(key) for key in value] + [item for child in value.values() for item in walk_strings(child)]
    if isinstance(value, list):
        return [item for child in value for item in walk_strings(child)]
    if isinstance(value, str):
        return [value]
    return []


def build_run_manifest(rows: list[dict[str, Any]], packet_hashes: dict[str, str]) -> dict[str, Any]:
    routes = copy.deepcopy(read_json(MODEL_FREEZE)["model_routes"])
    route_override = copy.deepcopy(read_json(ROUTE_OVERRIDE)["route"])
    routes = [route_override if item["route_order"] == 3 else item for item in routes]
    requests: list[dict[str, Any]] = []
    order = 0
    for route in sorted(routes, key=lambda item: item["route_order"]):
        for repeat in (1, 2, 3):
            for row in rows:
                order += 1
                packet_id = row["packet_id"]
                preimage = (
                    REQUEST_DOMAIN + str(route["route_order"]) + "\0" + str(repeat) + "\0" + packet_id
                    + "\0" + packet_hashes[packet_id]
                )
                requests.append({
                    "request_order": order,
                    "request_id": sha256_text(preimage)[:24],
                    "route_order": route["route_order"],
                    "repeat_index": repeat,
                    "packet_id": packet_id,
                    "packet_sha256": packet_hashes[packet_id],
                    "canary": route["route_order"] == 1 and repeat == 1,
                })
    return {
        "run_manifest_id": "dsa_v2_api_pilot_run_manifest_v0_2",
        "created_date": CREATED_DATE,
        "status": "frozen_pending_author_signoff_no_api",
        "pilot_id": PILOT_ID,
        "scientific_boundary": {
            "development_only": True,
            "confirmatory_exclusion": True,
            "effect_estimates_authorized": False,
            "paper_facing_effect_claim_authorized": False,
        },
        "factorial": {
            "tasks": 1,
            "candidates": 2,
            "conditions": 4,
            "model_routes": 3,
            "stateless_repeats": 3,
            "request_count": 72,
            "canary_request_count": 8,
        },
        "prompt": {"path": relative(PROMPT), "sha256": sha256_file(PROMPT)},
        "schema": {"path": relative(SCHEMA), "sha256": sha256_file(SCHEMA)},
        "routes": routes,
        "route_runtime_gate": (
            "Immediately before execution, verify exact endpoint/model identity. Missing identity, alias drift, "
            "fallback, provider-tag drift, or substitution stops that route without replacement."
        ),
        "retry_policy": {
            "scientific_outcome_retry": 0,
            "transport_retry_only": True,
            "transport_retry_limit": 2,
            "retryable": ["HTTP 429", "HTTP 5xx", "timeout", "empty transport body"],
            "non_retryable": ["parse-invalid non-empty response", "valid model decision", "identity mismatch"],
        },
        "execution_gate": {
            "first_stage": "execute eight canary requests",
            "continue_condition": "all canary requests are execution-valid; verdict direction is irrelevant",
            "stop_conditions": [
                "hidden/model-visible separation failure",
                "packet, prompt, schema, route, or runner hash drift",
                "exact model identity failure or provider fallback",
                "credential leakage",
                "append-only ledger continuity failure",
            ],
        },
        "requests": requests,
        "api_call_authorized": False,
        "model_api_calls": 0,
    }


def build_artifacts(revalidation: dict[str, Any]) -> dict[Path, str]:
    rows, packet_hashes = packet_rows(revalidation)
    run_manifest = build_run_manifest(rows, packet_hashes)
    contract = read_json(CONTRACT)
    forbidden = [str(item).lower() for item in contract["forbidden_visible_key_fragments"]]
    visible_text = "\n".join(walk_strings([row["model_visible_packet"] for row in rows])).lower()
    leakage = sorted({marker for marker in forbidden if marker in visible_text})
    prompt_text = PROMPT.read_text(encoding="utf-8")
    render_hashes = {
        row["packet_id"]: sha256_text(prompt_text.replace("{{EVIDENCE_PACKET_JSON}}", canonical_json(row["model_visible_packet"])))
        for row in rows
    }
    cumulative = True
    by_candidate: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        by_candidate[row["anonymous_candidate_code"]][row["condition_code"]] = row["model_visible_packet"]
    expected_keys = {
        "C0": ["change_request"],
        "C1": ["change_request", "executable_basic"],
        "C2": ["change_request", "executable_basic", "visible_f2p"],
        "C3": ["change_request", "executable_basic", "visible_f2p", "visible_p2p"],
    }
    for conditions in by_candidate.values():
        for code, keys in expected_keys.items():
            cumulative = cumulative and list(conditions[code]) == keys
        cumulative = cumulative and conditions["C0"]["change_request"] == conditions["C3"]["change_request"]
        cumulative = cumulative and conditions["C1"]["executable_basic"] == conditions["C3"]["executable_basic"]
        cumulative = cumulative and conditions["C2"]["visible_f2p"] == conditions["C3"]["visible_f2p"]

    packet_text = jsonl_text(rows)
    run_text = pretty_json(run_manifest)
    authoritative = [
        LEDGER, CANDIDATES, VISIBLE, PROMPT, SCHEMA, CONTRACT, MODEL_FREEZE, ROUTE_OVERRIDE,
        ROUTE_VERIFICATION, CATALOG_SNAPSHOT, REVOCATION, DOCKERFILE,
        ROOT / "configs/dsa_v2_api_pilot_v0_2.example.json",
        ROOT / "scripts/dsa2026_run_api_pilot_v0_2.py",
        Path(__file__).resolve(), REVALIDATION,
    ]
    file_rows = [{"path": relative(path), "sha256": sha256_file(path)} for path in authoritative]
    file_rows += [
        {"path": relative(PACKETS), "sha256": sha256_text(packet_text)},
        {"path": relative(RUN_MANIFEST), "sha256": sha256_text(run_text)},
    ]
    aggregate_source = "".join(f"{row['path']}\0{row['sha256']}\n" for row in file_rows)
    manifest = {
        "manifest_id": "dsa_v2_api_pilot_hash_manifest_v0_2",
        "created_date": CREATED_DATE,
        "status": "candidate_freeze_pending_author_signoff",
        "hash_algorithm": "SHA-256",
        "scope": "Authoritative development-pilot inputs plus derived packets and request schedule.",
        "files": file_rows,
        "aggregate_sha256": sha256_text(aggregate_source),
        "api_call_authorized": False,
    }
    manifest_text = pretty_json(manifest)
    ledger = read_json(LEDGER)
    route_verification = read_json(ROUTE_VERIFICATION)
    catalog_snapshot = read_json(CATALOG_SNAPSHOT)
    revocation = read_json(REVOCATION)
    checks = {
        "v0_1_authorization_revoked_before_api": not OLD_AUTHORIZATION.exists()
        and revocation.get("status") == "author_revoked_before_model_call"
        and revocation.get("revoked_aggregate_sha256") == "f8992839f6b47c507ab4bf8e0f49d2e63d6238998a2ff666d674b8eee4cfebeb"
        and revocation.get("activity_at_revocation", {}).get("model_api_calls") == 0,
        "ledger_v0_62_bound": ledger.get("attempted_tasks") == 62 and ledger.get("qualified_pairs") == 0,
        "order63_not_started": ledger.get("next_order") == 63 and ledger.get("next_task_started") is False,
        "revalidation_passed": revalidation.get("status") == "passed",
        "revalidation_api_zero": revalidation.get("activity", {}).get("model_api_calls") == 0,
        "selected_pair_hash_rule_bound": revalidation.get("selection", {}).get("selection_sha256") == select_pair()["selection_sha256"],
        "packet_count_is_8": len(rows) == 8,
        "packet_hashes_unique": len(set(packet_hashes.values())) == 8,
        "c0_c3_strictly_cumulative": cumulative,
        "model_visible_forbidden_markers_absent": leakage == [],
        "prompt_placeholder_exactly_once": prompt_text.count("{{EVIDENCE_PACKET_JSON}}") == 1,
        "render_count_is_8": len(render_hashes) == 8,
        "request_count_is_72": len(run_manifest["requests"]) == 72,
        "request_ids_unique": len({row["request_id"] for row in run_manifest["requests"]}) == 72,
        "canary_count_is_8": sum(bool(row["canary"]) for row in run_manifest["requests"]) == 8,
        "three_routes_three_repeats": len(run_manifest["routes"]) == 3 and {row["repeat_index"] for row in run_manifest["requests"]} == {1, 2, 3},
        "three_routes_public_docs_confirmed": route_verification.get("status") == "public_documentation_confirmed_runtime_identity_pending"
        and len(route_verification.get("routes", [])) == 3
        and all(row.get("exact_model_id_confirmed") is True for row in route_verification["routes"]),
        "openrouter_route_exactly_frozen": run_manifest["routes"][2].get("provider") == "OpenRouter"
        and run_manifest["routes"][2].get("model_id") == "google/gemini-3.5-flash"
        and run_manifest["routes"][2].get("parameters", {}).get("provider", {}).get("only") == ["google-ai-studio/priority"]
        and run_manifest["routes"][2].get("parameters", {}).get("provider", {}).get("allow_fallbacks") is False
        and run_manifest["routes"][2].get("parameters", {}).get("provider", {}).get("require_parameters") is True,
        "openrouter_catalog_snapshot_supports_frozen_route": catalog_snapshot.get("http_status") == 200
        and catalog_snapshot.get("canonical_model_id") == "google/gemini-3.5-flash-20260519"
        and catalog_snapshot.get("selected_provider_tag") == "google-ai-studio/priority"
        and catalog_snapshot.get("selected_provider_supports_required_parameters") is True
        and catalog_snapshot.get("activity", {}).get("model_api_calls") == 0,
        "development_only_boundary": run_manifest["scientific_boundary"]["development_only"] is True,
        "api_not_authorized": run_manifest["api_call_authorized"] is False,
    }
    audit = {
        "audit_id": "dsa_v2_api_pilot_gate_audit_v0_2",
        "created_date": CREATED_DATE,
        "status": "passed_pending_author_signoff" if all(checks.values()) else "failed",
        "checks": checks,
        "leakage_findings": leakage,
        "rendered_prompt_sha256": render_hashes,
        "hash_manifest_aggregate_sha256": manifest["aggregate_sha256"],
        "activity": {"api_keys_read": 0, "model_api_calls": 0, "prompt_renders": 8},
        "next_action": "Obtain hash-bound author sign-off; do not execute an API request in this phase.",
    }
    audit_text = pretty_json(audit)
    report = f"""# DSA v0.2 72-call development pilot freeze v0.2

日期：{CREATED_DATE}
状态：`NO-API FREEZE PASS / AUTHOR SIGN-OFF PENDING`

## 结论

本包机械选择旧证据中的一个 development-only pair，使用同一隔离镜像重新验证 patch
apply、syntax、visible F2P 和三个 visible P2P checks，并冻结 2 candidates × C0--C3 ×
3 routes × 3 repeats = 72 requests。前8项只是执行 canary；答案方向不得成为停止、修改
prompt 或重跑的理由。

该 pair 永久排除于确认性 cohort、效果量和 paper-facing effectiveness claim。

## 机械选择

- eligible legacy pairs：{revalidation['selection']['eligible_pair_count']}
- selection SHA-256：`{revalidation['selection']['selection_sha256']}`
- task id 只保存在私有审计记录，model-visible packets 不含 task/project/role/label。

## 冻结结果

- model-visible packets：8
- planned requests：72
- canary requests：8
- prompt SHA-256：`{sha256_file(PROMPT)}`
- schema SHA-256：`{sha256_file(SCHEMA)}`
- aggregate SHA-256：`{manifest['aggregate_sha256']}`
- model API calls：0

## 尚未授权

作者签核前不得读取 API key、调用 endpoint、把 pilot 回复接入确认性统计、修改 prompt/schema
或启动 order63。真实执行前还必须重新核验三条 exact route；OpenRouter route 固定
`google/gemini-3.5-flash` 与 `google-ai-studio/priority`、禁用 fallback 并要求全部参数受支持。
任一路由发生 alias/fallback/provider-tag/identity mismatch 时停止该 route，不得替换模型。
"""
    signoff = f"""# DSA v0.2 72-call development pilot 作者签核包 v0.2

状态：`UNSIGNED / NO API`

请作者独立核验并在对话中签署以下声明。当前文件本身不构成授权。

绑定 aggregate SHA-256：

`{manifest['aggregate_sha256']}`

建议签核声明：

> 我，高明，签核 DSA v0.2 72-call development pilot v0.2 及其 aggregate SHA-256。
> 我确认该 pilot 仅含一个机械选择的旧证据 pair，永久排除于确认性 cohort、效果量和
> paper-facing effectiveness claim；72项请求、8项 canary、prompt/schema、三条 route、
> 三次 repeat、hidden separation、transport-only retry 和 no-outcome-rerun 均已冻结；第三路线
> 固定为 OpenRouter `google/gemini-3.5-flash` 经 `google-ai-studio/priority`，禁止 provider/model fallback。
> 我授权在 exact route 重新核验和执行 runner check-only 通过后读取所需 API key 并运行
> 该72-call pilot；仅执行故障可触发预注册 transport retry，模型答案方向不得触发重跑、
> 改 prompt 或换模型。该签核不授权启动 order63、进入确认性 V2-P3/P5、公开发布或投稿。
"""
    return {
        PACKETS: packet_text,
        RUN_MANIFEST: run_text,
        HASH_MANIFEST: manifest_text,
        GATE_AUDIT: audit_text,
        REPORT: report,
        SIGNOFF: signoff,
    }


def write_artifacts(artifacts: dict[Path, str]) -> None:
    for path, text in artifacts.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))


def check_artifacts(artifacts: dict[Path, str]) -> None:
    mismatches = []
    for path, expected in artifacts.items():
        if not path.exists() or path.read_text(encoding="utf-8") != expected:
            mismatches.append(relative(path))
    if mismatches:
        raise SystemExit("pilot generated artifact mismatch: " + ", ".join(mismatches))


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--revalidate", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.revalidate:
        value = revalidate()
        REVALIDATION.parent.mkdir(parents=True, exist_ok=True)
        REVALIDATION.write_text(pretty_json(value), encoding="utf-8")
        print(pretty_json({"status": value["status"], "model_api_calls": 0, "selection_sha256": value["selection"]["selection_sha256"]}).strip())
        return 0 if value["status"] == "passed" else 1
    if not REVALIDATION.exists():
        raise SystemExit(f"missing {relative(REVALIDATION)}; run --revalidate first")
    revalidation_value = read_json(REVALIDATION)
    artifacts = build_artifacts(revalidation_value)
    if args.write:
        write_artifacts(artifacts)
    else:
        check_artifacts(artifacts)
    audit = json.loads(artifacts[GATE_AUDIT])
    print(pretty_json({
        "status": audit["status"],
        "aggregate_sha256": audit["hash_manifest_aggregate_sha256"],
        "requests": 72,
        "model_api_calls": 0,
    }).strip())
    return 0 if audit["status"] == "passed_pending_author_signoff" else 1


if __name__ == "__main__":
    raise SystemExit(main())
