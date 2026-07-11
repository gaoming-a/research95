# DSA P3 Prompt Change Record v0.1

Date: 2026-07-11
Status: frozen after author sign-off by 高明 at 2026-07-11T15:00:02+08:00
API calls: none

## Change

- New prompt: `prompts/dsa2026_evidence_conditioned_patch_gate_v0_1.md`.
- New schema: `data/protocols/dsa_p3_output_schema_v0_1.json`.
- The prompt was written from an empty new file for the DSA study. No deleted
  prompt was opened from Git history, restored, copied, paraphrased, or used to
  select wording.
- It does not replace a live prompt. The four retired templates remain absent;
  their deletion hashes are provenance only.

## Intended semantics

The same prompt and schema apply without condition-specific text to C0, C1,
C2, and C3. The three decisions mean automatic merge, do not merge, and no
automatic decision from the supplied information. The model must ground its
response only in the serialized packet and return the five preregistered JSON
fields.

## Conflict and duplication review

- The prompt does not state that sparse evidence implies escalation.
- It does not state that a failed check implies rejection.
- It does not name or explain C0--C3, evidence levels, candidate roles, hidden
  oracles, source decisions, rule decisions, or expected behavior.
- It contains no decision example, worked example, reference answer, tool
  verdict, coverage challenge, or model-specific instruction.
- It does not add fields beyond `decision`, `confidence`,
  `concise_rationale`, `evidence_used`, and `uncertainty`.
- It asks the model not to invent unreported outcomes but does not prescribe a
  decision for missing information.
- No active prompt duplicates the new role: the active directory contains this
  one DSA template plus the audit ledger.
- Byte-hash comparison against the four recorded pre-deletion hashes must be
  unequal. This is a provenance check, not recovery of deleted content.
- Author 高明 signed the new prompt/schema as one of the 11 P3 frozen items;
  any later model-visible or schema-semantic change terminates this study
  version rather than amending this prompt in place.
- Frozen P3 text hashes use UTF-8 with CRLF/CR normalized to LF, so a Windows
  checkout cannot change prompt or manifest identity solely through line-ending
  conversion. P2 raw freeze hashes remain separately checked byte-for-byte.

## Mechanical checks required before sign-off

The P3 auditor must verify one and only one packet placeholder, no unresolved
placeholder after rendering, exact output-schema fields, absence of prohibited
instructions, no duplicated normalized instruction line, recursive packet-key/value leakage count zero, cumulative
synthetic C0--C3 canonical diff, and new-hash inequality with every retired
prompt hash. A passing mechanical audit does not replace author sign-off.
