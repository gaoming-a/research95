# CCF-C Manuscript Revision Response v0.2

Date: 2026-07-03

## Scope

This note records the response to the external critique that the previous
draft still read like an experiment audit report rather than a CCF-C paper. The
revision uses only tracked aggregate artifacts. It does not call APIs, read raw
model outputs, change experimental results, or report unimplemented baselines
as completed evidence.

## One-Sentence Argument

EVP-8 is a hidden-evaluator evidence-visibility protocol showing that LLM
candidate-patch verification behavior is evidence-conditioned, model-dependent,
and often conservative; its strongest supported value is risk triage under
explicit evidence boundaries, not reliable autonomous patch correctness
verification.

## Critique-To-Action Map

| critique | action in v0.2 | status |
| --- | --- | --- |
| The draft reads like an audit report rather than a paper. | Rewrote the abstract, experimental design, results, discussion, and conclusion around a methods-and-measurement contribution. | addressed |
| The contribution is unclear. | Fixed the contribution as EVP-8 plus hidden-evaluator evidence visibility, label-conditioned metrics, and risk-triage boundary. | addressed |
| The zero-accept five-model result is too weak as the main result. | Removed the legacy v0.1 five-model synthesis from the main results. It is now explicit diagnostic history only. | addressed |
| Accept-aware v0.2/v0.3 results should become main evidence. | Added a Qwen v0.3 table with accept, correct accept, false accept, accepted precision, correct recall, false accept rate, and escalation rate. | addressed |
| E0-E6 evidence levels need transparent definition. | Added an E0-E6 protocol table generated from `data/protocols/evp8_protocol_v0_3_qwen_first.json`. | addressed |
| Metrics need FAR, accepted precision, correct recall, false reject, escalation, and invalid-output boundary. | Main tables now include accepted precision, correct recall, false accept rate, escalation rate; claim map also records checks for parse/run coverage and raw-output-free summaries. | partially addressed |
| The figure package still risks carrying v0.1 back into the paper. | Replaced Fig. 2 with an accept-aware/no-verdict metric figure based on Qwen v0.3 and E6 ablation metrics. | addressed |
| Verdict-like tool summaries may anchor behavior. | Added RQ3 with rule-only, E6-full, and E6-no-verdict metrics. | addressed |
| Tool-contestation should be interpreted as triage, not correction. | RQ4 states that known false accepts moved mainly to escalation and not strict rejection. | addressed |
| Realistic hard-negative branch should not be a main result if the gate failed. | RQ5 and Discussion classify it as source-acquisition/gate-readiness boundary evidence. | addressed |
| More baselines are needed, including always-escalate, random, majority, and E0/no-tool. | v0.2 explicitly says these are not tracked completed results; they remain submission-risk follow-up work. | deferred |
| Related work is too thin. | Expanded related-work scaffold around APR plausible patches, testing/semantic evidence, LLM-as-reviewer/judge, and selective triage. Citations still need to be inserted from verified sources. | partially addressed |
| Venue target should be concrete. | The manuscript stays venue-neutral as a stable CCF-C route; venue-specific formatting and official list confirmation remain outside this no-web, no-submission round. | deferred |

## Remaining Submission Risks

- Related work still needs verified citations before submission.
- The paper has only a rule-only baseline in tracked E6 ablation artifacts; it
  does not yet have always-escalate, random, majority, or full E0/no-tool
  baselines.
- Phase A confidence intervals are tracked, but the manuscript currently keeps
  them in supporting evidence rather than a full statistics subsection.
- The realistic hard-negative branch remains below the predeclared
  three-project verifier-readiness gate.
- The legacy v0.1 zero-accept setting is excluded from the main result chain;
  it may only be mentioned as protocol history explaining why accept-aware
  repair was required.
- The final venue choice and template requirements still need external
  confirmation before producing a submission package.

## Updated Files

- `scripts/write_final_manuscript_claim_map.py`
- `data/reviews/final_manuscript_claim_map_v0_1.json`
- `docs/paper/final_manuscript_claim_map_v0_1.md`
- `docs/paper/ccfc_manuscript_rewrite_v0_1.md`
