#!/usr/bin/env python3
"""Policy utility and case analysis for EVP-8-HARD tool-contestation runs.

This script only reads tracked evaluator labels, deterministic baseline
decisions, and parsed review schema fields. It must not read ignored raw
responses, rendered prompts, or patch diffs.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

EVALUATOR_MANIFEST = REPO_ROOT / "data/patches/evp8_hard_evaluator_manifest_v0_1.jsonl"
TOOL_BASELINE = REPO_ROOT / "data/baselines/evp8_hard_tool_only_baseline_v0_1.jsonl"

SYSTEM_INPUTS = {
    "tool_only_baseline": {
        "kind": "baseline",
        "path": TOOL_BASELINE,
        "display": "Tool-only baseline",
    },
    "qwen_evidence_only": {
        "kind": "review",
        "path": REPO_ROOT
        / "data/reviews/evp8_hard_e6_evidence_only_qwen_qwen3.7-max_full_reviews.jsonl",
        "display": "Qwen evidence-only",
    },
    "deepseek_evidence_only": {
        "kind": "review",
        "path": REPO_ROOT
        / "data/reviews/evp8_hard_e6_evidence_only_deepseek_deepseek-v4-pro_full_reviews.jsonl",
        "display": "DeepSeek evidence-only",
    },
    "qwen_tool_contestation": {
        "kind": "review",
        "path": REPO_ROOT
        / "data/reviews/evp8_hard_tool_contestation_qwen_qwen3.7-max_full_reviews.jsonl",
        "display": "Qwen tool-contestation",
    },
    "deepseek_tool_contestation": {
        "kind": "review",
        "path": REPO_ROOT
        / "data/reviews/evp8_hard_tool_contestation_deepseek_deepseek-v4-pro_full_reviews.jsonl",
        "display": "DeepSeek tool-contestation",
    },
}

RAW_FIELD_MARKERS = (
    "raw_response",
    "raw_response_text",
    "response_object",
    "provider_response",
    "rendered_prompt",
    "prompt_text",
    "patch_diff",
)

UTILITY_SCENARIOS = {
    "merge_gate_strict": {
        "true_accept_reward": 1.0,
        "false_accept_penalty": 20.0,
        "false_reject_penalty": 1.0,
        "escalation_cost": 0.25,
        "invalid_penalty": 20.0,
    },
    "balanced_triage": {
        "true_accept_reward": 1.0,
        "false_accept_penalty": 5.0,
        "false_reject_penalty": 1.0,
        "escalation_cost": 0.25,
        "invalid_penalty": 10.0,
    },
    "review_cost_sensitive": {
        "true_accept_reward": 1.0,
        "false_accept_penalty": 5.0,
        "false_reject_penalty": 1.0,
        "escalation_cost": 1.0,
        "invalid_penalty": 10.0,
    },
    "automation_recall": {
        "true_accept_reward": 1.0,
        "false_accept_penalty": 5.0,
        "false_reject_penalty": 2.0,
        "escalation_cost": 0.5,
        "invalid_penalty": 10.0,
    },
}


@dataclass(frozen=True)
class CandidateLabel:
    candidate_id: str
    task_id: str
    project: str
    normalized_label: str
    candidate_type: str
    expected_outcome: str

    @property
    def is_correct(self) -> bool:
        return self.normalized_label == "correct"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_labels() -> dict[str, CandidateLabel]:
    labels: dict[str, CandidateLabel] = {}
    for row in read_jsonl(EVALUATOR_MANIFEST):
        candidate_id = row["hard_candidate_id"]
        labels[candidate_id] = CandidateLabel(
            candidate_id=candidate_id,
            task_id=row["task_id"],
            project=row["project"],
            normalized_label=row["normalized_label"],
            candidate_type=row["candidate_type"],
            expected_outcome=row["expected_outcome"],
        )
    return labels


def detect_raw_fields(rows: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    for row in rows:
        for key in row:
            key_lower = key.lower()
            if any(marker in key_lower for marker in RAW_FIELD_MARKERS):
                seen.add(key)
    return sorted(seen)


def normalize_decision(value: Any) -> str:
    decision = str(value or "").strip().lower()
    if decision in {"accept", "reject", "escalate"}:
        return decision
    return "invalid"


def load_decisions(system_id: str, spec: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    rows = read_jsonl(spec["path"])
    raw_fields = detect_raw_fields(rows)
    decisions: dict[str, dict[str, Any]] = {}
    for row in rows:
        if spec["kind"] == "baseline":
            candidate_id = row["candidate_id"]
            parse_status = "valid"
        else:
            candidate_id = row["anonymous_candidate_id"]
            parse_status = row.get("parse_status", "valid")
        decision = normalize_decision(row.get("decision"))
        if parse_status != "valid":
            decision = "invalid"
        decisions[candidate_id] = {
            "system_id": system_id,
            "candidate_id": candidate_id,
            "decision": decision,
            "parse_status": parse_status,
            "primary_reason": row.get("primary_reason"),
            "risk_flags": row.get("risk_flags") or [],
            "coverage_concern": row.get("coverage_concern"),
            "visible_tests_sufficient": row.get("visible_tests_sufficient"),
            "tool_evidence_reliability": row.get("tool_evidence_reliability"),
            "would_challenge_visible_test_only_accept": row.get(
                "would_challenge_visible_test_only_accept"
            ),
            "challenge_reason": row.get("challenge_reason"),
        }
    return decisions, raw_fields


def confusion_for_system(
    labels: dict[str, CandidateLabel], decisions: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    counts = Counter(
        {
            "true_accept": 0,
            "false_accept": 0,
            "true_reject": 0,
            "false_reject": 0,
            "escalated_correct": 0,
            "escalated_incorrect": 0,
            "invalid_correct": 0,
            "invalid_incorrect": 0,
        }
    )
    examples: dict[str, list[str]] = defaultdict(list)
    decision_counts = Counter()

    for candidate_id, label in labels.items():
        record = decisions.get(candidate_id)
        decision = record["decision"] if record else "invalid"
        decision_counts[decision] += 1
        if decision == "accept" and label.is_correct:
            bucket = "true_accept"
        elif decision == "accept":
            bucket = "false_accept"
        elif decision == "reject" and label.is_correct:
            bucket = "false_reject"
        elif decision == "reject":
            bucket = "true_reject"
        elif decision == "escalate" and label.is_correct:
            bucket = "escalated_correct"
        elif decision == "escalate":
            bucket = "escalated_incorrect"
        elif label.is_correct:
            bucket = "invalid_correct"
        else:
            bucket = "invalid_incorrect"
        counts[bucket] += 1
        examples[bucket].append(candidate_id)

    correct_total = sum(1 for label in labels.values() if label.is_correct)
    incorrect_total = len(labels) - correct_total
    accepted_total = counts["true_accept"] + counts["false_accept"]
    escalated_total = counts["escalated_correct"] + counts["escalated_incorrect"]
    invalid_total = counts["invalid_correct"] + counts["invalid_incorrect"]

    metrics = {
        "record_count": len(labels),
        "correct_total": correct_total,
        "incorrect_total": incorrect_total,
        "accepted_total": accepted_total,
        "accepted_precision": safe_div(counts["true_accept"], accepted_total),
        "correct_recall": safe_div(counts["true_accept"], correct_total),
        "false_accept_rate": safe_div(counts["false_accept"], incorrect_total),
        "false_reject_rate": safe_div(counts["false_reject"], correct_total),
        "escalation_rate": safe_div(escalated_total, len(labels)),
        "automation_accept_rate": safe_div(accepted_total, len(labels)),
        "wrong_patch_safe_handling_rate": safe_div(
            counts["true_reject"] + counts["escalated_incorrect"], incorrect_total
        ),
        "invalid_output_rate": safe_div(invalid_total, len(labels)),
    }
    return {
        "counts": dict(counts),
        "decision_counts": dict(decision_counts),
        "metrics": metrics,
        "examples": {key: value for key, value in sorted(examples.items())},
    }


def safe_div(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 6)


def utility_score(counts: dict[str, int], params: dict[str, float]) -> float:
    escalated = counts["escalated_correct"] + counts["escalated_incorrect"]
    invalid = counts["invalid_correct"] + counts["invalid_incorrect"]
    return round(
        params["true_accept_reward"] * counts["true_accept"]
        - params["false_accept_penalty"] * counts["false_accept"]
        - params["false_reject_penalty"] * counts["false_reject"]
        - params["escalation_cost"] * escalated
        - params["invalid_penalty"] * invalid,
        6,
    )


def build_utility_tables(confusions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    scenario_tables: dict[str, Any] = {}
    for scenario, params in UTILITY_SCENARIOS.items():
        rows = []
        for system_id, payload in confusions.items():
            score = utility_score(payload["counts"], params)
            rows.append(
                {
                    "system_id": system_id,
                    "score": score,
                    "score_per_candidate": round(score / payload["metrics"]["record_count"], 6),
                    "parameters": params,
                }
            )
        rows.sort(key=lambda row: row["score"], reverse=True)
        for rank, row in enumerate(rows, start=1):
            row["rank"] = rank
        scenario_tables[scenario] = {
            "parameters": params,
            "rows": rows,
            "best_systems": [row["system_id"] for row in rows if row["score"] == rows[0]["score"]],
        }

    sensitivity = Counter()
    grid_rows = []
    for false_accept_penalty in [2.0, 5.0, 10.0, 20.0]:
        for escalation_cost in [0.0, 0.25, 0.5, 1.0, 2.0]:
            params = {
                "true_accept_reward": 1.0,
                "false_accept_penalty": false_accept_penalty,
                "false_reject_penalty": 1.0,
                "escalation_cost": escalation_cost,
                "invalid_penalty": 10.0,
            }
            scores = {
                system_id: utility_score(payload["counts"], params)
                for system_id, payload in confusions.items()
            }
            best_score = max(scores.values())
            winners = tuple(sorted(system_id for system_id, score in scores.items() if score == best_score))
            sensitivity[" + ".join(winners)] += 1
            grid_rows.append(
                {
                    "false_accept_penalty": false_accept_penalty,
                    "escalation_cost": escalation_cost,
                    "best_systems": list(winners),
                    "best_score": best_score,
                    "scores": scores,
                }
            )
    return {
        "scenarios": scenario_tables,
        "sensitivity_grid": grid_rows,
        "sensitivity_winner_counts": dict(sensitivity),
    }


def compact_text(value: Any, limit: int = 220) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def build_case_analysis(
    labels: dict[str, CandidateLabel],
    decisions_by_system: dict[str, dict[str, dict[str, Any]]],
    confusions: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    tool_false_accepts = sorted(confusions["tool_only_baseline"]["examples"].get("false_accept", []))
    opportunity_rows = []
    for candidate_id in tool_false_accepts:
        label = labels[candidate_id]
        row = {
            "candidate_id": candidate_id,
            "task_id": label.task_id,
            "project": label.project,
            "normalized_label": label.normalized_label,
            "candidate_type": label.candidate_type,
            "expected_outcome": label.expected_outcome,
            "systems": {},
        }
        for system_id in [
            "qwen_evidence_only",
            "deepseek_evidence_only",
            "qwen_tool_contestation",
            "deepseek_tool_contestation",
        ]:
            record = decisions_by_system[system_id][candidate_id]
            row["systems"][system_id] = {
                "decision": record["decision"],
                "coverage_concern": record.get("coverage_concern"),
                "visible_tests_sufficient": record.get("visible_tests_sufficient"),
                "tool_evidence_reliability": record.get("tool_evidence_reliability"),
                "would_challenge_visible_test_only_accept": record.get(
                    "would_challenge_visible_test_only_accept"
                ),
                "primary_reason": compact_text(record.get("primary_reason")),
                "challenge_reason": compact_text(record.get("challenge_reason")),
            }
        opportunity_rows.append(row)

    opportunity_summary = {}
    for system_id in [
        "qwen_evidence_only",
        "deepseek_evidence_only",
        "qwen_tool_contestation",
        "deepseek_tool_contestation",
    ]:
        decisions = Counter(decisions_by_system[system_id][cid]["decision"] for cid in tool_false_accepts)
        opportunity_summary[system_id] = {
            "decision_counts_on_tool_false_accepts": dict(decisions),
            "strict_reject_count": decisions.get("reject", 0),
            "safe_handled_count": decisions.get("reject", 0) + decisions.get("escalate", 0),
            "repeated_accept_count": decisions.get("accept", 0),
        }

    qwen_residual = [
        row
        for row in opportunity_rows
        if row["systems"]["qwen_tool_contestation"]["decision"] == "accept"
    ]

    deepseek_escalated_correct = []
    for candidate_id in confusions["deepseek_tool_contestation"]["examples"].get(
        "escalated_correct", []
    ):
        label = labels[candidate_id]
        deepseek_record = decisions_by_system["deepseek_tool_contestation"][candidate_id]
        qwen_record = decisions_by_system["qwen_tool_contestation"][candidate_id]
        deepseek_escalated_correct.append(
            {
                "candidate_id": candidate_id,
                "task_id": label.task_id,
                "project": label.project,
                "candidate_type": label.candidate_type,
                "deepseek_decision": deepseek_record["decision"],
                "qwen_decision": qwen_record["decision"],
                "deepseek_primary_reason": compact_text(deepseek_record.get("primary_reason")),
                "deepseek_challenge_reason": compact_text(deepseek_record.get("challenge_reason")),
            }
        )

    return {
        "tool_false_accept_opportunity_ids": tool_false_accepts,
        "opportunity_summary": opportunity_summary,
        "opportunity_cases": opportunity_rows,
        "qwen_residual_false_accept_cases": qwen_residual,
        "deepseek_escalated_correct_cases": deepseek_escalated_correct,
        "interpretation": {
            "strict_correction": "Neither model strictly rejected the nine tool false accepts under tool-contestation.",
            "risk_triage": "Tool-contestation mainly converts repeated false accepts into escalation.",
            "automation_tradeoff": "The same prompt sharply reduces autonomous correct-patch acceptance.",
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# EVP-8-HARD Tool-Contestation Policy and Case Analysis")
    lines.append("")
    lines.append("This is a no-API, raw-output-free analysis over tracked labels,")
    lines.append("deterministic baseline decisions, and parsed review schema fields.")
    lines.append("")

    lines.append("## Whole-cohort policy metrics")
    lines.append("")
    lines.append(
        "| System | accept | reject | escalate | true accept | false accept | "
        "correct recall | accepted precision | false accept rate | escalation rate |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for system_id, conf in payload["systems"].items():
        decisions = conf["decision_counts"]
        counts = conf["counts"]
        metrics = conf["metrics"]
        lines.append(
            f"| {system_id} | {decisions.get('accept', 0)} | {decisions.get('reject', 0)} | "
            f"{decisions.get('escalate', 0)} | {counts['true_accept']} | "
            f"{counts['false_accept']} | {fmt_pct(metrics['correct_recall'])} | "
            f"{fmt_pct(metrics['accepted_precision'])} | {fmt_pct(metrics['false_accept_rate'])} | "
            f"{fmt_pct(metrics['escalation_rate'])} |"
        )
    lines.append("")

    lines.append("## Utility scenarios")
    lines.append("")
    for scenario, table in payload["utility"]["scenarios"].items():
        params = table["parameters"]
        lines.append(
            f"### {scenario} "
            f"(FA penalty={params['false_accept_penalty']}, "
            f"FR penalty={params['false_reject_penalty']}, "
            f"escalation cost={params['escalation_cost']})"
        )
        lines.append("")
        lines.append("| Rank | System | Score | Score/candidate |")
        lines.append("|---:|---|---:|---:|")
        for row in table["rows"]:
            lines.append(
                f"| {row['rank']} | {row['system_id']} | {row['score']:.3f} | "
                f"{row['score_per_candidate']:.3f} |"
            )
        lines.append("")

    lines.append("## Sensitivity summary")
    lines.append("")
    lines.append(
        "Across the penalty grid "
        "`false_accept_penalty in {2,5,10,20}` x "
        "`escalation_cost in {0,0.25,0.5,1,2}`:"
    )
    lines.append("")
    lines.append("| Winner | Grid cells |")
    lines.append("|---|---:|")
    for winner, count in sorted(
        payload["utility"]["sensitivity_winner_counts"].items(), key=lambda item: (-item[1], item[0])
    ):
        lines.append(f"| {winner} | {count} |")
    lines.append("")

    cases = payload["case_analysis"]
    lines.append("## Opportunity-set cases")
    lines.append("")
    lines.append(
        "The opportunity set contains the nine candidates that the deterministic "
        "tool-only baseline false-accepted."
    )
    lines.append("")
    lines.append("| System | repeated accept | escalate | strict reject | safe handled |")
    lines.append("|---|---:|---:|---:|---:|")
    for system_id, summary in cases["opportunity_summary"].items():
        decisions = summary["decision_counts_on_tool_false_accepts"]
        lines.append(
            f"| {system_id} | {summary['repeated_accept_count']} | "
            f"{decisions.get('escalate', 0)} | {summary['strict_reject_count']} | "
            f"{summary['safe_handled_count']} |"
        )
    lines.append("")

    lines.append("## Residual and conservative cases")
    lines.append("")
    qwen_residual = cases["qwen_residual_false_accept_cases"]
    lines.append(f"- Qwen residual false accepts under tool-contestation: {len(qwen_residual)}.")
    for row in qwen_residual:
        qwen = row["systems"]["qwen_tool_contestation"]
        deepseek = row["systems"]["deepseek_tool_contestation"]
        lines.append(
            f"  - `{row['candidate_id']}` / `{row['task_id']}` / `{row['candidate_type']}`: "
            f"Qwen accepted with visible_tests_sufficient={qwen['visible_tests_sufficient']} "
            f"and reliability={qwen['tool_evidence_reliability']}; "
            f"DeepSeek decision={deepseek['decision']}."
        )
    lines.append(
        f"- DeepSeek escalated correct patches under tool-contestation: "
        f"{len(cases['deepseek_escalated_correct_cases'])}."
    )
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "- The result has practical value only as a risk-policy finding: explicit "
        "tool-contestation greatly reduces unsafe autonomous accepts when false "
        "accepts are expensive."
    )
    lines.append(
        "- It is not evidence that the LLM semantically verifies correctness: strict "
        "reject remains 0/9 on known tool false accepts, and the main improvement "
        "is accept-to-escalate."
    )
    lines.append(
        "- The usable paper claim is therefore a tradeoff claim: tool-contestation "
        "can be a conservative triage layer, but it sacrifices automation recall "
        "and still needs human or stronger semantic evidence for final correctness."
    )
    lines.append("")
    return "\n".join(lines)


def fmt_pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.2f}%"


def validate_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload["boundary"]["raw_field_violations"]:
        errors.append("raw-like fields were found in tracked inputs")
    if payload["candidate_count"] != 47:
        errors.append(f"expected 47 candidates, got {payload['candidate_count']}")
    for system_id, conf in payload["systems"].items():
        if conf["metrics"]["record_count"] != 47:
            errors.append(f"{system_id} record count is not 47")
    qwen_residual = payload["case_analysis"]["qwen_residual_false_accept_cases"]
    if len(qwen_residual) != 1:
        errors.append(f"expected one Qwen residual false accept, got {len(qwen_residual)}")
    deepseek_residual = payload["case_analysis"]["opportunity_summary"][
        "deepseek_tool_contestation"
    ]["repeated_accept_count"]
    if deepseek_residual != 0:
        errors.append(f"expected zero DeepSeek repeated accepts, got {deepseek_residual}")
    for system_id in ["qwen_tool_contestation", "deepseek_tool_contestation"]:
        strict_reject = payload["case_analysis"]["opportunity_summary"][system_id][
            "strict_reject_count"
        ]
        if strict_reject != 0:
            errors.append(f"expected zero strict rejects for {system_id}, got {strict_reject}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out-json",
        default=str(
            REPO_ROOT
            / "data/reviews/evp8_hard_tool_contestation_policy_case_analysis_v0_1.json"
        ),
    )
    parser.add_argument(
        "--out-md",
        default=str(
            REPO_ROOT
            / "docs/experiments/evp8_hard_tool_contestation_policy_case_analysis_v0_1.md"
        ),
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    labels = load_labels()
    decisions_by_system: dict[str, dict[str, dict[str, Any]]] = {}
    raw_field_violations: dict[str, list[str]] = {}

    for system_id, spec in SYSTEM_INPUTS.items():
        decisions, raw_fields = load_decisions(system_id, spec)
        decisions_by_system[system_id] = decisions
        if raw_fields:
            raw_field_violations[system_id] = raw_fields

    confusions = {
        system_id: confusion_for_system(labels, decisions)
        for system_id, decisions in decisions_by_system.items()
    }

    payload = {
        "analysis_id": "evp8_hard_tool_contestation_policy_case_analysis_v0_1",
        "cohort_id": "evp8_hard_v0_1",
        "candidate_count": len(labels),
        "boundary": {
            "api_call_attempted": False,
            "raw_outputs_read": False,
            "patch_diff_saved": False,
            "prompt_modified": False,
            "raw_field_violations": raw_field_violations,
        },
        "inputs": {
            "evaluator_manifest": str(EVALUATOR_MANIFEST.relative_to(REPO_ROOT)),
            "systems": {
                system_id: str(spec["path"].relative_to(REPO_ROOT))
                for system_id, spec in SYSTEM_INPUTS.items()
            },
        },
        "systems": confusions,
        "utility": build_utility_tables(confusions),
        "case_analysis": build_case_analysis(labels, decisions_by_system, confusions),
    }

    errors = validate_payload(payload)
    payload["validation"] = {"status": "passed" if not errors else "failed", "errors": errors}

    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    write_json(out_json, payload)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(render_markdown(payload), encoding="utf-8")

    print(
        json.dumps(
            {
                "analysis_id": payload["analysis_id"],
                "validation": payload["validation"],
                "out_json": str(out_json),
                "out_md": str(out_md),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
