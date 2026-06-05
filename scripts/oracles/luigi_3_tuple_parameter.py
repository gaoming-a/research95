from __future__ import annotations

import collections
import collections.abc
import inspect
import os
import sys
from collections import namedtuple


def patch_python311_compatibility() -> None:
    for name in dir(collections.abc):
        if not hasattr(collections, name):
            setattr(collections, name, getattr(collections.abc, name))

    if not hasattr(inspect, "ArgSpec"):
        inspect.ArgSpec = namedtuple("ArgSpec", "args varargs keywords defaults")

    if not hasattr(inspect, "getargspec"):

        def getargspec(func):
            spec = inspect.getfullargspec(func)
            return inspect.ArgSpec(spec.args, spec.varargs, spec.varkw, spec.defaults)

        inspect.getargspec = getargspec


def main() -> None:
    patch_python311_compatibility()
    sys.path.insert(0, os.getcwd())

    import luigi  # noqa: E402

    value = (1, 2, 3)
    parameter = luigi.TupleParameter()
    serialized = parameter.serialize(value)
    parsed = parameter.parse(serialized)

    assert parsed == value, (serialized, parsed)
    assert isinstance(parsed, tuple), type(parsed)
    print("oracle_passed")


if __name__ == "__main__":
    main()
