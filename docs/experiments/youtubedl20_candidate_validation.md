# youtube-dl_20 Candidate Validation

Date: 2026-06-14

`bugsinpy_youtube-dl_20` was admitted through the controlled EVP-7
project-level P2P-broad gate.

## Scope

- Task: `bugsinpy_youtube-dl_20`
- Project: `youtube-dl`
- Framework: `unittest`
- F2P oracle:
  `test.test_utils.TestUtil.test_get_element_by_attribute`
- P2P manifest:
  `data/p2p_scopes/bugsinpy_youtube-dl_20_p2p_broad.json`
- Candidate records:
  `outputs/youtubedl20_candidate_validation_001/candidates.jsonl`
- Oracle validation:
  `outputs/youtubedl20_candidate_validation_001/oracle_validation_summary.json`
- P2P validation:
  `outputs/youtubedl20_candidate_validation_001/p2p_validation_summary.json`

Raw workdirs and validation logs remain under ignored `outputs/`.

## P2P-Broad Summary

- Scope type: `project_level_p2p_broad`
- Test framework: `unittest`
- Collected/common nodeids: 2181
- Excluded generated download nodeids: 1948
- Excluded static external-dependency tests: 84
- Excluded retained F2P oracle: 1
- Excluded buggy-baseline failures: 6
- Retained P2P-broad tests: 142
- Collection error files: 0
- Scope policy: `youtube_dl_dynamic_download_nodeid_exclusion_v1`

The retained P2P-broad set excludes `test.test_download.TestDownload*` and does
not include the F2P oracle.

## Candidate Summary

Four candidate patches were generated:

- `bugsinpy_youtube-dl_20__reference_fix`: correct reference patch.
- `bugsinpy_youtube-dl_20__empty_diff_control`: no-op negative.
- `bugsinpy_youtube-dl_20__prefix_only`: partial negative that accepts
  valueless attributes only before the target attribute.
- `bugsinpy_youtube-dl_20__suffix_only`: partial negative that accepts
  valueless attributes only after the target attribute.

Retained-oracle validation:

- candidates = 4
- patch applied = 4/4
- oracle ran = 4/4
- oracle passed = 1/4

P2P validation:

- candidates = 4
- retained oracle passed = 1
- P2P-broad test count = 142
- labels:
  - `correct_under_f2p_and_p2p_broad`: 1
  - `incorrect_issue_not_fixed`: 3

## Admission Boundary

`bugsinpy_youtube-dl_20` is included in `p2p_broad_main`. This admission uses
project-level P2P-broad validation and does not rely on task-file P2P,
dependency installation, fixture shims, or model API calls.

The checkout was constructed from an existing local youtube-dl Git clone after
recent GitHub clone instability. Both ydl20 commits were verified present
locally, and the workspace followed the BugsInPy reset/copy-test-file flow.
