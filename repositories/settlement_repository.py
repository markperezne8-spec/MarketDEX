class SettlementRepository:
    """Append-only persistence boundary for M39A settlement authority."""

    def append(self, c, *, settlement_id, sale_id, settlement_request_id,
               settlement_event_id, settlement_evidence_id, settlement_platform,
               observed_payout_minor, settlement_result, created_at):
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
