import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtWidgets import QApplication, QAbstractItemView

from composition.application_composition import ApplicationComposition
from market_intelligence.composition import MarketIntelligenceComposition
from ui.market_intelligence_workspace import MarketIntelligenceWorkspace
from ui.shell_workspace_catalog import MARKET_INTELLIGENCE_WORKSPACE_ID


def test_market_intelligence_workspace_is_read_only_and_offline_safe():
    app = QApplication.instance() or QApplication([])
    workspace = MarketIntelligenceWorkspace(MarketIntelligenceComposition())

    assert workspace.objectName() == 'marketIntelligenceWorkspace'
    assert workspace.results_table.columnCount() == 3
    assert workspace.results_table.rowCount() == 5
    assert workspace.results_table.editTriggers() == QAbstractItemView.NoEditTriggers
    assert workspace.status_label.text() == 'Market Intelligence is mounted in read-only offline mode.'
    assert workspace.results_table.item(0, 0).text() == 'Observation Gateway'
    assert workspace.results_table.item(0, 1).text() == '0 provider(s) registered'
    assert 'no live network calls' in workspace.results_table.item(0, 2).text()
    workspace.close()


def test_application_composition_mounts_market_intelligence_workspace(tmp_path):
    app = QApplication.instance() or QApplication([])
    composition = ApplicationComposition(tmp_path / 'marketdex.sqlite3')

    window = composition.build_main_window()

    assert isinstance(window.market_intelligence_workspace, MarketIntelligenceWorkspace)
    assert window.market_intelligence_workspace.intelligence is composition.market_intelligence
    assert MARKET_INTELLIGENCE_WORKSPACE_ID in window.workspace_host.workspace_ids

    window.workspace_host.activate(MARKET_INTELLIGENCE_WORKSPACE_ID)

    assert window.workspace_host.currentWidget() is window.market_intelligence_workspace
    assert window.workspace_host.workspace_context.text() == 'MARKET INTELLIGENCE'
    assert window.workspace_host.status_message.text() == 'Market Intelligence workspace active'
    window.close()
