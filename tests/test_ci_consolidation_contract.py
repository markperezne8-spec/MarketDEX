from pathlib import Path


RETIRED_DUPLICATE_WORKFLOWS = (
    'viewport-fit-gate.yml',
    'listing-plan-queue-gate.yml',
    'listing-plan-queue-contract-gate.yml',
    'listing-plan-persistence-gate.yml',
    'operator-sale-completion-gate.yml',
    'm45-m49-authority-gate.yml',
    'm50-authority-gate.yml',
    'm56-m60-authority-gate.yml',
    'm61-m65-authority-gate.yml',
    'm66-m70-authority-gate.yml',
    'm76-m80-authority-gate.yml',
    'm81-m85-authority-gate.yml',
    'm106-m110-contract-gate.yml',
    'm116-m120-contract-gate.yml',
    'm151-m155-contract-gate.yml',
)

PRESERVED_TESTS = (
    'test_viewport_fit_feature.py',
    'test_inventory_listing_plan_queue_ui.py',
    'test_listing_plan_queue_contract.py',
    'test_listing_plan_repository.py',
    'test_inventory_listing_plan_ui.py',
    'test_operator_sale_completion.py',
    'test_operator_recorded_listing_outcome.py',
    'test_m45_m49_operating_command_chain.py',
    'test_m50_execution_feedback_authority.py',
    'test_m56_m60_continuous_business_loop.py',
    'test_m61_m65_autonomous_business_cycle.py',
    'test_m66_m70_strategic_control_loop.py',
    'test_m76_m80_enterprise_governance_loop.py',
    'test_m81_m85_executive_control_cycle.py',
    'test_m106_m110_executive_continuity_cycle.py',
    'test_m116_m120_executive_perpetuity_cycle.py',
    'test_m151_m155_executive_accountability_cycle.py',
)


def test_consolidated_ci_runs_complete_pytest_suite():
    workflow = Path('.github/workflows/marketdex-ci.yml').read_text(encoding='utf-8')

    assert 'name: MarketDEX CI' in workflow
    assert 'name: Permanent Codebase Verification' in workflow
    assert 'run: python -m pytest -q' in workflow
    assert 'cancel-in-progress: true' in workflow


def test_controlled_retirement_batches_remove_only_duplicate_workflow_triggers():
    workflow_dir = Path('.github/workflows')
    test_dir = Path('tests')

    for workflow_name in RETIRED_DUPLICATE_WORKFLOWS:
        assert not (workflow_dir / workflow_name).exists()
    for test_name in PRESERVED_TESTS:
        assert (test_dir / test_name).is_file()


def test_manual_windows_delivery_remains_separate():
    assert Path('.github/workflows/windows-rc-delivery.yml').is_file()
