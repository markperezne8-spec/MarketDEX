import json

import pytest

from app.engines.logging import LogLevel, LogRecord, format_log_record


def test_log_record_is_immutable_and_normalizes_details() -> None:
    details = {'attempt': 1}
    record = LogRecord(
        timestamp='2026-07-14T21:00:00Z',
        level=LogLevel.INFO,
        component='configuration',
        event='snapshot_created',
        message='Configuration snapshot created',
        details=details,
    )

    details['attempt'] = 2

    assert record.details['attempt'] == 1
    with pytest.raises(TypeError):
        record.details['attempt'] = 3


def test_log_record_rejects_missing_required_values() -> None:
    with pytest.raises(ValueError):
        LogRecord('', LogLevel.ERROR, 'app', 'failure', 'failed')


def test_log_record_rejects_invalid_level() -> None:
    with pytest.raises(TypeError):
        LogRecord('2026-07-14T21:00:00Z', 'INFO', 'app', 'event', 'message')


def test_format_log_record_is_deterministic() -> None:
    record = LogRecord(
        timestamp='2026-07-14T21:00:00Z',
        level=LogLevel.WARNING,
        component='app',
        event='retry',
        message='Retry requested',
        correlation_id='op-1',
        details={'z': 2, 'a': 1},
    )

    formatted = format_log_record(record)

    assert formatted == json.dumps({
        'timestamp': '2026-07-14T21:00:00Z',
        'level': 'WARNING',
        'component': 'app',
        'event': 'retry',
        'message': 'Retry requested',
        'correlation_id': 'op-1',
        'details': {'z': 2, 'a': 1},
    }, sort_keys=True, separators=(',', ':'))
