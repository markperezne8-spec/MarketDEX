from app.engines.configuration.materialize import materialize_configuration
from app.engines.configuration.snapshot import build_default_snapshot


def test_materialization_returns_detached_mutable_values() -> None:
    snapshot = build_default_snapshot()
    values = materialize_configuration(snapshot)

    assert values is not snapshot.values
    assert isinstance(values, dict)
    assert isinstance(values['recent_projects'], list)
    values['window']['width'] = 1280
    values['recent_projects'].append('demo')

    assert snapshot.get('window')['width'] == 1600
    assert snapshot.get('recent_projects') == ()
