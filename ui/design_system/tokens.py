from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping


class ColorRole(str, Enum):
    APP_BACKGROUND = "app-background"
    SHELL_BACKGROUND = "shell-background"
    SURFACE_PRIMARY = "surface-primary"
    SURFACE_SECONDARY = "surface-secondary"
    SURFACE_ELEVATED = "surface-elevated"
    SURFACE_INTERACTIVE = "surface-interactive"
    BORDER_SUBTLE = "border-subtle"
    BORDER_STRONG = "border-strong"
    TEXT_PRIMARY = "text-primary"
    TEXT_SECONDARY = "text-secondary"
    TEXT_MUTED = "text-muted"
    PRIMARY_ACTION = "primary-action"
    PRIMARY_ACTION_HOVER = "primary-action-hover"
    INFORMATION = "information"
    POSITIVE = "positive"
    WARNING = "warning"
    NEGATIVE = "negative"
    OPPORTUNITY = "opportunity"
    COLLECTION = "collection"
    RESEARCH = "research"
    FOCUS_RING = "focus-ring"
    DISABLED = "disabled"
    CHART_1 = "chart-1"
    CHART_2 = "chart-2"
    CHART_3 = "chart-3"
    CHART_4 = "chart-4"
    CHART_5 = "chart-5"
    CHART_6 = "chart-6"


class TypographyRole(str, Enum):
    DISPLAY = "display"
    WORKSPACE_TITLE = "workspace-title"
    SECTION_TITLE = "section-title"
    CARD_TITLE = "card-title"
    KPI_VALUE = "kpi-value"
    BODY = "body"
    BODY_STRONG = "body-strong"
    CAPTION = "caption"
    LABEL = "label"
    MONOSPACE_VALUE = "monospace-value"


class SpacingRole(str, Enum):
    XXS = "xxs"
    XS = "xs"
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"
    XXL = "xxl"
    SECTION = "section"


class Density(str, Enum):
    COMPACT = "compact"
    STANDARD = "standard"
    COMFORTABLE = "comfortable"
    LARGE_TEXT = "large-text"


@dataclass(frozen=True)
class TypographyToken:
    point_size: float
    weight: int
    line_height: float
    letter_spacing: float = 0.0
    family_role: str = "ui"


@dataclass(frozen=True)
class DensityToken:
    control_height: int
    row_height: int
    panel_padding: int
    horizontal_gap: int
    vertical_gap: int


@dataclass(frozen=True)
class MarketDEXDesignTokens:
    version: str
    visual_authority: str
    colors: Mapping[ColorRole, str]
    typography: Mapping[TypographyRole, TypographyToken]
    spacing: Mapping[SpacingRole, int]
    densities: Mapping[Density, DensityToken]
    corner_radii: Mapping[str, int]
    border_widths: Mapping[str, int]
    elevation: Mapping[str, int]
    motion_ms: Mapping[str, int]
    icon_sizes: Mapping[str, int]

    def color(self, role: ColorRole) -> str:
        return self.colors[role]

    def validate(self) -> None:
        missing_colors = set(ColorRole) - set(self.colors)
        missing_typography = set(TypographyRole) - set(self.typography)
        missing_spacing = set(SpacingRole) - set(self.spacing)
        missing_densities = set(Density) - set(self.densities)

        if missing_colors:
            raise ValueError(f"Missing color roles: {sorted(role.value for role in missing_colors)}")
        if missing_typography:
            raise ValueError(
                "Missing typography roles: "
                f"{sorted(role.value for role in missing_typography)}"
            )
        if missing_spacing:
            raise ValueError(
                f"Missing spacing roles: {sorted(role.value for role in missing_spacing)}"
            )
        if missing_densities:
            raise ValueError(
                f"Missing densities: {sorted(role.value for role in missing_densities)}"
            )

        for role, value in self.colors.items():
            if not _is_hex_color(value):
                raise ValueError(f"Invalid color token {role.value}: {value}")

        for role, value in self.spacing.items():
            if value < 0:
                raise ValueError(f"Negative spacing token {role.value}: {value}")

        for name, value in self.corner_radii.items():
            if value < 0:
                raise ValueError(f"Negative corner radius {name}: {value}")

        for name, value in self.motion_ms.items():
            if value < 0:
                raise ValueError(f"Negative motion duration {name}: {value}")


def _is_hex_color(value: str) -> bool:
    if len(value) not in (7, 9) or not value.startswith("#"):
        return False
    return all(character in "0123456789abcdefABCDEF" for character in value[1:])


def _frozen(values: dict) -> Mapping:
    return MappingProxyType(dict(values))


