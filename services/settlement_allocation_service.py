from repositories.settlement_allocation_repository import SettlementAllocationRepository


class SettlementAllocationNotReady(RuntimeError):
    pass


class SettlementAllocationService:
    """Build 498 intake authority. Cross-check authority is intentionally out of scope."""

    def __init__(self, database, repository=None):
        self.database = database
        self.repository = repository or SettlementAllocationRepository()

    @staticmethod
    def _required(value):
        return value is not None and str(value).strip() != ""

    def record_evidence(self, *, allocation_group_id, allocation_line_id,
                        settlement_evidence_id, source_traceability, evidence_date,
                        currency, component_type, created_event_id, created_at,
                        linked_sale_id=None, allocated_amount_minor=None, notes=""):
        required = (
            allocation_group_id, allocation_line_id, settlement_evidence_id,
            source_traceability, evidence_date, currency, component_type,
            created_event_id, created_at,
        )
        if not all(self._required(value) for value in required):
            raise SettlementAllocationNotReady("NOT READY: required allocation evidence is blank")
        if currency != "USD":
            raise SettlementAllocationNotReady("NOT READY: unsupported allocation currency")
        if allocated_amount_minor is not None:
            allocated_amount_minor = int(allocated_amount_minor)

        with self.database.transaction() as c:
            parent = self.repository.parent_by_id(c, settlement_evidence_id)
            if parent is None:
                raise SettlementAllocationNotReady("NOT READY: settlement evidence parent is missing")

            status = "PENDING EVIDENCE"
            if linked_sale_id is not None and str(linked_sale_id).strip() != "":
                sale_marketplace = self.repository.sale_marketplace(c, linked_sale_id)
                if sale_marketplace is None or sale_marketplace != parent["marketplace"]:
                    status = "ALLOCATION EXCEPTION"
                elif allocated_amount_minor is not None:
                    status = "READY FOR CROSS-CHECK"

            return self.repository.append_line(
                c,
                allocation_group_id=allocation_group_id,
                allocation_line_id=allocation_line_id,
                settlement_evidence_id=settlement_evidence_id,
                linked_sale_id=linked_sale_id,
                source_traceability=source_traceability,
                evidence_date=evidence_date,
                currency=currency,
                component_type=component_type,
                allocated_amount_minor=allocated_amount_minor,
                notes=notes or "",
                allocation_status=status,
                created_event_id=created_event_id,
                created_at=created_at,
            )
