from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


NextStepReadinessState = Literal['ready', 'unavailable', 'partial', 'error']
NextStepReadinessGroupKey = Literal[
    'next_safe_action',
    'inventory_readiness',
    'authority_audit_readiness',
    'readiness_note',
]

NEXT_STEP_READINESS_GROUP_ORDER: tuple[NextStepReadinessGroupKey, ...] = (
    'next_safe_action',
    'inventory_readiness',
    'authority_audit_readiness',
    'readiness_note',
)

NEXT_STEP_READINESS_GROUP_LABELS: dict[NextStepReadinessGroupKey, str] = {
    'next_safe_action': 'Next safe action',
    'inventory_readiness': 'Inventory readiness',
    'authority_audit_readiness': 'Authority/audit readiness',
    'readiness_note': 'Readiness note',
}

UNAVAILABLE_DETAIL = 'Evidence unavailable.'


@dataclass(frozen=True, slots=True)
class NextStepReadinessEvidence:
    group: NextStepReadinessGroupKey
    state: NextStepReadinessState
    label: str
    detail: str


@dataclass(frozen=True, slots=True)
class NextStepReadinessViewModel:
    state: NextStepReadinessState
    headline: str
    groups: tuple[NextStepReadinessEvidence, ...]
    error_text: str | None = None


def build_next_step_readiness_view_model(
    *,
    evidence: tuple[NextStepReadinessEvidence, ...] = (),
    error_text: str | None = None,
) -> NextStepReadinessViewModel:
    _validate_evidence_tuple(evidence)
    _validate_error_text(error_text)

    groups_by_key = {item.group: item for item in evidence}
    if len(groups_by_key) != len(evidence):
        raise ValueError('evidence must contain each readiness group at most once')

    ordered_groups = tuple(
        groups_by_key.get(group)
        or NextStepReadinessEvidence(
            group=group,
            state='unavailable',
            label=NEXT_STEP_READINESS_GROUP_LABELS[group],
            detail=UNAVAILABLE_DETAIL,
        )
        for group in NEXT_STEP_READINESS_GROUP_ORDER
    )

    if error_text is not None:
        return NextStepReadinessViewModel(
            state='error',
            headline='Action readiness unavailable',
            groups=ordered_groups,
            error_text=error_text,
        )

    if not evidence:
        return NextStepReadinessViewModel(
            state='unavailable',
            headline='Action readiness unavailable',
            groups=ordered_groups,
        )

    if any(group.state in ('unavailable', 'partial') for group in ordered_groups):
        return NextStepReadinessViewModel(
            state='partial',
            headline='Action readiness partially available',
            groups=ordered_groups,
        )

    return NextStepReadinessViewModel(
        state='ready',
        headline='Action readiness ready',
        groups=ordered_groups,
    )


def next_step_readiness_evidence(
    group: NextStepReadinessGroupKey,
    *,
    state: NextStepReadinessState,
    detail: str,
    label: str | None = None,
) -> NextStepReadinessEvidence:
    if group not in NEXT_STEP_READINESS_GROUP_ORDER:
        raise ValueError('group must be a supported next step readiness group')
    _validate_state(state)
    _validate_text(detail, 'detail')
    if label is None:
        label = NEXT_STEP_READINESS_GROUP_LABELS[group]
    else:
        _validate_text(label, 'label')
    return NextStepReadinessEvidence(
        group=group,
        state=state,
        label=label,
        detail=detail,
    )


def _validate_evidence_tuple(
    evidence: tuple[NextStepReadinessEvidence, ...],
) -> None:
    if not isinstance(evidence, tuple) or any(
        not isinstance(item, NextStepReadinessEvidence) for item in evidence
    ):
        raise TypeError(
            'evidence must be a tuple of NextStepReadinessEvidence values'
        )
    for item in evidence:
        if item.group not in NEXT_STEP_READINESS_GROUP_ORDER:
            raise ValueError('evidence contains an unsupported group')
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
