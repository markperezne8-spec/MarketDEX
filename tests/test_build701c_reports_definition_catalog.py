from dataclasses import FrozenInstanceError

import pytest

from composition.application_composition import ApplicationComposition
from reports.definitions import (
    CURRENT_STATE,
    EVENT_HISTORY,
    OUTCOMES,
    ReportCatalog,
    ReportDefinition,
)


def test_report_definition_normalizes_workbook_backed_contract() -> None:
    definition = ReportDefinition(
        report_id='  Inventory-Movement  ',
        name='  Inventory Movement  ',
        business_question='  What patterns does inventory history reveal?  ',
        evidence_families=(OUTCOMES, CURRENT_STATE, EVENT_HISTORY, EVENT_HISTORY),
        source_domains=('Inventory', 'Listing', 'inventory'),
        description='  Read-only evidence summary.  ',
    )

    assert definition.report_id == 'inventory-movement'
    assert definition.name == 'Inventory Movement'
    assert definition.business_question == 'What patterns does inventory history reveal?'
    assert definition.evidence_families == (
        CURRENT_STATE,
        EVENT_HISTORY,
        OUTCOMES,
    )
    assert definition.source_domains == ('inventory', 'listing')
    assert definition.description == 'Read-only evidence summary.'
    with pytest.raises(FrozenInstanceError):
        definition.name = 'Changed'


def test_report_definition_fails_closed_for_invalid_authority() -> None:
    with pytest.raises(ValueError, match='business_question is required'):
        ReportDefinition('missing-question', 'Missing', ' ', (CURRENT_STATE,), ('inventory',))
    with pytest.raises(ValueError, match='must end with a question mark'):
        ReportDefinition('statement', 'Statement', 'This is not a question', (CURRENT_STATE,), ('inventory',))
    with pytest.raises(ValueError, match='at least one evidence_family'):
        ReportDefinition('missing-evidence', 'Missing', 'What is missing?', (), ('inventory',))
    with pytest.raises(ValueError, match='unsupported evidence families'):
        ReportDefinition('unsafe', 'Unsafe', 'What is unsafe?', ('invented_truth',), ('inventory',))
    with pytest.raises(ValueError, match='at least one source_domain'):
        ReportDefinition('missing-source', 'Missing', 'What is missing?', (CURRENT_STATE,), ())


def test_report_catalog_is_deterministic_and_rejects_duplicates() -> None:
    beta = ReportDefinition('beta', 'Beta', 'What is beta?', (CURRENT_STATE,), ('inventory',))
    alpha_b = ReportDefinition('alpha-b', 'Alpha', 'What is alpha B?', (EVENT_HISTORY,), ('listing',))
    alpha_a = ReportDefinition('alpha-a', 'Alpha', 'What is alpha A?', (OUTCOMES,), ('settlement',))
    catalog = ReportCatalog((beta, alpha_b, alpha_a))

    assert catalog.report_ids == ('alpha-a', 'alpha-b', 'beta')
    assert [item.report_id for item in catalog.list_definitions()] == [
        'alpha-a',
        'alpha-b',
        'beta',
    ]
    assert catalog.get(' ALPHA-A ') is alpha_a
    with pytest.raises(ValueError, match='already registered'):
        catalog.register(
            ReportDefinition('ALPHA-A', 'Duplicate', 'What is duplicated?', (CURRENT_STATE,), ('inventory',))
        )
    with pytest.raises(KeyError, match='unknown report'):
        catalog.get('missing')


def test_application_composition_owns_one_non_executable_catalog(tmp_path) -> None:
    first = ApplicationComposition(tmp_path / 'first.sqlite3')
    second = ApplicationComposition(tmp_path / 'second.sqlite3')

    assert isinstance(first.report_catalog, ReportCatalog)
    assert first.report_catalog.report_ids == ('inventory-age-patterns',)
    assert second.report_catalog.report_ids == ('inventory-age-patterns',)
    assert first.report_catalog is not second.report_catalog
    assert not hasattr(first.report_catalog, 'execute')
    assert not hasattr(first.report_catalog, 'save')
