from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class InventoryAcquisitionProjectionState(str, Enum):
    AVAILABLE = 'available'
    UNAVAILABLE = 'unavailable'
    CONFLICTING = 'conflicting'


@dataclass(frozen=True, slots=True)
class InventoryAcquisitionProjectionRequest:
    period_start: date
    period_end: date
    as_of: datetime

    def __post_init__(self) -> None:
        if type(self.period_start) is not date or type(self.period_end) is not date:
            raise TypeError('period_start and period_end must be dates')
        if type(self.as_of) is not datetime or self.as_of.tzinfo is None or self.as_of.utcoffset() is None:
            raise TypeError('as_of must be a timezone-aware datetime')
        if self.period_start >= self.period_end:
            raise ValueError('period_start must precede period_end')
        if self.as_of.date() < self.period_start:
            raise ValueError('as_of must not precede period_start')


@dataclass(frozen=True, slots=True)
class InventoryAcquisitionProjectionRecord:
    inventory_id: str
    acquired_units: int
    acquisition_date: date
    purchase_source_label: str

    def __post_init__(self) -> None:
        inventory_id = str(self.inventory_id).strip()
        label = str(self.purchase_source_label).strip()
        if not inventory_id:
            raise ValueError('inventory_id is required')
        if type(self.acquired_units) is not int or self.acquired_units <= 0:
            raise ValueError('acquired_units must be a positive integer')
        if type(self.acquisition_date) is not date:
            raise TypeError('acquisition_date must be a date')
        if not label:
            raise ValueError('purchase_source_label is required')
        object.__setattr__(self, 'inventory_id', inventory_id)
        object.__setattr__(self, 'purchase_source_label', label)


@dataclass(frozen=True, slots=True)
class InventoryAcquisitionProjectionCoverage:
    period_start: date
    period_end: date
    as_of: datetime
    completeness: str = 'complete'

    def __post_init__(self) -> None:
        InventoryAcquisitionProjectionRequest(self.period_start, self.period_end, self.as_of)
        completeness = str(self.completeness).strip().lower()
        if completeness != 'complete':
            raise ValueError('coverage completeness must be complete')
        object.__setattr__(self, 'completeness', completeness)


@dataclass(frozen=True, slots=True)
class InventoryAcquisitionProjectionDiagnostic:
    reason_code: str
    message: str
    inventory_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        reason_code = str(self.reason_code).strip()
        message = str(self.message).strip()
        if not reason_code or not message:
            raise ValueError('reason_code and message are required')
        if not isinstance(self.inventory_ids, tuple):
            raise TypeError('inventory_ids must be a tuple')
        normalized = tuple(str(value).strip() for value in self.inventory_ids)
        if any(not value for value in normalized):
            raise ValueError('inventory_ids must not contain blank values')
        object.__setattr__(self, 'reason_code', reason_code)
        object.__setattr__(self, 'message', message)
        object.__setattr__(self, 'inventory_ids', normalized)


@dataclass(frozen=True, slots=True)
class InventoryAcquisitionProjectionAvailable:
    request: InventoryAcquisitionProjectionRequest
    coverage: InventoryAcquisitionProjectionCoverage
    records: tuple[InventoryAcquisitionProjectionRecord, ...]
    provenance: tuple[str, ...]
    state: InventoryAcquisitionProjectionState = InventoryAcquisitionProjectionState.AVAILABLE

    def __post_init__(self) -> None:
        if not isinstance(self.request, InventoryAcquisitionProjectionRequest):
            raise TypeError('request must be an InventoryAcquisitionProjectionRequest')
        if not isinstance(self.coverage, InventoryAcquisitionProjectionCoverage):
            raise TypeError('coverage must be InventoryAcquisitionProjectionCoverage')
        if (self.coverage.period_start, self.coverage.period_end, self.coverage.as_of) != (
            self.request.period_start, self.request.period_end, self.request.as_of,
        ):
            raise ValueError('coverage must exactly match request boundaries')
        if not isinstance(self.records, tuple) or any(
            not isinstance(record, InventoryAcquisitionProjectionRecord) for record in self.records
        ):
            raise TypeError('records must be a tuple of InventoryAcquisitionProjectionRecord')
        inventory_ids = tuple(record.inventory_id for record in self.records)
        if len(set(inventory_ids)) != len(inventory_ids):
            raise ValueError('duplicate canonical inventory identity')
        for record in self.records:
            if record.acquisition_date < self.request.period_start or record.acquisition_date >= self.request.period_end:
                raise ValueError('acquisition_date falls outside the requested period')
            if record.acquisition_date > self.request.as_of.date():
                raise ValueError('acquisition_date exceeds as_of')
        ordered = tuple(sorted(
            self.records,
            key=lambda record: (
                record.acquisition_date,
                record.inventory_id,
                record.purchase_source_label.casefold(),
                record.purchase_source_label,
            ),
        ))
        if not isinstance(self.provenance, tuple) or not self.provenance or any(not str(value).strip() for value in self.provenance):
            raise ValueError('provenance must be a non-empty tuple of non-blank values')
        object.__setattr__(self, 'records', ordered)
        object.__setattr__(self, 'provenance', tuple(str(value).strip() for value in self.provenance))


@dataclass(frozen=True, slots=True)
class InventoryAcquisitionProjectionUnavailable:
    request: InventoryAcquisitionProjectionRequest
    diagnostic: InventoryAcquisitionProjectionDiagnostic
    state: InventoryAcquisitionProjectionState = InventoryAcquisitionProjectionState.UNAVAILABLE


@dataclass(frozen=True, slots=True)
class InventoryAcquisitionProjectionConflict:
    request: InventoryAcquisitionProjectionRequest
    diagnostic: InventoryAcquisitionProjectionDiagnostic
    state: InventoryAcquisitionProjectionState = InventoryAcquisitionProjectionState.CONFLICTING


InventoryAcquisitionProjectionResult = (
    InventoryAcquisitionProjectionAvailable
    | InventoryAcquisitionProjectionUnavailable
    | InventoryAcquisitionProjectionConflict
)
