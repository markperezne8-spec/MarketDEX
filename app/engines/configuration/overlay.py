from __future__ import annotations

from typing import Any, Mapping

from .materialize import _materialize
from .snapshot import ConfigurationSnapshot


def _merge(base: dict[str, Any], overlay: Mapping[str, Any]) -> dict[str, Any]:
    for key, value in overlay.items():
        current = base.get(key)
        if isinstance(value, Mapping) and isinstance(current, Mapping):
            base[key] = _merge(dict(current), value)
        else:
            base[key] = _materialize(value)
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
    return ConfigurationSnapshot(_merge(_materialize(base.values), overlay))
