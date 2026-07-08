from pathlib import Path
from core.database_manager import DatabaseManager


class MissionControlService:
    """Read-only desktop projection over the protected MarketDEX SQLite authority."""

    def __init__(self, database_path):
        self.path = Path(database_path)
        self.database = DatabaseManager(self.path)
        self.database.initialize()

    def snapshot(self):
        with self.database.read_connection() as connection:
            inventory = connection.execute(
                "SELECT COALESCE(SUM(i.quantity),0) AS units, "
                "COALESCE(SUM(i.total_cost_minor),0) AS cost_minor, "
                "COUNT(*) AS asset_count FROM inventory_authority i "
                "JOIN assets a ON a.asset_id=i.asset_id WHERE a.state='COMPLETED'"
            ).fetchone()
            sales = connection.execute(
                "SELECT COUNT(*) AS sale_count, COALESCE(SUM(revenue_minor),0) AS revenue_minor, "
                "COALESCE(SUM(profit_minor),0) AS profit_minor FROM sales WHERE state='COMPLETED'"
            ).fetchone()
            audits = connection.execute("SELECT COUNT(*) AS verified_count FROM audit_events WHERE verification_result='VERIFIED'").fetchone()
            events = connection.execute("SELECT COUNT(*) AS event_count FROM event_identity").fetchone()
        return {'inventory_units':int(inventory['units']),'inventory_asset_count':int(inventory['asset_count']),'inventory_cost_minor':int(inventory['cost_minor']),'completed_sales':int(sales['sale_count']),'revenue_minor':int(sales['revenue_minor']),'profit_minor':int(sales['profit_minor']),'verified_audits':int(audits['verified_count']),'authority_events':int(events['event_count']),'database_path':str(self.path)}