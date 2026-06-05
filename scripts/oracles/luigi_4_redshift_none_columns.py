from __future__ import annotations

import collections
import collections.abc
import inspect
import os
import sys
from collections import namedtuple
from unittest import mock


def patch_python311_compatibility() -> None:
    for name in dir(collections.abc):
        if not hasattr(collections, name):
            setattr(collections, name, getattr(collections.abc, name))

    if not hasattr(inspect, "ArgSpec"):
        inspect.ArgSpec = namedtuple("ArgSpec", "args varargs keywords defaults")

    if not hasattr(inspect, "getargspec"):

        def getargspec(func):
            spec = inspect.getfullargspec(func)
            return inspect.ArgSpec(spec.args, spec.varargs, spec.varkw, spec.defaults)

        inspect.getargspec = getargspec


def main() -> None:
    patch_python311_compatibility()
    sys.path.insert(0, os.getcwd())

    import luigi  # noqa: E402
    import luigi.contrib.redshift  # noqa: E402

    class DummyCopyToTable(luigi.contrib.redshift.S3CopyToTable):
        host = "dummy_host"
        database = "dummy_database"
        user = "dummy_user"
        password = "dummy_password"
        table = luigi.Parameter(default="dummy_table")
        columns = luigi.TupleParameter(default=(("some_text", "varchar(255)"),))
        copy_options = ""
        prune_table = ""
        prune_column = ""
        prune_date = ""
        aws_access_key_id = "key"
        aws_secret_access_key = "secret"

        def s3_load_path(self):
            return "s3://bucket/key"

    task = DummyCopyToTable(columns=None)
    cursor = mock.Mock()
    task.copy(cursor, task.s3_load_path())

    statement = cursor.execute.call_args[0][0]
    assert "COPY dummy_table  from 's3://bucket/key'" in statement, statement
    print("oracle_passed")


if __name__ == "__main__":
    main()
