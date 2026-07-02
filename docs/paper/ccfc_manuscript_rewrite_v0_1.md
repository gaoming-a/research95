# Evidence Visibility Shapes Risk Behavior in LLM-Based Candidate Patch Verification

Draft status: stable CCF-C manuscript rewrite v0.1, 2026-07-03.

## Abstract

Large language models (LLMs) are increasingly used to review software patches, but a patch-verification decision depends on the evidence visible at review time. We study candidate patch verification as an evidence-conditioned merge-gate task, where a verifier must accept, reject, or escalate a candidate patch while hidden evaluator labels remain withheld until after the decision. Using a frozen EVP-8 packet set with 98 candidate patches, seven evidence levels, and five LLMs, we find that evidence visibility changes decision patterns, but not as a monotonic correctness curve. The five-model synthesis passed run, parse, and coverage checks, and aggregate decisions varied across evidence levels. Accept-aware analyses further show why an earlier zero-accept setting should be treated as a protocol artifact rather than a main behavioral finding. In ablations, removing verdict-like fields and adding tool-contestation changed model behavior, but the strongest supported effect was risk triage through escalation rather than strict semantic correction. A fresh realistic hard-negative branch produced 26 visible-pass/hidden-fail cases across two projects, but failed the predeclared three-project verifier-readiness gate. The results support bounded claims about evidence-conditioned risk behavior in LLM-based patch verification, not reliable autonomous correctness verification.

## 1. Introduction

Candidate patches generated or reviewed by automated systems can look plausible while remaining incomplete, irrelevant, or unsafe to merge. This creates a software-quality problem: teams need to decide not only whether a patch resembles a fix, but whether the evidence available at review time is sufficient to accept it. In practice, that evidence may include issue summaries, patch diffs, static checks, visible tests, generated tests, or tool summaries. A verifier that ignores this evidence boundary risks confusing apparent plausibility with correctness.

LLMs are attractive as patch reviewers because they can read code context and produce structured explanations. However, model behavior may depend strongly on what evidence is visible. If a study does not control the model-visible evidence, it becomes difficult to distinguish model capability from evidence presentation, tool-summary anchoring, or prompt-induced caution. This paper therefore treats evidence visibility as the main experimental variable in candidate patch verification.

We study a hidden-evaluator workflow in which model-visible evidence packets are separated from evaluator-only labels. The verifier emits one merge-gate decision: accept, reject, or escalate. Correctness labels, hidden oracle outcomes, and failure taxonomy labels are joined only after execution for analysis. This design lets us ask a bounded question: how does evidence visibility shape LLM risk behavior when reviewing candidate patches?

Our central finding is that evidence visibility changes merge-gate behavior, but the change is model-dependent and non-monotonic. The result is not evidence that LLMs are reliable autonomous patch correctness verifiers. Instead, it supports a software-quality interpretation: LLM verifiers should be evaluated as evidence-conditioned risk controllers whose behavior can shift toward rejection, escalation, or tool-summary dependence depending on the setting.

## 2. Background and Related Work

Patch correctness has long been a central concern in automated program repair and software testing. Generate-and-validate systems can produce plausible patches that pass available tests while failing broader semantic expectations. LLM-based coding agents expand this problem because they can generate fluent explanations and plausible edits, but plausibility is not equivalent to merge readiness.

Existing repair benchmarks primarily evaluate whether a system can resolve a task. The verification problem studied here is adjacent but distinct: given a candidate patch, what decision should a verifier make under a stated evidence boundary? This distinction matters for software quality because a patch-review system may be useful as a triage layer even when it cannot prove correctness.

Prior experiments in this repository also showed that prompt-only or verdict-like settings can create misleading interpretations. We therefore separate paper-facing results from diagnostic protocol history. The manuscript uses accept-aware repaired analyses, no-verdict ablations, tool-contestation audits, and final setting-validity checks to avoid overclaiming from a single prompt or protocol version.

## 3. Evidence-Visibility Protocol

The unit of analysis is a candidate patch reviewed under a predefined evidence packet. Each packet contains only model-visible information for its evidence level, while hidden evaluator labels and oracle outcomes remain unavailable to the model. After the model decision, evaluator-only labels are joined to compute false accepts, correct recall, escalation, and other bounded metrics.

The EVP-8 packet set contains 98 candidate patches reviewed across seven evidence levels, E0 through E6. Five selected models produced 686 parse-valid decisions each on the frozen packet set. The synthesis supports descriptive per-level decision-pattern reporting for the packet set; it does not support broad claims that one evidence level is universally optimal or that LLMs outperform deterministic baselines.

The protocol also distinguishes paper-facing evidence from diagnostic history. Earlier settings that produced zero accept decisions are treated as protocol artifacts unless repaired by accept-aware construction and label-conditioned analysis. This separation is necessary because otherwise a setting artifact could be mistaken for a general property of LLM patch verification.

## 4. Experimental Design

We organize the study around five evidence sources. First, the five-model EVP-8 synthesis measures descriptive decision patterns across seven evidence levels. Second, accept-aware v0.2/v0.3 analyses repair the earlier zero-accept artifact and allow bounded recall and false-accept analysis. Third, E6 no-verdict ablations test whether verdict-like tool summaries anchor model behavior. Fourth, EVP-8-HARD tool-contestation asks whether models challenge visible-test-only accept premises or route risk to escalation. Fifth, the realistic hard-negative branch evaluates whether a fresh source-acquisition pipeline can produce a verifier-ready three-project hard-negative cohort.

