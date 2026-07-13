import pytest

from reports.definitions import (
    CATALOG_ONLY_EXECUTION_MODE,
    ReportDefinition,
    build_report_catalog,
)


def test_build701ay_catalog_declares_catalog_only_mode() -> None:
    report = build_report_catalog().get('inventory-age-patterns')

    assert report.execution_mode == CATALOG_ONLY_EXECUTION_MODE


def test_build701ay_rejects_unsupported_execution_mode() -> None:
    with pytest.raises(ValueError, match='unsupported execution mode'):
        ReportDefinition(
            report_id='invalid-mode',
            name='Invalid Mode',
            business_question='Does this report execute?',
            evidence_families=('current_state',),
            source_domains=('inventory',),
            execution_mode='live-provider',
        )
