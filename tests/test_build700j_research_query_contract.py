from dataclasses import FrozenInstanceError

import pytest

from market_intelligence.composition import MarketIntelligenceComposition
from market_intelligence.research_queries import (
    ResearchQueryCatalog,
    ResearchQueryDefinition,
)


def test_research_query_definition_normalizes_provider_neutral_fields():
    definition = ResearchQueryDefinition(
        query_id='  Sealed-Watch  ',
        name='  Sealed Watch  ',
        product_ids=('PRODUCT-2', 'PRODUCT-1', 'PRODUCT-1'),
        observation_kinds=('DAILY_VOLUME', 'market_price'),
        marketplace_ids=('TCGPLAYER', 'ebay'),
        notes='  review only  ',
    )

    assert definition.query_id == 'sealed-watch'
    assert definition.name == 'Sealed Watch'
    assert definition.product_ids == ('PRODUCT-1', 'PRODUCT-2')
    assert definition.observation_kinds == ('daily_volume', 'market_price')
    assert definition.marketplace_ids == ('ebay', 'tcgplayer')
    assert definition.notes == 'review only'
    with pytest.raises(FrozenInstanceError):
        definition.name = 'Changed'


def test_research_query_definition_fails_closed_for_blank_required_values():
    with pytest.raises(ValueError, match='query_id is required'):
        ResearchQueryDefinition(query_id=' ', name='Valid')
    with pytest.raises(ValueError, match='name is required'):
        ResearchQueryDefinition(query_id='valid', name=' ')
    with pytest.raises(ValueError, match='product_id is required'):
        ResearchQueryDefinition(query_id='valid', name='Valid', product_ids=(' ',))


def test_research_query_catalog_is_deterministic_and_rejects_duplicates():
    beta = ResearchQueryDefinition(query_id='beta', name='Beta')
    alpha_b = ResearchQueryDefinition(query_id='alpha-b', name='Alpha')
    alpha_a = ResearchQueryDefinition(query_id='alpha-a', name='Alpha')
    catalog = ResearchQueryCatalog((beta, alpha_b, alpha_a))

    assert catalog.query_ids == ('alpha-a', 'alpha-b', 'beta')
    assert [item.query_id for item in catalog.list_definitions()] == [
        'alpha-a',
        'alpha-b',
        'beta',
    ]
    assert catalog.get(' ALPHA-A ') is alpha_a
    with pytest.raises(ValueError, match='already registered'):
        catalog.register(ResearchQueryDefinition(query_id='ALPHA-A', name='Duplicate'))
    with pytest.raises(KeyError, match='unknown research query'):
        catalog.get('missing')


def test_market_intelligence_composition_owns_one_empty_in_memory_catalog():
    first = MarketIntelligenceComposition()
    second = MarketIntelligenceComposition()

    assert isinstance(first.research_query_catalog, ResearchQueryCatalog)
    assert first.research_query_catalog.query_ids == ()
    assert second.research_query_catalog.query_ids == ()
    assert first.research_query_catalog is not second.research_query_catalog
