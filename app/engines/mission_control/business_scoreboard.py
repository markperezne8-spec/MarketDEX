from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


BusinessScoreboardState = Literal[
    'ready',
    'unavailable',
    'partial',
    'not_applicable',
    'error',
]
BusinessScoreboardGroup = Literal['money', 'throughput']

BUSINESS_SCOREBOARD_GROUP_ORDER: tuple[BusinessScoreboardGroup, ...] = (
    'money',
    'throughput',
)

BUSINESS_SCOREBOARD_GROUP_TITLES: dict[BusinessScoreboardGroup, str] = {
    'money': 'Money',
    'throughput': 'Throughput',
}

DEFAULT_PERIOD_LABEL = '90 DAYS'
UNAVAILABLE_TEXT = 'Evidence unavailable.'
UNAVAILABLE_SOURCE = 'Local evidence unavailable'
UNAVAILABLE_CALCULATION_AUTHORITY = 'Calculation authority unavailable'


@dataclass(frozen=True, slots=True)
class BusinessScoreboardMetric:
    label: str
    state: BusinessScoreboardState
    value_label: str
    period_label: str
    evidence_summary: str
    source_authority: str
    calculation_authority: str


@dataclass(frozen=True, slots=True)
class BusinessScoreboardGroupEvidence:
    group: BusinessScoreboardGroup
    state: BusinessScoreboardState
    title: str
    evidence_summary: str
    source_authority: str
    period_label: str
    metrics: tuple[BusinessScoreboardMetric, ...]


@dataclass(frozen=True, slots=True)
class BusinessScoreboardViewModel:
    state: BusinessScoreboardState
    headline: str
    selected_period_label: str
    groups: tuple[BusinessScoreboardGroupEvidence, ...]
    error_text: str | None = None


def build_business_scoreboard_view_model(
    *,
    evidence: tuple[BusinessScoreboardGroupEvidence, ...] = (),
    selected_period_label: str = DEFAULT_PERIOD_LABEL,
    error_text: str | None = None,
) -> BusinessScoreboardViewModel:
    _validate_evidence_tuple(evidence)
    _validate_text(selected_period_label, 'selected_period_label')
    _validate_error_text(error_text)

    evidence_by_group = {item.group: item for item in evidence}
    if len(evidence_by_group) != len(evidence):
        raise ValueError('evidence must contain each Business Scoreboard group at most once')

    ordered_groups = tuple(
        evidence_by_group.get(group) or _unavailable_group(group, selected_period_label)
        for group in BUSINESS_SCOREBOARD_GROUP_ORDER
    )

    if error_text is not None:
        return BusinessScoreboardViewModel(
            state='error',
            headline='Business Scoreboard unavailable',
            selected_period_label=selected_period_label,
            groups=ordered_groups,
            error_text=error_text,
        )

    if not evidence:
        return BusinessScoreboardViewModel(
            state='unavailable',
            headline='Business Scoreboard unavailable',
            selected_period_label=selected_period_label,
            groups=ordered_groups,
        )

    if all(_is_not_applicable(group) for group in ordered_groups):
        return BusinessScoreboardViewModel(
            state='not_applicable',
            headline='Business Scoreboard not applicable',
            selected_period_label=selected_period_label,
            groups=ordered_groups,
        )

    if any(_has_incomplete_state(group) for group in ordered_groups):
        return BusinessScoreboardViewModel(
            state='partial',
            headline='Business Scoreboard partially available',
            selected_period_label=selected_period_label,
            groups=ordered_groups,
        )

    return BusinessScoreboardViewModel(
        state='ready',
        headline='Business Scoreboard ready',
        selected_period_label=selected_period_label,
        groups=ordered_groups,
    )


def business_scoreboard_group_evidence(
    group: BusinessScoreboardGroup,
    *,
    state: BusinessScoreboardState,
    evidence_summary: str,
    source_authority: str,
    period_label: str,
    metrics: tuple[BusinessScoreboardMetric, ...],
    title: str | None = None,
) -> BusinessScoreboardGroupEvidence:
    _validate_group(group)
    _validate_state(state)
    _validate_text(evidence_summary, 'evidence_summary')
    _validate_text(source_authority, 'source_authority')
    _validate_text(period_label, 'period_label')
    _validate_metrics_tuple(metrics)
    if title is not None:
        _validate_text(title, 'title')
    return BusinessScoreboardGroupEvidence(
        group=group,
        state=state,
        title=title or BUSINESS_SCOREBOARD_GROUP_TITLES[group],
        evidence_summary=evidence_summary,
        source_authority=source_authority,
        period_label=period_label,
        metrics=metrics,
    )


