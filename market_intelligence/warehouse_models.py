from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from types import MappingProxyType
from typing import Mapping

from market_intelligence.observations import ObservationKind


def _required_text(field_name: str, value: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f'{field_name} must not be empty')
    return normalized


def _required_datetime(field_name: str, value: datetime) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f'{field_name} must be a datetime')
    return value


@dataclass(frozen=True)
class WarehouseSource:
    source_id: str
    display_name: str
    source_type: str
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, 'source_id', _required_text('source_id', self.source_id))
        object.__setattr__(self, 'display_name', _required_text('display_name', self.display_name))
        object.__setattr__(self, 'source_type', _required_text('source_type', self.source_type))
        object.__setattr__(self, 'metadata', MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class ObservationProvenance:
    provenance_id: str
    source_id: str
    captured_at: datetime
    dataset_version: str | None = None
    external_reference: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, 'provenance_id', _required_text('provenance_id', self.provenance_id))
        object.__setattr__(self, 'source_id', _required_text('source_id', self.source_id))
        object.__setattr__(self, 'captured_at', _required_datetime('captured_at', self.captured_at))
        if self.dataset_version is not None:
            object.__setattr__(self, 'dataset_version', _required_text('dataset_version', self.dataset_version))
        if self.external_reference is not None:
            object.__setattr__(self, 'external_reference', _required_text('external_reference', self.external_reference))
        object.__setattr__(self, 'metadata', MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class WarehouseObservation:
    observation_id: str
    product_id: str
    provenance_id: str
    kind: ObservationKind
    observed_at: datetime
    value: Decimal
    confidence: float
    currency: str | None = None
    sample_size: int | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, 'observation_id', _required_text('observation_id', self.observation_id))
        object.__setattr__(self, 'product_id', _required_text('product_id', self.product_id))
        object.__setattr__(self, 'provenance_id', _required_text('provenance_id', self.provenance_id))
        if not isinstance(self.kind, ObservationKind):
            raise TypeError('kind must be an ObservationKind')
        object.__setattr__(self, 'observed_at', _required_datetime('observed_at', self.observed_at))
        object.__setattr__(self, 'value', Decimal(str(self.value)))
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError('confidence must be between 0 and 1')
        if self.currency is not None:
            object.__setattr__(self, 'currency', _required_text('currency', self.currency).upper())
        if self.sample_size is not None and self.sample_size < 0:
            raise ValueError('sample_size must not be negative')
        object.__setattr__(self, 'metadata', MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class WarehouseSnapshot:
    snapshot_id: str
    captured_at: datetime
    observation_ids: tuple[str, ...]
    label: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, 'snapshot_id', _required_text('snapshot_id', self.snapshot_id))
        object.__setattr__(self, 'captured_at', _required_datetime('captured_at', self.captured_at))
        normalized_ids = tuple(_required_text('observation_id', value) for value in self.observation_ids)
        if len(normalized_ids) != len(set(normalized_ids)):
            raise ValueError('observation_ids must not contain duplicates')
        object.__setattr__(self, 'observation_ids', normalized_ids)
        if self.label is not None:
            object.__setattr__(self, 'label', _required_text('label', self.label))
        object.__setattr__(self, 'metadata', MappingProxyType(dict(self.metadata)))
