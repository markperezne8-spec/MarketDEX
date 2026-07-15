import sqlite3
import sys
import tempfile
from contextlib import closing
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from services.inventory_product_link_service import InventoryProductLinkService,REQ


def test_m35_acceptance_contract() -> None:
    with tempfile.TemporaryDirectory() as td:
        database_path = Path(td) / 'db.sqlite3'
        service = InventoryProductLinkService(database_path)
        result = service.run_acceptance()
        assert result['passed'] == 12, result
        link_id = result['lid']
        product_id = service.ensure_acceptance_authority()
        assert service.link('AST-M35-CHARIZARD-001', product_id, REQ) == link_id
        with closing(sqlite3.connect(database_path)) as connection:
            assert connection.execute('select count(*) from inventory_product_links where asset_id=?', ('AST-M35-CHARIZARD-001',)).fetchone()[0] == 1
            assert connection.execute('select count(*) from inventory_history where event_id=(select created_event_id from inventory_product_links where inventory_product_link_id=?)', (link_id,)).fetchone()[0] == 0
            try:
                connection.execute('delete from inventory_product_link_history')
                raise AssertionError('delete allowed')
            except sqlite3.DatabaseError:
                pass
        verification = InventoryProductLinkService(database_path).verify()
        assert verification['passed'] == 12 and verification['lid'] == link_id
