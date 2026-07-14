from app.engines.logging import LogLevel, LogRecord, records_at_or_above


def make_record(level: LogLevel, event: str) -> LogRecord:
    return LogRecord(
        timestamp='2026-07-14T21:00:00Z',
        level=level,
        component='app',
        event=event,
        message=event,
    )


def test_records_at_or_above_threshold_preserves_order() -> None:
    records = [
        make_record(LogLevel.ERROR, 'error-first'),
        make_record(LogLevel.INFO, 'info'),
        make_record(LogLevel.CRITICAL, 'critical'),
        make_record(LogLevel.WARNING, 'warning'),
    ]

    selected = records_at_or_above(records, LogLevel.WARNING)

    assert [record.event for record in selected] == [
        'error-first',
        'critical',
        'warning',
    ]


def test_records_at_or_above_accepts_all_records_at_debug() -> None:
    records = [make_record(LogLevel.DEBUG, 'debug'), make_record(LogLevel.INFO, 'info')]

    assert records_at_or_above(records, LogLevel.DEBUG) == tuple(records)


def test_records_at_or_above_requires_log_level_threshold() -> None:
    try:
        records_at_or_above([], 'INFO')
    except TypeError as exc:
        assert 'LogLevel' in str(exc)
    else:
        raise AssertionError('invalid threshold was accepted')