def build_visual_north_star_tokens() -> MarketDEXDesignTokens:
    """Return the approved semantic token baseline for desktop implementation.

    These values are the first controlled approximation of the approved Visual
    North Star. They are semantic roles, not permission for widgets to hard-code
    colors independently. Refinements require visual review and version updates.
    """

    tokens = MarketDEXDesignTokens(
        version="visual-north-star-v1.0",
        visual_authority=(
            "assets/brand/visual_north_star/marketdex_visual_north_star_v1.png"
        ),
        colors=_frozen(
            {
                ColorRole.APP_BACKGROUND: "#040B16",
                ColorRole.SHELL_BACKGROUND: "#071426",
                ColorRole.SURFACE_PRIMARY: "#0B1C33",
                ColorRole.SURFACE_SECONDARY: "#102744",
                ColorRole.SURFACE_ELEVATED: "#153254",
                ColorRole.SURFACE_INTERACTIVE: "#123B69",
                ColorRole.BORDER_SUBTLE: "#1B3D67",
                ColorRole.BORDER_STRONG: "#2579D8",
                ColorRole.TEXT_PRIMARY: "#F7FAFF",
                ColorRole.TEXT_SECONDARY: "#C6D2E3",
                ColorRole.TEXT_MUTED: "#8192AA",
                ColorRole.PRIMARY_ACTION: "#1677FF",
                ColorRole.PRIMARY_ACTION_HOVER: "#3C91FF",
                ColorRole.INFORMATION: "#28C3FF",
                ColorRole.POSITIVE: "#32D583",
                ColorRole.WARNING: "#FFB020",
                ColorRole.NEGATIVE: "#F04444",
                ColorRole.OPPORTUNITY: "#FFD12E",
                ColorRole.COLLECTION: "#8B5CF6",
                ColorRole.RESEARCH: "#B15CFF",
                ColorRole.FOCUS_RING: "#7DD3FC",
                ColorRole.DISABLED: "#46566D",
                ColorRole.CHART_1: "#2F80ED",
                ColorRole.CHART_2: "#32D583",
                ColorRole.CHART_3: "#FFD12E",
                ColorRole.CHART_4: "#F04444",
                ColorRole.CHART_5: "#8B5CF6",
                ColorRole.CHART_6: "#FF8A34",
            }
        ),
        typography=_frozen(
            {
                TypographyRole.DISPLAY: TypographyToken(26.0, 700, 1.10),
                TypographyRole.WORKSPACE_TITLE: TypographyToken(20.0, 700, 1.15),
                TypographyRole.SECTION_TITLE: TypographyToken(15.0, 700, 1.20),
                TypographyRole.CARD_TITLE: TypographyToken(12.0, 700, 1.20),
                TypographyRole.KPI_VALUE: TypographyToken(22.0, 700, 1.05),
                TypographyRole.BODY: TypographyToken(10.5, 400, 1.35),
                TypographyRole.BODY_STRONG: TypographyToken(10.5, 600, 1.35),
                TypographyRole.CAPTION: TypographyToken(9.0, 400, 1.30),
                TypographyRole.LABEL: TypographyToken(9.0, 600, 1.20, 0.2),
                TypographyRole.MONOSPACE_VALUE: TypographyToken(
                    10.5, 500, 1.25, family_role="monospace"
                ),
            }
        ),
        spacing=_frozen(
            {
                SpacingRole.XXS: 2,
                SpacingRole.XS: 4,
                SpacingRole.SM: 8,
                SpacingRole.MD: 12,
                SpacingRole.LG: 16,
                SpacingRole.XL: 24,
                SpacingRole.XXL: 32,
                SpacingRole.SECTION: 40,
            }
        ),
        densities=_frozen(
            {
                Density.COMPACT: DensityToken(28, 26, 8, 6, 6),
                Density.STANDARD: DensityToken(34, 32, 12, 10, 10),
                Density.COMFORTABLE: DensityToken(40, 38, 16, 14, 14),
                Density.LARGE_TEXT: DensityToken(46, 44, 18, 16, 16),
            }
        ),
        corner_radii=_frozen(
            {
                "small": 4,
                "control": 6,
                "panel": 8,
                "prominent": 12,
                "pill": 999,
            }
        ),
        border_widths=_frozen(
            {
                "subtle": 1,
                "standard": 1,
                "selected": 2,
                "focus": 2,
            }
        ),
        elevation=_frozen(
            {
                "base": 0,
                "panel": 1,
                "floating": 2,
                "dialog": 3,
                "critical": 4,
            }
        ),
        motion_ms=_frozen(
            {
                "instant": 0,
                "fast": 100,
                "standard": 180,
                "deliberate": 260,
                "celebration": 420,
            }
        ),
        icon_sizes=_frozen(
            {
                "small": 14,
                "standard": 18,
                "navigation": 20,
                "prominent": 28,
                "empty-state": 48,
            }
        ),
    )
    tokens.validate()
    return tokens
