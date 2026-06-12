# EVP-7 youtube-dl P2P Decision Packet 2026-06-13

This packet records the next explicit decision. It does not execute P2P and
does not admit any new task into `p2p_broad_main`.

## Background

The current main cohort remains seven project-level P2P tasks across four
projects. Post-G5 controlled expansion did not find fresh-project promising
candidates. The only efficient clean-F2P lane found so far is the `youtube-dl`
family.

`bugsinpy_youtube-dl_1` already showed the key risk: the retained F2P oracle was
clear, but project-level unittest P2P discovery over `test/` reached the bounded
runtime without producing a manifest. Because of that history, the current
seven F2P-established `youtube-dl` probes must be treated as P2P candidates, not
main-cohort tasks.

## Current Candidate Set

F2P-established, P2P-not-attempted candidates:

- `bugsinpy_youtube-dl_2`
- `bugsinpy_youtube-dl_3`
- `bugsinpy_youtube-dl_4`
- `bugsinpy_youtube-dl_5`
- `bugsinpy_youtube-dl_6`
- `bugsinpy_youtube-dl_7`
- `bugsinpy_youtube-dl_11`

All seven were established without dependency installation, checkout edits,
test edits, fixture shims, or task-file P2P downgrade.

## Decision Needed

Approve or reject one bounded project-level P2P-broad attempt for the
`youtube-dl` family.

Recommended first representative: `bugsinpy_youtube-dl_6`.

Reason: it is a pure utility unittest with a clear buggy fail and fixed pass,
and it is less likely than downloader/network tests to depend on external
services. This is an inference from the recorded target command; it is not yet
P2P evidence.

## Proposed Boundary If Approved

- Run only one `youtube-dl` project-level P2P attempt first.
- Use project-level unittest discovery under `test/`, not task-file P2P.
- Exclude the retained F2P oracle.
- Keep static exclusions for obvious network/external execution tokens.
- Use bounded runtime and batch-first validation.
- Do not install dependencies or edit source, tests, fixtures, or checkout
  files.
- Stop after the first representative attempt if it repeats the
  `youtube-dl_1` timeout pattern.

Command template:

```powershell
python scripts\build_pass_to_pass_scope.py `
  --task-id bugsinpy_youtube-dl_6 `
  --project youtube-dl `
  --test-framework unittest `
  --unittest-start-dir test `
  --unittest-pattern "test_*.py" `
  --fail-to-pass-nodeid "test.test_utils.TestUtil.test_parse_dfxp_time_expr" `
  --scope-type project_level_p2p_broad `
  --runs 3 `
  --timeout-seconds 30 `
  --batch-timeout-seconds 1800 `
  --batch-size 50 `
  --batch-first `
  --static-exclude-token "YoutubeDL(" `
  --static-exclude-token "download(" `
  --static-exclude-token "urlopen" `
  --static-exclude-token "http://" `
  --static-exclude-token "https://" `
  --out-dir outputs\p2p_scope_builds\bugsinpy_youtube-dl_6 `
  --manifest-out data\p2p_scopes\bugsinpy_youtube-dl_6_p2p_broad.json
```

## Static Preflight

A no-run static preflight over the existing `bugsinpy_youtube-dl_6`
buggy/fixed checkouts inspected unittest method definitions only. It did not
execute F2P or P2P tests and did not create a P2P manifest.

| Version | Test files | Test methods | Excluded by static tokens | Remaining methods |
| --- | ---: | ---: | ---: | ---: |
| buggy | 20 | 154 | 43 | 111 |
| fixed | 20 | 154 | 43 | 111 |

The remaining method set is identical across buggy and fixed checkouts:

- common remaining methods: 111;
- buggy-only remaining methods: 0;
- fixed-only remaining methods: 0;
- `test/test_utils.py` remaining methods: 46 on both sides.

This preflight supports a bounded representative attempt, but it does not prove
that dynamic project-level P2P will finish within budget.

## Success Gate

A `youtube-dl` task can move toward admission only if all of the following are
true:

- project-level P2P manifest is generated;
- `p2p_broad_size >= 3`;
- reference patch passes retained F2P and P2P-broad;
- candidate patches are constructed and revalidated under F2P plus P2P-broad;
- cohort registry records `project_level_p2p_status = completed` and
  `p2p_broad_main_included = true`.

## Failure Gate

Stop and record a blocker if any of the following occurs:

- project-level discovery or dynamic P2P reaches the bounded runtime without a
  usable manifest;
- generated P2P-broad size is below 3;
- reference patch fails P2P-broad;
- the attempt requires dependency installation, fixture edits, source edits, or
  task-file P2P downgrade.

## Efficiency Note

Further F2P-only `youtube-dl` probes are now lower value than resolving this P2P
decision. The efficient next step is one bounded representative P2P attempt, not
bulk-adding more F2P candidates.
