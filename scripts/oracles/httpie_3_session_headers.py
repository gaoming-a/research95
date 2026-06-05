from __future__ import annotations

import collections
import collections.abc
import os
import sys
import tempfile


sys.path.insert(0, os.getcwd())
collections.Iterable = collections.abc.Iterable

from httpie.sessions import Session  # noqa: E402


def main() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        session = Session(os.path.join(tmpdir, "session.json"))
        session.update_headers(
            {
                "X-Regular": b"kept",
                "X-Unset": None,
                "Content-Type": b"text/plain",
                "User-Agent": b"HTTPie/0.0.0",
            }
        )

        assert session.headers == {"X-Regular": "kept"}, session.headers

    print("oracle_passed")


if __name__ == "__main__":
    main()
