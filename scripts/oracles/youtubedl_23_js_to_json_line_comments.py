from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    sys.path.insert(0, str(Path.cwd()))

    from youtube_dl.utils import js_to_json

    assert json.loads(js_to_json('{ 0: // comment\n1 }')) == {"0": 1}
    assert json.loads(js_to_json('[1, // comment\n2]')) == [1, 2]
    assert json.loads(js_to_json('{ 0: /* " \n */ ",]" , }')) == {"0": ",]"}
    assert json.loads(js_to_json('{"url": "http://example.com/a//b"}')) == {
        "url": "http://example.com/a//b"
    }
    assert json.loads(js_to_json('{"text": "// not a comment"}')) == {
        "text": "// not a comment"
    }
    assert json.loads(js_to_json('["abc", "def",]')) == ["abc", "def"]


if __name__ == "__main__":
    main()
