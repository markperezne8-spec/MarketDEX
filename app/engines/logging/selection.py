from __future__ import annotations

from collections.abc import Iterable

from .filtering import records_at_or_above
from .formatting import format_log_records
from .record import LogLevel, LogRecord


def format_records_at_or_above(
    records: Iterable[LogRecord],
    threshold: LogLevel,
) -> str:
    """Filter records by severity, then format the retained batch."""

    return format_log_records(records_at_or_above(records, threshold))
