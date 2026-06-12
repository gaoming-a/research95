# EVP-7 youtube-dl F2P-Only Continuation 2026-06-13

This batch extends controlled expansion triage inside the `youtube-dl` family.
It does not admit any task into `p2p_broad_main`.

## Scope

- `bugsinpy_youtube-dl_3`: `python -m unittest -q test.test_utils.TestUtil.test_unescape_html`
- `bugsinpy_youtube-dl_4`: `python -m unittest -q test.test_jsinterp.TestJSInterpreter.test_call`
- `bugsinpy_youtube-dl_5`: `python -m unittest -q test.test_utils.TestUtil.test_unified_timestamps`

No dependency install, checkout edit, test edit, fixture shim, or
project-level P2P-broad construction was performed.

## Results

| Task | Buggy | Fixed | Probe status |
| --- | --- | --- | --- |
| `bugsinpy_youtube-dl_3` | fails target unittest | passes target unittest | `f2p_established_p2p_not_attempted` |
| `bugsinpy_youtube-dl_4` | errors in target unittest | passes target unittest | `f2p_established_p2p_not_attempted` |
| `bugsinpy_youtube-dl_5` | errors in target unittest | passes target unittest | `f2p_established_p2p_not_attempted` |

## Implication

Together with `bugsinpy_youtube-dl_2`, the current controlled probes have four
new `youtube-dl` tasks with clean F2P signal under the no-install/no-edit
boundary. None are main-cohort tasks until bounded project-level P2P-broad
construction and candidate revalidation pass.

