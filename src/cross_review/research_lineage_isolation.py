"""Fail-closed guard for the quarantined legacy package CLI."""

from __future__ import annotations

import fnmatch
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data/protocols/research_lineage_quarantine_v0_1.json"


def _matches(path: str, patterns: list[str]) -> bool:
    folded = path.casefold()
    return any(fnmatch.fnmatchcase(folded, pattern.casefold()) for pattern in patterns)


def _load_registry() -> dict[str, Any]:
    value = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("research-lineage registry must be a JSON object")
    return value


def assert_prior_research_execution_blocked(entrypoint: str) -> None:
    """Always stop an old entrypoint; registry errors also fail closed."""
    try:
        registry = _load_registry()
        configured = (
            registry.get("status") == "author_directed_active_fail_closed"
            and _matches(
                entrypoint,
                registry["old_execution_termination"]["blocked_entrypoint_globs"],
            )
        )
    except Exception as exc:
        raise PermissionError(
            f"research-lineage isolation unavailable for {entrypoint}; fail closed"
        ) from exc
    if not configured:
        raise PermissionError(
            f"research-lineage isolation is not configured for {entrypoint}; fail closed"
        )
    raise PermissionError(
        f"{entrypoint} is revoked by research_lineage_quarantine_v0_1; "
        "start a separately preregistered study instead"
    )
