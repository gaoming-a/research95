# EVP-8-HARD DeepSeek/Qwen Comparison v0.1

## Scope

- Cohort: `EVP-8-HARD`
- Evidence level: `E6`
- Candidate count: 47
- Models:
  - `qwen/qwen3.7-max`
  - `deepseek/deepseek-v4-pro`
- Raw response policy: ignored raw responses stay under `outputs/`; this
  report uses only tracked raw-output-free summaries, parsed decisions, and the
  post-run audit.

## Run Gate

| Artifact | Status |
|---|---|
| Qwen summary | `passed`, 47/47 parse-valid |
| DeepSeek summary | `passed`, 47/47 parse-valid |
| Combined audit | `passed` |
| Parsed reviews contain raw response text | `false` |
| Audit reads raw model outputs | `false` |

Tracked result files:

- `data/reviews/evp8_hard_qwen_qwen3.7-max_full_summary.json`
- `data/reviews/evp8_hard_qwen_qwen3.7-max_full_reviews.jsonl`
- `data/reviews/evp8_hard_deepseek_deepseek-v4-pro_full_summary.json`
- `data/reviews/evp8_hard_deepseek_deepseek-v4-pro_full_reviews.jsonl`
- `data/protocols/evp8_hard_qwen_deepseek_result_audit_v0_1.json`

## Main Results

| System | Accept | Reject | Escalate | Accepted precision | Correct recall | False accept rate | False reject rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| Tool-only baseline | 17 | 30 | 0 | 47.06% | 80.00% | 24.32% | 20.00% |
| Qwen E6 | 17 | 30 | 0 | 47.06% | 80.00% | 24.32% | 20.00% |
| DeepSeek E6 | 17 | 30 | 0 | 47.06% | 80.00% | 24.32% | 20.00% |

Both LLMs match the tool-only baseline not only in aggregate counts, but also
candidate by candidate.

## Opportunity-Set Result

The hard-case cohort contains 11 actionable tool-baseline mistakes:

- Tool false accepts: 9
- Tool false rejects: 2

Neither model corrected these opportunity cases.

| Model | Tool false accepts corrected to reject | Tool false accepts repeated as accept | Tool false rejects corrected to accept | Tool false rejects repeated as reject | Escalated opportunity cases |
|---|---:|---:|---:|---:|---:|
| Qwen E6 | 0/9 | 9/9 | 0/2 | 2/2 | 0 |
| DeepSeek E6 | 0/9 | 9/9 | 0/2 | 2/2 | 0 |

The repeated false accepts are:

- `evp8_hard_candidate_0001`
- `evp8_hard_candidate_0002`
- `evp8_hard_candidate_0003`
- `evp8_hard_candidate_0008`
- `evp8_hard_candidate_0009`
- `evp8_hard_candidate_0010`
- `evp8_hard_candidate_0011`
- `evp8_hard_candidate_0012`
- `evp8_hard_candidate_0022`

The repeated false rejects are:

- `evp8_hard_candidate_0017`
- `evp8_hard_candidate_0031`

## Cost And Parse Stability

| Model | Parsed reviews | Invalid parses | Estimated cost |
|---|---:|---:|---:|
| Qwen | 47 | 0 | CNY 2.42502 |
| DeepSeek | 47 | 0 | USD 0.035463607 |

Both runs were execution-stable. The negative result is therefore not caused by
schema failure, missing coverage, or invalid model outputs.

## Interpretation

This is a stronger negative result than the Qwen-only run. On the current
`EVP-8-HARD` E6 construction, two different models exactly reproduced the
deterministic visible tool boundary and failed to correct any of the 11 known
tool opportunity cases.

The safe conclusion is:

> Under the current hard-case E6 evidence construction, Qwen and DeepSeek do
> not add independent verification value beyond the visible tool-only baseline.

This should not be used to claim that LLM-based patch verification improves
hard-case merge decisions. It supports a narrower and more useful claim:
structured tool summaries can dominate LLM verifier behavior, and LLMs may
repeat tool false accepts and false rejects unless the experimental design
explicitly separates evidence from verdict and creates failure modes that
require independent semantic judgment.

## Paper Boundary

This result is paper-useful as a negative finding:

- It validates that the hard-case cohort has measurable tool headroom.
- It shows that two LLMs did not use that headroom under current E6 conditions.
- It argues against writing the system as an automatic merge gate.
- It motivates the next experiment: remove or weaken verdict-like tool-summary
  fields and test whether models can handle the same opportunity cases using
  only lower-level evidence.

The result is not enough for a positive system claim. A stronger paper route
requires an ablation that separates raw evidence from tool verdicts, plus
qualitative analysis of why the nine visible-test-passing wrong patches were
accepted.
