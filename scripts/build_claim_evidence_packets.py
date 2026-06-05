from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path
from typing import Any

from cross_review.jsonl import read_jsonl, write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build evidence packets for manual/tool-backed claim-level validation."
    )
    parser.add_argument("--labels", required=True, help="Claim-labeling JSONL produced by build_claim_labeling_batch.py.")
    parser.add_argument(
        "--source-run",
        action="append",
        nargs=2,
        metavar=("RUN_ID", "SEED_DIR"),
        required=True,
        help="Source run id and seed directory containing generations.jsonl.",
    )
    parser.add_argument("--out", required=True, help="Evidence packet JSONL output.")
    parser.add_argument("--summary-out", required=True, help="Summary JSON output.")
    parser.add_argument("--markdown-dir", help="Optional directory for one Markdown evidence packet per claim.")
    args = parser.parse_args()

    source_generations = load_source_generations(args.source_run)
    claims = read_jsonl(args.labels)
    packets = [build_packet(claim, source_generations) for claim in claims]

    write_jsonl(args.out, packets)
    if args.markdown_dir:
        write_markdown_packets(Path(args.markdown_dir), packets)

    summary = summarize(packets)
    summary_path = Path(args.summary_out)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


def load_source_generations(source_runs: list[list[str]]) -> dict[str, dict[tuple[str, str], dict[str, Any]]]:
    by_run: dict[str, dict[tuple[str, str], dict[str, Any]]] = {}
    for run_id, seed_dir in source_runs:
        generations_path = Path(seed_dir) / "generations.jsonl"
        records = read_jsonl(generations_path)
        by_run[run_id] = {
            (str(record.get("task_id")), str(record.get("variant"))): record
            for record in records
            if record.get("task_id") and record.get("variant")
        }
    return by_run


def build_packet(
    claim: dict[str, Any],
    source_generations: dict[str, dict[tuple[str, str], dict[str, Any]]],
) -> dict[str, Any]:
    run_id = str(claim.get("source_run_id"))
    task_id = str(claim.get("task_id"))
    variant = str(claim.get("candidate_variant"))
    counterpart_variant = "fixed_control" if variant == "buggy" else "buggy"
    generation_lookup = source_generations.get(run_id, {})
    counterpart = generation_lookup.get((task_id, counterpart_variant))
    counterpart_excerpt = str(counterpart.get("code") if counterpart else "")
    source_excerpt = str(claim.get("source_excerpt") or "")

    return {
        "claim_label_id": claim.get("claim_label_id"),
        "source_run_id": run_id,
        "review_id": claim.get("review_id"),
        "project": claim.get("project"),
        "bug_id": claim.get("bug_id"),
        "task_id": task_id,
        "candidate_id": claim.get("candidate_id"),
        "candidate_variant": variant,
        "candidate_oracle_label": claim.get("candidate_oracle_label"),
        "oracle": claim.get("oracle"),
        "oracle_passed": claim.get("oracle_passed"),
        "reviewer": claim.get("reviewer"),
        "claim_location": claim.get("claim_location"),
        "claim_text": claim.get("claim_text"),
        "suggested_fix": claim.get("suggested_fix"),
        "target_behavior": claim.get("target_behavior"),
        "submitted_excerpt": source_excerpt,
        "counterpart_variant": counterpart_variant,
        "counterpart_excerpt_found": counterpart is not None,
        "counterpart_excerpt": counterpart_excerpt,
        "submitted_vs_counterpart_diff": unified_diff(
            source_excerpt,
            counterpart_excerpt,
            fromfile=f"{task_id}__{variant}",
            tofile=f"{task_id}__{counterpart_variant}",
        ),
        "labeling_fields_to_fill": {
            "primary_label": claim.get("primary_label", ""),
            "taxonomy_tags": claim.get("taxonomy_tags", []),
            "evidence_sources": claim.get("evidence_sources", []),
            "evidence_summary": claim.get("evidence_summary", ""),
            "needs_additional_context": claim.get("needs_additional_context"),
            "labeler": claim.get("labeler", ""),
            "label_date": claim.get("label_date", ""),
        },
    }


def unified_diff(source: str, counterpart: str, fromfile: str, tofile: str) -> str:
    if not counterpart:
        return ""
    diff_lines = difflib.unified_diff(
        source.splitlines(),
        counterpart.splitlines(),
        fromfile=fromfile,
        tofile=tofile,
        lineterm="",
        n=8,
    )
    return "\n".join(diff_lines)


def write_markdown_packets(markdown_dir: Path, packets: list[dict[str, Any]]) -> None:
    markdown_dir.mkdir(parents=True, exist_ok=True)
    for packet in packets:
        packet_id = str(packet["claim_label_id"])
        out_path = markdown_dir / f"{packet_id}.md"
        out_path.write_text(render_markdown(packet), encoding="utf-8", newline="\n")


def render_markdown(packet: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# Claim Evidence Packet: {packet['claim_label_id']}",
            "",
            "## Metadata",
            "",
            f"- Source run: `{packet['source_run_id']}`",
            f"- Review id: `{packet['review_id']}`",
            f"- Project: `{packet['project']}`",
            f"- Bug id: `{packet['bug_id']}`",
            f"- Candidate: `{packet['candidate_id']}`",
            f"- Candidate variant: `{packet['candidate_variant']}`",
            f"- Candidate oracle label: `{packet['candidate_oracle_label']}`",
            f"- Oracle passed: `{packet['oracle_passed']}`",
            f"- Reviewer: `{packet['reviewer']}`",
            "",
            "## Reviewer Claim",
            "",
            f"- Location: `{packet.get('claim_location')}`",
            "",
            str(packet.get("claim_text") or ""),
            "",
            "## Suggested Fix",
            "",
            str(packet.get("suggested_fix") or ""),
            "",
            "## Target Behavior",
            "",
            str(packet.get("target_behavior") or ""),
            "",
            "## Submitted vs Counterpart Diff",
            "",
            "```diff",
            str(packet.get("submitted_vs_counterpart_diff") or ""),
            "```",
            "",
            "## Labeling Fields To Fill",
            "",
            "```json",
            json.dumps(packet.get("labeling_fields_to_fill"), indent=2, sort_keys=True),
            "```",
            "",
            "## Submitted Excerpt",
            "",
            "```text",
            str(packet.get("submitted_excerpt") or ""),
            "```",
            "",
            "## Counterpart Excerpt",
            "",
            "```text",
            str(packet.get("counterpart_excerpt") or ""),
            "```",
            "",
        ]
    )


def summarize(packets: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "packets": len(packets),
        "packets_with_counterpart_excerpt": sum(1 for packet in packets if packet.get("counterpart_excerpt_found")),
        "packets_with_diff": sum(1 for packet in packets if packet.get("submitted_vs_counterpart_diff")),
        "by_candidate_variant": count_by(packets, "candidate_variant"),
        "by_reviewer": count_by(packets, "reviewer"),
        "by_source_run": count_by(packets, "source_run_id"),
    }


def count_by(records: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        value = str(record.get(key))
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


if __name__ == "__main__":
    main()
