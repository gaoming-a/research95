# EVP-7 Related-Work Positioning

This note records the paper-facing related-work boundary for the current
EVP-7 draft. It is a writing and citation artifact, not new experimental
evidence.

## Citation Scope Decision

The user requested Nature-style paper handling, but the specific related-work
gap is software engineering and automated program repair. A strict
Nature/CNS-family-only search is not an appropriate support basis for claims
about real-bug software benchmarks, patch plausibility, LLM-based program
repair, or agentic software engineering. Following the conservative
`nature-citation` principle, this note uses field-specific primary sources
that directly support the claims being positioned.

Reference-manager export:

- `docs/references/evp7_related_work_references.ris`

## One-Sentence Positioning Argument

This paper does not propose another patch-generation benchmark or a generic
tool-use prompt. It studies candidate-patch verification as a merge-gate
decision whose outcome must be interpreted against the evidence that was
visible before accept, reject, or escalate was chosen.

## Segment-to-Reference Map

| segment | claim | support | citation keys | support grade |
|---|---|---|---|---|
| S001 | Real-bug benchmarks make controlled repair and evaluation possible, but they usually define tasks or testable faults rather than the evidence available to a verifier at decision time. | Defects4J and BugsInPy are real-bug benchmark/data resources; SWE-bench is a real-world GitHub issue benchmark. | `just2014defects4j`, `widyasari2020bugsinpy`, `jimenez2024swebench` | strong for benchmark context; partial for evidence-visibility gap |
| S002 | Test passing and benchmark pass rates do not by themselves prove semantic correctness, because plausible patches can still be incorrect. | Qi et al. analyze plausible-but-incorrect patches in generate-and-validate repair. | `qi2015patchcorrectness` | strong for patch-plausibility warning |
| S003 | LLM-based repair and agentic software engineering expand patch generation and task-solving workflows, but benchmark success does not specify how a verifier should combine visible evidence with hidden evaluator labels. | Xia et al. study LLM-based APR; SWE-agent studies agent-computer interfaces for software engineering. | `xia2023llmapr`, `yang2024sweagent` | background to partial support |
| S004 | EVP-7 differs by varying evidence visibility before the decision and joining hidden labels only after review. | This is the current paper's own protocol and result; cite internal figures/tables rather than external work. | internal | supported by current artifacts |

## Paper-Use Boundary

- Use the references to position the problem, not to claim that those papers
  evaluated evidence visibility.
- Do not imply that Evidence Gain is a standardized community metric. In the
  current draft it is a descriptive pilot metric used to summarize merge-gate
  utility under the frozen EVP-7 protocol.
- Do not describe SWE-bench, SWE-agent, BugsInPy, or Defects4J as direct
  baselines for EVP-7. They motivate the task setting and evidence gap.

## Related-Work Structure

The IEEE draft should use three compact paragraphs:

1. Real-bug and issue-based benchmarks: scope and limitation.
2. Automated repair, test-suite adequacy, and LLM/agent repair: scope and
   limitation.
3. EVP-7 distinction: evidence visibility, hidden-label separation, and
   descriptive Evidence Gain.
