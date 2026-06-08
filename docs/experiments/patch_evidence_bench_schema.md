# PatchEvidenceBench Schema

This document defines the long-term schema for the evidence-visibility patch
verification study. It extends the current pilot schema and should be used
before expanding beyond the existing 30 candidates.

## Design Goals

- Keep evaluator-facing labels separate from model-visible evidence.
- Preserve enough provenance to reproduce patch generation and validation.
- Support accept/reject/escalate verifier decisions across evidence levels.
- Make tool-only, LLM-only, and LLM-with-evidence conditions comparable.

## TaskRecord

One record per real bug or issue-derived task.

Required fields:

```json
{
  "task_id": "bugsinpy_httpie_1",
  "source": "bugsinpy",
  "project": "httpie",
  "language": "python",
  "base_version": "buggy",
  "reference_version": "fixed",
  "issue_summary": "download filename collision handling should create a unique filename",
  "touched_files": ["httpie/downloads.py"],
  "visible_test_hints": ["tests/test_downloads.py::TestDownloadUtils::test_unique_filename"],
  "hidden_evaluator_ids": ["httpie_1_unique_filename", "httpie_1_errno_fallback"],
  "environment_profile": "local-retained-checkout",
  "task_status": "validated"
}
```

`hidden_evaluator_ids` are evaluator-facing. Verifier prompts may refer to
visible test hints, but must not expose hidden evaluator identifiers, hidden
results, or final labels.

## PatchRecord

One record per candidate patch.

Required fields:

```json
{
  "patch_id": "bugsinpy_httpie_1__missing_change_1",
  "model_candidate_id": "candidate_0005",
  "task_id": "bugsinpy_httpie_1",
  "source_type": "constructed",
  "generator_model": null,
  "generation_protocol": "reference_diff_with_one_change_omitted",
  "patch_diff": "diff --git ...",
  "patch_size": {
    "files_changed": 1,
    "added_lines": 35,
    "deleted_lines": 3
  },
  "modified_files": ["httpie/downloads.py"],
  "candidate_type": "partial_fix",
  "expected_outcome": "partial",
  "failure_type_label": "partial_fix",
  "label_confidence": "high"
}
```

Evaluator-only fields:

- `patch_id`;
- `candidate_type`;
- `expected_outcome`;
- `failure_type_label`;
- `generation_protocol` when it reveals construction type;
- reference-patch relationship.

Model-visible identifier:

- `model_candidate_id`.

## EvidencePacket

One record per candidate and evidence level. These are the only records passed
to verifier models.

Required fields:

```json
{
  "evidence_packet_id": "candidate_0005__E4",
  "model_candidate_id": "candidate_0005",
  "task_id": "bugsinpy_httpie_1",
  "evidence_level": "E4_visible_tests",
  "visible_issue_summary": "download filename collision handling should create a unique filename",
  "visible_patch_diff": "diff --git ...",
  "visible_static_results": {
    "patch_applies": true,
    "syntax_import_check": "not_run"
  },
  "visible_runtime_trace": null,
  "visible_test_results": [
    {
      "test_name": "tests/test_downloads.py::TestDownloadUtils::test_unique_filename",
      "status": "passed"
    }
  ],
  "generated_test_results": [],
  "label_leakage_guard": "no evaluator labels, hidden tests, reference patch, or oracle outcome included"
}
```

Evidence levels:

| Level | Meaning |
| --- | --- |
| E0 | issue summary + patch diff |
| E1 | E0 + modified files / changed functions |
| E2 | E1 + patch apply / static checks |
| E3 | E2 + runtime trace |
| E4 | E3 + visible fail-to-pass and pass-to-pass test results |
| E5 | E4 + generated targeted test results |
| E6 | E5 + realistic full tool evidence summary |
| E7 | oracle upper bound, reported separately |

## ValidationOutcome

One record per candidate, computed by evaluator-side validation.

Required fields:

```json
{
  "patch_id": "bugsinpy_httpie_1__missing_change_1",
  "model_candidate_id": "candidate_0005",
  "task_id": "bugsinpy_httpie_1",
  "patch_applied": true,
  "syntax_import_passed": true,
  "visible_tests_passed": true,
  "hidden_tests_passed": false,
  "regression_tests_passed": false,
  "generated_tests_passed": null,
  "ground_truth_label": "partial",
  "failure_type_label": "partial_fix",
  "validation_status": "validated"
}
```

`ValidationOutcome` is evaluator-facing by default. Only explicitly selected
visible subsets may be copied into an `EvidencePacket`.

## VerifierDecision

One record per verifier, candidate, and evidence condition.

Required fields:

```json
{
  "decision_id": "candidate_0005__deepseek-v4-pro__E4",
  "model_candidate_id": "candidate_0005",
  "patch_id": "bugsinpy_httpie_1__missing_change_1",
  "verifier_id": "deepseek-v4-pro",
  "condition": "E4_visible_tests",
  "decision": "reject",
  "confidence": 0.82,
  "rationale": "The visible behavior evidence does not establish the fallback path.",
  "cited_evidence": ["visible_test_results[0]", "patch_diff"],
  "claims": [],
  "raw_response_path": "outputs/.../candidate_0005.json",
  "cost_usd": 0.0,
  "invalid_reason": null
}
```

Allowed decisions:

- `accept`;
- `reject`;
- `escalate`;
- `invalid_output`.

## Required Joins

- `TaskRecord.task_id` -> `PatchRecord.task_id`.
- `PatchRecord.model_candidate_id` -> `EvidencePacket.model_candidate_id`.
- `PatchRecord.patch_id` -> `ValidationOutcome.patch_id`.
- `PatchRecord.patch_id` -> `VerifierDecision.patch_id`.

## Expansion Gate

A task is not eligible for the expanded experiment until all of these hold:

1. `TaskRecord.task_status = validated`.
2. At least one `correct_reference`, one no-op/irrelevant negative, and one
   difficult negative candidate exist.
3. All candidates have `ValidationOutcome.validation_status = validated`.
4. Evidence packets pass leakage checks.
5. Tool-only baselines can run without reading final labels.
