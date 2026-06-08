# BugsInPy Expansion Screening

## Boundary

This started as an expansion screening registry, not an expanded patch-verification dataset. The five `httpie` tasks have since completed the first Stage A/B closed loop in `httpie_stage_ab_001`; the remaining selected tasks still need task-specific oracle and candidate validation before they can support experimental claims.

## Summary

- screened tasks: 22
- eligible tasks: 22
- selected tasks: 15 / target 15
- selected project counts: `{'black': 3, 'cookiecutter': 3, 'httpie': 5, 'luigi': 2, 'tqdm': 2}`

## Selected Task Registry

| task_id | project | changed Python files | prior visible test | next step |
| --- | --- | ---: | --- | --- |
| `bugsinpy_black_1` | `black` | 1 | `python -m unittest -q tests.test_black.BlackTestCase.test_works_in_mono_process_only_environment` | write_or_migrate_patch_verification_oracle_before candidate generation |
| `bugsinpy_black_2` | `black` | 1 | `not migrated` | write_or_migrate_patch_verification_oracle_before candidate generation |
| `bugsinpy_black_3` | `black` | 1 | `python -m unittest -q tests.test_black.BlackTestCase.test_invalid_config_return_code` | write_or_migrate_patch_verification_oracle_before candidate generation |
| `bugsinpy_cookiecutter_1` | `cookiecutter` | 1 | `not migrated` | write_or_migrate_patch_verification_oracle_before candidate generation |
| `bugsinpy_cookiecutter_2` | `cookiecutter` | 1 | `not migrated` | write_or_migrate_patch_verification_oracle_before candidate generation |
| `bugsinpy_cookiecutter_3` | `cookiecutter` | 1 | `not migrated` | write_or_migrate_patch_verification_oracle_before candidate generation |
| `bugsinpy_httpie_1` | `httpie` | 2 | `pytest tests/test_downloads.py::TestDownloadUtils::test_unique_filename` | stage_ab_001_validated |
| `bugsinpy_httpie_2` | `httpie` | 2 | `pytest tests/test_redirects.py::TestRedirects::test_max_redirects` | stage_ab_001_validated |
| `bugsinpy_httpie_3` | `httpie` | 1 | `pytest tests/test_sessions.py::TestSession::test_download_in_session` | stage_ab_001_validated |
| `bugsinpy_httpie_4` | `httpie` | 1 | `pytest tests/test_regressions.py::test_Host_header_overwrite` | stage_ab_001_validated |
| `bugsinpy_httpie_5` | `httpie` | 1 | `pytest tests/tests.py::TestItemParsing::test_escape_longsep` | stage_ab_001_validated |
| `bugsinpy_luigi_3` | `luigi` | 1 | `pytest test/parameter_test.py::TestSerializeTupleParameter::testSerialize` | write_or_migrate_patch_verification_oracle_before candidate generation |
| `bugsinpy_luigi_4` | `luigi` | 1 | `pytest test/contrib/redshift_test.py::TestS3CopyToTable::test_s3_copy_with_nonetype_columns` | write_or_migrate_patch_verification_oracle_before candidate generation |
| `bugsinpy_tqdm_1` | `tqdm` | 2 | `python3 -m pytest tqdm/tests/tests_contrib.py::test_enumerate` | write_or_migrate_patch_verification_oracle_before candidate generation |
| `bugsinpy_tqdm_2` | `tqdm` | 2 | `python3 -m pytest tqdm/tests/tests_tqdm.py::test_format_meter` | write_or_migrate_patch_verification_oracle_before candidate generation |

## Acceptance Rule For Real Expansion

A screened task becomes part of the expanded experiment only after:

1. a patch-verification oracle exists in `scripts/oracles/` or an equivalent validated command is wrapped;
2. buggy and fixed/reference behavior are both checked;
3. reference, no-op, irrelevant, and at least one difficult negative candidate are materialized;
4. `validate_patch_candidates.py` reports validated records for all candidates;
5. visible evidence and hidden evaluator fields pass leakage checks.
