from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    sys.path.insert(0, str(Path.cwd()))

    from youtube_dl.utils import js_to_json

    quoted_title = r'''"The CW\'s \'Crazy Ex-Girlfriend\'"'''
    converted = js_to_json(quoted_title)
    if converted != '''"The CW's 'Crazy Ex-Girlfriend'"''':
        raise AssertionError(f"unexpected converted title: {converted!r}")

    escaped_unicode = (
        r'"SAND Number: SAND 2013-7800P\nPresenter: Tom Russo\n'
        r'Habanero Software Training - Xyce Software\nXyce, Sandia\u0027s"'
    )
    converted_unicode = js_to_json(escaped_unicode)
    if json.loads(converted_unicode) != json.loads(escaped_unicode):
        raise AssertionError(f"escaped unicode string changed semantics: {converted_unicode!r}")

    print("oracle_passed")


if __name__ == "__main__":
    main()
