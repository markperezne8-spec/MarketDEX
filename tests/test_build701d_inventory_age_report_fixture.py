from reports.definitions import (
    CURRENT_STATE,
    EVENT_HISTORY,
    INVENTORY_AGE_PATTERNS_REPORT,
    build_report_catalog,
)


def test_inventory_age_fixture_matches_workbook_backed_definition() -> None:
    definition = INVENTORY_AGE_PATTERNS_REPORT

    assert definition.report_id == 'inventory-age-patterns'
    assert definition.name == 'Inventory Age Patterns'
    assert definition.business_question == 'What patterns does inventory age reveal?'
    assert definition.evidence_families == (CURRENT_STATE, EVENT_HISTORY)
    assert definition.source_domains == ('inventory',)
    assert 'without executing queries or defining thresholds' in definition.description


def test_default_catalog_contains_exactly_one_deterministic_fixture() -> None:
    catalog = build_report_catalog()

    assert catalog.report_ids == ('inventory-age-patterns',)
    assert catalog.list_definitions() == (INVENTORY_AGE_PATTERNS_REPORT,)
    assert catalog.get('INVENTORY-AGE-PATTERNS') is INVENTORY_AGE_PATTERNS_REPORT


def test_inventory_age_fixture_adds_no_execution_or_persistence_authority() -> None:
    catalog = build_report_catalog()

    assert not hasattr(catalog, 'execute')
    assert not hasattr(catalog, 'query')
    assert not hasattr(catalog, 'save')
    assert not hasattr(catalog, 'export')
