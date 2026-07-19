from uuid import uuid4
from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QLabel,QPushButton,QGridLayout,QGroupBox,QHBoxLayout,QTableWidget,QTableWidgetItem,QDialog,QFormLayout,QLineEdit,QComboBox,QSpinBox,QDoubleSpinBox,QDialogButtonBox,QMessageBox,QFileDialog,QAbstractItemView,QSizePolicy
from services.inventory_csv_import_service import InventoryCsvImportService
from ui.design_system.qt_theme import build_marketdex_qss
from ui.design_system.tokens import NorthStarPanelTone, build_visual_north_star_tokens
from ui.design_system.widgets import MarketDEXDashboardPanel,MarketDEXKpiCard,MarketDEXStatusBadge,MarketDEXWorkspaceHeader,StatusTone
from ui.header_status_band import HeaderStatusBand
from ui.health_status_card import HealthStatusCard
from ui.business_scoreboard_panel import BusinessScoreboardPanel
from ui.capital_health_panel import CapitalHealthPanel
from ui.next_steps_panel import NextStepsPanel
from ui.opportunity_risk_panel import OpportunityRiskPanel
from ui.visual_intelligence_panel import VisualIntelligencePanel
from ui.operational_status_strip import OperationalStatusStrip
from ui.todays_top3_panel import TodaysTop3Panel
from app.engines.health.status_view_model import HealthStatusViewModel
from app.engines.mission_control.capital_health import CapitalHealthViewModel
from app.engines.mission_control.business_scoreboard import BusinessScoreboardViewModel
from app.engines.mission_control.header_status import HeaderStatusViewModel
from app.engines.mission_control.next_steps import NextStepReadinessViewModel
from app.engines.mission_control.opportunity_risk import OpportunityRiskViewModel
from app.engines.mission_control.visual_intelligence import VisualIntelligenceViewModel
from app.engines.mission_control.operational_status import OperationalStatusViewModel
from app.engines.mission_control.todays_top3 import TodaysTop3ViewModel


class AddAssetDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent); self.setWindowTitle('Add Inventory Asset'); form=QFormLayout(self); self.name=QLineEdit(); self.asset_type=QComboBox(); self.asset_type.addItems(['SINGLE','SEALED','SLAB','ACCESSORY']); self.quantity=QSpinBox(); self.quantity.setRange(0,100000); self.quantity.setValue(1); self.cost=QDoubleSpinBox(); self.cost.setRange(0,1000000); self.cost.setDecimals(2); self.cost.setPrefix('$'); self.purchase_date=QLineEdit(); self.purchase_date.setPlaceholderText('YYYY-MM-DD'); self.purchase_source=QLineEdit(); self.storage_location=QLineEdit(); self.notes=QLineEdit(); form.addRow('Asset Name',self.name); form.addRow('Asset Type',self.asset_type); form.addRow('Quantity',self.quantity); form.addRow('Total Cost',self.cost); form.addRow('Purchase Date',self.purchase_date); form.addRow('Purchase Source',self.purchase_source); form.addRow('Storage Location',self.storage_location); form.addRow('Notes',self.notes); buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel); buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); form.addRow(buttons)


class AdjustAssetDialog(QDialog):
    def __init__(self,detail,parent=None):
        super().__init__(parent); self.setWindowTitle('Adjust Inventory Asset'); form=QFormLayout(self); form.addRow('Asset',QLabel(detail['asset_name'])); form.addRow('Current Quantity',QLabel(str(detail['quantity']))); form.addRow('Current Cost',QLabel(f"${detail['total_cost_minor']/100:,.2f}")); self.quantity_delta=QSpinBox(); self.quantity_delta.setRange(-100000,100000); self.quantity_delta.setPrefix('Delta '); self.cost_delta=QDoubleSpinBox(); self.cost_delta.setRange(-1000000,1000000); self.cost_delta.setDecimals(2); self.cost_delta.setPrefix('Delta $'); form.addRow('Quantity Adjustment',self.quantity_delta); form.addRow('Cost Adjustment',self.cost_delta); buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel); buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); form.addRow(buttons)


