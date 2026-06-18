# Paper Outline: Evidence Visibility for Candidate Patch Verification

## Working Title

Evidence Visibility Matters: A Systematic Study of LLM-Based Verification for
Candidate Patches

## One-Sentence Contribution

We study candidate patch verification as an accept/reject/escalate merge-gate
decision problem and show, within a bounded real-bug pilot, how increasing
visible evidence changes LLM verifier behavior, safety, recall, escalation, and
utility.

## Motivation

Candidate patches can look plausible even when they are partial, irrelevant, or
regression-prone. A merge gate therefore needs more than a fluent reviewer
opinion: it needs a decision tied to visible, non-leaking engineering evidence.
The current project treats AI-generated patches as one possible candidate
source, not as the required unit of every task.

## Reader Path

The paper should explain the experiment before historical runs:

1. candidate patch;
2. model-visible evidence packet;
3. accept/reject/escalate decision;
4. hidden evaluator label join after review;
5. aggregate metric and claim-boundary computation.

The first-pilot API and tool-augmented sections are diagnostic design evidence.
The frozen EVP-7 run is the paper-facing evidence-visibility result.

## Research Questions

RQ1. How risky is evidence-poor LLM review as a merge gate for candidate
patches?

RQ2. Does prompt-only evidence discipline reduce observed false accepts, and
what correct-recall cost does it introduce?

RQ3. Across E0/E2/E4/E6, how does visible evidence change false accepts,
accepted precision, correct recall, escalation, and utility?

RQ4. What do deterministic and tool-assisted evidence baselines allow us to
claim about LLM contribution?

RQ5. Which paper claims remain supported or unsupported under the frozen
20-task EVP-7 pilot boundary?

## Expected Contributions

1. A candidate patch verification framing with accept/reject/escalate decisions
   under controlled evidence visibility.
2. A related-work positioning that separates evidence visibility from
   benchmark pass rates, test-only validation, prompt engineering, and generic
   tool-use prompting.
3. A compact reader-flow bridge from candidate patch to metric computation,
   anchored by the decision-to-metric figure.
4. A real-bug-derived candidate-patch pilot with hidden evaluator separation
   and project-level P2P-broad validation for the current main cohort.
5. A negative or mixed prompt-only evidence-first result from the first real
   API pilot.
6. A conditional tool-assisted verification result from the separate
   tool-augmented run.
7. A bounded EVP-7 evidence-visibility pilot over 20 tasks, 94 candidates, and
   376 evidence packets.
8. Paper-facing artifacts for the frozen EVP-7 result: Evidence Visibility
   Curve, statistical intervals, utility sensitivity, and claim-boundary
   traceability.

## Current Supported Claims

- The first prompt-only evidence-first full run is not a positive result under
  its configured gate.
- The separate tool-augmented full run supports only a conditional
  tool-assisted verifier claim.
- The EVP-7 G5 run supports bounded pilot observations that verifier decisions
  and metrics vary by evidence level on the frozen 20-task cohort.
- In the current EVP-7 run, E4 and E6 preserve zero observed false accepts and
  accepted precision 1.0, while E6 has higher correct recall and utility than
  E0 within the bounded pilot.

## Non-Claims

- Do not claim scale generality from the frozen 20-task EVP-7 pilot.
- Do not claim that the LLM strictly outperforms deterministic visible-test or
  tool-only baselines.
- Do not claim that E6 is strictly superior to E4 as a generalized finding.
- Do not present tool-augmented results as proof of prompt-only model ability.
- Do not treat runner-estimated cost as an external billing statement.
- Do not title the current paper around AI-generated patches until generated
  patches become a dominant, validated candidate source.
