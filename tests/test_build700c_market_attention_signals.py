from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from market_intelligence.attention import AttentionSeverity, SuggestedAction
from market_intelligence.attention_service import (
    AttentionSignalPolicy,
    MarketAttentionSignalService,
)
from market_intelligence.composition import MarketIntelligenceComposition
from market_intelligence.observations import MarketObservation, ObservationKind


NOW = datetime(2026, 7, 12, 12, tzinfo=timezone.utc)


def _observation(
    observation_id: str,
    kind: ObservationKind,
    value: str,
    *,
    product_id: str = 'PRODUCT-1',
    confidence: float = 0.9,
    hours_ago: int = 1,
) -> MarketObservation:
    return MarketObservation(
        observation_id=observation_id,
        product_id=product_id,
        source_id='fixture',
        kind=kind,
        observed_at=NOW - timedelta(hours=hours_ago),
        value=Decimal(value),
        confidence=confidence,
        sample_size=10,
    )


def test_attention_service_returns_no_signals_without_evidence():
    service = MarketAttentionSignalService()

    assert service.derive_signals((), now=NOW) == ()


def test_attention_service_ignores_low_confidence_evidence():
    service = MarketAttentionSignalService(AttentionSignalPolicy(minimum_confidence=0.8))

    signals = service.derive_signals(
        (_observation('OBS-1', ObservationKind.DAILY_VOLUME, '100', confidence=0.7),),
        now=NOW,
    )

    assert signals == ()


def test_attention_service_rejects_duplicate_evidence_ids():
    service = MarketAttentionSignalService()

    with pytest.raises(ValueError, match='duplicate market observation evidence ids'):
        service.derive_signals(
            (
                _observation('OBS-1', ObservationKind.SUPPLY, '10'),
                _observation('OBS-1', ObservationKind.ACTIVE_LISTING, '5'),
            ),
            now=NOW,
        )


def test_attention_service_derives_supply_pressure_signal_from_trusted_evidence():
    service = MarketAttentionSignalService(
        AttentionSignalPolicy(supply_pressure_ratio=Decimal('1.5'))
    )

    signals = service.derive_signals(
        (
            _observation('OBS-SUPPLY', ObservationKind.SUPPLY, '30'),
            _observation('OBS-ACTIVE', ObservationKind.ACTIVE_LISTING, '10'),
        ),
        now=NOW,
    )

    assert len(signals) == 1
    signal = signals[0]
    assert signal.signal_id == 'market-supply-pressure-PRODUCT-1'
    assert signal.severity is AttentionSeverity.WATCH
    assert signal.suggested_action is SuggestedAction.REVIEW
    assert signal.evidence_ids == ('OBS-SUPPLY', 'OBS-ACTIVE')


def test_attention_service_derives_volume_opportunity_signal_from_trusted_evidence():
    service = MarketAttentionSignalService(
        AttentionSignalPolicy(volume_opportunity_ratio=Decimal('1.2'))
    )

    signals = service.derive_signals(
        (
            _observation('OBS-VOLUME', ObservationKind.DAILY_VOLUME, '25'),
            _observation('OBS-ACTIVE', ObservationKind.ACTIVE_LISTING, '10'),
        ),
        now=NOW,
    )

    assert len(signals) == 1
    signal = signals[0]
    assert signal.signal_id == 'market-volume-opportunity-PRODUCT-1'
    assert signal.severity is AttentionSeverity.OPPORTUNITY
    assert signal.evidence_ids == ('OBS-VOLUME', 'OBS-ACTIVE')


def test_attention_service_derives_stale_data_signal_for_old_latest_evidence():
    service = MarketAttentionSignalService(AttentionSignalPolicy(stale_hours=48))

    signals = service.derive_signals(
        (_observation('OBS-OLD', ObservationKind.MARKET_PRICE, '15', hours_ago=72),),
        now=NOW,
    )

    assert len(signals) == 1
    signal = signals[0]
    assert signal.signal_id == 'market-stale-PRODUCT-1'
    assert signal.severity is AttentionSeverity.INFO
    assert signal.evidence_ids == ('OBS-OLD',)


def test_attention_service_sorts_signals_by_priority_then_identity():
    service = MarketAttentionSignalService(
        AttentionSignalPolicy(
            stale_hours=48,
            supply_pressure_ratio=Decimal('1.5'),
            volume_opportunity_ratio=Decimal('1.2'),
        )
    )

    signals = service.derive_signals(
        (
            _observation('OBS-SUPPLY', ObservationKind.SUPPLY, '30', hours_ago=72),
            _observation('OBS-VOLUME', ObservationKind.DAILY_VOLUME, '25', hours_ago=72),
            _observation('OBS-ACTIVE', ObservationKind.ACTIVE_LISTING, '10', hours_ago=72),
        ),
        now=NOW,
    )

    assert [signal.priority for signal in signals] == [30, 20, 10]
    assert [signal.signal_id for signal in signals] == [
        'market-supply-pressure-PRODUCT-1',
        'market-volume-opportunity-PRODUCT-1',
        'market-stale-PRODUCT-1',
    ]


def test_attention_service_requires_timezone_aware_now():
    service = MarketAttentionSignalService()

    with pytest.raises(TypeError, match='now must be timezone-aware'):
        service.derive_signals(
            (_observation('OBS-1', ObservationKind.MARKET_PRICE, '10'),),
            now=datetime(2026, 7, 12, 12),
        )


def test_market_intelligence_composition_owns_attention_signal_service():
    composition = MarketIntelligenceComposition()

    assert isinstance(composition.attention_signal_service, MarketAttentionSignalService)
