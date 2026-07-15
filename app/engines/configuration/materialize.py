from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .snapshot import ConfigurationSnapshot


def _materialize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _materialize(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_materialize(item) for item in value]
    return deepcopy(value)


def materialize_configuration(snapshot: ConfigurationSnapshot) -> dict[str, Any]:
    """Return a detached mutable copy of an immutable configuration snapshot."""

    return _materialize(snapshot.values)
