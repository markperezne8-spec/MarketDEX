from datetime import datetime
from inspect import signature
from pathlib import Path
from typing import get_type_hints

from market_intelligence.warehouse_repositories import (
    ObservationRepository,
    PreviewHistoryRepository,
    SnapshotRepository,
    SourceRepository,
)


def test_repository_protocols_are_runtime_checkable_contracts():
    class EmptyRepository:
        pass

    assert not isinstance(EmptyRepository(), ObservationRepository)
    assert not isinstance(EmptyRepository(), SourceRepository)
    assert not isinstance(EmptyRepository(), SnapshotRepository)
    assert not isinstance(EmptyRepository(), PreviewHistoryRepository)


def test_observation_repository_keeps_append_and_read_responsibilities_explicit():
    assert set(ObservationRepository.__dict__) >= {'append', 'get', 'list_for_product'}
    parameters = signature(ObservationRepository.list_for_product).parameters
    assert {'product_id', 'source_id', 'kind', 'observed_from', 'observed_to'} <= set(parameters)


def test_source_snapshot_and_preview_contracts_are_separate():
    assert set(SourceRepository.__dict__) >= {
        'register_source',
        'register_provenance',
        'get_source',
        'get_provenance',
    }
    assert set(SnapshotRepository.__dict__) >= {'append', 'get', 'list_captured_between'}
    assert set(PreviewHistoryRepository.__dict__) >= {'list_observations'}
    assert 'append' not in PreviewHistoryRepository.__dict__


def test_read_contracts_return_immutable_tuples():
    observation_hints = get_type_hints(ObservationRepository.list_for_product)
    snapshot_hints = get_type_hints(SnapshotRepository.list_captured_between)
    preview_hints = get_type_hints(PreviewHistoryRepository.list_observations)

    assert observation_hints['return'].__origin__ is tuple
    assert snapshot_hints['return'].__origin__ is tuple
    assert preview_hints['return'].__origin__ is tuple


def test_repository_interface_module_has_no_persistence_implementation_imports():
    source = Path('market_intelligence/warehouse_repositories.py').read_text(encoding='utf-8')
    forbidden = ('sqlite3', 'sqlalchemy', 'CREATE TABLE', 'INSERT INTO', 'requests', 'httpx')
    for token in forbidden:
        assert token not in source


def test_repository_time_filters_use_datetime_contracts():
    hints = get_type_hints(SnapshotRepository.list_captured_between)
    assert datetime in hints['captured_from'].__args__
    assert datetime in hints['captured_to'].__args__
