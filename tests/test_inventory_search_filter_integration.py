from services.inventory_app_service import InventoryAppService


def _service(tmp_path):
    service=InventoryAppService(tmp_path/'marketdex.sqlite3')
    assets=(
        ('asset-1','Charizard ex 125/197','SINGLE',1,2500),
        ('asset-2','Mega Evolution ETB','SEALED',2,13000),
        ('asset-3','Charizard PSA 10','SLAB',1,18000),
        ('asset-4','Toploader Pack','ACCESSORY',5,1000),
    )
    for index,(asset_id,name,asset_type,quantity,cost) in enumerate(assets):
        service.add_asset(asset_id=asset_id,asset_name=name,asset_type=asset_type,quantity=quantity,total_cost_minor=cost,request_id=f'add-{index}')
    return service


def test_inventory_search_is_case_insensitive_and_name_scoped(tmp_path):
    rows=_service(tmp_path).list_inventory(search_text='CHARIZARD')
    assert [row['asset_id'] for row in rows]==['asset-1','asset-3']


def test_inventory_type_filter_returns_only_requested_type(tmp_path):
    rows=_service(tmp_path).list_inventory(asset_type='SEALED')
    assert [row['asset_id'] for row in rows]==['asset-2']


def test_search_and_type_filter_compose(tmp_path):
    rows=_service(tmp_path).list_inventory(search_text='charizard',asset_type='SLAB')
    assert [row['asset_id'] for row in rows]==['asset-3']


def test_all_filter_preserves_complete_sorted_projection(tmp_path):
    rows=_service(tmp_path).list_inventory(search_text='',asset_type='ALL')
    assert [row['asset_name'] for row in rows]==['Charizard ex 125/197','Charizard PSA 10','Mega Evolution ETB','Toploader Pack']


def test_search_and_filter_are_read_only(tmp_path):
    service=_service(tmp_path)
    with service.database.read_connection() as connection:
        before=(connection.execute('SELECT COUNT(*) n FROM event_identity').fetchone()['n'],connection.execute('SELECT COUNT(*) n FROM inventory_history').fetchone()['n'],connection.execute('SELECT COUNT(*) n FROM audit_events').fetchone()['n'])
    service.list_inventory(search_text='charizard',asset_type='SINGLE')
    service.list_inventory(search_text='mega',asset_type='SEALED')
    with service.database.read_connection() as connection:
        after=(connection.execute('SELECT COUNT(*) n FROM event_identity').fetchone()['n'],connection.execute('SELECT COUNT(*) n FROM inventory_history').fetchone()['n'],connection.execute('SELECT COUNT(*) n FROM audit_events').fetchone()['n'])
    assert after==before
