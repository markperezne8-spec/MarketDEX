from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Iterable

from market_intelligence.offline_fixtures import OFFLINE_SAMPLE_PRODUCT_ID


_CANONICAL_QUERY_ID = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')


def _required_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f'{field_name} is required')
    return normalized


def _normalized_name(value: str) -> str:
    return ' '.join(_required_text(value, 'name').split())


def _canonical_query_id(value: str) -> str:
    normalized = _required_text(value, 'query_id').lower()
    if not _CANONICAL_QUERY_ID.fullmatch(normalized):
        raise ValueError(
            'query_id must use canonical lowercase letters, numbers, and single hyphens'
        )
    return normalized


def _normalized_unique_values(
    values: Iterable[str],
    field_name: str,
    normalizer: Callable[[str], str],
) -> tuple[str, ...]:
    normalized_values: list[str] = []
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        normalized = normalizer(_required_text(value, field_name))
        if normalized in seen:
            duplicates.add(normalized)
        else:
            seen.add(normalized)
            normalized_values.append(normalized)
    if duplicates:
        raise ValueError(
            f'duplicate {field_name} values: {", ".join(sorted(duplicates))}'
        )
    return tuple(sorted(normalized_values))


@dataclass(frozen=True, slots=True)
class ResearchQueryDefinition:
    """Immutable, provider-neutral definition for a read-only research query."""

    query_id: str
    name: str
    product_ids: tuple[str, ...] = ()
    observation_kinds: tuple[str, ...] = ()
    marketplace_ids: tuple[str, ...] = ()
    notes: str = ''

    def __post_init__(self) -> None:
        object.__setattr__(self, 'query_id', _canonical_query_id(self.query_id))
        object.__setattr__(self, 'name', _normalized_name(self.name))
        object.__setattr__(
            self,
            'product_ids',
            _normalized_unique_values(self.product_ids, 'product_id', lambda item: item),
        )
        object.__setattr__(
            self,
            'observation_kinds',
            _normalized_unique_values(
                self.observation_kinds,
                'observation_kind',
                str.lower,
            ),
        )
        object.__setattr__(
            self,
            'marketplace_ids',
            _normalized_unique_values(
                self.marketplace_ids,
                'marketplace_id',
                str.lower,
            ),
        )
        object.__setattr__(self, 'notes', self.notes.strip())


class ResearchQueryCatalog:
    """Deterministic in-memory catalog. It owns no persistence or execution authority."""

    def __init__(self, definitions: Iterable[ResearchQueryDefinition] = ()) -> None:
        self._definitions: dict[str, ResearchQueryDefinition] = {}
        for definition in definitions:
            self.register(definition)

    def register(self, definition: ResearchQueryDefinition) -> None:
        if not isinstance(definition, ResearchQueryDefinition):
            raise TypeError('definition must be ResearchQueryDefinition')
        if definition.query_id in self._definitions:
            raise ValueError(f'research query already registered: {definition.query_id}')
        self._definitions[definition.query_id] = definition

    def get(self, query_id: str) -> ResearchQueryDefinition:
        normalized = _canonical_query_id(query_id)
        try:
            return self._definitions[normalized]
        except KeyError as exc:
            raise KeyError(f'unknown research query: {normalized}') from exc

    def list_definitions(self) -> tuple[ResearchQueryDefinition, ...]:
        return tuple(
            sorted(
                self._definitions.values(),
                key=lambda item: (item.name.casefold(), item.query_id),
            )
        )

    @property
    def query_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._definitions))


OFFLINE_RESEARCH_QUERY_FIXTURE = ResearchQueryDefinition(
    query_id='mega-evolution-etb-watch',
    name='Mega Evolution ETB Watch',
    product_ids=(OFFLINE_SAMPLE_PRODUCT_ID,),
    marketplace_ids=('ebay', 'tcgplayer'),
    observation_kinds=('active_listing', 'daily_volume', 'market_price'),
    notes='Offline fixture only; review evidence without execution.',
)


def build_research_query_catalog() -> ResearchQueryCatalog:
    return ResearchQueryCatalog((OFFLINE_RESEARCH_QUERY_FIXTURE,))
