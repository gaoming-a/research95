from __future__ import annotations

import os
import sys

try:
    from StringIO import StringIO
except ImportError:  # pragma: no cover - Python 3 path
    from io import StringIO


def main() -> None:
    sys.path.insert(0, os.getcwd())

    from tqdm import format_meter, tqdm

    meter = format_meter(1, 9999, 1, unit_scale=True)
    if "10.0K " not in meter:
        raise AssertionError(f"expected 9999 to round to 10.0K, got {meter!r}")

    progressbar = tqdm(total=2, file=StringIO(), miniters=1)
    try:
        length = len(progressbar)
    finally:
        progressbar.close()
    if length != 2:
        raise AssertionError(f"expected len(tqdm(total=2)) == 2, got {length!r}")

    print("oracle_passed")


if __name__ == "__main__":
    main()
