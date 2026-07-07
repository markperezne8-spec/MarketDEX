import sqlite3
import pytest
from services.executive_feedback_loop_service import ExecutiveFeedbackLoopService


def test_m86_m90_schema_initializes_and_is_append_only(tmp_path):
    service = ExecutiveFeedbackLoopService(tmp_path / 'm90.sqlite3')
    with pytest.raises(sqlite3.IntegrityError):
        with service.database.transaction() as connection:
            connection.execute('DELETE FROM executive_feedback_loops_history')
