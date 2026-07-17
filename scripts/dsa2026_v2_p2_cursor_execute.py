# ruff: noqa: E402
#!/usr/bin/env python3
"""Generic phased executor for the unique frozen V2-P2 cursor task."""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/dsa2026_v2_p2_cursor_execute.py")

import argparse
import hashlib
import json
import shutil
import subprocess
import tarfile
import tempfile
import posixpath
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any

import dsa2026_v2_p2_freeze_task_context as source_lib
import dsa2026_v2_p2_materialize_candidates as materializer
import dsa2026_v2_p2_run_candidates as candidate_runner
import dsa2026_v2_p2_run_oracle as oracle_runner


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "data/protocols/dsa_v2_p2_cursor_task_config_v0_1.json"
DOCKERFILE = ROOT / "containers/dsa2026_v2_p2/Dockerfile.cursor"
DANGLING_AMENDMENT = ROOT / "data/protocols/dsa_v2_p2_dangling_docs_symlink_amendment_v0_1.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
        ).encode("utf-8")
    ).hexdigest()


def resolve_archive_root(archive: Path, expected_root: str) -> str:
    """Accept only the canonical full-SHA expansion of a frozen short SHA."""
    with tarfile.open(archive, "r:gz") as tar:
        roots = {PurePosixPath(member.name).parts[0] for member in tar.getmembers()
                 if PurePosixPath(member.name).parts}
    if len(roots) != 1:
        raise ValueError(f"archive must have exactly one root: {sorted(roots)}")
    actual_root = next(iter(roots))
    if actual_root == expected_root:
        return actual_root
    if "-" not in expected_root:
        raise ValueError(f"archive root drift: {actual_root} != {expected_root}")
    repository_name, frozen_commit = expected_root.rsplit("-", 1)
    actual_prefix = repository_name + "-"
    actual_commit = actual_root[len(actual_prefix):] if actual_root.startswith(actual_prefix) else ""
    is_canonical_expansion = (
        7 <= len(frozen_commit) < 40
        and len(actual_commit) == 40
        and all(char in "0123456789abcdef" for char in frozen_commit.lower())
        and all(char in "0123456789abcdef" for char in actual_commit.lower())
        and actual_commit.lower().startswith(frozen_commit.lower())
    )
    if not is_canonical_expansion:
        raise ValueError(f"archive root drift: {actual_root} != {expected_root}")
    return actual_root


def changed_source_paths(catalog_root: Path, task: dict[str, Any]) -> set[str]:
    patch = (
        catalog_root
        / "projects"
        / task["project"]
        / "bugs"
        / str(task["bug_id"])
        / "bug_patch.txt"
    ).read_text(encoding="utf-8", errors="replace")
    paths: set[str] = set()
    for line in patch.splitlines():
        if not line.startswith(("--- ", "+++ ")):
            continue
        value = line[4:].split("\t", 1)[0]
        if value == "/dev/null":
            continue
        if value.startswith(("a/", "b/")):
            value = value[2:]
        normalized = PurePosixPath(posixpath.normpath(value)).as_posix()
        if normalized and not normalized.startswith("../"):
            paths.add(normalized)
    if not paths:
        raise ValueError("changed-source path derivation is empty")
    return paths


def inspect_dangling_symlinks(archive: Path, expected_root: str) -> list[dict[str, str]]:
    with tarfile.open(archive, "r:gz") as tar:
        members = tar.getmembers()
    present = {PurePosixPath(member.name).as_posix() for member in members}
    manifest: list[dict[str, str]] = []
    for member in members:
        if not member.issym():
            continue
        parts = PurePosixPath(member.name).parts
        if not parts or parts[0] != expected_root:
            raise ValueError("archive root drift during dangling inspection")
        relative = PurePosixPath(*parts[1:])
        if PurePosixPath(member.linkname).is_absolute():
            raise ValueError("absolute symlink target is a hard stop")
        normalized = PurePosixPath(
            posixpath.normpath(str(relative.parent / PurePosixPath(member.linkname)))
        )
        if not normalized.parts or normalized.parts[0] == "..":
            raise ValueError("archive-escaping symlink is a hard stop")
        resolved = PurePosixPath(expected_root, *normalized.parts).as_posix()
        if resolved not in present:
            manifest.append({
                "kind": "symbolic",
                "path": relative.as_posix(),
                "target": member.linkname,
            })
    return sorted(manifest, key=lambda item: (item["path"], item["target"]))


