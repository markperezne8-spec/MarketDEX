import os
import tempfile
import unittest
from pathlib import Path

from core.database_manager import DatabaseManager


class SchemaAuthorityRegressionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="marketdex_schema_", dir=".")
        self.path = Path(self.tmp) / "schema_regression.sqlite3"
        self.db = DatabaseManager(self.path)
        self.db.initialize()

    def tearDown(self):
        try:
            self.db.connect().close()
        except Exception:
            pass
        for suffix in ["", "-shm", "-wal"]:
            try:
                (self.path if not suffix else self.path.with_suffix(self.path.suffix + suffix)).unlink(missing_ok=True)
            except Exception:
                pass
        try:
            os.rmdir(self.tmp)
        except Exception:
            pass

    def test_m36_inventory_reconciliation_authority_restored(self):
        with self.db.connect() as c:
            tables = {
                row[0]
                for row in c.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('inventory_movements','inventory_adjustments','inventory_reconciliations','reconciliation_history')"
                )
            }
            self.assertEqual(
                tables,
                {"inventory_movements", "inventory_adjustments", "inventory_reconciliations", "reconciliation_history"},
            )

            triggers = {
                row[0]
                for row in c.execute(
                    "SELECT name FROM sqlite_master WHERE type='trigger' AND name LIKE 'inventory_%'"
                )
            }
            self.assertTrue({"inventory_adjustments_no_update", "inventory_movements_no_update", "inventory_reconciliations_no_update"}.issubset(triggers))

    def test_schema_version_is_m36_authority_level(self):
        with self.db.connect() as c:
            row = c.execute("SELECT schema_version FROM schema_metadata ORDER BY rowid DESC LIMIT 1").fetchone()
            if row is None:
                self.assertEqual(c.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='schema_metadata'").fetchone()[0], 1)
                self.assertEqual(c.execute("SELECT COUNT(*) FROM schema_metadata").fetchone()[0], 0)
            else:
                self.assertEqual(row[0], 12)


if __name__ == "__main__":
    unittest.main()
