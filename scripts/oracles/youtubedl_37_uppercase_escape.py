from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    sys.path.insert(0, str(Path.cwd()))

    from youtube_dl.utils import uppercase_escape

    assert uppercase_escape("plain") == "plain"
    assert uppercase_escape("aä") == "aä"
    assert uppercase_escape(r"\U0001d550") == "𝕐"
    assert uppercase_escape(r"x\U0001d550y") == "x𝕐y"
    assert uppercase_escape(r"\U0001d550-\U0001d552") == "𝕐-𝕒"


if __name__ == "__main__":
    main()
