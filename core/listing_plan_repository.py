from datetime import datetime, timezone
from uuid import uuid4


class ListingPlanRepository:
    def __init__(self, database_manager):
        self.database_manager = database_manager

    def save(self, asset_id, marketplace, target_sale_price_minor, fee_percent, shipping_minor, packaging_minor, target_roi_percent):
        now = datetime.now(timezone.utc).isoformat()
        with self.database_manager.transaction() as connection:
            existing = connection.execute('SELECT plan_id FROM listing_plans WHERE asset_id=?', (asset_id,)).fetchone()
            plan_id = existing['plan_id'] if existing else str(uuid4())
            connection.execute(
                '''INSERT INTO listing_plans(plan_id,asset_id,marketplace,target_sale_price_minor,fee_percent,shipping_minor,packaging_minor,target_roi_percent,updated_at)
                   VALUES(?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(asset_id) DO UPDATE SET marketplace=excluded.marketplace,target_sale_price_minor=excluded.target_sale_price_minor,fee_percent=excluded.fee_percent,shipping_minor=excluded.shipping_minor,packaging_minor=excluded.packaging_minor,target_roi_percent=excluded.target_roi_percent,updated_at=excluded.updated_at''',
                (plan_id, asset_id, marketplace, int(target_sale_price_minor), float(fee_percent), int(shipping_minor), int(packaging_minor), float(target_roi_percent), now),
            )
        return self.get(asset_id)

    def get(self, asset_id):
        with self.database_manager.read_connection() as connection:
            row = connection.execute('SELECT * FROM listing_plans WHERE asset_id=?', (asset_id,)).fetchone()
            return None if row is None else dict(row)

    def list_all(self):
        with self.database_manager.read_connection() as connection:
            return [dict(row) for row in connection.execute('SELECT * FROM listing_plans ORDER BY updated_at DESC').fetchall()]
