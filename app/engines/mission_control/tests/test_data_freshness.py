import pytest

from app.engines.mission_control.data_freshness import (
    DATA_FRESHNESS_DOMAIN_ORDER,
    build_data_freshness_view_model,
    data_freshness_evidence,
)


def _evidence(domain, *, state='ready'):
    return data_freshness_evidence(
        domain,
        state=state,
        source_authority='Prepared local authority',
        as_of_label='As of prepared snapshot',
        freshness_label='Prepared local freshness',
        detail='Read-only freshness evidence.',
    )


def test_missing_evidence_is_unavailable_in_stable_order():
    model = build_data_freshness_view_model()

    assert model.state == 'unavailable'
    assert tuple(item.domain for item in model.domains) == (
        *DATA_FRESHNESS_DOMAIN_ORDER,
    )
    assert all(item.state == 'unavailable' for item in model.domains)


def test_complete_injected_evidence_is_ready_and_reordered():
    evidence = tuple(
        _evidence(domain)
        for domain in reversed(DATA_FRESHNESS_DOMAIN_ORDER)
    )

    model = build_data_freshness_view_model(evidence=evidence)

    assert model.state == 'ready'
    assert tuple(item.domain for item in model.domains) == (
        *DATA_FRESHNESS_DOMAIN_ORDER,
    )


def test_missing_or_partial_evidence_is_partial():
    model = build_data_freshness_view_model(
        evidence=(_evidence('inventory'), _evidence('reports', state='partial'))
    )

    assert model.state == 'partial'
    assert model.domains[2].state == 'unavailable'
    assert model.domains[1].state == 'partial'


def test_error_text_is_error_safe():
    model = build_data_freshness_view_model(
        error_text='Prepared freshness evidence failed.'
    )

    assert model.state == 'error'
    assert model.error_text == 'Prepared freshness evidence failed.'


def test_outputs_are_immutable():
    model = build_data_freshness_view_model()

    with pytest.raises((AttributeError, TypeError)):
        model.state = 'ready'


def test_duplicates_and_invalid_inputs_are_rejected():
    with pytest.raises(ValueError, match='at most once'):
        build_data_freshness_view_model(
            evidence=(_evidence('inventory'), _evidence('inventory'))
        )
    with pytest.raises(ValueError):
        _evidence('unknown')
    with pytest.raises(TypeError):
        build_data_freshness_view_model(evidence=[])


def test_required_freshness_authority_fields_are_validated():
    with pytest.raises(ValueError):
        data_freshness_evidence(
            'inventory',
            state='ready',
            source_authority='',
            as_of_label='As of snapshot',
            freshness_label='Fresh',
            detail='Detail',
        )
