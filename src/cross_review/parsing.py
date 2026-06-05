from __future__ import annotations

import json
import re
from typing import Any


FENCED_BLOCK_RE = re.compile(r"```(?:python|py)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def response_text(response: dict[str, Any]) -> str:
    choices = response.get("choices")
    if not choices:
        return ""
    first = choices[0]
    if not isinstance(first, dict):
        return ""
    message = first.get("message", {})
    if isinstance(message, dict):
        content = message.get("content", "")
        if isinstance(content, str):
            return content
    text = first.get("text", "")
    return text if isinstance(text, str) else ""


def extract_code(text: str) -> str:
    match = FENCED_BLOCK_RE.search(text)
    if match:
        return match.group(1).strip() + "\n"
    return text.strip() + "\n"


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    try:
        value = json.loads(stripped)
        if isinstance(value, dict):
            return value
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    for index, char in enumerate(stripped):
        if char != "{":
            continue
        try:
            value, _ = decoder.raw_decode(stripped[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    raise ValueError("No JSON object found in model response")


def normalize_review(value: dict[str, Any]) -> dict[str, Any]:
    bug_found = bool(value.get("bug_found", False))
    confidence = value.get("confidence", 0)
    try:
        confidence_int = int(confidence)
    except (TypeError, ValueError):
        confidence_int = 0
    confidence_int = max(0, min(confidence_int, 5))
    return {
        "bug_found": bug_found,
        "bug_type": str(value.get("bug_type", "none" if not bug_found else "other")),
        "location": str(value.get("location", "none")),
        "explanation": str(value.get("explanation", "")),
        "suggested_fix": str(value.get("suggested_fix", "")),
        "confidence": confidence_int,
    }
