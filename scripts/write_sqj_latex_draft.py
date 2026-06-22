from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


REQUIRED_SNIPPETS = [
    r"\documentclass[pdflatex,sn-basic]{sn-jnl}",
    r"\abstract{",
    r"\keywords{",
    r"\section{Introduction}",
    r"\section{Evidence Visibility Protocol}",
    r"\section{Multi-Model Study}",
    r"\section{Results}",
    r"\section{Software Quality Risks}",
    r"\section{Threats to Validity}",
    r"\bmhead{Data availability}",
    r"\bmhead{Competing interests}",
    r"\bibliography{sqj_references}",
    "sqj_fig1_evp8_protocol.pdf",
    "sqj_fig2_decision_patterns.pdf",
    "sqj_fig3_cost_boundary.pdf",
    "Evidence visibility is a first-order experimental variable",
    "model-dependent and non-monotonic",
    "not valid model-result records",
]

FORBIDDEN_SNIPPETS = [
    "LLM verifiers outperform deterministic",
    "E6 is strictly better than E4",
    "strictly improves over E4",
    "scale-generalized",
    "guaranteed school recognition",
    "Open Access route by default",
]


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


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def per_level_totals(synthesis: dict[str, Any]) -> list[dict[str, int | str]]:
    by_level = synthesis.get("per_level_decision_counts_by_model", {})
    if not isinstance(by_level, dict):
        raise ValueError("synthesis missing per_level_decision_counts_by_model")
    rows: list[dict[str, int | str]] = []
    for level in ["E0", "E1", "E2", "E3", "E4", "E5", "E6"]:
        models = by_level.get(level, {})
        if not isinstance(models, dict):
            raise ValueError(f"synthesis missing {level}")
        accept = escalate = reject = 0
        for counts in models.values():
            if not isinstance(counts, dict):
                continue
            accept += int(counts.get("accept", 0) or 0)
            escalate += int(counts.get("escalate", 0) or 0)
            reject += int(counts.get("reject", 0) or 0)
        rows.append({"level": level, "accept": accept, "escalate": escalate, "reject": reject})
    return rows


def total_line(rows: list[dict[str, int | str]]) -> str:
    parts = []
    for row in rows:
        parts.append(f"{row['level']}: {row['escalate']} escalate / {row['reject']} reject")
    return "; ".join(parts)


def build_bibtex() -> str:
    return r"""@inproceedings{just2014defects4j,
  author    = {Just, Ren{\'e} and Jalali, Darioush and Ernst, Michael D.},
  title     = {Defects4J: A Database of Existing Faults to Enable Controlled Testing Studies for Java Programs},
  booktitle = {Proceedings of the 2014 International Symposium on Software Testing and Analysis},
  year      = {2014},
  pages     = {437--440}
}

@inproceedings{widyasari2020bugsinpy,
  author    = {Widyasari, R. and others},
  title     = {BugsInPy: A Database of Existing Bugs in Python Programs to Enable Controlled Testing and Debugging Studies},
  booktitle = {Proceedings of the ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering},
  year      = {2020},
  pages     = {1556--1560}
}

@inproceedings{qi2015patchcorrectness,
  author    = {Qi, Zichao and Long, Fan and Achour, Sara and Rinard, Martin},
  title     = {An Analysis of Patch Plausibility and Correctness for Generate-and-Validate Patch Generation Systems},
  booktitle = {Proceedings of the 2015 International Symposium on Software Testing and Analysis},
  year      = {2015},
  pages     = {24--36}
}

@inproceedings{xia2023llmapr,
  author    = {Xia, Chunqiu Steven and Wei, Yuxiang and Zhang, Lingming},
  title     = {Automated Program Repair in the Era of Large Pre-trained Language Models},
  booktitle = {Proceedings of the 45th International Conference on Software Engineering},
  year      = {2023},
  pages     = {1482--1494}
}

@inproceedings{jimenez2024swebench,
  author    = {Jimenez, Carlos E. and Yang, John and Wettig, Alexander and Yao, Shunyu and Pei, Kexin and Press, Ofir and Narasimhan, Karthik},
  title     = {SWE-bench: Can Language Models Resolve Real-world GitHub Issues?},
  booktitle = {Proceedings of the International Conference on Learning Representations},
  year      = {2024}
}
"""


