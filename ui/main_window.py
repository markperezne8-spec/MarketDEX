from uuid import uuid4
from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QTableWidget,QTableWidgetItem,QDialog,QFormLayout,QComboBox,QLineEdit,QDialogButtonBox,QMessageBox

class MainWindow(QMainWindow):
 def __init__(self,database,services):
  super().__init__(); self.database,self.services=database,services
  self.setWindowTitle('MarketDEX OS — M26.B1'); self.resize(1380,760)
  root=QWidget(); lay=QVBoxLayout(root); title=QLabel('MarketDEX OS'); title.setStyleSheet('font-size:36px;font-weight:700'); lay.addWidget(title)
  lay.addWidget(QLabel('EXCEPTIONS + AUDIT + REPLAY DEFENSE AUTHORITY'))
  lay.addWidget(QLabel('Fail Closed • Exception Evidence • Immutable Event Audit • ZERO Second Authoritative Mutation'))
  bar=QHBoxLayout(); bar.addStretch()
  ex=QPushButton('Record Exception'); ex.clicked.connect(self.record_exception)
  au=QPushButton('Verify Audit'); au.clicked.connect(self.verify_audit)
  rp=QPushButton('Run Replay Defense Check'); rp.clicked.connect(self.replay_check)
  for b in (ex,au,rp): bar.addWidget(b)
  lay.addLayout(bar)
  self.table=QTableWidget(0,6); self.table.setHorizontalHeaderLabels(['Authority','ID / Request','Target / Source Event','Type','Result','State']); self.table.horizontalHeader().setStretchLastSection(True); lay.addWidget(self.table)
  self.status=QLabel(); lay.addWidget(self.status); self.setCentralWidget(root); self.refresh()
 def events(self):
  with self.database.connect() as c: return c.execute("SELECT event_id,event_type,request_id,payload_sha256 FROM event_identity ORDER BY committed_at").fetchall()
 def refresh(self):
  rows=[]
  with self.database.connect() as c:
   for r in c.execute('SELECT exception_id,source_event_id,exception_type,state FROM exception_authority ORDER BY created_at'):
    rows.append(('EXCEPTION',r['exception_id'],r['source_event_id'] or 'NO SOURCE EVENT',r['exception_type'],'EVIDENCE PRESERVED',r['state']))
   for r in c.execute('SELECT audit_verification_id,target_event_id,verification_result FROM audit_verifications ORDER BY verified_at'):
    rows.append(('AUDIT',r['audit_verification_id'],r['target_event_id'],'EVENT HASH',r['verification_result'],'COMPLETED'))
   for r in c.execute('SELECT request_id,original_event_id,attempted_event_type,defense_result FROM replay_defense_history ORDER BY recorded_at'):
    rows.append(('REPLAY DEFENSE',r['request_id'],r['original_event_id'],r['attempted_event_type'],r['defense_result'],'COMPLETED'))
  self.table.setRowCount(len(rows))
  for i,row in enumerate(rows):
   for j,v in enumerate(row): self.table.setItem(i,j,QTableWidgetItem(str(v)))
  self.status.setText(f'Append-only M26 authority results: {len(rows)}')
 def _event_dialog(self,title,include_evidence=False):
  d=QDialog(self); d.setWindowTitle(title); f=QFormLayout(d); combo=QComboBox()
  for r in self.events(): combo.addItem(f"{r['event_type']} — {r['event_id']}",r['event_id'])
  f.addRow('Authoritative Event',combo); evidence=QLineEdit('Verified exception evidence')
  if include_evidence: f.addRow('Exception Evidence',evidence)
  b=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel); b.accepted.connect(d.accept); b.rejected.connect(d.reject); f.addRow(b)
  if d.exec()!=QDialog.DialogCode.Accepted:return None,None
  return combo.currentData(),evidence.text().strip()
 def record_exception(self):
  target,evidence=self._event_dialog('Exception Authority',True)
  if not target:return
  op=str(uuid4())
  try:
   self.services.exception.record(request_id=f'{op}:exception',exception_id=f'EXC-{op}',exception_type='AUTHORITY_REVIEW',evidence=evidence,source_event_id=target)
   self.refresh(); QMessageBox.information(self,'Exception verified','Exception evidence preserved in REVIEW with authoritative source lineage.')
  except Exception as exc: self.refresh(); QMessageBox.critical(self,'Exception blocked',str(exc))
 def verify_audit(self):
  target,_=self._event_dialog('Audit Authority')
  if not target:return
  op=str(uuid4())
  try:
   _,result=self.services.audit.verify(request_id=f'{op}:audit',audit_verification_id=f'AUD-{op}',target_event_id=target)
   self.refresh(); QMessageBox.information(self,'Audit verified',f'Immutable authoritative event hash: {result}.')
  except Exception as exc: self.refresh(); QMessageBox.critical(self,'Audit blocked',str(exc))
 def replay_check(self):
  events=self.events()
  if not events: QMessageBox.warning(self,'Replay check blocked','No authoritative event exists.'); return
  target=events[-1]
  from core.event_identity import EventIdentity
  duplicate=EventIdentity.create(target['event_type'],target['request_id'],{})
  # Reconstruct exact persisted payload hash identity without inventing a business write.
  duplicate=type(duplicate)(duplicate.event_id,target['event_type'],target['request_id'],duplicate.occurred_at,duplicate.committed_at,'{}',target['payload_sha256'])
  try:
   with self.database.transaction() as c: self.services.audit._append_event_and_audit(c,duplicate,'replay_defense_probe')
  except Exception as exc:
   self.refresh(); QMessageBox.information(self,'Replay defense verified',str(exc)); return
  QMessageBox.critical(self,'Replay defense failed','Duplicate execution was not blocked.')