class BulkAdjustDialog(QDialog):
    def __init__(self,selected_count,parent=None):
        super().__init__(parent); self.setWindowTitle('Bulk Adjust Inventory'); form=QFormLayout(self); form.addRow('Selected Assets',QLabel(f'{selected_count:,}')); self.quantity_delta=QSpinBox(); self.quantity_delta.setRange(-100000,100000); self.quantity_delta.setPrefix('Delta '); self.cost_delta=QDoubleSpinBox(); self.cost_delta.setRange(-1000000,1000000); self.cost_delta.setDecimals(2); self.cost_delta.setPrefix('Delta $'); form.addRow('Quantity Delta Per Asset',self.quantity_delta); form.addRow('Cost Adjustment',self.cost_delta); buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel); buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); form.addRow(buttons)


class MainWindow(QMainWindow):
    def __init__(self,service,inventory_service,health_status_view_model: HealthStatusViewModel | None = None,operational_status_view_model: OperationalStatusViewModel | None = None,next_steps_view_model: NextStepReadinessViewModel | None = None,header_status_view_model: HeaderStatusViewModel | None = None,todays_top3_view_model: TodaysTop3ViewModel | None = None,capital_health_view_model: CapitalHealthViewModel | None = None,opportunity_risk_view_model: OpportunityRiskViewModel | None = None,business_scoreboard_view_model: BusinessScoreboardViewModel | None = None,visual_intelligence_view_model: VisualIntelligenceViewModel | None = None):
        super().__init__(); self.service=service; self.inventory_service=inventory_service; self.inventory_import_service=InventoryCsvImportService(inventory_service); self.inventory_rows=[]; self.inventory_view='ACTIVE'; self.setWindowTitle('MarketDEX OS — Mission Control'); self.resize(1280,800)
        self.setStyleSheet(build_marketdex_qss(build_visual_north_star_tokens()))
        self._health_status_view_model=health_status_view_model
        self._operational_status_view_model=operational_status_view_model
        self._next_steps_view_model=next_steps_view_model
        self._header_status_view_model=header_status_view_model
        self._todays_top3_view_model=todays_top3_view_model
        self._capital_health_view_model=capital_health_view_model
        self._opportunity_risk_view_model=opportunity_risk_view_model
        self._business_scoreboard_view_model=business_scoreboard_view_model
        self._visual_intelligence_view_model=visual_intelligence_view_model
        root=QWidget(); root.setObjectName('marketdexAppRoot'); outer=QHBoxLayout(root); panel=QWidget(); panel.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred); self.inventory_panel=panel; layout=QVBoxLayout(panel); outer.addWidget(panel,1)
        self.mission_control_header=MarketDEXWorkspaceHeader('MarketDEX OS','MISSION CONTROL — LIVE SQLITE BUSINESS SNAPSHOT'); layout.addWidget(self.mission_control_header)
        self.values={}; self.dashboard_grid_shell=self._build_dashboard_grid_shell(); layout.addWidget(self.dashboard_grid_shell); inventory_header=QHBoxLayout(); self.inventory_header=inventory_header; inventory_header.addWidget(QLabel('📦 INVENTORY')); inventory_header.addStretch(1)
        import_button=QPushButton('Import CSV'); import_button.clicked.connect(self.import_inventory); inventory_header.addWidget(import_button); export_button=QPushButton('Export CSV'); export_button.clicked.connect(self.export_inventory); inventory_header.addWidget(export_button); self.view_button=QPushButton('View Archived'); self.view_button.clicked.connect(self.toggle_inventory_view); inventory_header.addWidget(self.view_button); self.adjust_button=QPushButton('Adjust Selected'); self.adjust_button.setEnabled(False); self.adjust_button.clicked.connect(self.adjust_selected); inventory_header.addWidget(self.adjust_button); self.bulk_adjust_button=QPushButton('Bulk Adjust'); self.bulk_adjust_button.setEnabled(False); self.bulk_adjust_button.clicked.connect(self.bulk_adjust_selected); inventory_header.addWidget(self.bulk_adjust_button); self.archive_button=QPushButton('Archive Selected'); self.archive_button.setEnabled(False); self.archive_button.clicked.connect(self.archive_selected); inventory_header.addWidget(self.archive_button); self.restore_button=QPushButton('Restore Selected'); self.restore_button.setEnabled(False); self.restore_button.clicked.connect(self.restore_selected); inventory_header.addWidget(self.restore_button); add_button=QPushButton('+ Add Asset'); add_button.clicked.connect(self.add_asset); inventory_header.addWidget(add_button); layout.addLayout(inventory_header)
        filter_bar=QHBoxLayout(); self.inventory_search=QLineEdit(); self.inventory_search.setPlaceholderText('Search inventory by asset name...'); self.inventory_search.textChanged.connect(self.refresh_inventory); filter_bar.addWidget(self.inventory_search); self.inventory_type_filter=QComboBox(); self.inventory_type_filter.addItems(['ALL','SINGLE','SEALED','SLAB','ACCESSORY']); self.inventory_type_filter.currentTextChanged.connect(self.refresh_inventory); filter_bar.addWidget(self.inventory_type_filter); layout.addLayout(filter_bar)
        sort_bar=QHBoxLayout(); sort_bar.addWidget(QLabel('Sort by')); self.inventory_sort=QComboBox(); self.inventory_sort.addItems(['NAME','TYPE','QUANTITY','TOTAL COST']); self.inventory_sort.currentTextChanged.connect(self.refresh_inventory); sort_bar.addWidget(self.inventory_sort); self.inventory_sort_order=QComboBox(); self.inventory_sort_order.addItems(['ASC','DESC']); self.inventory_sort_order.currentTextChanged.connect(self.refresh_inventory); sort_bar.addWidget(self.inventory_sort_order); sort_bar.addStretch(1); layout.addLayout(sort_bar)
        summary_bar=QHBoxLayout(); self.inventory_summary={}
        for label,key in (('Assets','asset_count'),('Units','total_units'),('Filtered Cost','total_cost_minor')): box=QGroupBox(label); box_layout=QVBoxLayout(box); value=QLabel('--'); value.setStyleSheet('font-size:18px;font-weight:700'); box_layout.addWidget(value); self.inventory_summary[key]=value; summary_bar.addWidget(box)
        layout.addLayout(summary_bar); self.inventory_table=QTableWidget(0,4); self.inventory_table.setHorizontalHeaderLabels(['Asset','Type','Qty','Total Cost']); self.inventory_table.setEditTriggers(QTableWidget.NoEditTriggers); self.inventory_table.setSelectionBehavior(QTableWidget.SelectRows); self.inventory_table.setSelectionMode(QAbstractItemView.ExtendedSelection); self.inventory_table.itemSelectionChanged.connect(self.show_selected); self.inventory_table.setMinimumHeight(180); self.inventory_table.setMaximumHeight(320); layout.addWidget(self.inventory_table); self.inventory_result=QLabel(''); layout.addWidget(self.inventory_result); self.asset_detail=QLabel('Select an inventory asset to view details.'); self.asset_detail.setWordWrap(True); layout.addWidget(self.asset_detail); self.refresh_button=QPushButton('Refresh MarketDEX'); self.refresh_button.clicked.connect(self.refresh); layout.addWidget(self.refresh_button); self.footer=QLabel('Loading MarketDEX business authority...'); self.footer.setWordWrap(True); layout.addWidget(self.footer); self.setCentralWidget(root); self.refresh()

    @staticmethod
    def _money(minor): return f'${minor/100:,.2f}'

    @staticmethod
    def _detail_value(value): return str(value).strip() if str(value or '').strip() else '—'

    @property
    def dashboard_grid_visual_contract(self): return 'm1.14e-north-star-dashboard-grid-shell'

    @property
    def inventory_command_center_visual_contract(self): return 'm1.14f-inventory-command-center-shell'

    @property
    def visual_intelligence_visual_contract(self): return 'm1.14g-visual-intelligence-shell'

    def _build_dashboard_grid_shell(self):
        shell=MarketDEXDashboardPanel('Dashboard Grid','Read-only command-center snapshot',tone=NorthStarPanelTone.COMMAND)
        shell.setObjectName('marketdexDashboardPanel')
        shell.setProperty('dashboardRole','dashboard-grid-shell')
        shell.setProperty('visualContract',self.dashboard_grid_visual_contract)
        shell.setAccessibleName('Mission Control dashboard grid shell. Read-only command-center snapshot.')
        badge=MarketDEXStatusBadge('Read-only',StatusTone.INFORMATION,shell); shell.add_header_action(badge)
        grid=QGridLayout(); grid.setContentsMargins(0,0,0,0); grid.setHorizontalSpacing(10); grid.setVerticalSpacing(10); self.dashboard_grid=grid
        cards=(('📦 Inventory Units','inventory_units'),('🗂️ Inventory Assets','inventory_asset_count'),('💰 Inventory Cost','inventory_cost_minor'),('🧾 Completed Sales','completed_sales'),('📈 Revenue','revenue_minor'),('💵 Profit','profit_minor'),('🛡️ Verified Audits','verified_audits'),('⚙️ Authority Events','authority_events'))
        for index,(label,key) in enumerate(cards):
            card=MarketDEXKpiCard(label,'--'); card.setProperty('dashboardRole','existing-kpi'); self.values[key]=card.value_widget; grid.addWidget(card,index//2,index%2)
        self.inventory_command_center=self._build_inventory_command_center()
        grid.addWidget(self.inventory_command_center,4,0,1,2)
        self.visual_intelligence_shell=self._build_visual_intelligence_shell()
        grid.addWidget(self.visual_intelligence_shell,5,0,1,2)
        shell.content_layout.addLayout(grid)
        return shell

    def _build_inventory_command_center(self):
        panel=MarketDEXDashboardPanel('Inventory Command Center','Read-only local inventory command snapshot',tone=NorthStarPanelTone.INVENTORY)
        panel.setObjectName('marketdexDashboardPanel')
        panel.setProperty('dashboardRole','inventory-command-center-shell')
        panel.setProperty('visualContract',self.inventory_command_center_visual_contract)
        panel.setAccessibleName('Inventory Command Center. Read-only local inventory command snapshot.')
        panel.add_header_action(MarketDEXStatusBadge('Local summary',StatusTone.POSITIVE,panel))
        summary_grid=QGridLayout(); summary_grid.setContentsMargins(0,0,0,0); summary_grid.setHorizontalSpacing(10); summary_grid.setVerticalSpacing(8)
        self.inventory_command_values={}
        for index,(label,key) in enumerate((('Units','inventory_units'),('Assets','inventory_asset_count'),('Cost','inventory_cost_minor'))):
            card=MarketDEXKpiCard(label,'--',panel); card.setProperty('dashboardRole','inventory-command-summary'); self.inventory_command_values[key]=card.value_widget; summary_grid.addWidget(card,0,index)
        placeholder_grid=QGridLayout(); placeholder_grid.setContentsMargins(0,0,0,0); placeholder_grid.setHorizontalSpacing(10); placeholder_grid.setVerticalSpacing(8); self.inventory_command_placeholder_grid=placeholder_grid
        for index,title in enumerate(('Listing readiness','Inventory age','Storage review','Audit coverage')):
            placeholder_grid.addWidget(self._build_inventory_command_placeholder(title),index//2,index%2)
        panel.content_layout.addLayout(summary_grid)
        panel.content_layout.addLayout(placeholder_grid)
        return panel

    def _build_inventory_command_placeholder(self,title):
        tile=MarketDEXDashboardPanel(title,'Future inventory contract',tone=NorthStarPanelTone.SCOREBOARD)
        tile.setObjectName('marketdexDashboardPanel')
        tile.setProperty('dashboardRole','inventory-command-placeholder')
        tile.add_header_action(MarketDEXStatusBadge('Unavailable',StatusTone.WARNING,tile))
        detail=QLabel('Evidence unavailable. Future inventory contract required.',tile)
        detail.setObjectName('marketdexPanelDescription')
        detail.setWordWrap(True)
        tile.add_content_widget(detail)
        tile.setAccessibleName(f'{title}. Unavailable. Evidence unavailable. Future inventory contract required.')
        return tile

    def _build_visual_intelligence_shell(self):\n        return VisualIntelligencePanel(view_model=self._visual_intelligence_view_model)\n\n    def _build_unavailable_dashboard_tile(self,title,tone):
        tile=MarketDEXDashboardPanel(title,'Future contract area',tone=NorthStarPanelTone.SCOREBOARD)
        tile.setObjectName('marketdexDashboardPanel')
        tile.setProperty('dashboardRole','future-contract-placeholder')
        badge=MarketDEXStatusBadge('Unavailable',tone,tile); tile.add_header_action(badge)
        detail=QLabel('Evidence unavailable. Future contract required.',tile)
        detail.setObjectName('marketdexPanelDescription')
        detail.setWordWrap(True)
        tile.add_content_widget(detail)
        tile.setAccessibleName(f'{title}. Unavailable. Evidence unavailable. Future contract required.')
        return tile

    def refresh_inventory(self):
        listing=self.inventory_service.list_archived_inventory if self.inventory_view=='ARCHIVED' else self.inventory_service.list_inventory; self.inventory_rows=listing(search_text=self.inventory_search.text(),asset_type=self.inventory_type_filter.currentText(),sort_key=self.inventory_sort.currentText(),sort_order=self.inventory_sort_order.currentText()); self.inventory_table.setRowCount(len(self.inventory_rows)); summary=self.inventory_service.summarize_inventory(self.inventory_rows); self.inventory_summary['asset_count'].setText(f"{summary['asset_count']:,}"); self.inventory_summary['total_units'].setText(f"{summary['total_units']:,}"); self.inventory_summary['total_cost_minor'].setText(self._money(summary['total_cost_minor']))
        for row_index,row in enumerate(self.inventory_rows):
            for column,value in enumerate((row['asset_name'],row['asset_type'],row['quantity'],self._money(row['total_cost_minor']))): self.inventory_table.setItem(row_index,column,QTableWidgetItem(str(value)))
        self.inventory_table.resizeColumnsToContents(); label='archived' if self.inventory_view=='ARCHIVED' else 'active'; self.inventory_result.setText(f"Showing {len(self.inventory_rows):,} {label} inventory asset(s) • {self.inventory_sort.currentText()} {self.inventory_sort_order.currentText()}"); self.show_selected()

    def toggle_inventory_view(self):
        self.inventory_view='ARCHIVED' if self.inventory_view=='ACTIVE' else 'ACTIVE'; self.view_button.setText('View Active' if self.inventory_view=='ARCHIVED' else 'View Archived'); self.refresh_inventory()

    def import_inventory(self):
        source,_=QFileDialog.getOpenFileName(self,'Import MarketDEX Inventory CSV','','CSV Files (*.csv)')
        if not source:return
        try:
            rows=self.inventory_import_service.validate_csv(source); answer=QMessageBox.question(self,'Confirm Inventory Import',f"Import {len(rows):,} validated asset(s) as authoritative inventory events?",QMessageBox.Yes|QMessageBox.No)
            if answer!=QMessageBox.Yes:return
            imported=self.inventory_import_service.import_csv(source,f'ui-import-{uuid4().hex}'); self.refresh(); QMessageBox.information(self,'Inventory Imported',f'Imported {len(imported):,} asset(s) into MarketDEX authority.')
        except Exception as exc:QMessageBox.critical(self,'Import Blocked',str(exc))

    def export_inventory(self):
        destination,_=QFileDialog.getSaveFileName(self,'Export Current Inventory View','MarketDEX_Inventory.csv','CSV Files (*.csv)')
        if not destination:return
        try: exported=self.inventory_service.export_inventory_csv(self.inventory_rows,destination); QMessageBox.information(self,'Inventory Exported',f'Exported {len(self.inventory_rows):,} visible asset(s) to:\n{exported}')
        except Exception as exc:QMessageBox.critical(self,'Export Failed',str(exc))

    def refresh(self):
        if not hasattr(self, 'header_status_band'):
            self.header_status_band=HeaderStatusBand(self._header_status_view_model)
            self.inventory_panel.layout().insertWidget(1, self.header_status_band)
        if not hasattr(self, 'health_status_card'):
            self.health_status_card=HealthStatusCard(self._health_status_view_model)
            self.inventory_panel.layout().insertWidget(2, self.health_status_card)
        if not hasattr(self, 'operational_status_strip'):
            self.operational_status_strip=OperationalStatusStrip(self._operational_status_view_model)
            self.inventory_panel.layout().insertWidget(3, self.operational_status_strip)
        if not hasattr(self, 'next_steps_panel'):
            self.next_steps_panel=NextStepsPanel(self._next_steps_view_model)
            self.inventory_panel.layout().insertWidget(4, self.next_steps_panel)
        if not hasattr(self, 'todays_top3_panel'):
            self.todays_top3_panel=TodaysTop3Panel(self._todays_top3_view_model)
            self.inventory_panel.layout().insertWidget(5, self.todays_top3_panel)
        if not hasattr(self, 'capital_health_panel'):
            self.capital_health_panel=CapitalHealthPanel(self._capital_health_view_model)
            self.inventory_panel.layout().insertWidget(6, self.capital_health_panel)
        if not hasattr(self, 'opportunity_risk_panel'):
            self.opportunity_risk_panel=OpportunityRiskPanel(self._opportunity_risk_view_model)
            self.inventory_panel.layout().insertWidget(7, self.opportunity_risk_panel)
        if not hasattr(self, 'business_scoreboard_panel'):
            self.business_scoreboard_panel=BusinessScoreboardPanel(self._business_scoreboard_view_model)
            self.inventory_panel.layout().insertWidget(8, self.business_scoreboard_panel)
        snapshot=self.service.snapshot()
        for key in ('inventory_units','inventory_asset_count','completed_sales','verified_audits','authority_events'): self.values[key].setText(f'{snapshot[key]:,}')
        for key in ('inventory_cost_minor','revenue_minor','profit_minor'): self.values[key].setText(self._money(snapshot[key]))
        for key in ('inventory_units','inventory_asset_count'): self.inventory_command_values[key].setText(f'{snapshot[key]:,}')
        self.inventory_command_values['inventory_cost_minor'].setText(self._money(snapshot['inventory_cost_minor']))
        self.refresh_inventory(); self.footer.setText(f"LIVE DATABASE: {snapshot['database_path']} — refreshed from protected SQLite authority.")

    def selected_asset_ids(self): return [self.inventory_rows[index.row()]['asset_id'] for index in self.inventory_table.selectionModel().selectedRows() if 0<=index.row()<len(self.inventory_rows)]
    def selected_asset_id(self): selected=self.selected_asset_ids(); return selected[0] if len(selected)==1 else None

    def show_selected(self):
        selected=self.selected_asset_ids(); active=self.inventory_view=='ACTIVE'; self.adjust_button.setEnabled(active and len(selected)==1); self.bulk_adjust_button.setEnabled(active and len(selected)>1); self.archive_button.setEnabled(active and len(selected)==1); self.restore_button.setEnabled(not active and len(selected)==1)
        if not selected: self.asset_detail.setText('Select an inventory asset to view details.'); return
        if len(selected)>1: self.asset_detail.setText(f'SELECTED: {len(selected):,} inventory assets'); return
        detail=self.inventory_service.get_asset_detail(selected[0]); self.asset_detail.setText(f"SELECTED: {detail['asset_name']}  •  {detail['asset_type']}  •  Qty {detail['quantity']}  •  Cost {self._money(detail['total_cost_minor'])}  •  {detail['state']}\nPURCHASE: {self._detail_value(detail['purchase_date'])}  •  SOURCE: {self._detail_value(detail['purchase_source'])}\nSTORAGE: {self._detail_value(detail['storage_location'])}\nNOTES: {self._detail_value(detail['notes'])}")

    def add_asset(self):
        dialog=AddAssetDialog(self)
        if dialog.exec()!=QDialog.Accepted:return
        if not dialog.name.text().strip(): QMessageBox.warning(self,'Asset Required','Enter an asset name.'); return
        try:
            asset_id=f'asset-{uuid4().hex}'
            self.inventory_service.add_asset(asset_id=asset_id,asset_name=dialog.name.text(),asset_type=dialog.asset_type.currentText(),quantity=dialog.quantity.value(),total_cost_minor=round(dialog.cost.value()*100),request_id=f'ui-add-{uuid4().hex}')
            business_values={'purchase_date':dialog.purchase_date.text(),'purchase_source':dialog.purchase_source.text(),'storage_location':dialog.storage_location.text(),'notes':dialog.notes.text()}
            if any(str(value or '').strip() for value in business_values.values()): self.inventory_service.update_business_details(asset_id=asset_id,request_id=f'ui-add-business-details-{uuid4().hex}',**business_values)
            self.refresh()
        except Exception as exc:QMessageBox.critical(self,'Add Asset Failed',str(exc))

    def adjust_selected(self):
        asset_id=self.selected_asset_id()
        if asset_id is None:return
        dialog=AdjustAssetDialog(self.inventory_service.get_asset_detail(asset_id),self)
        if dialog.exec()!=QDialog.Accepted:return
        try:self.inventory_service.adjust_asset(asset_id=asset_id,quantity_delta=dialog.quantity_delta.value(),cost_delta_minor=round(dialog.cost_delta.value()*100),request_id=f'ui-adjust-{uuid4().hex}'); self.refresh()
        except Exception as exc:QMessageBox.critical(self,'Adjustment Blocked',str(exc))

    def bulk_adjust_selected(self):
        asset_ids=self.selected_asset_ids()
        if len(asset_ids)<2:return
        dialog=BulkAdjustDialog(len(asset_ids),self)
        if dialog.exec()!=QDialog.Accepted:return
        quantity_delta=dialog.quantity_delta.value(); cost_delta_minor=round(dialog.cost_delta.value()*100); answer=QMessageBox.question(self,'Confirm Bulk Adjustment',f'Apply quantity delta {quantity_delta:+,} and cost delta {self._money(cost_delta_minor)} to each of {len(asset_ids):,} selected assets?',QMessageBox.Yes|QMessageBox.No)
        if answer!=QMessageBox.Yes:return
        try: adjusted=self.inventory_service.bulk_adjust_assets(asset_ids=asset_ids,quantity_delta=quantity_delta,cost_delta_minor=cost_delta_minor,request_prefix=f'ui-bulk-adjust-{uuid4().hex}'); self.refresh(); QMessageBox.information(self,'Bulk Adjustment Complete',f'Adjusted {len(adjusted):,} inventory assets through authoritative events.')
        except Exception as exc:QMessageBox.critical(self,'Bulk Adjustment Blocked',str(exc))

    def archive_selected(self):
        asset_id=self.selected_asset_id()
        if asset_id is None:return
        detail=self.inventory_service.get_asset_detail(asset_id); answer=QMessageBox.warning(self,'Archive Inventory Asset',f"Archive {detail['asset_name']}?\n\nIt will leave the active inventory view. Authority events, inventory history, movements, and audit evidence are preserved.",QMessageBox.Yes|QMessageBox.No)
        if answer!=QMessageBox.Yes:return
        try:self.inventory_service.archive_asset(asset_id=asset_id,request_id=f'ui-archive-{uuid4().hex}'); self.refresh(); QMessageBox.information(self,'Inventory Archived','Asset archived. Historical authority evidence was preserved.')
        except Exception as exc:QMessageBox.critical(self,'Archive Blocked',str(exc))

    def restore_selected(self):
        asset_id=self.selected_asset_id()
        if asset_id is None:return
        detail=self.inventory_service.get_asset_detail(asset_id); answer=QMessageBox.question(self,'Restore Inventory Asset',f"Restore {detail['asset_name']} to active inventory?\n\nExisting quantity, cost, history, movements, and audit evidence remain preserved.",QMessageBox.Yes|QMessageBox.No)
        if answer!=QMessageBox.Yes:return
        try:self.inventory_service.restore_asset(asset_id=asset_id,request_id=f'ui-restore-{uuid4().hex}'); self.refresh(); QMessageBox.information(self,'Inventory Restored','Asset restored to active inventory through an authoritative event.')
        except Exception as exc:QMessageBox.critical(self,'Restore Blocked',str(exc))
