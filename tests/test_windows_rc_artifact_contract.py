from pathlib import Path


def test_windows_rc_workflow_publishes_verified_executable():
    workflow = Path('.github/workflows/windows-rc-package-gate.yml').read_text(encoding='utf-8')

    verify_at = workflow.index('Verify packaged executable')
    publish_at = workflow.index('Publish Windows RC executable')
    assert verify_at < publish_at
    assert 'actions/upload-artifact@v4' in workflow
    assert 'name: MarketDEX-Windows-RC' in workflow
    assert 'path: dist/MarketDEX.exe' in workflow
    assert 'if-no-files-found: error' in workflow
