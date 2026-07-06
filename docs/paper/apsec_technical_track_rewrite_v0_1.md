# Evidence Visibility Shapes Risk Behavior in a Controlled LLM Patch-Verifier Study

Draft status: APSEC technical-track Markdown rewrite v0.1, 2026-07-05.

Target format note: this draft is shaped for an APSEC-style technical research paper. The companion IEEEtran/BibTeX/page-budget draft package is generated separately; this Markdown file is not the final PDF.

## Abstract

Patch-verification decisions made by large language models (LLMs) are meaningful only relative to the evidence visible at review time. Existing evaluations often report whether an LLM accepts or rejects a patch without making this evidence boundary explicit, which makes it difficult to separate model capability from visible-test evidence, tool-summary anchoring, or prompt-induced caution. This paper introduces the Evidence-Visibility Protocol (EVP-8), a hidden-evaluator protocol for candidate patch verification. EVP-8 reviews 98 candidate patches across seven cumulative evidence levels while withholding evaluator-only correctness labels until post-decision analysis. In three repaired v0.3 runs, Qwen reached 95.24% E6 correct recall with 83.33% accepted precision, DeepSeek reached 80.95% E6 correct recall with 80.95% accepted precision, and Gemini reached 95.24% E6 correct recall with 80.00% accepted precision. The three models still accepted 4-5 of 77 non-correct candidates at E6. E6 rule-only, no-verdict, and coverage-contestation ablations show that verdict-like tool summaries and prompt framing can strongly shift risk policy: the coverage-contestation condition removed repeated false accepts on current-98, but mainly by rejecting or escalating most correct patches. These results support a bounded software-engineering claim: in this controlled LLM patch-verifier study, evidence visibility should be treated as an experimental variable for risk control, not as proof of general autonomous correctness verification.

## 1. Introduction

Automated patch generation and LLM-assisted review are increasingly positioned near software merge decisions. This creates a practical software-quality question: when a candidate patch appears plausible, which visible evidence is sufficient for a verifier to accept it rather than reject it or escalate it for human review? Prior automated program repair work has shown that plausible or test-passing patches can still be incorrect [qi_issta_2015_patch_plausibility; legoues_icse_2012_genprog], so a merge decision cannot be reduced to surface plausibility alone.

The difficulty is not only whether an LLM can read code. It is that a verifier's decision may change when issue context, patch structure, static status, visible tests, regression checks, diagnostics, or tool summaries become visible. If these evidence fields are not controlled, an evaluation may conflate model judgment with evidence presentation. In particular, authoritative-looking tool summaries can encourage acceptance even when the underlying semantic correctness remains unknown.

This paper studies candidate patch verification as an evidence-conditioned merge-gate task. A verifier receives a candidate patch and a predefined model-visible evidence packet, then emits one of three decisions: accept, reject, or escalate. Correctness labels and hidden evaluator outcomes are joined only after the decision. This design follows the intuition behind reject-option and selective-classification settings [chow_tit_1970_reject_option; geifman_el_yaniv_2017_selective_classification], but applies it to software patch verification. The current empirical scope is intentionally controlled: the paper-facing main result is a three-model repaired v0.3 analysis for Qwen, DeepSeek, and Gemini, supported by E6 ablations and tool-contestation evidence, rather than a broad claim about all LLM verifiers.

The paper makes three contributions:

- It defines EVP-8, a hidden-evaluator evidence-visibility protocol for measuring accept, reject, and escalation behavior in candidate patch verification.
- It reports repaired Qwen, DeepSeek, and Gemini v0.3 label-conditioned results showing that visible executable and tool evidence can unlock correct-patch acceptance while introducing bounded false-accept risk.
- It analyzes E6 rule-only, no-verdict, tool-contestation, and coverage-contestation conditions to separate deterministic tool evidence, verdict-like anchoring, safe handling, strict correction, and prompt-induced conservatism.

