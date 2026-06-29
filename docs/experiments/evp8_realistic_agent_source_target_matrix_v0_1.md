# EVP-8 Realistic Agent-Patch Source Target Matrix v0.1

Date: 2026-06-29

This is a no-API target matrix. It does not generate patches and does not
authorize model calls. It selects stable tasks for future realistic
agent-like patch source construction.

## Boundary Checks

- api_call_not_attempted: passed (False)
- patch_generation_not_attempted: passed (False)
- candidate_manifest_not_created: passed (False)
- prompt_text_not_stored: passed (False)
- source_inventory_detected: passed (passed)
- target_project_count_at_least_3: passed (3)
- planned_generation_slots_at_least_50: passed (54)
- primary_non_httpie_slots_at_least_40: passed (54)

## Strategy

Use non-httpie stable P2P tasks as the main source of new agent-like patches, then add a capped httpie slice only if the non-httpie runner-supported pool cannot reach the 50-slot source target. The current shortest path uses a larger bounded variant budget on the six runner-supported non-httpie tasks instead of expanding the generation runner in this step.

- primary projects: PySnooper, cookiecutter, luigi, tqdm
- secondary projects: httpie
- primary patches per task: 9
- secondary patches per task: 3

## Target Summary

- target tasks: 6
- target projects: 3
- planned generation slots: 54
- primary non-httpie slots: 54
- secondary httpie slots: 0

Project slot counts:

- `PySnooper`: 18
- `cookiecutter`: 27
- `tqdm`: 9

## Targets

| task | project | priority | slots | P2P broad size | existing candidates |
| --- | --- | --- | ---: | ---: | ---: |
| `bugsinpy_PySnooper_1` | `PySnooper` | `primary_non_httpie` | 9 | 24 | 6 |
| `bugsinpy_PySnooper_3` | `PySnooper` | `primary_non_httpie` | 9 | 4 | 4 |
| `bugsinpy_cookiecutter_1` | `cookiecutter` | `primary_non_httpie` | 9 | 290 | 4 |
| `bugsinpy_cookiecutter_2` | `cookiecutter` | `primary_non_httpie` | 9 | 278 | 11 |
| `bugsinpy_cookiecutter_3` | `cookiecutter` | `primary_non_httpie` | 9 | 255 | 4 |
| `bugsinpy_tqdm_9` | `tqdm` | `primary_non_httpie` | 9 | 12 | 7 |

## Excluded Stable Tasks

| task | project | reason |
| --- | --- | --- |
| `bugsinpy_httpie_5` | `httpie` | `known_hard_generation_case_and_p2p_broad_size_3` |
| `bugsinpy_thefuck_1` | `thefuck` | `not_supported_by_current_agent_generation_runner` |
| `bugsinpy_youtube-dl_2` | `youtube-dl` | `not_supported_by_current_agent_generation_runner` |
| `bugsinpy_youtube-dl_4` | `youtube-dl` | `not_supported_by_current_agent_generation_runner` |
| `bugsinpy_youtube-dl_5` | `youtube-dl` | `not_supported_by_current_agent_generation_runner` |
| `bugsinpy_youtube-dl_6` | `youtube-dl` | `not_supported_by_current_agent_generation_runner` |
| `bugsinpy_youtube-dl_7` | `youtube-dl` | `not_supported_by_current_agent_generation_runner` |
| `bugsinpy_youtube-dl_11` | `youtube-dl` | `not_supported_by_current_agent_generation_runner` |
| `bugsinpy_youtube-dl_16` | `youtube-dl` | `not_supported_by_current_agent_generation_runner` |
| `bugsinpy_youtube-dl_17` | `youtube-dl` | `not_supported_by_current_agent_generation_runner` |
| `bugsinpy_youtube-dl_20` | `youtube-dl` | `not_supported_by_current_agent_generation_runner` |
| `bugsinpy_youtube-dl_21` | `youtube-dl` | `not_supported_by_current_agent_generation_runner` |
| `bugsinpy_youtube-dl_23` | `youtube-dl` | `not_supported_by_current_agent_generation_runner` |
| `bugsinpy_youtube-dl_37` | `youtube-dl` | `not_supported_by_current_agent_generation_runner` |
| `bugsinpy_youtube-dl_43` | `youtube-dl` | `not_supported_by_current_agent_generation_runner` |

## Next Gate

Run generator dry-run commands first, then seek explicit API authorization for generation only.

Required after generation:

- validate generated candidates
- relabel with evaluator-only hidden outcomes
- rerun realistic source inventory
- construct separated evaluator/model-visible cohort only if fresh gates pass

No verifier API run is allowed from this matrix alone.
