from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    sys.path.insert(0, str(Path.cwd()))

    from youtube_dl.utils import url_basename

    assert url_basename("http://foo.de/") == ""
    assert url_basename("http://foo.de/bar/baz") == "baz"
    assert url_basename("http://foo.de/bar/baz?x=y") == "baz"
    assert url_basename("http://foo.de/bar/baz#x=y") == "baz"
    assert url_basename("http://foo.de/bar/baz/") == "baz"
    assert url_basename("http://media.w3.org/2010/05/sintel/trailer.mp4") == "trailer.mp4"


if __name__ == "__main__":
    main()
