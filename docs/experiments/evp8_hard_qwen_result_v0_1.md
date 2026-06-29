# EVP-8-HARD Qwen Result v0.1

## Scope

- Cohort: `EVP-8-HARD`
- Model: `qwen/qwen3.7-max`
- Evidence level: `E6`
- Candidate count: 47
- API run: authorized by user for Qwen only
- DeepSeek status: not run in this step
- Raw response policy: raw responses are under ignored `outputs/`; this report
  uses only tracked summary and parsed review records.

## Run Gate

- Summary: `data/reviews/evp8_hard_qwen_qwen3.7-max_full_summary.json`
- Parsed reviews: `data/reviews/evp8_hard_qwen_qwen3.7-max_full_reviews.jsonl`
- Result audit: `data/protocols/evp8_hard_qwen_deepseek_result_audit_v0_1.json`
- Review count: 47/47
- Parse-valid count: 47/47
- Run gate: `passed`
- Usage/cost gate: `passed`
- Raw text in tracked summary: `false`
- Raw text in parsed reviews: `false`

## Main Results

| System | Accept | Reject | Escalate | Accepted precision | Correct recall | False accept rate | False reject rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| Tool-only baseline | 17 | 30 | 0 | 47.06% | 80.00% | 24.32% | 20.00% |
| Qwen E6 | 17 | 30 | 0 | 47.06% | 80.00% | 24.32% | 20.00% |

Qwen exactly matched the deterministic visible tool-only baseline on this
hard-case cohort.

## Error Profile

Qwen accepted 17 candidates:

- True accepts: 8
- False accepts: 9

Qwen rejected 30 candidates:

- True rejects: 28
- False rejects: 2

False accepts:

- `evp8_hard_candidate_0001`
- `evp8_hard_candidate_0002`
- `evp8_hard_candidate_0003`
- `evp8_hard_candidate_0008`
- `evp8_hard_candidate_0009`
- `evp8_hard_candidate_0010`
- `evp8_hard_candidate_0011`
- `evp8_hard_candidate_0012`
- `evp8_hard_candidate_0022`

False rejects:

- `evp8_hard_candidate_0017`
- `evp8_hard_candidate_0031`

## Tool-Opportunity Analysis

The hard-case cohort was constructed to contain tool-baseline headroom:

- Tool false accepts: 9
- Tool false rejects: 2
- Total actionable opportunity cases: 11

Qwen did not improve any of these cases:

- Tool false accepts corrected to reject: 0/9
- Tool false accepts repeated as accept: 9/9
- Tool false rejects corrected to accept: 0/2
- Tool false rejects repeated as reject: 2/2
- Escalations on opportunity cases: 0

## Interpretation

This is a negative result for Qwen on the current EVP-8-HARD E6 setup. The
model did not add independent verification value beyond the visible tool
summary. More specifically, it followed the accept/reject boundary implied by
the deterministic visible merge gate, including all known tool mistakes.

The result is still useful because it tests the exact concern that motivated
the hard-case extension: whether an LLM can recover from visible-test/tool
blind spots when plausible wrong patches pass the visible gate. For Qwen under
the current E6 evidence construction, the answer is no.

The safe claim is therefore:

> On the 47-candidate EVP-8-HARD cohort, Qwen E6 reproduced the deterministic
> tool-only baseline and did not correct any of the 11 tool false-accept or
> false-reject opportunity cases.

This should not be written as evidence that LLM verification improves hard-case
patch acceptance. It supports a more cautious claim: strong structured
tool-summary evidence can dominate the LLM decision, and Qwen did not act as an
independent safeguard against the tool baseline's known errors in this run.

## Next Step

DeepSeek has not been run for this hard-case cohort. Running DeepSeek would
test whether the Qwen result is model-specific or a broader consequence of the
E6 evidence construction.
