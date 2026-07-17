from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


CapitalHealthState = Literal['ready', 'unavailable', 'partial', 'error']
CapitalHealthGroup = Literal['availability', 'recycling', 'commitment', 'growth']

CAPITAL_HEALTH_GROUP_ORDER: tuple[CapitalHealthGroup, ...] = (
    'availability',
    'recycling',
    'commitment',
    'growth',
)

CAPITAL_HEALTH_GROUP_TITLES: dict[CapitalHealthGroup, str] = {
    'availability': 'Availability',
    'recycling': 'Recycling',
    'commitment': 'Commitment',
    'growth': 'Growth',
}

UNAVAILABLE_TEXT = 'Evidence unavailable.'
UNAVAILABLE_SOURCE = 'Local evidence unavailable'
UNAVAILABLE_PERIOD = 'Period unavailable'


@dataclass(frozen=True, slots=True)
class CapitalHealthMetric:
    label: str
    state: CapitalHealthState
    value_label: str
    evidence_summary: str


@dataclass(frozen=True, slots=True)
class CapitalHealthGroupEvidence:
    group: CapitalHealthGroup
    state: CapitalHealthState
    title: str
    evidence_summary: str
    source_authority: str
    period_label: str
    explanation: str
    metrics: tuple[CapitalHealthMetric, ...]


@dataclass(frozen=True, slots=True)
class CapitalHealthViewModel:
    state: CapitalHealthState
    headline: str
    groups: tuple[CapitalHealthGroupEvidence, ...]
    error_text: str | None = None


def build_capital_health_view_model(
    *,
    evidence: tuple[CapitalHealthGroupEvidence, ...] = (),
    error_text: str | None = None,
) -> CapitalHealthViewModel:
    _validate_evidence_tuple(evidence)
    _validate_error_text(error_text)

    evidence_by_group = {item.group: item for item in evidence}
    if len(evidence_by_group) != len(evidence):
        raise ValueError('evidence must contain each Capital Health group at most once')

    ordered_groups = tuple(
        evidence_by_group.get(group) or _unavailable_group(group)
        for group in CAPITAL_HEALTH_GROUP_ORDER
    )

    if error_text is not None:
        return CapitalHealthViewModel(
            state='error',
            headline='Capital Health unavailable',
            groups=ordered_groups,
            error_text=error_text,
        )

    if not evidence:
        return CapitalHealthViewModel(
            state='unavailable',
            headline='Capital Health unavailable',
            groups=ordered_groups,
        )

    if any(_has_incomplete_state(group) for group in ordered_groups):
        return CapitalHealthViewModel(
            state='partial',
            headline='Capital Health partially available',
            groups=ordered_groups,
        )

    return CapitalHealthViewModel(
        state='ready',
        headline='Capital Health ready',
        groups=ordered_groups,
    )


def capital_health_group_evidence(
    group: CapitalHealthGroup,
    *,
    state: CapitalHealthState,
    evidence_summary: str,
    source_authority: str,
    period_label: str,
    explanation: str,
    metrics: tuple[CapitalHealthMetric, ...],
    title: str | None = None,
) -> CapitalHealthGroupEvidence:
    _validate_group(group)
    _validate_state(state)
    _validate_text(evidence_summary, 'evidence_summary')
    _validate_text(source_authority, 'source_authority')
    _validate_text(period_label, 'period_label')
    _validate_text(explanation, 'explanation')
    _validate_metrics_tuple(metrics)
    if title is not None:
        _validate_text(title, 'title')
    return CapitalHealthGroupEvidence(
        group=group,
        state=state,
        title=title or CAPITAL_HEALTH_GROUP_TITLES[group],
        evidence_summary=evidence_summary,
        source_authority=source_authority,
        period_label=period_label,
        explanation=explanation,
        metrics=metrics,
    )


def capital_health_metric(
    label: str,
    *,
    state: CapitalHealthState,
    value_label: str,
    evidence_summary: str,
) -> CapitalHealthMetric:
    _validate_text(label, 'label')
    _validate_state(state)
    _validate_text(value_label, 'value_label')
    _validate_text(evidence_summary, 'evidence_summary')
    return CapitalHealthMetric(
        label=label,
        state=state,
        value_label=value_label,
        evidence_summary=evidence_summary,
    )


