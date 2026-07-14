import json

from app.engines.logging import LogLevel, LogRecord, format_log_record, sanitize_details


def test_sanitize_details_redacts_sensitive_keys_recursively() -> None:
    details = {
        'attempt': 1,
        'api_key': 'do-not-print',
        'nested': {'authorization': 'Bearer secret', 'status': 'retrying'},
        'items': [{'password': 'hidden', 'count': 2}],
    }

    sanitized = sanitize_details(details)

    assert sanitized == {
        'attempt': 1,
        'api_key': '[REDACTED]',
        'nested': {'authorization': '[REDACTED]', 'status': 'retrying'},
        'items': [{'password': '[REDACTED]', 'count': 2}],
    }
    assert details['api_key'] == 'do-not-print'


def test_format_log_record_redacts_sensitive_details() -> None:
    record = LogRecord(
        timestamp='2026-07-14T21:00:00Z',
        level=LogLevel.ERROR,
        component='app',
        event='request_failed',
        message='Request failed',
        details={'token': 'hidden', 'retryable': True},
    )

    payload = json.loads(format_log_record(record))

    assert payload['details'] == {'retryable': True, 'token': '[REDACTED]'}
