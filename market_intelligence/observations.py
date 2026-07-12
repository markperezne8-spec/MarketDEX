from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping


class ObservationKind(StrEnum):
    ACTIVE_LISTING = 'active-listing'
    SOLD_SALE = 'sold-sale'
    MARKET_PRICE = 'market-price'
    SUPPLY = 'supply'
    DAILY_VOLUME = 'daily-volume'
    SEARCH_INTEREST = 'search-interest'
    POPULATION = 'population'


@dataclass(frozen=True)
class MarketObservation:
    observation_id: str
    product_id: str
    source_id: str
    kind: ObservationKind
    observed_at: datetime
    value: Decimal
    confidence: float
    currency: str | None = None
    sample_size: int | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for field_name in ('observation_id', 'product_id', 'source_id'):
            value = getattr(self, field_name)
            if not value.strip():
                raise ValueError(f'{field_name} must not be empty')
        if not isinstance(self.observed_at, datetime):
            raise TypeError('observed_at must be a datetime')
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError('confidence must be between 0 and 1')
        if self.sample_size is not None and self.sample_size < 0:
            raise ValueError('sample_size must not be negative')
        decimal_value = Decimal(str(self.value))
        object.__setattr__(self, 'value', decimal_value)
        object.__setattr__(self, 'metadata', MappingProxyType(dict(self.metadata)))
