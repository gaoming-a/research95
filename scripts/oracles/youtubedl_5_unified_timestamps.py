from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    sys.path.insert(0, str(Path.cwd()))

    from youtube_dl.utils import unified_timestamp

    strptime_pm = unified_timestamp("2/2/2015 6:47:40 PM", day_first=False)
    if strptime_pm != 1422902860:
        raise AssertionError(f"unexpected strptime PM timestamp: {strptime_pm!r}")

    parsedate_pm = unified_timestamp("May 16, 2016 11:15 PM")
    if parsedate_pm != 1463440500:
        raise AssertionError(f"unexpected parsedate PM timestamp: {parsedate_pm!r}")

    print("oracle_passed")


if __name__ == "__main__":
    main()
