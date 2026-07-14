import json

from app.engines.logging import LogLevel, LogRecord, format_log_records


def make_record(event: str) -> LogRecord:
    return LogRecord(
        timestamp='2026-07-14T21:00:00Z',
        level=LogLevel.INFO,
        component='app',
        event=event,
        message=event,
    )


def test_format_log_records_preserves_order_and_line_boundaries() -> None:
    formatted = format_log_records([make_record('first'), make_record('second')])

    lines = formatted.splitlines()

    assert [json.loads(line)['event'] for line in lines] == ['first', 'second']


def test_format_log_records_empty_batch_is_empty() -> None:
    assert format_log_records([]) == ''
