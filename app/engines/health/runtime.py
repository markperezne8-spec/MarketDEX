from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .bundle import HealthProviderBundle
from .bundle_report import health_bundle_report_payload


@dataclass(frozen=True, slots=True)
class HealthRuntimeComposition:
    runtime_name: str
    provider_bundle: HealthProviderBundle

    def __post_init__(self) -> None:
        if not isinstance(self.runtime_name, str) or not self.runtime_name.strip():
            raise ValueError('runtime_name must be non-empty text')
        if not isinstance(self.provider_bundle, HealthProviderBundle):
            raise TypeError('provider_bundle must be a HealthProviderBundle')


def build_runtime_health_report(composition: HealthRuntimeComposition) -> dict[str, Any]:
    if not isinstance(composition, HealthRuntimeComposition):
        raise TypeError('composition must be a HealthRuntimeComposition')

    return {
        'runtime': composition.runtime_name,
        'health': health_bundle_report_payload(composition.provider_bundle),
    }
