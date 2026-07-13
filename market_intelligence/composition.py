from dataclasses import dataclass, field

from market_intelligence.attention_service import (
    MarketAttentionSignalService,
    build_market_attention_signal_service,
)
from market_intelligence.marketplaces import MarketplaceRegistry, build_marketplace_registry
from market_intelligence.modes import ModeCatalog, build_mode_catalog
from market_intelligence.observation_gateway import (
    MarketObservationGateway,
    build_market_observation_gateway,
)
from market_intelligence.research_queries import (
    ResearchQueryCatalog,
    build_research_query_catalog,
)
from market_intelligence.research_query_preview import (
    ResearchQueryPreviewService,
    build_research_query_preview_service,
)
from market_intelligence.visualizations import VisualizationCatalog, build_visualization_catalog


@dataclass
class MarketIntelligenceComposition:
    """Owns the stable catalogs, gateways, and services used by market-focused features."""

    mode_catalog: ModeCatalog = field(default_factory=build_mode_catalog)
    marketplace_registry: MarketplaceRegistry = field(default_factory=build_marketplace_registry)
    visualization_catalog: VisualizationCatalog = field(default_factory=build_visualization_catalog)
    observation_gateway: MarketObservationGateway = field(
        default_factory=build_market_observation_gateway
    )
    attention_signal_service: MarketAttentionSignalService = field(
        default_factory=build_market_attention_signal_service
    )
    research_query_catalog: ResearchQueryCatalog = field(
        default_factory=build_research_query_catalog
    )
    research_query_preview_service: ResearchQueryPreviewService = field(init=False)

    def __post_init__(self) -> None:
        self.research_query_preview_service = build_research_query_preview_service(
            self.observation_gateway
        )
