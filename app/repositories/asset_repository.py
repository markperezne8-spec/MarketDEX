from app.database.database_manager import DatabaseManager

class AssetRepository:
    def __init__(self):
        self.db=DatabaseManager(); self.db.initialize()

    def count(self):
        with self.db.connect() as c:
            return c.execute("SELECT COUNT(*) FROM assets").fetchone()[0]

    def all(self):
        with self.db.connect() as c:
            return c.execute("SELECT * FROM assets ORDER BY name").fetchall()

    # TODO: Implement SQL
    def add(self, asset): raise NotImplementedError
    def update(self, asset): raise NotImplementedError
    def delete(self, asset_id): raise NotImplementedError
    def find_by_uuid(self, uuid): raise NotImplementedError
    def search(self, text): raise NotImplementedError
