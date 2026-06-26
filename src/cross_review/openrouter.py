from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from typing import Any

from cross_review.env import is_placeholder_secret


RETRYABLE_HTTP_STATUS = {429, 500, 502, 503, 504}
DEFAULT_TIMEOUT_SECONDS = 120.0
DEFAULT_MAX_RETRIES = 2
DEFAULT_RETRY_BACKOFF_SECONDS = 2.0
MAX_ERROR_DETAIL_CHARS = 1200


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw in (None, ""):
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be a number") from exc


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw in (None, ""):
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc
    return max(0, value)


def redact_sensitive_text(text: str, api_key: str | None = None) -> str:
    redacted = text
    if api_key:
        redacted = redacted.replace(api_key, "<redacted-openrouter-key>")
    key_prefix = "".join(["sk-", "or-v1-"])
    redacted = re.sub(re.escape(key_prefix) + r"[A-Za-z0-9_-]+", "<redacted-openrouter-key>", redacted)
    redacted = re.sub(r'("user_id"\s*:\s*")[^"]+(")', r"\1<redacted-openrouter-user>\2", redacted)
    redacted = re.sub(r"\buser_[A-Za-z0-9]+\b", "<redacted-openrouter-user>", redacted)
    return redacted


def safe_error_detail(text: str, api_key: str | None = None) -> str:
    cleaned = redact_sensitive_text(text, api_key=api_key).replace("\r", "\\r").replace("\n", "\\n")
    if len(cleaned) > MAX_ERROR_DETAIL_CHARS:
        return cleaned[:MAX_ERROR_DETAIL_CHARS] + "...<truncated>"
    return cleaned


def response_error_code(error: dict[str, Any]) -> int | None:
    code = error.get("code")
    if isinstance(code, int):
        return code
    if isinstance(code, str):
        try:
            return int(code)
        except ValueError:
            return None
    return None


class OpenAICompatibleChatClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://openrouter.ai/api/v1",
        api_key_env: str = "OPENROUTER_API_KEY",
        base_url_env: str = "OPENROUTER_BASE_URL",
        provider_name: str = "OpenRouter",
        timeout_seconds: float | None = None,
        max_retries: int | None = None,
        retry_backoff_seconds: float | None = None,
    ) -> None:
        self.api_key_env = api_key_env
        self.provider_name = provider_name
        self.api_key = api_key or os.environ.get(api_key_env)
        if is_placeholder_secret(self.api_key):
            raise RuntimeError(f"{api_key_env} is not set. Set it in the shell or an untracked .env file.")
        self.base_url = os.environ.get(base_url_env, base_url).rstrip("/")
        self.timeout_seconds = (
            timeout_seconds
            if timeout_seconds is not None
            else _env_float("OPENROUTER_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS)
        )
        self.max_retries = (
            max_retries
            if max_retries is not None
            else _env_int("OPENROUTER_MAX_RETRIES", DEFAULT_MAX_RETRIES)
        )
        self.retry_backoff_seconds = (
            retry_backoff_seconds
            if retry_backoff_seconds is not None
            else _env_float("OPENROUTER_RETRY_BACKOFF_SECONDS", DEFAULT_RETRY_BACKOFF_SECONDS)
        )

    def chat_completion(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.2,
        top_p: float = 1.0,
        max_tokens: int = 4096,
        provider: dict[str, Any] | None = None,
        reasoning: dict[str, Any] | None = None,
        include_reasoning: bool | None = None,
        thinking: dict[str, Any] | None = None,
        response_format: dict[str, Any] | None = None,
        metadata_enabled: bool = False,
    ) -> dict[str, Any]:
        return self.chat_completion_messages(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            provider=provider,
            reasoning=reasoning,
            include_reasoning=include_reasoning,
            thinking=thinking,
            response_format=response_format,
            metadata_enabled=metadata_enabled,
        )

    def chat_completion_messages(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        top_p: float = 1.0,
        max_tokens: int = 4096,
        provider: dict[str, Any] | None = None,
        reasoning: dict[str, Any] | None = None,
        include_reasoning: bool | None = None,
        thinking: dict[str, Any] | None = None,
        response_format: dict[str, Any] | None = None,
        metadata_enabled: bool = False,
    ) -> dict[str, Any]:
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
        }
        if provider is not None:
            payload["provider"] = provider
        if reasoning is not None:
            payload["reasoning"] = reasoning
        if include_reasoning is not None:
            payload["include_reasoning"] = include_reasoning
        if thinking is not None:
            payload["thinking"] = thinking
        if response_format is not None:
            payload["response_format"] = response_format
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if metadata_enabled:
            headers["X-OpenRouter-Metadata"] = "enabled"
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=body,
            method="POST",
            headers=headers,
        )
        start = time.perf_counter()
        data, attempts = self._open_json_with_retries(request)
        latency_ms = int((time.perf_counter() - start) * 1000)
        data["latency_ms"] = latency_ms
        data["request_attempts"] = attempts
        return data

    def _open_json_with_retries(self, request: urllib.request.Request) -> tuple[dict[str, Any], int]:
        attempts_allowed = self.max_retries + 1
        for attempt in range(1, attempts_allowed + 1):
            raw = ""
            try:
                with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                    raw = response.read().decode("utf-8")
                data = json.loads(raw)
                if not isinstance(data, dict):
                    raise RuntimeError("OpenRouter response JSON was not an object")
                error = data.get("error")
                if isinstance(error, dict):
                    code = response_error_code(error)
                    if code in RETRYABLE_HTTP_STATUS and attempt < attempts_allowed:
                        time.sleep(self.retry_backoff_seconds * attempt)
                        continue
                    safe_details = safe_error_detail(json.dumps(data, ensure_ascii=False), api_key=self.api_key)
                    raise RuntimeError(
                        f"{self.provider_name} response error after {attempt} attempt(s): {safe_details}"
                    )
                return data, attempt
            except urllib.error.HTTPError as exc:
                details = exc.read().decode("utf-8", errors="replace")
                if exc.code in RETRYABLE_HTTP_STATUS and attempt < attempts_allowed:
                    time.sleep(self.retry_backoff_seconds * attempt)
                    continue
                safe_details = safe_error_detail(details, api_key=self.api_key)
                raise RuntimeError(f"{self.provider_name} HTTP {exc.code} after {attempt} attempt(s): {safe_details}") from exc
            except urllib.error.URLError as exc:
                if attempt < attempts_allowed:
                    time.sleep(self.retry_backoff_seconds * attempt)
                    continue
                safe_reason = safe_error_detail(str(exc.reason), api_key=self.api_key)
                raise RuntimeError(f"{self.provider_name} request failed after {attempt} attempt(s): {safe_reason}") from exc
            except TimeoutError as exc:
                if attempt < attempts_allowed:
                    time.sleep(self.retry_backoff_seconds * attempt)
                    continue
                raise RuntimeError(f"{self.provider_name} request timed out after {attempt} attempt(s)") from exc
            except json.JSONDecodeError as exc:
                if attempt < attempts_allowed:
                    time.sleep(self.retry_backoff_seconds * attempt)
                    continue
                safe_raw = safe_error_detail(raw, api_key=self.api_key)
                raise RuntimeError(
                    f"{self.provider_name} response was not valid JSON after {attempt} attempt(s): "
                    f"{exc}; body={safe_raw}"
                ) from exc
        raise RuntimeError(f"{self.provider_name} request failed without a captured exception")


class OpenRouterClient(OpenAICompatibleChatClient):
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://openrouter.ai/api/v1",
        timeout_seconds: float | None = None,
        max_retries: int | None = None,
        retry_backoff_seconds: float | None = None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            api_key_env="OPENROUTER_API_KEY",
            base_url_env="OPENROUTER_BASE_URL",
            provider_name="OpenRouter",
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            retry_backoff_seconds=retry_backoff_seconds,
        )


class DeepSeekClient(OpenAICompatibleChatClient):
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.deepseek.com",
        timeout_seconds: float | None = None,
        max_retries: int | None = None,
        retry_backoff_seconds: float | None = None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            api_key_env="DEEPSEEK_API_KEY",
            base_url_env="DEEPSEEK_BASE_URL",
            provider_name="DeepSeek",
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            retry_backoff_seconds=retry_backoff_seconds,
        )


class QwenClient(OpenAICompatibleChatClient):
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
        timeout_seconds: float | None = None,
        max_retries: int | None = None,
        retry_backoff_seconds: float | None = None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            api_key_env="QWEN_API_KEY",
            base_url_env="QWEN_BASE_URL",
            provider_name="Qwen",
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            retry_backoff_seconds=retry_backoff_seconds,
        )


def list_openrouter_models(base_url: str = "https://openrouter.ai/api/v1") -> list[dict[str, Any]]:
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/models",
        method="GET",
        headers={"Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read().decode("utf-8")
            data = json.loads(raw)
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenRouter models HTTP {exc.code}: {safe_error_detail(details)}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"OpenRouter models response was not valid JSON: {exc}") from exc
    models = data.get("data", data)
    if not isinstance(models, list):
        raise RuntimeError("Unexpected OpenRouter models response shape")
    return [model for model in models if isinstance(model, dict)]
