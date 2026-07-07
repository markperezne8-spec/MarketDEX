import pytest
from services.inventory_app_service import InventoryAppService


def _service(tmp_path):
    service=InventoryAppService(tmp_path/'marketdex.sqlite3')
    assets=(
        ('asset-1','Charizard ex','SINGLE',1,2500),
        ('asset-2','Mega Evolution ETB','SEALED',2,13000),
        ('asset-3','Alakazam PSA 10','SLAB',7,18000),
        ('asset-4','Toploader Pack','ACCESSORY',5,1000),
    )
    for index,(asset_id,name,asset_type,quantity,cost) in enumerate(assets):
        service.add_asset(asset_id=asset_id,asset_name=name,asset_type=asset_type,quantity=quantity,total_cost_minor=cost,request_id=f'add-{index}')
    return service


def test_inventory_sorts_name_ascending_by_default(tmp_path):
    rows=_service(tmp_path).list_inventory()
    assert [row['asset_name'] for row in rows]==['Alakazam PSA 10','Charizard ex','Mega Evolution ETB','Toploader Pack']


def test_inventory_sorts_quantity_descending(tmp_path):
    rows=_service(tmp_path).list_inventory(sort_key='QUANTITY',sort_order='DESC')
    assert [row['quantity'] for row in rows]==[7,5,2,1]


def test_inventory_sorts_total_cost_ascending(tmp_path):
    rows=_service(tmp_path).list_inventory(sort_key='TOTAL COST',sort_order='ASC')
    assert [row['total_cost_minor'] for row in rows]==[1000,2500,13000,18000]


def test_sort_composes_with_search_and_type_filter(tmp_path):
    service=_service(tmp_path)
    service.add_asset(asset_id='asset-5',asset_name='Charizard UPC',asset_type='SEALED',quantity=3,total_cost_minor=9000,request_id='add-5')
    rows=service.list_inventory(search_text='a',asset_type='SEALED',sort_key='TOTAL COST',sort_order='DESC')
    assert [row['asset_id'] for row in rows]==['asset-2','asset-5']


def test_invalid_sort_contract_is_rejected(tmp_path):
    service=_service(tmp_path)
    with pytest.raises(ValueError,match='sort key'): service.list_inventory(sort_key='EVENT_ID')
    with pytest.raises(ValueError,match='sort order'): service.list_inventory(sort_order='SIDEWAYS')


def test_sorting_is_read_only(tmp_path):
    service=_service(tmp_path)
    with service.database.read_connection() as connection:
        before=(connection.execute('SELECT COUNT(*) n FROM event_identity').fetchone()['n'],connection.execute('SELECT COUNT(*) n FROM inventory_history').fetchone()['n'],connection.execute('SELECT COUNT(*) n FROM audit_events').fetchone()['n'])
    for key in ('NAME','TYPE','QUANTITY','TOTAL COST'):
        service.list_inventory(sort_key=key,sort_order='DESC')
    with service.database.read_connection() as connection:
        after=(connection.execute('SELECT COUNT(*) n FROM event_identity').fetchone()['n'],connection.execute('SELECT COUNT(*) n FROM inventory_history').fetchone()['n'],connection.execute('SELECT COUNT(*) n FROM audit_events').fetchone()['n'])
    assert after==before