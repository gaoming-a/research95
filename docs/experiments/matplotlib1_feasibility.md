# Matplotlib 1 Feasibility Probe

Date: 2026-06-12

## Decision

`bugsinpy_matplotlib_1` is excluded from `p2p_broad_main` as
`blocked_native_extension_import`.

## Scope

- Project: `matplotlib`
- Buggy commit: `c404d1f716e8aaefd4d7371ff49673e9c1f7f07c`
- Fixed commit: `5324adaec6a7fd3d78dea7b28451d5f6e95392a6`
- F2P command:
  - `pytest lib/matplotlib/tests/test_bbox_tight.py::test_noop_tight_bbox`

## Probe Result

The checkouts were expensive but reached BugsInPy marker-file creation. The
buggy retained checkout did not contain the target test file at the expected
`lib/matplotlib/tests/test_bbox_tight.py` path, so the buggy oracle could not be
run.

The fixed retained checkout did contain the target test file. Running the target
test with `PYTHONPATH=checkout/lib` and `MPLBACKEND=Agg` failed during Matplotlib
import because the compiled `ft2font` extension is unavailable.

## Boundary

Matplotlib's `setup.sh` requests Cython and an editable install of the checkout.
That path requires native/build-time work and is outside this round's no-global
install and no-unapproved-build boundary. No editable install, dependency
substitution, source edit, test fixture edit, or task-file P2P downgrade was
used.

No project-level P2P-broad construction was attempted because F2P was not
established.
