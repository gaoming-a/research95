# BugsInPy Candidate Pool Screening

## Decision Boundary

This screening follows the decision to stop prioritizing legacy `nose` and
Black `typed_ast` / MSVC repair work. It introduces a broader BugsInPy
candidate pool and applies metadata-level filters before any checkout or
project-level P2P construction.

## Summary

- total BugsInPy tasks: 501
- already registered tasks: 47
- new candidate tasks: 454
- promising metadata-level candidates: 202
- framework counts: `{'other': 1, 'pytest': 351, 'unittest': 102}`
- metadata blocker counts: `{'external_service_dependency': 5, 'heavy_ml_dependency': 45, 'native_build_dependency': 179}`

## Top Candidates

| task_id | project | framework | test file | score | run command |
| --- | --- | --- | --- | ---: | --- |
| `bugsinpy_fastapi_4` | `fastapi` | `pytest` | `tests/test_param_in_path_and_dependency.py` | 8 | `pytest tests/test_param_in_path_and_dependency.py::test_reused_param` |
| `bugsinpy_fastapi_5` | `fastapi` | `pytest` | `tests/test_filter_pydantic_sub_model.py` | 8 | `pytest tests/test_filter_pydantic_sub_model.py::test_filter_sub_model` |
| `bugsinpy_fastapi_7` | `fastapi` | `pytest` | `tests/test_multi_body_errors.py` | 8 | `pytest tests/test_multi_body_errors.py::test_jsonable_encoder_requiring_error` |
| `bugsinpy_fastapi_8` | `fastapi` | `pytest` | `tests/test_custom_route_class.py` | 8 | `pytest tests/test_custom_route_class.py::test_route_classes` |
| `bugsinpy_fastapi_9` | `fastapi` | `pytest` | `tests/test_request_body_parameters_media_type.py` | 8 | `pytest tests/test_request_body_parameters_media_type.py::test_openapi_schema` |
| `bugsinpy_fastapi_10` | `fastapi` | `pytest` | `tests/test_skip_defaults.py` | 8 | `pytest tests/test_skip_defaults.py::test_return_defaults` |
| `bugsinpy_fastapi_12` | `fastapi` | `pytest` | `tests/test_security_http_bearer_optional.py` | 8 | `pytest tests/test_security_http_bearer_optional.py::test_security_http_bearer_incorrect_scheme_credentials` |
| `bugsinpy_fastapi_13` | `fastapi` | `pytest` | `tests/test_additional_responses_router.py` | 8 | `pytest tests/test_additional_responses_router.py::test_openapi_schema` |
| `bugsinpy_fastapi_14` | `fastapi` | `pytest` | `tests/test_additional_properties.py` | 8 | `pytest tests/test_additional_properties.py::test_additional_properties_schema` |
| `bugsinpy_fastapi_15` | `fastapi` | `pytest` | `tests/test_ws_router.py` | 8 | `pytest tests/test_ws_router.py::test_router; pytest tests/test_ws_router.py::test_prefix_router` |
| `bugsinpy_fastapi_16` | `fastapi` | `pytest` | `tests/test_datetime_custom_encoder.py;tests/test_jsonable_encoder.py` | 8 | `pytest tests/test_jsonable_encoder.py::test_encode_model_with_config` |
| `bugsinpy_sanic_2` | `sanic` | `pytest` | `tests/test_app.py` | 8 | `pytest tests/test_app.py::test_asyncio_server_start_serving` |
| `bugsinpy_sanic_3` | `sanic` | `pytest` | `tests/test_url_for.py` | 8 | `pytest tests/test_url_for.py::test_routes_with_host` |
| `bugsinpy_sanic_4` | `sanic` | `pytest` | `tests/test_requests.py` | 8 | `pytest tests/test_requests.py::test_url_for_without_server_name` |
| `bugsinpy_sanic_5` | `sanic` | `pytest` | `tests/test_logging.py` | 8 | `pytest tests/test_logging.py::test_logging_modified_root_logger_config` |
| `bugsinpy_thefuck_1` | `thefuck` | `pytest` | `tests/rules/test_pip_unknown_command.py` | 8 | `pytest tests/rules/test_pip_unknown_command.py::test_get_new_command` |
| `bugsinpy_thefuck_2` | `thefuck` | `pytest` | `tests/test_utils.py` | 8 | `pytest tests/test_utils.py::test_get_all_executables_pathsep` |
| `bugsinpy_thefuck_3` | `thefuck` | `pytest` | `tests/shells/test_fish.py` | 8 | `pytest tests/shells/test_fish.py::TestFish::test_info` |
| `bugsinpy_thefuck_4` | `thefuck` | `pytest` | `tests/shells/test_fish.py` | 8 | `pytest tests/shells/test_fish.py::TestFish::test_get_aliases` |
| `bugsinpy_thefuck_5` | `thefuck` | `pytest` | `tests/rules/test_git_push.py` | 8 | `pytest tests/rules/test_git_push.py::test_match_bitbucket` |
| `bugsinpy_thefuck_6` | `thefuck` | `pytest` | `tests/rules/test_git_branch_exists.py` | 8 | `pytest tests/rules/test_git_branch_exists.py::test_get_new_command` |
| `bugsinpy_thefuck_7` | `thefuck` | `pytest` | `tests/rules/test_php_s.py` | 8 | `pytest tests/rules/test_php_s.py::test_match` |
| `bugsinpy_thefuck_8` | `thefuck` | `pytest` | `tests/rules/test_dnf_no_such_command.py` | 8 | `pytest tests/rules/test_dnf_no_such_command.py::test_get_new_command; pytest tests/rules/test_dnf_no_such_command.py::test_get_operations` |
| `bugsinpy_thefuck_9` | `thefuck` | `pytest` | `tests/rules/test_git_push.py` | 8 | `pytest tests/rules/test_git_push.py::test_get_new_command` |
| `bugsinpy_thefuck_10` | `thefuck` | `pytest` | `tests/rules/test_man.py` | 8 | `pytest tests/rules/test_man.py::test_get_new_command` |
| `bugsinpy_thefuck_11` | `thefuck` | `pytest` | `tests/rules/test_git_push.py` | 8 | `pytest tests/rules/test_git_push.py::test_get_new_command` |
| `bugsinpy_thefuck_12` | `thefuck` | `pytest` | `tests/rules/test_no_command.py` | 8 | `pytest tests/rules/test_no_command.py::test_not_match; pytest tests/rules/test_no_command.py::test_match` |
| `bugsinpy_thefuck_13` | `thefuck` | `pytest` | `tests/rules/test_git_branch_exists.py` | 8 | `pytest tests/rules/test_git_branch_exists.py::test_match; pytest tests/rules/test_git_branch_exists.py::test_get_new_command` |
| `bugsinpy_thefuck_14` | `thefuck` | `pytest` | `tests/shells/test_fish.py` | 8 | `pytest tests/shells/test_fish.py::TestFish::test_get_overridden_aliases` |
| `bugsinpy_thefuck_15` | `thefuck` | `pytest` | `tests/rules/test_git_add.py` | 8 | `pytest tests/rules/test_git_add.py::test_match` |
| `bugsinpy_thefuck_16` | `thefuck` | `pytest` | `tests/shells/test_bash.py;tests/shells/test_zsh.py` | 8 | `pytest tests/shells/test_bash.py::TestBash::test_app_alias_variables_correctly_set; pytest tests/shells/test_zsh.py::TestZsh::test_app_alias` |
| `bugsinpy_thefuck_17` | `thefuck` | `pytest` | `tests/shells/test_bash.py` | 8 | `pytest tests/shells/test_bash.py::TestBash::test_get_aliases; pytest tests/shells/test_bash.py::TestBash::test_from_shell` |
| `bugsinpy_thefuck_18` | `thefuck` | `pytest` | `tests/rules/test_sudo.py` | 8 | `pytest tests/rules/test_sudo.py::test_not_match` |
| `bugsinpy_thefuck_19` | `thefuck` | `pytest` | `tests/rules/test_git_push_force.py` | 8 | `pytest tests/rules/test_git_push_force.py::test_get_new_command` |
| `bugsinpy_thefuck_20` | `thefuck` | `pytest` | `tests/rules/test_dirty_unzip.py` | 8 | `pytest tests/rules/test_dirty_unzip.py::test_get_new_command` |
| `bugsinpy_thefuck_21` | `thefuck` | `pytest` | `tests/rules/test_git_fix_stash.py` | 8 | `pytest tests/rules/test_git_fix_stash.py::test_not_match` |
| `bugsinpy_thefuck_22` | `thefuck` | `pytest` | `tests/test_types.py` | 8 | `pytest tests/test_types.py::TestSortedCorrectedCommandsSequence::test_with_blank` |
| `bugsinpy_thefuck_24` | `thefuck` | `pytest` | `tests/test_types.py` | 8 | `pytest tests/test_types.py::TestCorrectedCommand::test_equality; pytest tests/test_types.py::TestCorrectedCommand::test_hashable` |
| `bugsinpy_thefuck_25` | `thefuck` | `pytest` | `tests/rules/test_mkdir_p.py` | 8 | `pytest tests/rules/test_mkdir_p.py::test_get_new_command` |
| `bugsinpy_thefuck_26` | `thefuck` | `pytest` | `tests/rules/test_vagrant_up.py` | 8 | `pytest tests/rules/test_vagrant_up.py::test_get_new_command` |
| `bugsinpy_thefuck_27` | `thefuck` | `pytest` | `tests/rules/test_open.py` | 8 | `pytest tests/rules/test_open.py::test_get_new_command` |
| `bugsinpy_thefuck_28` | `thefuck` | `pytest` | `tests/rules/test_fix_file.py` | 8 | `pytest tests/rules/test_fix_file.py::test_get_new_command_with_settings` |
| `bugsinpy_thefuck_29` | `thefuck` | `pytest` | `tests/test_types.py;tests/test_utils.py` | 8 | `pytest tests/test_types.py::test_update_settings; pytest tests/test_utils.py::test_wrap_settings` |
| `bugsinpy_thefuck_30` | `thefuck` | `pytest` | `tests/rules/test_fix_file.py` | 8 | `pytest tests/rules/test_fix_file.py::test_not_file` |
| `bugsinpy_thefuck_31` | `thefuck` | `pytest` | `tests/rules/test_git_diff_staged.py` | 8 | `pytest tests/rules/test_git_diff_staged.py::test_get_new_command` |
| `bugsinpy_thefuck_32` | `thefuck` | `pytest` | `tests/rules/test_ls_lah.py` | 8 | `pytest tests/rules/test_ls_lah.py::test_match` |
| `bugsinpy_fastapi_3` | `fastapi` | `pytest` | `tests/test_serialize_response_model.py` | 7 | `pytest tests/test_serialize_response_model.py::test_valid; pytest tests/test_serialize_response_model.py::test_coerce; pytest tests/test_ser` |
| `bugsinpy_fastapi_6` | `fastapi` | `pytest` | `tests/test_forms_from_non_typing_sequences.py` | 7 | `pytest tests/test_forms_from_non_typing_sequences.py::test_python_list_param_as_form; pytest tests/test_forms_from_non_typing_sequences.py::` |
| `bugsinpy_fastapi_11` | `fastapi` | `pytest` | `tests/test_union_body.py;tests/test_union_inherited_body.py` | 7 | `pytest tests/test_union_body.py::test_item_openapi_schema; pytest tests/test_union_body.py::test_post_other_item; pytest tests/test_union_bo` |
| `bugsinpy_scrapy_2` | `scrapy` | `unittest` | `tests/test_utils_datatypes.py` | 7 | `python -m unittest -q tests.test_utils_datatypes.LocalCacheTest.test_cache_without_limit` |

## Admission Rule

A task from this pool can enter `p2p_broad_main` only after checkout,
F2P validation, project-level P2P-broad construction with at least three
stable P2P tests, candidate generation, and F2P + P2P-broad candidate
revalidation. This metadata screen is not experimental evidence.
