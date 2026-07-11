# Prompt Change Log

This log records prompt changes for the patch-verification study. It is scoped
to experiment prompts, not agent system prompts.

## 2026-06-20 EVP-8 Visible Evidence Merge-Gate v0.1

- Prompt id: `evp8_visible_evidence_merge_gate_v0_1`
- Prompt file: `prompts/evp8_visible_evidence_merge_gate_v0_1.md`
- Protocol spec: `data/protocols/evp8_protocol_v0_1.json`
- Change type: new EVP-8 prompt template.
- Replaces: nothing. EVP-7 prompt `patch_verify_evidence_visibility_merge_gate_v1`
  remains the historical four-anchor pilot prompt.

Conflict and duplication check:

- The EVP-7 prompt is a merge-gate verifier prompt for `E0/E2/E4/E6`.
- The EVP-8 prompt keeps the same visible-only merge-gate boundary but targets
  the new adjacent-difference `E0-E6` protocol.
- The EVP-8 output schema removes evaluator-taxonomy-style fields and matches
  the protocol-defined keys:
  `decision`, `confidence`, `primary_reason`, `evidence_used`,
  `visible_contradictions`, `risk_flags`, and `human_review_needed`.
- The prompt does not expose per-candidate evaluator labels, hidden oracle
  outcomes, reference provenance, or final merge labels.
- The prompt is frozen for no-API Phase 0 auditing only. It does not authorize
  model calls or evidence-packet generation.

Verification:

- Run `python scripts\build_evp8_prompt_manifest.py --check`.
- Run `python scripts\audit_evp8_protocol_spec.py --check`.

## 2026-06-26 EVP-8 Visible Evidence Merge-Gate v0.2

- Prompt id: `evp8_visible_evidence_merge_gate_v0_2`
- Prompt file: `prompts/evp8_visible_evidence_merge_gate_v0_2.md`
- Protocol spec: `data/protocols/evp8_protocol_v0_2.json`
- Change type: JSON/schema-discipline repair for the accept-aware DeepSeek/Qwen
  retest.
- Replaces: no historical result. EVP-8 v0.1 remains the frozen five-model
  packet-set prompt; v0.2 is a separate accept-aware retest prompt.

Conflict and duplication check:

- v0.2 keeps the v0.1 visible-only merge-gate boundary and the same decision
  values: `accept`, `reject`, and `escalate`.
- v0.2 does not add hidden evaluator labels, hidden tests, reference-patch
  provenance, candidate types, or final merge labels.
- v0.2 does not change the substantive decision policy. It only makes the
  output contract stricter by requiring exact JSON, exact risk-flag enum
  values, and `human_review_needed=false` for supported accept/reject decisions.
- The change is not duplicated with EVP-7 because EVP-7 used the historical
  four-anchor prompt; this prompt targets the EVP-8 E0-E6 adjacent ladder.

Verification:

- Run
  `python scripts\build_evp8_prompt_manifest.py --spec-in data\protocols\evp8_protocol_v0_2.json --template-in prompts\evp8_visible_evidence_merge_gate_v0_2.md --manifest-out data\protocols\evp8_prompt_manifest_v0_2.json --boundary-audit-out data\protocols\evp8_prompt_boundary_audit_v0_2.json --check`.
- Run
  `python scripts\audit_evp8_protocol_spec.py --spec-in data\protocols\evp8_protocol_v0_2.json --summary-out data\protocols\evp8_protocol_v0_2_audit_summary.json --check`.

## 2026-06-30 EVP-8-HARD Tool-Contestation Merge-Gate v0.1

- Prompt id: `evp8_tool_contestation_merge_gate_v0_1`
- Prompt file: `prompts/evp8_tool_contestation_merge_gate_v0_1.md`
- Runner/config:
  `scripts/run_evp8_hard_tool_contestation.py` and
  `configs/evp8_hard_tool_contestation.example.json`
- Change type: new EVP-8-HARD ablation prompt for tool-evidence reliability
  and visible-test-only accept-premise contestation.
- Replaces: nothing. EVP-8 v0.2 remains the main visible-evidence merge-gate
  prompt; this prompt is a separate hard-case ablation.

Conflict and duplication check:

- The prompt keeps the v0.2 visible-only boundary: it does not expose hidden
  evaluator labels, hidden tests, hidden oracle outcomes, reference-patch
  provenance, or final merge labels.
- The prompt intentionally does not expose final deterministic tool verdict
  fields. The runner removes `rule_based_visible_merge_gate_decision`,
  `rule_based_visible_merge_gate_reasons`, and `source_decision` before prompt
  rendering.
- The prompt adds tool-contestation output fields:
  `coverage_concern`, `visible_tests_sufficient`,
  `tool_evidence_reliability`, `would_challenge_visible_test_only_accept`, and
  `challenge_reason`.
