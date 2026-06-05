from __future__ import annotations

import collections
import collections.abc
import os
import sys
from unittest import mock


sys.path.insert(0, os.getcwd())
collections.Iterable = collections.abc.Iterable

from httpie.downloads import get_unique_filename  # noqa: E402


def main() -> None:
    cases = [
        ("foo.bar", 0, "foo.bar"),
        ("foo.bar", 1, "foo.bar-1"),
        ("foo.bar", 10, "foo.bar-10"),
        ("A" * 20, 0, "A" * 10),
        ("A" * 20, 1, "A" * 8 + "-1"),
        ("A" * 20, 10, "A" * 7 + "-10"),
        ("A" * 20 + ".txt", 0, "A" * 6 + ".txt"),
        ("A" * 20 + ".txt", 1, "A" * 4 + ".txt-1"),
        ("foo." + "A" * 20, 0, "foo." + "A" * 6),
        ("foo." + "A" * 20, 1, "foo." + "A" * 4 + "-1"),
        ("foo." + "A" * 20, 10, "foo." + "A" * 3 + "-10"),
    ]

    with mock.patch("httpie.downloads.get_filename_max_length") as patched:
        patched.return_value = 10
        for original_name, unique_on_attempt, expected in cases:
            actual = get_unique_filename(original_name, attempts(unique_on_attempt))
            assert actual == expected, (original_name, unique_on_attempt, expected, actual)

    print("oracle_passed")


def attempts(unique_on_attempt: int = 0):
    def exists(filename: str) -> bool:
        if exists.attempt == unique_on_attempt:
            return False
        exists.attempt += 1
        return True

    exists.attempt = 0
    return exists


if __name__ == "__main__":
    main()
