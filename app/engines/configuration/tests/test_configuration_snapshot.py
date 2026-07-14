from collections import UserDict

from app.engines.configuration.snapshot import (
    ConfigurationSnapshot,
    build_default_snapshot,
)


def test_default_snapshot_is_valid_and_independent() -> None:
    first = build_default_snapshot()
    second = build_default_snapshot()

    assert isinstance(first, ConfigurationSnapshot)
    assert first.get('version') == 1
    assert first.values is not second.values
    assert first.get('recent_projects') == ()


def test_snapshot_rejects_invalid_window() -> None:
    config = build_default_snapshot().values
    invalid = dict(config)
    invalid['window'] = dict(config['window'])
    invalid['window']['width'] = 0

    try:
        ConfigurationSnapshot(invalid)
    except ValueError as exc:
        assert 'invalid' in str(exc)
    else:
        raise AssertionError('invalid configuration was accepted')


def test_snapshot_is_immutable() -> None:
    snapshot = build_default_snapshot()

    try:
        snapshot.values['version'] = 2
    except TypeError:
        pass
    else:
        raise AssertionError('snapshot mapping was mutable')


def test_snapshot_freezes_nested_mapping_values() -> None:
    source = dict(build_default_snapshot().values)
    source['window'] = UserDict(dict(source['window']))

    snapshot = ConfigurationSnapshot(source)

    assert type(snapshot.get('window')).__name__ == 'mappingproxy'
    try:
        snapshot.get('window')['width'] = 1280
    except TypeError:
        pass
    else:
        raise AssertionError('nested mapping was mutable')
