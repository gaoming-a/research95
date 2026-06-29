from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_FRAMING = Path("docs/paper/sqj_submission_framing.md")
DEFAULT_DRAFT = Path("docs/paper/sqj_submission_draft.tex")
DEFAULT_SYNTHESIS = Path("data/protocols/evp8_five_model_synthesis_v0_1.json")
DEFAULT_COST = Path("data/reviews/evp8_cost_accounting_summary.json")
DEFAULT_FRESH_DECISION = Path("data/protocols/evp8_realistic_hardneg_paper_claim_decision_packet_v0_1.json")
DEFAULT_FRESH_GATE = Path("data/protocols/evp8_realistic_hardneg_combined_generation_gate_with_full_file_v0_1.json")
DEFAULT_JSON_OUT = Path("data/reviews/sqj_claim_traceability.json")
DEFAULT_MD_OUT = Path("docs/experiments/sqj_claim_traceability.md")

RAW_MARKERS = ("raw_" + "response", "provider_" + "response", "prompt_" + "text", "patch_" + "text")

SUPPORTED_CLAIMS = [
    {
        "id": "evidence_visibility_variable",
        "claim": "Evidence visibility is a first-order experimental variable for LLM-based patch verification.",
        "keyword_groups": [["evidence visibility", "first-order"], ["patch verification"]],
        "evidence_sources": ["evp8_synthesis"],
    },
    {
        "id": "frozen_evp8_scope",
        "claim": "The SQJ main result is a descriptive five-model EVP-8 study over 98 candidates and seven evidence levels.",
        "keyword_groups": [["98", "candidate"], ["evidence"], ["five", "model"]],
        "evidence_sources": ["evp8_synthesis"],
    },
    {
        "id": "non_monotonic_model_dependent",
        "claim": "The observed EVP-8 decision patterns are model-dependent and non-monotonic.",
        "keyword_groups": [["model-dependent"], ["non-monotonic"]],
        "evidence_sources": ["evp8_synthesis"],
    },
    {
        "id": "devstral_saturation_risk",
        "claim": "Devstral 2 saturation to escalation is a verifier reliability finding.",
        "keyword_groups": [["Devstral", "escalat"], ["saturat"]],
        "evidence_sources": ["evp8_synthesis"],
    },
    {
        "id": "blocked_kimi_cost_risk",
        "claim": "Blocked Kimi attempts are cost and execution-risk evidence only, not valid model-result records.",
        "keyword_groups": [["blocked Kimi"], ["cost"], ["not valid", "model-result"]],
        "evidence_sources": ["evp8_cost"],
    },
    {
        "id": "fresh_realistic_negative_result",
        "claim": "The fresh realistic branch is a two-project source-acquisition negative result, not a verifier-ready main experiment.",
        "keyword_groups": [["fresh realistic"], ["two-project"], ["negative result"]],
        "evidence_sources": ["fresh_decision", "fresh_gate"],
    },
]

FORBIDDEN_CLAIMS = [
    {
        "id": "llm_superiority",
        "claim": "LLM verifiers outperform deterministic visible-tool or test-based baselines.",
        "forbidden_phrases": [
            "LLM verifiers outperform deterministic",
            "LLM superiority over deterministic",
            "LLM outperforms deterministic",
        ],
    },
    {
        "id": "e6_general_optimal",
        "claim": "E6 is strictly or generally better than E4.",
        "forbidden_phrases": [
            "E6 is strictly better than E4",
            "E6 strictly improves over E4",
            "E6 is generally better than E4",
        ],
    },
    {
        "id": "monotonic_effectiveness_ranking",
        "claim": "Evidence levels establish a final monotonic effectiveness ranking.",
        "forbidden_phrases": [
            "final monotonic effectiveness ranking",
            "monotonic improvement from E0 to E6",
            "more evidence is always better",
        ],
    },
    {
        "id": "scale_generalization",
        "claim": "The 98-candidate EVP-8 set supports broad scale generalization.",
        "forbidden_phrases": [
            "supports broad scale generalization",
            "scale-generalizes beyond the frozen EVP-8",
            "universal ranking of evidence levels",
        ],
    },
    {
        "id": "fresh_verifier_ready",
        "claim": "The fresh realistic branch is a three-project verifier-ready main experiment.",
        "forbidden_phrases": [
            "three-project verifier-ready main experiment",
            "ready for Qwen or DeepSeek verifier API evaluation",
            "verifier-ready main experiment",
        ],
    },
    {
        "id": "practical_autonomous_verifier",
        "claim": "The full-file generation-interface repair validates practical autonomous patch verification.",
        "forbidden_phrases": [
            "practical autonomous patch verification",
            "validates the verifier system",
            "agent patch verifier is practically reliable",
        ],
    },
]


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def normalize(text: str) -> str:
    return " ".join(text.lower().replace("\\", " ").split())


