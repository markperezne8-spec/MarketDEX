"""MarketDEX desktop design-system contracts.

The package contains presentation-safe semantic tokens and component definitions.
It deliberately does not import PySide6 so foundations can be tested without a UI
runtime and reused by desktop view implementations.
"""

from .component_contracts import (
    ComponentDefinition,
    ComponentState,
    build_component_catalog,
)
from .tokens import (
    ColorRole,
    Density,
    MarketDEXDesignTokens,
    SpacingRole,
    TypographyRole,
    build_visual_north_star_tokens,
)

__all__ = [
    "ColorRole",
    "ComponentDefinition",
    "ComponentState",
    "Density",
    "MarketDEXDesignTokens",
    "SpacingRole",
    "TypographyRole",
    "build_component_catalog",
    "build_visual_north_star_tokens",
]
