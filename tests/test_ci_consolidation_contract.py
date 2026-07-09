from pathlib import Path


RETIRED_DUPLICATE_WORKFLOWS = (
    'viewport-fit-gate.yml',
    'listing-plan-queue-gate.yml',
    'listing-plan-queue-contract-gate.yml',
    'listing-plan-persistence-gate.yml',
    'operator-sale-completion-gate.yml',
)

PRESERVED_TESTS = (
    'test_viewport_fit_feature.py',
    'test_inventory_listing_plan_queue_ui.py',
    'test_listing_plan_queue_contract.py',
    'test_listing_plan_repository.py',
    'test_inventory_listing_plan_ui.py',
    'test_operator_sale_completion.py',
    'test_operator_recorded_listing_outcome.py',
)


def test_consolidated_ci_runs_complete_pytest_suite():
    workflow = Path('.github/workflows/marketdex-ci.yml').read_text(encoding='utf-8')

    assert 'name: MarketDEX CI' in workflow
    assert 'name: Permanent Codebase Verification' in workflow
    assert 'run: python -m pytest -q' in workflow
    assert 'cancel-in-progress: true' in workflow


def test_second_retirement_batch_removes_only_duplicate_workflow_triggers():
    workflow_dir = Path('.github/workflows')
    test_dir = Path('tests')

    for workflow_name in RETIRED_DUPLICATE_WORKFLOWS:
        assert not (workflow_dir / workflow_name).exists()
    for test_name in PRESERVED_TESTS:
        assert (test_dir / test_name).is_file()


def test_manual_windows_delivery_remains_separate():
    assert Path('.github/workflows/windows-rc-delivery.yml').is_file()
