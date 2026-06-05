from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from cross_review.env import load_env_file  # noqa: E402
from cross_review.jsonl import read_jsonl, write_jsonl  # noqa: E402
from cross_review.openrouter import DeepSeekClient, OpenRouterClient, redact_sensitive_text  # noqa: E402
from cross_review.parsing import extract_json_object, response_text  # noqa: E402

import analyze_patch_verification as metrics_module  # noqa: E402


PROMPT_VERSIONS = {
    "llm_only": "patch_verify_llm_only_v1",
    "evidence_first": "patch_verify_evidence_first_v1",
    "tool_augmented_evidence": "patch_verify_tool_augmented_evidence_v1",
}
DEFAULT_TEMPERATURE = 0.0
DEFAULT_MAX_TOKENS = 4096

FORBIDDEN_RENDERED_PROMPT_TOKENS = [
    "expected_outcome",
    "candidate_type",
    "patch_materialization",
    "hidden_oracles",
    "oracle_command",
    "oracle_workdir",
    "construction_notes",
    "label_confidence",
]


def render_prompt(condition: str, evidence_packet: dict[str, Any]) -> str:
    if condition == "llm_only":
        return "\n".join(
            [
                "You are reviewing a proposed software patch.",
                "",
                "Decide whether the patch should be accepted, rejected, or escalated for human/tool verification.",
                "",
                "Use only the task context and patch text below. Do not assume hidden tests or oracle results.",
                "Return exactly one JSON object with fields: decision, confidence, claims, rationale, uncertainty.",
                "",
                "Decision policy:",
                "- Accept only if the patch clearly addresses the task behavior and no visible contradiction exists.",
                "- Reject if the patch is empty, unrelated, internally inconsistent, or visibly fails to address the behavior.",
                "- Escalate if the patch may be plausible but the visible evidence is insufficient.",
                "",
                f"Task:\n{evidence_packet['task_summary']}",
                "",
                f"Visible context:\n{evidence_packet['visible_context']}",
                "",
                f"Candidate patch:\n{evidence_packet['patch_text']}",
            ]
        )
    if condition == "evidence_first":
        return "\n".join(
            [
                "You are performing evidence-first verification of a proposed software patch.",
                "",
                "Decide whether the patch should be accepted, rejected, or escalated for human/tool verification.",
                "",
                "You must tie every accept/reject decision to concrete visible evidence.",
                "Do not assume hidden labels, hidden tests, or oracle results.",
                "Return exactly one JSON object with fields: decision, confidence, claims, rationale, uncertainty.",
                "",
                "Decision policy:",
                "- Accept only if the patch's correctness claim is directly supported by the visible patch diff and task context.",
                "- Reject if the patch is empty, unrelated, internally inconsistent, or contradicts the required behavior.",
                "- Escalate if visible evidence is insufficient to verify the correctness claim.",
                "",
                f"Task:\n{evidence_packet['task_summary']}",
                "",
                f"Visible context:\n{evidence_packet['visible_context']}",
                "",
                f"Candidate patch:\n{evidence_packet['patch_text']}",
                "",
                "Available evidence sources:",
                json.dumps(evidence_packet["available_evidence_sources"], ensure_ascii=False),
                "",
                "Visible tests or behavioral hints:",
                json.dumps(evidence_packet["visible_tests"], ensure_ascii=False),
            ]
        )
    if condition == "tool_augmented_evidence":
        return "\n".join(
            [
                "You are performing tool-augmented verification of a proposed software patch.",
                "",
                "Decide whether the patch should be accepted, rejected, or escalated for human/tool verification.",
                "",
                "You may use only the visible task context, candidate patch, patch-apply status, and tool/oracle execution summary below.",
                "Do not assume hidden labels or evaluator annotations.",
                "Return exactly one JSON object with fields: decision, confidence, claims, rationale, uncertainty.",
                "",
                "Decision policy:",
                "- Accept if the patch applies, relevant tool/oracle evidence supports the behavior, and no visible contradiction remains.",
                "- Reject if the patch does not apply, tool/oracle evidence contradicts the behavior, the patch is unrelated, or required behavior is visibly missing.",
                "- Escalate if tool evidence is incomplete, ambiguous, or insufficient to decide.",
                "",
                f"Task:\n{evidence_packet['task_summary']}",
                "",
                f"Visible context:\n{evidence_packet['visible_context']}",
                "",
                f"Candidate patch:\n{evidence_packet['patch_text']}",
                "",
                "Tool evidence:",
                json.dumps(evidence_packet["tool_evidence_summary"], ensure_ascii=False, indent=2, sort_keys=True),
                "",
                "Visible tests or behavioral hints:",
                json.dumps(evidence_packet["visible_tests"], ensure_ascii=False),
            ]
        )
    raise ValueError(f"unsupported condition: {condition}")


