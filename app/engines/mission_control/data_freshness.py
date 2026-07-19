from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


DataFreshnessState = Literal['ready', 'unavailable', 'partial', 'error']
DataFreshnessDomain = Literal[
    'inventory',
    'reports',
    'market_intelligence',
    'authority',
]

DATA_FRESHNESS_DOMAIN_ORDER: tuple[DataFreshnessDomain, ...] = (
    'inventory',
    'reports',
    'market_intelligence',
    'authority',
)

DATA_FRESHNESS_DOMAIN_TITLES: dict[DataFreshnessDomain, str] = {
    'inventory': 'Inventory',
    'reports': 'Reports',
    'market_intelligence': 'Market Intelligence',
    'authority': 'Authority',
}

UNAVAILABLE_SOURCE = 'Local evidence unavailable'
UNAVAILABLE_AS_OF = 'As-of unavailable'
UNAVAILABLE_FRESHNESS = 'Freshness unavailable'
UNAVAILABLE_DETAIL = 'Evidence unavailable.'


@dataclass(frozen=True, slots=True)
class DataFreshnessEvidence:
    domain: DataFreshnessDomain
    state: DataFreshnessState
    title: str
    source_authority: str
    as_of_label: str
    freshness_label: str
    detail: str


@dataclass(frozen=True, slots=True)
class DataFreshnessViewModel:
    state: DataFreshnessState
    headline: str
    domains: tuple[DataFreshnessEvidence, ...]
    error_text: str | None = None


def build_data_freshness_view_model(
    *,
    evidence: tuple[DataFreshnessEvidence, ...] = (),
    error_text: str | None = None,
) -> DataFreshnessViewModel:
    _validate_evidence_tuple(evidence)
    _validate_error_text(error_text)

    evidence_by_domain = {item.domain: item for item in evidence}
    if len(evidence_by_domain) != len(evidence):
        raise ValueError('evidence must contain each Data Freshness domain at most once')

    ordered_domains = tuple(
        evidence_by_domain.get(domain) or _unavailable_domain(domain)
        for domain in DATA_FRESHNESS_DOMAIN_ORDER
    )

    if error_text is not None:
        return DataFreshnessViewModel(
            state='error',
            headline='Data Freshness unavailable',
            domains=ordered_domains,
            error_text=error_text,
        )

    if not evidence:
        return DataFreshnessViewModel(
            state='unavailable',
            headline='Data Freshness unavailable',
            domains=ordered_domains,
        )

    if any(domain.state != 'ready' for domain in ordered_domains):
        return DataFreshnessViewModel(
            state='partial',
            headline='Data Freshness partially available',
            domains=ordered_domains,
        )

    return DataFreshnessViewModel(
        state='ready',
        headline='Data Freshness ready',
        domains=ordered_domains,
    )


def data_freshness_evidence(
    domain: DataFreshnessDomain,
    *,
    state: DataFreshnessState,
    source_authority: str,
    as_of_label: str,
    freshness_label: str,
    detail: str,
    title: str | None = None,
) -> DataFreshnessEvidence:
    _validate_domain(domain)
    _validate_state(state)
    _validate_text(source_authority, 'source_authority')
    _validate_text(as_of_label, 'as_of_label')
    _validate_text(freshness_label, 'freshness_label')
    _validate_text(detail, 'detail')
    if title is not None:
        _validate_text(title, 'title')

    return DataFreshnessEvidence(
        domain=domain,
        state=state,
        title=title or DATA_FRESHNESS_DOMAIN_TITLES[domain],
        source_authority=source_authority,
        as_of_label=as_of_label,
        freshness_label=freshness_label,
        detail=detail,
    )


def _unavailable_domain(domain: DataFreshnessDomain) -> DataFreshnessEvidence:
    return DataFreshnessEvidence(
        domain=domain,
        state='unavailable',
        title=DATA_FRESHNESS_DOMAIN_TITLES[domain],
        source_authority=UNAVAILABLE_SOURCE,
        as_of_label=UNAVAILABLE_AS_OF,
        freshness_label=UNAVAILABLE_FRESHNESS,
        detail=UNAVAILABLE_DETAIL,
    )


def _validate_evidence_tuple(
    evidence: tuple[DataFreshnessEvidence, ...],
) -> None:
    if not isinstance(evidence, tuple) or any(
        not isinstance(item, DataFreshnessEvidence) for item in evidence
    ):
        raise TypeError('evidence must be a tuple of DataFreshnessEvidence values')
    for item in evidence:
        _validate_domain(item.domain)
        _validate_state(item.state)
        _validate_text(item.title, 'title')
        _validate_text(item.source_authority, 'source_authority')
        _validate_text(item.as_of_label, 'as_of_label')
        _validate_text(item.freshness_label, 'freshness_label')
        _validate_text(item.detail, 'detail')


def _validate_error_text(error_text: str | None) -> None:
    if error_text is not None:
        _validate_text(error_text, 'error_text')


def _validate_domain(domain: str) -> None:
    if domain not in DATA_FRESHNESS_DOMAIN_ORDER:
        raise ValueError(
            'domain must be inventory, reports, market_intelligence, or authority'
        )


def _validate_state(state: str) -> None:
    if state not in ('ready', 'unavailable', 'partial', 'error'):
        raise ValueError('state must be ready, unavailable, partial, or error')


def _validate_text(value: str | None, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field_name} must be non-empty text')
