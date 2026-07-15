from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


HealthStatusState = Literal['available', 'unavailable', 'error']


@dataclass(frozen=True, slots=True)
class HealthStatusViewModel:
    state: HealthStatusState
    status_text: str
    diagnostic_lines: tuple[str, ...]
    error_text: str | None = None


def build_health_status_view_model(
    *,
    status_text: str | None,
    diagnostic_lines: tuple[str, ...] = (),
    error_text: str | None = None,
) -> HealthStatusViewModel:
    if not isinstance(diagnostic_lines, tuple) or any(
        not isinstance(line, str) for line in diagnostic_lines
    ):
        raise TypeError('diagnostic_lines must be a tuple of text values')
    if any(not line for line in diagnostic_lines):
        raise ValueError('diagnostic_lines must not contain empty text')
    if status_text is not None and (
        not isinstance(status_text, str) or not status_text.strip()
    ):
        raise ValueError('status_text must be non-empty text or None')
    if error_text is not None and (
        not isinstance(error_text, str) or not error_text.strip()
    ):
        raise ValueError('error_text must be non-empty text or None')
    if status_text is None and error_text is not None:
        return HealthStatusViewModel(
            state='error',
            status_text='Health status unavailable',
            diagnostic_lines=diagnostic_lines,
            error_text=error_text,
        )
    if status_text is None:
        return HealthStatusViewModel(
            state='unavailable',
            status_text='Health status unavailable',
            diagnostic_lines=diagnostic_lines,
        )
    if error_text is not None:
        raise ValueError('error_text requires unavailable status evidence')
    return HealthStatusViewModel(
        state='available',
        status_text=status_text,
        diagnostic_lines=diagnostic_lines,
    )
