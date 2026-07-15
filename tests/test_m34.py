import sqlite3
import sys
import tempfile
from contextlib import closing
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from services.product_registry_service import ProductRegistryService,ACCEPTANCE_REQUEST


def test_m34_acceptance_contract() -> None:
    with tempfile.TemporaryDirectory() as td:
        database_path = Path(td) / 'db.sqlite3'
        service = ProductRegistryService(database_path)
        result = service.run_acceptance()
        assert result['passed'] == 12
        product_id = result['pid']
        assert service.register('SINGLE', 'Charizard ex', 'Obsidian Flames', '125/197', 'Double Rare', ACCEPTANCE_REQUEST) == product_id
        with closing(sqlite3.connect(database_path)) as connection:
            assert connection.execute('select count(*) from products where canonical_name="Charizard ex"').fetchone()[0] == 1
            try:
                connection.execute('delete from product_registration_history')
                raise AssertionError('delete allowed')
            except sqlite3.DatabaseError:
                pass
        verification = ProductRegistryService(database_path).verify()
        assert verification['passed'] == 12 and verification['pid'] == product_id
