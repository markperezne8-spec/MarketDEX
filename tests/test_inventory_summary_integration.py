from services.inventory_app_service import InventoryAppService


def _service(tmp_path):
    service=InventoryAppService(tmp_path/'marketdex.sqlite3')
    assets=(
        ('asset-1','Charizard ex','SINGLE',1,2500),
        ('asset-2','Mega Evolution ETB','SEALED',2,13000),
        ('asset-3','Alakazam PSA 10','SLAB',7,18000),
        ('asset-4','Toploader Pack','ACCESSORY',5,1000),
        ('asset-5','Charizard UPC','SEALED',3,9000),
    )
    for index,(asset_id,name,asset_type,quantity,cost) in enumerate(assets):
        service.add_asset(asset_id=asset_id,asset_name=name,asset_type=asset_type,quantity=quantity,total_cost_minor=cost,request_id=f'add-{index}')
    return service


def test_summary_totals_current_inventory_projection(tmp_path):
    service=_service(tmp_path)
    summary=service.summarize_inventory(service.list_inventory())
    assert summary=={'asset_count':5,'total_units':18,'total_cost_minor':43500}


def test_summary_tracks_filtered_projection(tmp_path):
    service=_service(tmp_path)
    rows=service.list_inventory(asset_type='SEALED')
    assert service.summarize_inventory(rows)=={'asset_count':2,'total_units':5,'total_cost_minor':22000}


def test_summary_tracks_search_and_filter_composition(tmp_path):
    service=_service(tmp_path)
    rows=service.list_inventory(search_text='charizard',asset_type='SEALED',sort_key='TOTAL COST',sort_order='DESC')
    assert service.summarize_inventory(rows)=={'asset_count':1,'total_units':3,'total_cost_minor':9000}


def test_empty_projection_has_zero_summary(tmp_path):
    service=_service(tmp_path)
    rows=service.list_inventory(search_text='missing asset')
    assert service.summarize_inventory(rows)=={'asset_count':0,'total_units':0,'total_cost_minor':0}


def test_summary_is_read_only(tmp_path):
    service=_service(tmp_path)
    with service.database.read_connection() as connection:
        before=(connection.execute('SELECT COUNT(*) n FROM event_identity').fetchone()['n'],connection.execute('SELECT COUNT(*) n FROM inventory_history').fetchone()['n'],connection.execute('SELECT COUNT(*) n FROM audit_events').fetchone()['n'])
    service.summarize_inventory(service.list_inventory(asset_type='SEALED'))
    with service.database.read_connection() as connection:
        after=(connection.execute('SELECT COUNT(*) n FROM event_identity').fetchone()['n'],connection.execute('SELECT COUNT(*) n FROM inventory_history').fetchone()['n'],connection.execute('SELECT COUNT(*) n FROM audit_events').fetchone()['n'])
    assert after==before