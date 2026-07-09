from datetime import datetime, timezone


class ListingPackageReviewRepository:
    def __init__(self, database_manager):
        self.database_manager = database_manager

    def save(self, asset_id, review_state):
        completed = 1 if review_state == 'PACKAGE APPROVED • OFFLINE ONLY' else 0
        now = datetime.now(timezone.utc).isoformat()
        with self.database_manager.transaction() as connection:
            connection.execute(
                '''INSERT INTO listing_package_reviews(asset_id,review_state,completed,updated_at)
                   VALUES(?,?,?,?)
                   ON CONFLICT(asset_id) DO UPDATE SET review_state=excluded.review_state,completed=excluded.completed,updated_at=excluded.updated_at''',
                (asset_id, review_state, completed, now),
            )
        return self.get(asset_id)

    def get(self, asset_id):
        with self.database_manager.read_connection() as connection:
            row = connection.execute('SELECT * FROM listing_package_reviews WHERE asset_id=?', (asset_id,)).fetchone()
            return None if row is None else dict(row)

    def list_completed(self):
        with self.database_manager.read_connection() as connection:
            rows = connection.execute(
                'SELECT * FROM listing_package_reviews WHERE completed=1 ORDER BY updated_at DESC'
            ).fetchall()
            return [dict(row) for row in rows]
