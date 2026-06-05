from __future__ import annotations

import os
import sys
from types import SimpleNamespace


sys.path.insert(0, os.getcwd())

from httpie import client  # noqa: E402


class StubSession:
    def request(self, **kwargs):
        assert getattr(self, "max_redirects", None) == 1, self.__dict__
        return {"request_kwargs": kwargs}


def main() -> None:
    session = StubSession()
    original_get_requests_session = client.get_requests_session
    client.get_requests_session = lambda: session
    try:
        response = client.get_response(
            args=SimpleNamespace(
                auth=None,
                auth_type=None,
                cert=None,
                cert_key=None,
                data={},
                debug=False,
                files={},
                follow=True,
                form=False,
                headers={},
                json=False,
                max_redirects=1,
                method="GET",
                params={},
                proxy=[],
                session=None,
                session_read_only=None,
                timeout=30,
                url="http://example.com/redirect/3",
                verify="yes",
            ),
            config_dir=".",
        )
    finally:
        client.get_requests_session = original_get_requests_session

    assert response["request_kwargs"]["allow_redirects"] is True, response
    print("oracle_passed")


if __name__ == "__main__":
    main()
