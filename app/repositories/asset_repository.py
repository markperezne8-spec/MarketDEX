"""Asset repository implementing CRUD operations for assets."""

from datetime import datetime, timezone
from app.database.database_manager import DatabaseManager
from app.models.asset import Asset


class AssetRepository:
    """Repository pattern implementation for Asset persistence.
    
    Provides CRUD operations using parameterized SQL for security.
    All operations use UUID as the primary identifier.
    """

    def __init__(self):
        self.db = DatabaseManager()
        self.db.initialize()

    # Helper method
    @staticmethod
    def _row_to_asset(row) -> Asset:
        """Convert database row to Asset object.
        
        Args:
            row: sqlite3.Row from database query
            
        Returns:
            Asset object with all fields populated
        """
        return Asset(
            uuid=row['uuid'] or "",
            name=row['name'] or "",
            asset_type=row['asset_type'] or "",
            set_name=row['set_name'] or "",
            card_number=row['card_number'] or "",
            rarity=row['rarity'] or "",
            variant=row['variant'] or "",
            card_condition=row['card_condition'] or "",
            quantity=row['quantity'] or 0,
            purchase_price=row['purchase_price'] or 0.0,
            current_value=row['current_value'] or 0.0,
            purchase_date=row['purchase_date'] or "",
            purchase_source=row['purchase_source'] or "",
            storage_location=row['storage_location'] or "",
            notes=row['notes'] or "",
            status=row['status'] or "inventory",
            created_at=row['created_at'] or "",
            updated_at=row['updated_at'] or "",
        )

    # Query methods
    def count(self) -> int:
        """Get total number of assets.
        
        Returns:
            int: Total asset count
        """
        with self.db.connect() as conn:
            result = conn.execute("SELECT COUNT(*) FROM assets").fetchone()
            return result[0]

    def exists(self, uuid: str) -> bool:
        """Check if asset with given UUID exists.
        
        Args:
            uuid: Asset UUID to check
            
        Returns:
            bool: True if asset exists, False otherwise
        """
        with self.db.connect() as conn:
            result = conn.execute(
                "SELECT 1 FROM assets WHERE uuid = ? LIMIT 1",
                (uuid,)
            ).fetchone()
            return result is not None

    def get_all(self) -> list:
        """Get all assets ordered by creation date (newest first).
        
        Returns:
            list: List of Asset objects
        """
        with self.db.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM assets ORDER BY created_at DESC"
            ).fetchall()
            return [self._row_to_asset(row) for row in rows]

    def find_by_uuid(self, uuid: str) -> Asset:
        """Find asset by UUID.
        
        Args:
            uuid: Asset UUID to search for
            
        Returns:
            Asset: Asset object if found, None otherwise
        """
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM assets WHERE uuid = ?",
                (uuid,)
            ).fetchone()
            return self._row_to_asset(row) if row else None

    def search(self, query: str) -> list:
        """Search assets by keyword across multiple fields.
        
        Searches in: name, set_name, card_number, purchase_source,
                    storage_location, notes, status
        
        Args:
            query: Search term (case-insensitive)
            
        Returns:
            list: List of matching Asset objects
        """
        search_pattern = f"%{query}%"
        with self.db.connect() as conn:
            rows = conn.execute(
                """SELECT * FROM assets WHERE
                   name LIKE ? OR
                   set_name LIKE ? OR
                   card_number LIKE ? OR
                   purchase_source LIKE ? OR
                   storage_location LIKE ? OR
                   notes LIKE ? OR
                   status LIKE ?
                   ORDER BY created_at DESC""",
                (search_pattern, search_pattern, search_pattern,
                 search_pattern, search_pattern, search_pattern,
                 search_pattern)
            ).fetchall()
            return [self._row_to_asset(row) for row in rows]

    # CRUD operations
    def add(self, asset: Asset) -> str:
        """Add new asset to database.
        
        Args:
            asset: Asset object to insert (UUID auto-generated if not set)
            
        Returns:
            str: UUID of created asset
        """
        with self.db.connect() as conn:
            conn.execute(
                """INSERT INTO assets (
                   uuid, name, asset_type, set_name, card_number,
                   rarity, variant, card_condition, quantity,
                   purchase_price, current_value, purchase_date,
                   purchase_source, storage_location, notes,
                   status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (asset.uuid, asset.name, asset.asset_type, asset.set_name,
                 asset.card_number, asset.rarity, asset.variant,
                 asset.card_condition, asset.quantity, asset.purchase_price,
                 asset.current_value, asset.purchase_date, asset.purchase_source,
                 asset.storage_location, asset.notes, asset.status,
                 asset.created_at, asset.updated_at)
            )
            conn.commit()
        return asset.uuid

    def update(self, asset: Asset) -> bool:
        """Update existing asset (preserves created_at, updates updated_at).
        
        Args:
            asset: Asset object with updated values
            
        Returns:
            bool: True if asset was updated, False if not found
        """
        # Auto-update the updated_at timestamp
        asset.updated_at = datetime.now(timezone.utc).isoformat()
        
        with self.db.connect() as conn:
            cursor = conn.execute(
                """UPDATE assets SET
                   name = ?, asset_type = ?, set_name = ?, card_number = ?,
                   rarity = ?, variant = ?, card_condition = ?, quantity = ?,
                   purchase_price = ?, current_value = ?, purchase_date = ?,
                   purchase_source = ?, storage_location = ?, notes = ?,
                   status = ?, updated_at = ?
                WHERE uuid = ?""",
                (asset.name, asset.asset_type, asset.set_name, asset.card_number,
                 asset.rarity, asset.variant, asset.card_condition, asset.quantity,
                 asset.purchase_price, asset.current_value, asset.purchase_date,
                 asset.purchase_source, asset.storage_location, asset.notes,
                 asset.status, asset.updated_at, asset.uuid)
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete(self, uuid: str) -> bool:
        """Delete asset by UUID.
        
        Args:
            uuid: UUID of asset to delete
            
        Returns:
            bool: True if asset was deleted, False if not found
        """
        with self.db.connect() as conn:
            cursor = conn.execute(
                "DELETE FROM assets WHERE uuid = ?",
                (uuid,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def save(self, asset: Asset) -> str:
        """Save asset (add if new, update if exists).
        
        Automatically detects whether to insert or update based on UUID.
        
        Args:
            asset: Asset object to save
            
        Returns:
            str: UUID of saved asset
        """
        if self.exists(asset.uuid):
            self.update(asset)
        else:
            self.add(asset)
        return asset.uuid

    # Backward compatibility
    def all(self) -> list:
        """Alias for get_all() for backward compatibility.
        
        Returns:
            list: List of all Asset objects
        """
        return self.get_all()
