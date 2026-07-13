from datetime import date, datetime

import pytest

from reports.inventory_age_query_request import InventoryAgeReportQueryRequest


def test_build701af_request_normalizes_identity_and_remains_immutable() -> None:
    request = InventoryAgeReportQueryRequest('  position-701af  ', date(2026, 7, 13))

    assert request.inventory_position_id == 'position-701af'
    assert request.as_of_date == date(2026, 7, 13)
    with pytest.raises(AttributeError):
        request.inventory_position_id = 'changed'


@pytest.mark.parametrize('value', ['', '   '])
def test_build701af_request_rejects_missing_identity(value: str) -> None:
    with pytest.raises(ValueError, match='inventory_position_id is required'):
        InventoryAgeReportQueryRequest(value, date(2026, 7, 13))


def test_build701af_request_requires_explicit_date() -> None:
    with pytest.raises(TypeError, match='as_of_date must be a date'):
        InventoryAgeReportQueryRequest('position-701af', datetime.now().time())
