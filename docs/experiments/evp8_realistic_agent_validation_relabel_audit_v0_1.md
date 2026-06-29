# EVP-8 Realistic Agent Validation/Relabel Audit v0.1

- status: `passed_needs_more_sources`
- raw output content stored: `false`
- patch text stored: `false`
- prompt text stored: `false`

## Validation

- records: 54
- patch applied: 54
- oracle ran: 54
- oracle passed: 9
- initial-label status counts: `{'label_mismatch': 9, 'validated': 45}`

## Relabel

- expected outcome counts: `{'correct': 9, 'incorrect': 45}`
- environment invalid: 0
- ready for revalidation: `True`

## Source Readiness

- fresh usable candidates: 46
- fresh agent-like candidates: 46
- fresh non-trivial hard negatives: 46
- fresh projects: 3
- ready for Phase 1 curation: `False`
- ready for API: `False`

## Checks

- generation_audit_passed: passed (passed)
- validation_record_count_54: passed (54)
- validation_all_patches_applied: passed (54)
- validation_all_oracles_ran: passed (54)
- relabel_candidate_count_54: passed (54)
- relabel_no_environment_invalid: passed (0)
- relabel_ready_for_revalidation: passed (True)
- source_inventory_v0_2_passed: passed (passed)
- fresh_agent_like_at_least_30: passed ({'fresh_agent_like_candidates': 46, 'fresh_nontrivial_hard_negatives': 46, 'fresh_project_count': 3, 'fresh_usable_candidates': 46, 'pending_agent_like_candidates': 13, 'pending_nontrivial_hard_negatives': 13, 'pending_usable_candidates': 13})
- fresh_hard_negatives_at_least_25: passed ({'fresh_agent_like_candidates': 46, 'fresh_nontrivial_hard_negatives': 46, 'fresh_project_count': 3, 'fresh_usable_candidates': 46, 'pending_agent_like_candidates': 13, 'pending_nontrivial_hard_negatives': 13, 'pending_usable_candidates': 13})
- fresh_projects_at_least_3: passed ({'fresh_agent_like_candidates': 46, 'fresh_nontrivial_hard_negatives': 46, 'fresh_project_count': 3, 'fresh_usable_candidates': 46, 'pending_agent_like_candidates': 13, 'pending_nontrivial_hard_negatives': 13, 'pending_usable_candidates': 13})

## Next Step

add at least four fresh usable realistic candidates or revise the predeclared Phase 1 count gate before constructing the verifier cohort
