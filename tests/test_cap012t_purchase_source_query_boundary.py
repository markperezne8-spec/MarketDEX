from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from reports.purchase_source_performance_calculator import PurchaseSourcePerformanceEvidence
from reports.purchase_source_performance_contract import PurchaseSourcePerformanceRequest
from reports.purchase_source_performance_query import (
    PurchaseSourcePerformanceQueryResponse,
    PurchaseSourcePerformanceQueryService,
)


def _request() -> PurchaseSourcePerformanceRequest:
    return PurchaseSourcePerformanceRequest(
        period_start=date(2026, 1, 1),
        period_end=date(2026, 2, 1),
        as_of=date(2026, 2, 1),
        source_coverage_required=('inventory', 'listing', 'audit'),
    )


def _evidence(label: str, state: str = 'valid') -> PurchaseSourcePerformanceEvidence:
    return PurchaseSourcePerformanceEvidence(
        purchase_source_label=label,
        acquired_units=10 if state == 'valid' else None,
        completed_sale_units=5 if state == 'valid' else None,
        source_domains=('inventory', 'listing', 'audit'),
        source_coverage=('complete',) if state == 'valid' else (state,),
        provenance=(f'test:{label}',),
        evidence_state=state,
    )


class _Provider:
    def __init__(self, response):
        self.response = response

    def get_purchase_source_performance_evidence(self, request):
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


def test_query_response_is_frozen_and_deterministically_orders_exact_labels():
    request = _request()
    response = PurchaseSourcePerformanceQueryResponse(
        request=request,
        evidence=(_evidence(' Walmart '), _evidence('eBay'), _evidence('Target')),
        source_domains=('inventory', 'listing', 'audit'),
        source_coverage=('complete',),
        provenance=('test:query',),
    )

    assert [item.purchase_source_label for item in response.evidence] == ['eBay', 'Target', 'Walmart']
    with pytest.raises(FrozenInstanceError):
        response.provenance = ('changed',)


def test_query_service_returns_matching_immutable_response():
    request = _request()
    response = PurchaseSourcePerformanceQueryResponse(
        request=request,
        evidence=(_evidence('Target'),),
        source_domains=('inventory', 'listing', 'audit'),
        source_coverage=('complete',),
        provenance=('test:query',),
    )

    assert PurchaseSourcePerformanceQueryService(_Provider(response)).get_evidence_for_request(request) == response


@pytest.mark.parametrize('provider_value', [RuntimeError('offline'), object()])
def test_query_service_fails_closed_for_provider_failure_or_unsupported_response(provider_value):
    request = _request()
    response = PurchaseSourcePerformanceQueryService(_Provider(provider_value)).get_evidence_for_request(request)

    assert response.request == request
    assert len(response.evidence) == 1
    assert response.evidence[0].evidence_state == 'unavailable'
    assert response.evidence[0].acquired_units is None
    assert response.evidence[0].completed_sale_units is None


def test_query_service_fails_closed_for_mismatched_request():
    request = _request()
    other_request = PurchaseSourcePerformanceRequest(
        period_start=date(2026, 2, 1),
        period_end=date(2026, 3, 1),
        as_of=date(2026, 3, 1),
        source_coverage_required=('inventory', 'listing', 'audit'),
    )
    response = PurchaseSourcePerformanceQueryResponse(
        request=other_request,
        evidence=(_evidence('Target', 'conflicting'),),
        source_domains=('inventory', 'listing', 'audit'),
        source_coverage=('conflicting',),
        provenance=('test:mismatch',),
    )

    result = PurchaseSourcePerformanceQueryService(_Provider(response)).get_evidence_for_request(request)
    assert result.request == request
    assert result.evidence[0].evidence_state == 'unavailable'


def test_query_service_rejects_wrong_request_type():
    with pytest.raises(TypeError):
        PurchaseSourcePerformanceQueryService(_Provider(None)).get_evidence_for_request(object())