def authorized_archive_extractor(
    s: dict[str, Any], catalog_root: Path, manifests: list[dict[str, Any]]
):
    amendment = read_json(DANGLING_AMENDMENT)
    if amendment.get("status") != "author_signed_immutable":
        raise PermissionError("dangling-docs amendment is not author-signed immutable")
    authorization = amendment.get("authorization", {})
    if authorization.get("general_v2_p2_source_materialization_rule") is not True:
        raise PermissionError("general dangling-docs rule is not authorized")
    declared = {
        PurePosixPath(item).as_posix()
        for item in s["task"]["declared_test_file"].split(";")
        if item
    }
    test_root = PurePosixPath(s["config"]["project_test_scope"]["project_test_root"]).as_posix().rstrip("/")
    package_metadata = {
        "setup.py", "setup.cfg", "pyproject.toml", "tox.ini", "Pipfile",
        "Pipfile.lock", "poetry.lock", "MANIFEST.in", "requirements.txt",
    }

    def extract(archive: Path, destination: Path, expected_root: str) -> dict[str, Any]:
        actual_root = resolve_archive_root(archive, expected_root)
        dangling = inspect_dangling_symlinks(archive, actual_root)
        if not dangling:
            return source_lib.extract_commit_archive(archive, destination, actual_root)
        changed = changed_source_paths(catalog_root, s["task"])
        paths = {item["path"] for item in dangling}
        predicates = {
            "all_symbolic": all(item["kind"] == "symbolic" for item in dangling),
            "all_normalized_paths_strictly_under_docs": all(
                PurePosixPath(path).parts[:1] == ("docs",) and len(PurePosixPath(path).parts) > 1
                for path in paths
            ),
            "no_changed_source_intersection": paths.isdisjoint(changed),
            "no_declared_test_intersection": paths.isdisjoint(declared),
            "no_project_test_root_intersection": all(
                path != test_root and not path.startswith(test_root + "/") for path in paths
            ),
            "no_package_build_metadata_intersection": paths.isdisjoint(package_metadata),
        }
        manifest_sha = canonical_sha(dangling)
        archive_sha = hashlib.sha256(archive.read_bytes()).hexdigest()
        manifest_record = {
            "archive_sha256": archive_sha,
            "archive_root": actual_root,
            "dangling_manifest": dangling,
            "dangling_manifest_sha256": manifest_sha,
            "predicates": predicates,
        }
        if not all(predicates.values()):
            raise ValueError(f"dangling symlink hard stop: {manifest_record}")
        if s["task_id"] == "bugsinpy_black_4":
            if archive_sha not in amendment["black_4_archive_sha256s"]:
                raise ValueError("Black_4 archive hash drift")
            if manifest_sha != amendment["black_4_manifest_sha256"]:
                raise ValueError("Black_4 dangling manifest hash drift")
        manifests.append(manifest_record)
        allowed = {(item["path"], item["target"]) for item in dangling}
        return source_lib.extract_commit_archive(
            archive, destination, actual_root, omittable_dangling_symlinks=allowed
        )

    return extract


