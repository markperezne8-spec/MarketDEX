class SettlementEvidenceConflict(RuntimeError):
    pass


class SettlementRepository:
    """Append-only persistence boundary for settlement execution and evidence parent authority."""

    LINKAGE_STATUSES = ("", "UNMATCHED", "SINGLE_SALE_LINKED", "MULTI_SALE_PENDING_ALLOCATION", "ALLOCATED")
    SETTLEMENT_EVIDENCE_STATUSES = ("INTAKE", "EVIDENCE_COMPLETE", "CROSS_CHECK_PENDING", "VERIFIED", "EXCEPTION")
    SETTLEMENT_VERIFICATION_RESULTS = ("NOT READY", "PENDING", "SETTLEMENT VERIFIED", "SETTLEMENT EXCEPTION")

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
        if status == "MULTI_SALE_PENDING_ALLOCATION" and sale_id is not None:
            raise SettlementEvidenceConflict("Pending multi-sale linkage cannot assert a sale identity")
        if status == "ALLOCATED" and (sale_id is not None or group_id is None):
            raise SettlementEvidenceConflict("Allocated linkage requires allocation group identity")
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

    def verification_authority(self, c, settlement_evidence_id, *, expected_settlement_minor=None,
                               tolerance_minor=0):
        """Builds 487-497 read-only verification chain. It creates no settlement execution authority."""
        evidence = self.evidence_by_id(c, settlement_evidence_id)
        linkage = self.evidence_linkage_by_id(c, settlement_evidence_id)
        result = {
            "settlement_evidence_status": "INTAKE",
            "settlement_verification_result": "NOT READY",
            "cross_check_difference_minor": None,
            "verification_authority": "NO SETTLEMENT AUTHORITY — FAIL CLOSED",
        }
        if evidence is None or linkage is None:
            return result

        required_trace = (
            evidence["marketplace"], evidence["marketplace_settlement_reference"],
            evidence["settlement_date"], evidence["settlement_currency"],
            evidence["evidence_source_type"], evidence["evidence_source_reference"],
        )
        if not all(str(value).strip() for value in required_trace) or evidence["settlement_net_minor"] is None:
            return result

        status = str(linkage["linkage_status"]).strip().upper()
        sale_id = linkage["linked_sale_id"]
        group_id = linkage["allocation_group_id"]
        resolved = (
            status == "SINGLE_SALE_LINKED" and sale_id is not None and group_id is None
        ) or (
            status == "ALLOCATED" and sale_id is None and group_id is not None
        )
        if not resolved:
            result["settlement_evidence_status"] = "EVIDENCE_COMPLETE"
            return result

        result["settlement_evidence_status"] = "CROSS_CHECK_PENDING"
        if expected_settlement_minor is None:
            result["settlement_verification_result"] = "PENDING"
            return result
        try:
            expected = int(expected_settlement_minor)
            tolerance = int(tolerance_minor)
        except (TypeError, ValueError):
            return result
        if expected < 0 or tolerance < 0:
            return result

        difference = expected - int(evidence["settlement_net_minor"])
        result["cross_check_difference_minor"] = difference
        if abs(difference) <= tolerance:
            result["settlement_evidence_status"] = "VERIFIED"
            result["settlement_verification_result"] = "SETTLEMENT VERIFIED"
            result["verification_authority"] = "SETTLEMENT AUTHORITY ONLY — NO TAX OR SETTLEMENT COMPLETION AUTHORITY"
        else:
            result["settlement_evidence_status"] = "EXCEPTION"
            result["settlement_verification_result"] = "SETTLEMENT EXCEPTION"
        return result

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
