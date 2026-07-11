# DSA P3 Author Sign-off v0.1

Status: **SIGNED / P3 FREEZE EFFECTIVE**
Prepared: 2026-07-11
Author: 高明
Signed: 2026-07-11T15:00:02+08:00
API calls: none
P4/P5 authorization: none

The author supplied the declaration in the Codex task and explicitly accepted
all 11 frozen items. This record closes only P3; it does not authorize P4, P5,
smoke, full, or any model API call.

## Frozen items to confirm

- [x] `research_questions_claim_boundary`: I accept RQ1--RQ3 and the bounded finite-cohort claim in
  `data/protocols/dsa_p3_preregistration_v0_1.json`.
- [x] `estimands_scientific_unit`: I accept `Delta_minus` and `Delta_plus` as the only primary estimands,
  with task as the only scientific analysis unit and finite-cohort `n=30`.
- [x] `cumulative_evidence_contract`: I accept the cumulative C0--C3 evidence contract in
  `data/protocols/dsa_p3_evidence_contract_v0_1.json`.
- [x] `p2_regular_source_and_transform_freeze`: I accept the P2 Regular source order and the four-transform priority as
  frozen; I will not add a task-specific transform or select by candidate/model
  outcome.
- [x] `outcome_classification`: I accept the primary, secondary, and descriptive-only outcome classes.
- [x] `conditional_interval_and_stability`: I accept the 20,000-draw paired repeat-block percentile procedure,
  Bonferroni endpoints 0.0125/0.9875, seed `2026071103`, project-balanced
  reweighting, and leave-one-project-out range boundaries.
- [x] `exclusion_stop_and_no_rerun`: I accept all P4 admission/exclusion, reserve, retry, stop, and no-rerun
  rules, including stopping if 30 complete pairs cannot be materialized.
- [x] `model_routes_parameters_order_and_repeats`: I accept the three exact model routes, provider-native parameters,
  request-order algorithms, three repeats, identity checks, date window, and
  token/attempt/cost ceilings in `data/protocols/dsa_p3_model_freeze_v0_1.json`.
- [x] `new_prompt_and_output_schema`: I accept the new DSA prompt and five-field output schema and confirm that
  no condition-specific instruction should be added after seeing outputs.
- [x] `unfavorable_result_reporting`: I understand that null, negative, wide, heterogeneous, or otherwise
  unfavorable results will be reported and will not trigger a replacement run.
- [x] `scientific_ai_and_authorship_responsibility`: I can independently inspect the protocol and artifacts, will verify every
  paper claim, will comply with the venue's final AI policy, and accept full
  scientific and authorship responsibility.

## Signing record

- Source: `codex_user_message`.
- Exact declaration: `data/protocols/dsa_p3_author_declaration_v0_1.txt`.
- Canonicalization: UTF-8 exact user message with terminal CR/LF removed.
- SHA-256: `48b19341bdd25e26f8fb2d1412ae8b30d462d8b40e7400f2002e25fb2e522e52`.
- Scientific and authorship responsibility: confirmed by 高明.
