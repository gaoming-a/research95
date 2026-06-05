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


def build_draft(tables_tex: str, result_tables_tex: str) -> str:
    tables_tex = tables_tex.replace("Generated pre-API paper tables", "Generated dataset and no-API paper tables")
    return rf"""\documentclass[conference]{{IEEEtran}}

\usepackage{{booktabs}}
\usepackage{{graphicx}}
\usepackage{{url}}
\usepackage{{xspace}}

\newcommand{{\toolname}}{{Tool-Augmented Patch Verification\xspace}}

\title{{Verifiable Review of AI-Generated Patches in Real Software Projects}}

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
patch acceptance as a verification problem: given a real task and a candidate
patch, decide whether the patch should be accepted, rejected, or escalated
based on evidence. We construct a pilot patch-verification dataset from
retained real-bug pairs, materialize source-level patch candidates, validate
labels with executable oracles, and evaluate three review conditions: LLM-only
patch review, prompt-only evidence-first verification, and tool-augmented
evidence verification. The pilot contains 30 validated patch candidates from 7
real-bug tasks across 2 projects, including 9 partial-fix candidates. In a
single-model DeepSeek API pilot, prompt-only evidence-first verification
removes observed false accepts but loses correct-patch recall. A separate
tool-augmented verifier, given executable behavior summaries, restores correct
recall while preserving zero observed false accepts on this pilot. The result
supports a conditional tool-assisted verification claim rather than a general
claim that prompt-only review is sufficient.
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

\textbf{{RQ1.}} How reliable is LLM-only review when deciding whether candidate
patches should be accepted?

\textbf{{RQ2.}} Can prompt-only evidence-first verification reduce false
accepts compared with LLM-only review?

\textbf{{RQ3.}} Does evidence-first verification preserve useful correct-patch
recall, or does it only reduce false accepts by rejecting or escalating too
aggressively?

\textbf{{RQ4.}} Does tool-augmented evidence verification recover the
correct-patch recall lost by prompt-only evidence-first verification?

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
\caption{{Evidence visibility by condition. Hidden evaluator labels and oracle
paths are not exposed; the tool-augmented condition is distinguished by
patch-application and behavior summaries.}}
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

\section{{Real API Pilot Result}}

The first API pilot ran two prompt-only conditions on the validated candidates:
LLM-only review and evidence-first verification. Both conditions used
\texttt{{deepseek-v4-pro}} through the DeepSeek official API, yielding 60
non-mock review records. The run passed completeness checks: 30 candidates, 2
conditions, raw response hashes present, no missing raw responses, no
\texttt{{run\_error.json}}, and required review fields present.

Prompt-only evidence-first verification removed the observed false accepts and
improved accepted precision, but correct-patch recall dropped below the
configured gate. The result is therefore mixed rather than positive: it
supports a safety/utility tradeoff claim, not a superiority claim.

\section{{Tool-Augmented Redesign}}

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

\begin{{figure*}}[t]
\centering
\includegraphics[width=0.86\textwidth]{{docs/figures/fig4_result_tradeoff.pdf}}
\caption{{Safety/recall tradeoff across review conditions. Prompt-only
evidence-first verification removes observed false accepts but loses recall;
tool-augmented evidence restores recall under the current pilot.}}
\label{{fig:result-tradeoff}}
\end{{figure*}}

\begin{{figure}}[t]
\centering
\includegraphics[width=\columnwidth]{{docs/figures/fig5_claim_boundary.pdf}}
\caption{{Claim boundary supported by the current evidence. The positive claim
is conditional on tool-visible execution evidence, not prompt-only model
review.}}
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

The first real API pilot is a within-model comparison using
\texttt{{deepseek-v4-pro}} through the DeepSeek official API. This controls for
base-model capability within the prompt-only comparison and isolates the
condition change. It does not establish cross-model generality.

\section{{Threats to Validity}}

Dataset size is small. The current pilot is designed to validate the method and
failure surfaces, not to make broad claims about all AI-generated patches. The
partial-fix candidates are source-backed and oracle-checkable, but they are
constructed from retained reference diffs rather than generated by live coding
agents. A later stage should add model-generated patches or SWE-bench-style
tasks.

Visible test hints may not represent the evidence actually available in all
engineering workflows. Tool-augmented evidence includes executable behavior
summaries; this is closer to an engineering verification workflow than pure
LLM review, but it may also be a strong upper-bound form of evidence depending
on how such summaries are produced in deployment.

Model behavior can drift over time and across providers. Every API run must
record model id, provider, date, prompt version, decoding settings, cost, raw
response path, and invalid-output status. The first pilot uses a single model
by design and cannot support claims about all frontier models or all coding
agents.

\section{{Conclusion}}

The current artifact establishes a validated patch-verification pilot and a
completed single-model API pilot. Prompt-only evidence-first verification is
not sufficient under the configured gate: it reduces false accepts but loses
too much correct-patch recall. The redesigned tool-augmented verifier passes
the 30-candidate full-run gate by accepting all correct reference patches and
rejecting all negative candidates. The defensible conclusion is therefore a
three-stage finding: LLM-only review is unsafe as a merge gate, prompt-only
evidence-first review is too conservative under evidence poverty, and
tool-visible execution evidence can support a stronger verifier under the
current pilot conditions.

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
    parser.add_argument("--out", default="docs/paper/ieee_submission_draft.tex")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tables_tex = read_text(Path(args.tables_tex))
    result_tables_tex = build_result_tables(read_json(Path(args.prompt_metrics)), read_json(Path(args.tool_gate)))
    write_text(Path(args.out), build_draft(tables_tex, result_tables_tex))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
