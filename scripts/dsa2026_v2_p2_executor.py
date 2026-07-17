# ruff: noqa: E402
"""Pure V2-P2 construction state machine for synthetic check-only validation.

The module has no filesystem, process, network, container, test-runner, prompt,
credential, or model capability. A separate check-only auditor loads and
validates the frozen V2-P1 JSON before constructing ``FrozenSpec``.
"""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/dsa2026_v2_p2_executor.py")

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Sequence


EXPECTED_CANDIDATE_CLASSES = (
    "T1_omit_one_source_file",
    "T2_omit_one_hunk",
    "T3_omit_one_edit_block",
    "T4_revert_one_changed_line",
)
TERMINAL_DISPOSITIONS = {"pair-qualified", "materialization-failed"}
HEX64 = re.compile(r"[0-9a-f]{64}")


class ProtocolViolation(ValueError):
    """Raised when a synthetic execution attempts to drift from V2-P1."""


@dataclass(frozen=True)
class FrozenSpec:
    protocol_id: str
    source_order_id: str
    task_ids: tuple[str, ...]
    candidate_classes: tuple[str, ...]
    candidate_order_seed: str
    target_pairs: int
    fresh_run_count: int
    visible_p2p_count: int
    hidden_maximum: int


@dataclass(frozen=True)
class RunOutcome:
    basic_pass: bool
    visible_f2p_pass: bool
    visible_p2p_pass: bool
    hidden_all_pass: bool


@dataclass(frozen=True)
class CandidateObservation:
    class_id: str
    descriptor_json: str
    order_sha256: str
    run_a: RunOutcome
    run_b: RunOutcome


@dataclass(frozen=True)
class TaskObservation:
    task_id: str
    environment_run_a_pass: bool
    environment_run_b_pass: bool
    oracle_run_a: RunOutcome
    oracle_run_b: RunOutcome
    candidates: tuple[CandidateObservation, ...]


@dataclass(frozen=True)
class TerminalRecord:
    order: int
    task_id: str
    disposition: str
    reason: str
    selected_candidate_sha256: str | None


@dataclass(frozen=True)
class CursorState:
    status: str
    attempted_tasks: int
    qualified_pairs: int
    next_order: int | None
    next_task_id: str | None
    stop_reason: str | None


@dataclass(frozen=True)
class SyntheticExecution:
    mode: str
    selected_task_started: bool
    input_cursor: CursorState
    trace: tuple[str, ...]
    terminal_record: TerminalRecord
    output_cursor: CursorState
    activity: dict[str, int]


