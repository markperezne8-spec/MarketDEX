from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from composition.application_composition import ApplicationComposition
from market_intelligence.attention import (
    AttentionSeverity,
    AttentionSignal,
    SuggestedAction,
)
from market_intelligence.marketplaces import MarketplaceCapability
from market_intelligence.modes import ApplicationMode
from market_intelligence.observations import MarketObservation, ObservationKind
from market_intelligence.sealed_decision import (
    SealedDecisionInput,
    SealedRecommendation,
    evaluate_sealed_decision,
)
from market_intelligence.trends import TrendPoint, TrendSeries
from market_intelligence.visualizations import ChartKind


def test_application_composition_owns_market_intelligence_catalogs(tmp_path):
    composition = ApplicationComposition(tmp_path / 'marketdex.sqlite3')

    assert composition.market_intelligence.mode_catalog.resolve(ApplicationMode.BUSINESS)
    assert composition.market_intelligence.marketplace_registry.resolve('ebay')
    assert composition.market_intelligence.visualization_catalog.definitions


def test_modes_expose_business_and_collector_categories():
    composition = ApplicationComposition.__new__(ApplicationComposition)
    from market_intelligence.composition import MarketIntelligenceComposition

    intelligence = MarketIntelligenceComposition()
    business = intelligence.mode_catalog.resolve(ApplicationMode.BUSINESS)
    collector = intelligence.mode_catalog.resolve(ApplicationMode.COLLECTOR)

    assert {'inventory', 'pricing', 'marketplaces', 'sealed-decisions'} <= set(business.categories)
    assert {'collection-overview', 'watchlist', 'grading', 'sealed-decisions'} <= set(collector.categories)


def test_marketplace_registry_declares_supported_capabilities():
    from market_intelligence.composition import MarketIntelligenceComposition

    registry = MarketIntelligenceComposition().marketplace_registry

    assert MarketplaceCapability.SOLD_SALES in registry.resolve('ebay').capabilities
    assert MarketplaceCapability.MARKET_PRICE in registry.resolve('tcgplayer').capabilities
    assert MarketplaceCapability.POPULATION in registry.resolve('psa').capabilities


def test_collection_overview_includes_every_required_visualization_kind():
    from market_intelligence.composition import MarketIntelligenceComposition

    charts = MarketIntelligenceComposition().visualization_catalog.definitions
    kinds = {chart.kind for chart in charts}

    assert {
        ChartKind.LINE,
        ChartKind.BAR,
        ChartKind.PIE,
        ChartKind.HEATMAP,
        ChartKind.VOLUME,
        ChartKind.SENTIMENT,
    } <= kinds
    assert [chart.chart_id for chart in charts if chart.default_visible] == [
        'collection-value-history',
        'marketplace-net-proceeds',
        'collection-allocation',
    ]


def test_market_observation_preserves_source_confidence_and_daily_metrics():
    observation = MarketObservation(
        observation_id='OBS-1',
        product_id='PRODUCT-1',
        source_id='ebay',
        kind=ObservationKind.DAILY_VOLUME,
        observed_at=datetime(2026, 7, 11, tzinfo=timezone.utc),
        value=Decimal('42'),
        confidence=0.9,
        sample_size=42,
    )

    assert observation.value == Decimal('42')
    assert observation.kind is ObservationKind.DAILY_VOLUME
    assert observation.confidence == 0.9


def test_attention_signal_ranks_important_actions():
    signal = AttentionSignal(
        signal_id='SIGNAL-1',
        subject_id='PRODUCT-1',
        severity=AttentionSeverity.WATCH,
        title='Supply is falling',
        explanation='Daily listed supply fell while confirmed sales volume increased.',
        suggested_action=SuggestedAction.REVIEW,
        confidence=0.8,
        created_at=datetime(2026, 7, 11, tzinfo=timezone.utc),
        evidence_ids=('OBS-1', 'OBS-2'),
    )

    assert signal.priority == 30
    assert signal.suggested_action is SuggestedAction.REVIEW


def test_sealed_decision_compares_pack_value_with_sealed_net_value():
    result = evaluate_sealed_decision(
        SealedDecisionInput(
            sealed_market_value_minor=6000,
            pack_count=10,
            expected_pack_value_minor=1200,
            sealed_selling_cost_minor=500,
            opening_cost_minor=100,
            expected_open_value_confidence=0.75,
            decision_buffer_percent=10,
        )
    )

    assert result.sealed_price_per_pack_minor == 600
    assert result.expected_open_gross_minor == 12000
    assert result.risk_adjusted_open_value_minor == 8900
    assert result.recommendation is SealedRecommendation.OPEN


def test_google_trends_series_uses_ordered_relative_interest_points():
    series = TrendSeries(
        product_id='PRODUCT-1',
        query='Charizard ex Pokemon card',
        region='US',
        points=(
            TrendPoint(date(2026, 7, 10), 45),
            TrendPoint(date(2026, 7, 11), 72),
        ),
    )

    assert series.source_id == 'google-trends'
    assert series.points[-1].interest_index == 72

    with pytest.raises(ValueError, match='between 0 and 100'):
        TrendPoint(date(2026, 7, 11), 101)
