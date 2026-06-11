from __future__ import annotations

import collections
import collections.abc
import os
import sys
import tempfile
from pathlib import Path


for _name in dir(collections.abc):
    if not hasattr(collections, _name):
        setattr(collections, _name, getattr(collections.abc, _name))


def main() -> None:
    sys.path.insert(0, os.getcwd())

    import pysnooper

    with tempfile.TemporaryDirectory(prefix="pysnooper_oracle_") as folder:
        log_path = Path(folder) / "foo.log"

        @pysnooper.snoop(log_path)
        def foo() -> int:
            value = "失败"
            return len(value)

        result = foo()
        if result != 2:
            raise AssertionError(f"unexpected function result: {result!r}")

        output = log_path.read_text(encoding="utf-8")

    if "失败" not in output:
        raise AssertionError(f"UTF-8 log output did not contain Chinese text: {output!r}")

    print("oracle_passed")


if __name__ == "__main__":
    main()
