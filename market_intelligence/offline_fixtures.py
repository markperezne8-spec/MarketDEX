from datetime import datetime, timezone
from decimal import Decimal

from market_intelligence.observations import MarketObservation, ObservationKind


OFFLINE_SAMPLE_PRODUCT_ID = "SAMPLE-MEGA-ETB"
OFFLINE_SAMPLE_SOURCE_ID = "offline-fixture"


def build_offline_fixture_observations() -> tuple[MarketObservation, ...]:
    observed_at = datetime(2026, 7, 12, 12, tzinfo=timezone.utc)
    return (
        MarketObservation(
            observation_id="FIXTURE-PRICE-001",
            product_id=OFFLINE_SAMPLE_PRODUCT_ID,
            source_id=OFFLINE_SAMPLE_SOURCE_ID,
            kind=ObservationKind.MARKET_PRICE,
            observed_at=observed_at,
            value=Decimal("89.99"),
            confidence=0.92,
            currency="USD",
            sample_size=18,
            metadata={"dataset": "offline-sample", "label": "Mega Evolution ETB"},
        ),
        MarketObservation(
            observation_id="FIXTURE-LISTINGS-001",
            product_id=OFFLINE_SAMPLE_PRODUCT_ID,
            source_id=OFFLINE_SAMPLE_SOURCE_ID,
            kind=ObservationKind.ACTIVE_LISTING,
            observed_at=observed_at,
            value=Decimal("12"),
            confidence=0.88,
            sample_size=12,
            metadata={"dataset": "offline-sample", "label": "active listings"},
        ),
        MarketObservation(
            observation_id="FIXTURE-VOLUME-001",
            product_id=OFFLINE_SAMPLE_PRODUCT_ID,
            source_id=OFFLINE_SAMPLE_SOURCE_ID,
            kind=ObservationKind.DAILY_VOLUME,
            observed_at=observed_at,
            value=Decimal("25"),
            confidence=0.84,
            sample_size=7,
            metadata={"dataset": "offline-sample", "label": "daily volume"},
        ),
    )
