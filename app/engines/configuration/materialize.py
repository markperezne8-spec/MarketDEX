from __future__ import annotations

from copy import deepcopy
from typing import Any

from .snapshot import ConfigurationSnapshot


def materialize_configuration(snapshot: ConfigurationSnapshot) -> dict[str, Any]:
    """Return a detached mutable copy of an immutable configuration snapshot."""

    return deepcopy(dict(snapshot.values))
