# EVP-7 Next Decision Packet

Date: 2026-06-18

Updated: 2026-06-20 for the user-confirmed journal-upgrade planning route.

This is a no-API decision packet. It does not start a new experiment, call a
model, expand the cohort, or change the evidence levels.

## Current Verified State

- Current paper claim: bounded EVP-7 evidence-visibility pilot.
- Structural/no-API cohort: 21 tasks, 6 projects, 98 candidates, 392
  E0/E2/E4/E6 evidence packets.
- Paper-facing real DeepSeek G5 run: 20 tasks, 94 candidates, 376 records.
- Current paper route: four-anchor E0/E2/E4/E6 pilot, not a full E0-E6
  adjacent-difference ladder.
- Current paper and artifact readiness:
  - paper tables regenerate from tracked summaries;
  - IEEE draft regenerates from tracked tables;
  - IEEE PDF compiles twice;
  - claim-boundary audit is raw-output-free and passes;
  - anonymous artifact audit is safe;
  - local quality gate passes.
- `bugsinpy_cookiecutter_4` is a tracked P2P blocker, not an admitted task.

## Decision Required Before Further Experiments

The next experimental action must be one of the following. Do not infer it from
a generic "continue" instruction.

### Option A: Submit Current Four-Anchor Paper Package

Use when the priority is finishing the paper submission with the current claim
boundary.

Allowed work:

- language polishing;
- formatting;
- reference cleanup;
- final PDF/artifact rebuild;
- response-to-advisor summary.

Forbidden work:

- no new API calls;
- no cohort expansion;
- no E1/E3/E5 insertion;
- no claim that the LLM beats deterministic tool-only baselines.

Confirmation needed:

- target venue or format constraints, if any;
- whether to freeze the current 7-page IEEE PDF as the submission draft.

### Option B: Second-Model Key-Anchor Replication

Use only if the priority is robustness evidence beyond DeepSeek G5.

Default scope:

- same paper-facing 20-task / 94-candidate cohort;
- only E0, E4, and E6 key anchors;
- no E1/E3/E5;
- no bug expansion.

Required user confirmations:

- provider;
- model id;
- maximum total cost;
- smoke packet count;
- whether full-run permission is granted after smoke passes;
- stopping rule for inconsistent or low-quality outputs.

Required no-API steps before any model call:

- create ignored local config;
- strict preflight;
- guarded workflow check-only;
- prompt-boundary and leakage checks;
- cost-observability readiness.

Expected outputs if executed:

- raw-output-free second-model summary;
- quality audit;
- statistics;
- utility sensitivity;
- claim-boundary update;
- paper wording that reports agreement or disagreement as robustness boundary.

### Option C: New 30-50 Bug Expansion Boundary

Use only if the priority is increasing dataset scale beyond the current
21-task structural cohort.

Required user confirmations:

- whether native/editable builds are allowed;
- whether external benchmarks outside BugsInPy are allowed;
- whether project-level P2P remains mandatory;
- target task and candidate scale;
- maximum time budget for blocker probes;
- whether blocked tasks count as feasibility evidence or must be replaced.

Forbidden by default:

- no task-file P2P downgrade for main metrics;
- no source or test fixture edits for admission;
- no blind BugsInPy sweeping;
- no candidate construction before F2P plus admissible P2P.

### Option D: New Verifier Design

Use only if the priority is repairing the old prompt-only evidence-first line.

Required user confirmations:

- whether the old prompt-only result remains a negative/redesign finding;
- whether the new design is prompt-only or tool-assisted;
- target dry-run scope;
- evaluation gates;
- whether any real API calls are allowed after dry-run passes.

Forbidden by default:

- do not expand `patch_verify_evidence_first_v1`;
- do not use `tool_augmented_evidence` to rescue prompt-only conclusions;
- do not call APIs before dry-run and prompt-boundary checks pass.

### Option E: EVP-8 Journal-Scale Full-Ladder Protocol

Use only if the priority is upgrading the current bounded pilot into a journal
version.

Canonical plan:

- `docs/experiments/evp8_journal_scale_execution_plan_20260620.md`

Default scope:

- new EVP-8 protocol, not a modification of current EVP-7 artifacts;
- seven model-visible levels `E0-E6`, plus evaluator-only `E7` oracle upper
  bound;
- target scale of 30-50 validation-stable bugs and 100-180 candidates;
- five-model target set:
  - `deepseek/deepseek-v4-pro`;
  - `qwen/qwen3.7-max`;
  - `moonshotai/kimi-k2.6`;
  - `mistralai/devstral-2512`;
  - `google/gemini-2.5-flash`.

Execution order:

1. No-API protocol freeze: evidence-level definitions, packet schema, prompt
   schema, candidate-set policy, evaluator joins, metrics, stop gates, and
   provider/model routing policy.
2. DeepSeek + Qwen first batch only after dry-run, leakage, prompt-boundary,
   cost-observability, and smoke gates pass.
3. Later add Kimi, Devstral, and Gemini using the same frozen packets and
   prompts.

Required user confirmations before any API call:

- whether the first EVP-8 execution should use the current 20-task /
  94-candidate cohort for protocol validation or first expand toward 30-50
  bugs;
- DeepSeek provider/config;
- Qwen provider/config;
- maximum total cost for the first batch;
- smoke packet count;
- full-run permission after smoke passes;
- stop rule for inconsistent, low-quality, or schema-invalid outputs.

Forbidden by default:

- no model API calls during protocol design;
- no automatic use of Kimi/Devstral/Gemini until an OpenRouter or official-key
  route is confirmed;
- no modification of evidence levels, prompt schema, candidate set, or evaluator
  joins after the first model call without bumping the protocol version and
  rerunning affected models;
- no final five-model journal claim from the DeepSeek + Qwen interim batch.

## Default If No Decision Is Given

If no explicit decision is given, continue only with no-API paper-submission
maintenance:

- regenerate tables/draft/PDF;
- rerun readiness and artifact audits;
- update handoff notes;
- do not start new experiments.

## Current Recommended Path

As of 2026-06-20, the user has expressed intent to upgrade to a journal version.
The next non-conflicting experimental path is therefore Option E, starting with
no-API EVP-8 protocol design and freeze. This still does not authorize model
API calls: DeepSeek and Qwen can run only after the EVP-8 no-API gates and
explicit execution permission pass.
