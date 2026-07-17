#!/usr/bin/env python3
"""Audit and enforce fail-closed isolation of every prior research lineage."""

from __future__ import annotations

import argparse
import ast
import concurrent.futures
import copy
import fnmatch
import hashlib
import json
import re
import stat
import subprocess
import urllib.parse
from datetime import UTC, date, datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/protocols/research_lineage_quarantine_v0_1.json"
FUTURE_MANIFEST = ROOT / "data/protocols/future_research_input_manifest_v0_1.json"
AUDIT_JSON = ROOT / "data/protocols/research_lineage_isolation_audit_v0_1.json"
AUDIT_MD = ROOT / "docs/experiments/research_lineage_isolation_v0_1.md"
CONTENT_FINGERPRINTS = ROOT / "data/protocols/research_lineage_blocked_content_fingerprints_v0_1.json"
PAYLOAD_EXCLUSIONS = ROOT / "data/protocols/research_lineage_payload_exclusion_registry_v0_1.json"

LEGACY_DENYLIST = ROOT / "data/protocols/dsa_legacy_analysis_denylist_v0_1.json"
LEGACY_TASKS = ROOT / "data/protocols/dsa_legacy_task_exclusion_registry_v0_1.json"
DEVELOPMENT_TASKS = ROOT / "data/protocols/dsa_p2_development_exclusion_registry_v0_1.json"
V01_TERMINATION = ROOT / "data/protocols/dsa_v0_1_termination_and_v0_2_redesign_v0_1.json"
V2_LEDGER = ROOT / "data/protocols/dsa_v2_p2_terminal_ledger_v0_62.json"
PILOT_REVALIDATION = ROOT / "data/protocols/dsa_v2_api_pilot_evidence_revalidation_v0_1.json"
PILOT_POSTRUN = ROOT / "data/protocols/dsa_v2_api_pilot_postrun_audit_v0_3.json"
EVP8_CANDIDATE_SET = ROOT / "data/protocols/evp8_candidate_set_v0_1.json"
EVP8_HARDNEG_STRESS = ROOT / "data/protocols/evp8_realistic_hardneg_stress_cohort_v0_1.json"
DSA_SOURCE_FRAME = ROOT / "data/protocols/dsa_p2_source_frame_v0_1.json"

HEX64 = re.compile(r"[0-9a-f]{64}")
SHA256_JSON_STRING_PATTERN = r'"[0-9a-f]{64}"'
PATCH_SHA256_FIELD_PATTERN = (
    r'"[^"]*patch[^"]*"[[:space:]]*:[[:space:]]*"[0-9a-f]{64}"'
)
SELECTED_CANDIDATE_SHA256_FIELD_PATTERN = (
    r'"selected_candidate_sha256"[[:space:]]*:[[:space:]]*"[0-9a-f]{64}"'
)
MANIFEST_KEYS = {
    "manifest_id",
    "created_date",
    "status",
    "study_id",
    "quarantine_registry_canonical_sha256",
    "namespace",
    "selection_inputs",
    "records",
    "authorization",
    "boundary",
}
RECORD_KEYS = {
    "sample_id",
    "split",
    "source_dataset",
    "upstream_source_uri",
    "upstream_release_id",
    "upstream_item_id",
    "upstream_payload_sha256",
    "project",
    "task_id",
    "artifact_paths",
    "artifact_sha256s",
    "source_payload_sha256s",
    "origin_study_ids",
}
ALLOWED_SPLITS = {"train", "development", "validation", "test"}
SIGNOFF_STATEMENT = (
    "I attest that this study was selected independently of quarantined results, "
    "and I authorize only the exact pre-use manifest bound here."
)
EXPECTED_PROJECTION_SOURCES = {
    "data/protocols/dsa_legacy_analysis_denylist_v0_1.json",
    "data/protocols/dsa_legacy_task_exclusion_registry_v0_1.json",
    "data/protocols/dsa_p2_development_exclusion_registry_v0_1.json",
    "data/protocols/dsa_v0_1_termination_and_v0_2_redesign_v0_1.json",
    "data/protocols/dsa_v2_p2_terminal_ledger_v0_62.json",
    "data/protocols/dsa_v2_api_pilot_evidence_revalidation_v0_1.json",
    "data/protocols/dsa_v2_api_pilot_postrun_audit_v0_3.json",
    "data/protocols/evp8_candidate_set_v0_1.json",
    "data/protocols/evp8_realistic_hardneg_stress_cohort_v0_1.json",
    "data/protocols/dsa_p2_source_frame_v0_1.json",
}
EXPECTED_REVOKED_AUTHORIZATION_IDS = {
    "dsa_v2_p2_continuous_authorization_v0_1",
    "dsa_v2_api_pilot_standing_authorization_v0_1",
    "dsa_v2_api_pilot_execution_authorization_v0_2",
    "dsa_v2_api_pilot_execution_authorization_v0_3",
}
GUARD_IMPORT_MODULES = {
    "audit_research_lineage_isolation",
    "cross_review.research_lineage_isolation",
}
PROJECT_TIMEZONE = timezone(timedelta(hours=8), name="Asia/Shanghai")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {display(path)}")
    return value


