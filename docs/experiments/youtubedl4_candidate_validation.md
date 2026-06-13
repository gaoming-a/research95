# youtube-dl_4 Candidate Validation

Date: 2026-06-13

`bugsinpy_youtube-dl_4` was admitted through the controlled EVP-7
project-level P2P-broad gate.

## Scope

- Task: `bugsinpy_youtube-dl_4`
- Project: `youtube-dl`
- Framework: `unittest`
- F2P oracle:
  `test.test_jsinterp.TestJSInterpreter.test_call`
- P2P manifest:
  `data/p2p_scopes/bugsinpy_youtube-dl_4_p2p_broad.json`
- Candidate records:
  `outputs/youtubedl4_candidate_validation_001/candidates.jsonl`
- Oracle validation:
  `outputs/youtubedl4_candidate_validation_001/oracle_validation_summary.json`
- P2P validation:
  `outputs/youtubedl4_candidate_validation_001/p2p_validation_summary.json`

Raw workdirs and validation logs remain under ignored `outputs/`.

## P2P-Broad Summary

- Scope type: `project_level_p2p_broad`
- Test framework: `unittest`
- Collected/common nodeids: 1994
- Excluded generated download nodeids: 1772
- Excluded static external-dependency tests: 81
- Excluded retained F2P oracle: 1
- Excluded buggy-baseline failures: 3
- Retained P2P-broad tests: 137
- Collection error files: 0
- Scope policy: `youtube_dl_dynamic_download_nodeid_exclusion_v1`

The retained P2P-broad set excludes
`test.test_download.TestDownload*` and does not include the F2P oracle.

## Candidate Summary

Four candidate patches were generated:

- `bugsinpy_youtube-dl_4__reference_fix`: correct reference patch.
- `bugsinpy_youtube-dl_4__empty_diff_control`: no-op negative.
- `bugsinpy_youtube-dl_4__regex_only_empty_args`: partial negative that
  accepts empty call syntax but still resolves an empty local variable.
- `bugsinpy_youtube-dl_4__irrelevant_noop_assignment`: irrelevant negative.

Retained-oracle validation:

- candidates = 4
- patch applied = 4/4
- oracle ran = 4/4
- oracle passed = 1/4

P2P validation:

- candidates = 4
- retained oracle passed = 1
- P2P-broad test count = 137
- labels:
  - `correct_under_f2p_and_p2p_broad`: 1
  - `incorrect_issue_not_fixed`: 3

## Admission Boundary

`bugsinpy_youtube-dl_4` is included in `p2p_broad_main`. This admission uses
project-level P2P-broad validation and does not rely on task-file P2P,
dependency installation, fixture shims, or model API calls.