The claim is deliberately bounded. The results do not establish reliable autonomous patch correctness verification, nor do they show that LLM decisions consistently outperform deterministic baselines. They show that evidence visibility is a measurable experimental variable that should be controlled and reported in LLM patch-verifier studies.

## 2. Background and Motivation

Automated program repair research has long distinguished plausible patches from correct patches. Generate-and-validate systems and controlled benchmarks have shown that passing available tests may be insufficient for semantic correctness [qi_issta_2015_patch_plausibility; just_issta_2014_defects4j]. EVP-8 studies the downstream verifier setting: after a candidate patch exists, the question is not how it was generated, but whether a merge-gate decision is justified by the evidence visible to the verifier.

Software testing research also motivates the hidden-evaluator design. The oracle problem means that deciding correctness is itself a validity boundary [barr_tse_2015_oracle_problem]. EVP-8 therefore keeps evaluator-only labels separate from model-visible evidence and joins them only after decisions have been produced.

LLM-based repair and code-editing studies show that LLMs can produce or inspect patches [xia_zhang_icse_2023_llm_apr; tufano_icse_2019_bugfix_nmt]. However, verifier behavior is not identical to generation performance. A patch reviewer must decide whether visible evidence is enough to accept, reject, or escalate. This makes the task closer to code review and risk triage than to benchmark success alone [bacchelli_bird_icse_2013_code_review].

Finally, LLM-as-judge and automation-reliance work warn that model judgments and automation outputs require controlled protocols and explicit boundaries [zheng_neurips_2023_llm_judge; parasuraman_riley_1997_automation]. The protocol in this paper responds to that concern by making evidence visibility an explicit variable rather than an implicit property of the prompt.

## 3. Evidence-Visibility Protocol

EVP-8 evaluates a candidate patch under a fixed evidence packet. The model-visible packet contains only the evidence level assigned to that condition. The evaluator-only layer contains hidden correctness labels and oracle outcomes used only after the verifier emits its decision.

![Figure 1. Hidden-evaluator evidence-visibility protocol.](../figures/ccfc/ccfc_fig1_protocol.png)

**Figure 1. Hidden-evaluator evidence-visibility protocol.** Model-visible evidence and evaluator-only labels are separated until post-decision analysis. The model can inspect candidate patches and level-specific evidence, but evaluator labels remain hidden until post-decision analysis.

The reviewed unit is a candidate patch. The decision space is accept, reject, or escalate. Escalation is treated as a human-review routing decision, not as semantic rejection. This distinction is important because safe handling of a risky patch can occur through escalation even when strict correction does not occur.

EVP-8 uses seven cumulative evidence levels:

| level | visible evidence | meaning |
| --- | --- | --- |
| E0 | Issue summary and candidate patch diff | minimal review context |
| E1 | Structured changed-file/function map | patch surface information |
| E2 | Patch application and static-check status | basic feasibility evidence |
| E3 | Visible fail-to-pass test results | issue-relevant executable evidence |
| E4 | Visible pass-to-pass regression results | regression-safety evidence |
| E5 | Additional diagnostics | broader tool evidence |
| E6 | Deterministic merge-gate summary | summarized tool verdict |

The current packet set contains 98 candidate patches from 6 projects and 21 BugsInPy tasks. It contains 21 correct patches and 77 non-correct patches under hidden F2P/P2P-broad evaluator labels. The candidate mix is intentionally skewed toward negative and partial cases because the merge-gate risk is false acceptance rather than classification accuracy on a balanced benchmark.

| candidate type | count | evaluator label | label count | label source | purpose |
| --- | ---: | --- | ---: | --- | --- |
| correct_reference | 21 | correct_under_f2p_and_p2p_broad | 21 | hidden F2P and P2P-broad evaluator labels | measure correct-patch recall |
| buggy_noop | 21 | incorrect_issue_not_fixed | part of 76 issue-not-fixed negatives | hidden evaluator labels | issue-not-fixed false-accept risk |
| irrelevant_patch | 14 | incorrect_issue_not_fixed | part of 76 issue-not-fixed negatives | hidden evaluator labels | plausibility-trap negative patches |
| partial_fix | 41 | incorrect_issue_not_fixed | part of 76 issue-not-fixed negatives | hidden F2P and P2P-broad evaluator labels | semantic incompleteness and partial repair risk |
| regression_patch | 1 | incorrect_regression | 1 | P2P-broad regression label | regression-safety risk |

