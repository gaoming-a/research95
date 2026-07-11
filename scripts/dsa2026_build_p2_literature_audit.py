"""Build the P2 nearest-neighbor matrix, search log, HTML, and final RIS."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CROSSREF_JSON = ROOT / "docs/literature/dsa_p2_nearest_neighbor_browser_v0_1/dsa_p2_nearest_neighbor_references_v0_1.json"
RIS_OUT = ROOT / "docs/literature/dsa_p2_nearest_neighbor_references_v0_1.ris"
MATRIX_OUT = ROOT / "docs/literature/dsa_p2_nearest_neighbor_matrix_v0_1.md"
HTML_OUT = ROOT / "docs/literature/dsa_p2_nearest_neighbor_matrix_v0_1.html"
LOG_OUT = ROOT / "data/protocols/dsa_p2_literature_search_log_v0_1.json"

MANUAL_ARXIV = [
    {
        "title": "PatchZero: Zero-Shot Automatic Patch Correctness Assessment",
        "authors": ["Zhou, Xin", "Xu, Bowen", "Kim, Kisub", "Han, DongGyun", "Le-Cong, Thanh", "He, Junda", "Le, Bach", "Lo, David"],
        "year": "2023",
        "doi": "10.48550/arXiv.2303.00202",
        "url": "https://arxiv.org/abs/2303.00202",
        "journal": "arXiv",
    },
    {
        "title": "Evaluating Large Language Models for Code Review",
        "authors": ["Cihan, Umut", "İçöz, Arda", "Haratian, Vahid", "Tüzün, Eray"],
        "year": "2025",
        "doi": "10.48550/arXiv.2505.20206",
        "url": "https://arxiv.org/abs/2505.20206",
        "journal": "arXiv",
    },
    {
        "title": "SWE-PRBench: Benchmarking AI Code Review Quality Against Pull Request Feedback",
        "authors": ["Kumar, Deepak"],
        "year": "2026",
        "doi": "10.48550/arXiv.2603.26130",
        "url": "https://arxiv.org/abs/2603.26130",
        "journal": "arXiv",
    },
]

ASSESSMENTS = {
    "10.1109/tse.2024.3452252": {
        "short": "LLM4PatchCorrect",
        "task": "binary APCA for patches from unseen repair tools",
        "evidence": "bug description, execution trace, failing tests, coverage, and labeled similar patches",
        "output": "correct/incorrect prediction",
        "overlap": "high",
        "support": "partial support",
        "difference": "does not isolate cumulative real evidence on the same patch and does not study accept/reject/escalate policy",
    },
    "10.1109/icst60714.2024.00036": {
        "short": "FixCheck",
        "task": "generate fault-revealing tests for suspected incorrect patches",
        "evidence": "random testing plus LLM-generated tests",
        "output": "new tests exposing patch faults",
        "overlap": "medium",
        "support": "partial support",
        "difference": "uses LLMs to create oracles rather than measuring a fixed reviewer's response to accumulated evidence",
    },
    "10.1145/3533767.3534368": {
        "short": "Shibboleth",
        "task": "static/dynamic APCA ranking and classification",
        "evidence": "production-code similarity and passing-test coverage impact",
        "output": "ranking and binary correctness class",
        "overlap": "medium",
        "support": "partial support",
        "difference": "not an LLM evidence-visibility intervention and not a triage policy study",
    },
    "10.1007/s10664-020-09920-w": {
        "short": "RGT at scale",
        "task": "assess overfitting patches with generated tests",
        "evidence": "random tests derived from the human patch as oracle",
        "output": "overfitting assessment",
        "overlap": "foundation",
        "support": "background support",
        "difference": "establishes independent-test labeling rather than LLM evidence-conditioned decisions",
    },
    "10.1109/icse.2019.00064": {
        "short": "Annotation reliability",
        "task": "compare independent-test and author correctness labels",
        "evidence": "professional-developer gold labels and independent test suites",
        "output": "label reliability",
        "overlap": "foundation",
        "support": "strong support",
        "difference": "supports the hidden-evaluator boundary but does not evaluate LLM review",
    },
    "10.1145/3368089.3417943": {
        "short": "BugsInPy",
        "task": "Python real-bug benchmark",
        "evidence": "buggy/fixed commits and bug-revealing tests",
        "output": "controlled testing/debugging dataset",
        "overlap": "foundation",
        "support": "strong support",
        "difference": "dataset source, not a patch-review method",
    },
    "10.1109/scam59687.2023.00036": {
        "short": "BugsInPy reproduction",
        "task": "reproduce and repair benchmark environments",
        "evidence": "original virtualenv and improved Conda/Docker executions",
        "output": "reproducibility results and improved framework",
        "overlap": "foundation",
        "support": "strong support",
        "difference": "directly constrains source feasibility but not the LLM research question",
    },
    "10.1007/s10515-026-00638-5": {
        "short": "Requirement-conformance review",
        "task": "LLM judgment of code against natural-language requirements",
        "evidence": "prompt variants and executable counterfactual verification filter",
        "output": "binary conformance judgment and overcorrection analysis",
        "overlap": "high",
        "support": "partial support",
        "difference": "tests prompt complexity and a fix-guided filter, not a cumulative executable evidence ladder on real patches",
    },
    "10.18653/v1/2026.acl-long.888": {
        "short": "CodeJudgeBench",
        "task": "robustness of LLM judges for generation, repair, and unit tests",
        "evidence": "candidate responses and code-specific perturbations",
        "output": "comparative judgment robustness",
        "overlap": "high",
        "support": "partial support",
        "difference": "judge robustness benchmark without real executable C0-C3 evidence accumulation or merge triage",
    },
    "10.48550/arxiv.2303.00202": {
        "short": "PatchZero",
        "task": "zero-shot APCA for unseen repair tools",
        "evidence": "code-model representation plus semantically similar labeled patches",
        "output": "binary correctness prediction",
        "overlap": "high",
        "support": "partial support",
        "difference": "static transfer/classification setting rather than within-patch executable-evidence intervention",
    },
    "10.48550/arxiv.2505.20206": {
        "short": "LLM code-review evaluation",
        "task": "classify and improve HumanEval-style code",
        "evidence": "code with or without problem descriptions",
        "output": "correct/incorrect classification and suggested repair",
        "overlap": "medium",
        "support": "partial support",
        "difference": "problem-description ablation on function tasks, not real patches or executable evidence levels",
    },
    "10.48550/arxiv.2603.26130": {
        "short": "SWE-PRBench",
        "task": "detect issues matching human pull-request feedback",
        "evidence": "diff, file content, or full structured context",
        "output": "issue-detection quality",
        "overlap": "high",
        "support": "partial support",
        "difference": "context-volume ablation without a pass/fail test oracle or accept/reject/escalate patch gate",
    },
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def ris_record(record: dict[str, Any]) -> str:
    lines = ["TY  - JOUR", f"TI  - {record['title']}"]
    lines.extend(f"AU  - {author}" for author in record["authors"])
    lines.extend(
        [
            f"T2  - {record['journal']}",
            f"PY  - {record['year']}",
            f"DO  - {record['doi']}",
            f"UR  - {record['url']}",
            "N1  - Abstract checked on the official arXiv page for the P2 nearest-neighbor audit.",
            "ER  -",
        ]
    )
    return "\n".join(lines)


def build_records() -> list[dict[str, Any]]:
    crossref = read_json(CROSSREF_JSON)
    records = [
        {
            "title": item["title"],
            "authors": item["authors"],
            "year": item["year"],
            "doi": item["doi"],
            "url": item["doi_url"],
            "journal": item["journal"],
            "ris_record": item["ris_record"],
        }
        for item in crossref["references"]
    ]
    records.extend({**item, "ris_record": ris_record(item)} for item in MANUAL_ARXIV)
    for record in records:
        key = record["doi"].lower()
        if key not in ASSESSMENTS:
            raise ValueError(f"missing assessment for {key}")
        record["assessment"] = ASSESSMENTS[key]
    return sorted(records, key=lambda record: (record["year"], record["title"]))


def build_log(records: list[dict[str, Any]]) -> dict[str, Any]:
    exact_matches = [
        record for record in records
        if "cumulative executable evidence" in record["assessment"]["task"].lower()
        and "accept/reject/escalate" in record["assessment"]["output"].lower()
    ]
    return {
        "search_id": "dsa_p2_literature_search_log_v0_1",
        "search_date": "2026-07-11",
        "publication_window": {"from_year": 2018, "to_year": 2026},
        "language": "English queries; Chinese evidence notes",
        "scope_note": "The citation helper's strict CNS scope is not suitable for software-engineering nearest neighbors. Explicit DOI export and official IEEE/ACM/ACL/arXiv/Springer or institutional pages were used.",
        "query_families": [
            "LLM automatic patch correctness assessment execution trace failing tests coverage",
            "LLM code review correctness context ablation executable tests",
            "LLM-as-a-judge code repair robustness benchmark",
            "BugsInPy reproducibility Docker Conda",
        ],
        "source_policy": "primary paper, publisher/proceedings page, official arXiv or author/institution page; discovery aggregators not used as sole evidence",
        "reference_count": len(records),
        "crossref_export_count": len(records) - len(MANUAL_ARXIV),
        "manual_arxiv_recovery_count": len(MANUAL_ARXIV),
        "crossref_retrieval_errors_recovered": [record["doi"] for record in MANUAL_ARXIV],
        "exact_design_match_found": bool(exact_matches),
        "positioning_gate_passed": not exact_matches and sum(record["assessment"]["overlap"] == "high" for record in records) >= 3,
        "allowed_positioning": "A controlled finite-cohort study of how cumulative real executable evidence changes fixed-LLM patch-gating policy; not a first/unique/SOTA claim and not APCA correctness proof.",
        "records": [
            {
                "title": record["title"],
                "year": record["year"],
                "doi": record["doi"],
                "url": record["url"],
                "abstract_or_full_page_checked": True,
                **record["assessment"],
            }
            for record in records
        ],
    }


def render_markdown(records: list[dict[str, Any]], log: dict[str, Any]) -> str:
    lines = [
        "# DSA 2026 P2 Nearest-Neighbor Literature Matrix v0.1",
        "",
        "检索日期：2026-07-11；时间窗：2018--2026。",
        "",
        "## 定位结论",
        "",
        "没有发现同时满足以下全部条件的直接设计：同一真实补丁、C0--C3 累积真实可执行证据、固定 LLM、",
        "accept/reject/escalate 三分类、task-level paired effect。最接近的是 LLM4PatchCorrect、PatchZero、",
        "SWE-PRBench、CodeJudgeBench 和 requirement-conformance review；它们必须在 Related Work 中正面区分。",
        "",
        "允许的定位是 `controlled finite-cohort evidence-conditioned patch-gating study`。禁止写 first、unique、SOTA、",
        "autonomous correctness verification 或 LLM superiority。",
        "",
        "## 最近邻矩阵",
        "",
        "| 工作 | 任务 | 输入/证据 | 输出 | 重叠 | 支撑等级 | 与本研究的关键差异 |",
        "|---|---|---|---|---|---|---|",
    ]
    for record in records:
        assessment = record["assessment"]
        link = f"[{assessment['short']}]({record['url']})"
        lines.append(
            f"| {link} | {assessment['task']} | {assessment['evidence']} | {assessment['output']} | "
            f"{assessment['overlap']} | {assessment['support']} | {assessment['difference']} |"
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            f"- exact design match found: `{str(log['exact_design_match_found']).lower()}`",
            f"- positioning gate passed: `{str(log['positioning_gate_passed']).lower()}`",
            "- 每篇均已检查官方摘要或全文页面；Crossref 只用于元数据，不单独作为内容支撑。",
            "- 三个 arXiv DOI 的 Crossref 404 已从 arXiv 官方页面恢复，并保留在 search log。",
            "",
        ]
    )
    return "\n".join(lines)


def render_html(records: list[dict[str, Any]], log: dict[str, Any]) -> str:
    rows = []
    for record in records:
        a = record["assessment"]
        rows.append(
            "<tr>"
            f"<td><a href='{html.escape(record['url'])}'>{html.escape(a['short'])}</a></td>"
            f"<td>{html.escape(record['year'])}</td><td>{html.escape(a['overlap'])}</td>"
            f"<td>{html.escape(a['support'])}</td><td>{html.escape(a['task'])}</td>"
            f"<td>{html.escape(a['difference'])}</td></tr>"
        )
    return """<!doctype html><html><head><meta charset='utf-8'><title>DSA P2 Nearest Neighbors</title>
