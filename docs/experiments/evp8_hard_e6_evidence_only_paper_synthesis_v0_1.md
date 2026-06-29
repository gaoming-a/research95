# EVP-8-HARD E6 Evidence-Only Paper Synthesis v0.1

## Question

This ablation asks:

> If verdict-like deterministic tool summary fields are removed, do LLM
> verifiers still repeat the tool-only baseline's dangerous false accepts, or
> do they use lower-level visible evidence to become more cautious?

The study is not a test of whether the system is a reliable automated patch
verifier. The evidence boundary still lacks hidden oracle information, and the
primary cohort is deliberately hard.

## Experimental Contrast

The original EVP-8-HARD E6-full condition exposed a deterministic visible merge
decision to the model. In that condition, Qwen, DeepSeek, and the tool-only
baseline had identical decisions:

| System | Accept | Reject | Escalate | False accepts |
|---|---:|---:|---:|---:|
| tool-only baseline | 17 | 30 | 0 | 9 |
| Qwen E6-full | 17 | 30 | 0 | 9 |
| DeepSeek E6-full | 17 | 30 | 0 | 9 |

The evidence-only condition removes:

- `rule_based_visible_merge_gate_decision`
- `rule_based_visible_merge_gate_reasons`
- `source_decision`

It keeps lower-level visible evidence: patch surface, application/static
status, visible fail-to-pass tests, visible pass-to-pass evidence slots, and
tool diagnostics without a final verdict.

## Main Finding

Removing verdict-like fields changes model behavior, but the change is mainly
escalation rather than semantic rejection.

| System | Accept | Reject | Escalate | False accepts | Correct recall |
|---|---:|---:|---:|---:|---:|
| tool-only baseline | 17 | 30 | 0 | 9 | 80.00% |
| Qwen evidence-only | 15 | 30 | 2 | 7 | 80.00% |
| DeepSeek evidence-only | 6 | 30 | 11 | 4 | 20.00% |

On the nine known repeated false accepts:

| Model | Still accept | Escalate | Reject |
|---|---:|---:|---:|
| Qwen evidence-only | 7 | 2 | 0 |
| DeepSeek evidence-only | 4 | 5 | 0 |

The strict correction count is zero for both models: neither model rejected a
known false accept. The useful behavior is risk triage: some unsafe accepts are
moved to human review.

## Statistical Boundary

Whole-cohort Wilson 95% intervals for false accept rate overlap:

| System | False accept rate Wilson 95% CI |
|---|---:|
| tool-only baseline | 0.243 [0.134, 0.401] |
| Qwen evidence-only | 0.189 [0.095, 0.342] |
| DeepSeek evidence-only | 0.108 [0.043, 0.247] |

On the nine-case opportunity set, safe-handling intervals are wide:

| Model | Safe handling Wilson 95% CI |
|---|---:|
| Qwen evidence-only | 0.222 [0.063, 0.547] |
| DeepSeek evidence-only | 0.556 [0.267, 0.811] |

DeepSeek-minus-Qwen safe-handling paired bootstrap delta is 0.333
[0.000, 0.667]. This supports a descriptive tendency, not a stable superiority
claim.

## Supported Claims

1. Verdict-like tool summaries can dominate LLM verifier decisions.
   The E6-full condition produced exact agreement between both LLMs and the
   tool-only baseline, including all known false accepts.

2. Removing the visible verdict summary changes LLM behavior.
   Qwen and DeepSeek no longer exactly match the tool-only baseline under the
   same hard-case cohort.

3. The behavior shift is mostly risk escalation.
   The models move some dangerous accepts to `escalate`, but do not strictly
   reject the known false accepts.

4. Evidence-only LLM verification is better framed as triage.
   It can expose uncertainty and route some cases to human review, but it does
   not provide autonomous correctness verification.

## Unsupported Claims

Do not claim:

- The system is a reliable automated patch verifier.
- The system is safe as an autonomous merge gate.
- Evidence-only LLM verification eliminates false accepts.
- DeepSeek is generally superior to Qwen.
- Lower false accept rate is a free safety gain.

The DeepSeek result is more conservative, but it also escalates six correct
patches and drops correct recall to 20.00%.

## Paper Framing

A defensible paper framing is:

> We study how visible evidence construction shapes LLM patch-verifier
> decisions. On a hard-case cohort, exposing a deterministic merge verdict makes
> two LLMs repeat the tool-only baseline, including dangerous false accepts.
> Removing that verdict field induces model-dependent escalation of some known
> false accepts, but does not yield strict rejection or safe autonomous
> acceptance. This supports using LLMs as evidence-aware triage components, not
> as automatic merge gates.

## Threats And Limits

- The cohort has only 47 candidates and the primary opportunity set has nine
  known false accepts.
- The hard cases are concentrated in `httpie`, limiting external validity.
- The visible evidence still contains passing fail-to-pass tests, but hidden
  oracle failures are unavailable to the model.
- Escalation can reduce merge risk while increasing human-review workload.
- Model behavior differs substantially: Qwen preserves recall; DeepSeek is much
  more conservative.

## Next Paper-Strengthening Step

The next high-value experiment is not another same-prompt model run. It is a
controlled, realistic agent-patch cohort or a larger hard-case expansion that
tests whether this triage pattern holds beyond the nine `httpie`-heavy
opportunity cases.

Minimum next-cohort target:

- 50 to 100 additional realistic agent-generated patches;
- explicit visible evidence and hidden evaluator separation;
- tool-only baseline and evidence-only LLM comparison;
- per-project and per-patch-source breakdown;
- same Wilson/bootstrap reporting.

Until that exists, this result should be written as a controlled hard-case
ablation with a clear negative/conditional conclusion.
