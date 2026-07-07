import sqlite3
import pytest
from services.executive_feedback_loop_service import ExecutiveFeedbackLoopService


def test_m86_m90_schema_initializes_and_is_append_only(tmp_path):
    service = ExecutiveFeedbackLoopService(tmp_path / 'm90.sqlite3')
    with service.database.transaction() as connection:
        connection.execute(
            '''INSERT INTO executive_feedback_loops_history(
                executive_feedback_loop_id,
                executive_response_id,
                executive_feedback_loop_event_id,
                executive_feedback_loop_result,
                recorded_at
            ) VALUES (?, ?, ?, ?, ?)''',
            ('loop-1', 'response-1', 'event-1', 'EXECUTIVE_FEEDBACK_LOOP_READY', '2026-07-07T00:00:00Z'),
        )
    with pytest.raises(sqlite3.IntegrityError):
        with service.database.transaction() as connection:
            connection.execute(
                'DELETE FROM executive_feedback_loops_history WHERE executive_feedback_loop_id=?',
                ('loop-1',),
            )
