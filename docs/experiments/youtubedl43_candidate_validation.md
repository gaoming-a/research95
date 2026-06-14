# youtube-dl_43 Candidate Validation

Date: 2026-06-14

`bugsinpy_youtube-dl_43` was admitted through the controlled EVP-7
project-level P2P-broad gate.

## Scope

- Task: `bugsinpy_youtube-dl_43`
- Project: `youtube-dl`
- Framework: `unittest`
- F2P oracle:
  `test.test_utils.TestUtil.test_url_basename`
- P2P manifest:
  `data/p2p_scopes/bugsinpy_youtube-dl_43_p2p_broad.json`
- Candidate records:
  `outputs/youtubedl43_candidate_validation_001/candidates.jsonl`
- Oracle validation:
  `outputs/youtubedl43_candidate_validation_001/oracle_validation_summary.json`
- P2P validation:
  `outputs/youtubedl43_candidate_validation_001/p2p_validation_summary.json`

Raw workdirs and validation logs remain under ignored `outputs/`.

## P2P-Broad Summary

- Scope type: `project_level_p2p_broad`
- Test framework: `unittest`
- Collected/common nodeids: 324
- Excluded generated download nodeids: 224
- Excluded static external-dependency tests: 49
- Excluded retained F2P oracle: 1
- Excluded buggy-baseline failures: 32
- Retained P2P-broad tests: 18
- Collection error files: 0
- Scope policy: `youtube_dl_dynamic_download_nodeid_exclusion_v1`

The retained P2P-broad set excludes `test.test_download.TestDownload*` and does
not include the F2P oracle.

## Candidate Summary

Four candidate patches were generated:

- `bugsinpy_youtube-dl_43__reference_fix`: correct reference patch.
- `bugsinpy_youtube-dl_43__empty_diff_control`: no-op negative.
- `bugsinpy_youtube-dl_43__two_directory_only`: partial negative that supports
  one extra directory level but still fails deeper paths.
- `bugsinpy_youtube-dl_43__noop_assignment`: irrelevant negative that changes no
  `url_basename` behavior.

Retained-oracle validation:

- candidates = 4
- patch applied = 4/4
- oracle ran = 4/4
- oracle passed = 1/4

P2P validation:

- candidates = 4
- retained oracle passed = 1
- P2P-broad test count = 18
- labels:
  - `correct_under_f2p_and_p2p_broad`: 1
  - `incorrect_issue_not_fixed`: 3

## Admission Boundary

`bugsinpy_youtube-dl_43` is included in `p2p_broad_main`. This admission uses
project-level P2P-broad validation and does not rely on task-file P2P,
dependency installation, fixture shims, or model API calls.

The checkout was constructed from an existing local youtube-dl Git clone after
recent GitHub clone instability. Both ydl43 commits were verified present
locally, and the workspace followed the BugsInPy reset/copy-test-file flow.
