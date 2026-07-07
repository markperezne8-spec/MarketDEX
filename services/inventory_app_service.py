from pathlib import Path
from core.database_manager import DatabaseManager
from core.event_repository import EventRepository
from services.base_service import AuthoritativeService


class InventoryAppService(AuthoritativeService):
    service_name = 'inventory_app_service'

    def __init__(self, database_path):
        self.path = Path(database_path)
        database = DatabaseManager(self.path)
        database.initialize()
        super().__init__(database, EventRepository())

    def list_inventory(self):
        with self.database.read_connection() as connection:
            rows = connection.execute(
                "SELECT a.asset_id,a.asset_name,a.asset_type,i.quantity,i.total_cost_minor "
                "FROM assets a JOIN inventory_authority i ON i.asset_id=a.asset_id "
                "ORDER BY a.asset_name COLLATE NOCASE,a.asset_id"
            ).fetchall()
        return [dict(row) for row in rows]

    def add_asset(self, *, asset_id, asset_name, asset_type, quantity, total_cost_minor, request_id):
        asset_id = str(asset_id).strip()
        asset_name = str(asset_name).strip()
        asset_type = str(asset_type).strip().upper()
        quantity = int(quantity)
        total_cost_minor = int(total_cost_minor)
        if not asset_id or not asset_name or not asset_type or quantity < 0 or total_cost_minor < 0:
            raise ValueError('Complete valid asset details are required')
        event = self._new_event('INVENTORY_ASSET_ADDED', request_id, {
            'asset_id': asset_id, 'asset_name': asset_name, 'asset_type': asset_type,
            'quantity': quantity, 'total_cost_minor': total_cost_minor,
        })
        with self.database.transaction() as connection:
            self._append_event_and_audit(connection, event, 'add_inventory_asset')
            connection.execute(
                "INSERT INTO assets(asset_id,asset_name,asset_type,state,created_event_id,created_at) VALUES (?,?,?,?,?,?)",
                (asset_id, asset_name, asset_type, 'COMPLETED', event.event_id, event.committed_at),
            )
            connection.execute(
                "INSERT INTO inventory_authority(asset_id,quantity,total_cost_minor,last_event_id,verified_at) VALUES (?,?,?,?,?)",
                (asset_id, quantity, total_cost_minor, event.event_id, event.committed_at),
            )
            connection.execute(
                "INSERT INTO inventory_history(event_id,asset_id,quantity_delta,cost_delta_minor,resulting_quantity,resulting_total_cost_minor,recorded_at) VALUES (?,?,?,?,?,?,?)",
                (event.event_id, asset_id, quantity, total_cost_minor, quantity, total_cost_minor, event.committed_at),
            )
            connection.execute(
                "INSERT INTO inventory_movements(movement_id,asset_id,event_id,quantity_delta,cost_delta_minor,movement_type,recorded_at) VALUES (?,?,?,?,?,?,?)",
                (f'movement-{event.event_id}', asset_id, event.event_id, quantity, total_cost_minor, 'ASSET_ADD', event.committed_at),
            )
            connection.execute(
                "INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)",
                (event.event_id, 'INVENTORY_ASSET', asset_id, 'VERIFIED', event.committed_at),
            )
            self._verify_event(connection, event)
        return asset_id
