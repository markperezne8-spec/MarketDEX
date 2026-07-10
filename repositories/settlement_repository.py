class SettlementEvidenceConflict(RuntimeError):
    pass


class SettlementRepository:
    """Append-only persistence boundary for settlement execution and evidence parent authority."""

    LINKAGE_STATUSES = ("", "UNMATCHED", "SINGLE_SALE_LINKED", "MULTI_SALE_PENDING_ALLOCATION", "ALLOCATED")

    def append_evidence(self, c, *, settlement_evidence_id, marketplace,
                        marketplace_settlement_reference, settlement_date,
                        settlement_currency, evidence_source_type,
                        evidence_source_reference, settlement_net_minor,
                        evidence_status, verification_result, created_event_id,
                        created_at, settlement_gross_minor=None,
                        settlement_fee_minor=None, settlement_adjustment_minor=None):
        values = (
            settlement_evidence_id, marketplace, marketplace_settlement_reference,
            settlement_date, settlement_currency, evidence_source_type,
            evidence_source_reference, settlement_gross_minor, settlement_fee_minor,
            settlement_adjustment_minor, int(settlement_net_minor), evidence_status,
            verification_result, created_event_id, created_at,
        )
        prior = self.evidence_by_id(c, settlement_evidence_id)
        if prior is not None:
            columns = (
                "settlement_evidence_id", "marketplace", "marketplace_settlement_reference",
                "settlement_date", "settlement_currency", "evidence_source_type",
                "evidence_source_reference", "settlement_gross_minor", "settlement_fee_minor",
                "settlement_adjustment_minor", "settlement_net_minor", "evidence_status",
                "verification_result", "created_event_id", "created_at",
            )
            if tuple(prior[column] for column in columns) != values:
                raise SettlementEvidenceConflict("Contradictory settlement evidence blocked")
            return prior
        c.execute(
            """INSERT INTO settlement_evidence(
               settlement_evidence_id,marketplace,marketplace_settlement_reference,
               settlement_date,settlement_currency,evidence_source_type,
               evidence_source_reference,settlement_gross_minor,settlement_fee_minor,
               settlement_adjustment_minor,settlement_net_minor,evidence_status,
               verification_result,created_event_id,created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            values,
        )
        return self.evidence_by_id(c, settlement_evidence_id)

    def evidence_by_id(self, c, settlement_evidence_id):
        return c.execute(
            "SELECT * FROM settlement_evidence WHERE settlement_evidence_id=?",
            (settlement_evidence_id,),
        ).fetchone()

    def append_evidence_linkage(self, c, *, settlement_evidence_id, linkage_status,
                                created_event_id, created_at, linked_sale_id=None,
                                allocation_group_id=None):
        status = "" if linkage_status is None else str(linkage_status).strip().upper()
        sale_id = None if linked_sale_id is None or not str(linked_sale_id).strip() else str(linked_sale_id).strip()
        group_id = None if allocation_group_id is None or not str(allocation_group_id).strip() else str(allocation_group_id).strip()
        if status not in self.LINKAGE_STATUSES:
            raise SettlementEvidenceConflict("Non-canonical settlement linkage status blocked")
        if self.evidence_by_id(c, settlement_evidence_id) is None:
            raise SettlementEvidenceConflict("Settlement evidence parent required")
        if status in ("", "UNMATCHED") and (sale_id is not None or group_id is not None):
            raise SettlementEvidenceConflict("Contradictory settlement linkage identity blocked")
        if status == "SINGLE_SALE_LINKED" and (sale_id is None or group_id is not None):
            raise SettlementEvidenceConflict("Single-sale linkage requires exactly one sale identity")
        if status in ("MULTI_SALE_PENDING_ALLOCATION", "ALLOCATED") and (sale_id is not None or group_id is None):
            raise SettlementEvidenceConflict("Allocation linkage requires allocation group identity")
        values = (settlement_evidence_id, sale_id, group_id, status, created_event_id, created_at)
        prior = self.evidence_linkage_by_id(c, settlement_evidence_id)
        if prior is not None:
            columns = ("settlement_evidence_id", "linked_sale_id", "allocation_group_id", "linkage_status", "created_event_id", "created_at")
            if tuple(prior[column] for column in columns) != values:
                raise SettlementEvidenceConflict("Contradictory settlement linkage evidence blocked")
            return prior
        c.execute(
            """INSERT INTO settlement_evidence_linkage(
               settlement_evidence_id,linked_sale_id,allocation_group_id,linkage_status,
               created_event_id,created_at) VALUES (?,?,?,?,?,?)""",
            values,
        )
        return self.evidence_linkage_by_id(c, settlement_evidence_id)

    def evidence_linkage_by_id(self, c, settlement_evidence_id):
        return c.execute(
            "SELECT * FROM settlement_evidence_linkage WHERE settlement_evidence_id=?",
            (settlement_evidence_id,),
        ).fetchone()

    def append(self, c, *, settlement_id, sale_id, settlement_request_id,
               settlement_event_id, settlement_evidence_id, settlement_platform,
               observed_payout_minor, settlement_result, created_at):
        self.append_evidence(
            c,
            settlement_evidence_id=settlement_evidence_id,
            marketplace=settlement_platform,
            marketplace_settlement_reference=settlement_evidence_id,
            settlement_date=created_at,
            settlement_currency="USD",
            evidence_source_type="MANUAL_ENTRY",
            evidence_source_reference=settlement_evidence_id,
            settlement_net_minor=observed_payout_minor,
            evidence_status="VERIFIED",
            verification_result="VERIFIED",
            created_event_id=settlement_event_id,
            created_at=created_at,
        )
        values = (
            settlement_id, sale_id, settlement_request_id, settlement_event_id,
            settlement_evidence_id, settlement_platform, int(observed_payout_minor),
            settlement_result, created_at,
        )
        c.execute(
            """INSERT INTO settlement_executions(
               settlement_id,sale_id,settlement_request_id,settlement_event_id,
               settlement_evidence_id,settlement_platform,observed_payout_minor,
               settlement_result,created_at) VALUES (?,?,?,?,?,?,?,?,?)""",
            values,
        )
        c.execute(
            """INSERT INTO settlement_history(
               settlement_id,sale_id,settlement_request_id,settlement_event_id,
               settlement_evidence_id,settlement_platform,observed_payout_minor,
               settlement_result,recorded_at) VALUES (?,?,?,?,?,?,?,?,?)""",
            values,
        )

    def by_id(self, c, settlement_id):
        return c.execute(
            "SELECT * FROM settlement_executions WHERE settlement_id=?", (settlement_id,)
        ).fetchone()

    def by_sale_id(self, c, sale_id):
        return c.execute(
            "SELECT * FROM settlement_executions WHERE sale_id=?", (sale_id,)
        ).fetchone()

    def by_request_id(self, c, request_id):
        return c.execute(
            "SELECT * FROM settlement_executions WHERE settlement_request_id=?", (request_id,)
        ).fetchone()

    def history_for(self, c, settlement_id):
        return c.execute(
            "SELECT * FROM settlement_history WHERE settlement_id=? ORDER BY settlement_history_id",
            (settlement_id,),
        ).fetchall()