def check_rendered_prompt(prompt: str) -> None:
    hits = [token for token in FORBIDDEN_RENDERED_PROMPT_TOKENS if token in prompt]
    if hits:
        raise ValueError(f"rendered prompt contains forbidden evaluator tokens: {hits}")


def normalize_model_output(parsed: dict[str, Any]) -> tuple[str, float, list[dict[str, Any]], str | None]:
    decision = str(parsed.get("decision", "")).strip().lower()
    if decision not in {"accept", "reject", "escalate"}:
        return "invalid_output", 0.0, [], f"invalid decision: {decision}"
    try:
        confidence = float(parsed.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))
    claims_raw = parsed.get("claims", [])
    claims: list[dict[str, Any]] = []
    if isinstance(claims_raw, list):
        for index, claim in enumerate(claims_raw, start=1):
            if not isinstance(claim, dict):
                continue
            claims.append(
                {
                    "claim_id": f"claim_{index:03d}",
                    "claim": str(claim.get("claim", "")),
                    "evidence": claim.get("evidence", []),
                    "evidence_status": str(claim.get("evidence_status", "insufficient")),
                }
            )
    return decision, confidence, claims, None


def raw_response_path(out_dir: Path, condition: str, model_slug: str, candidate_id: str) -> Path:
    safe_model = re.sub(r"[^A-Za-z0-9_.-]+", "_", model_slug)
    return out_dir / "raw" / condition / safe_model / f"{candidate_id}.json"


