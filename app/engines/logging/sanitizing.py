from __future__ import annotations

from collections.abc import Mapping
from typing import Any

_REDACTED = '[REDACTED]'
_SENSITIVE_PARTS = ('password', 'token', 'secret', 'api_key', 'authorization')


def _is_sensitive(key: str) -> bool:
    normalized = key.lower().replace('-', '_')
    return any(part in normalized for part in _SENSITIVE_PARTS)


def sanitize_details(details: Mapping[str, Any]) -> dict[str, Any]:
    """Return detached diagnostic details with credential-like values redacted."""

    if not isinstance(details, Mapping):
        raise TypeError('details must be a mapping')

    sanitized: dict[str, Any] = {}
    for key, value in details.items():
        key_text = str(key)
        if _is_sensitive(key_text):
            sanitized[key_text] = _REDACTED
        elif isinstance(value, Mapping):
            sanitized[key_text] = sanitize_details(value)
        elif isinstance(value, list):
            sanitized[key_text] = [
                sanitize_details(item) if isinstance(item, Mapping) else item
                for item in value
            ]
        else:
            sanitized[key_text] = value
    return sanitized
