from __future__ import annotations

import os
from pathlib import Path


def load_env_file(path: str | Path = ".env", override: bool = False) -> dict[str, str]:
    env_path = Path(path)
    loaded: dict[str, str] = {}
    if not env_path.exists():
        return loaded
    with env_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" not in stripped:
                raise ValueError(f"Invalid env line at {env_path}:{line_number}")
            key, value = stripped.split("=", 1)
            key = key.strip()
            value = strip_env_value(value.strip())
            if not key:
                raise ValueError(f"Empty env key at {env_path}:{line_number}")
            if override or key not in os.environ:
                os.environ[key] = value
            loaded[key] = value
    return loaded


def strip_env_value(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def is_placeholder_secret(value: str | None) -> bool:
    if not value:
        return True
    stripped = value.strip()
    return stripped.startswith("<") or stripped.endswith(">") or "your-" in stripped.lower()
