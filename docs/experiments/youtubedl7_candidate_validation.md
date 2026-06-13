# youtube-dl_7 Candidate Validation

Date: 2026-06-13

## Scope

This record documents formal admission of `bugsinpy_youtube-dl_7` into the
EVP-7 main cohort after the project-level P2P-broad manifest already existed:

```text
data/p2p_scopes/bugsinpy_youtube-dl_7_p2p_broad.json
```

The P2P scope contains 108 retained pass-to-pass unittest nodeids under the
`youtube_dl_dynamic_download_nodeid_exclusion_v1` policy.

## Retained Oracle

Tracked oracle:

```text
scripts/oracles/youtubedl_7_js_to_json.py
```

The oracle checks `youtube_dl.utils.js_to_json` on the escaped-apostrophe
real-world string fixed by the official patch. It fails on the buggy checkout
and passes on the fixed checkout.

## Candidate Slice

Builder:

```text
scripts/build_youtubedl7_candidates.py
```

Generated ignored candidate file:

```text
outputs/youtubedl7_candidate_validation_001/candidates.jsonl
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
  "p2p_broad_test_count": 108,
  "label_with_p2p_broad_counts": {
    "correct_under_f2p_and_p2p_broad": 1,
    "incorrect_issue_not_fixed": 3
  }
}
```

## Execution-Chain Fix

The first P2P candidate validation attempt mislabeled the reference patch as a
regression because the candidate validator always invoked pytest. This was an
execution-chain bug: the `youtube-dl_7` P2P manifest records `test_framework`
as `unittest`, so dotted nodeids must be executed with:

```text
python -m unittest -q <nodeids...>
```

`scripts/validate_candidates_with_p2p.py` now dispatches by manifest
`test_framework`. The EVP-7 visible-test runner uses the same framework-aware
dispatch.

## Admission Outcome

`bugsinpy_youtube-dl_7` is now included in `p2p_broad_main`.

Current EVP-7 tracked artifact counts after rebuild:

- main tasks: 8;
- projects: 5;
- promoted candidates: 46;
- correct reference candidates: 8;
- issue-not-fixed candidates: 38;
- E0/E2/E4/E6 evidence packets: 184;
- G5 prompt manifest records: 184.

The later fresh DeepSeek G5 full run now covers the admitted
8-task/184-packet cohort. The older 168-packet run remains historical
pre-admission evidence only.