Five selected models produced complete parse-valid decisions on an earlier frozen E0-E6 packet set, but the paper-facing main result now uses repaired Qwen, DeepSeek, and Gemini v0.3 label-conditioned analyses plus the E6 ablation package. The earlier five-model aggregate synthesis is used only descriptively and not as evidence of final model superiority. The repaired three-model main table removes the previous single-/two-model visibility weakness, but it still does not prove broad LLM superiority over deterministic tool summaries.

## 4. Experimental Design

The experiment asks three research questions. RQ1 asks whether repaired accept-aware evidence changes Qwen, DeepSeek, and Gemini label-conditioned decisions across E0-E6. RQ2 asks whether verdict-like deterministic tool summaries anchor E6 decisions. RQ3 asks whether explicit tool- or coverage-contestation can challenge visible-test-only accept premises, and whether that challenge occurs through strict rejection, safe escalation, or over-conservative recall loss. The fresh realistic hard-negative branch is not treated as a main research question because it did not pass its predeclared source-acquisition gate; it is reported later as a boundary condition.

All metrics are computed after post-decision hidden-label join. The main metrics are accepted precision, correct recall, false accept rate, false reject rate, and escalation rate. Accepted precision measures the correctness of accepted patches. Correct recall measures how many correct patches were accepted. False accept rate measures how often non-correct candidates were accepted. Escalation rate measures routing to human review.

The baseline boundary is explicit. Always-escalate, always-reject, and always-accept are deterministic reference policies calculated from label totals. Uniform random three-way is an expected reference policy, not a stochastic experiment. The completed deterministic baseline is rule-only visible-tool. Qwen E0 is an observed model condition, not a deterministic no-tool verifier. Majority-vote and a separate E0/no-tool deterministic verifier are not reported as completed because current tracked summaries do not contain candidate-level aligned decision records.

| policy or condition | status | accept | reject | escalate | role |
| --- | --- | ---: | ---: | ---: | --- |
| always_escalate | calculable_from_label_totals | 0 | 0 | 98 | conservative abstention reference, not a useful verifier. |
| always_reject | calculable_from_label_totals | 0 | 98 | 0 | safety-heavy lower-bound reference exposing recall collapse. |
| always_accept | calculable_from_label_totals | 98 | 0 | 0 | unsafe throughput reference exposing base-rate risk. |
| uniform_random_three_way_expected | calculable_expected_reference_from_label_totals | 32.666666666666664 | 32.666666666666664 | 32.666666666666664 | sanity-check reference for the decision space, not a completed verifier or a reported stochastic experiment. |
| rule_only_visible_tool | completed_existing_tracked_result | 25 | 73 | 0 | main deterministic baseline for E6 full/no-verdict comparison. |

All paper-facing claims are constrained by a setting-validity audit. The audit checks run coverage, parse validity, raw-output-free summaries, post-execution label joins, prompt-boundary conditions, baseline feasibility, and exclusion of the earlier invalid setting. The audit passed only for bounded claims.

## 5. Results

### 5.1 Visible executable evidence changed three repaired model policies

In the repaired Qwen, DeepSeek, and Gemini v0.3 runs, E0-E2 produced no accepted correct patches for Qwen and DeepSeek and only a single incorrect Gemini accept at E1. Once visible executable evidence entered the packet, all three models began accepting correct patches, but their risk policies diverged. Qwen reached 80.95% correct recall at E3 and 95.24% at E6. DeepSeek reached 61.90% correct recall at E3, became more conservative at E4-E5, and reached 80.95% at E6. Gemini reached 95.24% correct recall from E3 through E6, but accepted five of 77 non-correct candidates at E6. The repaired three-model table therefore strengthens the evidence-visibility finding while preserving the false-accept risk boundary.

