# youtube-dl_7 P2P Execution Attempt

Date: 2026-06-13

## User Decision

The user approved one bounded project-level P2P-broad attempt for
`bugsinpy_youtube-dl_7` with the reply:

> `1、批准 2、暂时不用管`

The same reply instructed that GitHub sync can be ignored temporarily.

## Approved Scope

- Task: `bugsinpy_youtube-dl_7`
- Scope type: `project_level_p2p_broad`
- Fail-to-pass nodeid:
  `test.test_utils.TestUtil.test_js_to_json_realworld`
- Command source:
  `docs/experiments/evp7_youtubedl_p2p_decision_packet_20260613.md`

## Attempt Result

The approved command was executed once. It did not produce
`data/p2p_scopes/bugsinpy_youtube-dl_7_p2p_broad.json` before the tool-level
timeout.

Observed execution state:

- output dir created: `outputs/p2p_scope_builds/bugsinpy_youtube-dl_7`;
- tracked manifest created: no;
- lingering builder/unittest processes were terminated after timeout;
- the active unittest child was running dynamically generated
  `test.test_download.TestDownload.*` tests.

## Diagnosis

This is an execution-chain and evidence-boundary issue, not a completed P2P
result. The current static source-token exclusions do not catch dynamically
generated `TestDownload` unittest cases because they do not correspond to
static AST `test_` methods. Continuing would require an explicit nodeid-level
exclusion or another documented scope-policy revision before rerunning real
P2P.

## Follow-up Scope Policy

The user later allowed this explicit execution-chain fix and clarified that
future clear fixes of this kind do not need confirmation unless there is a
genuinely ambiguous option.

The bounded rerun policy is:

- policy name: `youtube_dl_dynamic_download_nodeid_exclusion_v1`;
- excluded nodeid prefix: `test.test_download.TestDownload`;
- retained fail-to-pass oracle remains
  `test.test_utils.TestUtil.test_js_to_json_realworld`;
- no other youtube-dl task is added by this decision;
- dry-run must pass before the real P2P rerun.

## Rerun Diagnosis

The first rerun with the dynamic-download prefix exclusion still timed out
without producing a manifest. The active unittest child was
`test.test_age_restriction.TestAgeRestriction.test_youtube`.

This exposed a separate execution-chain bug: unittest dotted nodeids were not
mapped back to source files for static filtering, and method-only source
segments missed same-file helper calls that perform `YoutubeDL(...).download`.
The builder fix keeps the existing static external-dependency policy, but makes
it effective for unittest dotted nodeids and same-file helper wrappers.

## Completed Rerun Result

After the builder fix, the bounded rerun completed and produced:

- manifest: `data/p2p_scopes/bugsinpy_youtube-dl_7_p2p_broad.json`;
- collected/common unittest nodeids: 1472;
- excluded by nodeid prefix: 1297;
- excluded by static external-dependency tokens: 64;
- excluded retained fail-to-pass oracle: 1;
- included P2P-broad tests: 108.

The manifest records `youtube_dl_dynamic_download_nodeid_exclusion_v1` and no
included P2P-broad nodeid starts with `test.test_download.TestDownload`.
