from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_repository import EventRepository
from repositories.inventory_repository import InventoryRepository
from services.base_service import AuthoritativeService


class InventoryAppService(AuthoritativeService):
    service_name = 'inventory_app_service'

    def __init__(self, database_path):
        self.path = Path(database_path)
        database = DatabaseManager(self.path)
        database.initialize()
        super().__init__(database, EventRepository())
        self.inventory = InventoryRepository()

    def list_inventory(self, search_text='', asset_type='ALL', sort_key='NAME', sort_order='ASC'):
        search_text = str(search_text or '').strip().casefold()
        asset_type = str(asset_type or 'ALL').strip().upper()
        sort_key = str(sort_key or 'NAME').strip().upper()
        sort_order = str(sort_order or 'ASC').strip().upper()
        sort_fields = {'NAME':'asset_name','TYPE':'asset_type','QUANTITY':'quantity','TOTAL COST':'total_cost_minor'}
        if sort_key not in sort_fields:
            raise ValueError('Unsupported inventory sort key')
        if sort_order not in {'ASC','DESC'}:
            raise ValueError('Unsupported inventory sort order')
        with self.database.read_connection() as connection:
            rows = connection.execute(
                "SELECT a.asset_id,a.asset_name,a.asset_type,i.quantity,i.total_cost_minor "
                "FROM assets a JOIN inventory_authority i ON i.asset_id=a.asset_id "
                "ORDER BY a.asset_name COLLATE NOCASE,a.asset_id"
            ).fetchall()
        inventory = [dict(row) for row in rows]
        if search_text:
            inventory = [row for row in inventory if search_text in row['asset_name'].casefold()]
        if asset_type != 'ALL':
            inventory = [row for row in inventory if row['asset_type'] == asset_type]
        field = sort_fields[sort_key]
        def sort_value(row):
            value = row[field]
            return value.casefold() if isinstance(value, str) else value
        return sorted(inventory, key=lambda row:(sort_value(row), row['asset_id']), reverse=sort_order == 'DESC')

    def get_asset_detail(self, asset_id):
        with self.database.read_connection() as connection:
            row = connection.execute(
                "SELECT a.asset_id,a.asset_name,a.asset_type,a.state,i.quantity,i.total_cost_minor,i.verified_at "
                "FROM assets a JOIN inventory_authority i ON i.asset_id=a.asset_id WHERE a.asset_id=?",
                (asset_id,),
            ).fetchone()
        if row is None:
            raise ValueError('Inventory asset not found')
        return dict(row)

    def add_asset(self, *, asset_id, asset_name, asset_type, quantity, total_cost_minor, request_id):
        asset_id = str(asset_id).strip(); asset_name = str(asset_name).strip(); asset_type = str(asset_type).strip().upper()
        quantity = int(quantity); total_cost_minor = int(total_cost_minor)
        if not asset_id or not asset_name or not asset_type or quantity < 0 or total_cost_minor < 0:
            raise ValueError('Complete valid asset details are required')
        event = self._new_event('INVENTORY_ASSET_ADDED', request_id, {'asset_id':asset_id,'asset_name':asset_name,'asset_type':asset_type,'quantity':quantity,'total_cost_minor':total_cost_minor})
        with self.database.transaction() as connection:
            self._append_event_and_audit(connection, event, 'add_inventory_asset')
            connection.execute("INSERT INTO assets(asset_id,asset_name,asset_type,state,created_event_id,created_at) VALUES (?,?,?,?,?,?)", (asset_id,asset_name,asset_type,'COMPLETED',event.event_id,event.committed_at))
            self.inventory.apply(connection, asset_id=asset_id, quantity_delta=quantity, cost_delta_minor=total_cost_minor, event_id=event.event_id, recorded_at=event.committed_at)
            connection.execute("INSERT INTO inventory_movements(movement_id,asset_id,event_id,quantity_delta,cost_delta_minor,movement_type,recorded_at) VALUES (?,?,?,?,?,?,?)", (f'movement-{event.event_id}',asset_id,event.event_id,quantity,total_cost_minor,'ASSET_ADD',event.committed_at))
            connection.execute("INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)", (event.event_id,'INVENTORY_ASSET',asset_id,'VERIFIED',event.committed_at))
            self._verify_event(connection, event)
        return asset_id

    def adjust_asset(self, *, asset_id, quantity_delta, cost_delta_minor, request_id):
        quantity_delta = int(quantity_delta); cost_delta_minor = int(cost_delta_minor)
        if quantity_delta == 0 and cost_delta_minor == 0:
            raise ValueError('Enter a quantity or cost adjustment')
        self.get_asset_detail(asset_id)
        event = self._new_event('INVENTORY_ASSET_ADJUSTED', request_id, {'asset_id':asset_id,'quantity_delta':quantity_delta,'cost_delta_minor':cost_delta_minor})
        with self.database.transaction() as connection:
            self._append_event_and_audit(connection, event, 'adjust_inventory_asset')
            self.inventory.apply(connection, asset_id=asset_id, quantity_delta=quantity_delta, cost_delta_minor=cost_delta_minor, event_id=event.event_id, recorded_at=event.committed_at)
            connection.execute("INSERT INTO inventory_movements(movement_id,asset_id,event_id,quantity_delta,cost_delta_minor,movement_type,recorded_at) VALUES (?,?,?,?,?,?,?)", (f'movement-{event.event_id}',asset_id,event.event_id,quantity_delta,cost_delta_minor,'MANUAL_ADJUSTMENT',event.committed_at))
            connection.execute("INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)", (event.event_id,'INVENTORY_ADJUSTMENT',asset_id,'VERIFIED',event.committed_at))
            self._verify_event(connection, event)
        return self.get_asset_detail(asset_id)