def frozen_spec(protocol: dict[str, Any], source_order: dict[str, Any]) -> FrozenSpec:
    if protocol.get("protocol_id") != "dsa_v2_p1_construction_protocol_v0_1":
        raise ProtocolViolation("unexpected V2-P1 protocol ID")
    if protocol.get("status") != "immutable_author_signed_rules_only":
        raise ProtocolViolation("V2-P1 protocol is not author-signed immutable rules")
    if source_order.get("source_order_id") != "dsa_v2_p1_source_order_v0_1":
        raise ProtocolViolation("unexpected source-order ID")
    if source_order.get("status") != "frozen_after_v2_p1_author_signoff":
        raise ProtocolViolation("source order is not frozen after author signoff")
    authorization = protocol["current_authorization"]
    forbidden_true = [
        name
        for name in (
            "v2_p2_materialization",
            "task_checkout",
            "environment_build",
            "container_run",
            "project_test",
            "prompt_change",
            "prompt_render",
            "model_api",
            "paper_result_change",
        )
        if authorization.get(name) is not False
    ]
    if forbidden_true:
        raise ProtocolViolation(f"forbidden authorization active: {forbidden_true}")
    task_ids = tuple(record["task_id"] for record in source_order["records"])
    if len(task_ids) != source_order["eligible_task_count"] or len(set(task_ids)) != len(task_ids):
        raise ProtocolViolation("source order count/uniqueness mismatch")
    if [record["order"] for record in source_order["records"]] != list(
        range(1, len(task_ids) + 1)
    ):
        raise ProtocolViolation("source order is not contiguous")
    candidate_classes = tuple(
        item["id"]
        for item in protocol["candidate_generation"]["candidate_classes_in_priority_order"]
    )
    if candidate_classes != EXPECTED_CANDIDATE_CLASSES:
        raise ProtocolViolation("candidate class order drift")
    tie_preimage = protocol["candidate_generation"]["tie_preimage"]
    suffix = "|<task_id>|<canonical_descriptor>"
    if not tie_preimage.endswith(suffix):
        raise ProtocolViolation("candidate tie preimage drift")
    candidate_order_seed = tie_preimage[: -len(suffix)]
    qualification = protocol["qualification"]
    oracle = protocol["regression_oracle_construction"]
    if qualification["fresh_run_count"] != 2:
        raise ProtocolViolation("dual-fresh qualification drift")
    if oracle["visible_p2p_count"] != 3 or oracle["hidden_count"] != 20:
        raise ProtocolViolation("visible/hidden oracle split drift")
    return FrozenSpec(
        protocol_id=protocol["protocol_id"],
        source_order_id=source_order["source_order_id"],
        task_ids=task_ids,
        candidate_classes=candidate_classes,
        candidate_order_seed=candidate_order_seed,
        target_pairs=30,
        fresh_run_count=qualification["fresh_run_count"],
        visible_p2p_count=oracle["visible_p2p_count"],
        hidden_maximum=oracle["hidden_count"],
    )


def cursor_state(spec: FrozenSpec, ledger: Sequence[TerminalRecord]) -> CursorState:
    if len(ledger) > len(spec.task_ids):
        raise ProtocolViolation("ledger is longer than frozen source order")
    qualified = 0
    for index, record in enumerate(ledger):
        expected_order = index + 1
        expected_task = spec.task_ids[index]
        if record.order != expected_order or record.task_id != expected_task:
            raise ProtocolViolation("ledger does not follow contiguous frozen source order")
        if record.disposition not in TERMINAL_DISPOSITIONS:
            raise ProtocolViolation("ledger contains nonterminal disposition")
        if record.disposition == "pair-qualified":
            qualified += 1
    if qualified >= spec.target_pairs:
        return CursorState(
            status="cohort-qualified",
            attempted_tasks=len(ledger),
            qualified_pairs=qualified,
            next_order=None,
            next_task_id=None,
            stop_reason="target-pairs-reached",
        )
    if len(ledger) == len(spec.task_ids):
        return CursorState(
            status="source-exhausted",
            attempted_tasks=len(ledger),
            qualified_pairs=qualified,
            next_order=None,
            next_task_id=None,
            stop_reason="eligible-source-order-exhausted-before-30-pairs",
        )
    return CursorState(
        status="pending",
        attempted_tasks=len(ledger),
        qualified_pairs=qualified,
        next_order=len(ledger) + 1,
        next_task_id=spec.task_ids[len(ledger)],
        stop_reason=None,
    )


