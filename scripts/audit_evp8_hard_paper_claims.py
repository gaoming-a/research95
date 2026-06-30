#!/usr/bin/env python3
"""Generate EVP-8-HARD paper claim traceability and final table scaffold.

This is a no-API, raw-output-free paper-facing audit. It reads only tracked
aggregate audits and analysis JSON files.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

FULL_WITH_VERDICT_AUDIT = REPO_ROOT / "data/protocols/evp8_hard_qwen_deepseek_result_audit_v0_1.json"
EVIDENCE_ONLY_AUDIT = REPO_ROOT / "data/protocols/evp8_hard_e6_evidence_only_result_audit_v0_1.json"
TOOL_CONTESTATION_AUDIT = REPO_ROOT / "data/protocols/evp8_hard_tool_contestation_result_audit_v0_1.json"
POLICY_CASE_ANALYSIS = (
    REPO_ROOT / "data/reviews/evp8_hard_tool_contestation_policy_case_analysis_v0_1.json"
)
STATISTICAL_BOUNDARY = (
    REPO_ROOT / "data/reviews/evp8_hard_e6_evidence_only_statistical_boundary_v0_1.json"
)

DEFAULT_TRACE_JSON = REPO_ROOT / "data/reviews/evp8_hard_paper_claim_traceability_v0_1.json"
DEFAULT_TRACE_MD = REPO_ROOT / "docs/experiments/evp8_hard_paper_claim_traceability_v0_1.md"
DEFAULT_TABLE_JSON = REPO_ROOT / "data/reviews/evp8_hard_final_results_table_scaffold_v0_1.json"
DEFAULT_TABLE_MD = (
    REPO_ROOT / "docs/experiments/evp8_hard_final_results_table_scaffold_v0_1.md"
)

RAW_MARKERS = (
    "raw_response",
    "provider_response",
    "rendered_prompt",
    "prompt_text",
    "patch_diff",
    "patch_text",
)

SUPPORTED_CLAIMS = [
    {
        "id": "hard_cohort_scope",
        "claim": (
            "EVP-8-HARD is a controlled 47-candidate hard-case cohort with "
            "10 correct and 37 incorrect candidates."
        ),
        "evidence_sources": ["full_with_verdict_audit", "policy_case_analysis"],
        "evidence_summary": (
            "All audited systems report 47 records, 10 correct candidates, and "
            "37 incorrect candidates."
        ),
        "paper_use": "Dataset and experimental setup.",
    },
    {
        "id": "verdict_like_summary_dominance",
        "claim": (
            "When the verdict-like deterministic merge-gate summary is visible, "
            "Qwen and DeepSeek reproduce the tool-only baseline decisions on this cohort."
        ),
        "evidence_sources": ["full_with_verdict_audit"],
        "evidence_summary": (
            "Tool-only, Qwen with-verdict, and DeepSeek with-verdict all have "
            "accept=17, reject=30, false_accept=9, false_reject=2, and no escalation."
        ),
        "paper_use": "Core result for tool-verdict dominance.",
    },
    {
        "id": "evidence_only_partial_decoupling",
        "claim": (
            "Removing verdict-like fields partially decouples LLM decisions from "
            "the tool baseline, but does not yield strict correction of known false accepts."
        ),
        "evidence_sources": ["evidence_only_audit", "policy_case_analysis"],
        "evidence_summary": (
            "On the nine tool false accepts, Qwen evidence-only repeats seven accepts "
            "and DeepSeek evidence-only repeats four; strict reject remains 0."
        ),
        "paper_use": "Ablation result and limitation.",
    },
    {
        "id": "tool_contestation_risk_triage",
        "claim": (
            "Explicit tool-contestation reduces unsafe autonomous accepts mainly by "
            "routing known tool false accepts to escalation."
        ),
        "evidence_sources": ["tool_contestation_audit", "policy_case_analysis"],
        "evidence_summary": (
            "On the nine tool false accepts, Qwen tool-contestation escalates eight "
            "and repeats one accept; DeepSeek escalates all nine. Strict reject is 0/9."
        ),
        "paper_use": "Main positive, bounded result.",
    },
    {
        "id": "policy_utility_tradeoff",
        "claim": (
            "Tool-contestation is useful under policies where false accepts are much "
            "more expensive than human escalation, but this utility is conditional."
        ),
        "evidence_sources": ["policy_case_analysis"],
        "evidence_summary": (
            "DeepSeek tool-contestation wins 16/20 sensitivity cells, but correct "
            "recall is 0 because all correct accepted-by-tool patches are escalated or rejected."
        ),
        "paper_use": "Discussion and practical implications.",
    },
]

QUALIFIED_CLAIMS = [
    {
        "id": "risk_controller_not_merge_gate",
        "claim": (
            "The system can be positioned as an evidence-aware risk controller, "
            "not as an autonomous merge gate."
        ),
        "condition": (
            "Only valid when escalation is treated as human-review routing and not as "
            "automatic correctness verification."
        ),
    },
    {
        "id": "llm_added_value_is_policy_behavior",
        "claim": "The observed LLM-added value is policy behavior over evidence, not semantic proof.",
        "condition": (
            "Supported because known false accepts become escalations, while strict "
            "reject remains zero on the primary opportunity set."
        ),
    },
]

FORBIDDEN_CLAIMS = [
    {
        "id": "automatic_correctness_verifier",
        "claim": "The EVP-8-HARD system is a reliable automatic patch correctness verifier.",
        "reason": "Tool-contestation does not strictly reject the nine known tool false accepts.",
    },
    {
        "id": "llm_beats_tools_as_merge_gate",
        "claim": "Qwen or DeepSeek outperforms the deterministic tool-only baseline as an automatic merge gate.",
        "reason": (
            "With verdict, both models match the tool baseline; without verdict, gains are "
            "mostly escalation and correct recall collapses under tool-contestation."
        ),
    },
    {
        "id": "semantic_error_detection",
        "claim": "The LLM semantically identifies the wrong patches in the opportunity set.",
        "reason": "Strict reject is 0/9 for both tool-contestation models.",
    },
    {
        "id": "broad_external_validity",
        "claim": "The 47-candidate controlled cohort proves performance on real agent patch distributions.",
        "reason": "The cohort is controlled and small; realistic hard-negative acquisition remains a separate boundary.",
    },
    {
        "id": "monotonic_more_evidence_better",
        "claim": "More visible evidence monotonically improves verifier quality.",
        "reason": "E6 with verdict repeats tool false accepts; tool-contestation improves safety by escalation but loses recall.",
    },
]


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def input_state(path: Path) -> dict[str, Any]:
    return {
        "path": rel(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
    }


def find_raw_like_keys(value: Any, prefix: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_path = f"{prefix}.{key}" if prefix else str(key)
            lower = str(key).lower()
            if any(marker in lower for marker in RAW_MARKERS) and child is not False:
                hits.append(key_path)
            hits.extend(find_raw_like_keys(child, key_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(find_raw_like_keys(child, f"{prefix}[{index}]"))
    return hits


def system_row(system_id: str, variant: str, model: str, payload: dict[str, Any]) -> dict[str, Any]:
    counts = (payload.get("confusion") or {}).get("counts") or payload.get("counts") or {}
    metrics = payload.get("metrics") or (payload.get("confusion") or {}).get("metrics") or {}
    decisions = payload.get("decision_counts") or {}
    return {
        "system_id": system_id,
        "variant": variant,
        "model": model,
        "accept": decisions.get("accept", 0),
        "reject": decisions.get("reject", 0),
        "escalate": decisions.get("escalate", 0),
        "true_accept": counts.get("true_accept", 0),
        "false_accept": counts.get("false_accept", 0),
        "false_reject": counts.get("false_reject", 0),
        "accepted_precision": metrics.get("accepted_precision"),
        "correct_recall": metrics.get("correct_recall"),
        "false_accept_rate": metrics.get("false_accept_rate"),
        "false_reject_rate": metrics.get("false_reject_rate"),
        "escalation_rate": metrics.get("escalation_rate"),
        "claim_use": claim_use_for_variant(variant),
    }


def claim_use_for_variant(variant: str) -> str:
    if variant == "tool_only_baseline":
        return "baseline risk and opportunity-set definition"
    if variant == "with_verdict":
        return "tool-verdict dominance"
    if variant == "evidence_only":
        return "verdict removal ablation"
    if variant == "tool_contestation":
        return "risk triage under explicit contestation"
    return "descriptive"


def fmt_pct(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value) * 100:.2f}%"


def build_results_tables(
    full: dict[str, Any],
    evidence: dict[str, Any],
    contest: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    rows = [
        system_row(
            "tool_only_baseline",
            "tool_only_baseline",
            "deterministic",
            full["tool_only_baseline"],
        )
    ]
    for model_id, model_payload in sorted(full["models"].items()):
        rows.append(system_row(f"{model_id}::with_verdict", "with_verdict", model_id, model_payload))
    for model_id, model_payload in sorted(evidence["models"].items()):
        rows.append(system_row(f"{model_id}::evidence_only", "evidence_only", model_id, model_payload))
    for model_id, model_payload in sorted(contest["models"].items()):
        rows.append(system_row(f"{model_id}::tool_contestation", "tool_contestation", model_id, model_payload))

    opportunity = []
    opportunity.append(
        {
            "system_id": "tool_only_baseline",
            "variant": "tool_only_baseline",
            "repeated_accept": 9,
            "escalate": 0,
            "strict_reject": 0,
            "safe_handled": 0,
            "interpretation": "defines the nine-case false-accept opportunity set",
        }
    )
    opportunity.append(
        {
            "system_id": "qwen_with_verdict",
            "variant": "with_verdict",
            "repeated_accept": 9,
            "escalate": 0,
            "strict_reject": 0,
            "safe_handled": 0,
            "interpretation": "repeats tool-only false accepts",
        }
    )
    opportunity.append(
        {
            "system_id": "deepseek_with_verdict",
            "variant": "with_verdict",
            "repeated_accept": 9,
            "escalate": 0,
            "strict_reject": 0,
            "safe_handled": 0,
            "interpretation": "repeats tool-only false accepts",
        }
    )
    for system_id, summary in policy["case_analysis"]["opportunity_summary"].items():
        decisions = summary["decision_counts_on_tool_false_accepts"]
        opportunity.append(
            {
                "system_id": system_id,
                "variant": "evidence_only" if "evidence_only" in system_id else "tool_contestation",
                "repeated_accept": summary["repeated_accept_count"],
                "escalate": decisions.get("escalate", 0),
                "strict_reject": summary["strict_reject_count"],
                "safe_handled": summary["safe_handled_count"],
                "interpretation": (
                    "safe handling is escalation-driven"
                    if summary["safe_handled_count"]
                    else "no opportunity-set improvement"
                ),
            }
        )

    utility_rows = []
    for scenario, table in policy["utility"]["scenarios"].items():
        top = table["rows"][0]
        utility_rows.append(
            {
                "scenario": scenario,
                "best_system": top["system_id"],
                "best_score": top["score"],
                "false_accept_penalty": table["parameters"]["false_accept_penalty"],
                "false_reject_penalty": table["parameters"]["false_reject_penalty"],
                "escalation_cost": table["parameters"]["escalation_cost"],
                "claim_use": "conditional policy ranking, not correctness proof",
            }
        )

    return {
        "analysis_id": "evp8_hard_final_results_table_scaffold_v0_1",
        "boundary": {
            "api_call_attempted": False,
            "raw_outputs_read": False,
            "patch_diff_saved": False,
            "prompt_modified": False,
        },
        "whole_cohort_rows": rows,
        "opportunity_set_rows": opportunity,
        "utility_rows": utility_rows,
        "sensitivity_winner_counts": policy["utility"]["sensitivity_winner_counts"],
        "table_notes": [
            "Use with-verdict rows for tool-verdict dominance, not LLM-added-value claims.",
            "Use tool-contestation rows for risk-triage claims, not semantic correctness claims.",
            "Report accepted precision as n/a when accepted_total is zero.",
        ],
    }


def build_claim_traceability(
    full: dict[str, Any],
    evidence: dict[str, Any],
    contest: dict[str, Any],
    policy: dict[str, Any],
    stats: dict[str, Any],
    tables: dict[str, Any],
    raw_key_hits: dict[str, list[str]],
) -> dict[str, Any]:
    checks = [
        check("full_with_verdict_audit_passed", full.get("audit_status") == "passed", full.get("audit_status")),
        check("evidence_only_audit_passed", evidence.get("audit_status") == "passed", evidence.get("audit_status")),
        check("tool_contestation_audit_passed", contest.get("audit_status") == "passed", contest.get("audit_status")),
        check(
            "policy_case_analysis_passed",
            (policy.get("validation") or {}).get("status") == "passed",
            (policy.get("validation") or {}).get("status"),
        ),
        check("candidate_count_consistent", candidate_counts_consistent(full, evidence, contest, policy)),
        check("raw_like_keys_absent", not raw_key_hits, raw_key_hits),
        check("with_verdict_models_match_tool", with_verdict_models_match_tool(full)),
        check("tool_contestation_strict_reject_zero", tool_contestation_strict_reject_zero(policy)),
        check("table_scaffold_has_required_rows", len(tables["whole_cohort_rows"]) == 7),
    ]
    return {
        "audit_id": "evp8_hard_paper_claim_traceability_v0_1",
        "boundary": (
            "This audit maps EVP-8-HARD paper claims to tracked aggregate evidence. "
            "It does not call model APIs, read raw model responses, read patch diffs, "
            "modify prompts, or infer new model outputs."
        ),
        "inputs": {
            "full_with_verdict_audit": input_state(FULL_WITH_VERDICT_AUDIT),
            "evidence_only_audit": input_state(EVIDENCE_ONLY_AUDIT),
            "tool_contestation_audit": input_state(TOOL_CONTESTATION_AUDIT),
            "policy_case_analysis": input_state(POLICY_CASE_ANALYSIS),
            "statistical_boundary": input_state(STATISTICAL_BOUNDARY),
        },
        "checks": checks,
        "passed": all(item["passed"] for item in checks),
        "supported_claims": supported_claim_records(),
        "qualified_claims": QUALIFIED_CLAIMS,
        "forbidden_claims": FORBIDDEN_CLAIMS,
        "terminology_ledger": terminology_ledger(),
        "one_sentence_argument": (
            "In controlled candidate patch verification, EVP-8-HARD shows that "
            "verdict-like tool evidence can dominate LLM decisions, while explicit "
            "tool-contestation can reduce unsafe autonomous accepts through escalation, "
            "but the evidence supports risk triage rather than autonomous correctness verification."
        ),
        "paper_section_scaffold": paper_section_scaffold(),
        "linked_table_scaffold": {
            "json": rel(DEFAULT_TABLE_JSON),
            "markdown": rel(DEFAULT_TABLE_MD),
        },
        "statistical_boundary": stats.get("claim_boundary"),
    }


def supported_claim_records() -> list[dict[str, Any]]:
    return [
        {
            **claim,
            "status": "supported",
            "allowed_wording": allowed_wording_for_claim(claim["id"]),
        }
        for claim in SUPPORTED_CLAIMS
    ]


def allowed_wording_for_claim(claim_id: str) -> str:
    wording = {
        "hard_cohort_scope": (
            "We study a controlled 47-candidate hard-case cohort with hidden evaluator labels."
        ),
        "verdict_like_summary_dominance": (
            "With a visible verdict-like tool summary, both models reproduced the deterministic baseline."
        ),
        "evidence_only_partial_decoupling": (
            "Removing verdict-like fields changed decisions but did not produce strict corrections of known false accepts."
        ),
        "tool_contestation_risk_triage": (
            "Tool-contestation shifted known false accepts primarily from accept to escalation."
        ),
        "policy_utility_tradeoff": (
            "Under policies where false accepts are costly, contestation can be useful as a conservative triage layer."
        ),
    }
    return wording[claim_id]


def terminology_ledger() -> list[dict[str, str]]:
    return [
        {
            "term": "EVP-8-HARD",
            "definition": "The 47-candidate controlled hard-case cohort used in this branch.",
            "usage": "Use as cohort name, not as a general benchmark claim.",
        },
        {
            "term": "with-verdict",
            "definition": "The E6 setting where a verdict-like deterministic merge-gate summary is visible.",
            "usage": "Use for tool-dominance analysis.",
        },
        {
            "term": "evidence-only",
            "definition": "The ablation removing verdict-like fields while preserving lower-level visible evidence.",
            "usage": "Use for verdict removal analysis.",
        },
        {
            "term": "tool-contestation",
            "definition": "The prompt variant asking the model to challenge visible-test-only accept premises.",
            "usage": "Use for conservative risk-triage analysis.",
        },
        {
            "term": "strict correction",
            "definition": "Rejecting a known tool false accept.",
            "usage": "Do not conflate with escalation.",
        },
        {
            "term": "safe handling",
            "definition": "Rejecting or escalating a known tool false accept.",
            "usage": "Report separately from strict correction.",
        },
    ]


def paper_section_scaffold() -> list[dict[str, str]]:
    return [
        {
            "section": "Results 1: Tool-verdict dominance",
            "job": "Show that Qwen and DeepSeek match tool-only under with-verdict.",
            "primary_table": "whole_cohort_rows",
        },
        {
            "section": "Results 2: Verdict removal and tool-contestation",
            "job": "Show decision shifts after removing verdict fields and adding contestation.",
            "primary_table": "opportunity_set_rows",
        },
        {
            "section": "Results 3: Policy utility",
            "job": "Show when conservative escalation is useful and when automation recall is lost.",
            "primary_table": "utility_rows",
        },
        {
            "section": "Discussion",
            "job": "Interpret the result as risk triage, not autonomous verification.",
            "primary_table": "claim_traceability",
        },
    ]


def check(name: str, passed: bool, detail: Any = None) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def candidate_counts_consistent(*payloads: dict[str, Any]) -> bool:
    counts = []
    for payload in payloads:
        if "candidate_count" in payload:
            counts.append(payload["candidate_count"])
    return counts and all(count == 47 for count in counts)


def with_verdict_models_match_tool(full: dict[str, Any]) -> bool:
    tool_counts = full["tool_only_baseline"]["confusion"]["counts"]
    tool_decisions = full["tool_only_baseline"]["decision_counts"]
    for model_payload in full["models"].values():
        if model_payload["confusion"]["counts"] != tool_counts:
            return False
        if model_payload["decision_counts"] != tool_decisions:
            return False
    return True


def tool_contestation_strict_reject_zero(policy: dict[str, Any]) -> bool:
    summary = policy["case_analysis"]["opportunity_summary"]
    return (
        summary["qwen_tool_contestation"]["strict_reject_count"] == 0
        and summary["deepseek_tool_contestation"]["strict_reject_count"] == 0
    )


def render_traceability_md(trace: dict[str, Any]) -> str:
    lines = [
        "# EVP-8-HARD Paper Claim Traceability v0.1",
        "",
        trace["boundary"],
        "",
        "## Summary",
        "",
        f"- passed: {'yes' if trace['passed'] else 'no'}",
        "- API call attempted: no",
        "- raw outputs read: no",
        "- patch diffs read: no",
        "- prompt modified: no",
        "",
        "## One-Sentence Argument",
        "",
        trace["one_sentence_argument"],
        "",
        "## Terminology Ledger",
        "",
        "| term | definition | usage |",
        "|---|---|---|",
    ]
    for item in trace["terminology_ledger"]:
        lines.append(f"| `{item['term']}` | {item['definition']} | {item['usage']} |")
    lines.extend(["", "## Checks", "", "| check | passed | detail |", "|---|---:|---|"])
    for item in trace["checks"]:
        lines.append(f"| `{item['check']}` | {str(item['passed']).lower()} | `{json.dumps(item['detail'], ensure_ascii=False)}` |")
    lines.extend(["", "## Supported Claims", "", "| id | status | evidence sources | allowed wording |", "|---|---|---|---|"])
    for claim in trace["supported_claims"]:
        sources = ", ".join(f"`{source}`" for source in claim["evidence_sources"])
        lines.append(f"| `{claim['id']}` | {claim['status']} | {sources} | {claim['allowed_wording']} |")
    lines.extend(["", "## Qualified Claims", "", "| id | claim | condition |", "|---|---|---|"])
    for claim in trace["qualified_claims"]:
        lines.append(f"| `{claim['id']}` | {claim['claim']} | {claim['condition']} |")
    lines.extend(["", "## Forbidden Claims", "", "| id | forbidden claim | reason |", "|---|---|---|"])
    for claim in trace["forbidden_claims"]:
        lines.append(f"| `{claim['id']}` | {claim['claim']} | {claim['reason']} |")
    lines.extend(["", "## Paper Section Scaffold", "", "| section | job | primary table |", "|---|---|---|"])
    for item in trace["paper_section_scaffold"]:
        lines.append(f"| {item['section']} | {item['job']} | `{item['primary_table']}` |")
    lines.extend(
        [
            "",
            "## Linked Outputs",
            "",
            f"- Final table scaffold JSON: `{trace['linked_table_scaffold']['json']}`",
            f"- Final table scaffold Markdown: `{trace['linked_table_scaffold']['markdown']}`",
            "",
        ]
    )
    return "\n".join(lines)


def render_table_md(tables: dict[str, Any]) -> str:
    lines = [
        "# EVP-8-HARD Final Results Table Scaffold v0.1",
        "",
        "Generated from tracked aggregate audits only. This is a table scaffold for paper writing, not a new experiment.",
        "",
        "## Table 1. Whole-Cohort Decisions and Metrics",
        "",
        "| system | variant | model | accept | reject | escalate | true accept | false accept | accepted precision | correct recall | false accept rate | escalation rate | claim use |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in tables["whole_cohort_rows"]:
        lines.append(
            f"| `{row['system_id']}` | `{row['variant']}` | `{row['model']}` | "
            f"{row['accept']} | {row['reject']} | {row['escalate']} | "
            f"{row['true_accept']} | {row['false_accept']} | "
            f"{fmt_pct(row['accepted_precision'])} | {fmt_pct(row['correct_recall'])} | "
            f"{fmt_pct(row['false_accept_rate'])} | {fmt_pct(row['escalation_rate'])} | "
            f"{row['claim_use']} |"
        )
    lines.extend(
        [
            "",
            "## Table 2. Nine-Case Tool False-Accept Opportunity Set",
            "",
            "| system | variant | repeated accept | escalate | strict reject | safe handled | interpretation |",
            "|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in tables["opportunity_set_rows"]:
        lines.append(
            f"| `{row['system_id']}` | `{row['variant']}` | {row['repeated_accept']} | "
            f"{row['escalate']} | {row['strict_reject']} | {row['safe_handled']} | "
            f"{row['interpretation']} |"
        )
    lines.extend(
        [
            "",
            "## Table 3. Policy Utility Scenario Winners",
            "",
            "| scenario | best system | best score | false accept penalty | false reject penalty | escalation cost | claim use |",
            "|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in tables["utility_rows"]:
        lines.append(
            f"| `{row['scenario']}` | `{row['best_system']}` | {row['best_score']:.3f} | "
            f"{row['false_accept_penalty']:.2f} | {row['false_reject_penalty']:.2f} | "
            f"{row['escalation_cost']:.2f} | {row['claim_use']} |"
        )
    lines.extend(["", "## Sensitivity Winner Counts", "", "| winner | grid cells |", "|---|---:|"])
    for winner, count in sorted(
        tables["sensitivity_winner_counts"].items(), key=lambda item: (-item[1], item[0])
    ):
        lines.append(f"| `{winner}` | {count} |")
    lines.extend(["", "## Table Notes", ""])
    for note in tables["table_notes"]:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace-json", default=str(DEFAULT_TRACE_JSON))
    parser.add_argument("--trace-md", default=str(DEFAULT_TRACE_MD))
    parser.add_argument("--table-json", default=str(DEFAULT_TABLE_JSON))
    parser.add_argument("--table-md", default=str(DEFAULT_TABLE_MD))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    inputs = {
        "full": read_json(FULL_WITH_VERDICT_AUDIT),
        "evidence": read_json(EVIDENCE_ONLY_AUDIT),
        "contest": read_json(TOOL_CONTESTATION_AUDIT),
        "policy": read_json(POLICY_CASE_ANALYSIS),
        "stats": read_json(STATISTICAL_BOUNDARY),
    }
    raw_key_hits = {
        key: hits for key, value in inputs.items() if (hits := find_raw_like_keys(value))
    }
    tables = build_results_tables(
        inputs["full"], inputs["evidence"], inputs["contest"], inputs["policy"]
    )
    trace = build_claim_traceability(
        inputs["full"],
        inputs["evidence"],
        inputs["contest"],
        inputs["policy"],
        inputs["stats"],
        tables,
        raw_key_hits,
    )
    tables["validation"] = {
        "status": "passed" if trace["passed"] else "failed",
        "linked_claim_traceability": rel(DEFAULT_TRACE_JSON),
    }

    write_json(Path(args.trace_json), trace)
    write_text(Path(args.trace_md), render_traceability_md(trace))
    write_json(Path(args.table_json), tables)
    write_text(Path(args.table_md), render_table_md(tables))

    print(
        json.dumps(
            {
                "audit_id": trace["audit_id"],
                "passed": trace["passed"],
                "trace_json": args.trace_json,
                "trace_md": args.trace_md,
                "table_json": args.table_json,
                "table_md": args.table_md,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if trace["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
