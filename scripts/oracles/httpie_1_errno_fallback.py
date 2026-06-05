from __future__ import annotations

import errno
import collections
import collections.abc
import os
import sys
from unittest import mock


sys.path.insert(0, os.getcwd())
collections.Iterable = collections.abc.Iterable

from httpie import downloads  # noqa: E402


def main() -> None:
    error = OSError()
    error.errno = errno.EINVAL
    with mock.patch("httpie.downloads.os.pathconf", side_effect=error, create=True):
        assert downloads.get_filename_max_length(".") == 255

    print("oracle_passed")


if __name__ == "__main__":
    main()