def build_draft(
    synthesis: dict[str, Any],
    cost: dict[str, Any],
    tables_tex_path: Path,
    framing_path: Path,
) -> str:
    totals = cost.get("totals", {})
    if not isinstance(totals, dict):
        raise ValueError("cost summary missing totals")
    rows = per_level_totals(synthesis)
    aggregate_line = total_line(rows)
    passed_usd = float(totals.get("passed_result_usd_excluding_qwen", 0) or 0)
    qwen_cny = float(totals.get("passed_qwen_cny", 0) or 0)
    blocked_usd = float(totals.get("blocked_attempt_usd", 0) or 0)
    observable_usd = float(totals.get("tracked_plus_blocked_observable_usd_excluding_qwen", 0) or 0)
    later_observable = float(totals.get("later_model_observable_usd_including_blocked", 0) or 0)

    return rf"""\documentclass[pdflatex,sn-basic]{{sn-jnl}}

\usepackage{{booktabs}}
\usepackage{{graphicx}}
\usepackage{{url}}
\usepackage{{xspace}}

\jyear{{2026}}

\title[Evidence Visibility in LLM-Based Patch Verification]{{Evidence Visibility in LLM-Based Patch Verification: A Software Quality Perspective}}

\author*[1]{{\fnm{{Anonymous}} \sur{{Author}}}}\email{{anonymous@example.com}}
\affil*[1]{{\orgdiv{{Anonymous Department}}, \orgname{{Anonymous Institution}}, \country{{Anonymous}}}}

\abstract{{
Large language models are increasingly used to judge candidate software
patches, yet a verifier decision depends on the evidence that is visible at
review time. This paper studies evidence visibility as a software quality
variable in LLM-based patch verification. We construct a hidden-evaluator
workflow in which candidate patches are reviewed under frozen evidence packets
and evaluator labels are joined only after the model decision. On a frozen
EVP-8 packet set covering 98 candidate patches and seven evidence levels, five
LLMs each produced 686 parse-valid merge-gate decisions. The resulting decision
patterns show that evidence visibility changes verifier behavior, but not as a
simple monotonic curve: DeepSeek V4 Pro and Qwen3.7 Max show substantial
level-specific variation, Kimi K2.6 and Gemini 2.5 Flash show smaller local
differences, and Devstral 2 saturates to escalation. The aggregate decision
totals were also non-monotonic across E0-E6. We further report cost
observability and blocked-run accounting, separating valid model results from
execution-risk evidence. The study supports descriptive claims about
evidence-conditioned verifier behavior, not claims that LLM verifiers
outperform deterministic baselines or that any evidence level is generally
optimal.
}}

\keywords{{large language models, patch verification, software quality, evidence visibility, empirical software engineering, software reliability}}

\begin{{document}}

\maketitle

\section{{Introduction}}

Candidate patches for real software tasks can appear plausible while still
being partial, irrelevant, or unsafe to merge. This makes patch verification a
software quality problem rather than only a patch-generation problem. A merge
gate must decide whether to accept, reject, or escalate a patch under the
evidence available at the time of review.

Large language models (LLMs) are attractive as patch reviewers because they can
read code, summarize changes, and produce explanations. However, the same
model can make different decisions when the visible evidence changes. If a
study does not control what the model sees, it becomes difficult to separate
model capability from evidence presentation.

Evidence visibility is a first-order experimental variable
in LLM-based patch verification. We ask how verifier decisions change when the
same candidate patches are reviewed under a frozen sequence of evidence
levels. The study is framed for software quality: the question is not which
model wins a leaderboard, but whether LLM-based merge gates behave reliably
when evidence is structured, withheld, or augmented.

We report an EVP-8 multi-model study over 98 candidate patches, seven evidence
levels, and five LLMs. Each model produced 686 parse-valid decisions on the
same frozen packet set. The observed patterns are model-dependent and
non-monotonic, which means that more evidence did not translate into a simple
monotone decision curve. This is the main finding and the main boundary of the
paper.

\section{{Background and Related Work}}

Real-bug benchmarks such as Defects4J and BugsInPy support controlled testing
and repair studies by providing reproducible failures and fixes
\cite{{just2014defects4j,widyasari2020bugsinpy}}. Generate-and-validate repair
research has also shown that plausible patches can pass available tests while
remaining semantically wrong \cite{{qi2015patchcorrectness}}. Recent LLM-based
repair and agentic software-engineering work expands the set of systems that
can produce or evaluate patches \cite{{xia2023llmapr,jimenez2024swebench}}.

This study focuses on a different but adjacent problem. Given a candidate
patch, a verifier must decide whether the evidence supports accepting it. The
contribution is therefore not another patch-generation benchmark. It is a
controlled examination of how model-visible evidence affects merge-gate
decisions.

\section{{Evidence Visibility Protocol}}

The experimental unit is a candidate patch reviewed under a stated evidence
packet. Model-visible packets contain task and patch information plus a
predefined evidence level. Evaluator-only labels, construction notes, oracle
results, and correctness labels are withheld from the model and joined only
after the decision.

The EVP-8 protocol defines seven model-visible evidence levels, E0 through E6,
for the same frozen 98-candidate set. The levels are designed as a full ladder
for protocol validation and multi-model decision-pattern analysis. The protocol
does not expose evaluator-only labels, and the tracked summaries avoid raw
model-response text.

Each verifier returns one merge-gate decision: accept, reject, or escalate. In
the observed EVP-8 runs, the selected models did not emit accept decisions on
this packet set; the measured behavior is therefore an escalation/rejection
pattern. This is still informative for reliability because over-escalation and
model saturation are deployment risks for a verifier.

\begin{{figure*}}[t]
\centering
\includegraphics[width=\textwidth]{{docs/figures/sqj/sqj_fig1_evp8_protocol.pdf}}
\caption{{EVP-8 hidden-evaluator study design. The protocol reviews 98
candidate patches across seven evidence levels and five model verifiers while
withholding evaluator-only labels until after the model decision. The figure
also marks the raw-output-free summary boundary and the zero-observed-accept
decision pattern.}}
\label{{fig:sqj-evp8-protocol}}
\end{{figure*}}

\section{{Candidate Patch and Evidence Packet Construction}}

The EVP-8 candidate set is derived from the project's tracked real-bug
candidate-patch pipeline. The frozen v0.1 packet set contains 98 candidate
patches and seven evidence levels, for 686 planned review records per model.
The source pipeline keeps model-visible evidence separate from evaluator-side
correctness labels and oracle outcomes.

The earlier EVP-7 four-anchor pilot remains part of the motivation and
artifact history. It established the candidate-patch verification workflow and
bounded claim discipline. The SQJ-facing result in this draft, however, is the
EVP-8 five-model full-ladder decision-pattern study.

\section{{Multi-Model Study}}

We evaluated five fixed model identifiers on the same frozen EVP-8 v0.1 packet
set: DeepSeek V4 Pro, Qwen3.7 Max, Kimi K2.6, Devstral 2, and Gemini 2.5
Flash. Each model was run under the same prompt version, output schema, parser
boundary, and evidence packet set. Later-model runs through OpenRouter pinned
the requested model identifier and recorded actual provider and model metadata.

The synthesis passed only after all selected model summaries were present and
raw-output-free audits passed. The resulting synthesis supports descriptive
per-level decision-pattern reporting for the frozen EVP-8 packet set. It does
not support claims of LLM superiority over deterministic baselines, final
evidence-level effectiveness, or broad scale generalization.

\section{{Results}}

Evidence visibility changed verifier behavior across the five-model set. The
aggregate per-level totals were: {aggregate_line}. These totals show a
non-monotonic pattern rather than a simple improvement from E0 to E6.

DeepSeek V4 Pro and Qwen3.7 Max showed the clearest level-specific variation.
For example, DeepSeek produced 66 escalations and 32 rejections at E0, 58
escalations and 40 rejections at E1, and 86 escalations and 12 rejections at
E6. Qwen similarly shifted from 75 escalations and 23 rejections at E0 to 91
escalations and 7 rejections at E6. These patterns indicate evidence
sensitivity, but not a strictly monotone effectiveness ranking.

The later models behaved differently. Kimi K2.6 mostly escalated, with local
rejection differences at E1, E2, and E4. Gemini 2.5 Flash also mostly
escalated, with only three total rejections across the full run. Devstral 2
escalated on all 686 records. This saturation is a software-quality result:
a verifier that escalates everything may be safe in the narrow sense of not
accepting questionable patches, but it provides little automation value as a
merge gate.

\begin{{figure*}}[t]
\centering
\includegraphics[width=\textwidth]{{docs/figures/sqj/sqj_fig2_decision_patterns.pdf}}
\caption{{Five-model decision patterns on the frozen EVP-8 v0.1 packet set.
The heatmap reports rejection counts per 98 candidate-level packets; the lower
panel aggregates rejection and escalation counts across models. The pattern is
model-dependent and non-monotonic across E0-E6.}}
\label{{fig:sqj-decision-patterns}}
\end{{figure*}}

\input{{generated_tables.tex}}

\section{{Software Quality Risks}}

The results expose three risks for LLM-based patch verification. First, model
decisions are conditioned by evidence presentation, so studies that compare
models without controlling evidence visibility may confound model behavior with
prompt context. Second, verifier behavior is model-dependent. A protocol that
induces useful variation in one model can produce near-total escalation in
another. Third, more evidence does not automatically imply a better verifier
decision. The observed E0-E6 patterns require calibrated interpretation rather
than a single ranked evidence level.

Cost observability is also part of software quality for LLM verifier pipelines.
The passed-result cost was USD {passed_usd:.6f} excluding Qwen, with Qwen
tracked separately as CNY {qwen_cny:.6f}. Two blocked Kimi attempts consumed
USD {blocked_usd:.6f}, which raised the observable USD total excluding Qwen to
USD {observable_usd:.6f}. The later-model observable USD including blocked
attempts was USD {later_observable:.6f}. These blocked attempts are cost and
execution-risk evidence only; they are not valid model-result records.

\begin{{figure*}}[t]
\centering
\includegraphics[width=0.92\textwidth]{{docs/figures/sqj/sqj_fig3_cost_boundary.pdf}}
\caption{{Cost-observability and result-validity boundary for EVP-8. Passed
model results and blocked Kimi attempts are tracked separately. Blocked
attempts contribute to engineering-risk and cost accounting, but are excluded
from five-model decision-pattern synthesis.}}
\label{{fig:sqj-cost-boundary}}
\end{{figure*}}

\section{{Threats to Validity}}

The main internal-validity risk is that the evidence ladder may interact with
the prompt, output schema, or model-specific response style. We address this by
using a frozen packet set, one prompt version, raw-output-free summaries, and
post-run audits, but the result remains tied to this protocol version.

Construct validity is limited by the merge-gate decision space. Accept,
reject, and escalate are useful for verifier studies, but they do not capture
all forms of developer review. In this run, no model emitted accept decisions,
so the EVP-8 result primarily characterizes escalation and rejection behavior.

External validity is bounded by the 98-candidate EVP-8 v0.1 set and by the
five selected models. The result should be read as evidence that visibility
matters and that models differ, not as a universal ranking of evidence levels
or models.

\section{{Artifact and Reproducibility}}

The tracked artifacts include the frozen EVP-8 protocol summaries, five-model
synthesis, generated paper tables, and cost accounting summaries. Raw model
responses remain outside the tracked artifact boundary. The current draft is
generated from {repo_relative(framing_path)}, {repo_relative(tables_tex_path)},
{repo_relative(REPO_ROOT / "data" / "protocols" / "evp8_five_model_synthesis_v0_1.json")},
and {repo_relative(REPO_ROOT / "data" / "reviews" / "evp8_cost_accounting_summary.json")}.

\section{{Conclusion}}

This study shows that evidence visibility is a first-order variable in
LLM-based patch verification. Across five models and seven evidence levels,
merge-gate decisions changed with evidence exposure, but the response was
model-dependent and non-monotonic. The result supports a software quality view
of LLM verifiers: a verifier must be evaluated together with the evidence it
sees, the boundaries of hidden evaluator labels, and the cost and execution
risks of the evaluation pipeline.

\backmatter

\bmhead{{Data availability}}

The submission draft is generated from tracked raw-output-free summaries and
paper tables in the project repository. Raw model responses, local API
configuration, and ignored execution logs are excluded from the tracked
artifact boundary.

\bmhead{{Code availability}}

The draft-generation command is \verb|python scripts\write_sqj_latex_draft.py --check|.
The resulting source file is \verb|docs/paper/sqj_submission_draft.tex|.

\bmhead{{Competing interests}}

The authors declare no competing interests. This statement must be confirmed
before submission.

\bmhead{{Author contributions}}

Author contribution statements are placeholders in this draft and must be
completed before submission.

\bmhead{{Funding}}

Funding information is not specified in this draft and must be completed before
submission.

\bibliography{{sqj_references}}

\end{{document}}
"""