| model | E6 accept | E6 correct accept | E6 false accept | E6 accepted precision | E6 correct recall | E6 false accept rate | E6 escalation rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| qwen/qwen3.7-max | 24 | 20 | 4 | 83.33% | 95.24% | 5.19% | 0.00% |
| deepseek/deepseek-v4-pro | 21 | 17 | 4 | 80.95% | 80.95% | 5.19% | 4.08% |
| google/gemini-2.5-flash | 25 | 20 | 5 | 80.00% | 95.24% | 6.49% | 0.00% |

Qwen level-conditioned metrics:

| level | accept | correct accept | false accept | accepted precision | correct recall | false accept rate | escalation rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E0 | 0 | 0 | 0 | n/a | 0.00% | 0.00% | 75.51% |
| E1 | 0 | 0 | 0 | n/a | 0.00% | 0.00% | 75.51% |
| E2 | 0 | 0 | 0 | n/a | 0.00% | 0.00% | 74.49% |
| E3 | 20 | 17 | 3 | 85.00% | 80.95% | 3.90% | 4.08% |
| E4 | 21 | 18 | 3 | 85.71% | 85.71% | 3.90% | 2.04% |
| E5 | 21 | 18 | 3 | 85.71% | 85.71% | 3.90% | 3.06% |
| E6 | 24 | 20 | 4 | 83.33% | 95.24% | 5.19% | 0.00% |

DeepSeek level-conditioned metrics:

| level | accept | correct accept | false accept | accepted precision | correct recall | false accept rate | escalation rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E0 | 0 | 0 | 0 | n/a | 0.00% | 0.00% | 96.94% |
| E1 | 0 | 0 | 0 | n/a | 0.00% | 0.00% | 98.98% |
| E2 | 0 | 0 | 0 | n/a | 0.00% | 0.00% | 98.98% |
| E3 | 16 | 13 | 3 | 81.25% | 61.90% | 3.90% | 8.16% |
| E4 | 7 | 7 | 0 | 100.00% | 33.33% | 0.00% | 18.37% |
| E5 | 1 | 1 | 0 | 100.00% | 4.76% | 0.00% | 24.49% |
| E6 | 21 | 17 | 4 | 80.95% | 80.95% | 5.19% | 4.08% |

Gemini level-conditioned metrics:

| level | accept | correct accept | false accept | accepted precision | correct recall | false accept rate | escalation rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E0 | 0 | 0 | 0 | n/a | 0.00% | 0.00% | 98.98% |
| E1 | 1 | 0 | 1 | 0.00% | 0.00% | 1.30% | 95.92% |
| E2 | 0 | 0 | 0 | n/a | 0.00% | 0.00% | 98.98% |
| E3 | 25 | 20 | 5 | 80.00% | 95.24% | 6.49% | 3.06% |
| E4 | 25 | 20 | 5 | 80.00% | 95.24% | 6.49% | 0.00% |
| E5 | 25 | 20 | 5 | 80.00% | 95.24% | 6.49% | 0.00% |
| E6 | 25 | 20 | 5 | 80.00% | 95.24% | 6.49% | 0.00% |

![Figure 2. Accept-aware and no-verdict metric evidence.](../figures/ccfc/ccfc_fig2_decision_patterns.png)

**Figure 2. Accept-aware and no-verdict metric evidence.** Repaired evidence unlocks Qwen correct-patch acceptance while E6 ablations expose verdict-dependent risk tradeoffs. The figure emphasizes the main tradeoff: more visible evidence enabled correct accepts, but acceptance remained bounded by false-accept risk.

The three-model result supports an evidence-visibility claim, not a monotonic correctness claim. More evidence changed policy behavior and unlocked acceptance, but DeepSeek's E4-E5 conservatism and the shared partial/regression false accepts show that visible evidence did not become a correctness oracle.

### 5.2 Verdict-like evidence affected policy behavior

