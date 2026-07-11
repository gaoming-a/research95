# DSA P4 `bugsinpy_tornado_10` Environment Gate v0.1

Date: 2026-07-11

## Outcome

`DISCARD_PRE_CANDIDATE_ENVIRONMENT_BUILD_FAILURE`

The frozen task-specific image could not be built. The first command in the
official BugsInPy `setup.sh`, `pip install unittest`, exited 1 because no such
installable distribution exists. This is an official metadata/environment
failure, not a candidate, test, oracle, model, or network outcome.

Under the signed P3 exclusion and no-redesign rules, the command cannot be
deleted, ignored, or replaced with an outcome-motivated dependency repair.
The task is therefore discarded before official F2P, regression-pool discovery,
or T1 materialization.

## Frozen inputs

- attempted-from commit:
  `36e3fc0fa06dcd5cc20a44307e587bda8a8c3592`;
- replacement cursor SHA-256:
  `24f37f3f2eefe99c9346b4b141965cb137e8f7dfb87e6e11eaa0ac909b0fbf2e`;
- source/context record SHA-256:
  `cf5b5bf5b44885161d538a2063090afdc347396593bd90eeef0687337d686038`;
- official `setup.sh` SHA-256:
  `d3a4076796d738e69fdc78f14825c1f2e48cd317367ac3812b2e9df6ff8b580b`;
- Python lock: `py370` / Python 3.7.0 / SHA-256
  `2b79c03af7d1cffa7d8a91b0830da6ddc27e353f7ec482434173671824825b82`;
- toolchain image ID:
  `sha256:97e089cee02d0908e374f7b784ee0ffbb2fe5a2d64f619335aa962dc3ab3d768`.

## Environment evidence

The frozen commands and exit codes were:

| index | command | exit |
|---:|---|---:|
| 1 | `pip install unittest` | 1 |
| 2 | `pip install python-gettext` | 0 |
| 3 | `pip install tornado` | 0 |

Both empty requirements passes and `pip check` exited 0, but the aggregate
setup status remained 1. The first log contains both exact failure markers:
`Could not find a version that satisfies the requirement unittest` and
`No matching distribution found for unittest`. The task image tag was absent
after the failed build.

The raw ignored logs are hash-bound by
`data/hidden/dsa_p4_pre_candidate_discard_v0_1.json`. Its record SHA-256 is
`6fd7c9b54962796c61e382353b5beae2ff7d58f681de792f63d98a0d7ce817f9`;
`scripts/dsa2026_p4_record_pre_candidate_discard.py` performs write/check replay.

## Boundary audit

- official reference F2P executed: no;
- regression pool discovered/frozen: no;
- transformed candidate materialized or run: no;
- Tornado record in oracle/candidate/result registries: no;
- model API calls: 0;
- dependency, oracle, transform, or task repair: none;
- P5/rendered prompt/paper result change: none.

This Gate consumes the current cursor task and ends the bounded Goal. A later,
separately authorized Goal may recompute the primary-first replacement cursor;
this record does not select or start the next task.
