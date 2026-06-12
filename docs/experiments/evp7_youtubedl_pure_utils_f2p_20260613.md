# EVP-7 youtube-dl Pure-Utils F2P-Only Triage 2026-06-13

This batch continues controlled expansion triage inside the `youtube-dl`
family. It does not admit any task into `p2p_broad_main`.

## Scope

- `bugsinpy_youtube-dl_6`: `python -m unittest -q test.test_utils.TestUtil.test_parse_dfxp_time_expr`
- `bugsinpy_youtube-dl_7`: `python -m unittest -q test.test_utils.TestUtil.test_js_to_json_realworld`
- `bugsinpy_youtube-dl_11`: `python -m unittest -q test.test_utils.TestUtil.test_str_to_int`

No dependency install, checkout edit, test edit, fixture shim, or
project-level P2P-broad construction was performed.

## Results

| Task | Buggy | Fixed | Probe status |
| --- | --- | --- | --- |
| `bugsinpy_youtube-dl_6` | fails target unittest | passes target unittest | `f2p_established_p2p_not_attempted` |
| `bugsinpy_youtube-dl_7` | fails target unittest | passes target unittest | `f2p_established_p2p_not_attempted` |
| `bugsinpy_youtube-dl_11` | errors in target unittest | passes target unittest | `f2p_established_p2p_not_attempted` |

## Implication

The controlled `youtube-dl` probes now have seven clean F2P candidates:
`youtube-dl_2`, `youtube-dl_3`, `youtube-dl_4`, `youtube-dl_5`,
`youtube-dl_6`, `youtube-dl_7`, and `youtube-dl_11`. They remain P2P candidates,
not main-cohort tasks.

