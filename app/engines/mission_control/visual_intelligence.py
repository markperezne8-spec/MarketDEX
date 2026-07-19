from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


VisualIntelligenceState = Literal['ready', 'unavailable', 'partial', 'error']
VisualIntelligenceRegion = Literal[
    'performance_charts',
    'inventory_alerts',
    'attention_heat_map',
    'market_attention_trend',
]

VISUAL_INTELLIGENCE_REGION_ORDER: tuple[VisualIntelligenceRegion, ...] = (
    'performance_charts',
    'inventory_alerts',
    'attention_heat_map',
    'market_attention_trend',
)

VISUAL_INTELLIGENCE_REGION_TITLES: dict[VisualIntelligenceRegion, str] = {
    'performance_charts': 'Performance charts',
    'inventory_alerts': 'Inventory alerts',
    'attention_heat_map': 'Attention heat map',
    'market_attention_trend': 'Market attention trend',
}

UNAVAILABLE_TEXT = 'Evidence unavailable.'
UNAVAILABLE_SOURCE = 'Local evidence unavailable'
UNAVAILABLE_FRESHNESS = 'Freshness unavailable'


@dataclass(frozen=True, slots=True)
class VisualIntelligenceEvidence:
    region: VisualIntelligenceRegion
    state: VisualIntelligenceState
    title: str
    subtitle: str
    evidence_summary: str
    source_authority: str
    freshness_label: str
    detail: str


@dataclass(frozen=True, slots=True)
class VisualIntelligenceViewModel:
    state: VisualIntelligenceState
    headline: str
    regions: tuple[VisualIntelligenceEvidence, ...]
    error_text: str | None = None


def build_visual_intelligence_view_model(
    *,
    evidence: tuple[VisualIntelligenceEvidence, ...] = (),
    error_text: str | None = None,
) -> VisualIntelligenceViewModel:
    _validate_evidence_tuple(evidence)
    _validate_error_text(error_text)

    evidence_by_region = {item.region: item for item in evidence}
    if len(evidence_by_region) != len(evidence):
        raise ValueError(
            'evidence must contain each Visual Intelligence region at most once'
        )

    ordered_regions = tuple(
        evidence_by_region.get(region) or _unavailable_region(region)
        for region in VISUAL_INTELLIGENCE_REGION_ORDER
    )

    if error_text is not None:
        return VisualIntelligenceViewModel(
            state='error',
            headline='Visual Intelligence unavailable',
            regions=ordered_regions,
            error_text=error_text,
        )

    if not evidence:
        return VisualIntelligenceViewModel(
            state='unavailable',
            headline='Visual Intelligence unavailable',
            regions=ordered_regions,
        )

    if any(region.state != 'ready' for region in ordered_regions):
        return VisualIntelligenceViewModel(
            state='partial',
            headline='Visual Intelligence partially available',
            regions=ordered_regions,
        )

    return VisualIntelligenceViewModel(
        state='ready',
        headline='Visual Intelligence ready',
        regions=ordered_regions,
    )


def visual_intelligence_evidence(
    region: VisualIntelligenceRegion,
    *,
    state: VisualIntelligenceState,
    subtitle: str,
    evidence_summary: str,
    source_authority: str,
    freshness_label: str,
    detail: str,
    title: str | None = None,
) -> VisualIntelligenceEvidence:
    _validate_region(region)
    _validate_state(state)
    _validate_text(subtitle, 'subtitle')
    _validate_text(evidence_summary, 'evidence_summary')
    _validate_text(source_authority, 'source_authority')
    _validate_text(freshness_label, 'freshness_label')
    _validate_text(detail, 'detail')
    if title is not None:
        _validate_text(title, 'title')

    return VisualIntelligenceEvidence(
        region=region,
        state=state,
        title=title or VISUAL_INTELLIGENCE_REGION_TITLES[region],
        subtitle=subtitle,
        evidence_summary=evidence_summary,
        source_authority=source_authority,
        freshness_label=freshness_label,
        detail=detail,
    )


def _unavailable_region(
    region: VisualIntelligenceRegion,
) -> VisualIntelligenceEvidence:
    title = VISUAL_INTELLIGENCE_REGION_TITLES[region]
    return VisualIntelligenceEvidence(
        region=region,
        state='unavailable',
        title=title,
        subtitle='Future visual intelligence contract',
        evidence_summary=UNAVAILABLE_TEXT,
        source_authority=UNAVAILABLE_SOURCE,
        freshness_label=UNAVAILABLE_FRESHNESS,
        detail=f'{UNAVAILABLE_TEXT} Future {title.lower()} contract required.',
    )


def _validate_evidence_tuple(
    evidence: tuple[VisualIntelligenceEvidence, ...],
) -> None:
    if not isinstance(evidence, tuple) or any(
        not isinstance(item, VisualIntelligenceEvidence) for item in evidence
    ):
        raise TypeError(
            'evidence must be a tuple of VisualIntelligenceEvidence values'
        )
    for item in evidence:
        _validate_region(item.region)
        _validate_state(item.state)
        _validate_text(item.title, 'title')
        _validate_text(item.subtitle, 'subtitle')
        _validate_text(item.evidence_summary, 'evidence_summary')
        _validate_text(item.source_authority, 'source_authority')
        _validate_text(item.freshness_label, 'freshness_label')
        _validate_text(item.detail, 'detail')


def _validate_error_text(error_text: str | None) -> None:
    if error_text is not None:
        _validate_text(error_text, 'error_text')


def _validate_region(region: str) -> None:
    if region not in VISUAL_INTELLIGENCE_REGION_ORDER:
        raise ValueError(
            'region must be performance_charts, inventory_alerts, '
            'attention_heat_map, or market_attention_trend'
        )


def _validate_state(state: str) -> None:
    if state not in ('ready', 'unavailable', 'partial', 'error'):
        raise ValueError('state must be ready, unavailable, partial, or error')


def _validate_text(value: str | None, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field_name} must be non-empty text')