def display(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_sha256(path: Path) -> str:
    value = read_json(path)
    canonical = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def canonical_value_sha256(value: Any) -> str:
    canonical = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def projection_hash(values: list[str]) -> str:
    return hashlib.sha256(("\n".join(sorted(values, key=str.casefold)) + "\n").encode()).hexdigest()


def serialized(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def project_from_task_id(task_id: str) -> str:
    if not task_id.startswith("bugsinpy_") or "_" not in task_id.removeprefix("bugsinpy_"):
        raise ValueError(f"unrecognized task identifier: {task_id}")
    return task_id.removeprefix("bugsinpy_").rsplit("_", 1)[0]


def normalized_repo_path(value: Any) -> str | None:
    if not isinstance(value, str) or not value or "\\" in value:
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value:
        return None
    return value


def is_canonical_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and value == value.strip()
        and value.isprintable()
    )


def manifest_created_date_is_valid(value: Any, registry: dict[str, Any]) -> bool:
    try:
        created = date.fromisoformat(value)
        effective = date.fromisoformat(registry["effective_date"])
    except (KeyError, TypeError, ValueError):
        return False
    return effective <= created <= datetime.now(PROJECT_TIMEZONE).date()


def path_matches_any(path: str, patterns: list[str]) -> bool:
    folded = path.casefold()
    return any(fnmatch.fnmatchcase(folded, pattern.casefold()) for pattern in patterns)


def is_regular_non_reparse_file(path: Path) -> bool:
    if not path.is_file() or path.is_symlink():
        return False
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    return not bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def path_chain_is_non_reparse(path: Path, trusted_root: Path) -> bool:
    """Reject aliases through symlink, junction, or other reparse-point parents."""
    try:
        relative = path.relative_to(trusted_root)
    except ValueError:
        return False
    current = trusted_root
    for part in relative.parts:
        current /= part
        try:
            metadata = current.lstat()
        except OSError:
            return False
        if current.is_symlink():
            return False
        attributes = getattr(metadata, "st_file_attributes", 0)
        if attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
            return False
    return True


def git_blob_oid(path: str) -> str:
    completed = subprocess.run(
        ["git", "hash-object", f"--path={path}", path],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="strict",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return completed.stdout.strip()


def git_head_blob_oid(path: str) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", f"HEAD:{path}"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="strict",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return completed.stdout.strip()


def fingerprint_scope_sha256(declaration: dict[str, Any]) -> str:
    return canonical_value_sha256(
        {
            "included_path_globs": sorted(declaration["included_path_globs"], key=str.casefold),
            "excluded_path_globs": sorted(declaration["excluded_path_globs"], key=str.casefold),
        }
    )


def path_is_in_fingerprint_scope(path: str, declaration: dict[str, Any]) -> bool:
    return path_matches_any(path, declaration["included_path_globs"]) and not path_matches_any(
        path,
        declaration["excluded_path_globs"],
    )


def git_tree_blob_map(commit: str) -> dict[str, str]:
    tree = subprocess.check_output(["git", "ls-tree", "-r", "-z", commit], cwd=ROOT)
    result = {}
    for raw_record in tree.split(b"\0"):
        if not raw_record:
            continue
        metadata, raw_path = raw_record.split(b"\t", 1)
        _mode, kind, oid = metadata.decode("ascii").split()
        if kind == "blob":
            result[raw_path.decode("utf-8")] = oid
    return result


def git_grep_sha256_tokens(
    commit: str,
    pattern: str,
    pathspecs: list[str],
) -> dict[str, set[str]]:
    completed = subprocess.run(
        ["git", "grep", "-I", "-E", "-o", pattern, commit, "--", *pathspecs],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="strict",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode not in {0, 1}:
        raise subprocess.CalledProcessError(
            completed.returncode,
            completed.args,
            output=completed.stdout,
            stderr=completed.stderr,
        )
    result: dict[str, set[str]] = {}
    for line in completed.stdout.splitlines():
        revision, path, fragment = line.split(":", 2)
        if revision != commit:
            raise ValueError(f"unexpected git-grep revision: {revision}")
        token_match = re.search(r"[0-9a-f]{64}", fragment)
        if token_match is None:
            raise ValueError(f"git-grep output lacks SHA-256 token: {path}")
        result.setdefault(path, set()).add(token_match.group())
    return result


def discover_payload_sources(
    registry: dict[str, Any],
    commit: str,
) -> tuple[dict[str, set[str]], set[str]]:
    declaration = registry["payload_exclusion_registry"]
    pathspecs = declaration["source_git_pathspecs"]
    metadata = git_grep_sha256_tokens(commit, SHA256_JSON_STRING_PATTERN, pathspecs)
    patch_fields = git_grep_sha256_tokens(commit, PATCH_SHA256_FIELD_PATTERN, pathspecs)
    selected_fields = git_grep_sha256_tokens(
        commit,
        SELECTED_CANDIDATE_SHA256_FIELD_PATTERN,
        pathspecs,
    )
    patch_payloads = set().union(*patch_fields.values(), *selected_fields.values())
    return metadata, patch_payloads


def freeze_payload_exclusions(registry: dict[str, Any]) -> dict[str, Any]:
    source_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, encoding="utf-8"
    ).strip()
    discovered, patch_payloads = discover_payload_sources(registry, source_commit)
    tree_blobs = git_tree_blob_map(source_commit)
    sources = [
        {
            "path": path,
            "source_commit_blob_oid": tree_blobs[path],
            "unique_metadata_sha256_count": len(discovered[path]),
        }
        for path in sorted(discovered)
    ]
    metadata_identifiers = sorted(set().union(*discovered.values()))
    sorted_patch_payloads = sorted(patch_payloads)
    return {
        "registry_id": "research_lineage_payload_exclusion_registry_v0_1",
        "created_date": "2026-07-18",
        "status": "frozen_at_isolation_cutoff",
        "source_commit": source_commit,
        "source_count": len(sources),
        "source_path_projection_sha256": projection_hash(list(discovered)),
        "sources": sources,
        "patch_payload_sha256_count": len(sorted_patch_payloads),
        "patch_payload_projection_sha256": projection_hash(sorted_patch_payloads),
        "patch_payload_sha256s": sorted_patch_payloads,
        "metadata_content_identifier_sha256_count": len(metadata_identifiers),
        "metadata_content_identifier_projection_sha256": projection_hash(metadata_identifiers),
        "metadata_content_identifier_sha256s": metadata_identifiers,
        "extraction_boundary": {
            "immutable_git_commit_machine_metadata_only": True,
            "all_lowercase_sha256_json_string_values_quarantined": True,
            "raw_model_response_text_interpreted": False,
            "patch_text_read": False,
            "model_api_calls": 0,
        },
    }


def load_payload_exclusions(
    registry: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, bool]]:
    declaration = registry["payload_exclusion_registry"]
    path = ROOT / declaration["path"]
    value = read_json(path)
    source_commit = value["source_commit"]
    discovered, patch_payloads = discover_payload_sources(registry, source_commit)
    tree_blobs = git_tree_blob_map(source_commit)
    declared_sources = value["sources"]
    source_paths = [source["path"] for source in declared_sources]
    source_checks = [
        source["source_commit_blob_oid"] == tree_blobs.get(source["path"])
        and source["unique_metadata_sha256_count"] == len(discovered.get(source["path"], set()))
        for source in declared_sources
    ]
    declared_metadata = value["metadata_content_identifier_sha256s"]
    projected_metadata = sorted(set().union(*discovered.values()))
    declared_patch_payloads = value["patch_payload_sha256s"]
    projected_patch_payloads = sorted(patch_payloads)
    checks = {
        "canonical_hash_exact": canonical_json_sha256(path) == declaration["canonical_json_sha256"],
        "status_frozen": value.get("status") == "frozen_at_isolation_cutoff",
        "source_projection_exact": (
            source_paths == sorted(discovered)
            and len(source_paths) == value["source_count"] == declaration["source_count"] > 0
            and value["source_path_projection_sha256"] == projection_hash(source_paths)
            and all(source_checks)
        ),
        "patch_payload_projection_exact": (
            declared_patch_payloads == projected_patch_payloads
            and declared_patch_payloads == sorted(set(declared_patch_payloads))
            and all(HEX64.fullmatch(payload) for payload in declared_patch_payloads)
            and len(declared_patch_payloads)
            == value["patch_payload_sha256_count"]
            == declaration["patch_payload_sha256_count"]
            and value["patch_payload_projection_sha256"]
            == declaration["patch_payload_projection_sha256"]
            == projection_hash(declared_patch_payloads)
        ),
        "metadata_content_identifier_projection_exact": (
            declared_metadata == projected_metadata
            and declared_metadata == sorted(set(declared_metadata))
            and all(HEX64.fullmatch(identifier) for identifier in declared_metadata)
            and len(declared_metadata)
            == value["metadata_content_identifier_sha256_count"]
            == declaration["metadata_content_identifier_sha256_count"]
            and value["metadata_content_identifier_projection_sha256"]
            == declaration["metadata_content_identifier_projection_sha256"]
            == projection_hash(declared_metadata)
        ),
        "metadata_only_boundary": (
            value["extraction_boundary"]["immutable_git_commit_machine_metadata_only"] is True
            and value["extraction_boundary"]["all_lowercase_sha256_json_string_values_quarantined"] is True
            and value["extraction_boundary"]["raw_model_response_text_interpreted"] is False
            and value["extraction_boundary"]["patch_text_read"] is False
            and value["extraction_boundary"]["model_api_calls"] == 0
        ),
    }
    return value, checks


def preauthorization_manifest_sha256(manifest: dict[str, Any]) -> str:
    value = copy.deepcopy(manifest)
    value["authorization"] = {
        "data_use_authorized": False,
        "author_signoff_path": None,
        "author_signoff_sha256": None,
    }
    return canonical_value_sha256(value)


def validate_signoff_value(manifest: dict[str, Any], signoff: dict[str, Any]) -> list[str]:
    expected_fields = {
        "signoff_id",
        "study_id",
        "quarantine_registry_canonical_sha256",
        "manifest_pre_authorization_canonical_sha256",
        "signer_id",
        "signed_at_utc",
        "statement",
    }
    violations = []
    if set(signoff) != expected_fields:
        violations.append("author_signoff_fields_not_exact")
    if signoff.get("study_id") != manifest.get("study_id"):
        violations.append("author_signoff_study_mismatch")
    if signoff.get("quarantine_registry_canonical_sha256") != manifest.get(
        "quarantine_registry_canonical_sha256"
    ):
        violations.append("author_signoff_registry_mismatch")
    if signoff.get("manifest_pre_authorization_canonical_sha256") != preauthorization_manifest_sha256(manifest):
        violations.append("author_signoff_manifest_mismatch")
    if signoff.get("statement") != SIGNOFF_STATEMENT:
        violations.append("author_signoff_statement_mismatch")
    study_id = manifest.get("study_id")
    if signoff.get("signoff_id") != f"{study_id}_author_signoff_v0_1":
        violations.append("author_signoff_id_invalid")
    signer_id = signoff.get("signer_id")
    if not isinstance(signer_id, str) or not re.fullmatch(r"[A-Za-z0-9._@-]{2,128}", signer_id):
        violations.append("author_signoff_signer_id_invalid")
    signed_at = signoff.get("signed_at_utc")
    try:
        signed_datetime = datetime.fromisoformat(signed_at.replace("Z", "+00:00"))
        manifest_created = date.fromisoformat(manifest["created_date"])
        if (
            signed_datetime.tzinfo != UTC
            or signed_datetime.astimezone(PROJECT_TIMEZONE).date() < manifest_created
            or signed_datetime > datetime.now(UTC)
        ):
            raise ValueError
    except (AttributeError, KeyError, OverflowError, TypeError, ValueError):
        violations.append("author_signoff_timestamp_invalid")
    return violations


def prior_execution_block_status(entrypoint: str) -> dict[str, Any]:
    """Return guard configuration without ever authorizing the old entrypoint."""
    try:
        registry = read_json(REGISTRY)
        configured = (
            registry.get("status") == "author_directed_active_fail_closed"
            and path_matches_any(
                entrypoint,
                registry["old_execution_termination"]["blocked_entrypoint_globs"],
            )
        )
        return {
            "blocked": True,
            "configured": configured,
            "registry_status": registry.get("status"),
            "entrypoint": entrypoint,
            "reason": "prior research execution was terminated" if configured else "isolation configuration invalid; fail closed",
        }
    except Exception as exc:
        return {
            "blocked": True,
            "configured": False,
            "registry_status": "unreadable",
            "entrypoint": entrypoint,
            "reason": f"isolation registry unavailable; fail closed: {exc}",
        }


def assert_prior_research_execution_blocked(entrypoint: str) -> None:
    status = prior_execution_block_status(entrypoint)
    if not status["configured"]:
        raise PermissionError(status["reason"])
    raise PermissionError(
        f"{entrypoint} is revoked by research_lineage_quarantine_v0_1; "
        "start a separately preregistered study instead"
    )


def recompute_old_p1(denylist: dict[str, Any]) -> dict[str, Any]:
    forbidden = [value.casefold() for value in denylist["forbidden_identifiers_in_dsa_analysis"]]
    forbidden.extend(value.casefold() for value in denylist["forbidden_generator_scripts"])
    forbidden.extend(value.casefold().replace("*", "") for value in denylist["forbidden_input_globs"])
    scripts = sorted(ROOT.glob(denylist["scope"]["analysis_namespace_glob"]))
    violations = []
    for path in scripts:
        content = path.read_text(encoding="utf-8").casefold()
        for token in sorted(set(forbidden)):
            if token and token in content:
                violations.append({"script": display(path), "forbidden_token": token})
    return {
        "recomputed_status": "passed" if not violations else "failed",
        "scanned_script_count": len(scripts),
        "violation_count": len(violations),
        "violations": violations,
        "authority_for_future_research": False,
        "note": "Recomputed from current scripts; the stored historical P1 status is not trusted.",
    }


def load_content_fingerprints(registry: dict[str, Any]) -> tuple[dict[str, Any], dict[str, bool]]:
    declaration = registry["content_fingerprint_registry"]
    path = ROOT / declaration["path"]
    value = read_json(path)
    tracked = value["tracked_head_content"]
    history = value["reachable_git_history_content"]
    worktree = value["cutoff_worktree_content"]
    source_commit_check = subprocess.run(
        ["git", "cat-file", "-e", f"{value['source_commit']}^{{commit}}"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0
    checks = {
        "canonical_hash_exact": canonical_json_sha256(path) == declaration["canonical_json_sha256"],
        "status_frozen": value.get("status") == "frozen_at_isolation_cutoff",
        "source_commit_present": source_commit_check,
        "fingerprint_scope_projection_exact": (
            value.get("fingerprint_scope_projection_sha256")
            == fingerprint_scope_sha256(declaration)
        ),
        "tracked_counts_exact": (
            tracked["matched_path_count"] == declaration["tracked_head_path_count"]
            and tracked["unique_blob_oid_count"] == declaration["tracked_unique_blob_oid_count"]
            and len(tracked["blob_oids"]) == tracked["unique_blob_oid_count"] > 0
            and bool(HEX64.fullmatch(tracked["path_projection_sha256"]))
        ),
        "reachable_history_counts_exact": (
            history["matched_object_path_count"]
            == declaration["reachable_history_matched_object_path_count"]
            and history["unique_blob_oid_count"]
            == declaration["reachable_history_unique_blob_oid_count"]
            and history["unique_raw_sha256_count"]
            == declaration["reachable_history_unique_raw_sha256_count"]
            and len(history["blob_oids"]) == history["unique_blob_oid_count"] > 0
            and len(history["raw_sha256s"]) == history["unique_raw_sha256_count"] > 0
            and history["unique_raw_sha256_count"] == history["unique_blob_oid_count"]
            and bool(HEX64.fullmatch(history["path_projection_sha256"]))
        ),
        "cutoff_worktree_counts_exact": (
            worktree["matched_path_count"] == declaration["cutoff_worktree_matched_path_count"]
            and worktree["regular_file_count"] == declaration["cutoff_worktree_file_count"]
            and worktree["unique_sha256_count"]
            == declaration["cutoff_worktree_unique_sha256_count"]
            and len(worktree["content_sha256s"]) == worktree["unique_sha256_count"] > 0
            and worktree["total_bytes_hashed"] == declaration["cutoff_worktree_bytes_hashed"]
            and worktree["matched_path_count"]
            == worktree["regular_file_count"] + worktree["reparse_or_nonregular_count"]
            and worktree["reparse_or_nonregular_count"]
            == declaration["reparse_or_nonregular_count"]
            == 0
            and worktree["reparse_or_nonregular_paths"] == []
            and bool(HEX64.fullmatch(worktree["path_projection_sha256"]))
            and bool(HEX64.fullmatch(worktree["path_content_projection_sha256"]))
        ),
        "hash_lists_sorted_unique": (
            tracked["blob_oids"] == sorted(set(tracked["blob_oids"]))
            and history["blob_oids"] == sorted(set(history["blob_oids"]))
            and history["raw_sha256s"] == sorted(set(history["raw_sha256s"]))
            and worktree["content_sha256s"] == sorted(set(worktree["content_sha256s"]))
            and tracked["git_object_format"] == "sha1"
            and all(re.fullmatch(r"[0-9a-f]{40}", item) for item in tracked["blob_oids"])
            and all(re.fullmatch(r"[0-9a-f]{40}", item) for item in history["blob_oids"])
            and all(HEX64.fullmatch(item) for item in history["raw_sha256s"])
            and all(HEX64.fullmatch(item) for item in worktree["content_sha256s"])
        ),
        "content_not_interpreted": (
            value["hashing_boundary"]["file_contents_interpreted_or_rendered"] is False
            and value["hashing_boundary"]["raw_output_text_or_json_parsed"] is False
            and value["hashing_boundary"][
                "secret_or_credential_values_interpreted_or_emitted"
            ]
            is False
            and value["hashing_boundary"]["tracked_worktree_modifications_hashed"] is True
            and value["hashing_boundary"]["all_reachable_git_refs_hashed"] is True
            and value["hashing_boundary"]["model_api_calls"] == 0
        ),
    }
    return value, checks


def derive_quarantine(registry: dict[str, Any]) -> dict[str, Any]:
    source_checks: dict[str, bool] = {}
    for source in registry["projection_sources"]:
        path = ROOT / source["path"]
        source_checks[source["path"]] = (
            path.is_file()
            and canonical_json_sha256(path) == source["canonical_json_sha256"]
        )

    legacy = read_json(LEGACY_TASKS)
    development = read_json(DEVELOPMENT_TASKS)
    termination = read_json(V01_TERMINATION)
    ledger = read_json(V2_LEDGER)
    pilot = read_json(PILOT_REVALIDATION)
    postrun = read_json(PILOT_POSTRUN)
    candidate_set = read_json(EVP8_CANDIDATE_SET)
    hardneg_stress = read_json(EVP8_HARDNEG_STRESS)
    source_frame = read_json(DSA_SOURCE_FRAME)
    fingerprints, fingerprint_checks = load_content_fingerprints(registry)
    payload_registry, payload_registry_checks = load_payload_exclusions(registry)

    task_sets = {
        "legacy_p1": {str(value) for value in legacy["excluded_task_ids"]},
        "development_exclusion": {str(value) for value in development["excluded_task_ids"]},
        "terminated_dsa_v0_1": {
            str(value)
            for value in termination["v0_1_termination"]["v0_2_development_exclusion_task_ids"]
        },
        "dsa_v2_materialization": {str(record["task_id"]) for record in ledger["records"]},
        "dsa_v0_3_pilot": {str(pilot["selection"]["task_id"])},
        "evp8_candidate_set": {str(record["task_id"]) for record in candidate_set["records"]},
        "evp8_hardneg_stress": {
            str(record["task_id"]) for record in hardneg_stress["case_records"]
        },
        "dsa_p2_source_frame": {str(record["task_id"]) for record in source_frame["records"]},
    }
    blocked_tasks = set().union(*task_sets.values())
    blocked_projects = {project_from_task_id(task_id) for task_id in blocked_tasks}
    blocked_payloads = set(payload_registry["metadata_content_identifier_sha256s"])

    latest_ledgers = []
    for path in (ROOT / "data/protocols").glob("dsa_v2_p2_terminal_ledger_v0_*.json"):
        match = re.fullmatch(r"dsa_v2_p2_terminal_ledger_v0_(\d+)\.json", path.name)
        if match:
            latest_ledgers.append((int(match.group(1)), path))
    latest_number, latest_path = max(latest_ledgers)

    revocation_checks: dict[str, bool] = {}
    revoked_ids = set()
    for record in registry["old_execution_termination"]["revoked_authorizations"]:
        path = ROOT / record["path"]
        value = read_json(path)
        revoked_ids.add(record["authorization_id"])
        revocation_checks[record["authorization_id"]] = (
            canonical_json_sha256(path) == record["canonical_json_sha256"]
            and value.get("authorization_id") == record["authorization_id"]
        )

    return {
        "source_hash_checks": source_checks,
        "task_source_counts": {name: len(values) for name, values in task_sets.items()},
        "payload_source_count": payload_registry["source_count"],
        "blocked_task_ids": sorted(blocked_tasks, key=str.casefold),
        "blocked_task_count": len(blocked_tasks),
        "blocked_task_projection_sha256": projection_hash(list(blocked_tasks)),
        "blocked_projects": sorted(blocked_projects, key=str.casefold),
        "blocked_project_count": len(blocked_projects),
        "blocked_project_projection_sha256": projection_hash(list(blocked_projects)),
        "blocked_payload_sha256s": sorted(blocked_payloads),
        "blocked_payload_sha256_count": len(blocked_payloads),
        "blocked_payload_projection_sha256": projection_hash(list(blocked_payloads)),
        "revoked_authorization_ids": sorted(revoked_ids),
        "revocation_record_checks": revocation_checks,
        "content_fingerprint_registry": {
            "path": registry["content_fingerprint_registry"]["path"],
            "source_commit": fingerprints["source_commit"],
            "checks": fingerprint_checks,
            "tracked_head_path_count": fingerprints["tracked_head_content"]["matched_path_count"],
            "tracked_unique_blob_oid_count": fingerprints["tracked_head_content"]["unique_blob_oid_count"],
            "reachable_history_unique_blob_oid_count": fingerprints[
                "reachable_git_history_content"
            ]["unique_blob_oid_count"],
            "reachable_history_unique_raw_sha256_count": fingerprints[
                "reachable_git_history_content"
            ]["unique_raw_sha256_count"],
            "cutoff_worktree_file_count": fingerprints["cutoff_worktree_content"][
                "regular_file_count"
            ],
            "cutoff_worktree_unique_sha256_count": fingerprints["cutoff_worktree_content"][
                "unique_sha256_count"
            ],
            "cutoff_worktree_bytes_hashed": fingerprints["cutoff_worktree_content"][
                "total_bytes_hashed"
            ],
            "cutoff_worktree_reparse_or_nonregular_count": fingerprints[
                "cutoff_worktree_content"
            ]["reparse_or_nonregular_count"],
        },
        "payload_exclusion_registry": {
            "path": registry["payload_exclusion_registry"]["path"],
            "source_commit": payload_registry["source_commit"],
            "checks": payload_registry_checks,
            "source_count": payload_registry["source_count"],
            "patch_payload_sha256_count": payload_registry["patch_payload_sha256_count"],
            "patch_payload_projection_sha256": payload_registry[
                "patch_payload_projection_sha256"
            ],
            "metadata_content_identifier_sha256_count": payload_registry[
                "metadata_content_identifier_sha256_count"
            ],
            "metadata_content_identifier_projection_sha256": payload_registry[
                "metadata_content_identifier_projection_sha256"
            ],
        },
        "terminal_boundary": {
            "latest_ledger": display(latest_path),
            "latest_ledger_number": latest_number,
            "attempted_tasks": ledger["attempted_tasks"],
            "qualified_pairs": ledger["qualified_pairs"],
            "next_order": ledger["next_order"],
            "next_task_started": ledger["next_task_started"],
            "model_api_calls": ledger["model_api_calls"],
            "pilot_status": postrun["status"],
            "pilot_valid_model_outputs": postrun["activity"]["valid_model_outputs"],
            "pilot_scientific_boundary": postrun["scientific_boundary"],
        },
    }


def core_isolation_checks(
    registry: dict[str, Any],
    derived: dict[str, Any],
) -> dict[str, bool]:
    expected = registry["expected_projections"]
    return {
        "registry_active_fail_closed": (
            registry.get("status") == "author_directed_active_fail_closed"
        ),
        "projection_source_hashes_exact": (
            set(derived["source_hash_checks"]) == EXPECTED_PROJECTION_SOURCES
            and all(derived["source_hash_checks"].values())
        ),
        "blocked_task_projection_exact": (
            derived["blocked_task_count"] == expected["blocked_task_count"]
            and derived["blocked_task_projection_sha256"]
            == expected["blocked_task_projection_sha256"]
        ),
        "blocked_project_projection_exact": (
            derived["blocked_project_count"] == expected["blocked_project_count"]
            and derived["blocked_project_projection_sha256"]
            == expected["blocked_project_projection_sha256"]
        ),
        "blocked_payload_projection_exact": (
            derived["blocked_payload_sha256_count"]
            == expected["blocked_payload_sha256_count"]
            and derived["blocked_payload_projection_sha256"]
            == expected["blocked_payload_projection_sha256"]
        ),
        "blocked_content_fingerprint_registry_exact": all(
            derived["content_fingerprint_registry"]["checks"].values()
        ),
        "blocked_payload_exclusion_registry_exact": all(
            derived["payload_exclusion_registry"]["checks"].values()
        ),
        "cutoff_source_commits_identical": (
            derived["content_fingerprint_registry"]["source_commit"]
            == derived["payload_exclusion_registry"]["source_commit"]
        ),
        "revoked_authorization_records_exact": (
            set(derived["revocation_record_checks"])
            == EXPECTED_REVOKED_AUTHORIZATION_IDS
            and all(derived["revocation_record_checks"].values())
        ),
    }


def git_object_types(oids: list[str]) -> dict[str, str]:
    if not oids:
        return {}
    completed = subprocess.run(
        ["git", "cat-file", "--batch-check=%(objectname) %(objecttype)"],
        cwd=ROOT,
        input="\n".join(oids) + "\n",
        text=True,
        encoding="utf-8",
        errors="strict",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    result = {}
    for line in completed.stdout.splitlines():
        oid, kind = line.split()
        result[oid] = kind
    return result


def git_blob_content_sha256s(oids: list[str]) -> list[str]:
    if not oids:
        return []
    process = subprocess.Popen(
        ["git", "cat-file", "--batch"],
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.stdin is None or process.stdout is None or process.stderr is None:
        process.kill()
        raise RuntimeError("failed to open git cat-file pipes")
    digests = []
    try:
        for expected_oid in oids:
            process.stdin.write(expected_oid.encode("ascii") + b"\n")
            process.stdin.flush()
            header = process.stdout.readline().decode("ascii").strip()
            oid, kind, raw_size = header.split()
            if oid != expected_oid or kind != "blob":
                raise ValueError(f"unexpected git cat-file header: {header}")
            remaining = int(raw_size)
            digest = hashlib.sha256()
            while remaining:
                chunk = process.stdout.read(min(1024 * 1024, remaining))
                if not chunk:
                    raise EOFError(f"truncated git blob: {expected_oid}")
                digest.update(chunk)
                remaining -= len(chunk)
            if process.stdout.read(1) != b"\n":
                raise ValueError(f"missing git cat-file separator: {expected_oid}")
            digests.append(digest.hexdigest())
        process.stdin.close()
        stderr = process.stderr.read().decode("utf-8", errors="replace")
        return_code = process.wait()
        if return_code != 0:
            raise subprocess.CalledProcessError(
                return_code,
                process.args,
                stderr=stderr,
            )
    except Exception:
        process.kill()
        process.wait()
        raise
    return digests


def reachable_history_fingerprints(declaration: dict[str, Any]) -> dict[str, Any]:
    output = subprocess.check_output(
        ["git", "rev-list", "--objects", "--all"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )
    candidates = []
    for line in output.splitlines():
        parts = line.split(" ", 1)
        if len(parts) != 2:
            continue
        oid, path = parts
        if path_is_in_fingerprint_scope(path, declaration):
            candidates.append((oid, path))
    object_types = git_object_types(sorted({oid for oid, _path in candidates}))
    blob_records = [(oid, path) for oid, path in candidates if object_types.get(oid) == "blob"]
    blob_oids = sorted({oid for oid, _path in blob_records})
    raw_sha256s = sorted(set(git_blob_content_sha256s(blob_oids)))
    return {
        "matched_object_path_count": len(blob_records),
        "path_projection_sha256": projection_hash([path for _oid, path in blob_records]),
        "unique_blob_oid_count": len(blob_oids),
        "blob_oids": blob_oids,
        "unique_raw_sha256_count": len(raw_sha256s),
        "raw_sha256s": raw_sha256s,
    }


def discover_worktree_scope(declaration: dict[str, Any]) -> list[str]:
    literal_files = {
        pattern
        for pattern in declaration["included_path_globs"]
        if not any(character in pattern for character in "*?[")
        and (ROOT / pattern).is_file()
        and path_is_in_fingerprint_scope(pattern, declaration)
    }
    roots = sorted(
        {
            pattern.split("/", 1)[0]
            for pattern in declaration["included_path_globs"]
            if (ROOT / pattern.split("/", 1)[0]).is_dir()
        }
    )
    discovered = subprocess.check_output(
        ["rg", "--files", "-0", "-uu", *roots], cwd=ROOT
    ).decode("utf-8", errors="strict").split("\0")
    return sorted(
        literal_files
        | {
            value.replace("\\", "/")
            for value in discovered
            if value and path_is_in_fingerprint_scope(value.replace("\\", "/"), declaration)
        },
        key=str.casefold,
    )


def cutoff_worktree_fingerprints(declaration: dict[str, Any]) -> dict[str, Any]:
    paths = discover_worktree_scope(declaration)

    def fingerprint(value: str) -> tuple[str, int] | None:
        path = ROOT / value
        if not is_regular_non_reparse_file(path):
            return None
        before = path.stat()
        digest = sha256_file(path)
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise RuntimeError(f"file changed while hashing isolation cutoff: {value}")
        return digest, after.st_size

    records = []
    reparse_paths = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        results = executor.map(fingerprint, paths)
        for value, result in zip(paths, results, strict=True):
            if result is None:
                reparse_paths.append(value)
            else:
                digest, size = result
                records.append((value, digest, size))
    content_hashes = sorted({digest for _path, digest, _size in records})
    return {
        "matched_path_count": len(paths),
        "regular_file_count": len(records),
        "reparse_or_nonregular_count": len(reparse_paths),
        "reparse_or_nonregular_paths": reparse_paths,
        "path_projection_sha256": projection_hash(paths),
        "path_content_projection_sha256": projection_hash(
            [f"{path}\0{digest}" for path, digest, _size in records]
        ),
        "total_bytes_hashed": sum(size for _path, _digest, size in records),
        "unique_sha256_count": len(content_hashes),
        "content_sha256s": content_hashes,
    }


def freeze_content_fingerprints(registry: dict[str, Any]) -> dict[str, Any]:
    declaration = registry["content_fingerprint_registry"]
    source_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, encoding="utf-8"
    ).strip()
    tree_blobs = git_tree_blob_map(source_commit)
    tracked_records = sorted(
        (path, oid)
        for path, oid in tree_blobs.items()
        if path_is_in_fingerprint_scope(path, declaration)
    )
    tracked_oids = sorted({oid for _path, oid in tracked_records})
    history = reachable_history_fingerprints(declaration)
    worktree = cutoff_worktree_fingerprints(declaration)
    return {
        "registry_id": "research_lineage_blocked_content_fingerprints_v0_1",
        "created_date": "2026-07-18",
        "status": "frozen_at_isolation_cutoff",
        "source_commit": source_commit,
        "fingerprint_scope_projection_sha256": fingerprint_scope_sha256(declaration),
        "tracked_head_content": {
            "matched_path_count": len(tracked_records),
            "path_projection_sha256": projection_hash([path for path, _oid in tracked_records]),
            "git_object_format": subprocess.check_output(
                ["git", "rev-parse", "--show-object-format"],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
            ).strip(),
            "unique_blob_oid_count": len(tracked_oids),
            "blob_oids": tracked_oids,
        },
        "reachable_git_history_content": history,
        "cutoff_worktree_content": worktree,
        "hashing_boundary": {
            "file_contents_interpreted_or_rendered": False,
            "raw_output_bytes_hashed_for_quarantine_only": True,
            "raw_output_text_or_json_parsed": False,
            "secret_or_credential_values_interpreted_or_emitted": False,
            "tracked_worktree_modifications_hashed": True,
            "all_reachable_git_refs_hashed": True,
            "model_api_calls": 0,
        },
    }


def validate_not_started_manifest(manifest: dict[str, Any], registry: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    if set(manifest) != MANIFEST_KEYS:
        violations.append("manifest_fields_not_exact")
    if manifest.get("status") != "not_started":
        violations.append("status_not_not_started")
    if manifest.get("manifest_id") != "future_research_input_manifest_v0_1":
        violations.append("not_started_manifest_id_invalid")
    if not manifest_created_date_is_valid(manifest.get("created_date"), registry):
        violations.append("manifest_created_date_outside_isolation_window")
    if manifest.get("study_id") is not None or manifest.get("namespace") is not None:
        violations.append("study_or_namespace_already_set")
    if manifest.get("selection_inputs") != [] or manifest.get("records") != []:
        violations.append("not_started_manifest_is_not_empty")
    if manifest.get("quarantine_registry_canonical_sha256") != canonical_json_sha256(REGISTRY):
        violations.append("quarantine_registry_hash_mismatch")
    if manifest.get("boundary") != registry["future_study_contract"][
        "not_started_boundary_statement"
    ]:
        violations.append("not_started_boundary_statement_invalid")
    authorization = manifest.get("authorization")
    if authorization != {
        "data_use_authorized": False,
        "author_signoff_path": None,
        "author_signoff_sha256": None,
    }:
        violations.append("data_use_must_be_unauthorized")
    return violations


def validate_activation_manifest(
    manifest: dict[str, Any],
    registry: dict[str, Any],
    derived: dict[str, Any],
    *,
    check_files: bool,
) -> list[str]:
    violations: list[str] = []
    if set(manifest) != MANIFEST_KEYS:
        violations.append("manifest_fields_not_exact")
    study_id = manifest.get("study_id")
    namespace = manifest.get("namespace")
    frozen_studies = {value.casefold() for value in registry["frozen_study_ids"]}
    if manifest.get("status") != "frozen_preuse":
        violations.append("status_not_frozen_preuse")
    if not isinstance(study_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{2,63}", study_id):
        violations.append("invalid_study_id")
    elif study_id.casefold() in frozen_studies:
        violations.append("study_id_is_frozen_lineage")
    expected_namespace = f"data/future_studies/{study_id}" if isinstance(study_id, str) else None
    if namespace != expected_namespace:
        violations.append("namespace_not_isolated")
    if manifest.get("manifest_id") != f"future_research_input_manifest_{study_id}":
        violations.append("activation_manifest_id_invalid")
    if not manifest_created_date_is_valid(manifest.get("created_date"), registry):
        violations.append("manifest_created_date_outside_isolation_window")
    if manifest.get("boundary") != registry["future_study_contract"][
        "activation_boundary_statement"
    ]:
        violations.append("activation_boundary_statement_invalid")
    if manifest.get("quarantine_registry_canonical_sha256") != canonical_json_sha256(REGISTRY):
        violations.append("quarantine_registry_hash_mismatch")
    for check_name, passed in core_isolation_checks(registry, derived).items():
        if not passed:
            violations.append(f"isolation_integrity_{check_name}_failed")
    fingerprints, fingerprint_checks = load_content_fingerprints(registry)
    if not all(fingerprint_checks.values()):
        violations.append("blocked_content_fingerprint_registry_invalid")
    blocked_local_hashes = set(fingerprints["cutoff_worktree_content"]["content_sha256s"])
    blocked_history_hashes = set(
        fingerprints["reachable_git_history_content"]["raw_sha256s"]
    )
    blocked_tracked_oids = set(
        fingerprints["reachable_git_history_content"]["blob_oids"]
    )
    blocked_payloads = set(derived["blocked_payload_sha256s"])

    def validate_new_file(path_value: str, declared_sha: str, label: str) -> None:
        if declared_sha in blocked_local_hashes:
            violations.append(f"{label}_matches_quarantined_local_content")
        if declared_sha in blocked_history_hashes:
            violations.append(f"{label}_matches_quarantined_git_history_content")
        if declared_sha in blocked_payloads:
            violations.append(f"{label}_matches_quarantined_metadata_content")
        if not check_files:
            return
        path = ROOT / path_value
        if not is_regular_non_reparse_file(path):
            violations.append(f"{label}_not_regular_or_is_reparse")
            return
        if path.stat().st_nlink != 1:
            violations.append(f"{label}_hardlink_not_allowed")
            return
        namespace_path = ROOT / expected_namespace if expected_namespace else None
        if namespace_path is None or not path_chain_is_non_reparse(path, ROOT):
            violations.append(f"{label}_path_chain_is_reparse_or_missing")
            return
        try:
            repo_root = ROOT.resolve(strict=True)
            namespace_root = namespace_path.resolve(strict=True)
            resolved = path.resolve(strict=True)
            namespace_root.relative_to(repo_root)
            resolved.relative_to(namespace_root)
        except (OSError, ValueError):
            violations.append(f"{label}_resolved_outside_new_namespace")
            return
        if sha256_file(path) != declared_sha:
            violations.append(f"{label}_file_or_hash_invalid")
        try:
            blob_oid = git_blob_oid(path_value)
        except (OSError, subprocess.SubprocessError, UnicodeError):
            violations.append(f"{label}_git_blob_hash_failed")
        else:
            if blob_oid in blocked_tracked_oids:
                violations.append(f"{label}_matches_quarantined_tracked_content")

    authorization = manifest.get("authorization")
    if not isinstance(authorization, dict) or set(authorization) != {
        "data_use_authorized",
        "author_signoff_path",
        "author_signoff_sha256",
    }:
        violations.append("authorization_fields_not_exact")
    else:
        if authorization.get("data_use_authorized") is not True:
            violations.append("data_use_not_authorized")
        signoff_path = normalized_repo_path(authorization.get("author_signoff_path"))
        signoff_sha = authorization.get("author_signoff_sha256")
        if signoff_path is None or expected_namespace is None or not signoff_path.startswith(expected_namespace + "/"):
            violations.append("author_signoff_not_in_new_namespace")
        if not isinstance(signoff_sha, str) or not HEX64.fullmatch(signoff_sha):
            violations.append("invalid_author_signoff_hash")
        elif check_files and signoff_path is not None:
            path = ROOT / signoff_path
            if (
                not is_regular_non_reparse_file(path)
                or not path_chain_is_non_reparse(path, ROOT)
                or path.stat().st_nlink != 1
                or sha256_file(path) != signoff_sha
            ):
                violations.append("author_signoff_file_or_hash_invalid")
            else:
                try:
                    signoff = read_json(path)
                except (OSError, ValueError, json.JSONDecodeError):
                    violations.append("author_signoff_not_valid_json")
                else:
                    violations.extend(validate_signoff_value(manifest, signoff))

    selection_inputs = manifest.get("selection_inputs")
    if not isinstance(selection_inputs, list) or not selection_inputs:
        violations.append("selection_inputs_missing_or_empty")
    else:
        for index, item in enumerate(selection_inputs):
            if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
                violations.append(f"selection_input_{index}_fields_not_exact")
                continue
            path_value = normalized_repo_path(item.get("path"))
            if path_value is None or expected_namespace is None or not path_value.startswith(expected_namespace + "/"):
                violations.append(f"selection_input_{index}_outside_new_namespace")
            if path_value and path_matches_any(path_value, registry["blocked_path_globs"]):
                violations.append(f"selection_input_{index}_matches_blocked_path")
            sha = item.get("sha256")
            if not isinstance(sha, str) or not HEX64.fullmatch(sha):
                violations.append(f"selection_input_{index}_invalid_hash")
            elif path_value is not None:
                validate_new_file(path_value, sha, f"selection_input_{index}")

    records = manifest.get("records")
    if not isinstance(records, list) or not records:
        violations.append("records_missing_or_empty")
        records = []
    seen_samples: set[str] = set()
    blocked_tasks = {value.casefold() for value in derived["blocked_task_ids"]}
    blocked_projects = {value.casefold() for value in derived["blocked_projects"]}
    for index, record in enumerate(records):
        prefix = f"record_{index}"
        if not isinstance(record, dict) or set(record) != RECORD_KEYS:
            violations.append(f"{prefix}_fields_not_exact")
            continue
        sample_id = record.get("sample_id")
        if not is_canonical_identifier(sample_id) or sample_id in seen_samples:
            violations.append(f"{prefix}_sample_id_invalid_or_duplicate")
        else:
            seen_samples.add(sample_id)
        if record.get("split") not in ALLOWED_SPLITS:
            violations.append(f"{prefix}_split_invalid")
        source_dataset = record.get("source_dataset")
        if not is_canonical_identifier(source_dataset):
            violations.append(f"{prefix}_source_dataset_invalid")
        if (
            isinstance(source_dataset, str)
            and source_dataset.strip().casefold() in frozen_studies
        ):
            violations.append(f"{prefix}_source_dataset_is_quarantined_study")
        source_uri = record.get("upstream_source_uri")
        parsed_uri = urllib.parse.urlparse(source_uri) if isinstance(source_uri, str) else None
        if (
            not is_canonical_identifier(source_uri)
            or parsed_uri is None
            or parsed_uri.scheme != "https"
            or not parsed_uri.netloc
            or parsed_uri.username is not None
            or parsed_uri.password is not None
        ):
            violations.append(f"{prefix}_upstream_source_uri_invalid")
        for field in ("upstream_release_id", "upstream_item_id"):
            value = record.get(field)
            if not is_canonical_identifier(value):
                violations.append(f"{prefix}_{field}_invalid")
        upstream_payload = record.get("upstream_payload_sha256")
        if not isinstance(upstream_payload, str) or not HEX64.fullmatch(upstream_payload):
            violations.append(f"{prefix}_upstream_payload_hash_invalid")
        elif (
            upstream_payload in blocked_local_hashes
            or upstream_payload in blocked_history_hashes
            or upstream_payload in blocked_payloads
        ):
            violations.append(f"{prefix}_upstream_payload_is_quarantined")
        project = record.get("project")
        if not is_canonical_identifier(project):
            violations.append(f"{prefix}_project_invalid")
        if isinstance(project, str) and project.strip().casefold() in blocked_projects:
            violations.append(f"{prefix}_blocked_project")
        task_id = record.get("task_id")
        if not is_canonical_identifier(task_id):
            violations.append(f"{prefix}_task_id_invalid")
        if isinstance(task_id, str) and task_id.strip().casefold() in blocked_tasks:
            violations.append(f"{prefix}_blocked_task")

        artifact_paths = record.get("artifact_paths")
        artifact_hashes = record.get("artifact_sha256s")
        if not isinstance(artifact_paths, list) or not artifact_paths:
            violations.append(f"{prefix}_artifact_paths_missing_or_empty")
            artifact_paths = []
        if not isinstance(artifact_hashes, dict) or set(artifact_hashes) != set(artifact_paths):
            violations.append(f"{prefix}_artifact_hash_mapping_mismatch")
            artifact_hashes = {}
        for path_index, raw_path in enumerate(artifact_paths):
            path_value = normalized_repo_path(raw_path)
            if path_value is None or expected_namespace is None or not path_value.startswith(expected_namespace + "/"):
                violations.append(f"{prefix}_artifact_{path_index}_outside_new_namespace")
                continue
            if path_matches_any(path_value, registry["blocked_path_globs"]):
                violations.append(f"{prefix}_artifact_{path_index}_matches_blocked_path")
            sha = artifact_hashes.get(raw_path)
            if not isinstance(sha, str) or not HEX64.fullmatch(sha):
                violations.append(f"{prefix}_artifact_{path_index}_invalid_hash")
            else:
                validate_new_file(path_value, sha, f"{prefix}_artifact_{path_index}")

        payloads = record.get("source_payload_sha256s")
        if not isinstance(payloads, list) or not payloads:
            violations.append(f"{prefix}_payload_hashes_missing_or_empty")
        else:
            for payload in payloads:
                if not isinstance(payload, str) or not HEX64.fullmatch(payload):
                    violations.append(f"{prefix}_payload_hash_invalid")
                elif (
                    payload in blocked_payloads
                    or payload in blocked_local_hashes
                    or payload in blocked_history_hashes
                ):
                    violations.append(f"{prefix}_blocked_payload")
            if isinstance(upstream_payload, str) and upstream_payload not in payloads:
                violations.append(f"{prefix}_upstream_payload_not_declared_in_payload_hashes")
        origins = record.get("origin_study_ids")
        if not isinstance(origins, list) or not origins:
            violations.append(f"{prefix}_origin_studies_invalid")
        elif any(
            not is_canonical_identifier(value)
            or value.strip().casefold() in frozen_studies
            for value in origins
        ):
            violations.append(f"{prefix}_blocked_or_invalid_origin_study")
        elif isinstance(source_dataset, str) and source_dataset not in origins:
            violations.append(f"{prefix}_source_dataset_missing_from_origin_studies")
    return sorted(set(violations))


def self_tests(registry: dict[str, Any], derived: dict[str, Any]) -> dict[str, bool]:
    registry_sha = canonical_json_sha256(REGISTRY)
    study_id = "clean_new_study"
    namespace = f"data/future_studies/{study_id}"
    artifact = f"{namespace}/inputs/sample.json"
    clean_selection_hash = hashlib.sha256(b"clean-independent-selection-v0-1").hexdigest()
    clean_artifact_hash = hashlib.sha256(b"clean-independent-artifact-v0-1").hexdigest()
    clean_payload_hash = hashlib.sha256(b"clean-independent-payload-v0-1").hexdigest()
    base = {
        "manifest_id": f"future_research_input_manifest_{study_id}",
        "created_date": "2026-07-18",
        "status": "frozen_preuse",
        "study_id": study_id,
        "quarantine_registry_canonical_sha256": registry_sha,
        "namespace": namespace,
        "selection_inputs": [
            {"path": f"{namespace}/selection.json", "sha256": clean_selection_hash}
        ],
        "records": [
            {
                "sample_id": "new_sample_001",
                "split": "train",
                "source_dataset": "independent_primary_source",
                "upstream_source_uri": "https://example.org/independent-dataset",
                "upstream_release_id": "release-1",
                "upstream_item_id": "item-001",
                "upstream_payload_sha256": clean_payload_hash,
                "project": "new_project",
                "task_id": "new_task_001",
                "artifact_paths": [artifact],
                "artifact_sha256s": {artifact: clean_artifact_hash},
                "source_payload_sha256s": [clean_payload_hash],
                "origin_study_ids": ["independent_primary_source"],
            }
        ],
        "authorization": {
            "data_use_authorized": True,
            "author_signoff_path": f"{namespace}/author_signoff.json",
            "author_signoff_sha256": "4" * 64,
        },
        "boundary": registry["future_study_contract"]["activation_boundary_statement"],
    }

    def violations_after(change: Any) -> list[str]:
        fixture = copy.deepcopy(base)
        change(fixture)
        return validate_activation_manifest(fixture, registry, derived, check_files=False)

    def rejected_with(change: Any, expected_violation: str) -> bool:
        return expected_violation in violations_after(change)

    def set_blocked_payload(value: dict[str, Any]) -> None:
        payload = derived["blocked_payload_sha256s"][0]
        value["records"][0].update(
            {
                "upstream_payload_sha256": payload,
                "source_payload_sha256s": [payload],
            }
        )

    def set_frozen_study_id(value: dict[str, Any]) -> None:
        frozen_study = "legacy_evp8"
        old_namespace = value["namespace"]
        new_namespace = f"data/future_studies/{frozen_study}"
        value.update(
            {
                "manifest_id": f"future_research_input_manifest_{frozen_study}",
                "study_id": frozen_study,
                "namespace": new_namespace,
            }
        )
        value["selection_inputs"][0]["path"] = value["selection_inputs"][0][
            "path"
        ].replace(old_namespace, new_namespace, 1)
        old_artifact = value["records"][0]["artifact_paths"][0]
        new_artifact = old_artifact.replace(old_namespace, new_namespace, 1)
        value["records"][0]["artifact_paths"] = [new_artifact]
        value["records"][0]["artifact_sha256s"] = {
            new_artifact: clean_artifact_hash
        }
        value["authorization"]["author_signoff_path"] = value["authorization"][
            "author_signoff_path"
        ].replace(old_namespace, new_namespace, 1)

    signoff = {
        "signoff_id": f"{study_id}_author_signoff_v0_1",
        "study_id": study_id,
        "quarantine_registry_canonical_sha256": registry_sha,
        "manifest_pre_authorization_canonical_sha256": preauthorization_manifest_sha256(base),
        "signer_id": "fixture_author",
        "signed_at_utc": datetime.now(UTC).isoformat(timespec="seconds").replace(
            "+00:00", "Z"
        ),
        "statement": SIGNOFF_STATEMENT,
    }
    bad_signoff = copy.deepcopy(signoff)
    bad_signoff["study_id"] = "wrong_study"
    future_signoff = copy.deepcopy(signoff)
    future_signoff["signed_at_utc"] = "9999-12-31T23:59:59Z"
    pre_manifest_signoff = copy.deepcopy(signoff)
    pre_manifest_signoff["signed_at_utc"] = "2000-01-01T00:00:00Z"
    fingerprints, _ = load_content_fingerprints(registry)
    blocked_local_hash = fingerprints["cutoff_worktree_content"]["content_sha256s"][0]
    shrunk_projection = copy.deepcopy(derived)
    shrunk_projection["blocked_task_count"] -= 1
    invalid_payload_registry = copy.deepcopy(derived)
    invalid_payload_registry["payload_exclusion_registry"]["checks"][
        "canonical_hash_exact"
    ] = False

    return {
        "clean_independent_fixture_accepted": not validate_activation_manifest(
            base, registry, derived, check_files=False
        ),
        "empty_activation_manifest_rejected": rejected_with(
            lambda value: value.update({"records": []}),
            "records_missing_or_empty",
        ),
        "blocked_task_rejected": rejected_with(
            lambda value: value["records"][0].update(
                {"task_id": derived["blocked_task_ids"][0]}
            ),
            "record_0_blocked_task",
        ),
        "blocked_task_case_variant_rejected": rejected_with(
            lambda value: value["records"][0].update(
                {"task_id": derived["blocked_task_ids"][0].swapcase()}
            ),
            "record_0_blocked_task",
        ),
        "blocked_task_whitespace_variant_rejected": rejected_with(
            lambda value: value["records"][0].update(
                {"task_id": derived["blocked_task_ids"][0] + " "}
            ),
            "record_0_task_id_invalid",
        ),
        "blocked_project_rejected": rejected_with(
            lambda value: value["records"][0].update(
                {"project": derived["blocked_projects"][0]}
            ),
            "record_0_blocked_project",
        ),
        "blocked_project_case_variant_rejected": rejected_with(
            lambda value: value["records"][0].update(
                {"project": derived["blocked_projects"][0].swapcase()}
            ),
            "record_0_blocked_project",
        ),
        "blocked_project_whitespace_variant_rejected": rejected_with(
            lambda value: value["records"][0].update(
                {"project": derived["blocked_projects"][0] + " "}
            ),
            "record_0_project_invalid",
        ),
        "blocked_payload_rejected": rejected_with(
            set_blocked_payload,
            "record_0_blocked_payload",
        ),
        "copied_local_content_hash_rejected": rejected_with(
            lambda value: value["records"][0].update(
                {
                    "artifact_sha256s": {artifact: blocked_local_hash},
                }
            ),
            "record_0_artifact_0_matches_quarantined_local_content",
        ),
        "quarantined_source_dataset_rejected": rejected_with(
            lambda value: value["records"][0].update(
                {
                    "source_dataset": registry["frozen_study_ids"][0],
                    "origin_study_ids": [registry["frozen_study_ids"][0]],
                }
            ),
            "record_0_source_dataset_is_quarantined_study",
        ),
        "quarantined_source_dataset_whitespace_rejected": rejected_with(
            lambda value: value["records"][0].update(
                {
                    "source_dataset": "legacy_evp8 ",
                    "origin_study_ids": ["legacy_evp8 "],
                }
            ),
            "record_0_source_dataset_invalid",
        ),
        "blocked_origin_study_rejected": rejected_with(
            lambda value: value["records"][0].update(
                {"origin_study_ids": [registry["frozen_study_ids"][0]]}
            ),
            "record_0_blocked_or_invalid_origin_study",
        ),
        "blocked_path_matcher_detects_old_path": path_matches_any(
            "data/protocols/dsa_p3_output_schema_v0_1.json",
            registry["blocked_path_globs"],
        ),
        "frozen_study_id_rejected": rejected_with(
            set_frozen_study_id,
            "study_id_is_frozen_lineage",
        ),
        "pre_isolation_manifest_date_rejected": rejected_with(
            lambda value: value.update({"created_date": "2026-07-17"}),
            "manifest_created_date_outside_isolation_window",
        ),
        "future_manifest_date_rejected": rejected_with(
            lambda value: value.update({"created_date": "9999-12-31"}),
            "manifest_created_date_outside_isolation_window",
        ),
        "core_projection_shrink_rejected": (
            "isolation_integrity_blocked_task_projection_exact_failed"
            in validate_activation_manifest(
                base,
                registry,
                shrunk_projection,
                check_files=False,
            )
        ),
        "payload_registry_tamper_rejected": (
            "isolation_integrity_blocked_payload_exclusion_registry_exact_failed"
            in validate_activation_manifest(
                base,
                registry,
                invalid_payload_registry,
                check_files=False,
            )
        ),
        "bound_signoff_fixture_accepted": not validate_signoff_value(base, signoff),
        "wrong_study_signoff_rejected": (
            "author_signoff_study_mismatch" in validate_signoff_value(base, bad_signoff)
        ),
        "future_signoff_timestamp_rejected": (
            "author_signoff_timestamp_invalid"
            in validate_signoff_value(base, future_signoff)
        ),
        "pre_manifest_signoff_timestamp_rejected": (
            "author_signoff_timestamp_invalid"
            in validate_signoff_value(base, pre_manifest_signoff)
        ),
    }


def guard_checks(registry: dict[str, Any]) -> dict[str, Any]:
    globs = registry["old_execution_termination"]["blocked_entrypoint_globs"]
    paths = sorted({path for pattern in globs for path in ROOT.glob(pattern)})
    violations = []
    guarded_files = []
    for path in paths:
        relative = display(path)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        guard_index = None
        for index, node in enumerate(tree.body):
            if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call):
                continue
            call = node.value
            if (
                isinstance(call.func, ast.Name)
                and call.func.id == "assert_prior_research_execution_blocked"
                and len(call.args) == 1
                and isinstance(call.args[0], ast.Constant)
                and call.args[0].value == relative
            ):
                guard_index = index
                break
        if guard_index is None:
            violations.append({"path": relative, "reason": "missing_exact_top_level_guard"})
            continue
        allowed_before = True
        for node in tree.body[:guard_index]:
            is_docstring = isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)
            is_future = isinstance(node, ast.ImportFrom) and node.module == "__future__"
            is_guard_import = (
                isinstance(node, ast.ImportFrom)
                and node.module in GUARD_IMPORT_MODULES
                and {alias.name for alias in node.names} == {"assert_prior_research_execution_blocked"}
            )
            if not (is_docstring or is_future or is_guard_import):
                allowed_before = False
                break
        if not allowed_before:
            violations.append({"path": relative, "reason": "executable_code_or_unsafe_import_before_guard"})
            continue
        guarded_files.append(relative)
    expected_count = registry["old_execution_termination"]["expected_blocked_entrypoint_count"]
    expected_projection = registry["old_execution_termination"][
        "blocked_entrypoint_path_projection_sha256"
    ]
    guarded_projection = projection_hash(guarded_files)
    return {
        "entrypoint_globs": globs,
        "discovered_entrypoint_count": len(paths),
        "expected_entrypoint_count": expected_count,
        "guarded_entrypoint_count": len(guarded_files),
        "guarded_files": guarded_files,
        "guarded_entrypoint_path_projection_sha256": guarded_projection,
        "violations": violations,
        "exact_nonempty_projection": (
            len(paths) == expected_count > 0 and guarded_projection == expected_projection
        ),
        "all_entrypoints_guarded_before_other_code": len(guarded_files) == len(paths) and not violations,
    }


def build_audit() -> tuple[dict[str, Any], str]:
    registry = read_json(REGISTRY)
    derived = derive_quarantine(registry)
    manifest = read_json(FUTURE_MANIFEST)
    manifest_violations = validate_not_started_manifest(manifest, registry)
    tests = self_tests(registry, derived)
    guards = guard_checks(registry)
    terminal = derived["terminal_boundary"]
    checks = core_isolation_checks(registry, derived)
    checks.update({
        "old_cursor_frozen_before_order63": (
            terminal["latest_ledger_number"] == 62
            and terminal["attempted_tasks"] == 62
            and terminal["qualified_pairs"] == 0
            and terminal["next_order"] == 63
            and terminal["next_task_started"] is False
            and terminal["model_api_calls"] == 0
        ),
        "old_pilot_complete_development_only": (
            terminal["pilot_status"] == "passed_complete_development_only"
            and terminal["pilot_valid_model_outputs"] == 72
            and "development-only" in terminal["pilot_scientific_boundary"]
        ),
        "old_execution_entrypoints_fail_closed": (
            guards["exact_nonempty_projection"]
            and guards["all_entrypoints_guarded_before_other_code"]
        ),
        "future_manifest_empty_and_unauthorized": not manifest_violations,
        "adversarial_manifest_self_tests_pass": all(tests.values()),
    })
    old_p1 = recompute_old_p1(read_json(LEGACY_DENYLIST))
    passed = all(checks.values())
    audit = {
        "audit_id": "research_lineage_isolation_audit_v0_1",
        "audit_date": "2026-07-18",
        "status": "passed_armed_no_new_study" if passed else "failed",
        "gate_state": {
            "prior_research_execution_authorized": False,
            "new_study_data_use_authorized": False,
            "model_training_authorized": False,
            "confirmatory_evaluation_authorized": False,
            "api_execution_authorized": False,
        },
        "checks": checks,
        "derived_quarantine": derived,
        "guard_checks": guards,
        "future_manifest": {
            "path": display(FUTURE_MANIFEST),
            "status": manifest.get("status"),
            "record_count": len(manifest.get("records", [])),
            "violations": manifest_violations,
        },
        "adversarial_self_tests": tests,
        "superseded_legacy_p1_recomputation": old_p1,
        "execution_boundary": {
            "api_credentials_loaded_for_execution": False,
            "model_api_calls": 0,
            "containers_started": 0,
            "in_scope_file_bytes_read_for_hashing": True,
            "credential_values_interpreted_or_emitted": False,
            "historical_output_bytes_hashed_during_one_time_freeze": True,
            "raw_model_output_text_or_json_parsed": False,
            "prompt_text_read": False,
            "patch_text_read": False,
            "historical_files_moved_or_deleted": False,
        },
        "conclusion": (
            "Prior-study artifacts remain available only for provenance, failure analysis, contamination audit, "
            "and exclusion. No future-study data use is authorized until a nonempty independently sourced "
            "manifest passes this gate before use."
        ),
    }
    return audit, render_markdown(audit, registry)


def render_markdown(audit: dict[str, Any], registry: dict[str, Any]) -> str:
    derived = audit["derived_quarantine"]
    old_p1 = audit["superseded_legacy_p1_recomputation"]
    lines = [
        "# 既有研究谱系隔离与未来研究 Gate v0.1",
        "",
        "日期：2026-07-18",
        f"状态：{audit['status'].upper()}",
        "",
        "## 结论",
        "",
        "历史数据和结果没有被删除或搬移；它们被限制为 provenance、失败复盘、污染审计和",
        "排除用途。旧 V2-P2 cursor、order63、continuous authorization、pilot standing",
        "authorization、归档 v0.2 及 v0.3 execution authorization 均已撤销，并在旧研究",
        "执行入口 fail closed。当前未来研究",
        "manifest 为空，因此训练、验证、确认性测试、模型 API 和论文效果结论均未获授权。",
        "",
        "## 隔离投影",
        "",
        f"- 硬排除任务：{derived['blocked_task_count']} 个。",
        f"- 默认阻断项目：{derived['blocked_project_count']} 个；若未来需要项目复用，必须在接触新数据前另行预注册并版本化本规则。",
        f"- 硬排除旧元数据内容标识 SHA-256：{derived['blocked_payload_sha256_count']} 个；其中精确 patch payload SHA-256 为 "
        f"{derived['payload_exclusion_registry']['patch_payload_sha256_count']} 个。",
        f"- cutoff HEAD tracked 内容：{derived['content_fingerprint_registry']['tracked_head_path_count']} 个路径、"
        f"{derived['content_fingerprint_registry']['tracked_unique_blob_oid_count']} 个唯一 blob。",
        f"- cutoff 工作树内容指纹：{derived['content_fingerprint_registry']['cutoff_worktree_file_count']} 个文件，"
        f"{derived['content_fingerprint_registry']['cutoff_worktree_unique_sha256_count']} 个唯一 SHA-256，"
        f"{derived['content_fingerprint_registry']['cutoff_worktree_bytes_hashed']} bytes，"
        f"reparse/nonregular={derived['content_fingerprint_registry']['cutoff_worktree_reparse_or_nonregular_count']}；只哈希、不解析内容。",
        f"- 全部 Git refs 可达历史 blob 指纹："
        f"{derived['content_fingerprint_registry']['reachable_history_unique_blob_oid_count']} 个 blob、"
        f"{derived['content_fingerprint_registry']['reachable_history_unique_raw_sha256_count']} 个 raw SHA-256。",
        f"- 冻结旧研究谱系：{len(registry['frozen_study_ids'])} 条。",
        f"- fail-closed 全部旧研究 Python 入口：{audit['guard_checks']['guarded_entrypoint_count']} 个。",
        "- 历史原路径与字节：保留。",
        "",
        "## 允许与禁止用途",
        "",
        "允许用途只有 provenance、失败分析、污染审计、任务/项目/payload 去重排除，以及明确",
        "标注为 development-only 的假设动机。禁止进入训练/SFT/RL/reward、开发或验证集、",
        "prompt/model/超参数选择、采样与停止规则调整、样本量规划、确认性测试、效果量合并、",
        "论文数字/表/图/claim，以及任何读取旧 raw response 或 rationale 的未来流水线。",
        "复制或重命名不能改变内容指纹；未来命名空间中的 hardlink、symlink、junction 与其他",
        "reparse 链均被拒绝。哈希冻结读取了范围内文件字节，但没有解释或输出凭证值、raw",
        "response、rationale、prompt 或 patch 文本。",
        "",
        "## 原 P1 Gate 的诊断",
        "",
        f"原 P1 按当前脚本集合重算为 `{old_p1['recomputed_status']}`，发现 {old_p1['violation_count']} 条命名空间冲突。",
        "其历史 `status=passed` 不再被信任；本 Gate 不给旧 pilot 添加例外，而是把整条 pilot",
        "谱系封存。",
        "",
        "## Gate",
        "",
    ]
    for name, passed in audit["checks"].items():
        lines.append(f"- `{name}`: {'PASS' if passed else 'FAIL'}")
    lines.extend(
        [
            "",
            "当前状态是 `ARMED / NO NEW STUDY`，不是新研究数据有效性的空集证明。未来研究必须",
            "先在 `data/future_studies/<study_id>/` 建立独立输入、非空 manifest 和作者签核，",
            "研究代码只能放在 `future_studies/<study_id>/`，科学输入必须经 "
            "`src/cross_review/future_study_loader.py` 读取。",
        "再把预使用清单写入唯一规范路径 `data/protocols/future_research_input_manifest_v0_1.json`，",
        "并运行 `python scripts/audit_research_lineage_isolation.py --validate-manifest "
        "data/protocols/future_research_input_manifest_v0_1.json`。签核是可审计的作者声明，不是密码学身份认证或可信时间戳。",
        "仓库 Gate 约束受认可的研究流水线；同一操作系统用户仍可绕过代码直接读取文件。若要阻止这种读取，",
        "需要另行采用操作系统账户/ACL 隔离，本次未擅自改变文件权限。",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(audit: dict[str, Any], markdown: str) -> None:
    AUDIT_JSON.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_MD.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_JSON.write_text(serialized(audit), encoding="utf-8", newline="\n")
    AUDIT_MD.write_text(markdown, encoding="utf-8", newline="\n")


def check_outputs(audit: dict[str, Any], markdown: str) -> None:
    expected = {AUDIT_JSON: serialized(audit), AUDIT_MD: markdown}
    stale = [display(path) for path, content in expected.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
    if stale:
        raise SystemExit(f"stale or missing research-lineage isolation outputs: {stale}")


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--validate-manifest", type=Path)
    mode.add_argument("--freeze-content-fingerprints", action="store_true")
    mode.add_argument("--freeze-payload-exclusions", action="store_true")
    args = parser.parse_args()

    if args.freeze_payload_exclusions:
        value = freeze_payload_exclusions(read_json(REGISTRY))
        PAYLOAD_EXCLUSIONS.write_text(serialized(value), encoding="utf-8", newline="\n")
        print(
            json.dumps(
                {
                    "status": value["status"],
                    "source_count": value["source_count"],
                    "patch_payload_sha256_count": value["patch_payload_sha256_count"],
                    "metadata_content_identifier_sha256_count": value[
                        "metadata_content_identifier_sha256_count"
                    ],
                    "model_api_calls": 0,
                },
                sort_keys=True,
            )
        )
        return

    if args.freeze_content_fingerprints:
        value = freeze_content_fingerprints(read_json(REGISTRY))
        CONTENT_FINGERPRINTS.write_text(serialized(value), encoding="utf-8", newline="\n")
        print(
            json.dumps(
                {
                    "status": value["status"],
                    "tracked_paths": value["tracked_head_content"]["matched_path_count"],
                    "cutoff_worktree_files": value["cutoff_worktree_content"]["regular_file_count"],
                    "bytes_hashed": value["cutoff_worktree_content"]["total_bytes_hashed"],
                    "reachable_history_blobs": value["reachable_git_history_content"][
                        "unique_blob_oid_count"
                    ],
                    "model_api_calls": 0,
                },
                sort_keys=True,
            )
        )
        return

    if args.validate_manifest is not None:
        registry = read_json(REGISTRY)
        derived = derive_quarantine(registry)
        path = args.validate_manifest if args.validate_manifest.is_absolute() else ROOT / args.validate_manifest
        if path.resolve(strict=False) != FUTURE_MANIFEST.resolve(strict=False):
            raise SystemExit(
                "only the canonical future-study manifest may be validated: "
                f"{display(FUTURE_MANIFEST)}"
            )
        violations = validate_activation_manifest(read_json(path), registry, derived, check_files=True)
        print(json.dumps({"manifest": str(args.validate_manifest), "passed": not violations, "violations": violations}, ensure_ascii=False, sort_keys=True))
        if violations:
            raise SystemExit(1)
        return

    audit, markdown = build_audit()
    if args.write:
        write_outputs(audit, markdown)
    else:
        check_outputs(audit, markdown)
    print(json.dumps({"status": audit["status"], "checks": audit["checks"], "new_study_data_use_authorized": False}, ensure_ascii=False, sort_keys=True))
    if audit["status"] != "passed_armed_no_new_study":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
