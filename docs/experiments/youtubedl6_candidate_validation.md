# youtube-dl_6 Candidate Validation

Date: 2026-06-13

## Scope

This record documents formal admission of `bugsinpy_youtube-dl_6` into the
EVP-7 main cohort.

The project-level P2P-broad manifest is:

```text
data/p2p_scopes/bugsinpy_youtube-dl_6_p2p_broad.json
```

The scope contains 110 retained pass-to-pass unittest nodeids under the
`youtube_dl_dynamic_download_nodeid_exclusion_v1` policy.

## P2P Construction

The first real P2P construction attempt timed out while executing dynamically
generated `test.test_download.TestDownload.*` cases. The rerun used the same
audited policy already used for `bugsinpy_youtube-dl_7`:

- excluded nodeid prefix: `test.test_download.TestDownload`;
- retained fail-to-pass oracle:
  `test.test_utils.TestUtil.test_parse_dfxp_time_expr`;
- no dependency installation, compat shim, or task-file downgrade.

Completed P2P scope counts:

```json
{
  "common_collected_tests": 1525,
  "excluded_nodeid_prefix": 1345,
  "excluded_static_external_dependency": 67,
  "excluded_fail_to_pass_oracle": 1,
  "included_p2p_tests": 110
}
```

## Retained Oracle

Tracked oracle:

```text
scripts/oracles/youtubedl_6_dfxp_time.py
```

The oracle checks that missing or empty DFXP time expressions remain invalid
and that invalid DFXP subtitle paragraphs are ignored. It fails on the buggy
checkout and passes on the fixed checkout.

## Candidate Slice

Builder:

```text
scripts/build_youtubedl6_candidates.py
```

Generated ignored candidate file:

```text
outputs/youtubedl6_candidate_validation_001/candidates.jsonl
```

The admission slice contains four candidates:

| candidate type | expected validation behavior |
| --- | --- |
| `correct_reference` | retained oracle passes and P2P-broad passes |
| `buggy_noop` | retained oracle fails |
| `partial_fix` | retained oracle fails |
| `irrelevant_patch` | retained oracle fails |

## Validation Results

Retained-oracle validation:

```json
{
  "record_count": 4,
  "patch_applied_count": 4,
  "oracle_ran_count": 4,
  "oracle_all_passed_count": 1,
  "validation_status_counts": {
    "validated": 4
  },
  "all_validated": true
}
```

P2P-broad validation:

```json
{
  "record_count": 4,
  "patch_applied_count": 4,
  "retained_oracle_passed_count": 1,
  "p2p_broad_test_count": 110,
  "label_with_p2p_broad_counts": {
    "correct_under_f2p_and_p2p_broad": 1,
    "incorrect_issue_not_fixed": 3
  }
}
```

## Admission Outcome

`bugsinpy_youtube-dl_6` is now included in `p2p_broad_main`.

Current EVP-7 tracked no-API artifact counts after rebuild:

- main tasks: 9;
- projects: 5;
- promoted candidates: 50;
- correct reference candidates: 9;
- issue-not-fixed candidates: 41;
- E0/E2/E4/E6 evidence packets: 200;
- G5 prompt manifest records: 200.

The previous real DeepSeek V4 G5 full run remains scoped to the earlier
8-task/46-candidate/184-packet cohort. The new 9-task/200-packet cohort has
passed structural no-API gates but has not been rerun with a real LLM verifier.
