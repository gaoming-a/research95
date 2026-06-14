# youtube-dl_11 Candidate Validation

Date: 2026-06-14

`bugsinpy_youtube-dl_11` was admitted through the controlled EVP-7
project-level P2P-broad gate.

## Scope

- Task: `bugsinpy_youtube-dl_11`
- Project: `youtube-dl`
- Framework: `unittest`
- F2P oracle:
  `test.test_utils.TestUtil.test_str_to_int`
- P2P manifest:
  `data/p2p_scopes/bugsinpy_youtube-dl_11_p2p_broad.json`
- Candidate records:
  `outputs/youtubedl11_candidate_validation_001/candidates.jsonl`
- Oracle validation:
  `outputs/youtubedl11_candidate_validation_001/oracle_validation_summary.json`
- P2P validation:
  `outputs/youtubedl11_candidate_validation_001/p2p_validation_summary.json`

Raw workdirs and validation logs remain under ignored `outputs/`.

## P2P-Broad Summary

- Scope type: `project_level_p2p_broad`
- Test framework: `unittest`
- Collected/common nodeids: 2326
- Excluded generated download nodeids: 2095
- Excluded static external-dependency tests: 66
- Excluded retained F2P oracle: 1
- Excluded buggy-baseline failures: 4
- Retained P2P-broad tests: 160
- Collection error files: 1 common import error file
- Scope policy: `youtube_dl_dynamic_download_nodeid_exclusion_v1`

The retained P2P-broad set excludes
`test.test_download.TestDownload*` and does not include the F2P oracle. The
common collection error is `test.test_subtitles`, which fails in both buggy and
fixed checkouts because `FunnyOrDieIE` cannot be imported from
`youtube_dl.extractor`.

## Candidate Summary

Four candidate patches were generated:

- `bugsinpy_youtube-dl_11__reference_fix`: correct reference patch.
- `bugsinpy_youtube-dl_11__empty_diff_control`: no-op negative.
- `bugsinpy_youtube-dl_11__int_only_non_string_guard`: partial negative that
  preserves integers but still mishandles `None`.
- `bugsinpy_youtube-dl_11__irrelevant_noop_assignment`: irrelevant negative.

Retained-oracle validation:

- candidates = 4
- patch applied = 4/4
- oracle ran = 4/4
- oracle passed = 1/4

P2P validation:

- candidates = 4
- retained oracle passed = 1
- P2P-broad test count = 160
- labels:
  - `correct_under_f2p_and_p2p_broad`: 1
  - `incorrect_issue_not_fixed`: 3

## Admission Boundary

`bugsinpy_youtube-dl_11` is included in `p2p_broad_main`. This admission uses
project-level P2P-broad validation and does not rely on task-file P2P,
dependency installation, fixture shims, or model API calls.

After admission, the no-API EVP-7 structural artifacts were rebuilt to
13 tasks, 66 candidates, and 264 E0/E2/E4/E6 evidence packets. The latest real
DeepSeek G5 run remains the earlier 12-task/62-candidate/248-packet run until a
fresh 264-packet real run is explicitly authorized and audited.
