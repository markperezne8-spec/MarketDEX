from datetime import datetime, timezone
from decimal import Decimal

import pytest

from market_intelligence.composition import MarketIntelligenceComposition
from market_intelligence.observation_gateway import (
    FixtureObservationProvider,
    MarketObservationGateway,
    ProviderUnavailableError,
)
from market_intelligence.observations import MarketObservation, ObservationKind


def _observation(
    observation_id: str,
    *,
    product_id: str = 'PRODUCT-1',
    source_id: str = 'fixture',
    kind: ObservationKind = ObservationKind.MARKET_PRICE,
    day: int = 1,
) -> MarketObservation:
    return MarketObservation(
        observation_id=observation_id,
        product_id=product_id,
        source_id=source_id,
        kind=kind,
        observed_at=datetime(2026, 7, day, tzinfo=timezone.utc),
        value=Decimal('12.34'),
        confidence=0.9,
        currency='USD',
        sample_size=10,
        metadata={'fixture': 'true'},
    )


def test_fixture_gateway_is_deterministic_and_filters_by_product_and_kind():
    provider = FixtureObservationProvider(
        'fixture',
        (
            _observation('OBS-2', day=2),
            _observation('OBS-1', day=1),
            _observation('OBS-3', product_id='PRODUCT-2', day=3),
            _observation('OBS-4', kind=ObservationKind.DAILY_VOLUME, day=4),
        ),
    )
    gateway = MarketObservationGateway((provider,))

    first = gateway.list_observations(
        'FIXTURE',
        'PRODUCT-1',
        kinds=(ObservationKind.MARKET_PRICE,),
    )
    second = gateway.list_observations(
        'fixture',
        'PRODUCT-1',
        kinds=(ObservationKind.MARKET_PRICE,),
    )

    assert first == second
    assert [item.observation_id for item in first] == ['OBS-1', 'OBS-2']
    assert first[0].currency == 'USD'
    assert first[0].sample_size == 10
    assert first[0].metadata['fixture'] == 'true'


def test_gateway_fails_closed_for_unknown_unavailable_and_mismatched_providers():
    gateway = MarketObservationGateway()
    with pytest.raises(KeyError, match='unknown market observation provider'):
        gateway.list_observations('missing', 'PRODUCT-1')

    gateway.register(FixtureObservationProvider('offline', available=False))
    with pytest.raises(ProviderUnavailableError, match='provider is unavailable'):
        gateway.list_observations('offline', 'PRODUCT-1')

    gateway.register(
        FixtureObservationProvider(
            'fixture',
            (_observation('OBS-WRONG', source_id='other'),),
        )
    )
    with pytest.raises(ValueError, match='returned observation for source'):
        gateway.list_observations('fixture', 'PRODUCT-1')


def test_gateway_validates_query_limits_and_duplicate_registration():
    gateway = MarketObservationGateway((FixtureObservationProvider('fixture'),))

    with pytest.raises(ValueError, match='between 1 and 500'):
        gateway.list_observations('fixture', 'PRODUCT-1', limit=0)
    with pytest.raises(ValueError, match='between 1 and 500'):
        gateway.list_observations('fixture', 'PRODUCT-1', limit=501)
    with pytest.raises(ValueError, match='provider already registered'):
        gateway.register(FixtureObservationProvider('FIXTURE'))


def test_market_intelligence_composition_owns_single_offline_fixture_gateway():
    composition = MarketIntelligenceComposition()

    assert isinstance(composition.observation_gateway, MarketObservationGateway)
    assert composition.observation_gateway.provider_ids == ('offline-fixture',)
