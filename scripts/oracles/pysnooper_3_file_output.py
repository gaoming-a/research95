from __future__ import annotations

import sys
import tempfile
from pathlib import Path


def main() -> None:
    sys.path.insert(0, str(Path.cwd()))

    import pysnooper

    with tempfile.TemporaryDirectory(prefix="pysnooper3_") as temp_dir:
        log_path = Path(temp_dir) / "trace.log"

        @pysnooper.snoop(str(log_path))
        def traced(value: str) -> int:
            number = 7
            return len(value) + number

        result = traced("baba")
        if result != 11:
            raise AssertionError(f"unexpected traced result: {result}")
        if not log_path.exists():
            raise AssertionError("snoop file output was not created")
        output = log_path.read_text(encoding="utf-8")
        if "Starting var:.. value" not in output or "number = 7" not in output:
            raise AssertionError(f"snoop output missing expected trace content: {output!r}")

    print("oracle_passed")


if __name__ == "__main__":
    main()
