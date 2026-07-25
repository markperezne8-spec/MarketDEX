from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from reports.purchase_source_performance_calculator import (
    PurchaseSourcePerformanceEvidence,
)
from reports.purchase_source_performance_contract import (
    PurchaseSourcePerformanceRequest,
)


@dataclass(frozen=True, slots=True)
class PurchaseSourcePerformanceQueryResponse:
    """Immutable read-only response for one Purchase Source Performance request."""

    request: PurchaseSourcePerformanceRequest
    evidence: tuple[PurchaseSourcePerformanceEvidence, ...]
    source_domains: tuple[str, ...]
    source_coverage: tuple[str, ...]
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.request, PurchaseSourcePerformanceRequest):
            raise TypeError('request must be a PurchaseSourcePerformanceRequest')
        if not isinstance(self.evidence, tuple) or any(
            not isinstance(item, PurchaseSourcePerformanceEvidence)
            for item in self.evidence
        ):
            raise TypeError('evidence must be a tuple of PurchaseSourcePerformanceEvidence values')
        if not self.source_domains or not self.source_coverage or not self.provenance:
            raise ValueError('source domains, coverage, and provenance are required')
        object.__setattr__(
            self,
            'evidence',
            tuple(
                sorted(
                    self.evidence,
                    key=lambda item: (
                        item.purchase_source_label.casefold(),
                        item.purchase_source_label,
                        item.evidence_state,
                    ),
                )
            ),
        )
        object.__setattr__(self, 'source_domains', tuple(self.source_domains))
        object.__setattr__(self, 'source_coverage', tuple(self.source_coverage))
        object.__setattr__(self, 'provenance', tuple(self.provenance))


@runtime_checkable
class PurchaseSourcePerformanceEvidenceProvider(Protocol):
    """Read-only boundary for future purchase-source evidence providers."""

    def get_purchase_source_performance_evidence(
        self,
        request: PurchaseSourcePerformanceRequest,
    ) -> PurchaseSourcePerformanceQueryResponse:
        """Return immutable evidence for one validated request without mutation."""


class PurchaseSourcePerformanceQueryService:
    """Fail-closed query boundary around an injected evidence provider."""

    def __init__(self, provider: PurchaseSourcePerformanceEvidenceProvider) -> None:
        self._provider = provider

    def get_evidence_for_request(
        self,
        request: PurchaseSourcePerformanceRequest,
    ) -> PurchaseSourcePerformanceQueryResponse:
        if not isinstance(request, PurchaseSourcePerformanceRequest):
            raise TypeError('request must be a PurchaseSourcePerformanceRequest')

        try:
            response = self._provider.get_purchase_source_performance_evidence(request)
        except Exception:
            return self._unavailable_response(request, 'Purchase Source Performance provider unavailable')

        if not isinstance(response, PurchaseSourcePerformanceQueryResponse):
            return self._unavailable_response(request, 'Purchase Source Performance provider returned unsupported response')
        if response.request != request:
            return self._unavailable_response(request, 'Purchase Source Performance provider returned mismatched request')
        return response

    @staticmethod
    def _unavailable_response(
        request: PurchaseSourcePerformanceRequest,
        reason: str,
    ) -> PurchaseSourcePerformanceQueryResponse:
        evidence = PurchaseSourcePerformanceEvidence(
            purchase_source_label='Unavailable',
            acquired_units=None,
            completed_sale_units=None,
            source_domains=('inventory', 'listing', 'audit'),
            source_coverage=('unavailable',),
            provenance=('purchase-source-performance-query-boundary:provider-unavailable',),
            evidence_state='unavailable',
            reason=reason,
        )
        return PurchaseSourcePerformanceQueryResponse(
            request=request,
            evidence=(evidence,),
            source_domains=('inventory', 'listing', 'audit'),
            source_coverage=('unavailable',),
            provenance=('purchase-source-performance-query-boundary:provider-unavailable',),
        )
