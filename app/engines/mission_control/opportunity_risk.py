from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


OpportunityRiskState = Literal['ready', 'unavailable', 'partial', 'error']
OpportunityRiskKind = Literal['opportunity', 'risk']
OpportunityRiskTop3Relationship = Literal['independent', 'broader_related']

OPPORTUNITY_RISK_KIND_ORDER: tuple[OpportunityRiskKind, ...] = (
    'opportunity',
    'risk',
)

OPPORTUNITY_RISK_KIND_TITLES: dict[OpportunityRiskKind, str] = {
    'opportunity': 'Opportunities',
    'risk': 'Risks',
}

MAX_ITEMS_PER_GROUP = 3
UNAVAILABLE_TEXT = 'Evidence unavailable.'
UNAVAILABLE_SOURCE = 'Local evidence unavailable'
UNAVAILABLE_FRESHNESS = 'Freshness unavailable'


@dataclass(frozen=True, slots=True)
class OpportunityRiskItem:
    kind: OpportunityRiskKind
    state: OpportunityRiskState
    display_order: int
    candidate_key: str
    label: str
    why_it_matters: str
    direction_label: str
    evidence_summary: str
    source_authority: str
    freshness_label: str
    top3_relationship: OpportunityRiskTop3Relationship = 'independent'
    independent_evidence_summary: str | None = None


@dataclass(frozen=True, slots=True)
class OpportunityRiskGroup:
    kind: OpportunityRiskKind
    state: OpportunityRiskState
    title: str
    evidence_summary: str
    source_authority: str
    freshness_label: str
    items: tuple[OpportunityRiskItem, ...]


@dataclass(frozen=True, slots=True)
class OpportunityRiskViewModel:
    state: OpportunityRiskState
    headline: str
    groups: tuple[OpportunityRiskGroup, ...]
    excluded_todays_top3_candidate_keys: tuple[str, ...] = ()
    error_text: str | None = None


def build_opportunity_risk_view_model(
    *,
    evidence: tuple[OpportunityRiskItem, ...] = (),
    excluded_todays_top3_candidate_keys: tuple[str, ...] = (),
    error_text: str | None = None,
) -> OpportunityRiskViewModel:
    _validate_evidence_tuple(evidence)
    _validate_excluded_top3_keys(excluded_todays_top3_candidate_keys)
    _validate_error_text(error_text)

    candidate_keys = tuple(item.candidate_key for item in evidence)
    if len(set(candidate_keys)) != len(candidate_keys):
        raise ValueError('evidence must contain each Opportunity + Risk candidate key at most once')

    excluded_keys = set(excluded_todays_top3_candidate_keys)
    visible_evidence = tuple(
        item for item in evidence if item.candidate_key not in excluded_keys
    )

    ordered_groups = tuple(
        _build_group(kind, visible_evidence)
        for kind in OPPORTUNITY_RISK_KIND_ORDER
    )

    if error_text is not None:
        return OpportunityRiskViewModel(
            state='error',
            headline='Opportunity + Risk unavailable',
            groups=ordered_groups,
            excluded_todays_top3_candidate_keys=excluded_todays_top3_candidate_keys,
            error_text=error_text,
        )

    if not visible_evidence:
        return OpportunityRiskViewModel(
            state='unavailable',
            headline='Opportunity + Risk unavailable',
            groups=ordered_groups,
            excluded_todays_top3_candidate_keys=excluded_todays_top3_candidate_keys,
        )

    if any(group.state in ('unavailable', 'partial', 'error') for group in ordered_groups):
        return OpportunityRiskViewModel(
            state='partial',
            headline='Opportunity + Risk partially available',
            groups=ordered_groups,
            excluded_todays_top3_candidate_keys=excluded_todays_top3_candidate_keys,
        )

    return OpportunityRiskViewModel(
        state='ready',
        headline='Opportunity + Risk ready',
        groups=ordered_groups,
        excluded_todays_top3_candidate_keys=excluded_todays_top3_candidate_keys,
    )


def opportunity_risk_evidence(
    kind: OpportunityRiskKind,
    *,
    state: OpportunityRiskState,
    display_order: int,
    candidate_key: str,
    label: str,
    why_it_matters: str,
    direction_label: str,
    evidence_summary: str,
    source_authority: str,
    freshness_label: str,
    top3_relationship: OpportunityRiskTop3Relationship = 'independent',
    independent_evidence_summary: str | None = None,
) -> OpportunityRiskItem:
    _validate_kind(kind)
    _validate_state(state)
    _validate_display_order(display_order)
    _validate_text(candidate_key, 'candidate_key')
    _validate_text(label, 'label')
    _validate_text(why_it_matters, 'why_it_matters')
    _validate_text(direction_label, 'direction_label')
    _validate_text(evidence_summary, 'evidence_summary')
    _validate_text(source_authority, 'source_authority')
    _validate_text(freshness_label, 'freshness_label')
    _validate_top3_relationship(top3_relationship, independent_evidence_summary)
    return OpportunityRiskItem(
        kind=kind,
        state=state,
        display_order=display_order,
        candidate_key=candidate_key,
        label=label,
        why_it_matters=why_it_matters,
        direction_label=direction_label,
        evidence_summary=evidence_summary,
        source_authority=source_authority,
        freshness_label=freshness_label,
        top3_relationship=top3_relationship,
        independent_evidence_summary=independent_evidence_summary,
    )


