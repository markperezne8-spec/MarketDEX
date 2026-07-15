from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


OperationalStatusState = Literal['available', 'unavailable', 'partial', 'error']
OperationalStatusGroupKey = Literal[
    'local_authority',
    'offline_first',
    'inventory',
    'audit_authority',
]

OPERATIONAL_STATUS_GROUP_ORDER: tuple[OperationalStatusGroupKey, ...] = (
    'local_authority',
    'offline_first',
    'inventory',
    'audit_authority',
)

OPERATIONAL_STATUS_GROUP_LABELS: dict[OperationalStatusGroupKey, str] = {
    'local_authority': 'Local authority',
    'offline_first': 'Offline-first',
    'inventory': 'Inventory readiness',
    'audit_authority': 'Audit/authority evidence',
}

UNAVAILABLE_DETAIL = 'Evidence unavailable.'


@dataclass(frozen=True, slots=True)
class OperationalStatusEvidence:
    group: OperationalStatusGroupKey
    state: OperationalStatusState
    label: str
    detail: str


@dataclass(frozen=True, slots=True)
class OperationalStatusViewModel:
    state: OperationalStatusState
    headline: str
    groups: tuple[OperationalStatusEvidence, ...]
    error_text: str | None = None


def build_operational_status_view_model(
    *,
    evidence: tuple[OperationalStatusEvidence, ...] = (),
    error_text: str | None = None,
) -> OperationalStatusViewModel:
    _validate_evidence_tuple(evidence)
    _validate_error_text(error_text)

    groups_by_key = {item.group: item for item in evidence}
    if len(groups_by_key) != len(evidence):
        raise ValueError('evidence must contain each operational group at most once')

    ordered_groups = tuple(
        groups_by_key.get(group)
        or OperationalStatusEvidence(
            group=group,
            state='unavailable',
            label=OPERATIONAL_STATUS_GROUP_LABELS[group],
            detail=UNAVAILABLE_DETAIL,
        )
        for group in OPERATIONAL_STATUS_GROUP_ORDER
    )

    if error_text is not None:
        return OperationalStatusViewModel(
            state='error',
            headline='Operational status unavailable',
            groups=ordered_groups,
            error_text=error_text,
        )

    if not evidence:
        return OperationalStatusViewModel(
            state='unavailable',
            headline='Operational status unavailable',
            groups=ordered_groups,
        )

    if any(group.state in ('unavailable', 'partial') for group in ordered_groups):
        return OperationalStatusViewModel(
            state='partial',
            headline='Operational status partially available',
            groups=ordered_groups,
        )

    return OperationalStatusViewModel(
        state='available',
        headline='Operational status ready',
        groups=ordered_groups,
    )


def operational_status_evidence(
    group: OperationalStatusGroupKey,
    *,
    state: OperationalStatusState,
    detail: str,
    label: str | None = None,
) -> OperationalStatusEvidence:
    if group not in OPERATIONAL_STATUS_GROUP_ORDER:
        raise ValueError('group must be a supported operational status group')
    _validate_state(state)
    _validate_text(detail, 'detail')
    if label is None:
        label = OPERATIONAL_STATUS_GROUP_LABELS[group]
    else:
        _validate_text(label, 'label')
    return OperationalStatusEvidence(
        group=group,
        state=state,
        label=label,
        detail=detail,
    )


def _validate_evidence_tuple(
    evidence: tuple[OperationalStatusEvidence, ...],
) -> None:
    if not isinstance(evidence, tuple) or any(
        not isinstance(item, OperationalStatusEvidence) for item in evidence
    ):
        raise TypeError(
            'evidence must be a tuple of OperationalStatusEvidence values'
        )
    for item in evidence:
        if item.group not in OPERATIONAL_STATUS_GROUP_ORDER:
            raise ValueError('evidence contains an unsupported group')
        _validate_state(item.state)
        _validate_text(item.label, 'label')
        _validate_text(item.detail, 'detail')


def _validate_error_text(error_text: str | None) -> None:
    if error_text is not None:
        _validate_text(error_text, 'error_text')


def _validate_state(state: str) -> None:
    if state not in ('available', 'unavailable', 'partial', 'error'):
        raise ValueError('state must be available, unavailable, partial, or error')


def _validate_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field_name} must be non-empty text')
