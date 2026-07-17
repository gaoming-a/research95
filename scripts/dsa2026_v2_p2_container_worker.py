# ruff: noqa: E402
#!/usr/bin/env python3
"""V2-P2 entry point for the frozen generic isolated-check worker."""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/dsa2026_v2_p2_container_worker.py")

import json
import sys

from dsa2026_p4_container_worker import main


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"worker_error": type(error).__name__, "message": str(error)}, sort_keys=True))
        sys.exit(1)
