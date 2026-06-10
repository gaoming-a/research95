from __future__ import annotations

import json
import os
import sys
import tempfile
from collections import OrderedDict
from pathlib import Path


def main() -> None:
    sys.path.insert(0, os.getcwd())

    from cookiecutter import generate

    expected_name = "éèà"
    with tempfile.TemporaryDirectory(prefix="cookiecutter_utf8_oracle_") as temp_dir:
        context_file = Path(temp_dir) / "non_ascii.json"
        context_file.write_text(
            json.dumps({"full_name": expected_name}, ensure_ascii=False),
            encoding="utf-8",
        )

        context = generate.generate_context(context_file=str(context_file))

    expected = {"non_ascii": OrderedDict([("full_name", expected_name)])}
    if context != expected:
        raise AssertionError(
            "generate_context did not preserve UTF-8 context content: "
            f"expected={expected!r}, actual={context!r}"
        )

    print("oracle_passed")


if __name__ == "__main__":
    main()
