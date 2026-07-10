class SettlementAllocationConflict(RuntimeError):
    pass


class SettlementAllocationRepository:
    """Append-only persistence for Build 498 settlement allocation evidence intake."""

    def parent_by_id(self, c, settlement_evidence_id):
        return c.execute(
            "SELECT * FROM settlement_evidence WHERE settlement_evidence_id=?",
            (settlement_evidence_id,),
        ).fetchone()

    def line_by_id(self, c, allocation_line_id):
        return c.execute(
            "SELECT * FROM settlement_allocation_evidence WHERE allocation_line_id=?",
            (allocation_line_id,),
        ).fetchone()

    def lines_for_group(self, c, allocation_group_id):
        return c.execute(
            "SELECT * FROM settlement_allocation_evidence WHERE allocation_group_id=? ORDER BY created_at, allocation_line_id",
            (allocation_group_id,),
        ).fetchall()

    def sale_marketplace(self, c, sale_id):
        row = c.execute(
            """SELECT marketplace FROM publication_lifecycle_events
               WHERE sale_id=? AND event_type='SOLD_CONVERSION'
               ORDER BY created_at DESC LIMIT 1""",
            (sale_id,),
        ).fetchone()
        return None if row is None else row["marketplace"]

    def append_line(self, c, *, allocation_group_id, allocation_line_id,
                    settlement_evidence_id, linked_sale_id, source_traceability,
                    evidence_date, currency, component_type, allocated_amount_minor,
                    notes, allocation_status, created_event_id, created_at):
        group_parent = c.execute(
            """SELECT settlement_evidence_id FROM settlement_allocation_evidence
               WHERE allocation_group_id=? LIMIT 1""",
            (allocation_group_id,),
        ).fetchone()
        if group_parent is not None and group_parent["settlement_evidence_id"] != settlement_evidence_id:
            raise SettlementAllocationConflict("Allocation group re-parenting blocked")

        values = (
            allocation_group_id, allocation_line_id, settlement_evidence_id,
            linked_sale_id, source_traceability, evidence_date, currency,
            component_type, allocated_amount_minor, notes, allocation_status,
            created_event_id, created_at,
        )
        prior = self.line_by_id(c, allocation_line_id)
        if prior is not None:
            columns = (
                "allocation_group_id", "allocation_line_id", "settlement_evidence_id",
                "linked_sale_id", "source_traceability", "evidence_date", "currency",
                "component_type", "allocated_amount_minor", "notes", "allocation_status",
                "created_event_id", "created_at",
            )
            if tuple(prior[column] for column in columns) != values:
                raise SettlementAllocationConflict("Contradictory allocation evidence blocked")
            return prior

        c.execute(
            """INSERT INTO settlement_allocation_evidence(
               allocation_group_id,allocation_line_id,settlement_evidence_id,
               linked_sale_id,source_traceability,evidence_date,currency,component_type,
               allocated_amount_minor,notes,allocation_status,created_event_id,created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            values,
        )
        return self.line_by_id(c, allocation_line_id)
