from __future__ import annotations

from collections.abc import Iterable

from .record import LogLevel, LogRecord, validate_log_record

_LEVEL_ORDER = {
    LogLevel.DEBUG: 10,
    LogLevel.INFO: 20,
    LogLevel.WARNING: 30,
    LogLevel.ERROR: 40,
    LogLevel.CRITICAL: 50,
}


def records_at_or_above(
    records: Iterable[LogRecord],
    threshold: LogLevel,
) -> tuple[LogRecord, ...]:
    """Return records meeting a severity threshold in original order."""

    if not isinstance(threshold, LogLevel):
        raise TypeError('threshold must be a LogLevel')

    selected: list[LogRecord] = []
    for record in records:
        validate_log_record(record)
        if _LEVEL_ORDER[record.level] >= _LEVEL_ORDER[threshold]:
            selected.append(record)
    return tuple(selected)
