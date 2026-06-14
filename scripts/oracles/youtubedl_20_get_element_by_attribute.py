from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    sys.path.insert(0, str(Path.cwd()))

    from youtube_dl.utils import get_element_by_attribute

    html = '<span class="foo bar">nice</span>'
    assert get_element_by_attribute("class", "foo bar", html) == "nice"
    assert get_element_by_attribute("class", "foo", html) is None
    assert get_element_by_attribute("class", "no-such-foo", html) is None

    html_after = '<div itemprop="author" itemscope>foo</div>'
    assert get_element_by_attribute("itemprop", "author", html_after) == "foo"

    html_before = '<div itemscope itemprop="author">bar</div>'
    assert get_element_by_attribute("itemprop", "author", html_before) == "bar"


if __name__ == "__main__":
    main()