def business_scoreboard_metric(
    label: str,
    *,
    state: BusinessScoreboardState,
    value_label: str,
    period_label: str,
    evidence_summary: str,
    source_authority: str,
    calculation_authority: str,
) -> BusinessScoreboardMetric:
    _validate_text(label, 'label')
    _validate_state(state)
    _validate_text(value_label, 'value_label')
    _validate_text(period_label, 'period_label')
    _validate_text(evidence_summary, 'evidence_summary')
    _validate_text(source_authority, 'source_authority')
    _validate_text(calculation_authority, 'calculation_authority')
    return BusinessScoreboardMetric(
        label=label,
        state=state,
        value_label=value_label,
        period_label=period_label,
        evidence_summary=evidence_summary,
        source_authority=source_authority,
        calculation_authority=calculation_authority,
    )


def _unavailable_group(
    group: BusinessScoreboardGroup,
    period_label: str,
) -> BusinessScoreboardGroupEvidence:
    return BusinessScoreboardGroupEvidence(
        group=group,
        state='unavailable',
        title=BUSINESS_SCOREBOARD_GROUP_TITLES[group],
        evidence_summary=_unavailable_group_summary(group),
        source_authority=UNAVAILABLE_SOURCE,
        period_label=period_label,
        metrics=_unavailable_metrics(group, period_label),
    )


def _unavailable_metrics(
    group: BusinessScoreboardGroup,
    period_label: str,
) -> tuple[BusinessScoreboardMetric, ...]:
    if group == 'money':
        return (
            _unavailable_metric('Seller Net Proceeds', period_label),
            _unavailable_metric('Net Business Gain', period_label),
            _unavailable_metric('Capital Recycled This Period', period_label),
        )
    if group == 'throughput':
        return (
            _unavailable_metric('Orders Completed', period_label),
            _unavailable_metric('Items Sold', period_label),
            _unavailable_metric('Median Days to Sell', period_label),
        )
    raise ValueError('unsupported Business Scoreboard group')


def _unavailable_metric(label: str, period_label: str) -> BusinessScoreboardMetric:
    return BusinessScoreboardMetric(
        label=label,
        state='unavailable',
        value_label='Unavailable',
        period_label=period_label,
        evidence_summary=UNAVAILABLE_TEXT,
        source_authority=UNAVAILABLE_SOURCE,
        calculation_authority=UNAVAILABLE_CALCULATION_AUTHORITY,
    )


def _unavailable_group_summary(group: BusinessScoreboardGroup) -> str:
    if group == 'money':
        return 'Prepared local Money outcome evidence unavailable.'
    if group == 'throughput':
        return 'Prepared local Throughput outcome evidence unavailable.'
    raise ValueError('unsupported Business Scoreboard group')


def _has_incomplete_state(group: BusinessScoreboardGroupEvidence) -> bool:
    if group.state in ('unavailable', 'partial', 'not_applicable', 'error'):
        return True
    return any(
        metric.state in ('unavailable', 'partial', 'not_applicable', 'error')
        for metric in group.metrics
    )


def _is_not_applicable(group: BusinessScoreboardGroupEvidence) -> bool:
    return group.state == 'not_applicable' and all(
        metric.state == 'not_applicable'
        for metric in group.metrics
    )


def _validate_evidence_tuple(evidence: tuple[BusinessScoreboardGroupEvidence, ...]) -> None:
    if not isinstance(evidence, tuple) or any(
        not isinstance(item, BusinessScoreboardGroupEvidence) for item in evidence
    ):
        raise TypeError('evidence must be a tuple of BusinessScoreboardGroupEvidence values')
    for item in evidence:
        _validate_group(item.group)
        _validate_state(item.state)
        _validate_text(item.title, 'title')
        _validate_text(item.evidence_summary, 'evidence_summary')
        _validate_text(item.source_authority, 'source_authority')
        _validate_text(item.period_label, 'period_label')
        _validate_metrics_tuple(item.metrics)


def _validate_metrics_tuple(metrics: tuple[BusinessScoreboardMetric, ...]) -> None:
    if (
        not isinstance(metrics, tuple)
        or not metrics
        or any(not isinstance(metric, BusinessScoreboardMetric) for metric in metrics)
    ):
        raise TypeError('metrics must be a non-empty tuple of BusinessScoreboardMetric values')
    for metric in metrics:
        _validate_text(metric.label, 'label')
        _validate_state(metric.state)
        _validate_text(metric.value_label, 'value_label')
        _validate_text(metric.period_label, 'period_label')
        _validate_text(metric.evidence_summary, 'evidence_summary')
        _validate_text(metric.source_authority, 'source_authority')
        _validate_text(metric.calculation_authority, 'calculation_authority')


def _validate_error_text(error_text: str | None) -> None:
    if error_text is not None:
        _validate_text(error_text, 'error_text')


def _validate_group(group: str) -> None:
    if group not in BUSINESS_SCOREBOARD_GROUP_ORDER:
        raise ValueError('group must be money or throughput')


def _validate_state(state: str) -> None:
    if state not in ('ready', 'unavailable', 'partial', 'not_applicable', 'error'):
        raise ValueError(
            'state must be ready, unavailable, partial, not_applicable, or error'
        )


def _validate_text(value: str | None, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field_name} must be non-empty text')
