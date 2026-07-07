import sqlite3
import pytest
from services.executive_learning_cycle_service import ExecutiveLearningCycleService


def test_m91_m95_schema_initializes_and_is_append_only(tmp_path):
    service = ExecutiveLearningCycleService(tmp_path / 'm95.sqlite3')
    with service.database.transaction() as connection:
        connection.execute(
            '''INSERT INTO executive_learning_cycles_history(
                executive_learning_cycle_id, executive_adaptation_id,
                executive_learning_cycle_id_event_id,
                executive_learning_cycle_result, recorded_at
            ) VALUES (?, ?, ?, ?, ?)''',
            ('cycle-1', 'adaptation-1', 'event-1', 'EXECUTIVE_LEARNING_CYCLE_READY', '2026-07-07T00:00:00Z'),
        )
    with pytest.raises(sqlite3.IntegrityError):
        with service.database.transaction() as connection:
            connection.execute('DELETE FROM executive_learning_cycles_history WHERE executive_learning_cycle_id=?', ('cycle-1',))
