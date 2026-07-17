# ruff: noqa: E402
"""Run legacy unittest nodes under the current Python runtime."""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/run_unittest_legacy_py311.py")

import inspect
import os
import sys
import unittest
from collections import namedtuple


def apply_runtime_compatibility() -> None:
    if not hasattr(inspect, "ArgSpec"):
        inspect.ArgSpec = namedtuple("ArgSpec", "args varargs keywords defaults")

    if not hasattr(inspect, "getargspec"):

        def getargspec(func: object) -> object:
            spec = inspect.getfullargspec(func)
            return inspect.ArgSpec(spec.args, spec.varargs, spec.varkw, spec.defaults)

        inspect.getargspec = getargspec


def main(argv: list[str]) -> int:
    apply_runtime_compatibility()
    sys.path.insert(0, os.getcwd())
    program = unittest.main(module=None, argv=[sys.argv[0], *argv], exit=False)
    return 0 if program.result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
