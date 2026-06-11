from __future__ import annotations

import os
import sys
from unittest import mock


def main() -> None:
    sys.path.insert(0, os.getcwd())

    import click
    from cookiecutter.prompt import read_user_choice

    options = ["hello", "world", "foo", "bar"]

    with mock.patch("click.Choice", wraps=click.Choice) as choice, mock.patch("click.prompt") as prompt:
        prompt.return_value = "2"
        result = read_user_choice("varname", options)

    if result != "world":
        raise AssertionError(f"read_user_choice returned {result!r}, expected 'world'")

    _, kwargs = prompt.call_args
    if kwargs.get("show_choices") is not False:
        raise AssertionError(
            "click.prompt must be called with show_choices=False to avoid "
            f"duplicating rendered choices; kwargs={kwargs!r}"
        )
    if kwargs.get("default") != "1":
        raise AssertionError(f"unexpected default choice: {kwargs.get('default')!r}")
    if not choice.called:
        raise AssertionError("click.Choice was not used to validate numbered options")

    print("oracle_passed")


if __name__ == "__main__":
    main()
