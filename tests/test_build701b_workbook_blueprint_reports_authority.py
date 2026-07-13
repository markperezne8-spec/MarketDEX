from pathlib import Path


BLUEPRINT_PATH = Path('WorkbookBlueprint.md')
WORKFLOW_PATH = Path('docs/WORKFLOW.md')
REPORTS_ARCHITECTURE_PATH = Path('docs/Architecture/BUILD_701_REPORTS_FOUNDATION.md')


def test_governed_workbook_blueprint_is_present() -> None:
    content = BLUEPRINT_PATH.read_text(encoding='utf-8')

    assert '**Permanent Filename:** `WorkbookBlueprint.md`' in content
    assert '## 📊 Analytics Responsibility' in content
    assert 'What patterns does the business history reveal?' in content


def test_workflow_uses_governed_blueprint_filename() -> None:
    content = WORKFLOW_PATH.read_text(encoding='utf-8')

    assert '`WorkbookBlueprint.md`' in content
    assert 'Workbook_Blueprint.md' not in content


def test_reports_architecture_preserves_workbook_analytics_authority() -> None:
    content = REPORTS_ARCHITECTURE_PATH.read_text(encoding='utf-8')

    assert 'Workbook-backed Reports responsibility' in content
    assert 'Current State, Event History, Snapshots, Decision History, and Outcomes' in content
    assert 'charts explain, tables prove, and history remembers' in content
    assert 'missing evidence is unavailable, not zero' in content
    assert 'Build 701C may introduce' in content