def _validate_candidates(
    spec: FrozenSpec, task_id: str, candidates: Sequence[CandidateObservation]
) -> None:
    rank = {class_id: index for index, class_id in enumerate(spec.candidate_classes)}
    keys: list[tuple[int, str, str]] = []
    descriptor_fields = {
        "class_id",
        "path",
        "hunk_index",
        "edit_block_index",
        "line_index",
        "edit_kind",
        "raw_line_value",
    }
    for candidate in candidates:
        if candidate.class_id not in rank:
            raise ProtocolViolation(f"unknown candidate class: {candidate.class_id}")
        try:
            descriptor = json.loads(candidate.descriptor_json)
        except json.JSONDecodeError as exc:
            raise ProtocolViolation("candidate descriptor is not JSON") from exc
        canonical = json.dumps(
            descriptor, ensure_ascii=False, separators=(",", ":"), sort_keys=True
        )
        if canonical != candidate.descriptor_json:
            raise ProtocolViolation("candidate descriptor is not canonical JSON")
        if not isinstance(descriptor, dict) or set(descriptor) != descriptor_fields:
            raise ProtocolViolation("candidate descriptor fields drift")
        if descriptor["class_id"] != candidate.class_id:
            raise ProtocolViolation("candidate class/descriptor disagreement")
        expected_order_hash = hashlib.sha256(
            f"{spec.candidate_order_seed}|{task_id}|{candidate.descriptor_json}".encode(
                "utf-8"
            )
        ).hexdigest()
        if not HEX64.fullmatch(candidate.order_sha256) or candidate.order_sha256 != expected_order_hash:
            raise ProtocolViolation("candidate order SHA-256 drift")
        keys.append((rank[candidate.class_id], candidate.order_sha256, candidate.descriptor_json))
    if keys != sorted(keys) or len(keys) != len(set(keys)):
        raise ProtocolViolation("candidate observations are not unique frozen order")


def _oracle_positive_passes(run: RunOutcome) -> bool:
    return (
        run.basic_pass
        and run.visible_f2p_pass
        and run.visible_p2p_pass
        and run.hidden_all_pass
    )


def _hard_negative_passes(run: RunOutcome) -> bool:
    return (
        run.basic_pass
        and run.visible_f2p_pass
        and run.visible_p2p_pass
        and not run.hidden_all_pass
    )


def execute_synthetic(
    spec: FrozenSpec,
    ledger: Sequence[TerminalRecord],
    observation: TaskObservation,
) -> SyntheticExecution:
    before = cursor_state(spec, ledger)
    if before.status != "pending" or before.next_task_id is None or before.next_order is None:
        raise ProtocolViolation(f"cannot execute from terminal cursor: {before.status}")
    if observation.task_id != before.next_task_id:
        raise ProtocolViolation("observation does not match unique frozen next task")
    _validate_candidates(spec, observation.task_id, observation.candidates)
    trace: list[str] = ["pending"]
    selected: CandidateObservation | None = None
    if not (observation.environment_run_a_pass and observation.environment_run_b_pass):
        reason = "environment-failure-or-dual-disagreement"
        trace.append("materialization-failed")
        disposition = "materialization-failed"
    else:
        trace.append("environment-qualified")
        oracle_equal = observation.oracle_run_a == observation.oracle_run_b
        if not oracle_equal or not _oracle_positive_passes(observation.oracle_run_a):
            reason = "oracle-positive-failure-or-dual-disagreement"
            trace.append("materialization-failed")
            disposition = "materialization-failed"
        else:
            trace.extend(("oracle-qualified", "candidate-search"))
            for candidate in observation.candidates:
                if candidate.run_a == candidate.run_b and _hard_negative_passes(candidate.run_a):
                    selected = candidate
                    break
            if selected is None:
                reason = "no-qualifying-hard-negative"
                trace.append("materialization-failed")
                disposition = "materialization-failed"
            else:
                reason = "first-frozen-order-hard-negative-qualified"
                trace.append("pair-qualified")
                disposition = "pair-qualified"
    terminal = TerminalRecord(
        order=before.next_order,
        task_id=before.next_task_id,
        disposition=disposition,
        reason=reason,
        selected_candidate_sha256=(selected.order_sha256 if selected else None),
    )
    after = cursor_state(spec, [*ledger, terminal])
    return SyntheticExecution(
        mode="synthetic-check-only",
        selected_task_started=False,
        input_cursor=before,
        trace=tuple(trace),
        terminal_record=terminal,
        output_cursor=after,
        activity={
            "real_task_checkouts": 0,
            "environment_builds": 0,
            "containers_started": 0,
            "project_tests_run": 0,
            "prompt_renders": 0,
            "api_keys_read": 0,
            "model_api_calls": 0,
        },
    )


def records_as_dicts(records: Iterable[TerminalRecord]) -> list[dict[str, Any]]:
    return [asdict(record) for record in records]
