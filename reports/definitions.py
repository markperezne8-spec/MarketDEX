from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


CURRENT_STATE = 'current_state'
EVENT_HISTORY = 'event_history'
SNAPSHOTS = 'snapshots'
DECISION_HISTORY = 'decision_history'
OUTCOMES = 'outcomes'
CATALOG_ONLY_EXECUTION_MODE = 'catalog-only'

REPORT_EVIDENCE_FAMILIES = frozenset(
    {
        CURRENT_STATE,
        EVENT_HISTORY,
        SNAPSHOTS,
        DECISION_HISTORY,
        OUTCOMES,
    }
)


def _required_text(value: str, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f'{field_name} is required')
    return normalized


def _normalized_values(values: Iterable[str], field_name: str) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                _required_text(value, field_name).lower().replace(' ', '_')
                for value in values
            }
        )
    )


@dataclass(frozen=True, slots=True)
class ReportDefinition:
    """Immutable definition of a read-only business report."""

    report_id: str
    name: str
    business_question: str
    evidence_families: tuple[str, ...]
    source_domains: tuple[str, ...]
    description: str = ''
    execution_mode: str = CATALOG_ONLY_EXECUTION_MODE

    def __post_init__(self) -> None:
        report_id = _required_text(self.report_id, 'report_id').lower()
        name = _required_text(self.name, 'name')
        business_question = _required_text(self.business_question, 'business_question')
        if not business_question.endswith('?'):
            raise ValueError('business_question must end with a question mark')

        evidence_families = _normalized_values(
            self.evidence_families,
            'evidence_family',
        )
        if not evidence_families:
            raise ValueError('at least one evidence_family is required')
        unsupported = set(evidence_families) - REPORT_EVIDENCE_FAMILIES
        if unsupported:
            names = ', '.join(sorted(unsupported))
            raise ValueError(f'unsupported evidence families: {names}')

        source_domains = _normalized_values(self.source_domains, 'source_domain')
        if not source_domains:
            raise ValueError('at least one source_domain is required')

        execution_mode = _required_text(self.execution_mode, 'execution_mode').lower()
        if execution_mode != CATALOG_ONLY_EXECUTION_MODE:
            raise ValueError(
                f'unsupported execution mode: {execution_mode}'
            )

        object.__setattr__(self, 'report_id', report_id)
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'business_question', business_question)
        object.__setattr__(self, 'evidence_families', evidence_families)
        object.__setattr__(self, 'source_domains', source_domains)
        object.__setattr__(self, 'description', self.description.strip())
        object.__setattr__(self, 'execution_mode', execution_mode)


class ReportCatalog:
    """Deterministic in-memory catalog with no execution or persistence authority."""

    def __init__(self, definitions: Iterable[ReportDefinition] = ()) -> None:
        self._definitions: dict[str, ReportDefinition] = {}
        for definition in definitions:
            self.register(definition)

    def register(self, definition: ReportDefinition) -> None:
        if definition.report_id in self._definitions:
            raise ValueError(f'report already registered: {definition.report_id}')
        self._definitions[definition.report_id] = definition

    def get(self, report_id: str) -> ReportDefinition:
        normalized = _required_text(report_id, 'report_id').lower()
        try:
            return self._definitions[normalized]
        except KeyError as exc:
            raise KeyError(f'unknown report: {normalized}') from exc

    def list_definitions(self) -> tuple[ReportDefinition, ...]:
        return tuple(
            sorted(
                self._definitions.values(),
                key=lambda item: (item.name.casefold(), item.report_id),
            )
        )

    @property
    def report_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._definitions))


INVENTORY_AGE_PATTERNS_REPORT = ReportDefinition(
    report_id='inventory-age-patterns',
    name='Inventory Age Patterns',
    business_question='What patterns does inventory age reveal?',
    evidence_families=(CURRENT_STATE, EVENT_HISTORY),
    source_domains=('inventory',),
    description=(
        'Workbook-backed definition for reviewing inventory-age patterns '
        'without executing queries or defining thresholds.'
    ),
)

INVENTORY_TURNOVER_REPORT = ReportDefinition(
    report_id='inventory-turnover',
    name='Inventory Turnover',
    business_question='How quickly does business inventory turn over?',
    evidence_families=(CURRENT_STATE, EVENT_HISTORY, OUTCOMES),
    source_domains=('audit', 'inventory', 'listing'),
    description=(
        'Catalog-only definition for the inventory-turnover-units-v1 '
        'contract without query execution or formula computation.'
    ),
)


def build_report_catalog() -> ReportCatalog:
    return ReportCatalog(
        (
            INVENTORY_AGE_PATTERNS_REPORT,
            INVENTORY_TURNOVER_REPORT,
        )
    )
