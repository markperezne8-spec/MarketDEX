import sqlite3
import pytest
from services.executive_transparency_cycle_service import ExecutiveTransparencyCycleService

def test_m156_m160_schema_initializes_and_is_append_only(tmp_path):
 service=ExecutiveTransparencyCycleService(tmp_path/'m160.sqlite3')
 expected=('executive_accountability_observations','executive_transparency_reconstructions','executive_disclosure_authorities','executive_visibility_authorities','executive_transparency_cycles')
 with service.database.read_connection() as c:
  tables={r['name'] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
 assert all(t in tables and f'{t}_history' in tables for t in expected)
 with service.database.transaction() as c:
  c.execute('INSERT INTO executive_transparency_cycles_history(executive_transparency_cycle_id,executive_visibility_id,executive_transparency_cycle_id_event_id,executive_transparency_cycle_result,recorded_at) VALUES (?,?,?,?,?)',('cycle-1','visibility-1','event-1','EXECUTIVE_TRANSPARENCY_CYCLE_READY','2026-07-07T00:00:00Z'))
 with pytest.raises(sqlite3.IntegrityError):
  with service.database.transaction() as c: c.execute('DELETE FROM executive_transparency_cycles_history WHERE executive_transparency_cycle_id=?',('cycle-1',))
 with pytest.raises(sqlite3.IntegrityError):
  with service.database.transaction() as c: c.execute("UPDATE executive_transparency_cycles_history SET executive_transparency_cycle_result='ALTERED' WHERE executive_transparency_cycle_id=?",('cycle-1',))