def _unavailable_group(group: CapitalHealthGroup) -> CapitalHealthGroupEvidence:
    return CapitalHealthGroupEvidence(
        group=group,
        state='unavailable',
        title=CAPITAL_HEALTH_GROUP_TITLES[group],
        evidence_summary=_unavailable_group_summary(group),
        source_authority=UNAVAILABLE_SOURCE,
        period_label=UNAVAILABLE_PERIOD,
        explanation=_unavailable_group_explanation(group),
        metrics=_unavailable_metrics(group),
    )


def _unavailable_metrics(group: CapitalHealthGroup) -> tuple[CapitalHealthMetric, ...]:
    if group == 'availability':
        return (
            _unavailable_metric('Available Cash'),
            _unavailable_metric('Available for Redeployment'),
        )
    if group == 'recycling':
        return (_unavailable_metric('Capital Recycling Rate'),)
    if group == 'commitment':
        return (_unavailable_metric('Committed Capital'),)
    if group == 'growth':
        return (_unavailable_metric('Business-cycle Capital Growth'),)
    raise ValueError('unsupported Capital Health group')


def _unavailable_metric(label: str) -> CapitalHealthMetric:
    return CapitalHealthMetric(
        label=label,
        state='unavailable',
        value_label='Unavailable',
        evidence_summary=UNAVAILABLE_TEXT,
    )


def _unavailable_group_summary(group: CapitalHealthGroup) -> str:
    if group == 'availability':
        return 'Available Cash and Available for Redeployment evidence unavailable.'
    if group == 'recycling':
        return 'Capital Recycling Rate formula/evidence unavailable.'
    if group == 'commitment':
        return 'Committed capital evidence unavailable.'
    if group == 'growth':
        return 'Business-cycle growth evidence unavailable.'
    raise ValueError('unsupported Capital Health group')


def _unavailable_group_explanation(group: CapitalHealthGroup) -> str:
    if group == 'availability':
        return (
            'Available Cash remains distinct from Available for Redeployment; '
            'neither value is inferred without prepared local evidence.'
        )
    if group == 'recycling':
        return (
            'Capital Recycling Rate remains unavailable until formula authority '
            'and local evidence are supplied.'
        )
    if group == 'commitment':
        return 'Committed capital is not inferred without prepared local evidence.'
    if group == 'growth':
        return (
            'Capital Growth is business-cycle growth only and does not include '
            'external cash injection.'
        )
    raise ValueError('unsupported Capital Health group')


def _has_incomplete_state(group: CapitalHealthGroupEvidence) -> bool:
    if group.state in ('unavailable', 'partial', 'error'):
        return True
    return any(metric.state in ('unavailable', 'partial', 'error') for metric in group.metrics)


def _validate_evidence_tuple(evidence: tuple[CapitalHealthGroupEvidence, ...]) -> None:
    if not isinstance(evidence, tuple) or any(
        not isinstance(item, CapitalHealthGroupEvidence) for item in evidence
    ):
        raise TypeError('evidence must be a tuple of CapitalHealthGroupEvidence values')
    for item in evidence:
        _validate_group(item.group)
        _validate_state(item.state)
        _validate_text(item.title, 'title')
        _validate_text(item.evidence_summary, 'evidence_summary')
        _validate_text(item.source_authority, 'source_authority')
        _validate_text(item.period_label, 'period_label')
        _validate_text(item.explanation, 'explanation')
        _validate_metrics_tuple(item.metrics)


def _validate_metrics_tuple(metrics: tuple[CapitalHealthMetric, ...]) -> None:
    if (
        not isinstance(metrics, tuple)
        or not metrics
        or any(not isinstance(metric, CapitalHealthMetric) for metric in metrics)
    ):
        raise TypeError('metrics must be a non-empty tuple of CapitalHealthMetric values')
    for metric in metrics:
        _validate_text(metric.label, 'label')
        _validate_state(metric.state)
        _validate_text(metric.value_label, 'value_label')
        _validate_text(metric.evidence_summary, 'evidence_summary')


def _validate_error_text(error_text: str | None) -> None:
    if error_text is not None:
        _validate_text(error_text, 'error_text')


def _validate_group(group: str) -> None:
    if group not in CAPITAL_HEALTH_GROUP_ORDER:
        raise ValueError(
            'group must be availability, recycling, commitment, or growth'
        )


def _validate_state(state: str) -> None:
    if state not in ('ready', 'unavailable', 'partial', 'error'):
        raise ValueError('state must be ready, unavailable, partial, or error')


def _validate_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field_name} must be non-empty text')
