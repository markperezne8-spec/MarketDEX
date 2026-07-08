import csv
import pytest
from services.inventory_app_service import InventoryAppService
from services.inventory_csv_import_service import InventoryCsvImportService


def _write(path, rows, headers=None):
    headers=headers or ['Asset ID','Asset Name','Asset Type','Quantity','Total Cost']
    with path.open('w',newline='',encoding='utf-8-sig') as handle:
        writer=csv.DictWriter(handle,fieldnames=headers); writer.writeheader(); writer.writerows(rows)
    return path


def _services(tmp_path):
    inventory=InventoryAppService(tmp_path/'marketdex.sqlite3')
    return inventory,InventoryCsvImportService(inventory)


def test_import_creates_authoritative_inventory_events(tmp_path):
    inventory,importer=_services(tmp_path)
    source=_write(tmp_path/'inventory.csv',[{'Asset ID':'asset-1','Asset Name':'Charizard ex','Asset Type':'SINGLE','Quantity':'2','Total Cost':'25.50'},{'Asset ID':'asset-2','Asset Name':'Mega Evolution ETB','Asset Type':'SEALED','Quantity':'3','Total Cost':'180.00'}])
    imported=importer.import_csv(source,'import-1')
    assert imported==['asset-1','asset-2']
    assert inventory.summarize_inventory(inventory.list_inventory())=={'asset_count':2,'total_units':5,'total_cost_minor':20550}
    with inventory.database.read_connection() as connection:
        assert connection.execute('SELECT COUNT(*) n FROM event_identity').fetchone()['n']==2
        assert connection.execute('SELECT COUNT(*) n FROM inventory_history').fetchone()['n']==2
        assert connection.execute('SELECT COUNT(*) n FROM inventory_movements').fetchone()['n']==2
        assert connection.execute("SELECT COUNT(*) n FROM audit_events WHERE verification_result='VERIFIED'").fetchone()['n']==2


def test_validation_rejects_bad_row_before_any_authority_mutation(tmp_path):
    inventory,importer=_services(tmp_path)
    source=_write(tmp_path/'bad.csv',[{'Asset ID':'asset-1','Asset Name':'Good','Asset Type':'SINGLE','Quantity':'1','Total Cost':'10.00'},{'Asset ID':'asset-2','Asset Name':'Bad','Asset Type':'UNKNOWN','Quantity':'1','Total Cost':'5.00'}])
    with pytest.raises(ValueError,match='unsupported Asset Type'):
        importer.import_csv(source,'import-bad')
    assert inventory.list_inventory()==[]
    with inventory.database.read_connection() as connection:
        assert connection.execute('SELECT COUNT(*) n FROM event_identity').fetchone()['n']==0


def test_validation_rejects_existing_and_duplicate_asset_ids(tmp_path):
    inventory,importer=_services(tmp_path)
    inventory.add_asset(asset_id='asset-existing',asset_name='Existing',asset_type='SINGLE',quantity=1,total_cost_minor=100,request_id='seed')
    existing=_write(tmp_path/'existing.csv',[{'Asset ID':'asset-existing','Asset Name':'Again','Asset Type':'SINGLE','Quantity':'1','Total Cost':'1.00'}])
    with pytest.raises(ValueError,match='already exists'):
        importer.validate_csv(existing)
    duplicate=_write(tmp_path/'duplicate.csv',[{'Asset ID':'asset-new','Asset Name':'One','Asset Type':'SINGLE','Quantity':'1','Total Cost':'1.00'},{'Asset ID':'asset-new','Asset Name':'Two','Asset Type':'SEALED','Quantity':'1','Total Cost':'2.00'}])
    with pytest.raises(ValueError,match='duplicate Asset ID'):
        importer.validate_csv(duplicate)


def test_import_requires_exact_export_headers_and_rows(tmp_path):
    _,importer=_services(tmp_path)
    wrong=_write(tmp_path/'wrong.csv',[],headers=['Name'])
    with pytest.raises(ValueError,match='headers must exactly match'):
        importer.validate_csv(wrong)
    empty=_write(tmp_path/'empty.csv',[])
    with pytest.raises(ValueError,match='no inventory rows'):
        importer.validate_csv(empty)


def test_import_request_identity_is_exactly_once(tmp_path):
    inventory,importer=_services(tmp_path)
    first=_write(tmp_path/'first.csv',[{'Asset ID':'asset-1','Asset Name':'One','Asset Type':'SINGLE','Quantity':'1','Total Cost':'1.00'}])
    importer.import_csv(first,'same-import')
    second=_write(tmp_path/'second.csv',[{'Asset ID':'asset-2','Asset Name':'Two','Asset Type':'SINGLE','Quantity':'1','Total Cost':'2.00'}])
    with pytest.raises(Exception):
        importer.import_csv(second,'same-import')
    assert [row['asset_id'] for row in inventory.list_inventory()]==['asset-1']
