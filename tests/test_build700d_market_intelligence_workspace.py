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
    assert workspace.readiness_table.columnCount() == 3
    assert workspace.readiness_table.rowCount() == 6
    assert workspace.evidence_table.rowCount() == 3
    assert workspace.signal_table.rowCount() == 1
    assert workspace.readiness_table.editTriggers() == QAbstractItemView.NoEditTriggers
    assert workspace.status_label.text().endswith('fixture evidence only.')
    assert workspace.readiness_table.item(0, 0).text() == 'Observation Gateway'
    assert workspace.readiness_table.item(0, 1).text() == '1 provider(s) registered'
    assert 'fixture only' in workspace.readiness_table.item(0, 2).text()

    readiness_rows = {
        workspace.readiness_table.item(row, 0).text(): (
            workspace.readiness_table.item(row, 1).text(),
            workspace.readiness_table.item(row, 2).text(),
        )
        for row in range(workspace.readiness_table.rowCount())
    }
    query_status, query_boundary = readiness_rows['Research Query Catalog']
    assert query_status == '1 saved query definition(s)'
    assert 'in-memory' in query_boundary
    assert 'non-persistent' in query_boundary

    evidence_rows = {
        workspace.evidence_table.item(row, 0).text(): workspace.evidence_table.item(row, 1).text()
        for row in range(workspace.evidence_table.rowCount())
    }
    assert evidence_rows['Mega Evolution ETB'] == 'USD 89.99'
    assert workspace.signal_table.item(0, 0).text() == 'Demand signal increased'
    assert workspace.visualization_status.text().startswith('Catalog definition: Daily Market Volume')
    assert workspace.price_bar.value() == 89
    assert workspace.volume_bar.value() == 100
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
