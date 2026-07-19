from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CI_WORKFLOW = ROOT / '.github/workflows/ci.yml'

REQUIRED_JOB_IDS = (
    'core-tests',
    'collection',
    'market-intelligence',
    'reports',
    'inventory',
    'pricing',
    'listing',
    'mission-control-visual-slice',
    'desktop-build',
)

LINUX_JOB_CACHE_COUNT = 8


def _workflow_text():
    return CI_WORKFLOW.read_text(encoding='utf-8')


def test_ci_workflow_runs_for_pull_requests_and_main_pushes():
    workflow = _workflow_text()

    assert 'pull_request:' in workflow
    assert 'push:' in workflow
    assert 'branches: [main]' in workflow


def test_required_ci_jobs_remain_present():
    workflow = _workflow_text()

    missing_jobs = [
        job_id
        for job_id in REQUIRED_JOB_IDS
        if f'\n  {job_id}:\n' not in workflow
    ]

    assert not missing_jobs, ', '.join(missing_jobs)


def test_python_cache_dependency_paths_remain_explicit():
    workflow = _workflow_text()

    assert workflow.count('cache-dependency-path: requirements.txt') == LINUX_JOB_CACHE_COUNT
    assert (
        'cache-dependency-path: |\n'
        '            requirements-build.txt\n'
        '            requirements.txt'
    ) in workflow


def test_desktop_build_keeps_packaging_and_installer_gates():
    workflow = _workflow_text()
    desktop_build = workflow.split('\n  desktop-build:\n', 1)[1]

    required_markers = (
        'tests/test_ci_workflow_contract.py',
        'Run Desktop contract gate',
        'pyinstaller --noconfirm --clean MarketDEX.spec',
        'Verify packaged runtime',
        'Build MarketDEX installer',
        'Verify installed MarketDEX runtime',
        'Upload MarketDEX installer',
    )

    missing_markers = [
        marker
        for marker in required_markers
        if marker not in desktop_build
    ]

    assert not missing_markers, ', '.join(missing_markers)