def state() -> dict[str, Any]:
    config = read_json(CONFIG)
    task = config["task"]
    namespace = config["runtime_namespace"]
    protocol_root = ROOT / "data/protocols"
    hidden_root = ROOT / "data/hidden"
    runtime = ROOT / f"tmp/dsa_r/o{task['order']:03d}"
    return {
        "config": config,
        "task": task,
        "order": task["order"],
        "task_id": task["task_id"],
        "namespace": namespace,
        "runtime": runtime,
        "context": runtime / "context",
        "patch_root": runtime / "candidates",
        "source": protocol_root / f"dsa_v2_p2_{namespace}_source_v0_1.json",
        "environment": protocol_root / f"dsa_v2_p2_{namespace}_environment_v0_1.json",
        "oracle": hidden_root / f"dsa_v2_p2_{namespace}_oracle_v0_1.json",
        "candidate_registry": hidden_root
        / f"dsa_v2_p2_{namespace}_candidate_registry_v0_1.json",
        "candidate_results": hidden_root
        / f"dsa_v2_p2_{namespace}_candidate_results_v0_1.json",
        "terminal_draft": protocol_root
        / f"dsa_v2_p2_{namespace}_terminal_draft_v0_1.json",
        "audit": protocol_root / f"dsa_v2_p2_{namespace}_gate_audit_v0_1.json",
        "report": ROOT
        / f"docs/experiments/dsa_v2_p2_{namespace}_terminal_gate_v0_1.md",
        "image": f"dsa2026-v2-p2-task:{task['task_id']}",
    }


def next_task(order: int) -> str | None:
    records = read_json(ROOT / "data/protocols/dsa_v2_p1_source_order_v0_1.json")[
        "records"
    ]
    return records[order]["task_id"] if order < len(records) else None


def terminal_draft(
    s: dict[str, Any],
    disposition: str,
    reason: str,
    selected: str | None,
    evidence_key: str,
    evidence_sha: str,
) -> dict[str, Any]:
    return {
        "draft_id": f"dsa_v2_p2_{s['namespace']}_terminal_draft_v0_1",
        "created_date": "2026-07-12",
        "records": [
            {
                "order": s["order"],
                "task_id": s["task_id"],
                "disposition": disposition,
                "reason": reason,
                "selected_candidate_sha256": selected,
                evidence_key: evidence_sha,
            }
        ],
        "next_order": s["order"] + 1,
        "next_task_id": next_task(s["order"]),
        "next_task_started": False,
        "model_api_calls": 0,
    }


