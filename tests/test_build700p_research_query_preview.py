from decimal import Decimal

from PySide6.QtWidgets import QAbstractItemView

from market_intelligence.composition import MarketIntelligenceComposition
from market_intelligence.observation_gateway import MarketObservationGateway, FixtureObservationProvider
from market_intelligence.observations import MarketObservation, ObservationKind
from market_intelligence.offline_fixtures import (
    OFFLINE_SAMPLE_PRODUCT_ID,
    OFFLINE_SAMPLE_SOURCE_ID,
    build_offline_fixture_observations,
)
from market_intelligence.research_queries import ResearchQueryCatalog, ResearchQueryDefinition
from market_intelligence.research_query_preview import ResearchQueryPreviewService
from ui.market_intelligence_workspace import MarketIntelligenceWorkspace


def test_research_query_preview_matches_offline_fixture_evidence_only():
    service = ResearchQueryPreviewService(
        MarketObservationGateway(
            (
                FixtureObservationProvider(
                    OFFLINE_SAMPLE_SOURCE_ID,
                    build_offline_fixture_observations(),
                ),
            )
        )
    )
    definition = ResearchQueryDefinition(
        query_id='mega-evolution-etb-watch',
        name='Mega Evolution ETB Watch',
        product_ids=(OFFLINE_SAMPLE_PRODUCT_ID,),
        observation_kinds=('active_listing', 'daily_volume', 'market_price'),
    )

    rows = service.preview((definition,))

    assert [row.evidence_id for row in rows] == [
        'FIXTURE-LISTINGS-001',
        'FIXTURE-PRICE-001',
        'FIXTURE-VOLUME-001',
    ]
    assert {row.query_id for row in rows} == {'mega-evolution-etb-watch'}
    assert {row.product_id for row in rows} == {OFFLINE_SAMPLE_PRODUCT_ID}
    assert {row.observation_kind for row in rows} == {
        'active_listing',
        'daily_volume',
        'market_price',
    }
    assert rows[1].value == 'USD 89.99'
    assert rows[1].confidence == '92%'
    assert rows[1].observed_at == '2026-07-12 12:00 UTC'


def test_research_query_preview_is_empty_when_no_fixture_evidence_matches():
    service = ResearchQueryPreviewService(
        MarketObservationGateway(
            (
                FixtureObservationProvider(
                    OFFLINE_SAMPLE_SOURCE_ID,
                    build_offline_fixture_observations(),
                ),
            )
        )
    )
    definition = ResearchQueryDefinition(
        query_id='missing-product-watch',
        name='Missing Product Watch',
        product_ids=('MISSING-PRODUCT',),
        observation_kinds=('market_price',),
    )

    assert service.preview((definition,)) == ()


def test_research_query_preview_rejects_unknown_observation_kind():
    service = ResearchQueryPreviewService(
        MarketObservationGateway(
            (
                FixtureObservationProvider(
                    OFFLINE_SAMPLE_SOURCE_ID,
                    build_offline_fixture_observations(),
                ),
            )
        )
    )
    definition = ResearchQueryDefinition(
        query_id='bad-kind-watch',
        name='Bad Kind Watch',
        product_ids=(OFFLINE_SAMPLE_PRODUCT_ID,),
        observation_kinds=('not_a_kind',),
    )

    try:
        service.preview((definition,))
    except ValueError as exc:
        assert 'unknown research query observation kind: not_a_kind' in str(exc)
    else:
        raise AssertionError('Expected unknown observation kind to fail closed')


def test_market_intelligence_workspace_displays_offline_preview_rows(qtbot):
    workspace = MarketIntelligenceWorkspace(MarketIntelligenceComposition())
    qtbot.addWidget(workspace)

    assert workspace.preview_table.rowCount() == 3
    assert workspace.preview_table.editTriggers() == QAbstractItemView.NoEditTriggers
    assert workspace.preview_table.item(0, 0).text() == 'mega-evolution-etb-watch'
    assert workspace.preview_table.item(0, 1).text() == OFFLINE_SAMPLE_PRODUCT_ID
    assert workspace.preview_table.item(0, 2).text() == 'active listings'
    assert workspace.preview_table.item(0, 3).text() == 'active_listing'
    assert workspace.preview_table.item(0, 4).text() == '12'
    assert workspace.preview_table.item(1, 2).text() == 'Mega Evolution ETB'
    assert workspace.preview_table.item(1, 4).text() == 'USD 89.99'
    assert workspace.preview_table.item(2, 2).text() == 'daily volume'
    assert '3 offline fixture preview row(s)' in workspace.preview_status.text()
    assert 'read-only' in workspace.preview_status.text()
    assert 'not persisted' in workspace.preview_status.text()
    assert 'not executable' in workspace.preview_status.text()


def test_market_intelligence_workspace_preview_empty_state_is_explicit(qtbot):
    intelligence = MarketIntelligenceComposition(research_query_catalog=ResearchQueryCatalog())
    workspace = MarketIntelligenceWorkspace(intelligence)
    qtbot.addWidget(workspace)

    assert workspace.preview_table.rowCount() == 0
    assert 'No offline fixture evidence matches saved research queries' in workspace.preview_status.text()
    assert 'read-only' in workspace.preview_status.text()
    assert 'not persisted' in workspace.preview_status.text()
    assert 'not executable' in workspace.preview_status.text()


def test_research_query_preview_ignores_non_fixture_gateway_sources():
    # The preview service is intentionally pinned to the approved offline fixture source id.
    fixture_observation = build_offline_fixture_observations()[0]
    wrong_source = MarketObservation(
        observation_id='WRONG-SOURCE-001',
        product_id=OFFLINE_SAMPLE_PRODUCT_ID,
        source_id='other-provider',
        kind=ObservationKind.MARKET_PRICE,
        observed_at=fixture_observation.observed_at,
        value=Decimal('999.99'),
        confidence=1.0,
        currency='USD',
    )
    service = ResearchQueryPreviewService(
        MarketObservationGateway(
            (
                FixtureObservationProvider(OFFLINE_SAMPLE_SOURCE_ID, (fixture_observation,)),
                FixtureObservationProvider('other-provider', (wrong_source,)),
            )
        )
    )
    definition = ResearchQueryDefinition(
        query_id='source-pinning-watch',
        name='Source Pinning Watch',
        product_ids=(OFFLINE_SAMPLE_PRODUCT_ID,),
        observation_kinds=('market_price',),
    )

    rows = service.preview((definition,))

    assert len(rows) == 1
    assert rows[0].evidence_id == fixture_observation.observation_id
    assert rows[0].value == 'USD 89.99'
