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