def freeze_source(s: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    source_lib.signed_amendment()
    task = dict(s["task"])
    task["metadata_sha256"] = dict(task["metadata_sha256"])
    task["metadata_sha256"].setdefault("setup_provenance_only", "")
    source_lib.TASK_ID = s["task_id"]
    source_lib.SOURCE_REPOSITORY = s["config"]["repository"]
    catalog_root = Path(args.catalog_root).resolve()
    materialization_manifests: list[dict[str, Any]] = []
    extractor = authorized_archive_extractor(s, catalog_root, materialization_manifests)
    short_temp_root = Path(ROOT.anchor) / "dsa_s"
    short_temp_root.mkdir(parents=True, exist_ok=True)
    buggy_archive = Path(args.buggy_archive).resolve()
    fixed_archive = Path(args.fixed_archive).resolve()
    with tempfile.TemporaryDirectory(prefix="s_", dir=short_temp_root) as raw:
        try:
            generated, context_record = source_lib.build_context(
                task,
                buggy_archive,
                fixed_archive,
                catalog_root,
                Path(raw),
                archive_extractor=extractor,
                archive_root_prefix=s["config"]["repository"].rstrip("/").rsplit("/", 1)[-1],
            )
        except RuntimeError as error:
            message = str(error)
            if not message.startswith((
                "reference patch check failed:",
                "reference patch apply failed:",
            )):
                raise
            value = {
                "registry_id": f"dsa_v2_p2_{s['namespace']}_source_v0_1",
                "created_date": "2026-07-12",
                "status": "materialization-failed",
                "failure_reason": "reference-patch-validation-failure",
                "cursor_config_sha256": s["config"]["config_sha256"],
                "previous_ledger_sha256": s["config"]["ledger_sha256"],
                "records": [{
                    "task_id": s["task_id"],
                    "order": s["order"],
                    "source_record": s["task"],
                    "project_test_scope": s["config"]["project_test_scope"],
                    "buggy_archive_sha256": hashlib.sha256(buggy_archive.read_bytes()).hexdigest(),
                    "fixed_archive_sha256": hashlib.sha256(fixed_archive.read_bytes()).hexdigest(),
                    "source_materialization_manifests": materialization_manifests,
                    "validation_error_type": type(error).__name__,
                    "validation_error_sha256": hashlib.sha256(message.encode("utf-8")).hexdigest(),
                    "real_activity": {
                        "real_task_checkouts": 1,
                        "environment_builds": 0,
                        "containers_started": 0,
                        "project_tests_run": 0,
                        "prompt_renders": 0,
                        "api_keys_read": 0,
                        "model_api_calls": 0,
                    },
                    "task_specific_repair_attempted": False,
                }],
                "model_api_calls": 0,
            }
            value["records"][0]["record_sha256"] = canonical_sha(value["records"][0])
            if args.write:
                s["source"].write_text(
                    json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                    newline="\n",
                )
                draft = terminal_draft(
                    s,
                    "materialization-failed",
                    "reference-patch-validation-failure",
                    None,
                    "source_record_sha256",
                    canonical_sha(value),
                )
                s["terminal_draft"].write_text(
                    json.dumps(draft, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                    newline="\n",
                )
            elif (
                not s["source"].is_file()
                or read_json(s["source"]) != value
                or not s["terminal_draft"].is_file()
            ):
                raise SystemExit("stale cursor source-failure record")
            return value
        context_record["source_materialization_manifests"] = materialization_manifests
        context_record["record_sha256"] = canonical_sha({
            key: value for key, value in context_record.items() if key != "record_sha256"
        })
        value = {
            "registry_id": f"dsa_v2_p2_{s['namespace']}_source_v0_1",
            "created_date": "2026-07-12",
            "status": "cursor_task_source_frozen",
            "cursor_config_sha256": s["config"]["config_sha256"],
            "previous_ledger_sha256": s["config"]["ledger_sha256"],
            "records": [
                {
                    "task_id": s["task_id"],
                    "order": s["order"],
                    "source_record": s["task"],
                    "project_test_scope": s["config"]["project_test_scope"],
                    "context": context_record,
                    "real_activity": {
                        "real_task_checkouts": 1,
                        "environment_builds": 0,
                        "containers_started": 0,
                        "project_tests_run": 0,
                        "prompt_renders": 0,
                        "api_keys_read": 0,
                        "model_api_calls": 0,
                    },
                }
            ],
            "model_api_calls": 0,
        }
        value["records"][0]["record_sha256"] = canonical_sha(value["records"][0])
        content = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if args.write:
            if s["context"].exists():
                shutil.rmtree(s["context"])
            s["context"].parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(generated, s["context"])
            s["source"].write_text(content, encoding="utf-8", newline="\n")
        elif (
            not s["source"].is_file()
            or s["source"].read_text(encoding="utf-8") != content
            or source_lib.tree_sha256(s["context"])
            != context_record["context_tree_sha256"]
        ):
            raise SystemExit("stale cursor source")
    return value


def build_environment(s: dict[str, Any], timeout: int) -> dict[str, Any]:
    source = read_json(s["source"])["records"][0]
    lock = s["config"]["python_lock"]
    s["runtime"].mkdir(parents=True, exist_ok=True)
    args = {
        "TASK_CONTEXT": s["context"].relative_to(ROOT).as_posix(),
        "TASK_ID": s["task_id"],
        "ORDER": str(s["order"]),
        "PROJECT": s["task"]["project"],
        "PYTHON_ENV": lock["environment_name"],
        "PYTHON_VERSION": s["task"]["python_version"],
        "LOCK_PATH": lock["path"],
        "BUGGY_COMMIT": s["task"]["buggy_commit_id"],
        "FIXED_COMMIT": s["task"]["fixed_commit_id"],
    }
    command = [
        "docker",
        "build",
        "--progress",
        "plain",
        "--no-cache",
        "-f",
        str(DOCKERFILE),
        "-t",
        s["image"],
    ]
    for key, value in args.items():
        command += ["--build-arg", f"{key}={value}"]
    command.append(str(ROOT))
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=timeout)
    output = result.stdout + result.stderr
    (s["runtime"] / "docker_build.log").write_bytes(output)
    image = None
    if result.returncode == 0:
        inspected = json.loads(
            subprocess.check_output(
                ["docker", "image", "inspect", s["image"]], text=True, encoding="utf-8"
            )
        )[0]
        image = {
            "image": s["image"],
            "image_id": inspected["Id"],
            "labels": inspected["Config"].get("Labels", {}),
        }
        expected = {
            "dsa2026.v2_p2.task_id": s["task_id"],
            "dsa2026.v2_p2.order": str(s["order"]),
            "dsa2026.v2_p2.model_api_called": "false",
            "dsa2026.v2_p2.official_setup_executed": "false",
        }
        if not all(image["labels"].get(k) == v for k, v in expected.items()):
            raise RuntimeError("cursor image label drift")
    value = {
        "environment_id": f"dsa_v2_p2_{s['namespace']}_environment_v0_1",
        "created_date": "2026-07-12",
        "task_id": s["task_id"],
        "order": s["order"],
        "status": "environment-built-oracle-not-started"
        if result.returncode == 0
        else "materialization-failed",
        "failure_reason": None
        if result.returncode == 0
        else "environment-build-failure",
        "source_record_sha256": source["record_sha256"],
        "build_exit_code": result.returncode,
        "build_output_sha256": hashlib.sha256(output).hexdigest(),
        "build_output_bytes": len(output),
        "dockerfile_sha256": hashlib.sha256(DOCKERFILE.read_bytes()).hexdigest(),
        "image": image,
        "official_setup_executed": False,
        "task_specific_repair_attempted": False,
        "activity": {
            "real_task_checkouts": 1,
            "environment_builds": 1,
            "containers_started": 0,
            "project_tests_run": 0,
            "prompt_renders": 0,
            "api_keys_read": 0,
            "model_api_calls": 0,
        },
    }
    s["environment"].write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if result.returncode:
        draft = terminal_draft(
            s,
            "materialization-failed",
            "environment-build-failure",
            None,
            "environment_record_sha256",
            canonical_sha(value),
        )
        s["terminal_draft"].write_text(
            json.dumps(draft, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    return value


def configure_science(s: dict[str, Any]) -> None:
    oracle_runner.TASK_ID = s["task_id"]
    oracle_runner.ORDER = s["order"]
    oracle_runner.ORACLE_ID = f"dsa_v2_p2_{s['namespace']}_oracle_v0_1"
    oracle_runner.ENVIRONMENT = s["environment"]
    oracle_runner.SOURCE = s["source"]
    oracle_runner.CONTEXT = s["context"]
    oracle_runner.RUNTIME = s["runtime"] / "oracle"
    oracle_runner.OUT = s["oracle"]
    oracle_runner.TERMINAL = s["terminal_draft"]
    oracle_runner.write_terminal = lambda reason, value: s["terminal_draft"].write_text(
        json.dumps(
            terminal_draft(
                s,
                "materialization-failed",
                reason,
                None,
                "oracle_record_sha256",
                canonical_sha(value),
            ),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    materializer.TASK_ID = s["task_id"]
    materializer.ORDER = s["order"]
    materializer.REGISTRY_ID = f"dsa_v2_p2_{s['namespace']}_candidate_registry_v0_1"
    materializer.CONTEXT = s["context"]
    materializer.ORACLE = s["oracle"]
    materializer.OUT = s["candidate_registry"]
    materializer.PATCH_ROOT = s["patch_root"]
    candidate_runner.TASK_ID = s["task_id"]
    candidate_runner.ORDER = s["order"]
    candidate_runner.RESULTS_ID = f"dsa_v2_p2_{s['namespace']}_candidate_results_v0_1"
    candidate_runner.SOURCE = s["source"]
    candidate_runner.ORACLE = s["oracle"]
    candidate_runner.CANDIDATES = s["candidate_registry"]
    candidate_runner.OUT = s["candidate_results"]
    candidate_runner.TERMINAL = s["terminal_draft"]
    candidate_runner.terminal_record = lambda disposition, reason, selected, results: (
        terminal_draft(
            s,
            disposition,
            reason,
            selected["order_sha256"] if selected else None,
            "candidate_results_sha256",
            canonical_sha(results),
        )
    )


def repair_oracle_metadata(s: dict[str, Any]) -> dict[str, Any]:
    """Repair generic binding fields without re-running an observed oracle."""
    configure_science(s)
    payload = read_json(s["oracle"])
    if payload.get("task_id") != s["task_id"] or payload.get("model_api_calls") != 0:
        raise ValueError("existing oracle identity or API boundary drift")
    if payload.get("order") not in (1, s["order"]):
        raise ValueError("existing oracle order cannot be mechanically rebound")
    if payload.get("oracle_id") not in (
        "dsa_v2_p2_pandas_161_oracle_v0_1",
        oracle_runner.ORACLE_ID,
    ):
        raise ValueError("existing oracle id cannot be mechanically rebound")
    payload["order"] = s["order"]
    payload["oracle_id"] = oracle_runner.ORACLE_ID
    s["oracle"].write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if payload["status"] == "materialization-failed":
        oracle_runner.write_terminal(payload["failure_reason"], payload)
    return payload


def materialize(s: dict[str, Any], write: bool) -> dict[str, Any]:
    configure_science(s)
    with tempfile.TemporaryDirectory(prefix="dsa_v2_p2_cursor_candidates_") as raw:
        registry, generated = materializer.build_registry(
            s["context"], read_json(s["oracle"]), Path(raw) / s["task_id"]
        )
        content = (
            json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        )
        if write:
            if s["patch_root"].exists():
                shutil.rmtree(s["patch_root"])
            s["patch_root"].parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(generated, s["patch_root"])
            s["candidate_registry"].write_text(content, encoding="utf-8", newline="\n")
        elif (
            not s["candidate_registry"].is_file()
            or s["candidate_registry"].read_text(encoding="utf-8") != content
        ):
            raise SystemExit("stale cursor candidates")
    return registry


def finalize(s: dict[str, Any], write: bool) -> dict[str, Any]:
    previous = read_json(ROOT / s["config"]["ledger_path"])
    draft = read_json(s["terminal_draft"])
    record = draft["records"][0]
    if record["order"] != s["order"] or record["task_id"] != s["task_id"]:
        raise ValueError("terminal draft cursor drift")
    qualified = previous["qualified_pairs"] + int(
        record["disposition"] == "pair-qualified"
    )
    ledger = {
        "ledger_id": f"dsa_v2_p2_terminal_ledger_v0_{s['order']}",
        "created_date": "2026-07-12",
        "status": f"orders_1_{s['order']}_terminal",
        "supersedes": s["config"]["ledger_path"],
        "superseded_ledger_sha256": s["config"]["ledger_sha256"],
        "records": [*previous["records"], record],
        "attempted_tasks": s["order"],
        "qualified_pairs": qualified,
        "next_order": draft["next_order"],
        "next_task_id": draft["next_task_id"],
        "next_task_started": False,
        "model_api_calls": 0,
    }
    if s["environment"].is_file():
        environment = read_json(s["environment"])
        latest_evidence = environment
    else:
        source_record = read_json(s["source"])["records"][0]
        latest_evidence = {
            "activity": source_record["real_activity"],
            "task_specific_repair_attempted": source_record["task_specific_repair_attempted"],
        }
    if s["oracle"].is_file():
        latest_evidence = read_json(s["oracle"])
    if s["candidate_results"].is_file():
        latest_evidence = read_json(s["candidate_results"])
    checks = {
        "previous_ledger_hash_unchanged": canonical_sha(previous)
        == s["config"]["ledger_sha256"],
        "records_append_exactly_once": ledger["records"][:-1] == previous["records"],
        "counts_correct": ledger["attempted_tasks"] == len(ledger["records"])
        and qualified
        == sum(item["disposition"] == "pair-qualified" for item in ledger["records"]),
        "no_task_specific_repair": not latest_evidence["task_specific_repair_attempted"],
        "next_not_started": not ledger["next_task_started"],
        "model_api_zero": ledger["model_api_calls"] == 0,
    }
    audit = {
        "audit_id": f"dsa_v2_p2_{s['namespace']}_gate_audit_v0_1",
        "created_date": "2026-07-12",
        "status": "passed_terminal_continue_cursor"
        if all(checks.values())
        else "failed",
        "task_id": s["task_id"],
        "order": s["order"],
        "checks": checks,
        "terminal_record": record,
        "activity": latest_evidence["activity"],
        "qualified_pairs_after": qualified,
        "next_task_id": ledger["next_task_id"],
        "model_api_calls": 0,
    }
    report = "\n".join(
        [
            f"# DSA v0.2 V2-P2 {s['task_id']} Terminal Gate",
            "",
            f"- order: {s['order']}",
            f"- disposition: `{record['disposition']}`",
            f"- reason: `{record['reason']}`",
            f"- qualified pairs after: {qualified}",
            f"- next task: `{ledger['next_task_id']}`; started=false",
            "- model API calls: 0",
            "",
        ]
    )
    outputs = {
        ROOT
        / f"data/protocols/dsa_v2_p2_terminal_ledger_v0_{s['order']}.json": json.dumps(
            ledger, ensure_ascii=False, indent=2, sort_keys=True
        )
        + "\n",
        s["audit"]: json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True)
        + "\n",
        s["report"]: report,
    }
    if write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    else:
        stale = [
            str(path)
            for path, content in outputs.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            raise SystemExit(f"stale cursor finalize outputs: {stale}")
    if audit["status"] != "passed_terminal_continue_cursor":
        raise SystemExit("cursor finalize audit failed")
    return audit


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "phase",
        choices=("source", "build", "oracle", "oracle-metadata", "materialize", "candidates", "finalize"),
    )
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--catalog-root")
    parser.add_argument("--buggy-archive")
    parser.add_argument("--fixed-archive")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--collection-timeout", type=int, default=3600)
    args = parser.parse_args()
    s = state()
    if args.phase == "source":
        if args.write == args.check or not all(
            (args.catalog_root, args.buggy_archive, args.fixed_archive)
        ):
            parser.error("source requires archives/catalog and one mode")
        value = freeze_source(s, args)
    elif args.phase == "build":
        if not args.write:
            parser.error("build requires --write")
        value = build_environment(s, max(args.timeout, 7200))
    elif args.phase == "oracle":
        if not args.write:
            parser.error("oracle requires --write")
        configure_science(s)
        value = oracle_runner.execute(args.timeout, args.collection_timeout)
    elif args.phase == "oracle-metadata":
        if not args.write:
            parser.error("oracle-metadata requires --write")
        value = repair_oracle_metadata(s)
    elif args.phase == "materialize":
        if args.write == args.check:
            parser.error("materialize requires one mode")
        value = materialize(s, args.write)
    elif args.phase == "candidates":
        if not args.write:
            parser.error("candidates requires --write")
        configure_science(s)
        value = candidate_runner.execute(args.timeout)
    else:
        if args.write == args.check:
            parser.error("finalize requires one mode")
        value = finalize(s, args.write)
    print(
        json.dumps(
            {
                "phase": args.phase,
                "status": value["status"],
                "order": s["order"],
                "task_id": s["task_id"],
                "model_api_calls": 0,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
