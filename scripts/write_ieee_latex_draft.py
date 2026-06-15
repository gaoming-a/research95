from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def fmt_metric(value: Any) -> str:
    if value is None:
        return "--"
    if isinstance(value, str):
        return value
    return f"{float(value):.4f}"


def fmt_count(value: Any) -> str:
    return str(int(value))


def latex_escape(value: str) -> str:
    return (
        value.replace("\\", r"\textbackslash{}")
        .replace("_", r"\_")
        .replace("%", r"\%")
        .replace("&", r"\&")
        .replace("#", r"\#")
        .replace("{", r"\{")
        .replace("}", r"\}")
    )


def condition_metrics_rows(prompt_metrics: dict[str, Any], tool_gate: dict[str, Any]) -> str:
    groups = prompt_metrics.get("groups", {})
    if not isinstance(groups, dict):
        raise ValueError("prompt metrics must contain a groups object")
    llm_only = next((value for key, value in groups.items() if key.startswith("llm_only::")), {})
    evidence_first = next((value for key, value in groups.items() if key.startswith("evidence_first::")), {})
    row_specs = [
        ("llm_only", "LLM-only", llm_only),
        ("evidence_first", "Prompt-only evidence-first", evidence_first),
    ]
    tool_metrics = tool_gate.get("metrics", {})
    if not isinstance(tool_metrics, dict):
        raise ValueError("tool gate must contain a metrics object")
    row_specs.append(("tool_augmented_evidence", "Tool-augmented evidence", tool_metrics))

    rows: list[str] = []
    for _key, label, metrics in row_specs:
        if not isinstance(metrics, dict):
            metrics = {}
        rows.append(
            " & ".join(
                [
                    latex_escape(label),
                    fmt_metric(metrics.get("false_accept_rate")),
                    fmt_metric(metrics.get("accepted_precision")),
                    fmt_metric(metrics.get("correct_patch_recall")),
                    fmt_metric(metrics.get("false_reject_rate")),
                    fmt_metric(metrics.get("escalation_rate")),
                    fmt_metric(metrics.get("invalid_output_rate")),
                ]
            )
            + r" \\"
        )
    return "\n".join(rows)


def build_result_tables(prompt_metrics: dict[str, Any], tool_gate: dict[str, Any]) -> str:
    rows = condition_metrics_rows(prompt_metrics, tool_gate)
    return rf"""
\begin{{table*}}[t]
\centering
\caption{{Real API patch-verification results. The tool-augmented condition is a separate evidence-assisted workflow and must not be interpreted as prompt-only model ability.}}
\label{{tab:api-results}}
\begin{{tabular}}{{lrrrrrr}}
\toprule
Condition & False accept & Accepted precision & Correct recall & False reject & Escalation & Invalid output \\
\midrule
{rows}
\bottomrule
\end{{tabular}}
\end{{table*}}
"""


def evp7_summary_text(evp7_summary: dict[str, Any], evp7_quality: dict[str, Any]) -> dict[str, str]:
    quality = evp7_summary.get("quality", {})
    workflow = evp7_summary.get("workflow", {})
    metric_groups = evp7_summary.get("metrics", {}).get("metric_groups", {})
    if not isinstance(quality, dict) or not isinstance(workflow, dict) or not isinstance(metric_groups, dict):
        raise ValueError("EVP-7 summary is missing quality/workflow/metric_groups")
    e4 = metric_groups.get("E4", {})
    e6 = metric_groups.get("E6", {})
    cost_summary = workflow.get("cost_summary", {})
    if not isinstance(cost_summary, dict):
        cost_summary = {}
    unsupported = evp7_quality.get("unsupported_claims", [])
    limitations = evp7_quality.get("limitations", [])
    unsupported_text = "; ".join(latex_escape(str(item).rstrip(".")) for item in unsupported)
    return {
        "provider": latex_escape(str(evp7_summary.get("provider", "unknown"))),
        "model": latex_escape(str(evp7_summary.get("model", "unknown"))),
        "review_count": fmt_count(quality.get("review_count", 0)),
        "candidate_count": fmt_count(evp7_quality.get("candidate_count", 0)),
        "task_count": "20",
        "evidence_packet_count": fmt_count(quality.get("review_count", 0)),
        "invalid_output_rate": fmt_metric(quality.get("invalid_output_rate")),
        "total_cost_usd": fmt_metric(cost_summary.get("total_cost_usd")),
        "unknown_cost_count": fmt_count(cost_summary.get("unknown_cost_record_count", 0)),
        "quality_status": latex_escape(str(evp7_quality.get("quality_status", "unknown"))),
        "e4_false_accept": fmt_metric(e4.get("false_accept_rate")),
        "e4_precision": fmt_metric(e4.get("accepted_precision")),
        "e4_recall": fmt_metric(e4.get("correct_recall")),
        "e4_gain": fmt_metric(e4.get("evidence_gain_vs_e0")),
        "e6_false_accept": fmt_metric(e6.get("false_accept_rate")),
        "e6_precision": fmt_metric(e6.get("accepted_precision")),
        "e6_recall": fmt_metric(e6.get("correct_recall")),
        "e6_gain": fmt_metric(e6.get("evidence_gain_vs_e0")),
        "unsupported_claims": unsupported_text,
        "limitations": "; ".join(latex_escape(str(item)) for item in limitations),
    }


