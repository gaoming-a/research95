# EVP-8 Realistic Agent Validation/Relabel Audit v0.2

- status: `passed`
- raw output content stored: `false`
- patch text stored: `false`
- prompt text stored: `false`

## Validation

- records: 10
- patch applied: 10
- oracle ran: 10
- oracle passed: 0
- initial-label status counts: `{'validated': 10}`

## Relabel

- expected outcome counts: `{'incorrect': 10}`
- environment invalid: 0
- ready for revalidation: `True`

## Source Readiness

- fresh usable candidates: 53
- fresh agent-like candidates: 53
- fresh non-trivial hard negatives: 53
- fresh projects: 3
- ready for Phase 1 curation: `True`
- ready for API: `False`

## Checks

- generation_audit_passed: passed (passed)
- validation_record_count_matches_expected: passed (10)
- validation_all_patches_applied: passed (10)
- validation_all_oracles_ran: passed (10)
- relabel_candidate_count_matches_expected: passed (10)
- relabel_no_environment_invalid: passed (0)
- relabel_ready_for_revalidation: passed (True)
- source_inventory_passed: passed (passed)
- fresh_agent_like_at_least_30: passed ({'fresh_agent_like_candidates': 53, 'fresh_nontrivial_hard_negatives': 53, 'fresh_project_count': 3, 'fresh_usable_candidates': 53, 'pending_agent_like_candidates': 13, 'pending_nontrivial_hard_negatives': 13, 'pending_usable_candidates': 13})
- fresh_hard_negatives_at_least_25: passed ({'fresh_agent_like_candidates': 53, 'fresh_nontrivial_hard_negatives': 53, 'fresh_project_count': 3, 'fresh_usable_candidates': 53, 'pending_agent_like_candidates': 13, 'pending_nontrivial_hard_negatives': 13, 'pending_usable_candidates': 13})
- fresh_projects_at_least_3: passed ({'fresh_agent_like_candidates': 53, 'fresh_nontrivial_hard_negatives': 53, 'fresh_project_count': 3, 'fresh_usable_candidates': 53, 'pending_agent_like_candidates': 13, 'pending_nontrivial_hard_negatives': 13, 'pending_usable_candidates': 13})

## Next Step

construct a separated evaluator/model-visible realistic cohort manifest and visible-tool baseline