The E6 ablation is a separate verdict-field ablation package rather than the repaired v0.3 E0-E6 main table. It compares the deterministic rule-only visible-tool baseline, full E6 model conditions, and E6-no-verdict conditions to test whether model decisions add value beyond following visible tool verdict fields. Therefore, the DeepSeek E6-full row below should be read as ablation evidence, while the repaired v0.3 DeepSeek E6 row in Section 5.1 is the main E0-E6 evidence-visibility result.

| condition | accept | reject | escalate | accepted precision | correct recall | false accept rate | escalation rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| rule-only | 25 | 73 | 0 | 80.00% | 95.24% | 6.49% | 0.00% |
| deepseek/deepseek-v4-pro E6-full | 23 | 75 | 0 | 82.61% | 90.48% | 5.19% | 0.00% |
| deepseek/deepseek-v4-pro E6-no-verdict | 11 | 73 | 14 | 100.00% | 52.38% | 0.00% | 14.29% |
| qwen/qwen3.7-max E6-full | 24 | 74 | 0 | 83.33% | 95.24% | 5.19% | 0.00% |
| qwen/qwen3.7-max E6-no-verdict | 23 | 74 | 1 | 82.61% | 90.48% | 5.19% | 1.02% |

Qwen E6-full and rule-only produced similar correct recall, accepted precision, and false accept rates. Qwen E6-no-verdict remained close to Qwen E6-full. DeepSeek E6-no-verdict removed false accepts in this cohort, but correct recall dropped to 52.38% and escalation increased to 14.29%. The safer behavior therefore appears to be partly abstention-driven rather than strict semantic discrimination.

This is an important negative result for the LLM-verifier claim. The deterministic rule-only baseline was already strong: it reached 95.24% correct recall and 80.00% accepted precision, compared with 95.24% and 83.33% for Qwen E6-full. The current evidence therefore does not justify claiming a large LLM gain over the tool summary. The value of the LLM conditions in this draft is narrower: they expose how model policy changes when verdict-like fields are removed or challenged, and they show whether risky accepts are routed to escalation rather than autonomous acceptance.

The Wilson intervals are wide, so the ablation should be read as bounded risk-policy evidence rather than as a ranking of model quality.

| condition | accepted precision 95% CI | correct recall 95% CI | false accept rate 95% CI | escalation rate 95% CI |
| --- | ---: | ---: | ---: | ---: |
| rule-only | 80.00% [60.87%, 91.14%] | 95.24% [77.33%, 99.15%] | 6.49% [2.81%, 14.32%] | 0.00% [0.00%, 3.77%] |
| qwen/qwen3.7-max E6-full | 83.33% [64.15%, 93.32%] | 95.24% [77.33%, 99.15%] | 5.19% [2.04%, 12.61%] | 0.00% [0.00%, 3.77%] |
| qwen/qwen3.7-max E6-no-verdict | 82.61% [62.86%, 93.02%] | 90.48% [71.09%, 97.35%] | 5.19% [2.04%, 12.61%] | 1.02% [0.18%, 5.56%] |
| deepseek/deepseek-v4-pro E6-full | 82.61% [62.86%, 93.02%] | 90.48% [71.09%, 97.35%] | 5.19% [2.04%, 12.61%] | 0.00% [0.00%, 3.77%] |
| deepseek/deepseek-v4-pro E6-no-verdict | 100.00% [74.12%, 100.00%] | 52.38% [32.37%, 71.66%] | 0.00% [0.00%, 4.75%] | 14.29% [8.70%, 22.56%] |

### 5.3 Tool-contestation shifted risky accepts to escalation, not strict correction

On the EVP-8-HARD cohort, tool-contestation evaluated 47 candidates for both Qwen and DeepSeek. For the known tool false-accept opportunity set, DeepSeek shifted 9 tool false accepts to 9 escalations and 0 strict rejects. Qwen shifted 9 tool false accepts to 8 escalations, with 0 strict rejects and 1 repeated accept.

