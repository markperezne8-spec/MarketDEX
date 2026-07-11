from dataclasses import dataclass
from enum import StrEnum


class MarketplaceCapability(StrEnum):
    ACTIVE_LISTINGS = 'active-listings'
    SOLD_SALES = 'sold-sales'
    MARKET_PRICE = 'market-price'
    SUPPLY = 'supply'
    DAILY_VOLUME = 'daily-volume'
    POPULATION = 'population'


@dataclass(frozen=True)
class MarketplaceDefinition:
    marketplace_id: str
    title: str
    capabilities: frozenset[MarketplaceCapability]

    def __post_init__(self) -> None:
        if not self.marketplace_id.strip():
            raise ValueError('marketplace_id must not be empty')
        if self.marketplace_id != self.marketplace_id.strip():
            raise ValueError('marketplace_id must not contain surrounding whitespace')
        if not self.title.strip():
            raise ValueError(f'marketplace title must not be empty: {self.marketplace_id}')
        if not self.capabilities:
            raise ValueError(f'marketplace must declare capabilities: {self.marketplace_id}')


class MarketplaceRegistry:
    def __init__(self, definitions: tuple[MarketplaceDefinition, ...]) -> None:
        self._definitions = definitions
        self._by_id = {definition.marketplace_id: definition for definition in definitions}
        if len(self._by_id) != len(definitions):
            raise ValueError('duplicate marketplace ids')

    @property
    def definitions(self) -> tuple[MarketplaceDefinition, ...]:
        return self._definitions

    def resolve(self, marketplace_id: str) -> MarketplaceDefinition:
        try:
            return self._by_id[marketplace_id]
        except KeyError as exc:
            raise KeyError(f'unknown marketplace: {marketplace_id}') from exc


CORE_MARKETPLACES = (
    MarketplaceDefinition(
        'ebay',
        'eBay',
        frozenset(
            {
                MarketplaceCapability.ACTIVE_LISTINGS,
                MarketplaceCapability.SOLD_SALES,
                MarketplaceCapability.SUPPLY,
                MarketplaceCapability.DAILY_VOLUME,
            }
        ),
    ),
    MarketplaceDefinition(
        'tcgplayer',
        'TCGplayer',
        frozenset(
            {
                MarketplaceCapability.ACTIVE_LISTINGS,
                MarketplaceCapability.MARKET_PRICE,
                MarketplaceCapability.SUPPLY,
                MarketplaceCapability.DAILY_VOLUME,
            }
        ),
    ),
    MarketplaceDefinition(
        'collectr',
        'Collectr',
        frozenset({MarketplaceCapability.MARKET_PRICE}),
    ),
    MarketplaceDefinition(
        'psa',
        'PSA',
        frozenset({MarketplaceCapability.MARKET_PRICE, MarketplaceCapability.POPULATION}),
    ),
    MarketplaceDefinition(
        'local',
        'Local / Manual',
        frozenset({MarketplaceCapability.SOLD_SALES, MarketplaceCapability.MARKET_PRICE}),
    ),
)


def build_marketplace_registry() -> MarketplaceRegistry:
    return MarketplaceRegistry(CORE_MARKETPLACES)
