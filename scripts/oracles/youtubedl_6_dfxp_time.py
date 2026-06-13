from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    sys.path.insert(0, str(Path.cwd()))

    from youtube_dl.utils import dfxp2srt, parse_dfxp_time_expr

    if parse_dfxp_time_expr(None) is not None:
        raise AssertionError("None time expression should remain invalid")
    if parse_dfxp_time_expr("") is not None:
        raise AssertionError("empty time expression should remain invalid")

    dfxp_data = """<?xml version="1.0" encoding="UTF-8"?>
        <tt xmlns="http://www.w3.org/ns/ttml">
        <body>
            <div>
                <p begin="0" end="1">First</p>
                <p begin="1" dur="1">Second</p>
                <p begin="2" end="-1">Invalid end ignored</p>
                <p begin="-1" end="-1">Invalid begin ignored</p>
                <p begin="3" dur="-1">Invalid duration ignored</p>
                <p end="4">Missing begin ignored</p>
            </div>
        </body>
        </tt>"""
    expected = """1
00:00:00,000 --> 00:00:01,000
First

2
00:00:01,000 --> 00:00:02,000
Second

"""
    converted = dfxp2srt(dfxp_data)
    if converted != expected:
        raise AssertionError(f"unexpected SRT output: {converted!r}")

    print("oracle_passed")


if __name__ == "__main__":
    main()
