from __future__ import annotations

import os
import sys

from requests.structures import CaseInsensitiveDict
import requests.compat


sys.path.insert(0, os.getcwd())
requests.compat.is_windows = sys.platform.startswith("win")
requests.compat.is_py3 = True
requests.compat.is_py26 = False

from httpie.models import HTTPRequest  # noqa: E402


class PreparedRequestStub:
    method = "GET"
    url = "http://127.0.0.1/get"
    body = None

    def __init__(self) -> None:
        self.headers = CaseInsensitiveDict({"host": "httpbin.org"})


def main() -> None:
    rendered = HTTPRequest(PreparedRequestStub()).headers
    host_lines = [line for line in rendered.splitlines() if line.lower().startswith("host:")]

    assert host_lines == ["host: httpbin.org"], rendered

    print("oracle_passed")


if __name__ == "__main__":
    main()