<style>body{font-family:Arial,sans-serif;margin:2rem;line-height:1.4}table{border-collapse:collapse;width:100%}th,td{border:1px solid #bbb;padding:.45rem;vertical-align:top}th{background:#eee}</style></head><body>""" + (
        f"<h1>DSA 2026 P2 Nearest-Neighbor Matrix</h1><p>Search date: 2026-07-11; records: {len(records)}; exact match: {str(log['exact_design_match_found']).lower()}.</p>"
        "<table><thead><tr><th>Work</th><th>Year</th><th>Overlap</th><th>Support</th><th>Task</th><th>Key difference</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></body></html>"
    )


def serialize(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    records = build_records()
    log = build_log(records)
    outputs = {
        RIS_OUT: "\n\n".join(record["ris_record"].strip() for record in records) + "\n",
        MATRIX_OUT: render_markdown(records, log),
        HTML_OUT: render_html(records, log),
        LOG_OUT: serialize(log),
    }
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    else:
        stale = [str(path.relative_to(ROOT)) for path, content in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            raise SystemExit(f"stale or missing outputs: {stale}")
        if not log["positioning_gate_passed"]:
            raise SystemExit("nearest-neighbor positioning gate failed")
    print(json.dumps({"status": "passed", "reference_count": len(records), "exact_design_match_found": log["exact_design_match_found"]}, sort_keys=True))


if __name__ == "__main__":
    main()