def source_state(path: Path) -> dict[str, Any]:
    return {
        "path": path.as_posix(),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
    }


def keyword_group_present(text: str, keywords: list[str]) -> bool:
    normalized = normalize(text)
    return all(keyword.lower() in normalized for keyword in keywords)


def supported_claim_record(claim: dict[str, Any], framing: str, draft: str) -> dict[str, Any]:
    framing_groups = [keyword_group_present(framing, group) for group in claim["keyword_groups"]]
    draft_groups = [keyword_group_present(draft, group) for group in claim["keyword_groups"]]
    return {
        "id": claim["id"],
        "claim": claim["claim"],
        "evidence_sources": claim["evidence_sources"],
        "coverage": {
            "framing_keyword_groups": framing_groups,
            "draft_keyword_groups": draft_groups,
            "framing": all(framing_groups),
            "draft": all(draft_groups),
        },
        "passed": all(framing_groups) and all(draft_groups),
    }


def forbidden_claim_record(claim: dict[str, Any], framing: str, draft: str) -> dict[str, Any]:
    framing_norm = normalize(strip_forbidden_claims_section(framing))
    draft_norm = normalize(draft)
    hits = [
        phrase
        for phrase in claim["forbidden_phrases"]
        if positive_phrase_hit(framing_norm, phrase.lower()) or positive_phrase_hit(draft_norm, phrase.lower())
    ]
    return {
        "id": claim["id"],
        "claim": claim["claim"],
        "forbidden_phrases": claim["forbidden_phrases"],
        "hits": hits,
        "passed": not hits,
    }


def positive_phrase_hit(text: str, phrase: str) -> bool:
    start = 0
    while True:
        index = text.find(phrase, start)
        if index < 0:
            return False
        window = text[max(0, index - 90) : index]
        if not any(marker in window for marker in ["not ", "does not", "do not", "must not", "should not", "forbidden", "instead of"]):
            return True
        start = index + len(phrase)


def strip_forbidden_claims_section(text: str) -> str:
    marker = "## Forbidden Claims"
    index = text.find(marker)
    if index < 0:
        return text
    next_section = text.find("\n## ", index + len(marker))
    if next_section < 0:
        return text[:index]
    return text[:index] + text[next_section:]


def check(name: str, passed: bool, detail: Any = None) -> dict[str, Any]:
    return {"check": name, "passed": bool(passed), "detail": detail}


def audit_sqj_claim_traceability(
    framing_path: Path = DEFAULT_FRAMING,
    draft_path: Path = DEFAULT_DRAFT,
    synthesis_path: Path = DEFAULT_SYNTHESIS,
    cost_path: Path = DEFAULT_COST,
    fresh_decision_path: Path = DEFAULT_FRESH_DECISION,
    fresh_gate_path: Path = DEFAULT_FRESH_GATE,
) -> dict[str, Any]:
    framing = read_text(framing_path)
    draft = read_text(draft_path)
    synthesis = read_json(synthesis_path)
    cost = read_json(cost_path)
    fresh_decision = read_json(fresh_decision_path)
    fresh_gate = read_json(fresh_gate_path)

    supported = [supported_claim_record(claim, framing, draft) for claim in SUPPORTED_CLAIMS]
    forbidden = [forbidden_claim_record(claim, framing, draft) for claim in FORBIDDEN_CLAIMS]

    expected_levels = ["E0", "E1", "E2", "E3", "E4", "E5", "E6"]
    checks = [
        check("synthesis_passed", synthesis.get("synthesis_status") == "passed", synthesis.get("synthesis_status")),
        check("synthesis_no_api", synthesis.get("api_call_attempted") is False, synthesis.get("api_call_attempted")),
        check("synthesis_expected_models", len(synthesis.get("expected_model_ids", [])) == 5, synthesis.get("expected_model_ids", [])),
        check("synthesis_expected_levels", sorted((synthesis.get("per_level_decision_counts_by_model") or {}).keys()) == expected_levels),
        check("cost_passed", cost.get("passed") is True, cost.get("passed")),
        check("cost_api_freeze", (cost.get("decision") or {}).get("api_freeze") is True, (cost.get("decision") or {}).get("api_freeze")),
        check("blocked_attempts_not_model_results", "not valid model-result records" in cost.get("claim_boundary", "")),
        check("fresh_gate_failed_as_expected", (fresh_gate.get("hard_negative_gate") or {}).get("passed") is False),
        check("fresh_verifier_api_not_ready", (fresh_gate.get("readiness") or {}).get("ready_for_verifier_api") is False),
        check(
            "fresh_decision_downgraded",
            (fresh_decision.get("decision") or {}).get("paper_claim_status")
            == "downgrade_to_two_project_fresh_hard_negative_supplement_or_source_acquisition_negative_result",
            (fresh_decision.get("decision") or {}).get("paper_claim_status"),
        ),
        check("all_supported_claims_covered", all(record["passed"] for record in supported)),
        check("all_forbidden_claims_absent", all(record["passed"] for record in forbidden)),
    ]

    result = {
        "audit_id": "sqj_claim_traceability",
        "boundary": (
            "This audit maps SQJ manuscript claims to tracked raw-output-free evidence. "
            "It does not call model APIs, read raw model responses, infer new results, "
            "compile the manuscript, or mark final freeze complete."
        ),
        "inputs": {
            "framing": source_state(framing_path),
            "draft": source_state(draft_path),
            "evp8_synthesis": source_state(synthesis_path),
            "evp8_cost": source_state(cost_path),
            "fresh_decision": source_state(fresh_decision_path),
            "fresh_gate": source_state(fresh_gate_path),
        },
        "supported_claims": supported,
        "forbidden_claims": forbidden,
        "checks": checks,
        "api_call_attempted": False,
        "raw_outputs_read": False,
        "final_freeze_complete": False,
    }
    result["passed"] = all(item["passed"] for item in checks)
    result["raw_output_free_check"] = {
        "passed": not contains_raw_markers(result),
        "checked_for_raw_markers": True,
    }
    return result


