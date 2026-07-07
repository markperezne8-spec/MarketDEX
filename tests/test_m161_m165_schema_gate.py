import sqlite3
import pytest
from services.executive_integrity_cycle_service import ExecutiveIntegrityCycleService

def test_m161_m165_schema_initializes_and_is_append_only(tmp_path):
 service=ExecutiveIntegrityCycleService(tmp_path/'m165.sqlite3'); expected=('executive_transparency_observations','executive_integrity_reconstructions','executive_ethical_authorities','executive_fidelity_authorities','executive_integrity_cycles')
 with service.database.read_connection() as c: tables={r['name'] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
 assert all(t in tables and f'{t}_history' in tables for t in expected)
 with service.database.transaction() as c: c.execute('INSERT INTO executive_integrity_cycles_history(executive_integrity_cycle_id,executive_fidelity_id,executive_integrity_cycle_id_event_id,executive_integrity_cycle_result,recorded_at) VALUES (?,?,?,?,?)',('cycle-1','fidelity-1','event-1','EXECUTIVE_INTEGRITY_CYCLE_READY','2026-07-07T00:00:00Z'))
 with pytest.raises(sqlite3.IntegrityError):
  with service.database.transaction() as c: c.execute('DELETE FROM executive_integrity_cycles_history WHERE executive_integrity_cycle_id=?',('cycle-1',))
 with pytest.raises(sqlite3.IntegrityError):
  with service.database.transaction() as c: c.execute("UPDATE executive_integrity_cycles_history SET executive_integrity_cycle_result='ALTERED' WHERE executive_integrity_cycle_id=?",('cycle-1',))
