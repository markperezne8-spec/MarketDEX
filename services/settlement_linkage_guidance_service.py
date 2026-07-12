class SettlementLinkageGuidanceService:
    """Read-only Build 486 guidance for settlement linkage evidence.

    This service derives operator advice only. It does not write evidence or create
    settlement, allocation, reconciliation, tax, or completion authority.
    """

    CANONICAL_STATUSES = {
        "",
        "UNMATCHED",
        "SINGLE_SALE_LINKED",
        "MULTI_SALE_PENDING_ALLOCATION",
        "ALLOCATED",
    }

    AUTHORITY = "ADVISORY ONLY — NO SETTLEMENT AUTHORITY"

    @staticmethod
    def _identity(value):
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None

    def derive(self, *, linkage_status=None, linked_sale_id=None, allocation_group_id=None):
        status = "" if linkage_status is None else str(linkage_status).strip().upper()
        sale_id = self._identity(linked_sale_id)
        group_id = self._identity(allocation_group_id)

        result = {
            "contradiction_result": "CLEAR",
            "resolution_guidance": "Linkage evidence is internally consistent; no correction is required.",
            "review_fields": (),
            "guidance_authority": self.AUTHORITY,
        }

        if status == "" and sale_id is None and group_id is None:
            result.update(
                contradiction_result="UNKNOWN",
                resolution_guidance="No linkage has been asserted. Review settlement evidence before selecting a canonical linkage status.",
                review_fields=("linkage_status",),
            )
            return result

        if status not in self.CANONICAL_STATUSES:
            result.update(
                contradiction_result="CONTRADICTION",
                resolution_guidance="Replace the non-canonical linkage status with an approved settlement linkage status.",
                review_fields=("linkage_status",),
            )
            return result

        if status in ("", "UNMATCHED") and (sale_id is not None or group_id is not None):
            result.update(
                contradiction_result="CONTRADICTION",
                resolution_guidance="Blank or UNMATCHED linkage cannot assert a sale or allocation group. Clear the identities or choose the matching canonical status.",
                review_fields=("linkage_status", "linked_sale_id", "allocation_group_id"),
            )
        elif status == "SINGLE_SALE_LINKED" and (sale_id is None or group_id is not None):
            result.update(
                contradiction_result="CONTRADICTION",
                resolution_guidance="SINGLE_SALE_LINKED requires exactly one Linked Sale ID and no Allocation Group ID.",
                review_fields=("linked_sale_id", "allocation_group_id"),
            )
        elif status == "MULTI_SALE_PENDING_ALLOCATION" and sale_id is not None:
            result.update(
                contradiction_result="CONTRADICTION",
                resolution_guidance="MULTI_SALE_PENDING_ALLOCATION cannot assert a single Linked Sale ID. Clear it and review the allocation-group evidence.",
                review_fields=("linked_sale_id", "allocation_group_id"),
            )
        elif status == "ALLOCATED" and (sale_id is not None or group_id is None):
            result.update(
                contradiction_result="CONTRADICTION",
                resolution_guidance="ALLOCATED requires an Allocation Group ID and no Linked Sale ID.",
                review_fields=("linked_sale_id", "allocation_group_id"),
            )

        return result
