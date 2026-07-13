from PySide6.QtWidgets import QAbstractItemView

from market_intelligence.composition import MarketIntelligenceComposition
from market_intelligence.research_queries import ResearchQueryDefinition
from ui.market_intelligence_workspace import MarketIntelligenceWorkspace


def test_research_query_workspace_empty_state_is_explicit(qtbot):
    intelligence = MarketIntelligenceComposition()
    workspace = MarketIntelligenceWorkspace(intelligence)
    qtbot.addWidget(workspace)

    assert workspace.query_table.rowCount() == 0
    assert workspace.query_table.editTriggers() == QAbstractItemView.NoEditTriggers
    assert 'No saved research queries registered' in workspace.query_status.text()
    assert 'not persisted' in workspace.query_status.text()
    assert 'not executable' in workspace.query_status.text()


def test_research_query_workspace_uses_catalog_order_and_normalized_values(qtbot):
    intelligence = MarketIntelligenceComposition()
    intelligence.research_query_catalog.register(
        ResearchQueryDefinition(
            query_id='beta',
            name='Beta Watch',
            product_ids=('PRODUCT-2',),
            marketplace_ids=('TCGPLAYER',),
            observation_kinds=('DAILY_VOLUME',),
            notes='Review only',
        )
    )
    intelligence.research_query_catalog.register(
        ResearchQueryDefinition(
            query_id='alpha',
            name='Alpha Watch',
            product_ids=('PRODUCT-1',),
            marketplace_ids=('EBAY',),
            observation_kinds=('MARKET_PRICE',),
        )
    )

    workspace = MarketIntelligenceWorkspace(intelligence)
    qtbot.addWidget(workspace)

    assert workspace.query_table.rowCount() == 2
    assert workspace.query_table.item(0, 0).text() == 'alpha'
    assert workspace.query_table.item(0, 1).text() == 'Alpha Watch'
    assert workspace.query_table.item(0, 2).text() == 'PRODUCT-1'
    assert workspace.query_table.item(0, 3).text() == 'ebay'
    assert workspace.query_table.item(0, 4).text() == 'market_price'
    assert workspace.query_table.item(0, 5).text() == '—'
    assert workspace.query_table.item(1, 0).text() == 'beta'
    assert '2 saved research query definition(s)' in workspace.query_status.text()


def test_research_query_section_preserves_existing_market_intelligence_sections(qtbot):
    workspace = MarketIntelligenceWorkspace(MarketIntelligenceComposition())
    qtbot.addWidget(workspace)

    assert workspace.readiness_table.rowCount() == 6
    assert workspace.evidence_table.rowCount() == 3
    assert workspace.signal_table.rowCount() == 1
    assert workspace.price_bar.format() == 'USD 89.99 · offline sample'
    assert workspace.volume_bar.format() == '25 daily volume · offline sample'
