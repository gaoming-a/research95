# DSA P3 Author Sign-off v0.1

Status: **PENDING AUTHOR SIGN-OFF**
Prepared: 2026-07-11
API calls: none
P4/P5 authorization: none

This sheet is the only remaining non-mechanical P3 Gate. Please review the
machine-readable sources named below before signing. Codex cannot sign or
assume scientific responsibility for the author.

## Frozen items to confirm

- [ ] `research_questions_claim_boundary`: I accept RQ1--RQ3 and the bounded finite-cohort claim in
  `data/protocols/dsa_p3_preregistration_v0_1.json`.
- [ ] `estimands_scientific_unit`: I accept `Delta_minus` and `Delta_plus` as the only primary estimands,
  with task as the only scientific analysis unit and finite-cohort `n=30`.
- [ ] `cumulative_evidence_contract`: I accept the cumulative C0--C3 evidence contract in
  `data/protocols/dsa_p3_evidence_contract_v0_1.json`.
- [ ] `p2_regular_source_and_transform_freeze`: I accept the P2 Regular source order and the four-transform priority as
  frozen; I will not add a task-specific transform or select by candidate/model
  outcome.
- [ ] `outcome_classification`: I accept the primary, secondary, and descriptive-only outcome classes.
- [ ] `conditional_interval_and_stability`: I accept the 20,000-draw paired repeat-block percentile procedure,
  Bonferroni endpoints 0.0125/0.9875, seed `2026071103`, project-balanced
  reweighting, and leave-one-project-out range boundaries.
- [ ] `exclusion_stop_and_no_rerun`: I accept all P4 admission/exclusion, reserve, retry, stop, and no-rerun
  rules, including stopping if 30 complete pairs cannot be materialized.
- [ ] `model_routes_parameters_order_and_repeats`: I accept the three exact model routes, provider-native parameters,
  request-order algorithms, three repeats, identity checks, date window, and
  token/attempt/cost ceilings in `data/protocols/dsa_p3_model_freeze_v0_1.json`.
- [ ] `new_prompt_and_output_schema`: I accept the new DSA prompt and five-field output schema and confirm that
  no condition-specific instruction should be added after seeing outputs.
- [ ] `unfavorable_result_reporting`: I understand that null, negative, wide, heterogeneous, or otherwise
  unfavorable results will be reported and will not trigger a replacement run.
- [ ] `scientific_ai_and_authorship_responsibility`: I can independently inspect the protocol and artifacts, will verify every
  paper claim, will comply with the venue's final AI policy, and accept full
  scientific and authorship responsibility.

## Signing instruction

Reply in the Codex task with the following exact declaration, adding your name:

> 我作为作者【姓名】签核 DSA P3 v0.1 的全部 11 项冻结内容；我已审查研究问题、
> estimands、C0--C3、P2 transform priority、指标、统计、exclusion、停止与 no-rerun、
> 三条 exact model route、prompt/schema，并愿意独立核验全部结果和论文主张、遵守最终
> AI 政策并承担完整科学与作者责任。我理解该签核只授权完成 P3，不授权调用模型 API，
> 也不授权顺手进入 P4 或 P5。

After that declaration, the repository record will be updated with the author
name, timestamp, immutable hashes, and final P3 Gate. Until then P3 remains
pending, even if every mechanical audit passes.
