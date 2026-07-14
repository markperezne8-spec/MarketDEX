from __future__ import annotations

import json
from collections.abc import Iterable

from .record import LogRecord, validate_log_record
from .sanitizing import sanitize_details


def format_log_record(record: LogRecord) -> str:
    """Return deterministic, human-readable JSON for one diagnostic record."""

    validate_log_record(record)
    payload = {
        'timestamp': record.timestamp,
        'level': record.level.value,
        'component': record.component,
        'event': record.event,
        'message': record.message,
    }
    if record.correlation_id is not None:
        payload['correlation_id'] = record.correlation_id
    if record.details:
        payload['details'] = sanitize_details(record.details)
    return json.dumps(payload, sort_keys=True, separators=(',', ':'))


def format_log_records(records: Iterable[LogRecord]) -> str:
    """Format an ordered batch with one deterministic JSON record per line."""

    return '\n'.join(format_log_record(record) for record in records)