This result supports safe handling through escalation. It does not support a claim that tool-contestation reliably identifies semantic incorrectness, because strict correction remained zero for both models.

| model | opportunity cases | safe handling 95% CI | strict correction 95% CI | repeated accept 95% CI |
| --- | ---: | ---: | ---: | ---: |
| deepseek/deepseek-v4-pro | 9 | 100.00% [70.09%, 100.00%] | 0.00% [0.00%, 29.91%] | 0.00% [0.00%, 29.91%] |
| qwen/qwen3.7-max | 9 | 88.89% [56.50%, 98.01%] | 0.00% [0.00%, 29.91%] | 11.11% [1.99%, 43.50%] |

### 5.4 Coverage-contestation removed repeated false accepts by becoming highly conservative

The current-98 coverage-contestation condition tested whether a stronger prompt could challenge visible-test-only acceptance without changing the frozen E6/no-verdict packet set. It removed repeated false accepts for Qwen, DeepSeek, and Gemini, reducing the false accept rate on 77 non-correct candidates to 0.00% for all three models. This is prompt-sensitivity evidence, not a new main result, because the same condition also collapsed correct-patch acceptance. DeepSeek and Gemini accepted no correct patches, and Qwen accepted only 2 of 21 correct patches.

| model | accept | reject | escalate | repeated false accept | strict reject on wrong | safe escalation on wrong | correct recall | correct recall loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| deepseek/deepseek-v4-pro | 0 | 73 | 25 | 0.00% | 93.51% | 6.49% | 0.00% | 100.00% |
| google/gemini-2.5-flash | 0 | 73 | 25 | 0.00% | 93.51% | 6.49% | 0.00% | 100.00% |
| qwen/qwen3.7-max | 2 | 74 | 22 | 0.00% | 94.81% | 5.19% | 9.52% | 90.48% |

The result answers a narrow prompt-setting question. A model can be instructed to challenge coverage sufficiency and avoid visible-test-only acceptance on this frozen cohort, but the observed mechanism is mostly conservative triage rather than semantic discrimination. Therefore the paper should not claim that coverage-contestation improves autonomous verification. The supported claim is that prompt framing can move false-accept risk into reject/escalate outcomes while imposing a large correct-recall cost.

### 5.5 E6 false accepts were concentrated in partial and regression negatives

The most important failure mode is not the average E6 score but the remaining E6 false accepts among 77 non-correct candidates. Aggregate false-accept anatomy shows that Qwen and DeepSeek each accepted three partial fixes and one regression patch, while Gemini accepted four partial fixes and one regression patch. This breakdown supports the paper's risk framing: visible executable and tool evidence can unlock correct accepts, but summarized tool evidence can still miss semantic incompleteness and regression-safety failures. It remains aggregate anatomy, not a case-level project or rationale table.

| model | partial_fix accepts | regression_patch accepts | total E6 false accepts | what the failure shows |
| --- | ---: | ---: | ---: | --- |
| qwen/qwen3.7-max | 3/41 | 1/1 | 4 | semantic incompleteness and regression-safety failures remain visible-evidence risks |
| deepseek/deepseek-v4-pro | 3/41 | 1/1 | 4 | semantic incompleteness and regression-safety failures remain visible-evidence risks |
| google/gemini-2.5-flash | 4/41 | 1/1 | 5 | semantic incompleteness and regression-safety failures remain visible-evidence risks |

A sanitized case-level analysis is now available for these model-specific false accepts. It records candidate id, project, task, negative type, E6 decision, no-verdict decision where available, and compressed rationale categories, but excludes raw response text, full rationale text, rendered prompts, patch diffs, and credentials. The case rows show repeated risk concentration in the same regression case and several youtube-dl partial fixes; they support failure anatomy, not a claim that the complete model rationale has been audited semantically.

### 5.6 Realistic hard-negative acquisition remained a boundary

