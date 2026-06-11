from __future__ import annotations

import os
import stat
import sys
import tempfile
from pathlib import Path


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    sys.path.insert(0, os.getcwd())

    from cookiecutter import hooks, utils

    with tempfile.TemporaryDirectory(prefix="cookiecutter_hooks_oracle_") as temp_dir:
        repo = Path(temp_dir) / "repo"
        hooks_dir = repo / "hooks"
        target_dir = repo / "input{{hooks}}"
        hooks_dir.mkdir(parents=True)
        target_dir.mkdir()

        write_text(
            hooks_dir / "pre_gen_project.py",
            "\n".join(
                [
                    "#!/usr/bin/env python",
                    "from pathlib import Path",
                    "Path('python_pre.txt').write_text('ran', encoding='utf-8')",
                    "",
                ]
            ),
        )

        if sys.platform.startswith("win"):
            write_text(
                hooks_dir / "pre_gen_project.bat",
                "\n".join(
                    [
                        "@echo off",
                        "echo ran>shell_pre.txt",
                        "",
                    ]
                ),
            )
        else:
            shell_hook = hooks_dir / "pre_gen_project.sh"
            write_text(
                shell_hook,
                "\n".join(
                    [
                        "#!/bin/sh",
                        "printf ran > shell_pre.txt",
                        "",
                    ]
                ),
            )
            shell_hook.chmod(shell_hook.stat().st_mode | stat.S_IXUSR)

        with utils.work_in(str(repo)):
            hooks.run_hook("pre_gen_project", str(target_dir), {})

        missing = [
            name
            for name in ("python_pre.txt", "shell_pre.txt")
            if not (target_dir / name).is_file()
        ]
        if missing:
            raise AssertionError(f"run_hook did not execute all matching pre hooks: missing={missing}")

    print("oracle_passed")


if __name__ == "__main__":
    main()
