from dataclasses import dataclass
from typing import Iterable, Protocol

from market_intelligence.observations import MarketObservation, ObservationKind


class ProviderUnavailableError(RuntimeError):
    """Raised when a registered provider cannot serve an offline-safe read."""


@dataclass(frozen=True)
class ObservationQuery:
    product_id: str
    kinds: tuple[ObservationKind, ...] = ()
    limit: int = 200

    def __post_init__(self) -> None:
        if not self.product_id.strip():
            raise ValueError('product_id must not be empty')
        if self.limit < 1 or self.limit > 500:
            raise ValueError('limit must be between 1 and 500')


class MarketObservationProvider(Protocol):
    provider_id: str
    available: bool

    def fetch(self, query: ObservationQuery) -> tuple[MarketObservation, ...]: ...


class FixtureObservationProvider:
    """Deterministic in-memory provider for offline development and verification."""

    def __init__(
        self,
        provider_id: str,
        observations: Iterable[MarketObservation] = (),
        *,
        available: bool = True,
    ) -> None:
        normalized_id = str(provider_id).strip().lower()
        if not normalized_id:
            raise ValueError('provider_id must not be empty')
        self.provider_id = normalized_id
        self.available = bool(available)
        self._observations = tuple(observations)

    def fetch(self, query: ObservationQuery) -> tuple[MarketObservation, ...]:
        if not self.available:
            raise ProviderUnavailableError(f'provider is unavailable: {self.provider_id}')
        kinds = set(query.kinds)
        matches = (
            observation
            for observation in self._observations
            if observation.product_id == query.product_id
            and (not kinds or observation.kind in kinds)
        )
        return tuple(
            sorted(matches, key=lambda item: (item.observed_at, item.observation_id))[: query.limit]
        )


class MarketObservationGateway:
    """Read-only boundary between provider adapters and normalized observations."""

    def __init__(self, providers: Iterable[MarketObservationProvider] = ()) -> None:
        self._providers: dict[str, MarketObservationProvider] = {}
        for provider in providers:
            self.register(provider)

    @property
    def provider_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._providers))

    def register(self, provider: MarketObservationProvider) -> None:
        provider_id = str(provider.provider_id).strip().lower()
        if not provider_id:
            raise ValueError('provider_id must not be empty')
        if provider_id in self._providers:
            raise ValueError(f'provider already registered: {provider_id}')
        self._providers[provider_id] = provider

    def list_observations(
        self,
        provider_id: str,
        product_id: str,
        *,
        kinds: Iterable[ObservationKind] = (),
        limit: int = 200,
    ) -> tuple[MarketObservation, ...]:
        normalized_id = str(provider_id).strip().lower()
        try:
            provider = self._providers[normalized_id]
        except KeyError as exc:
            raise KeyError(f'unknown market observation provider: {normalized_id}') from exc
        query = ObservationQuery(product_id=str(product_id), kinds=tuple(kinds), limit=int(limit))
        observations = provider.fetch(query)
        for observation in observations:
            if observation.source_id.strip().lower() != normalized_id:
                raise ValueError(
                    f'provider {normalized_id} returned observation for source {observation.source_id}'
                )
        return observations


def build_market_observation_gateway() -> MarketObservationGateway:
    return MarketObservationGateway()