The fresh realistic branch produced 26 visible-pass/hidden-fail cases across 2 projects. This missed the predeclared verifier-readiness gate of 30 cases across 3 projects. The branch is therefore reported as a source-acquisition boundary rather than a main verifier experiment.

## 6. Discussion

The main implication is that LLM patch verification should be evaluated with explicit evidence boundaries. The same candidate patch may be treated differently when visible tests, regression checks, diagnostics, or deterministic tool summaries are introduced. Reporting only an aggregate accept/reject rate would hide this dependence.

The results also clarify the role of escalation. Escalation can be useful for software-quality workflows because it routes risky cases away from autonomous acceptance. However, escalation is not strict correction, and aggressive contestation can destroy correct-patch recall. This distinction matters for deployment: a verifier that escalates risky candidates may reduce unsafe automation, but it has not proven semantic incorrectness or preserved useful acceptance.

The strongest current contribution is methodological. EVP-8 provides a reproducible way to separate model-visible evidence from hidden evaluator labels, report accept/reject/escalate outcomes, and connect each claim to a validity gate. This is why the paper is framed as a controlled protocol and measurement study rather than as a new repair or verification algorithm.

Several reviewer concerns remain bounded rather than eliminated. The cohort is small, Wilson intervals are wide, repaired Qwen, DeepSeek, and Gemini are the main model conditions, majority-vote cannot be computed from the current tracked summaries, and the realistic hard-negative branch did not pass the three-project readiness gate. Most importantly, the current paper-facing main result is three-model but still not broad-model. These are not hidden weaknesses; they are the boundary conditions under which the current claims are valid.

![Figure 3. Claim boundary and setting-validity map.](../figures/ccfc/ccfc_fig3_claim_boundary.png)

**Figure 3. Claim boundary and setting-validity map.** Supported findings are bounded by leakage controls, protocol repairs, and remaining external-validity threats. The map separates supported claims from forbidden overclaims and shows why the realistic branch remains a boundary result.

## 7. Threats to Validity

**Internal validity.** Prompt wording, output schema, and evidence formatting may influence decisions. The study mitigates this risk through frozen packets, tracked prompt-boundary checks, parse-validity audits, raw-output-free summaries, and post-decision label joins. These controls reduce setup risk but do not make the results independent of the evaluated protocol versions.

**Construct validity.** The accept/reject/escalate decision space simplifies real review workflows. Escalation is a routing outcome, not proof of semantic rejection. Hidden evaluator labels are used only for post-decision analysis and should not be interpreted as model-visible truth.

**External validity.** The main evidence comes from a 98-candidate EVP-8 cohort, an EVP-8-HARD controlled cohort, and selected model conditions. The repaired E0-E6 main result now covers Qwen, DeepSeek, and Gemini, but it is still not a broad-model result, and the realistic hard-negative branch did not pass its readiness gate. The results therefore support bounded evidence-conditioned risk behavior in a controlled patch-verifier study, not universal LLM patch-verifier reliability.

**Baseline validity.** Rule-only visible-tool is the completed deterministic baseline. Always-* and uniform-random policies are reference policies. Majority-vote and a separate deterministic E0/no-tool verifier remain unavailable under the current tracked-summary boundary.

## 8. Conclusion

This paper introduces EVP-8 as a hidden-evaluator evidence-visibility protocol for candidate patch verification. The repaired Qwen, DeepSeek, and Gemini v0.3 results show that visible executable and tool evidence can unlock correct-patch acceptance while retaining false-accept risk and model-dependent caution. E6 ablations, tool-contestation, and coverage-contestation further show that verdict-like evidence and prompt framing can shape policy behavior, and that safer handling often occurs through escalation or conservative rejection rather than strict semantic correction. The contribution is a reproducible software-engineering protocol for measuring evidence-conditioned risk behavior in a controlled LLM patch-verifier study, not a claim of autonomous patch correctness verification.

The companion IEEEtran/BibTeX/page-budget draft package converts these citation keys into a draft reference file; final submission still requires BibTeX field normalization, PDF compilation, visual page-budget inspection, and double-blind checks.

