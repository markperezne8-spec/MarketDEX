import sqlite3
from typing import Optional

from core.database_manager import DatabaseManager
from repositories.settlement_allocation_repository import SettlementAllocationRepository


class SettlementAllocationNotReady(RuntimeError):
    pass


class SettlementAllocationService:
    """Builds 498-500 settlement allocation authority."""

    def __init__(self, database: DatabaseManager, repository: Optional[SettlementAllocationRepository] = None) -> None:
        self.database = database
        self.repository = repository or SettlementAllocationRepository()

    @staticmethod
    def _required(value: object) -> bool:
        return value is not None and str(value).strip() != ""

    def record_evidence(self, *, allocation_group_id: str, allocation_line_id: str, settlement_evidence_id: str,
                        source_traceability: str, evidence_date: str, currency: str, component_type: str,
                        created_event_id: str, created_at: str, linked_sale_id: Optional[str] = None,
                        allocated_amount_minor: Optional[int] = None, notes: str = "") -> sqlite3.Row:
        required = (allocation_group_id, allocation_line_id, settlement_evidence_id, source_traceability,
                    evidence_date, currency, component_type, created_event_id, created_at)
        if not all(self._required(value) for value in required):
            raise SettlementAllocationNotReady("NOT READY: required allocation evidence is blank")
        if currency != "USD":
            raise SettlementAllocationNotReady("NOT READY: unsupported allocation currency")
        normalized_sale_id = None if not self._required(linked_sale_id) else str(linked_sale_id).strip()
        if allocated_amount_minor is None or not self._required(allocated_amount_minor):
            normalized_amount = None
        else:
            try:
                normalized_amount = int(allocated_amount_minor)
            except (TypeError, ValueError) as exc:
                raise SettlementAllocationNotReady("NOT READY: allocated amount evidence is invalid") from exc
        with self.database.transaction() as c:
            parent = self.repository.parent_by_id(c, settlement_evidence_id)
            if parent is None:
                raise SettlementAllocationNotReady("NOT READY: settlement evidence parent is missing")
            status = "PENDING EVIDENCE"
            if normalized_sale_id is not None:
                sale_marketplace = self.repository.sale_marketplace(c, normalized_sale_id)
                if sale_marketplace is None or sale_marketplace != parent["marketplace"]:
                    status = "ALLOCATION EXCEPTION"
                elif normalized_amount is not None:
                    status = "READY FOR CROSS-CHECK"
            return self.repository.append_line(c, allocation_group_id=allocation_group_id,
                allocation_line_id=allocation_line_id, settlement_evidence_id=settlement_evidence_id,
                linked_sale_id=normalized_sale_id, source_traceability=source_traceability,
                evidence_date=evidence_date, currency=currency, component_type=component_type,
                allocated_amount_minor=normalized_amount, notes=notes or "", allocation_status=status,
                created_event_id=created_event_id, created_at=created_at)

    def cross_check_group(self, *, cross_check_id: str, allocation_group_id: str,
                          created_event_id: str, created_at: str) -> sqlite3.Row:
        required = (cross_check_id, allocation_group_id, created_event_id, created_at)
        if not all(self._required(value) for value in required):
            raise SettlementAllocationNotReady("NOT READY: required cross-check evidence is blank")
        with self.database.transaction() as c:
            lines = self.repository.lines_for_group(c, allocation_group_id)
            if not lines:
                raise SettlementAllocationNotReady("NOT READY: allocation group is missing")
            parent_ids = {str(line["settlement_evidence_id"]) for line in lines}
            if len(parent_ids) != 1:
                raise SettlementAllocationNotReady("NOT READY: allocation group parent identity is inconsistent")
            settlement_evidence_id = next(iter(parent_ids))
            parent = self.repository.parent_by_id(c, settlement_evidence_id)
            if parent is None:
                raise SettlementAllocationNotReady("NOT READY: settlement evidence parent is missing")
            if any(line["allocation_status"] != "READY FOR CROSS-CHECK" for line in lines):
                raise SettlementAllocationNotReady("NOT READY: allocation group contains ineligible line status")
            if any(line["allocated_amount_minor"] is None for line in lines):
                raise SettlementAllocationNotReady("NOT READY: allocation group contains unknown amount evidence")
            group_total = sum(int(line["allocated_amount_minor"]) for line in lines)
            settlement_net = int(parent["settlement_net_minor"])
            remainder = settlement_net - group_total
            status = "ALLOCATION CROSS-CHECKED" if remainder == 0 else "ALLOCATION EXCEPTION"
            return self.repository.append_cross_check(c, cross_check_id=cross_check_id,
                allocation_group_id=allocation_group_id, settlement_evidence_id=settlement_evidence_id,
                allocation_group_total_minor=group_total, settlement_net_minor=settlement_net,
                allocation_remainder_minor=remainder, cross_check_status=status,
                created_event_id=created_event_id, created_at=created_at)

    def record_sale_attribution_readiness(self, *, readiness_event_id: str, allocation_group_id: str,
                                          sale_id: str, recorded_at: str) -> sqlite3.Row:
        required = (readiness_event_id, allocation_group_id, sale_id, recorded_at)
        if not all(self._required(value) for value in required):
            raise SettlementAllocationNotReady("NOT READY: required settlement attribution evidence is blank")
        with self.database.transaction() as c:
            lines = self.repository.lines_for_group(c, allocation_group_id)
            if not lines:
                raise SettlementAllocationNotReady("NOT READY: allocation group is missing")
            sale_lines = [line for line in lines if line["linked_sale_id"] == sale_id]
            if not sale_lines:
                raise SettlementAllocationNotReady("NOT READY: sale is not linked to allocation evidence")
            if any(line["allocation_status"] != "READY FOR CROSS-CHECK" for line in sale_lines):
                raise SettlementAllocationNotReady("NOT READY: sale allocation line is ineligible")
            if any(line["allocated_amount_minor"] is None for line in sale_lines):
                raise SettlementAllocationNotReady("NOT READY: sale allocation amount is unknown")
            parent_ids = {str(line["settlement_evidence_id"]) for line in lines}
            if len(parent_ids) != 1:
                raise SettlementAllocationNotReady("NOT READY: allocation group parent identity is inconsistent")
            parent_id = next(iter(parent_ids))
            parent = self.repository.parent_by_id(c, parent_id)
            if parent is None:
                raise SettlementAllocationNotReady("NOT READY: settlement evidence parent is missing")
            sale_marketplace = self.repository.sale_marketplace(c, sale_id)
            if sale_marketplace is None or sale_marketplace != parent["marketplace"]:
                raise SettlementAllocationNotReady("NOT READY: sale linkage authority is inconsistent")
            cross_check = self.repository.latest_cross_check_for_group(c, allocation_group_id)
            if cross_check is None or cross_check["settlement_evidence_id"] != parent_id:
                raise SettlementAllocationNotReady("NOT READY: matching allocation cross-check authority is missing")
            if cross_check["cross_check_status"] != "ALLOCATION CROSS-CHECKED" or int(cross_check["allocation_remainder_minor"]) != 0:
                raise SettlementAllocationNotReady("NOT READY: allocation group is not cross-checked to zero remainder")
            return self.repository.append_attribution_readiness(c, event_id=readiness_event_id,
                sale_id=sale_id, allocation_group_id=allocation_group_id, recorded_at=recorded_at)
