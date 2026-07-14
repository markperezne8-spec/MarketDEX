import pytest

from app.engines.logging import LogLevel, LogRecord


def make_record(**overrides: object) -> LogRecord:
    values: dict[str, object] = {
        'timestamp': '2026-07-14T21:00:00Z',
        'level': LogLevel.INFO,
        'component': 'app',
        'event': 'started',
        'message': 'Application started',
    }
    values.update(overrides)
    return LogRecord(**values)


@pytest.mark.parametrize('field', ['timestamp', 'component', 'event', 'message'])
def test_record_rejects_whitespace_only_required_text(field: str) -> None:
    with pytest.raises(ValueError):
        make_record(**{field: '   '})


def test_record_rejects_whitespace_only_correlation_id() -> None:
    with pytest.raises(ValueError):
        make_record(correlation_id='  ')


def test_record_rejects_empty_detail_key() -> None:
    with pytest.raises(ValueError):
        make_record(details={'': 'value'})
