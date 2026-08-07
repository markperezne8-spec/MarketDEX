import tempfile
from datetime import date,datetime,timezone
from pathlib import Path
from core.database_manager import DatabaseManager
from core.sqlite_inventory_acquisition_projection_repository import SqliteInventoryAcquisitionProjectionRepository
from core.inventory_acquisition_projection import InventoryAcquisitionProjectionRequest,InventoryAcquisitionProjectionAvailable,InventoryAcquisitionProjectionConflict


def _db():
 tmp=tempfile.TemporaryDirectory(); db=DatabaseManager(Path(tmp.name)/'marketdex.sqlite3'); db.initialize(); return tmp,db


def _insert(db,**values):
 with db.transaction() as c:
  c.execute('INSERT INTO assets(asset_id,asset_name,asset_type,state,created_event_id,created_at) VALUES (?,?,?,?,?,?)',(values['asset_id'],values['asset_id'],'SINGLE','COMPLETED','asset-event-'+values['asset_id'],'2026-01-01T00:00:00+00:00'))
  c.execute('INSERT INTO inventory_acquisition_evidence(acquisition_evidence_id,asset_id,acquired_units,acquisition_date,purchase_source_label,provenance_reference,supersedes_acquisition_evidence_id,request_id,event_id,recorded_at) VALUES (?,?,?,?,?,?,?,?,?,?)',(values['evidence_id'],values['asset_id'],values.get('units',1),values.get('date','2026-08-01'),'TCGPlayer',values.get('provenance','receipt'),values.get('supersedes'),values['evidence_id'],values['evidence_id'],values.get('recorded','2026-08-01T00:00:00+00:00')))


def test_reads_complete_projection_and_empty_coverage_without_writes():
 tmp,db=_db()
 try:
  _insert(db,evidence_id='e1',asset_id='a1'); reader=SqliteInventoryAcquisitionProjectionRepository(db); request=InventoryAcquisitionProjectionRequest(date(2026,8,1),date(2026,9,1),datetime(2026,8,1,12,tzinfo=timezone.utc)); result=reader.read_inventory_acquisition_projection(request); assert isinstance(result,InventoryAcquisitionProjectionAvailable); assert result.records[0].inventory_id=='a1';
  before=db.read_connection
  empty=InventoryAcquisitionProjectionRequest(date(2027,1,1),date(2027,2,1),datetime(2027,1,1,tzinfo=timezone.utc)); assert reader.read_inventory_acquisition_projection(empty).records==()
 finally:tmp.cleanup()


def test_successor_is_visible_only_after_its_recorded_at():
 tmp,db=_db()
 try:
  _insert(db,evidence_id='e1',asset_id='a1',recorded='2026-08-01T00:00:00+00:00');
  with db.transaction() as c:c.execute('INSERT INTO inventory_acquisition_evidence VALUES (?,?,?,?,?,?,?,?,?,?)',('e2','a1',2,'2026-08-01','TCGPlayer','receipt-2','e1','e2','e2','2026-08-03T00:00:00+00:00'))
  reader=SqliteInventoryAcquisitionProjectionRepository(db); before=InventoryAcquisitionProjectionRequest(date(2026,8,1),date(2026,9,1),datetime(2026,8,2,tzinfo=timezone.utc)); after=InventoryAcquisitionProjectionRequest(date(2026,8,1),date(2026,9,1),datetime(2026,8,3,tzinfo=timezone.utc)); assert reader.read_inventory_acquisition_projection(before).records[0].acquired_units==1; assert reader.read_inventory_acquisition_projection(after).records[0].acquired_units==2
 finally:tmp.cleanup()


def test_cross_asset_supersession_fails_closed():
 tmp,db=_db()
 try:
  _insert(db,evidence_id='e1',asset_id='a1');
  with db.transaction() as c:
   c.execute("INSERT INTO assets(asset_id,asset_name,asset_type,state,created_event_id,created_at) VALUES ('a2','a2','SINGLE','COMPLETED','asset-event-a2','2026-01-01T00:00:00+00:00')")
   c.execute('INSERT INTO inventory_acquisition_evidence VALUES (?,?,?,?,?,?,?,?,?,?)',('e2','a2',1,'2026-08-01','TCGPlayer','receipt-2','e1','e2','e2','2026-08-02T00:00:00+00:00'))
  request=InventoryAcquisitionProjectionRequest(date(2026,8,1),date(2026,9,1),datetime(2026,8,3,tzinfo=timezone.utc)); assert isinstance(SqliteInventoryAcquisitionProjectionRepository(db).read_inventory_acquisition_projection(request),InventoryAcquisitionProjectionConflict)
 finally:tmp.cleanup()
