# EVP-8 Realistic Agent Generation Execution Packet v0.1

Date: 2026-06-29

This is a no-API execution packet. It freezes the future patch-generation
command and gates, but it does not authorize API execution.

- status: `ready`
- execution authorized by packet: `False`
- verifier API authorized: `False`
- model: `qwen3.7-max`
- provider: `qwen_official`
- planned generation slots: 54

## Checks

- api_call_not_attempted_by_packet: passed (False)
- execution_authorized_by_packet_false: passed (False)
- target_matrix_passed: passed (passed)
- dry_run_audit_passed: passed (passed)
- planned_generation_slots_54: passed (54)
- execute_command_uses_execute: passed (command redacted to separate section)
- execution_output_dir_absent: passed (outputs/evp8_realistic_agent_generation_qwen_primary_001)
- credential_presence_ready: passed (QWEN_API_KEY)

## Execute Command

```powershell
python scripts\generate_agent_patch_candidates.py --execute --out-dir outputs\evp8_realistic_agent_generation_qwen_primary_001 --run-id evp8_realistic_agent_generation_qwen_primary_001 --api-provider qwen_official --model qwen3.7-max --patches-per-task 9 --task-id bugsinpy_PySnooper_1 --task-id bugsinpy_PySnooper_3 --task-id bugsinpy_cookiecutter_1 --task-id bugsinpy_cookiecutter_2 --task-id bugsinpy_cookiecutter_3 --task-id bugsinpy_tqdm_9
```

## Target Tasks

- `bugsinpy_PySnooper_1`
- `bugsinpy_PySnooper_3`
- `bugsinpy_cookiecutter_1`
- `bugsinpy_cookiecutter_2`
- `bugsinpy_cookiecutter_3`
- `bugsinpy_tqdm_9`

## Stop Gates

- Do not run this command unless the user explicitly authorizes realistic agent-patch generation API execution.
- If generation_error.json is created, stop and diagnose generation failure before retrying.
- Do not commit raw responses or ignored output directories.
- After generation, validate and relabel candidates before constructing any realistic verifier cohort.
- Do not run Qwen/DeepSeek verifier APIs from this generation packet.

## Required After Generation

- validate generated candidates
- relabel with evaluator-only hidden outcomes
- rerun realistic source inventory
- construct separated evaluator/model-visible cohort only if fresh gates pass
- build visible-tool baseline before verifier APIs
