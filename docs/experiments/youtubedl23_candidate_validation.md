# youtube-dl_23 Candidate Validation

Date: 2026-06-14

Task: `bugsinpy_youtube-dl_23`

Target test: `test.test_utils.TestUtil.test_js_to_json_edgecases`

Issue: `js_to_json` must ignore JavaScript single-line `//` comments while
preserving existing string, block-comment, and trailing-comma behavior.

## Scope

- Buggy commit: `a22b2fd19bd8c08d50f884d1903486d4f00f76ec`
- Fixed commit: `b3ee552e4b918fb720111b23147e24fa5475a74b`
- Source patch: `youtube_dl/utils.py`
- Test patch: `test/test_utils.py`
- P2P manifest: `data/p2p_scopes/bugsinpy_youtube-dl_23_p2p_broad.json`

## F2P

- Buggy checkout: target test fails with `JSONDecodeError` on
  `{ 0: // comment\n1 }`.
- Fixed checkout: target test passes.

## P2P-Broad

Policy: `youtube_dl_dynamic_download_nodeid_exclusion_v1`

- Common collected tests: 2059
- Generated downloader tests excluded by nodeid prefix: 1836
- Static external-dependency tests excluded: 82
- F2P oracle excluded: 1
- Buggy-baseline failures excluded: 3
- Retained P2P-broad tests: 137
- Collection error files: 0

## Candidates

The candidate set contains one correct reference patch and three negatives:

- `reference_fix`: official source patch.
- `empty_diff_control`: no source change.
- `regex_only_line_comment`: tokenizes `//` comments but does not drop them.
- `replacer_only_line_comment`: can drop `//` tokens if seen, but never
  tokenizes them.

## Validation

Candidate generation:

- Builder: `scripts/build_youtubedl23_candidates.py`
- Output: `outputs/youtubedl23_candidate_validation_001/candidates.jsonl`
- Candidate count: 4

Retained-oracle validation:

- Summary:
  `outputs/youtubedl23_candidate_validation_001/oracle_validation_summary.json`
- Patch applied: 4/4
- Oracle ran: 4/4
- Oracle passed: 1/4
- Status: passed

P2P-broad validation:

- Summary:
  `outputs/youtubedl23_candidate_validation_001/p2p_validation_summary.json`
- P2P-broad test count: 137
- Patch applied: 4/4
- Retained oracle passed: 1/4
- Labels:
  - `correct_under_f2p_and_p2p_broad`: 1
  - `incorrect_issue_not_fixed`: 3
- Status: passed

## Admission

`bugsinpy_youtube-dl_23` is included in `p2p_broad_main`. This admission uses
project-level P2P-broad evidence only and does not change the boundary that the
latest real DeepSeek G5 run remains the earlier 12-task / 62-candidate /
248-packet cohort.
