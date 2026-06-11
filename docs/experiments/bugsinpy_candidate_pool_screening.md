# BugsInPy Candidate Pool Screening

## Decision Boundary

This screening follows the decision to stop prioritizing legacy `nose` and
Black `typed_ast` / MSVC repair work. It introduces a broader BugsInPy
candidate pool and applies metadata-level filters before any checkout or
project-level P2P construction.

## Summary

- total BugsInPy tasks: 501
- already registered tasks: 22
- new candidate tasks: 479
- promising metadata-level candidates: 195
- framework counts: `{'other': 1, 'pytest': 359, 'unittest': 119}`
- metadata blocker counts: `{'external_service_dependency': 5, 'heavy_ml_dependency': 45, 'native_build_dependency': 179, 'network_reference_in_metadata': 102}`

## Top Candidates

| task_id | project | framework | test file | score | run command |
| --- | --- | --- | --- | ---: | --- |
| `bugsinpy_PySnooper_1` | `PySnooper` | `pytest` | `tests/test_chinese.py` | 8 | `pytest -q -s tests/test_chinese.py::test_chinese` |
| `bugsinpy_PySnooper_2` | `PySnooper` | `pytest` | `tests/test_pysnooper.py` | 8 | `pytest -q -s tests/test_pysnooper.py::test_custom_repr_single` |
| `bugsinpy_PySnooper_3` | `PySnooper` | `pytest` | `tests/test_pysnooper.py` | 8 | `pytest -q -s tests/test_pysnooper.py::test_file_output` |
| `bugsinpy_fastapi_1` | `fastapi` | `pytest` | `tests/test_jsonable_encoder.py` | 8 | `pytest tests/test_jsonable_encoder.py::test_encode_model_with_default` |
| `bugsinpy_fastapi_2` | `fastapi` | `pytest` | `tests/test_ws_router.py` | 8 | `pytest tests/test_ws_router.py::test_router_ws_depends_with_override` |
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
| `bugsinpy_sanic_1` | `sanic` | `pytest` | `tests/test_blueprints.py` | 8 | `pytest tests/test_blueprints.py::test_bp_middleware_order` |
| `bugsinpy_sanic_2` | `sanic` | `pytest` | `tests/test_app.py` | 8 | `pytest tests/test_app.py::test_asyncio_server_start_serving` |
| `bugsinpy_sanic_3` | `sanic` | `pytest` | `tests/test_url_for.py` | 8 | `pytest tests/test_url_for.py::test_routes_with_host` |
| `bugsinpy_sanic_4` | `sanic` | `pytest` | `tests/test_requests.py` | 8 | `pytest tests/test_requests.py::test_url_for_without_server_name` |
| `bugsinpy_sanic_5` | `sanic` | `pytest` | `tests/test_logging.py` | 8 | `pytest tests/test_logging.py::test_logging_modified_root_logger_config` |
| `bugsinpy_fastapi_3` | `fastapi` | `pytest` | `tests/test_serialize_response_model.py` | 7 | `pytest tests/test_serialize_response_model.py::test_valid; pytest tests/test_serialize_response_model.py::test_coerce; pytest tests/test_ser` |
| `bugsinpy_fastapi_6` | `fastapi` | `pytest` | `tests/test_forms_from_non_typing_sequences.py` | 7 | `pytest tests/test_forms_from_non_typing_sequences.py::test_python_list_param_as_form; pytest tests/test_forms_from_non_typing_sequences.py::` |
| `bugsinpy_fastapi_11` | `fastapi` | `pytest` | `tests/test_union_body.py;tests/test_union_inherited_body.py` | 7 | `pytest tests/test_union_body.py::test_item_openapi_schema; pytest tests/test_union_body.py::test_post_other_item; pytest tests/test_union_bo` |
| `bugsinpy_scrapy_1` | `scrapy` | `unittest` | `tests/test_spidermiddleware_offsite.py` | 7 | `python -m unittest -q tests.test_spidermiddleware_offsite.TestOffsiteMiddleware4._get_spiderargs; python -m unittest -q tests.test_spidermid` |
| `bugsinpy_scrapy_2` | `scrapy` | `unittest` | `tests/test_utils_datatypes.py` | 7 | `python -m unittest -q tests.test_utils_datatypes.LocalCacheTest.test_cache_without_limit` |
| `bugsinpy_scrapy_3` | `scrapy` | `unittest` | `tests/test_downloadermiddleware_redirect.py` | 7 | `python -m unittest -q tests.test_downloadermiddleware_redirect.RedirectMiddlewareTest.test_redirect_302_relative` |
| `bugsinpy_scrapy_4` | `scrapy` | `unittest` | `tests/test_contracts.py` | 7 | `python -m unittest -q tests.test_contracts.ContractsManagerTest.test_errback` |
| `bugsinpy_scrapy_5` | `scrapy` | `unittest` | `tests/test_http_response.py` | 7 | `python -m unittest -q tests.test_http_response.BaseResponseTest.test_follow_None_url` |
| `bugsinpy_scrapy_6` | `scrapy` | `unittest` | `tests/test_pipeline_images.py` | 7 | `python -m unittest -q tests.test_pipeline_images.ImagesPipelineTestCase.test_convert_image` |
| `bugsinpy_scrapy_7` | `scrapy` | `unittest` | `tests/test_http_request.py` | 7 | `python -m unittest -q tests.test_http_request.FormRequestTest.test_spaces_in_action` |
| `bugsinpy_scrapy_8` | `scrapy` | `unittest` | `tests/test_item.py` | 7 | `python -m unittest -q tests.test_item.ItemMetaTest.test_new_method_propagates_classcell; python -m unittest -q tests.test_item.ItemMetaClass` |
| `bugsinpy_scrapy_9` | `scrapy` | `unittest` | `tests/test_mail.py` | 7 | `python -m unittest -q tests.test_mail.MailSenderTest.test_send_single_values_to_and_cc` |
| `bugsinpy_scrapy_10` | `scrapy` | `unittest` | `tests/test_downloadermiddleware_redirect.py` | 7 | `python -m unittest -q tests.test_downloadermiddleware_redirect.RedirectMiddlewareTest.test_latin1_location; python -m unittest -q tests.test` |
| `bugsinpy_scrapy_11` | `scrapy` | `unittest` | `tests/test_utils_gz.py` | 7 | `python -m unittest -q tests.test_utils_gz.GunzipTest.test_gunzip_illegal_eof` |
| `bugsinpy_scrapy_12` | `scrapy` | `unittest` | `tests/test_selector.py` | 7 | `python -m unittest -q tests.test_selector.SelectorTestCase.test_selector_bad_args` |
| `bugsinpy_scrapy_13` | `scrapy` | `unittest` | `tests/test_pipeline_images.py` | 7 | `python -m unittest -q tests.test_pipeline_images.ImagesPipelineTestCaseCustomSettings` |
| `bugsinpy_scrapy_14` | `scrapy` | `unittest` | `tests/test_utils_gz.py` | 7 | `python -m unittest -q tests.test_utils_gz.GunzipTest.test_is_gzipped_case_insensitive; python -m unittest -q tests.test_utils_gz.GunzipTest.` |
| `bugsinpy_scrapy_15` | `scrapy` | `unittest` | `tests/test_utils_url.py` | 7 | `python -m unittest -q tests.test_utils_url.CanonicalizeUrlTest.test_canonicalize_url_idna_exceptions` |
| `bugsinpy_scrapy_17` | `scrapy` | `unittest` | `tests/test_utils_response.py` | 7 | `python -m unittest -q tests.test_utils_response.ResponseUtilsTest.test_response_status_message` |

## Admission Rule

A task from this pool can enter `p2p_broad_main` only after checkout,
F2P validation, project-level P2P-broad construction with at least three
stable P2P tests, candidate generation, and F2P + P2P-broad candidate
revalidation. This metadata screen is not experimental evidence.
