from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


HeaderStatusState = Literal['ready', 'unavailable', 'partial', 'error']
HeaderStatusSlotKey = Literal[
    'operating_context',
    'app_status',
    'data_freshness',
    'workbook_health',
    'local_authority',
]

HEADER_STATUS_SLOT_ORDER: tuple[HeaderStatusSlotKey, ...] = (
    'operating_context',
    'app_status',
    'data_freshness',
    'workbook_health',
    'local_authority',
)

HEADER_STATUS_SLOT_LABELS: dict[HeaderStatusSlotKey, str] = {
    'operating_context': 'Operating context',
    'app_status': 'App/offline status',
    'data_freshness': 'Data freshness',
    'workbook_health': 'Workbook health',
    'local_authority': 'Local authority',
}

UNAVAILABLE_DETAIL = 'Evidence unavailable.'


@dataclass(frozen=True, slots=True)
class HeaderStatusEvidence:
    slot: HeaderStatusSlotKey
    state: HeaderStatusState
    label: str
    detail: str


@dataclass(frozen=True, slots=True)
class HeaderStatusViewModel:
    state: HeaderStatusState
    headline: str
    slots: tuple[HeaderStatusEvidence, ...]
    error_text: str | None = None


def build_header_status_view_model(
    *,
    evidence: tuple[HeaderStatusEvidence, ...] = (),
    error_text: str | None = None,
) -> HeaderStatusViewModel:
    _validate_evidence_tuple(evidence)
    _validate_error_text(error_text)

    slots_by_key = {item.slot: item for item in evidence}
    if len(slots_by_key) != len(evidence):
        raise ValueError('evidence must contain each header status slot at most once')

    ordered_slots = tuple(
        slots_by_key.get(slot)
        or HeaderStatusEvidence(
            slot=slot,
            state='unavailable',
            label=HEADER_STATUS_SLOT_LABELS[slot],
            detail=UNAVAILABLE_DETAIL,
        )
        for slot in HEADER_STATUS_SLOT_ORDER
    )

    if error_text is not None:
        return HeaderStatusViewModel(
            state='error',
            headline='Header status unavailable',
            slots=ordered_slots,
            error_text=error_text,
        )

    if not evidence:
        return HeaderStatusViewModel(
            state='unavailable',
            headline='Header status unavailable',
            slots=ordered_slots,
        )

    if any(slot.state in ('unavailable', 'partial') for slot in ordered_slots):
        return HeaderStatusViewModel(
            state='partial',
            headline='Header status partially available',
            slots=ordered_slots,
        )

    return HeaderStatusViewModel(
        state='ready',
        headline='Header status ready',
        slots=ordered_slots,
    )


def header_status_evidence(
    slot: HeaderStatusSlotKey,
    *,
    state: HeaderStatusState,
    detail: str,
    label: str | None = None,
) -> HeaderStatusEvidence:
    if slot not in HEADER_STATUS_SLOT_ORDER:
        raise ValueError('slot must be a supported header status slot')
    _validate_state(state)
    _validate_text(detail, 'detail')
    if label is None:
        label = HEADER_STATUS_SLOT_LABELS[slot]
    else:
        _validate_text(label, 'label')
    return HeaderStatusEvidence(
        slot=slot,
        state=state,
        label=label,
        detail=detail,
    )


def _validate_evidence_tuple(evidence: tuple[HeaderStatusEvidence, ...]) -> None:
    if not isinstance(evidence, tuple) or any(
        not isinstance(item, HeaderStatusEvidence) for item in evidence
    ):
        raise TypeError('evidence must be a tuple of HeaderStatusEvidence values')
    for item in evidence:
        if item.slot not in HEADER_STATUS_SLOT_ORDER:
            raise ValueError('evidence contains an unsupported slot')
        _validate_state(item.state)
        _validate_text(item.label, 'label')
        _validate_text(item.detail, 'detail')


def _validate_error_text(error_text: str | None) -> None:
    if error_text is not None:
        _validate_text(error_text, 'error_text')


def _validate_state(state: str) -> None:
    if state not in ('ready', 'unavailable', 'partial', 'error'):
        raise ValueError('state must be ready, unavailable, partial, or error')


def _validate_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field_name} must be non-empty text')
