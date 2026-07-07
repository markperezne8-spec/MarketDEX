import csv
from services.inventory_app_service import InventoryAppService


def _service(tmp_path):
    service=InventoryAppService(tmp_path/'marketdex.sqlite3')
    assets=(
        ('asset-1','Charizard ex','SINGLE',1,2500),
        ('asset-2','Mega Evolution ETB','SEALED',2,13000),
        ('asset-3','Charizard UPC','SEALED',3,9000),
    )
    for index,(asset_id,name,asset_type,quantity,cost) in enumerate(assets):
        service.add_asset(asset_id=asset_id,asset_name=name,asset_type=asset_type,quantity=quantity,total_cost_minor=cost,request_id=f'add-{index}')
    return service


def test_export_writes_libreoffice_friendly_csv(tmp_path):
    service=_service(tmp_path)
    destination=service.export_inventory_csv(service.list_inventory(),tmp_path/'inventory.csv')
    with destination.open(newline='',encoding='utf-8-sig') as handle:
        rows=list(csv.reader(handle))
    assert rows[0]==['Asset ID','Asset Name','Asset Type','Quantity','Total Cost']
    assert rows[1]==['asset-1','Charizard ex','SINGLE','1','25.00']


def test_export_preserves_exact_filtered_sorted_projection(tmp_path):
    service=_service(tmp_path)
    visible=service.list_inventory(search_text='charizard',asset_type='SEALED',sort_key='TOTAL COST',sort_order='DESC')
    destination=service.export_inventory_csv(visible,tmp_path/'visible')
    with destination.open(newline='',encoding='utf-8-sig') as handle:
        rows=list(csv.DictReader(handle))
    assert destination.suffix=='.csv'
    assert [row['Asset ID'] for row in rows]==['asset-3']
    assert rows[0]['Total Cost']=='90.00'


def test_export_empty_projection_writes_headers_only(tmp_path):
    service=_service(tmp_path)
    destination=service.export_inventory_csv([],tmp_path/'empty.csv')
    with destination.open(newline='',encoding='utf-8-sig') as handle:
        rows=list(csv.reader(handle))
    assert rows==[['Asset ID','Asset Name','Asset Type','Quantity','Total Cost']]


def test_export_is_read_only_to_authority(tmp_path):
    service=_service(tmp_path)
    with service.database.read_connection() as connection:
        before=(connection.execute('SELECT COUNT(*) n FROM event_identity').fetchone()['n'],connection.execute('SELECT COUNT(*) n FROM inventory_history').fetchone()['n'],connection.execute('SELECT COUNT(*) n FROM inventory_movements').fetchone()['n'],connection.execute('SELECT COUNT(*) n FROM audit_events').fetchone()['n'])
    service.export_inventory_csv(service.list_inventory(asset_type='SEALED'),tmp_path/'sealed.csv')
    with service.database.read_connection() as connection:
        after=(connection.execute('SELECT COUNT(*) n FROM event_identity').fetchone()['n'],connection.execute('SELECT COUNT(*) n FROM inventory_history').fetchone()['n'],connection.execute('SELECT COUNT(*) n FROM inventory_movements').fetchone()['n'],connection.execute('SELECT COUNT(*) n FROM audit_events').fetchone()['n'])
    assert after==before