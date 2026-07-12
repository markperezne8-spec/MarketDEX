from dataclasses import dataclass
from pathlib import Path

from core.database_manager import DatabaseManager
from services.product_registry_service import norm


@dataclass(frozen=True)
class ProductRegistryLookupResult:
    product_id: str
    product_type: str
    canonical_name: str
    set_name: str | None
    card_number: str | None
    variant_name: str | None
    state: str
    matched_by: str


class ProductRegistryLookupService:
    """Read-only operator lookup over canonical Product Registry authority."""

    def __init__(self, path):
        self.path = Path(path)
        self.database = DatabaseManager(self.path)
        self.database.initialize()

    @staticmethod
    def _result(row, matched_by):
        return ProductRegistryLookupResult(
            product_id=row['product_id'],
            product_type=row['product_type'],
            canonical_name=row['canonical_name'],
            set_name=row['set_name'],
            card_number=row['card_number'],
            variant_name=row['variant_name'],
            state=row['state'],
            matched_by=matched_by,
        )

    def by_product_id(self, product_id):
        value = str(product_id or '').strip()
        if not value:
            return None
        with self.database.read_connection() as connection:
            row = connection.execute(
                'SELECT * FROM products WHERE product_id=?', (value,)
            ).fetchone()
            return self._result(row, 'PRODUCT_ID') if row else None

    def search(self, query, *, product_type=None, limit=50):
        term = norm(query)
        if not term:
            return ()
        normalized_type = str(product_type or '').strip().upper() or None
        if normalized_type not in (None, 'SINGLE', 'SEALED'):
            raise ValueError('unsupported product_type filter')
        try:
            result_limit = int(limit)
        except (TypeError, ValueError) as exc:
            raise ValueError('limit must be an integer') from exc
        if result_limit < 1 or result_limit > 200:
            raise ValueError('limit must be between 1 and 200')

        like = f'%{term}%'
        with self.database.read_connection() as connection:
            rows = connection.execute(
                '''
                SELECT DISTINCT
                    p.*,
                    CASE
                        WHEN lower(p.product_id)=? THEN 'PRODUCT_ID'
                        WHEN a.normalized_alias_key=? THEN 'ALIAS'
                        WHEN lower(p.card_number)=? THEN 'CARD_NUMBER'
                        WHEN lower(p.canonical_name)=? THEN 'CANONICAL_NAME'
                        ELSE 'FIELDS'
                    END AS matched_by
                FROM products p
                LEFT JOIN product_aliases a ON a.product_id=p.product_id
                WHERE (? IS NULL OR p.product_type=?)
                  AND (
                    lower(p.product_id)=?
                    OR p.normalized_identity_key LIKE ?
                    OR a.normalized_alias_key LIKE ?
                    OR lower(COALESCE(p.set_name,'')) LIKE ?
                    OR lower(COALESCE(p.card_number,'')) LIKE ?
                    OR lower(COALESCE(p.variant_name,'')) LIKE ?
                  )
                ORDER BY p.canonical_name COLLATE NOCASE, p.product_id
                LIMIT ?
                ''',
                (
                    term, term, term, term,
                    normalized_type, normalized_type,
                    term, like, like, like, like, like,
                    result_limit,
                ),
            ).fetchall()
            return tuple(self._result(row, row['matched_by']) for row in rows)
