"""The only sanctioned file loader for a future, independently preregistered study."""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
AUDITOR = ROOT / "scripts/audit_research_lineage_isolation.py"
CANONICAL_MANIFEST = ROOT / "data/protocols/future_research_input_manifest_v0_1.json"


def _load_auditor() -> ModuleType:
    spec = importlib.util.spec_from_file_location("_research_lineage_isolation_auditor", AUDITOR)
    if spec is None or spec.loader is None:
        raise PermissionError("research-lineage auditor is unavailable; fail closed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _authorized_paths() -> tuple[dict[str, str], dict[str, Any]]:
    auditor = _load_auditor()
    registry = auditor.read_json(auditor.REGISTRY)
    derived = auditor.derive_quarantine(registry)
    manifest = auditor.read_json(CANONICAL_MANIFEST)
    violations = auditor.validate_activation_manifest(
        manifest,
        registry,
        derived,
        check_files=True,
    )
    if violations:
        raise PermissionError(f"canonical future-study manifest rejected: {violations}")
    authorized: dict[str, str] = {}
    for item in manifest["selection_inputs"]:
        authorized[item["path"]] = item["sha256"]
    for record in manifest["records"]:
        for path, digest in record["artifact_sha256s"].items():
            if path in authorized and authorized[path] != digest:
                raise PermissionError(f"conflicting manifest hashes for {path}")
            authorized[path] = digest
    return authorized, manifest


def load_authorized_bytes(path: str) -> bytes:
    """Revalidate the canonical manifest, then read one exact declared file."""
    authorized, _manifest = _authorized_paths()
    if path not in authorized:
        raise PermissionError(f"path is not authorized by the canonical manifest: {path}")
    target = ROOT / path
    content = target.read_bytes()
    if hashlib.sha256(content).hexdigest() != authorized[path]:
        raise PermissionError(f"authorized file changed after manifest validation: {path}")
    return content


def authorization_receipt() -> dict[str, Any]:
    """Return identifiers that consumers must record before any scientific use."""
    auditor = _load_auditor()
    _authorized, manifest = _authorized_paths()
    return {
        "manifest_id": manifest["manifest_id"],
        "study_id": manifest["study_id"],
        "manifest_canonical_sha256": auditor.canonical_value_sha256(manifest),
        "quarantine_registry_canonical_sha256": manifest[
            "quarantine_registry_canonical_sha256"
        ],
    }
