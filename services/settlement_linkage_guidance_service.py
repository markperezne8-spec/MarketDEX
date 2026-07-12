from dataclasses import dataclass
from typing import Mapping, Optional


@dataclass(frozen=True)
class SettlementLinkageGuidance:
    result: str
    guidance: str
    evidence_to_review: tuple[str, ...]
    authority: str = "ADVISORY ONLY — NO SETTLEMENT AUTHORITY"


class SettlementLinkageGuidanceService:
    """Read-only Build 486 guidance derived from canonical linkage evidence.

    This service does not persist, mutate, match, allocate, verify, reconcile, or
    complete settlement evidence. It only explains whether the supplied identity
    combination is internally consistent with the canonical linkage vocabulary.
    """

    CANONICAL_STATUSES = {
        "",
        "UNMATCHED",
        "SINGLE_SALE_LINKED",
        "MULTI_SALE_PENDING_ALLOCATION",
        "ALLOCATED",
    }

    def derive(
        self,
        linkage_status: Optional[str],
        linked_sale_id: Optional[str] = None,
        allocation_group_id: Optional[str] = None,
    ) -> SettlementLinkageGuidance:
        status = "" if linkage_status is None else str(linkage_status).strip().upper()
        sale_id = self._identity(linked_sale_id)
        group_id = self._identity(allocation_group_id)

        if status not in self.CANONICAL_STATUSES:
            return self._contradiction(
                "Replace the non-canonical linkage status with an approved status before review.",
                "linkage_status",
            )

        if status == "":
            if sale_id or group_id:
                return self._contradiction(
                    "Blank linkage status cannot assert a sale or allocation-group identity.",
                    "linkage_status",
                    "linked_sale_id" if sale_id else None,
                    "allocation_group_id" if group_id else None,
                )
            return SettlementLinkageGuidance(
                result="UNKNOWN",
                guidance="No linkage has been asserted. Review the settlement evidence before selecting a linkage status.",
                evidence_to_review=("linkage_status", "linked_sale_id", "allocation_group_id"),
            )

        if status == "UNMATCHED":
            if sale_id or group_id:
                return self._contradiction(
                    "UNMATCHED evidence cannot retain a sale or allocation-group identity.",
                    "linked_sale_id" if sale_id else None,
                    "allocation_group_id" if group_id else None,
                )
            return self._clear(
                "The evidence is consistently marked UNMATCHED. Review source evidence before creating a linkage."
            )

        if status == "SINGLE_SALE_LINKED":
            if not sale_id or group_id:
                return self._contradiction(
                    "SINGLE_SALE_LINKED requires exactly one Linked Sale ID and no Allocation Group ID.",
                    "linked_sale_id",
                    "allocation_group_id" if group_id else None,
                )
            return self._clear(
                "The settlement evidence is consistently linked to one sale. Review the Linked Sale ID before verification."
            )

        if status == "MULTI_SALE_PENDING_ALLOCATION":
            if sale_id:
                return self._contradiction(
                    "MULTI_SALE_PENDING_ALLOCATION cannot assert a single Linked Sale ID.",
                    "linked_sale_id",
                    "allocation_group_id",
                )
            return self._clear(
                "The evidence is consistently pending multi-sale allocation. Review or establish the Allocation Group ID."
            )

        if not group_id or sale_id:
            return self._contradiction(
                "ALLOCATED requires an Allocation Group ID and cannot assert a single Linked Sale ID.",
                "allocation_group_id",
                "linked_sale_id" if sale_id else None,
            )
        return self._clear(
            "The evidence is consistently allocated to a group. Review the Allocation Group ID and its allocation lines."
        )

    def derive_from_row(self, linkage: Optional[Mapping[str, object]]) -> SettlementLinkageGuidance:
        if linkage is None:
            return self.derive(None)
        return self.derive(
            linkage.get("linkage_status"),
            linkage.get("linked_sale_id"),
            linkage.get("allocation_group_id"),
        )

    @staticmethod
    def _identity(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None

    @staticmethod
    def _clear(guidance: str) -> SettlementLinkageGuidance:
        return SettlementLinkageGuidance(
            result="CLEAR",
            guidance=guidance,
            evidence_to_review=(),
        )

    @staticmethod
    def _contradiction(guidance: str, *fields: Optional[str]) -> SettlementLinkageGuidance:
        return SettlementLinkageGuidance(
            result="CONTRADICTION",
            guidance=guidance,
            evidence_to_review=tuple(field for field in fields if field),
        )
