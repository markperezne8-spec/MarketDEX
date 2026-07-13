from pathlib import Path

from composition.application_composition import ApplicationComposition
from reports.inventory_age_provider import ApplicationInventoryAgeInputProvider
from reports.inventory_age_query import InventoryAgeReportQueryService


def test_build701aa_composition_retains_query_service_over_existing_provider(tmp_path) -> None:
    composition = ApplicationComposition(tmp_path / 'marketdex.sqlite3')

    assert isinstance(composition.inventory_age_report_query, InventoryAgeReportQueryService)
    assert composition.inventory_age_report_query._input_provider is composition.inventory_age_input_provider
    assert isinstance(composition.inventory_age_input_provider, ApplicationInventoryAgeInputProvider)


def test_build701aa_composition_does_not_invoke_provider_or_query_at_startup() -> None:
    source = Path('composition/application_composition.py').read_text(encoding='utf-8')

    assert '.get_inventory_age_input(' not in source
    assert '.get_inventory_age_row(' not in source
    assert 'InventoryAgeReportQueryService(' in source
    assert 'self.inventory_age_input_provider' in source
