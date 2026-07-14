import json

from app.engines.logging import LogLevel, LogRecord, format_records_at_or_above


def make_record(level: LogLevel, event: str) -> LogRecord:
    return LogRecord(
        timestamp='2026-07-14T21:00:00Z',
        level=level,
        component='app',
        event=event,
        message=event,
    )


def test_format_records_at_or_above_composes_filter_and_formatter() -> None:
    formatted = format_records_at_or_above([
        make_record(LogLevel.INFO, 'info'),
        make_record(LogLevel.ERROR, 'error'),
        make_record(LogLevel.DEBUG, 'debug'),
    ], LogLevel.ERROR)

    assert [json.loads(line)['event'] for line in formatted.splitlines()] == ['error']


def test_format_records_at_or_above_returns_empty_for_no_matches() -> None:
    assert format_records_at_or_above([make_record(LogLevel.INFO, 'info')], LogLevel.ERROR) == ''