- The prompt is not a compatibility patch for v0.2. It answers a narrower
  causal question: whether models can challenge a visible-test-only accept
  premise when verdict-like tool summaries are absent.
- The result must be interpreted as risk triage when decisions move from
  `accept` to `escalate`; it does not establish automatic patch correctness
  verification.

Verification:

- Run
  `python -m py_compile scripts\run_evp8_hard_tool_contestation.py scripts\audit_evp8_hard_tool_contestation_results.py scripts\analyze_evp8_hard_tool_contestation_opportunity.py`.
- Run
  `python scripts\run_evp8_hard_tool_contestation.py --config configs\evp8_hard_tool_contestation.local.json --check-only`.
- Run
  `python scripts\audit_evp8_hard_tool_contestation_results.py --out data\protocols\evp8_hard_tool_contestation_result_audit_v0_1.json --check`.
- Run
  `python scripts\analyze_evp8_hard_tool_contestation_opportunity.py --out-json data\reviews\evp8_hard_tool_contestation_opportunity_analysis_v0_1.json --out-md docs\experiments\evp8_hard_tool_contestation_opportunity_analysis_v0_1.md --check`.

## 2026-07-10 Legacy EVP-8 Prompt Retirement

- Change type: physical deletion from the active worktree.
- Author decision: retire every legacy EVP-8 experiment prompt and continue
  under research objective A, which studies how visible evidence changes the
  accept/reject/escalate policy rather than claiming verifier correctness.
- Replacement: none. No EVP-v0.4 prompt was created in this change.
- API boundary: no smoke, full run, or model API call is authorized.

Deleted templates and their pre-deletion SHA-256 values:

| Deleted path | SHA-256 |
|---|---|
| `prompts/evp8_visible_evidence_merge_gate_v0_1.md` | `a31d23d74f5130c9ce06262c4a9f016a303da8e77683c007e7cfb142fb74066c` |
| `prompts/evp8_visible_evidence_merge_gate_v0_2.md` | `3e64dbedf9b0155f3013f30a4044631dc18d4f8d22920620941e16bd0e7d09f0` |
| `prompts/evp8_tool_contestation_merge_gate_v0_1.md` | `dbb09a88a3c4370d82cc257f9d44561924fcf7ba9f8cd21934adeabf2eb51bbc` |
| `prompts/evp8_coverage_contestation_merge_gate_v0_1.md` | `722608bd0b88ec8af3c31ce06fc756e39aa4c070f57292c9eea256a66e4c422a` |

Conflict and duplication check:

- The previous master plan said not to modify legacy prompts. The user's later
  explicit deletion decision superseded that retention rule, and the master
  plan was amended before deletion.
- The deleted templates encode policy and condition framing that the
  2026-07-10 root-cause audit found unsuitable for confirmatory reuse.
- The four original byte sequences remain recoverable from existing Git
  history; no second active or archived worktree copy was created.
- Historical protocols, manifests, run packets, results, and audits retain
  their original prompt paths, ids, and hashes as provenance. Their old
  `passed`, `ready`, `current`, or `main` labels describe the historical run
  state only and do not make the retired chain executable.
- Legacy example/local configs and runners must not be redirected to a future
  prompt. They are historical code and are not valid execution entry points.
- A future EVP-v0.4 prompt requires a new id, path, author decision, conflict
  check, preregistration gate, and separate change record.

Verification:

- The active `prompts/` directory must contain this log and no legacy EVP-8
  template.
- The four deleted paths must be absent.
- Historical data/protocol/result artifacts must have no content diff from
  this retirement change.

## 2026-07-11 DSA P3 New Prompt Freeze

- Prompt file: `prompts/dsa2026_evidence_conditioned_patch_gate_v0_1.md`.
- Schema file: `data/protocols/dsa_p3_output_schema_v0_1.json`.
- Change type: new DSA prompt and schema, created from empty files.
- Status: frozen after explicit author sign-off by 高明 at
  `2026-07-11T15:00:02+08:00`.
- API boundary: no inference API call is authorized by this change.

Conflict, duplication, and provenance boundary:

- No deleted prompt was opened from Git history, restored, copied, or
  paraphrased. Model selection and wording were not based on legacy outcomes.
- The new prompt has one neutral role across C0--C3. It contains no condition
  name, evidence-level explanation, candidate role, hidden label/oracle,
  expected answer, decision example, tool verdict, or condition-specific cue.
- It does not prescribe escalation for sparse evidence or rejection for a
  failed check. It only forbids inventing unreported facts.
- Its only output fields are `decision`, `confidence`, `concise_rationale`,
  `evidence_used`, and `uncertainty`; invalid output cannot be rewritten as
  escalation.
- The full mechanical review is recorded in
  `docs/experiments/dsa_p3_prompt_change_record_v0_1.md` and the generated P3
  prompt-boundary audit. Author sign-off remains a separate Gate.
