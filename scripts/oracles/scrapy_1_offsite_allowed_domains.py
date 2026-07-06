from __future__ import annotations

import os
import sys
import types
import warnings
from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location


def main() -> None:
    scrapy = types.ModuleType("scrapy")
    scrapy.signals = types.SimpleNamespace(spider_opened=object())
    scrapy_http = types.ModuleType("scrapy.http")
    scrapy_http.Request = type("Request", (), {})
    scrapy_utils_httpobj = types.ModuleType("scrapy.utils.httpobj")
    scrapy_utils_httpobj.urlparse_cached = lambda request: types.SimpleNamespace(hostname="")
    sys.modules.setdefault("scrapy", scrapy)
    sys.modules.setdefault("scrapy.http", scrapy_http)
    sys.modules.setdefault("scrapy.utils.httpobj", scrapy_utils_httpobj)

    module_path = Path(os.getcwd()) / "scrapy" / "spidermiddlewares" / "offsite.py"
    spec = spec_from_file_location("target_offsite", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {module_path}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    OffsiteMiddleware = module.OffsiteMiddleware
    URLWarning = module.URLWarning

    class Spider:
        allowed_domains = ["scrapytest.org", None, "http://example.com", "scrapy.org"]

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        regex = OffsiteMiddleware(stats=None).get_host_regex(Spider())

    assert any(issubclass(item.category, URLWarning) for item in caught), "URL entry should emit URLWarning"
    assert regex.search("scrapytest.org"), regex.pattern
    assert regex.search("sub.scrapy.org"), regex.pattern
    assert not regex.search("example.com"), regex.pattern
    assert "http://" not in regex.pattern, regex.pattern
    print("oracle_passed")


if __name__ == "__main__":
    main()
