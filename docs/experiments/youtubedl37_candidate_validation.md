# youtube-dl_37 Candidate Validation

Date: 2026-06-14

Task: `bugsinpy_youtube-dl_37`

Target test: `test.test_utils.TestUtil.test_uppercase_escpae`

Issue: `uppercase_escape` must decode uppercase Unicode escape sequences on
Python 3 without calling the removed `str.decode` method.

## Scope

- Buggy commit: `98b7cf1acefe398f792ca6ff4c5f84f1b7785fcb`
- Fixed commit: `676eb3f2dd542be3e84780b18388253382d3e465`
- Source patch: `youtube_dl/utils.py`
- Test patch: `test/test_utils.py`
- P2P manifest: `data/p2p_scopes/bugsinpy_youtube-dl_37_p2p_broad.json`

## F2P

- Buggy checkout: target test fails with
  `AttributeError: 'str' object has no attribute 'decode'`.
- Fixed checkout: target test passes.

## P2P-Broad

Policy: `youtube_dl_dynamic_download_nodeid_exclusion_v1`

- Common collected tests: 528
- Generated downloader tests excluded by nodeid prefix: 380
- Static external-dependency tests excluded: 73
- F2P oracle excluded: 1
- Buggy-baseline failures excluded: 44
- Retained P2P-broad tests: 30
- Collection error files: 0

## Candidates

The candidate set contains one correct reference patch and three negatives:

- `reference_fix`: official source patch.
- `empty_diff_control`: no source change.
- `import_only_codecs`: imports `codecs` but leaves the failing
  `str.decode` call unchanged.
- `raw_escape_passthrough`: avoids decoding and returns the raw escape text.

## Validation

Candidate generation:

- Builder: `scripts/build_youtubedl37_candidates.py`
- Output: `outputs/youtubedl37_candidate_validation_001/candidates.jsonl`
- Candidate count: 4

Retained-oracle validation:

- Summary:
  `outputs/youtubedl37_candidate_validation_001/oracle_validation_summary.json`
- Patch applied: 4/4
- Oracle ran: 4/4
- Oracle passed: 1/4
- Status: passed

P2P-broad validation:

- Summary:
  `outputs/youtubedl37_candidate_validation_001/p2p_validation_summary.json`
- P2P-broad test count: 30
- Patch applied: 4/4
- Retained oracle passed: 1/4
- Labels:
  - `correct_under_f2p_and_p2p_broad`: 1
  - `incorrect_issue_not_fixed`: 3
- Status: passed

## Admission

`bugsinpy_youtube-dl_37` is included in `p2p_broad_main`. This admission uses
project-level P2P-broad evidence only and does not change the boundary that the
latest real DeepSeek G5 run remains the earlier 12-task / 62-candidate /
248-packet cohort.
