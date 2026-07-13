from datetime import date

import pytest

from reports import (
    INPUT_CONFLICTING,
    INPUT_FOUND,
    INPUT_NOT_FOUND,
    INPUT_UNAVAILABLE,
    INPUT_UNLINKED,
    InventoryAgeInputProviderResult,
    InventoryAgeInputRecord,
    InventoryAgeReportQueryService,
    PRODUCT_LINK_LINKED,
)


class _Provider:
    def __init__(self, result: InventoryAgeInputProviderResult) -> None:
        self.result = result
        self.calls = 0

    def get_inventory_age_input(self, inventory_position_id: str, as_of_date: date):
        self.calls += 1
        assert inventory_position_id == 'asset-001'
        assert as_of_date == date(2025, 2, 1)
        return self.result


def _found(purchase_date_raw: str = '2025-01-01') -> InventoryAgeInputProviderResult:
    return InventoryAgeInputProviderResult(
        INPUT_FOUND,
        InventoryAgeInputRecord(
            inventory_position_id='asset-001',
            asset_name='Sample Card',
            current_quantity=2,
            inventory_status='COMPLETED',
            purchase_date_raw=purchase_date_raw,
            storage_location='A-1',
            product_link_state=PRODUCT_LINK_LINKED,
            product_id='product-001',
            as_of_date=date(2025, 2, 1),
        ),
        reason='approved evidence',
    )


def test_build701z_query_calls_provider_once_and_derives_found_row() -> None:
    provider = _Provider(_found())
    service = InventoryAgeReportQueryService(provider)

    result = service.get_inventory_age_row('asset-001', date(2025, 2, 1))

    assert result.outcome == INPUT_FOUND
    assert result.row is not None
    assert result.row.product_id == 'product-001'
    assert result.row.age_days == 31
    assert result.reason == 'approved evidence'
    assert provider.calls == 1


@pytest.mark.parametrize(
    'outcome',
    (INPUT_NOT_FOUND, INPUT_UNLINKED, INPUT_CONFLICTING, INPUT_UNAVAILABLE),
)
def test_build701z_query_preserves_nonfound_provider_outcomes(outcome: str) -> None:
    provider = _Provider(InventoryAgeInputProviderResult(outcome, reason='provider outcome'))
    service = InventoryAgeReportQueryService(provider)

    result = service.get_inventory_age_row('asset-001', date(2025, 2, 1))

    assert result.outcome == outcome
    assert result.row is None
    assert result.reason == 'provider outcome'
    assert provider.calls == 1


def test_build701z_query_preserves_found_provider_outcome_when_source_date_is_invalid() -> None:
    result = InventoryAgeReportQueryService(_Provider(_found('invalid-date'))).get_inventory_age_row(
        'asset-001',
        date(2025, 2, 1),
    )

    assert result.outcome == INPUT_FOUND
    assert result.row is not None
    assert result.row.age_days is None


def test_build701z_query_has_no_persistence_or_provider_recovery_path() -> None:
    source = __import__('pathlib').Path('reports/inventory_age_query.py').read_text(encoding='utf-8').lower()

    assert 'sqlite' not in source
    assert 'databasemanager' not in source
    assert 'repository' not in source
    assert source.count('.get_inventory_age_input(') == 1
