from dataclasses import dataclass
from enum import StrEnum

from market_intelligence.modes import ApplicationMode


class ChartKind(StrEnum):
    LINE = 'line'
    BAR = 'bar'
    PIE = 'pie'
    HEATMAP = 'heatmap'
    VOLUME = 'volume'
    SENTIMENT = 'sentiment'


@dataclass(frozen=True)
class ChartDefinition:
    chart_id: str
    title: str
    kind: ChartKind
    metric_id: str
    modes: frozenset[ApplicationMode]
    priority: int
    default_visible: bool = False

    def __post_init__(self) -> None:
        if not self.chart_id.strip():
            raise ValueError('chart_id must not be empty')
        if not self.title.strip():
            raise ValueError(f'chart title must not be empty: {self.chart_id}')
        if not self.metric_id.strip():
            raise ValueError(f'chart metric must not be empty: {self.chart_id}')
        if not self.modes:
            raise ValueError(f'chart must support at least one mode: {self.chart_id}')
        if self.priority < 0:
            raise ValueError(f'chart priority must not be negative: {self.chart_id}')


class VisualizationCatalog:
    def __init__(self, definitions: tuple[ChartDefinition, ...]) -> None:
        self._definitions = tuple(sorted(definitions, key=lambda definition: definition.priority))
        self._by_id = {definition.chart_id: definition for definition in definitions}
        if len(self._by_id) != len(definitions):
            raise ValueError('duplicate chart ids')

    @property
    def definitions(self) -> tuple[ChartDefinition, ...]:
        return self._definitions

    def for_mode(self, mode: ApplicationMode) -> tuple[ChartDefinition, ...]:
        return tuple(definition for definition in self._definitions if mode in definition.modes)


_BOTH_MODES = frozenset({ApplicationMode.BUSINESS, ApplicationMode.COLLECTOR})

COLLECTION_OVERVIEW_CHARTS = (
    ChartDefinition(
        'collection-value-history',
        'Collection Value',
        ChartKind.LINE,
        'collection-value-over-time',
        _BOTH_MODES,
        10,
        True,
    ),
    ChartDefinition(
        'marketplace-net-proceeds',
        'Marketplace Net Proceeds',
        ChartKind.BAR,
        'net-proceeds-by-marketplace',
        _BOTH_MODES,
        20,
        True,
    ),
    ChartDefinition(
        'collection-allocation',
        'Collection Allocation',
        ChartKind.PIE,
        'collection-value-by-category',
        _BOTH_MODES,
        30,
        True,
    ),
    ChartDefinition(
        'market-movement-heatmap',
        'Market Movement Heat Map',
        ChartKind.HEATMAP,
        'daily-price-change-by-product',
        _BOTH_MODES,
        40,
    ),
    ChartDefinition(
        'daily-market-volume',
        'Daily Market Volume',
        ChartKind.VOLUME,
        'daily-sales-volume',
        _BOTH_MODES,
        50,
    ),
    ChartDefinition(
        'market-sentiment',
        'Market Sentiment',
        ChartKind.SENTIMENT,
        'market-sentiment-score',
        _BOTH_MODES,
        60,
    ),
    ChartDefinition(
        'sealed-versus-open',
        'Sealed vs Open Value',
        ChartKind.BAR,
        'sealed-open-value-comparison',
        _BOTH_MODES,
        70,
    ),
)


def build_visualization_catalog() -> VisualizationCatalog:
    return VisualizationCatalog(COLLECTION_OVERVIEW_CHARTS)
