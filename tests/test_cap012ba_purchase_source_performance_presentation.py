from datetime import date
from dataclasses import FrozenInstanceError

import pytest

from reports.purchase_source_performance_calculator import PurchaseSourcePerformanceEvidence
from reports.purchase_source_performance_contract import PurchaseSourcePerformanceRequest
from reports.purchase_source_performance_presentation import (
    PurchaseSourcePerformancePresentation,
    present_purchase_source_performance,
)
from reports.purchase_source_performance_query import PurchaseSourcePerformanceQueryResponse


def _request() -> PurchaseSourcePerformanceRequest:
    return PurchaseSourcePerformanceRequest(
        period_start=date(2026, 1, 1),
        period_end=date(2026, 2, 1),
        as_of=date(2026, 2, 2),
        source_coverage_required=("inventory", "listing", "audit"),
    )


def _response() -> PurchaseSourcePerformanceQueryResponse:
    request = _request()
    evidence = (
        PurchaseSourcePerformanceEvidence(
            purchase_source_label=" Zeta ",
            acquired_units=10,
            completed_sale_units=4,
            source_domains=("inventory",),
            source_coverage=("complete",),
            provenance=("evidence:zeta",),
        ),
        PurchaseSourcePerformanceEvidence(
            purchase_source_label="Unavailable",
            acquired_units=None,
            completed_sale_units=None,
            source_domains=("inventory", "listing", "audit"),
            source_coverage=("unavailable",),
            provenance=("evidence:unavailable",),
            evidence_state="unavailable",
            reason="Source evidence is unavailable.",
        ),
    )
    return PurchaseSourcePerformanceQueryResponse(
        request=request,
        evidence=evidence,
        source_domains=("inventory", "listing", "audit"),
        source_coverage=("complete",),
        provenance=("query:sqlite",),
    )


def test_presentation_preserves_request_coverage_provenance_and_evidence_order() -> None:
    response = _response()

    presentation = present_purchase_source_performance(response)

    assert isinstance(presentation, PurchaseSourcePerformancePresentation)
    assert (presentation.period_start, presentation.period_end, presentation.as_of) == (
        date(2026, 1, 1), date(2026, 2, 1), date(2026, 2, 2)
    )
    assert presentation.source_coverage == ("complete",)
    assert presentation.provenance == ("query:sqlite",)
    assert [row.purchase_source_label for row in presentation.rows] == ["Unavailable", "Zeta"]
    assert presentation.rows[1].acquired_units == 10
    assert presentation.rows[1].completed_sale_units == 4
    assert presentation.rows[1].remaining_unsold_units is None
    assert presentation.rows[1].provenance == ("evidence:zeta",)


def test_presentation_keeps_unavailable_evidence_explicit_and_numeric_fields_empty() -> None:
    row = present_purchase_source_performance(_response()).rows[0]

    assert row.outcome == "unavailable"
    assert row.evidence_state == "unavailable"
    assert row.acquired_units is None
    assert row.completed_sale_units is None
    assert row.reason == "Source evidence is unavailable."


def test_presentation_is_immutable_and_rejects_wrong_response_type() -> None:
    presentation = present_purchase_source_performance(_response())

    with pytest.raises(FrozenInstanceError):
        presentation.rows = ()
    with pytest.raises(TypeError):
        present_purchase_source_performance(object())
