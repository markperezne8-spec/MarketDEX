import sqlite3
import pytest
from services.executive_legitimacy_cycle_service import ExecutiveLegitimacyCycleService

def test_m141_m145_schema_initializes_and_is_append_only(tmp_path):
 service=ExecutiveLegitimacyCycleService(tmp_path/'m145.sqlite3')
 with service.database.transaction() as c:
  c.execute('INSERT INTO executive_legitimacy_cycles_history(executive_legitimacy_cycle_id,executive_trust_id,executive_legitimacy_cycle_id_event_id,executive_legitimacy_cycle_result,recorded_at) VALUES (?,?,?,?,?)',('cycle-1','trust-1','event-1','EXECUTIVE_LEGITIMACY_CYCLE_READY','2026-07-07T00:00:00Z'))
 with pytest.raises(sqlite3.IntegrityError):
  with service.database.transaction() as c: c.execute('DELETE FROM executive_legitimacy_cycles_history WHERE executive_legitimacy_cycle_id=?',('cycle-1',))