All paper-facing claims are constrained by a final setting-validity audit. That audit verifies run and parse coverage, raw-output-free summaries, post-execution label joins, prompt-boundary checks, and the non-overclaiming of the realistic hard-negative branch. It passed only with bounded claims: the results are usable as real evidence for evidence-conditioned risk behavior, not as proof of autonomous correctness verification.

## 5. Results

### 5.1 Evidence visibility changed five-model decision patterns

Across the frozen EVP-8 packet set, aggregate decisions varied by evidence level: E0: escalate=435, reject=55; E1: escalate=416, reject=74; E2: escalate=423, reject=67; E3: escalate=452, reject=38; E4: escalate=446, reject=44; E5: escalate=443, reject=47; E6: escalate=471, reject=19. These totals show that the decision pattern was not a simple monotonic curve from less evidence to more evidence.

The variation was also model-dependent. DeepSeek V4 Pro and Qwen3.7 Max showed visible level-specific changes, whereas Devstral 2 saturated to escalation across the full packet set. Kimi K2.6 and Gemini 2.5 Flash mostly escalated, with limited local rejection differences. This spread is a software-quality result: a verifier can avoid unsafe accepts by escalating, but a system that escalates nearly everything provides limited automation value.

### 5.2 Accept-aware analyses controlled a protocol artifact

The earlier zero-accept behavior is not used as a main behavioral claim. Accept-aware v0.2/v0.3 analyses repair this setting and support bounded label-conditioned interpretation. In the final validity audit, the Qwen label-conditioned matrix had complete candidate-level coverage, no missing or duplicate cells, and hidden labels joined only after execution. This supports the claim that the repaired analyses are interpretable, while the historical zero-accept behavior remains protocol history.

### 5.3 Verdict-like evidence changed policy behavior

The E6 no-verdict ablation shows that verdict-like tool summaries affect model policy behavior. Removing verdict-like fields did not turn the models into reliable semantic verifiers. Instead, it exposed model-dependent tradeoffs between accepting correct patches, rejecting wrong patches, and escalating uncertain cases. This is why the paper reports verdict-full, no-verdict, and tool-contestation conditions separately.

### 5.4 Tool-contestation supported risk triage, not strict correction

On EVP-8-HARD, tool-contestation covered 47 candidates for both Qwen and DeepSeek. For the known tool false-accept opportunity set, DeepSeek shifted 9 tool false accepts to 9 escalations and 0 strict rejects. Qwen shifted 9 tool false accepts to 8 escalations, with 0 strict rejects and 1 repeated accept. The supported interpretation is therefore risk triage through escalation, not semantic correction of wrong patches.

### 5.5 Realistic hard-negative acquisition remained a boundary

The fresh realistic branch produced 26 visible-pass/hidden-fail cases, below the predeclared target of 30, and covered 2 projects rather than the required 3. It is therefore a source-acquisition and gate-readiness negative result, not a verifier-ready main experiment.

## 6. Discussion

The results support a bounded but practically important interpretation. LLM-based patch verifiers are not only functions of model identity; they are functions of the evidence boundary. A model may become conservative, tool-dependent, or saturated depending on how patch evidence is presented. This matters for software quality because a deployment pipeline must decide whether escalation is acceptable, whether tool summaries should be trusted, and when a patch should remain under human review.

The most important rival explanation is that the observed behavior is a setup artifact. The final setting-validity audit reduces this risk but does not erase all limitations. It shows that run coverage, parse validity, post-execution label joins, prompt-boundary checks, and claim boundaries are in place. It also identifies remaining threats: cohort diversity is limited, prompt formatting can influence behavior, and the realistic three-project hard-negative gate remains blocked.

The paper should therefore avoid a stronger interpretation. It does not show that LLMs reliably verify patch correctness. It shows that evidence visibility shapes risk behavior in candidate patch verification and that some apparent improvements are better understood as conservative routing rather than correctness proof.

## 7. Threats to Validity

Internal validity may be affected by prompt wording, output schema, and evidence formatting. We mitigate this by using frozen packet sets, tracked prompt-boundary audits, raw-output-free summaries, and post-run matrix checks, but the findings remain tied to the evaluated protocol versions.

Construct validity is limited by the accept/reject/escalate decision space. Escalation is useful as a human-review routing decision, but it is not strict correction. The manuscript therefore separates strict correction from safe handling.

External validity is bounded by the EVP-8 candidate set, the EVP-8-HARD controlled cohort, and the selected models. The realistic hard-negative branch provides useful source-acquisition evidence but did not pass the three-project verifier-readiness gate. We therefore report it as a negative boundary rather than as main verifier evidence.

Historical protocol versions are treated as diagnostic material. In particular, earlier zero-accept behavior is not used as a main result after accept-aware repair exposed its setting dependence.

## 8. Conclusion

This study shows that evidence visibility is a first-order variable in LLM-based candidate patch verification. Across frozen evidence packets, repaired analyses, no-verdict ablations, and tool-contestation audits, the strongest supported conclusion is that LLM verifier behavior is evidence-conditioned, model-dependent, and often conservative. These findings are useful for software-quality evaluation of LLM review pipelines, but they do not establish reliable autonomous patch correctness verification. A stable CCF-C manuscript should therefore present the work as a bounded empirical study of risk behavior under controlled evidence visibility.

## Planned Figures

Figure generation is pending backend selection. The current figure plan is:

- Fig. 1: Hidden-evaluator evidence-visibility protocol — Model-visible evidence and evaluator-only labels are separated until post-decision analysis.
- Fig. 2: Five-model evidence-level decision patterns — Escalation/rejection patterns vary by model and are non-monotonic across E0-E6.
- Fig. 3: Claim boundary and setting-validity map — Supported findings are bounded by leakage controls, protocol repairs, and remaining external-validity threats.