def validate_draft(text: str) -> list[str]:
    errors: list[str] = []
    for snippet in REQUIRED_SNIPPETS:
        if snippet not in text:
            errors.append(f"missing required snippet: {snippet}")
    for snippet in FORBIDDEN_SNIPPETS:
        if snippet in text:
            errors.append(f"forbidden snippet present: {snippet}")
    if "scale generalization" not in text and "broad scale generalization" not in text:
        errors.append("missing scale-generalization boundary phrasing")
    if "not valid model-result records" not in text:
        errors.append("missing blocked-attempt validity boundary")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the SQJ Springer Nature LaTeX draft.")
    parser.add_argument("--synthesis", default="data/protocols/evp8_five_model_synthesis_v0_1.json")
    parser.add_argument("--cost-accounting", default="data/reviews/evp8_cost_accounting_summary.json")
    parser.add_argument("--tables-tex", default="docs/paper/generated_tables.tex")
    parser.add_argument("--framing", default="docs/paper/sqj_submission_framing.md")
    parser.add_argument("--out", default="docs/paper/sqj_submission_draft.tex")
    parser.add_argument("--bib-out", default="docs/paper/sqj_references.bib")
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    synthesis_path = Path(args.synthesis)
    cost_path = Path(args.cost_accounting)
    tables_path = Path(args.tables_tex)
    framing_path = Path(args.framing)
    draft = build_draft(
        read_json(synthesis_path),
        read_json(cost_path),
        tables_path,
        framing_path,
    )
    errors = validate_draft(draft)
    if errors:
        raise SystemExit("SQJ draft validation failed: " + "; ".join(errors))
    write_text(Path(args.out), draft)
    write_text(Path(args.bib_out), build_bibtex())
    print(
        json.dumps(
            {
                "api_call_attempted": False,
                "bib_out": args.bib_out,
                "compile_attempted": False,
                "out": args.out,
                "passed": True,
                "reason": "sn-jnl.cls is not bundled locally; this check validates source structure only.",
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
