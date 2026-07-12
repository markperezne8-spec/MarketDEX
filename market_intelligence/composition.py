from dataclasses import dataclass, field

from market_intelligence.marketplaces import MarketplaceRegistry, build_marketplace_registry
from market_intelligence.modes import ModeCatalog, build_mode_catalog
from market_intelligence.observation_gateway import (
    MarketObservationGateway,
    build_market_observation_gateway,
)
from market_intelligence.visualizations import VisualizationCatalog, build_visualization_catalog


@dataclass
class MarketIntelligenceComposition:
    """Owns the stable catalogs and gateways used by market-focused features."""

    mode_catalog: ModeCatalog = field(default_factory=build_mode_catalog)
    marketplace_registry: MarketplaceRegistry = field(default_factory=build_marketplace_registry)
    visualization_catalog: VisualizationCatalog = field(default_factory=build_visualization_catalog)
    observation_gateway: MarketObservationGateway = field(
        default_factory=build_market_observation_gateway
    )
