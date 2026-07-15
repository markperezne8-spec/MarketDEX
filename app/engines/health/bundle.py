from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .provider import HealthReportProvider, build_health_report


@dataclass(frozen=True, slots=True)
class HealthProviderBundle:
    providers: tuple[HealthReportProvider, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.providers, tuple):
            raise TypeError('providers must be a tuple of HealthReportProvider values')

        seen_names: set[str] = set()
        for provider in self.providers:
            if not isinstance(provider, HealthReportProvider):
                raise TypeError('providers must contain HealthReportProvider values')
            if provider.name in seen_names:
                raise ValueError('provider names must be unique')
            seen_names.add(provider.name)


def create_health_provider_bundle(providers: Iterable[HealthReportProvider]) -> HealthProviderBundle:
    return HealthProviderBundle(tuple(providers))


def build_health_reports(bundle: HealthProviderBundle) -> tuple[dict[str, Any], ...]:
    if not isinstance(bundle, HealthProviderBundle):
        raise TypeError('bundle must be a HealthProviderBundle')

    return tuple(
        {
            'provider': provider.name,
            'report': build_health_report(provider),
        }
        for provider in bundle.providers
    )
