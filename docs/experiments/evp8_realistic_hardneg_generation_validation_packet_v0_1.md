# EVP-8 Realistic Hard-Negative Generation/Validation Packet v0.1

Date: 2026-06-30

This is a no-API packet. It records the broad API authorization but does
not use it. The packet is for future patch generation only; verifier API
execution remains blocked until a fresh visible-pass/hidden-fail gate passes.

- status: `ready_for_generation_api`
- generation API authorized by packet: `False`
- verifier API ready: `False`
- model/provider: `qwen3.7-max` / `qwen_official`
- planned slots: 54
- variant start index: 13
- model candidate start index: 3001

## Checks

- api_call_not_attempted_by_packet: passed (False)
- execution_authorized_by_packet_false: passed (False)
- opportunity_inventory_passed: passed (passed)
- current_verifier_api_not_ready: passed (False)
- target_matrix_passed: passed (passed)
- dry_run_audit_passed: passed (passed)
- dry_run_uses_expected_run_id: passed (evp8_realistic_hardneg_generation_dryrun_qwen_001)
- dry_run_prompt_count_expected: passed (54)
- dry_run_candidate_count_zero: passed (0)
- generation_execution_output_dir_absent: passed (outputs/evp8_realistic_hardneg_generation_qwen_001)
- validation_output_dir_absent: passed (outputs/evp8_realistic_hardneg_validation_qwen_001)
- credential_presence_ready: passed (QWEN_API_KEY)

## Generation Command

```powershell
python scripts\generate_agent_patch_candidates.py --execute --out-dir outputs/evp8_realistic_hardneg_generation_qwen_001 --run-id evp8_realistic_hardneg_generation_qwen_001 --api-provider qwen_official --model qwen3.7-max --patches-per-task 9 --variant-start-index 13 --model-candidate-start-index 3001 --task-id bugsinpy_PySnooper_1 --task-id bugsinpy_PySnooper_3 --task-id bugsinpy_cookiecutter_1 --task-id bugsinpy_cookiecutter_2 --task-id bugsinpy_cookiecutter_3 --task-id bugsinpy_tqdm_9
```

## Post-Generation Commands

### generation_result_audit

```powershell
python scripts\audit_evp8_realistic_agent_generation_results.py --run-dir outputs/evp8_realistic_hardneg_generation_qwen_001 --out-json data\protocols\evp8_realistic_hardneg_generation_result_audit_v0_1.json --out-md docs\experiments\evp8_realistic_hardneg_generation_result_audit_v0_1.md --expected-run-id evp8_realistic_hardneg_generation_qwen_001 --expected-model qwen3.7-max --expected-provider qwen_official --expected-slots 54 --expected-task-count bugsinpy_PySnooper_1=9 --expected-task-count bugsinpy_PySnooper_3=9 --expected-task-count bugsinpy_cookiecutter_1=9 --expected-task-count bugsinpy_cookiecutter_2=9 --expected-task-count bugsinpy_cookiecutter_3=9 --expected-task-count bugsinpy_tqdm_9=9 --check
```

### validate_generated_candidates

```powershell
python scripts\validate_patch_candidates.py --candidates outputs/evp8_realistic_hardneg_generation_qwen_001/candidates.pending.jsonl --workdir-root outputs/evp8_realistic_hardneg_validation_qwen_001/workdirs --out outputs/evp8_realistic_hardneg_validation_qwen_001/validation.jsonl --summary-out outputs/evp8_realistic_hardneg_validation_qwen_001/validation_summary.json
```

### relabel_generated_candidates

```powershell
python scripts\relabel_ai_patch_candidates.py --pending-candidates outputs/evp8_realistic_hardneg_generation_qwen_001/candidates.pending.jsonl --validation outputs/evp8_realistic_hardneg_validation_qwen_001/validation.jsonl --out-candidates outputs/evp8_realistic_hardneg_validation_qwen_001/candidates.relabeled.jsonl --out-evidence-packets outputs/evp8_realistic_hardneg_validation_qwen_001/evidence_packets.relabeled.jsonl --summary-out outputs/evp8_realistic_hardneg_validation_qwen_001/relabel_summary.json
```

### source_inventory_after_generation

```powershell
python scripts\inventory_evp8_realistic_agent_sources.py --out-json data\protocols\evp8_realistic_hardneg_source_inventory_after_generation_v0_1.json --out-md docs\experiments\evp8_realistic_hardneg_source_inventory_after_generation_v0_1.md --check
```

## Hard-Negative Filter Gate

- required property: `patch_applies && declared_visible_tests_pass && hidden_oracle_fails`
- minimum visible-pass/hidden-fail candidates: 30
- minimum projects: 3
- verifier API blocked until gate passes: `True`

## Stop Gates

- This packet does not authorize API execution by itself.
- If generation_error.json appears, stop and diagnose before retrying or resuming.
- Do not commit outputs/ raw responses, workdirs, pending candidates, or relabeled local candidate files.
- Do not construct a verifier cohort from relabel output until corrected oracle and visible-test consistency are audited.
- Do not run Qwen/DeepSeek verifier APIs until the hard-negative filter gate passes.
