from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    sys.path.insert(0, str(Path.cwd()))

    from youtube_dl.utils import str_to_int

    if str_to_int("1,234") != 1234:
        raise AssertionError("str_to_int should parse comma-separated digits")

    if str_to_int(None) is not None:
        raise AssertionError("str_to_int should preserve None")

    if str_to_int(523) != 523:
        raise AssertionError("str_to_int should preserve non-string integers")

    print("oracle_passed")


if __name__ == "__main__":
    main()
