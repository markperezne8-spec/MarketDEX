from dataclasses import dataclass
from datetime import date
from typing import Protocol


@dataclass(frozen=True)
class TrendPoint:
    observed_on: date
    interest_index: int

    def __post_init__(self) -> None:
        if not 0 <= self.interest_index <= 100:
            raise ValueError('interest_index must be between 0 and 100')


@dataclass(frozen=True)
class TrendSeries:
    product_id: str
    query: str
    region: str
    points: tuple[TrendPoint, ...]
    source_id: str = 'google-trends'

    def __post_init__(self) -> None:
        if not self.product_id.strip():
            raise ValueError('product_id must not be empty')
        if not self.query.strip():
            raise ValueError('trend query must not be empty')
        if not self.region.strip():
            raise ValueError('trend region must not be empty')
        dates = [point.observed_on for point in self.points]
        if dates != sorted(dates):
            raise ValueError('trend points must be ordered by date')
        if len(dates) != len(set(dates)):
            raise ValueError('trend points must not repeat a date')


class TrendProvider(Protocol):
    """Authorized provider boundary for relative search-interest data."""

    def fetch_interest(
        self,
        *,
        product_id: str,
        query: str,
        region: str,
        start_date: date,
        end_date: date,
    ) -> TrendSeries: ...
