from dataclasses import dataclass
from enum import StrEnum


class ApplicationMode(StrEnum):
    BUSINESS = 'business'
    COLLECTOR = 'collector'


@dataclass(frozen=True)
class ModeDefinition:
    mode: ApplicationMode
    title: str
    categories: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError('mode title must not be empty')
        if not self.categories:
            raise ValueError(f'mode must expose at least one category: {self.mode}')
        normalized = tuple(category.strip() for category in self.categories)
        if any(not category for category in normalized):
            raise ValueError(f'mode categories must not be empty: {self.mode}')
        if len(normalized) != len(set(normalized)):
            raise ValueError(f'duplicate mode categories: {self.mode}')
        object.__setattr__(self, 'categories', normalized)


class ModeCatalog:
    def __init__(self, definitions: tuple[ModeDefinition, ...]) -> None:
        self._definitions = definitions
        self._by_mode = {definition.mode: definition for definition in definitions}
        if len(self._by_mode) != len(definitions):
            raise ValueError('duplicate application modes')

    @property
    def definitions(self) -> tuple[ModeDefinition, ...]:
        return self._definitions

    def resolve(self, mode: ApplicationMode) -> ModeDefinition:
        try:
            return self._by_mode[mode]
        except KeyError as exc:
            raise KeyError(f'unknown application mode: {mode}') from exc


CORE_MODES = (
    ModeDefinition(
        ApplicationMode.BUSINESS,
        'Business Mode',
        (
            'mission-control',
            'inventory',
            'pricing',
            'marketplaces',
            'listings',
            'sales',
            'sealed-decisions',
            'reports',
        ),
    ),
    ModeDefinition(
        ApplicationMode.COLLECTOR,
        'Collector Mode',
        (
            'collection-overview',
            'watchlist',
            'market-pulse',
            'set-completion',
            'grading',
            'marketplaces',
            'sealed-decisions',
            'research',
        ),
    ),
)


def build_mode_catalog() -> ModeCatalog:
    return ModeCatalog(CORE_MODES)