def contains_raw_markers(value: Any) -> bool:
    serialized = json.dumps(value, ensure_ascii=False)
    return any(marker in serialized for marker in RAW_MARKERS)


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# SQJ Claim Traceability Audit",
        "",
        result["boundary"],
        "",
        "## Summary",
        "",
        f"- passed: {bool_mark(result['passed'])}",
        f"- raw-output-free check passed: {bool_mark(result['raw_output_free_check']['passed'])}",
        f"- API call attempted: {bool_mark(result['api_call_attempted'])}",
        f"- raw outputs read: {bool_mark(result['raw_outputs_read'])}",
        f"- final freeze complete: {bool_mark(result['final_freeze_complete'])}",
        "",
        "## Checks",
        "",
        "| check | passed | detail |",
        "|---|---:|---|",
    ]
    for item in result["checks"]:
        lines.append(f"| `{item['check']}` | {str(item['passed']).lower()} | `{json.dumps(item.get('detail'), ensure_ascii=False)}` |")
    lines.extend(
        [
            "",
            "## Supported Claims",
            "",
            "| id | framing | draft | evidence sources | claim |",
            "|---|---:|---:|---|---|",
        ]
    )
    for record in result["supported_claims"]:
        sources = ", ".join(f"`{source}`" for source in record["evidence_sources"])
        lines.append(
            f"| `{record['id']}` | {str(record['coverage']['framing']).lower()} | "
            f"{str(record['coverage']['draft']).lower()} | {sources} | {record['claim']} |"
        )
    lines.extend(
        [
            "",
            "## Forbidden Claims",
            "",
            "| id | absent | hits | claim |",
            "|---|---:|---|---|",
        ]
    )
    for record in result["forbidden_claims"]:
        lines.append(
            f"| `{record['id']}` | {str(record['passed']).lower()} | "
            f"`{json.dumps(record['hits'], ensure_ascii=False)}` | {record['claim']} |"
        )
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit SQJ claim-to-evidence traceability.")
    parser.add_argument("--framing", type=Path, default=DEFAULT_FRAMING)
    parser.add_argument("--draft", type=Path, default=DEFAULT_DRAFT)
    parser.add_argument("--synthesis", type=Path, default=DEFAULT_SYNTHESIS)
    parser.add_argument("--cost", type=Path, default=DEFAULT_COST)
    parser.add_argument("--fresh-decision", type=Path, default=DEFAULT_FRESH_DECISION)
    parser.add_argument("--fresh-gate", type=Path, default=DEFAULT_FRESH_GATE)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_MD_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = audit_sqj_claim_traceability(
        args.framing,
        args.draft,
        args.synthesis,
        args.cost,
        args.fresh_decision,
        args.fresh_gate,
    )
    write_json(args.out_json, result)
    write_text(args.out_md, render_markdown(result))
    print(json.dumps({"out_json": args.out_json.as_posix(), "out_md": args.out_md.as_posix(), "passed": result["passed"]}, indent=2))
    if not result["passed"] or not result["raw_output_free_check"]["passed"]:
        raise SystemExit(1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
