from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from market_intelligence.observations import ObservationKind
from market_intelligence.warehouse_models import (
    ObservationProvenance,
    WarehouseObservation,
    WarehouseSnapshot,
    WarehouseSource,
)


NOW = datetime(2026, 7, 13, 1, 0, tzinfo=timezone.utc)


def test_warehouse_models_are_immutable_and_normalized():
    source = WarehouseSource(
        source_id=' fixture-source ',
        display_name=' Offline Fixture ',
        source_type=' fixture ',
        metadata={'mode': 'offline'},
    )
    provenance = ObservationProvenance(
        provenance_id=' provenance-001 ',
        source_id=source.source_id,
        captured_at=NOW,
        dataset_version=' v1 ',
    )
    observation = WarehouseObservation(
        observation_id=' observation-001 ',
        product_id=' SAMPLE-MEGA-ETB ',
        provenance_id=provenance.provenance_id,
        kind=ObservationKind.MARKET_PRICE,
        observed_at=NOW,
        value='89.99',
        confidence=0.92,
        currency=' usd ',
        sample_size=18,
        metadata={'fixture': 'true'},
    )
    snapshot = WarehouseSnapshot(
        snapshot_id=' snapshot-001 ',
        captured_at=NOW,
        observation_ids=(observation.observation_id,),
        label=' Daily sample ',
    )

    assert source.source_id == 'fixture-source'
    assert provenance.dataset_version == 'v1'
    assert observation.product_id == 'SAMPLE-MEGA-ETB'
    assert observation.value == Decimal('89.99')
    assert observation.currency == 'USD'
    assert snapshot.observation_ids == ('observation-001',)
    assert snapshot.label == 'Daily sample'

    with pytest.raises(TypeError):
        source.metadata['mode'] = 'live'
    with pytest.raises(FrozenInstanceError):
        observation.confidence = 1.0


def test_warehouse_observation_validates_domain_boundaries():
    with pytest.raises(ValueError, match='product_id must not be empty'):
        WarehouseObservation(
            observation_id='obs-1',
            product_id=' ',
            provenance_id='prov-1',
            kind=ObservationKind.MARKET_PRICE,
            observed_at=NOW,
            value='1.00',
            confidence=0.5,
        )

    with pytest.raises(ValueError, match='confidence must be between 0 and 1'):
        WarehouseObservation(
            observation_id='obs-1',
            product_id='product-1',
            provenance_id='prov-1',
            kind=ObservationKind.MARKET_PRICE,
            observed_at=NOW,
            value='1.00',
            confidence=1.1,
        )

    with pytest.raises(TypeError, match='kind must be an ObservationKind'):
        WarehouseObservation(
            observation_id='obs-1',
            product_id='product-1',
            provenance_id='prov-1',
            kind='market-price',
            observed_at=NOW,
            value='1.00',
            confidence=0.5,
        )


def test_warehouse_snapshot_rejects_duplicate_membership():
    with pytest.raises(ValueError, match='observation_ids must not contain duplicates'):
        WarehouseSnapshot(
            snapshot_id='snapshot-1',
            captured_at=NOW,
            observation_ids=('obs-1', 'obs-1'),
        )


def test_warehouse_models_remain_persistence_agnostic():
    source = WarehouseSource('source-1', 'Offline Source', 'fixture')

    assert not hasattr(source, 'save')
    assert not hasattr(source, 'delete')
    assert not hasattr(source, 'connection')
