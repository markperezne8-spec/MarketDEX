from pathlib import Path


DOC_PATH = Path('docs/reports/inventory_age_report_query_service_boundary.md')


def test_build701x_query_boundary_requires_one_injected_provider_call() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    assert 'PREBUILD QUERY-SERVICE GATE' in content
    assert 'Injected InventoryAgeInputProvider — exactly one call' in content
    assert 'build_inventory_age_row_from_input()' in content
    assert 'only when the provider result is `found`' in content
    assert 'one Inventory position and one caller-provided `as_of_date`' in content


def test_build701x_query_boundary_preserves_outcomes_and_rejects_persistence_access() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    assert '`found`, `not_found`, `unlinked`, `conflicting`, or `unavailable`' in content
    assert 'return a row for an unlinked, conflicting, unavailable, or not-found provider result' in content
    assert 'invoke the provider again to recover an outcome' in content
    assert 'Mark has pulled current `main` locally' in content
    assert 'open SQLite connections' in content
    assert 'construct `DatabaseManager`, `InventoryAppService`, or product-link services' in content
