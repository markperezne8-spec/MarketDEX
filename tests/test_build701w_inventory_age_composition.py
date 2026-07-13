from pathlib import Path

from composition.application_composition import ApplicationComposition
from reports.inventory_age_provider import ApplicationInventoryAgeInputProvider
from services.inventory_detail_read import InventoryDetailReadAdapter
from services.inventory_product_link_read import InventoryProductLinkReadAdapter


def test_build701w_composition_reuses_inventory_read_connection_authority(tmp_path) -> None:
    composition = ApplicationComposition(tmp_path / 'marketdex.sqlite3')

    provider = composition.inventory_age_input_provider

    assert isinstance(provider, ApplicationInventoryAgeInputProvider)
    assert isinstance(provider._inventory_detail_reader, InventoryDetailReadAdapter)
    assert isinstance(provider._product_link_reader, InventoryProductLinkReadAdapter)
    assert provider._inventory_detail_reader._open_read_connection.__self__ is composition.inventory.database
    assert provider._product_link_reader._open_read_connection.__self__ is composition.inventory.database


def test_build701w_composition_does_not_add_provider_execution_or_database_authority() -> None:
    source = Path('composition/application_composition.py').read_text(encoding='utf-8')

    assert 'DatabaseManager' not in source
    assert 'sqlite3' not in source
    assert '.get_inventory_age_input(' not in source
    assert 'InventoryDetailReadAdapter(self.inventory.database.read_connection)' in source
    assert 'InventoryProductLinkReadAdapter(self.inventory.database.read_connection)' in source
