from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from core.database_manager import DatabaseManager
from core.inventory_acquisition_projection import (
    InventoryAcquisitionProjectionAvailable,
    InventoryAcquisitionProjectionConflict,
    InventoryAcquisitionProjectionCoverage,
    InventoryAcquisitionProjectionDiagnostic,
    InventoryAcquisitionProjectionRecord,
    InventoryAcquisitionProjectionRequest,
    InventoryAcquisitionProjectionResult,
    InventoryAcquisitionProjectionUnavailable,
)


@dataclass(frozen=True)
class _Evidence:
    evidence_id: str
    asset_id: str
    acquired_units: int
    acquisition_date: date
    source_label: str
    provenance: str
    supersedes_id: str | None
    recorded_at: datetime


class SqliteInventoryAcquisitionProjectionRepository:
    SOURCE_SYSTEM = 'sqlite.inventory_acquisition_evidence'

    def __init__(self, database_manager: DatabaseManager) -> None:
        self._database_manager = database_manager

    def read_inventory_acquisition_projection(self, request: InventoryAcquisitionProjectionRequest) -> InventoryAcquisitionProjectionResult:
        if not isinstance(request, InventoryAcquisitionProjectionRequest):
            raise TypeError('request must be an InventoryAcquisitionProjectionRequest')
        try:
            with self._database_manager.read_connection() as connection:
                rows = tuple(connection.execute('SELECT acquisition_evidence_id,asset_id,acquired_units,acquisition_date,purchase_source_label,provenance_reference,supersedes_acquisition_evidence_id,recorded_at FROM inventory_acquisition_evidence WHERE recorded_at <= ? ORDER BY recorded_at,acquisition_evidence_id',(request.as_of.isoformat(),)).fetchall())
        except Exception:
            return InventoryAcquisitionProjectionUnavailable(request=request,diagnostic=InventoryAcquisitionProjectionDiagnostic('sqlite_inventory_acquisition_read_unavailable','canonical acquisition evidence read failed'))
        try:
            evidence = tuple(self._decode(row) for row in rows)
            selected = self._select(evidence, request)
        except ValueError as exc:
            return self._conflict(request,'inventory_acquisition_lifecycle_conflict',str(exc))
        records = tuple(InventoryAcquisitionProjectionRecord(inventory_id=item.asset_id,acquired_units=item.acquired_units,acquisition_date=item.acquisition_date,purchase_source_label=item.source_label) for item in selected)
        coverage=InventoryAcquisitionProjectionCoverage(request.period_start,request.period_end,request.as_of)
        provenance=tuple(value for item in selected for value in (f'{self.SOURCE_SYSTEM}:{item.evidence_id}',f'provenance:{item.provenance}')) or (f'{self.SOURCE_SYSTEM}:empty',)
        return InventoryAcquisitionProjectionAvailable(request=request,coverage=coverage,records=records,provenance=provenance)

    @staticmethod
    def _decode(row: Any) -> _Evidence:
        evidence_id=str(row['acquisition_evidence_id']).strip(); asset_id=str(row['asset_id']).strip(); label=str(row['purchase_source_label']).strip(); provenance=str(row['provenance_reference']).strip()
        if not evidence_id or not asset_id or not label or not provenance: raise ValueError('missing acquisition evidence identity, asset, source, or provenance')
        if type(row['acquired_units']) is not int or row['acquired_units']<=0: raise ValueError(f'invalid acquired units for {evidence_id}')
        raw_date=str(row['acquisition_date']); parsed_date=date.fromisoformat(raw_date)
        if parsed_date.isoformat()!=raw_date: raise ValueError(f'invalid acquisition date for {evidence_id}')
        recorded=datetime.fromisoformat(str(row['recorded_at']))
        if recorded.tzinfo is None or recorded.utcoffset() is None: raise ValueError(f'recorded_at must be timezone-aware for {evidence_id}')
        supersedes=None if row['supersedes_acquisition_evidence_id'] is None else str(row['supersedes_acquisition_evidence_id']).strip()
        if supersedes=='': raise ValueError(f'blank supersession for {evidence_id}')
        return _Evidence(evidence_id,asset_id,row['acquired_units'],parsed_date,label,provenance,supersedes,recorded)

    @classmethod
    def _select(cls,evidence: tuple[_Evidence,...],request: InventoryAcquisitionProjectionRequest) -> tuple[_Evidence,...]:
        by_id={item.evidence_id:item for item in evidence}
        if len(by_id)!=len(evidence): raise ValueError('duplicate acquisition evidence identity')
        children: dict[str,list[_Evidence]]={}
        for item in evidence:
            if item.supersedes_id is None: continue
            parent=by_id.get(item.supersedes_id)
            if parent is None: raise ValueError(f'dangling supersession for {item.evidence_id}')
            if parent.asset_id!=item.asset_id: raise ValueError(f'cross-asset supersession for {item.evidence_id}')
            if item.recorded_at<=parent.recorded_at: raise ValueError(f'non-increasing supersession for {item.evidence_id}')
            children.setdefault(parent.evidence_id,[]).append(item)
        if any(len(values)>1 for values in children.values()): raise ValueError('branching supersession')
        for item in evidence:
            seen=set(); current=item
            while current.supersedes_id is not None:
                if current.evidence_id in seen: raise ValueError('cyclic supersession')
                seen.add(current.evidence_id); current=by_id[current.supersedes_id]
        terminals=tuple(item for item in evidence if item.evidence_id not in children)
        selected=[]
        for asset_id in sorted({item.asset_id for item in terminals}):
            candidates=tuple(item for item in terminals if item.asset_id==asset_id)
            in_period=tuple(item for item in candidates if request.period_start<=item.acquisition_date<request.period_end and item.acquisition_date<=request.as_of.date())
            if len(in_period)>1: raise ValueError(f'multiple eligible acquisition evidence for {asset_id}')
            if in_period: selected.append(in_period[0])
        return tuple(sorted(selected,key=lambda item:(item.acquisition_date,item.asset_id,item.source_label.casefold(),item.source_label)))

    @staticmethod
    def _conflict(request,reason_code,message):
        return InventoryAcquisitionProjectionConflict(request=request,diagnostic=InventoryAcquisitionProjectionDiagnostic(reason_code,message))
