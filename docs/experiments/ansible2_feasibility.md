# Ansible 2 Feasibility Probe

Date: 2026-06-12

## Decision

`bugsinpy_ansible_2` is excluded from `p2p_broad_main` as
`pending_blocked_checkout_timeout`.

## Scope

- Project: `ansible`
- Buggy commit: `de59b17c7f69d5cfb72479b71776cc8b97e29a6b`
- Fixed commit: `5b9418c06ca6d51507468124250bb58046886be6`
- F2P commands:
  - `pytest test/units/utils/test_version.py::test_alpha`
  - `pytest test/units/utils/test_version.py::test_numeric`

## Result

The buggy checkout was started serially, following the same-task checkout
parallelism boundary discovered during the Tornado 9 probe. The checkout did
not complete within the bounded feasibility window and did not write
`bugsinpy_run_test.sh` into the retained checkout.

The hanging checkout process was terminated, and the incomplete
`ansible_2` retained workspace was removed. No fixed checkout, F2P probe, or
project-level P2P-broad construction was attempted.

## Boundary

This is a checkout feasibility blocker, not a label result. No Ansible source
files, tests, or fixtures were edited. No global dependencies were installed and
no task-file P2P downgrade was used.
