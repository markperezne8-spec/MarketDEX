from datetime import date

import pytest

from reports import (
    INPUT_CONFLICTING,
    INPUT_FOUND,
    INPUT_NOT_FOUND,
    INPUT_UNAVAILABLE,
    INPUT_UNLINKED,
    ApplicationInventoryAgeInputProvider,
    InventoryAgeInputProvider,
)
from services.inventory_detail_read import (
    INVENTORY_DETAIL_FOUND,
    INVENTORY_DETAIL_NOT_FOUND,
    INVENTORY_DETAIL_UNAVAILABLE,
    InventoryDetailReadRecord,
    InventoryDetailReadResult,
)
from services.inventory_product_link_read import (
    PRODUCT_LINK_CONFLICTING,
    PRODUCT_LINK_FOUND,
    PRODUCT_LINK_UNAVAILABLE,
    PRODUCT_LINK_UNLINKED,
    InventoryProductLinkReadResult,
)


class _DetailReader:
    def __init__(self, result: InventoryDetailReadResult) -> None:
        self.result = result
        self.calls = 0

    def get_inventory_detail(self, request):
        self.calls += 1
        assert request.inventory_position_id == 'asset-001'
        return self.result


class _LinkReader:
    def __init__(self, result: InventoryProductLinkReadResult) -> None:
        self.result = result
        self.calls = 0

    def get_product_link(self, request):
        self.calls += 1
        assert request.inventory_position_id == 'asset-001'
        return self.result


def _detail(status: str = 'COMPLETED') -> InventoryDetailReadResult:
    return InventoryDetailReadResult(
        INVENTORY_DETAIL_FOUND,
        InventoryDetailReadRecord(
            inventory_position_id='asset-001',
            asset_name='Sample Card',
            current_quantity=2,
            inventory_status=status,
            purchase_date_raw='2025-01-01',
            storage_location='A-1',
        ),
    )


def test_build701u_provider_composes_verified_read_evidence() -> None:
    detail_reader = _DetailReader(_detail())
    link_reader = _LinkReader(
        InventoryProductLinkReadResult(
            PRODUCT_LINK_FOUND,
            product_id='product-001',
            reason='one verified product link',
        )
    )
    provider = ApplicationInventoryAgeInputProvider(detail_reader, link_reader)

    result = provider.get_inventory_age_input('asset-001', date(2025, 2, 1))

    assert isinstance(provider, InventoryAgeInputProvider)
    assert result.outcome == INPUT_FOUND
    assert result.record is not None
    assert result.record.inventory_position_id == 'asset-001'
    assert result.record.product_id == 'product-001'
    assert result.record.current_quantity == 2
    assert result.record.purchase_date_raw == '2025-01-01'
    assert result.record.storage_location == 'A-1'
    assert result.record.as_of_date == date(2025, 2, 1)
    assert detail_reader.calls == 1
    assert link_reader.calls == 1


@pytest.mark.parametrize(
    ('detail_outcome', 'expected_outcome'),
    (
        (INVENTORY_DETAIL_NOT_FOUND, INPUT_NOT_FOUND),
        (INVENTORY_DETAIL_UNAVAILABLE, INPUT_UNAVAILABLE),
    ),
)
def test_build701u_provider_fails_closed_before_product_link_read(
    detail_outcome: str,
    expected_outcome: str,
) -> None:
    detail_reader = _DetailReader(
        InventoryDetailReadResult(detail_outcome, reason='detail evidence outcome')
    )
    link_reader = _LinkReader(InventoryProductLinkReadResult(PRODUCT_LINK_UNLINKED))
    provider = ApplicationInventoryAgeInputProvider(detail_reader, link_reader)

    result = provider.get_inventory_age_input('asset-001', date(2025, 2, 1))

    assert result.outcome == expected_outcome
    assert result.record is None
    assert link_reader.calls == 0


def test_build701u_provider_rejects_noncompleted_inventory_without_link_read() -> None:
    link_reader = _LinkReader(InventoryProductLinkReadResult(PRODUCT_LINK_UNLINKED))
    provider = ApplicationInventoryAgeInputProvider(_DetailReader(_detail('ARCHIVED')), link_reader)

    result = provider.get_inventory_age_input('asset-001', date(2025, 2, 1))

    assert result.outcome == INPUT_NOT_FOUND
    assert link_reader.calls == 0


@pytest.mark.parametrize(
    ('link_outcome', 'expected_outcome'),
    (
        (PRODUCT_LINK_UNLINKED, INPUT_UNLINKED),
        (PRODUCT_LINK_CONFLICTING, INPUT_CONFLICTING),
        (PRODUCT_LINK_UNAVAILABLE, INPUT_UNAVAILABLE),
    ),
)
def test_build701u_provider_preserves_explicit_product_link_outcomes(
    link_outcome: str,
    expected_outcome: str,
) -> None:
    provider = ApplicationInventoryAgeInputProvider(
        _DetailReader(_detail()),
        _LinkReader(InventoryProductLinkReadResult(link_outcome, reason='link evidence outcome')),
    )

    result = provider.get_inventory_age_input('asset-001', date(2025, 2, 1))

    assert result.outcome == expected_outcome
    assert result.record is None
    assert result.reason == 'link evidence outcome'


def test_build701u_provider_validates_request_before_reading() -> None:
    detail_reader = _DetailReader(_detail())
    link_reader = _LinkReader(InventoryProductLinkReadResult(PRODUCT_LINK_UNLINKED))
    provider = ApplicationInventoryAgeInputProvider(detail_reader, link_reader)

    with pytest.raises(ValueError, match='inventory_position_id is required'):
        provider.get_inventory_age_input(' ', date(2025, 2, 1))
    with pytest.raises(TypeError, match='as_of_date must be a date'):
        provider.get_inventory_age_input('asset-001', '2025-02-01')  # type: ignore[arg-type]

    assert detail_reader.calls == 0
    assert link_reader.calls == 0
