class SettlementEvidenceConflict(RuntimeError):
    pass


class SettlementRepository:
    """Append-only persistence boundary for settlement execution and evidence parent authority."""

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
