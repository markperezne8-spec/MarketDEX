from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .snapshot import ConfigurationSnapshot


def _merge(base: dict[str, Any], overlay: Mapping[str, Any]) -> dict[str, Any]:
    for key, value in overlay.items():
        if isinstance(value, Mapping) and isinstance(base.get(key), dict):
            base[key] = _merge(base[key], value)
        else:
            base[key] = deepcopy(value)
    return base


def overlay_configuration(
    base: ConfigurationSnapshot,
    overlay: Mapping[str, Any],
) -> ConfigurationSnapshot:
    """Return a fresh immutable snapshot with a pure partial overlay applied."""

    if not isinstance(base, ConfigurationSnapshot):
        raise TypeError('base must be a ConfigurationSnapshot')
    if not isinstance(overlay, Mapping):
        raise TypeError('overlay must be a mapping')
    return ConfigurationSnapshot(_merge(deepcopy(dict(base.values)), overlay))
