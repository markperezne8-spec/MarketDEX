from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from .defaults import DEFAULT_CONFIGURATION
from .validation import validate_configuration


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


@dataclass(frozen=True, slots=True)
class ConfigurationSnapshot:
    """Immutable, in-memory configuration value with no persistence authority."""

    values: Mapping[str, Any]

    def __post_init__(self) -> None:
        source = deepcopy(dict(self.values))
        if not validate_configuration(source):
            raise ValueError('configuration snapshot is invalid')
        object.__setattr__(self, 'values', _freeze(source))

    def get(self, key: str, default: Any = None) -> Any:
        return self.values.get(key, default)


def build_default_snapshot() -> ConfigurationSnapshot:
    """Build a fresh validated default snapshot without shared mutable state."""

    return ConfigurationSnapshot(deepcopy(DEFAULT_CONFIGURATION))
