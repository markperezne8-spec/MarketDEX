from dataclasses import dataclass
from pathlib import Path

from core.database_manager import DatabaseManager


@dataclass(frozen=True)
class CollectionPosition:
    """Read-only projection of an inventory asset held as a Collection position.

    Collection-specific classification is intentionally nullable until its
    authority contract is approved.  The projection never infers valuation,
    condition, grade, or collector intent from inventory data.
    """

    asset_id: str
    product_id: str
    canonical_name: str
    product_type: str
    quantity: int
    storage_location: str
    purchase_date: str
    purchase_source: str
    condition_grade: str | None
    collector_intent: str | None


class CollectionPositionService:
    """Deterministic, non-mutating Collection Position read model."""

    def __init__(self, path):
        self.path = Path(path)
        self.database = DatabaseManager(self.path)
        self.database.initialize()

    def list_positions(self, query: str = '', *, limit: int = 200) -> tuple[CollectionPosition, ...]:
        try:
            result_limit = int(limit)
        except (TypeError, ValueError) as exc:
            raise ValueError('limit must be an integer') from exc
        if result_limit < 1 or result_limit > 500:
            raise ValueError('limit must be between 1 and 500')

        term = str(query or '').strip().lower()
        like = f'%{term}%'
        with self.database.read_connection() as connection:
            rows = connection.execute(
                '''
                SELECT
                    a.asset_id,
                    p.product_id,
                    p.canonical_name,
                    p.product_type,
                    ia.quantity,
                    COALESCE(id.storage_location, '') AS storage_location,
                    COALESCE(id.purchase_date, '') AS purchase_date,
                    COALESCE(id.purchase_source, '') AS purchase_source
                FROM inventory_product_links l
                JOIN assets a ON a.asset_id = l.asset_id
                JOIN products p ON p.product_id = l.product_id
                JOIN inventory_authority ia ON ia.asset_id = a.asset_id
                LEFT JOIN inventory_business_details id ON id.asset_id = a.asset_id
                WHERE (? = '' OR lower(a.asset_id) LIKE ?
                    OR lower(p.product_id) LIKE ?
                    OR lower(p.canonical_name) LIKE ?
                    OR lower(COALESCE(id.storage_location, '')) LIKE ?)
                ORDER BY p.canonical_name COLLATE NOCASE, a.asset_id
                LIMIT ?
                ''',
                (term, like, like, like, like, result_limit),
            ).fetchall()
        return tuple(
            CollectionPosition(
                asset_id=row['asset_id'],
                product_id=row['product_id'],
                canonical_name=row['canonical_name'],
                product_type=row['product_type'],
                quantity=int(row['quantity']),
                storage_location=row['storage_location'],
                purchase_date=row['purchase_date'],
                purchase_source=row['purchase_source'],
                condition_grade=None,
                collector_intent=None,
            )
            for row in rows
        )
