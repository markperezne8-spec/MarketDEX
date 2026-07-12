from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


def _required_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f'{field_name} is required')
    return normalized


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
        object.__setattr__(self, 'query_id', _required_text(self.query_id, 'query_id').lower())
        object.__setattr__(self, 'name', _required_text(self.name, 'name'))
        object.__setattr__(
            self,
            'product_ids',
            tuple(sorted({_required_text(item, 'product_id') for item in self.product_ids})),
        )
        object.__setattr__(
            self,
            'observation_kinds',
            tuple(sorted({_required_text(item, 'observation_kind').lower() for item in self.observation_kinds})),
        )
        object.__setattr__(
            self,
            'marketplace_ids',
            tuple(sorted({_required_text(item, 'marketplace_id').lower() for item in self.marketplace_ids})),
        )
        object.__setattr__(self, 'notes', self.notes.strip())


class ResearchQueryCatalog:
    """Deterministic in-memory catalog. It owns no persistence or execution authority."""

    def __init__(self, definitions: Iterable[ResearchQueryDefinition] = ()) -> None:
        self._definitions: dict[str, ResearchQueryDefinition] = {}
        for definition in definitions:
            self.register(definition)

    def register(self, definition: ResearchQueryDefinition) -> None:
        if definition.query_id in self._definitions:
            raise ValueError(f'research query already registered: {definition.query_id}')
        self._definitions[definition.query_id] = definition

    def get(self, query_id: str) -> ResearchQueryDefinition:
        normalized = _required_text(query_id, 'query_id').lower()
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


def build_research_query_catalog() -> ResearchQueryCatalog:
    return ResearchQueryCatalog()