def _build_group(
    kind: OpportunityRiskKind,
    visible_evidence: tuple[OpportunityRiskItem, ...],
) -> OpportunityRiskGroup:
    items = tuple(
        sorted(
            (item for item in visible_evidence if item.kind == kind),
            key=lambda item: (item.display_order, item.candidate_key),
        )
    )

    if len(items) > MAX_ITEMS_PER_GROUP:
        raise ValueError('each Opportunity + Risk group may contain at most three items')

    if not items:
        return _unavailable_group(kind)

    state: OpportunityRiskState = 'ready'
    if any(item.state in ('unavailable', 'partial', 'error') for item in items):
        state = 'partial'

    return OpportunityRiskGroup(
        kind=kind,
        state=state,
        title=OPPORTUNITY_RISK_KIND_TITLES[kind],
        evidence_summary=f'{OPPORTUNITY_RISK_KIND_TITLES[kind]} prepared local evidence.',
        source_authority='Prepared local evidence',
        freshness_label='Prepared local freshness',
        items=items,
    )


def _unavailable_group(kind: OpportunityRiskKind) -> OpportunityRiskGroup:
    return OpportunityRiskGroup(
        kind=kind,
        state='unavailable',
        title=OPPORTUNITY_RISK_KIND_TITLES[kind],
        evidence_summary=_unavailable_group_summary(kind),
        source_authority=UNAVAILABLE_SOURCE,
        freshness_label=UNAVAILABLE_FRESHNESS,
        items=(),
    )


def _unavailable_group_summary(kind: OpportunityRiskKind) -> str:
    if kind == 'opportunity':
        return 'Prepared local Opportunity evidence unavailable.'
    if kind == 'risk':
        return 'Prepared local Risk evidence unavailable.'
    raise ValueError('unsupported Opportunity + Risk kind')


def _validate_evidence_tuple(evidence: tuple[OpportunityRiskItem, ...]) -> None:
    if not isinstance(evidence, tuple) or any(
        not isinstance(item, OpportunityRiskItem) for item in evidence
    ):
        raise TypeError('evidence must be a tuple of OpportunityRiskItem values')
    for item in evidence:
        _validate_kind(item.kind)
        _validate_state(item.state)
        _validate_display_order(item.display_order)
        _validate_text(item.candidate_key, 'candidate_key')
        _validate_text(item.label, 'label')
        _validate_text(item.why_it_matters, 'why_it_matters')
        _validate_text(item.direction_label, 'direction_label')
        _validate_text(item.evidence_summary, 'evidence_summary')
        _validate_text(item.source_authority, 'source_authority')
        _validate_text(item.freshness_label, 'freshness_label')
        _validate_top3_relationship(
            item.top3_relationship,
            item.independent_evidence_summary,
        )


def _validate_excluded_top3_keys(keys: tuple[str, ...]) -> None:
    if not isinstance(keys, tuple) or any(not isinstance(key, str) for key in keys):
        raise TypeError('excluded_todays_top3_candidate_keys must be a tuple of text keys')
    if any(not key.strip() for key in keys):
        raise ValueError('excluded_todays_top3_candidate_keys must contain non-empty text keys')
    if len(set(keys)) != len(keys):
        raise ValueError('excluded_todays_top3_candidate_keys must not contain duplicates')


def _validate_top3_relationship(
    relationship: str,
    independent_evidence_summary: str | None,
) -> None:
    if relationship not in ('independent', 'broader_related'):
        raise ValueError('top3_relationship must be independent or broader_related')
    if relationship == 'broader_related':
        _validate_text(independent_evidence_summary, 'independent_evidence_summary')
    elif independent_evidence_summary is not None:
        _validate_text(independent_evidence_summary, 'independent_evidence_summary')


def _validate_error_text(error_text: str | None) -> None:
    if error_text is not None:
        _validate_text(error_text, 'error_text')


def _validate_kind(kind: str) -> None:
    if kind not in OPPORTUNITY_RISK_KIND_ORDER:
        raise ValueError('kind must be opportunity or risk')


def _validate_state(state: str) -> None:
    if state not in ('ready', 'unavailable', 'partial', 'error'):
        raise ValueError('state must be ready, unavailable, partial, or error')


def _validate_display_order(display_order: int) -> None:
    if not isinstance(display_order, int) or display_order < 1:
        raise ValueError('display_order must be a positive integer')


def _validate_text(value: str | None, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field_name} must be non-empty text')
