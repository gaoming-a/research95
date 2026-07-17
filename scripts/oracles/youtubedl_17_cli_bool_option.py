# ruff: noqa: E402
from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/oracles/youtubedl_17_cli_bool_option.py")

import sys
from pathlib import Path


def main() -> None:
    sys.path.insert(0, str(Path.cwd()))

    from youtube_dl.utils import cli_bool_option

    assert cli_bool_option({}, "--write-auto-sub", "write_auto_sub") == []
    assert cli_bool_option({"write_auto_sub": True}, "--write-auto-sub", "write_auto_sub") == [
        "--write-auto-sub",
        "true",
    ]
    assert cli_bool_option({"write_auto_sub": False}, "--write-auto-sub", "write_auto_sub") == [
        "--write-auto-sub",
        "false",
    ]
    assert cli_bool_option({"write_auto_sub": True}, "--write-auto-sub", "write_auto_sub", separator="=") == [
        "--write-auto-sub=true",
    ]
    assert cli_bool_option({"write_auto_sub": False}, "--write-auto-sub", "write_auto_sub", separator="=") == [
        "--write-auto-sub=false",
    ]


if __name__ == "__main__":
    main()
