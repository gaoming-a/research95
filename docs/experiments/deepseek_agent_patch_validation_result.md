# DeepSeek Agent-Style Patch Validation Result

## Scope

Run id: `httpie_agent_patch_stage_ab_001`.

This validation used the 8 existing DeepSeek official agent-style patch
candidates already generated before the `httpie_5` failure. No new model API
calls were made.

Input:

```text
outputs/httpie_agent_patch_stage_ab_001/candidates.pending.jsonl
```

The 8 candidates cover:

| task | candidates |
|---|---:|
| `bugsinpy_httpie_1` | 2 |
| `bugsinpy_httpie_2` | 2 |
| `bugsinpy_httpie_3` | 2 |
| `bugsinpy_httpie_4` | 2 |

## Validation Result

| metric | value |
|---|---:|
| generated candidates | 8 |
| patch applied | 8 |
| oracle ran | 8 |
| oracle passed | 0 |
| validation status `validated` | 8 |
| relabeled `incorrect` | 8 |
| environment invalid | 0 |

Outputs:

```text
outputs/httpie_agent_patch_stage_ab_001/validation.jsonl
outputs/httpie_agent_patch_stage_ab_001/validation_summary.json
outputs/httpie_agent_patch_stage_ab_001/candidates.relabeled.jsonl
outputs/httpie_agent_patch_stage_ab_001/evidence_packets.relabeled.jsonl
outputs/httpie_agent_patch_stage_ab_001/relabel_summary.json
```

## Interpretation

The coding-agent-style protocol solved the direct-diff materialization problem
for these 8 candidates: every generated patch applied cleanly and every retained
oracle executed.

However, none of the patches fixed the target behavior. The dataset slice is
therefore useful as a source of realistic generated negative patches, not as
evidence that the generator can produce correct repairs.

## Decision

Do not expand this path as the main source of balanced patch candidates yet.

The next paper-safe use is:

- keep real bug/reference patches as the main experimental backbone;
- use AI-generated patches as an extension focused on generated negative or
  partial-fix candidates;
- only promote AI-generated patches to a main dataset source after a future
  generation protocol produces both oracle-passing and oracle-failing patches
  with reproducible validation.

This result completes the four requested checks except remote GitHub sync, which
is currently blocked by failed `github.com:443` connectivity.
