# youtube-dl 5 Candidate Validation

Date: 2026-06-13

## Scope

`bugsinpy_youtube-dl_5` was admitted through the same controlled
project-level P2P-broad boundary used for the earlier youtube-dl admissions.

- Retained F2P oracle:
  `test.test_utils.TestUtil.test_unified_timestamps`.
- Hidden oracle:
  `scripts/oracles/youtubedl_5_unified_timestamps.py`.
- P2P manifest:
  `data/p2p_scopes/bugsinpy_youtube-dl_5_p2p_broad.json`.
- Candidate output:
  `outputs/youtubedl5_candidate_validation_001/candidates.jsonl`.

## P2P Scope

The project-level unittest P2P-broad construction used
`youtube_dl_dynamic_download_nodeid_exclusion_v1`.

- collected tests: 1890;
- dynamic downloader nodeids excluded: 1673;
- static external-dependency tests excluded: 80;
- retained F2P oracle excluded: 1;
- buggy-baseline failures excluded: 8;
- retained P2P-broad tests: 128;
- retained dynamic download nodeids: 0.

## Candidates

Four admission candidates were built:

| candidate | type | label after F2P + P2P-broad |
| --- | --- | --- |
| `candidate_0001` | reference fix | `correct_under_f2p_and_p2p_broad` |
| `candidate_0002` | empty diff | `incorrect_issue_not_fixed` |
| `candidate_0003` | strptime-PM-only partial | `incorrect_issue_not_fixed` |
| `candidate_0004` | irrelevant noop assignment | `incorrect_issue_not_fixed` |

Validation summary:

- patch applied: 4/4;
- retained oracle passed: 1/4;
- P2P-broad test count: 128;
- final labels: 1 correct reference, 3 issue-not-fixed negatives.

## Admission Result

`bugsinpy_youtube-dl_5` is included in `p2p_broad_main`.

After rebuilding no-API EVP-7 artifacts, the current structural cohort is:

- 10 tasks;
- 5 projects;
- 54 candidates;
- 216 E0/E2/E4/E6 evidence packets;
- E0/E2/E4/E6 each complete for 54 candidates;
- G1 packet completeness passed;
- G2 leakage audit passed;
- G3 deterministic tool-only baseline readiness passed;
- G4 schema stability passed;
- G5 prompt manifest readiness passed without API.

The latest real DeepSeek G5 full run remains the earlier 200-packet run and
must not be treated as covering this 216-packet cohort until a fresh run is
executed and audited.
