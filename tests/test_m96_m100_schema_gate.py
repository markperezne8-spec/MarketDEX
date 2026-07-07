import sqlite3
import pytest
from services.executive_evolution_cycle_service import ExecutiveEvolutionCycleService


def test_m96_m100_schema_initializes_and_is_append_only(tmp_path):
    service = ExecutiveEvolutionCycleService(tmp_path / 'm100.sqlite3')
    with service.database.transaction() as connection:
        connection.execute(
            '''INSERT INTO executive_evolution_cycles_history(
                executive_evolution_cycle_id, executive_transformation_id,
                executive_evolution_cycle_id_event_id,
                executive_evolution_cycle_result, recorded_at
            ) VALUES (?, ?, ?, ?, ?)''',
            ('cycle-1', 'transformation-1', 'event-1', 'EXECUTIVE_EVOLUTION_CYCLE_READY', '2026-07-07T00:00:00Z'),
        )
    with pytest.raises(sqlite3.IntegrityError):
        with service.database.transaction() as connection:
            connection.execute('DELETE FROM executive_evolution_cycles_history WHERE executive_evolution_cycle_id=?', ('cycle-1',))
