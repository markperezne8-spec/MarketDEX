from types import MappingProxyType

from app.engines.configuration.overlay import overlay_configuration
from app.engines.configuration.snapshot import build_default_snapshot


def test_overlay_preserves_nested_defaults_and_returns_new_snapshot() -> None:
    base = build_default_snapshot()
    updated = overlay_configuration(
        base,
        {'window': {'width': 1280}, 'theme': {'mode': 'dark'}},
    )

    assert updated is not base
    assert updated.get('window')['width'] == 1280
    assert updated.get('window')['height'] == 900
    assert updated.get('theme')['mode'] == 'dark'
    assert base.get('window')['width'] == 1600


def test_overlay_rejects_invalid_result() -> None:
    base = build_default_snapshot()
    try:
        overlay_configuration(base, {'window': {'width': 0}})
    except ValueError:
        pass
    else:
        raise AssertionError('invalid overlay was accepted')


def test_overlay_merges_mapping_proxy_values() -> None:
    base = build_default_snapshot()
    overlay = MappingProxyType({'window': MappingProxyType({'width': 1280})})

    updated = overlay_configuration(base, overlay)

    assert updated.get('window')['width'] == 1280
    assert updated.get('window')['height'] == 900
