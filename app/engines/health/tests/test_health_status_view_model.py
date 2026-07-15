from dataclasses import FrozenInstanceError

import pytest

from app.engines.health.status_view_model import (
    HealthStatusViewModel,
    build_health_status_view_model,
)


def test_build_health_status_view_model_preserves_available_status_and_order() -> None:
    model = build_health_status_view_model(
        status_text='Health ready',
        diagnostic_lines=('runtime=MarketDEX', 'overall=PASS', 'providers=2'),
    )

    assert model == HealthStatusViewModel(
        state='available',
        status_text='Health ready',
        diagnostic_lines=('runtime=MarketDEX', 'overall=PASS', 'providers=2'),
    )


def test_build_health_status_view_model_has_deterministic_unavailable_state() -> None:
    assert build_health_status_view_model(status_text=None) == HealthStatusViewModel(
        state='unavailable',
        status_text='Health status unavailable',
        diagnostic_lines=(),
    )


def test_build_health_status_view_model_has_error_safe_state() -> None:
    assert build_health_status_view_model(
        status_text=None,
        diagnostic_lines=('registration=desktop-health',),
        error_text='Health evidence unavailable',
    ) == HealthStatusViewModel(
        state='error',
        status_text='Health status unavailable',
        diagnostic_lines=('registration=desktop-health',),
        error_text='Health evidence unavailable',
    )


def test_health_status_view_model_is_immutable() -> None:
    model = build_health_status_view_model(status_text='Health ready')

    with pytest.raises(FrozenInstanceError):
        model.status_text = 'Changed'


@pytest.mark.parametrize(
    ('kwargs', 'exception'),
    [
        ({'status_text': 'Ready', 'diagnostic_lines': ['not', 'a', 'tuple']}, TypeError),
        ({'status_text': 'Ready', 'diagnostic_lines': ('',)}, ValueError),
        ({'status_text': '  '}, ValueError),
        ({'status_text': None, 'error_text': '  '}, ValueError),
        ({'status_text': 'Ready', 'error_text': 'unexpected'}, ValueError),
    ],
)
def test_build_health_status_view_model_rejects_invalid_input(kwargs, exception) -> None:
    with pytest.raises(exception):
        build_health_status_view_model(**kwargs)
