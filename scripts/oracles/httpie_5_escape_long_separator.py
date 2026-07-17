# ruff: noqa: E402
from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/oracles/httpie_5_escape_long_separator.py")

import os
import sys


sys.path.insert(0, os.getcwd())

from httpie import cli  # noqa: E402


def main() -> None:
    key_value = cli.KeyValueType(
        cli.SEP_HEADERS,
        cli.SEP_DATA,
        cli.SEP_DATA_RAW_JSON,
        cli.SEP_FILES,
    )
    headers, data, files = cli.parse_items([key_value(r"bob\:==foo")])

    assert headers == {}, headers
    assert files == {}, files
    assert data == {"bob:=": "foo"}, data

    print("oracle_passed")


if __name__ == "__main__":
    main()
