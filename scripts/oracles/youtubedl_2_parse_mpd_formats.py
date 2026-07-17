# ruff: noqa: E402
from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/oracles/youtubedl_2_parse_mpd_formats.py")

import subprocess
import sys


def main() -> int:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "-q",
            "test.test_InfoExtractor.TestInfoExtractor.test_parse_mpd_formats",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        return result.returncode
    print("oracle_passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
