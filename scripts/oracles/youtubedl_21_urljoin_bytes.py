from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    sys.path.insert(0, str(Path.cwd()))

    from youtube_dl.utils import urljoin

    assert urljoin("http://foo.de/", "/a/b/c.txt") == "http://foo.de/a/b/c.txt"
    assert urljoin(b"http://foo.de/", "/a/b/c.txt") == "http://foo.de/a/b/c.txt"
    assert urljoin("http://foo.de/", b"/a/b/c.txt") == "http://foo.de/a/b/c.txt"
    assert urljoin(b"http://foo.de/", b"/a/b/c.txt") == "http://foo.de/a/b/c.txt"
    assert urljoin("not a url", "/a/b/c.txt") is None
    assert urljoin("http://foo.de/", b"") is None


if __name__ == "__main__":
    main()
