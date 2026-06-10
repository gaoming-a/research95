# P2P Feasibility Sweep Update

Date: 2026-06-10.

This note records the first bounded feasibility sweep after freezing Luigi as a
pending large-suite stress case.

## Inclusion Rule

The final main cohort remains:

```text
project_level_p2p_status == completed
and p2p_broad_main_included is true
```

Tasks that fail the bounded sweep are retained in task-level accounting as
`pending_blocked`; they are not silently removed.

## Current Sweep Table

| task | project | project-level P2P status | collected / nodeids | blocker | main cohort |
|---|---|---|---:|---|---|
| `bugsinpy_httpie_5` | httpie | completed | 17 / 17 | none after external-dependency exclusions | yes |
| `bugsinpy_luigi_3` | luigi | pending_blocked | 113 files / 904 nodeids | 44 collection errors; two bounded attempts timed out | no |
| `bugsinpy_luigi_4` | luigi | pending_blocked | shared Luigi project | shared large-suite blocker; project-level attempt not continued | no |
| `bugsinpy_httpie_1` | httpie | pending_blocked | 19 files / 0 nodeids | missing `pytest_httpbin` collection dependency | no |
| `bugsinpy_httpie_2` | httpie | pending_blocked | not completed | bounded project-level scope timeout | no |
| `bugsinpy_httpie_3` | httpie | pending_blocked | not completed | bounded project-level scope timeout | no |
| `bugsinpy_httpie_4` | httpie | pending_blocked | 15 files / 0 nodeids initially | legacy requests compatibility; later bounded scope timeout | no |

## Interpretation

The first replacement sweep did not yet add new `p2p_broad_main` tasks beyond
`httpie_5`.

This is not a reason to lower the main standard. It shows that project-level
P2P-broad construction is a real feasibility constraint and must be reported
transparently.

## Next Selection Guidance

The next sweep should prioritize projects with:

- no mandatory network-service pytest fixtures;
- no bundled virtual environment inside the checkout;
- project-level collection within 5-8 minutes;
- collection errors <= 10, or errors clearly attributable to unavailable
  external dependencies;
- at least 3 P2P-broad tests over 3 stability runs.

Candidate projects from the existing screening registry should be evaluated
with this feasibility gate before any verifier API expansion.