def write_raw(path: Path, response: dict[str, Any]) -> dict[str, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(response, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path.write_text(content, encoding="utf-8")
    return {
        "path": path.as_posix(),
        "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
    }


def write_run_error(
    out_dir: Path,
    args: argparse.Namespace,
    evidence_packet: dict[str, Any],
    condition: str,
    records_completed: int,
    exc: Exception,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "run_error.json"
    error = {
        "stage": "api_call",
        "model": args.model,
        "condition": condition,
        "candidate_id": evidence_packet.get("candidate_id"),
        "records_completed": records_completed,
        "error_type": type(exc).__name__,
        "error": redact_sensitive_text(str(exc)),
        "run_date_utc": datetime.now(timezone.utc).isoformat(),
        "partial_reviews_path": (out_dir / "reviews.jsonl").as_posix(),
        "note": "This run is incomplete and must not be used as an experiment result until rerun successfully.",
    }
    path.write_text(json.dumps(error, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def build_review_record(
    candidate: dict[str, Any],
    evidence_packet: dict[str, Any],
    condition: str,
    model: str,
    api_provider: str,
    response: dict[str, Any],
    raw_path: str,
    raw_sha256: str,
) -> dict[str, Any]:
    text = response_text(response)
    try:
        parsed = extract_json_object(text)
        decision, confidence, claims, invalid_reason = normalize_model_output(parsed)
    except Exception as exc:  # noqa: BLE001
        decision, confidence, claims, invalid_reason = "invalid_output", 0.0, [], str(exc)
    usage = response.get("usage", {})
    cost = usage.get("cost", 0.0) if isinstance(usage, dict) else 0.0
    try:
        cost_usd = float(cost or 0.0)
    except (TypeError, ValueError):
        cost_usd = 0.0
    return {
        "patch_id": candidate["patch_id"],
        "model_candidate_id": evidence_packet["candidate_id"],
        "verifier_id": f"{condition}__{re.sub(r'[^A-Za-z0-9_.-]+', '_', model)}",
        "condition": condition,
        "decision": decision,
        "confidence": confidence,
        "claims": claims,
        "raw_response_path": raw_path,
        "raw_response_sha256": raw_sha256,
        "cost_usd": cost_usd,
        "invalid_reason": invalid_reason,
        "model": model,
        "api_provider": api_provider,
        "prompt_version": PROMPT_VERSIONS[condition],
        "run_date_utc": datetime.now(timezone.utc).isoformat(),
        "usage": usage,
    }


def run_reviews(args: argparse.Namespace) -> list[dict[str, Any]]:
    load_env_file(args.env)
    candidates = read_jsonl(args.candidates)
    evidence_packets = read_jsonl(args.evidence_packets)
    candidates_by_model_id = {candidate["model_candidate_id"]: candidate for candidate in candidates}
    out_dir = Path(args.out_dir)
    client = build_client(args.api_provider)
    records: list[dict[str, Any]] = []
    selected_packets = evidence_packets[: args.limit] if args.limit else evidence_packets
    for evidence_packet in selected_packets:
        candidate = candidates_by_model_id[evidence_packet["candidate_id"]]
        for condition in args.conditions:
            prompt = render_prompt(condition, evidence_packet)
            check_rendered_prompt(prompt)
            try:
                response = client.chat_completion(
                    model=args.model,
                    prompt=prompt,
                    temperature=args.temperature,
                    max_tokens=args.max_tokens,
                )
            except Exception as exc:  # noqa: BLE001
                error_path = write_run_error(out_dir, args, evidence_packet, condition, len(records), exc)
                if records:
                    write_jsonl(out_dir / "reviews.jsonl", records)
                raise SystemExit(
                    f"API run stopped before completion; see {error_path.as_posix()} for sanitized details."
                )
            raw = write_raw(
                raw_response_path(out_dir, condition, args.model, evidence_packet["candidate_id"]),
                response,
            )
            records.append(
                build_review_record(
                    candidate=candidate,
                    evidence_packet=evidence_packet,
                    condition=condition,
                    model=args.model,
                    api_provider=args.api_provider,
                    response=response,
                    raw_path=raw["path"],
                    raw_sha256=raw["sha256"],
                )
            )
            write_jsonl(out_dir / "reviews.jsonl", records)
    return records


def mock_decision(policy: str, condition: str, evidence_packet: dict[str, Any]) -> str:
    patch_text = str(evidence_packet["patch_text"])
    has_hunk = "@@" in patch_text
    if policy == "accept_all":
        return "accept"
    if policy == "reject_all":
        return "reject"
    if policy == "escalate_all":
        return "escalate"
    if policy == "patch_surface":
        if not has_hunk:
            return "reject"
        return "escalate" if condition == "evidence_first" else "accept"
    raise ValueError(f"unsupported mock policy: {policy}")


def mock_response(policy: str, condition: str, evidence_packet: dict[str, Any]) -> dict[str, Any]:
    decision = mock_decision(policy, condition, evidence_packet)
    content = {
        "decision": decision,
        "confidence": 0.5,
        "claims": [
            {
                "claim": "Mock reviewer output generated for pipeline validation only.",
                "evidence": ["mock_policy", policy],
                "evidence_status": "insufficient",
            }
        ],
        "rationale": "This is not a model decision and must not be reported as an experiment result.",
        "uncertainty": "mock output",
    }
    return {
        "choices": [{"message": {"content": json.dumps(content, ensure_ascii=False)}}],
        "usage": {"cost": 0.0, "mock": True},
        "mock_policy": policy,
    }


def run_mock_reviews(args: argparse.Namespace) -> list[dict[str, Any]]:
    candidates = read_jsonl(args.candidates)
    evidence_packets = read_jsonl(args.evidence_packets)
    candidates_by_model_id = {candidate["model_candidate_id"]: candidate for candidate in candidates}
    out_dir = Path(args.out_dir)
    records: list[dict[str, Any]] = []
    selected_packets = evidence_packets[: args.limit] if args.limit else evidence_packets
    model = f"mock::{args.mock_policy}"
    for evidence_packet in selected_packets:
        candidate = candidates_by_model_id[evidence_packet["candidate_id"]]
        for condition in args.conditions:
            prompt = render_prompt(condition, evidence_packet)
            check_rendered_prompt(prompt)
            response = mock_response(args.mock_policy, condition, evidence_packet)
            raw = write_raw(
                raw_response_path(out_dir, condition, model, evidence_packet["candidate_id"]),
                response,
            )
            record = build_review_record(
                candidate=candidate,
                evidence_packet=evidence_packet,
                condition=condition,
                model=model,
                api_provider="mock",
                response=response,
                raw_path=raw["path"],
                raw_sha256=raw["sha256"],
            )
            record["mock_run"] = True
            record["mock_policy"] = args.mock_policy
            records.append(record)
            write_jsonl(out_dir / "reviews.jsonl", records)
    return records


def render_prompt_manifest(args: argparse.Namespace) -> list[dict[str, Any]]:
    candidates = read_jsonl(args.candidates)
    evidence_packets = read_jsonl(args.evidence_packets)
    candidates_by_model_id = {candidate["model_candidate_id"]: candidate for candidate in candidates}
    selected_packets = evidence_packets[: args.limit] if args.limit else evidence_packets
    records: list[dict[str, Any]] = []
    for evidence_packet in selected_packets:
        candidate = candidates_by_model_id[evidence_packet["candidate_id"]]
        for condition in args.conditions:
            prompt = render_prompt(condition, evidence_packet)
            check_rendered_prompt(prompt)
            records.append(
                {
                    "candidate_id": evidence_packet["candidate_id"],
                    "patch_id": candidate["patch_id"],
                    "task_id": candidate["task_id"],
                    "condition": condition,
                    "prompt_version": PROMPT_VERSIONS[condition],
                    "model": args.model or "dry_run_model_unset",
                    "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                    "prompt_chars": len(prompt),
                    "label_leakage_check": "passed",
                }
            )
    return records


def write_metrics(path: Path, candidates_path: Path, records: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = metrics_module.read_jsonl(candidates_path)
    metrics = metrics_module.analyze(candidates, records)
    metrics_module.write_json(path, metrics)
    return metrics


def write_run_summary(
    path: Path,
    args: argparse.Namespace,
    records: list[dict[str, Any]],
    metrics_path: Path | None = None,
) -> None:
    invalid = sum(1 for record in records if record["decision"] == "invalid_output")
    cost = sum(float(record.get("cost_usd") or 0.0) for record in records)
    mock_records = sum(1 for record in records if record.get("mock_run"))
    model_label = f"mock::{args.mock_policy}" if args.mock_policy else (args.model or "unset")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# Patch Verification API Pilot Run",
                "",
                f"- model: `{model_label}`",
                f"- api provider: `{args.api_provider}`",
                f"- conditions: `{', '.join(args.conditions)}`",
                f"- records: {len(records)}",
                f"- invalid outputs: {invalid}",
                f"- recorded cost usd: {cost:.6f}",
                f"- temperature: {args.temperature}",
                f"- max tokens: {args.max_tokens}",
                f"- prompt versions: `{', '.join(PROMPT_VERSIONS[c] for c in args.conditions)}`",
                f"- metrics: `{metrics_path.as_posix() if metrics_path else 'not generated'}`",
                f"- mock records: {mock_records}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the small patch-verification API pilot.")
    parser.add_argument("--config", help="Optional API pilot config JSON.")
    parser.add_argument("--candidates")
    parser.add_argument("--evidence-packets")
    parser.add_argument("--out-dir")
    parser.add_argument("--model", help="Concrete model id. Required unless --dry-run is used.")
    parser.add_argument(
        "--api-provider",
        choices=["openrouter", "deepseek_official"],
        default=None,
        help="API provider for real model calls.",
    )
    parser.add_argument("--conditions", nargs="+", choices=sorted(PROMPT_VERSIONS), default=None)
    parser.add_argument("--temperature", type=float)
    parser.add_argument("--max-tokens", type=int)
    parser.add_argument("--limit", type=int, default=None, help="Optional candidate limit. Use 0 for a full run.")
    parser.add_argument("--env", default=".env", help="Untracked env file containing the selected provider API key.")
    parser.add_argument("--metrics-out", help="Metrics JSON output. Defaults to <out-dir>/metrics.json.")
    parser.add_argument(
        "--mock-policy",
        choices=["accept_all", "reject_all", "escalate_all", "patch_surface"],
        help="Generate local mock reviewer outputs for pipeline validation without calling model APIs.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Render prompts and validate prompt boundaries without calling model APIs.",
    )
    parser.add_argument(
        "--allow-direct-api-run",
        action="store_true",
        help="Internal guard used by run_api_pilot_workflow.py before real API calls.",
    )
    args = parser.parse_args()
    apply_config(args)
    apply_defaults(args)
    require_runtime_args(args)
    return args


def apply_defaults(args: argparse.Namespace) -> None:
    if args.conditions is None:
        args.conditions = ["llm_only", "evidence_first"]
    if args.temperature is None:
        args.temperature = DEFAULT_TEMPERATURE
    if args.max_tokens is None:
        args.max_tokens = DEFAULT_MAX_TOKENS


def apply_config(args: argparse.Namespace) -> None:
    if not args.config:
        return
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError(f"{args.config} must contain a JSON object")
    mapping = {
        "candidates": "candidates",
        "evidence_packets": "evidence_packets",
        "out_dir": "out_dir",
        "model": "model",
        "conditions": "conditions",
        "temperature": "temperature",
        "max_tokens": "max_tokens",
        "env": "env",
        "metrics_out": "metrics_out",
        "mock_policy": "mock_policy",
        "api_provider": "api_provider",
    }
    for key, attr in mapping.items():
        if getattr(args, attr) in (None, [], 0) and key in config:
            setattr(args, attr, config[key])
    if args.limit is None and config.get("smoke_limit") is not None and not args.dry_run:
        args.limit = int(config["smoke_limit"])


def require_runtime_args(args: argparse.Namespace) -> None:
    if not args.api_provider:
        args.api_provider = "openrouter"
    missing = [
        name
        for name in ("candidates", "evidence_packets", "out_dir")
        if not getattr(args, name)
    ]
    if missing:
        raise SystemExit(f"missing required arguments: {', '.join('--' + name.replace('_', '-') for name in missing)}")


def build_client(api_provider: str) -> OpenRouterClient | DeepSeekClient:
    if api_provider == "openrouter":
        return OpenRouterClient()
    if api_provider == "deepseek_official":
        return DeepSeekClient()
    raise SystemExit(f"unsupported api provider: {api_provider}")


def main() -> None:
    args = parse_args()
    if args.dry_run:
        records = render_prompt_manifest(args)
        out_dir = Path(args.out_dir)
        write_jsonl(out_dir / "prompt_manifest.jsonl", records)
        print(
            json.dumps(
                {
                    "dry_run": True,
                    "prompt_records": len(records),
                    "out": str(out_dir / "prompt_manifest.jsonl"),
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
        return
    if args.mock_policy:
        records = run_mock_reviews(args)
        metrics_path = Path(args.metrics_out) if args.metrics_out else Path(args.out_dir) / "metrics.json"
        write_metrics(metrics_path, Path(args.candidates), records)
        write_run_summary(Path(args.out_dir) / "run_summary.md", args, records, metrics_path)
        print(
            json.dumps(
                {
                    "mock_run": True,
                    "records": len(records),
                    "out_dir": args.out_dir,
                    "mock_policy": args.mock_policy,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    if not args.model:
        raise SystemExit("--model is required unless --dry-run is used")
    if not args.allow_direct_api_run:
        raise SystemExit(
            "Direct real API execution is disabled. Use scripts/run_api_pilot_workflow.py, "
            "which performs strict preflight, check-only gating, output overwrite checks, "
            "postprocess, and run-completeness auditing."
        )
    records = run_reviews(args)
    metrics_path = Path(args.metrics_out) if args.metrics_out else Path(args.out_dir) / "metrics.json"
    write_metrics(metrics_path, Path(args.candidates), records)
    write_run_summary(Path(args.out_dir) / "run_summary.md", args, records, metrics_path)
    print(json.dumps({"records": len(records), "out_dir": args.out_dir}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
