from dataclasses import dataclass, field

from market_intelligence.marketplaces import MarketplaceRegistry, build_marketplace_registry
from market_intelligence.modes import ModeCatalog, build_mode_catalog
from market_intelligence.visualizations import VisualizationCatalog, build_visualization_catalog


@dataclass
class MarketIntelligenceComposition:
    """Owns the stable catalogs used by market-focused features."""

    mode_catalog: ModeCatalog = field(default_factory=build_mode_catalog)
    marketplace_registry: MarketplaceRegistry = field(default_factory=build_marketplace_registry)
    visualization_catalog: VisualizationCatalog = field(default_factory=build_visualization_catalog)
