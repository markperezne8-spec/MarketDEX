from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QLabel,QPushButton,
    QTableWidget,QTableWidgetItem,QFrame
)

class MetricCard(QFrame):
    def __init__(self, title):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        lay=QVBoxLayout(self)
        label=QLabel(title)
        label.setStyleSheet('font-size:13px;')
        self.value=QLabel('—')
        self.value.setStyleSheet('font-size:26px;font-weight:700;')
        lay.addWidget(label)
        lay.addWidget(self.value)

class MainWindow(QMainWindow):
    def __init__(self,database,services):
        super().__init__()
        self.database,self.services=database,services
        self.setWindowTitle('MarketDEX OS — M27.B1')
        self.resize(1380,760)

        root=QWidget()
        lay=QVBoxLayout(root)
        title=QLabel('MarketDEX OS')
        title.setStyleSheet('font-size:36px;font-weight:700')
        lay.addWidget(title)
        lay.addWidget(QLabel('MISSION CONTROL — DERIVED AUTHORITY VIEWS'))
        lay.addWidget(QLabel('Read-Only Derived Truth • Inventory • Financial • Operations • Exceptions • Audit'))

        bar=QHBoxLayout()
        bar.addStretch()
        refresh=QPushButton('Refresh Mission Control')
        refresh.clicked.connect(self.refresh)
        bar.addWidget(refresh)
        lay.addLayout(bar)

        grid=QGridLayout()
        names=[
            ('inventory_value','Inventory Cost'),
            ('units','Units On Hand'),
            ('revenue','Completed Revenue'),
            ('profit','Realized Profit'),
            ('sales','Completed Sales'),
            ('transforms','Transformations'),
            ('exceptions','Exceptions in Review'),
            ('audit','Verified Audits'),
            ('corrective','Return / Correction / Reversal'),
            ('events','Authoritative Events'),
        ]
        self.cards={}
        for i,(key,name) in enumerate(names):
            card=MetricCard(name)
            self.cards[key]=card
            grid.addWidget(card,i//5,i%5)
        lay.addLayout(grid)

        lay.addWidget(QLabel('RECENT AUTHORITATIVE EVENTS'))
        self.table=QTableWidget(0,4)
        self.table.setHorizontalHeaderLabels(['Event Type','Event ID','Request ID','Committed At'])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        lay.addWidget(self.table)

        self.status=QLabel()
        lay.addWidget(self.status)
        self.setCentralWidget(root)
        self.refresh()

    def money(self,minor):
        return f'${minor/100:,.2f}'

    def refresh(self):
        m=self.services.dashboard.mission_control()
        values={
            'inventory_value':self.money(m['inventory_cost_minor']),
            'units':str(m['units_on_hand']),
            'revenue':self.money(m['revenue_minor']),
            'profit':self.money(m['realized_profit_minor']),
            'sales':str(m['completed_sales']),
            'transforms':str(m['completed_transformations']),
            'exceptions':str(m['review_exceptions']),
            'audit':f"{m['verified_audits']} / {m['audit_count']}",
            'corrective':f"{m['returns']} / {m['corrections']} / {m['reversals']}",
            'events':str(m['authoritative_events']),
        }
        for key,value in values.items():
            self.cards[key].value.setText(value)

        rows=self.services.dashboard.recent_authority()
        self.table.setRowCount(len(rows))
        for i,row in enumerate(rows):
            for j,key in enumerate(('event_type','event_id','request_id','committed_at')):
                self.table.setItem(i,j,QTableWidgetItem(str(row[key])))
        self.status.setText(
            f"Mission Control derived from {m['authoritative_events']} permanent authoritative events — ZERO dashboard truth writes"
        )