def build_draft(
    tables_tex: str,
    result_tables_tex: str,
    evp7_summary: dict[str, Any],
    evp7_quality: dict[str, Any],
) -> str:
    tables_tex = tables_tex.replace("Generated pre-API paper tables", "Generated dataset and no-API paper tables")
    evp7 = evp7_summary_text(evp7_summary, evp7_quality)
    return rf"""\documentclass[conference]{{IEEEtran}}

\usepackage{{booktabs}}
\usepackage{{graphicx}}
\usepackage{{url}}
\usepackage{{xspace}}

\newcommand{{\toolname}}{{Tool-Augmented Patch Verification\xspace}}

\title{{Evidence Visibility Matters: A Systematic Study of LLM-Based Verification for Candidate Patches}}

\author{{
\IEEEauthorblockN{{Anonymous Authors}}
\IEEEauthorblockA{{Anonymous Institution\\
Email: anonymous@example.com}}
}}

\begin{{document}}
\maketitle

\begin{{abstract}}
AI coding agents increasingly produce patches for real software tasks, but a
patch that looks plausible is not necessarily safe to merge. This paper studies
patch acceptance as an evidence-conditioned merge-gate decision: given a real
task and a candidate patch, decide whether the patch should be accepted,
rejected, or escalated under visible evidence. We construct a frozen EVP-7
pilot from retained real-bug tasks, materialize source-level patch candidates,
validate labels with executable oracles, and review {evp7["candidate_count"]}
candidates across E0/E2/E4/E6 evidence levels, yielding
{evp7["evidence_packet_count"]} evidence packets. A single-model DeepSeek G5
run produces {evp7["review_count"]} parse-valid non-mock records. E4 and E6
preserve zero observed false accepts and accepted precision 1.0000, while E6
achieves correct recall {evp7["e6_recall"]} and Evidence Gain
{evp7["e6_gain"]}. Wilson intervals, candidate-level bootstrap deltas, and a
claim-boundary audit keep the interpretation bounded. Earlier 30-candidate
API pilots motivate the design boundary: prompt-only evidence discipline
reduces observed false accepts but loses correct-patch recall, while
tool-visible execution summaries support a separate tool-assisted workflow.
The result supports bounded evidence-level variation, not scale-generalized
model or deployment claims.
\end{{abstract}}

\section{{Introduction}}

AI coding agents are increasingly used to generate patches for real codebases.
The standard question, ``does the patch pass tests?'', is insufficient when
tests are incomplete or generated changes are plausible but partial. Software
teams need a merge-gate decision: accept, reject, or escalate.

\begin{{figure}}[t]
\centering
\includegraphics[width=\columnwidth]{{docs/figures/fig1_framework.pdf}}
\caption{{Patch-verification workflow. The reviewer first sees task and patch
context; the redesigned verifier adds visible execution evidence before making
accept, reject, or escalation decisions.}}
\label{{fig:framework}}
\end{{figure}}

This work treats patch review as a verification problem rather than a generic
bug-finding problem. The reviewer is asked to judge a candidate patch against a
task summary and visible patch context. The evaluator uses executable or
tool-backed evidence to determine whether the decision is correct.

The motivating failure mode comes from earlier experiments in this project:
LLM-only review produced useful signals but also over-reported defects on
fixed/reference controls. That makes prompt-only review unsuitable as a merge
gate without stronger evidence discipline.

\section{{Research Questions}}

\textbf{{RQ1.}} How risky is evidence-poor LLM review as a merge gate for
candidate patches?

\textbf{{RQ2.}} Does prompt-only evidence discipline reduce observed false
accepts, and what correct-recall cost does it introduce?

\textbf{{RQ3.}} Across E0/E2/E4/E6, how does visible evidence change false
accepts, accepted precision, correct recall, escalation, and utility?

\textbf{{RQ4.}} What do deterministic and tool-assisted evidence baselines
allow us to claim about LLM contribution?

\textbf{{RQ5.}} Which paper claims remain supported or unsupported under the
frozen 20-task EVP-7 pilot boundary?

\section{{Dataset Construction}}

The pilot dataset is built from retained BugsInPy-derived real-bug assets. Each
source task has a buggy checkout, a fixed checkout, a task summary, touched
files, visible test hints, and retained executable oracles.

Each candidate record contains evaluator-facing fields, including patch
identity, candidate type, expected outcome, and oracle metadata. Model-visible
inputs use an anonymous candidate identifier and omit evaluator labels, oracle
paths, oracle results, and construction notes.

Patch materialization uses retained source artifacts: reference diffs between
buggy and fixed checkouts, no-op controls, applicable unrelated source changes,
and partial candidates derived from multi-hunk or multi-line reference fixes.

\section{{Executable Label Validation}}

Candidate labels are validated by applying each candidate patch to a copied
buggy checkout and running retained executable oracles. This guards against
purely prompt-based or manually asserted labels. Correct patches are expected
to pass all retained oracles. Negative candidates are expected to fail at least
one retained oracle.

\section{{Review Conditions}}

\subsection{{LLM-Only Review}}

The reviewer sees the task summary, visible context, and candidate patch. It
must output one JSON object with decision, confidence, claims, rationale, and
uncertainty. It does not see hidden oracle paths or oracle results.

\subsection{{Evidence-First Verification}}

The reviewer sees the same task and patch context plus model-visible evidence
source metadata and visible test hints. It must tie every accept/reject
decision to concrete visible evidence. If the visible evidence is insufficient,
it should escalate.

\subsection{{Tool-Augmented Evidence Verification}}

The reviewer sees the same task and patch context plus patch-apply status and
executable behavior summaries derived from retained validation runs. It still
does not see evaluator labels, candidate types, construction notes, oracle
paths, or hidden expected outcomes. This condition is reported separately
because it is a tool-assisted workflow, not prompt-only model ability.

\begin{{figure}}[t]
\centering
\includegraphics[width=\columnwidth]{{docs/figures/fig2_evidence_visibility.pdf}}
\caption{{EVP-7 evidence visibility levels. E0 exposes issue summary and patch
diff; E2 adds apply/static evidence; E4 adds visible F2P/P2P test outcomes; E6
adds visible tool/behavior summaries. Evaluator truth labels remain hidden at
all levels.}}
\label{{fig:evidence-visibility}}
\end{{figure}}

\subsection{{Oracle Upper Bound}}

The evaluator can use hidden labels and oracle outcomes to produce an upper
bound. This is not model capability and must be reported separately.

\section{{Metrics}}

Primary metrics are patch-level: false accept rate, false reject rate, accepted
precision, correct-patch recall, escalation rate, invalid-output rate, and cost.
Escalation is neither accept nor reject. It should be reported separately
because reducing false accepts by escalating everything is not a useful merge
gate.

\section{{No-API Baselines}}

The current no-API baselines validate the metric implementation and expected
tradeoffs. These baselines are not model-review results. They expose the
merge-gate tension: accepting everything preserves correct-patch recall while
accepting all wrong patches, and rejecting everything avoids false accepts
while rejecting all correct patches.

\begin{{figure}}[t]
\centering
\includegraphics[width=\columnwidth]{{docs/figures/fig3_dataset_composition.pdf}}
\caption{{Pilot dataset composition and executable validation. The dataset is
small but intentionally includes difficult partial-fix candidates.}}
\label{{fig:dataset}}
\end{{figure}}

{tables_tex}

\section{{First-Pilot API Diagnostic}}

Before the frozen EVP-7 run, a first API pilot ran two prompt-only conditions
on the validated candidates:
LLM-only review and evidence-first verification. Both conditions used
\texttt{{deepseek-v4-pro}} through the DeepSeek official API, yielding 60
non-mock review records. The run passed completeness checks: 30 candidates, 2
conditions, raw response hashes present, no missing raw responses, no
\texttt{{run\_error.json}}, and required review fields present.

Prompt-only evidence-first verification removed the observed false accepts and
improved accepted precision, but correct-patch recall dropped below the
configured gate. The result is therefore mixed rather than positive: it
supports a safety/utility tradeoff claim, not a superiority claim.

\section{{First-Pilot Tool-Augmented Redesign}}

After the prompt-only gate returned \texttt{{stop\_or\_redesign}}, we evaluated
a separate \texttt{{tool\_augmented\_evidence}} condition. The verifier saw
patch-apply status and executable behavior summaries, but not evaluator labels
or oracle paths. A five-candidate redesign smoke recovered the known failure
cases. The subsequent 30-candidate full run passed the dedicated
tool-augmented gate with 30 non-mock reviews, zero invalid outputs, zero false
accepts, and complete correct-patch recall.

{result_tables_tex}

This result supports a conditional tool-assisted verification claim. It does
not reverse the prompt-only result. Instead, it shows that executable evidence
summaries can be decisive when prompt-only evidence is too sparse.

\section{{EVP-7 Evidence-Visibility Result}}

The paper-facing result freezes a larger EVP-7 cohort with {evp7["task_count"]} real-bug tasks,
{evp7["candidate_count"]} patch candidates, and four model-visible evidence
levels per candidate. The resulting {evp7["evidence_packet_count"]} evidence
packets are reviewed by the G5 merge-gate verifier using
\texttt{{{evp7["model"]}}} through \texttt{{{evp7["provider"]}}}. The run
produced {evp7["review_count"]} non-mock records, invalid-output rate
{evp7["invalid_output_rate"]}, and quality status
\texttt{{{evp7["quality_status"]}}}. Cost observability is complete for the
tracked records: the runner-estimated total cost is {evp7["total_cost_usd"]}
USD and the unknown-cost record count is {evp7["unknown_cost_count"]}. This
cost is estimated from provider token usage and configured pricing; it is not
an external billing statement.

The EVP-7 tables report evidence-level decisions and the audited claim
boundary. Statistical intervals are reported with Wilson binomial intervals
and candidate-level paired bootstrap deltas to avoid presenting the 376-record
pilot as a scale-generalized result. A utility-sensitivity table varies
false-accept, escalation, and false-reject penalties around the default
merge-gate utility. E4 preserves false-accept rate {evp7["e4_false_accept"]}, accepted
precision {evp7["e4_precision"]}, correct recall {evp7["e4_recall"]}, and
evidence gain {evp7["e4_gain"]}. E6 preserves false-accept rate
{evp7["e6_false_accept"]}, accepted precision {evp7["e6_precision"]}, correct
recall {evp7["e6_recall"]}, and evidence gain {evp7["e6_gain"]}. The bounded
interpretation is that evidence visibility changes merge-gate behavior on this
pilot cohort. It does not establish deterministic-baseline superiority, E6
strict superiority over E4, scale generality, or billing equivalence.

\begin{{figure*}}[t]
\centering
\includegraphics[width=0.86\textwidth]{{docs/figures/fig6_evp7_visibility_curve.pdf}}
\caption{{EVP-7 evidence visibility curve over E0/E2/E4/E6. The curve reports
false accept rate, accepted precision, correct recall, escalation rate, and
Evidence Gain from the 376-record G5 run.}}
\label{{fig:evp7-visibility-curve}}
\end{{figure*}}

\begin{{figure*}}[t]
\centering
\includegraphics[width=0.86\textwidth]{{docs/figures/fig4_result_tradeoff.pdf}}
\caption{{Safety/recall tradeoff across first-pilot review conditions. Prompt-only
evidence-first verification removes observed false accepts but loses recall;
tool-augmented evidence restores recall under the current pilot.}}
\label{{fig:result-tradeoff}}
\end{{figure*}}

\begin{{figure}}[t]
\centering
\includegraphics[width=\columnwidth]{{docs/figures/fig5_claim_boundary.pdf}}
\caption{{Claim boundary supported by the current evidence. The first positive
claim is conditional on tool-visible execution evidence; the EVP-7 claim is a
bounded evidence-visibility pilot result.}}
\label{{fig:claim-boundary}}
\end{{figure}}

\section{{Reproducibility and Handoff Controls}}

The pre-API artifact includes deterministic reproduction checks for local
dataset construction. The original no-API pilot and a reproduced run are
compared by hashing deterministic output files. Runtime work directories, raw
API responses, external checkouts, and environment-dependent files are not
treated as deterministic reproducibility evidence.

The execution plan also separates local checks from model experiments. The
current handoff packet refreshes readiness, paper readiness, plan progress,
human-required inputs, Git-sync state, model-selection visibility, and
deterministic reproducibility.

\section{{Model Selection Boundary}}

The first real API pilot and the EVP-7 G5 run use \texttt{{deepseek-v4-pro}}
through the DeepSeek official API. This controls for base-model capability
within each comparison and isolates condition or evidence-level changes. It
does not establish cross-model generality.

\section{{Threats to Validity}}

Dataset size remains small. The first 30-candidate pilot and the later EVP-7
{evp7["evidence_packet_count"]}-packet pilot are designed to validate the
method and failure surfaces, not to make broad claims about all AI-generated
patches. The partial-fix candidates are source-backed and oracle-checkable, but
they are constructed from retained reference diffs rather than generated by
live coding agents. A later stage should add model-generated patches or
SWE-bench-style tasks.

Visible test hints may not represent the evidence actually available in all
engineering workflows. Tool-augmented evidence includes executable behavior
summaries; this is closer to an engineering verification workflow than pure
LLM review, but it may also be a strong upper-bound form of evidence depending
on how such summaries are produced in deployment.

Model behavior can drift over time and across providers. Every API run must
record model id, provider, date, prompt version, decoding settings, cost
observability, raw-output handling, and invalid-output status. The current
DeepSeek runs use a single model by design and cannot support claims about all
frontier models or all coding agents. The EVP-7 quality audit also rejects:
{evp7["unsupported_claims"]}.

\section{{Conclusion}}

The paper-facing artifact establishes a frozen EVP-7 evidence-visibility pilot:
20 real-bug tasks, {evp7["candidate_count"]} patch candidates, and
{evp7["evidence_packet_count"]} reviewed evidence packets. Within this bounded
single-model setting, evidence visibility changes merge-gate behavior: E4 and
E6 preserve zero observed false accepts and accepted precision 1.0000, while
E6 improves correct recall and Evidence Gain over E0 in the tracked summary.
The earlier 30-candidate pilots explain why this boundary matters:
prompt-only evidence-first verification was safer but too conservative under
evidence poverty, and tool-visible execution summaries supported a separate
tool-assisted verifier. The defensible conclusion is therefore not that the
LLM is deployment-ready or superior to deterministic tool evidence. It is that
candidate-patch verification must report what evidence was visible, how hidden
labels were withheld until evaluation, and which claims remain bounded by the
current cohort, model, and evidence design.

\end{{document}}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the IEEE LaTeX submission draft.")
    parser.add_argument("--tables-tex", default="docs/paper/generated_tables.tex")
    parser.add_argument("--prompt-metrics", default="outputs/patch_verification_api_pilot_002/metrics.json")
    parser.add_argument(
        "--tool-gate",
        default="outputs/patch_verification_tool_augmented_full_001/tool_augmented_full_gate.json",
    )
    parser.add_argument("--evp7-summary", default="data/reviews/evp7_g5_llm_376_full_summary.json")
    parser.add_argument("--evp7-quality-audit", default="data/reviews/evp7_g5_376_full_quality_audit.json")
    parser.add_argument("--out", default="docs/paper/ieee_submission_draft.tex")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tables_tex = read_text(Path(args.tables_tex))
    result_tables_tex = build_result_tables(read_json(Path(args.prompt_metrics)), read_json(Path(args.tool_gate)))
    evp7_summary = read_json(Path(args.evp7_summary))
    evp7_quality = read_json(Path(args.evp7_quality_audit))
    write_text(Path(args.out), build_draft(tables_tex, result_tables_tex, evp7_summary, evp7_quality))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
