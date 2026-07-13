from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from market_intelligence.observation_gateway import MarketObservationGateway
from market_intelligence.observations import MarketObservation, ObservationKind
from market_intelligence.offline_fixtures import OFFLINE_SAMPLE_SOURCE_ID
from market_intelligence.research_queries import ResearchQueryDefinition


@dataclass(frozen=True, slots=True)
class ResearchQueryPreviewRow:
    """Read-only evidence row matched to a saved research query definition."""

    query_id: str
    query_name: str
    product_id: str
    evidence_id: str
    evidence_label: str
    observation_kind: str
    value: str
    confidence: str
    observed_at: str


class ResearchQueryPreviewService:
    """Offline-only preview boundary for saved research queries.

    The service reads saved query definitions and approved fixture observations only. It owns
    no persistence, no live provider access, and no execution or mutation authority.
    """

    def __init__(self, observation_gateway: MarketObservationGateway) -> None:
        self._observation_gateway = observation_gateway

    def preview(
        self,
        definitions: Iterable[ResearchQueryDefinition],
    ) -> tuple[ResearchQueryPreviewRow, ...]:
        rows: list[ResearchQueryPreviewRow] = []
        for definition in definitions:
            kinds = _preview_kinds(definition)
            for product_id in definition.product_ids:
                observations = self._observation_gateway.list_observations(
                    OFFLINE_SAMPLE_SOURCE_ID,
                    product_id,
                    kinds=kinds,
                )
                rows.extend(_preview_row(definition, observation) for observation in observations)
        return tuple(
            sorted(
                rows,
                key=lambda row: (
                    row.query_name.casefold(),
                    row.query_id,
                    row.product_id,
                    row.observed_at,
                    row.evidence_id,
                ),
            )
        )


def _preview_kinds(definition: ResearchQueryDefinition) -> tuple[ObservationKind, ...]:
    kinds: list[ObservationKind] = []
    for raw_kind in definition.observation_kinds:
        lookup_key = raw_kind.replace('-', '_').upper()
        try:
            kinds.append(ObservationKind[lookup_key])
        except KeyError as exc:
            raise ValueError(f'unknown research query observation kind: {raw_kind}') from exc
    return tuple(kinds)


def _preview_row(
    definition: ResearchQueryDefinition,
    observation: MarketObservation,
) -> ResearchQueryPreviewRow:
    return ResearchQueryPreviewRow(
        query_id=definition.query_id,
        query_name=definition.name,
        product_id=observation.product_id,
        evidence_id=observation.observation_id,
        evidence_label=observation.metadata.get('label', observation.kind.value),
        observation_kind=observation.kind.name.lower(),
        value=_format_value(observation),
        confidence=f'{observation.confidence:.0%}',
        observed_at=observation.observed_at.strftime('%Y-%m-%d %H:%M UTC'),
    )


def _format_value(observation: MarketObservation) -> str:
    if observation.kind is ObservationKind.MARKET_PRICE:
        return f'{observation.currency or ""} {observation.value}'.strip()
    return str(observation.value)


def build_research_query_preview_service(
    observation_gateway: MarketObservationGateway,
) -> ResearchQueryPreviewService:
    return ResearchQueryPreviewService(observation_gateway)
