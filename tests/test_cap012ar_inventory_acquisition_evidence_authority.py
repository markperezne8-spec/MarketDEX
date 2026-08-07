import tempfile
from pathlib import Path
import pytest
from core.database_manager import DatabaseManager
from core.event_repository import EventRepository, ReplayRejected
from repositories.asset_repository import AssetRepository
from repositories.inventory_acquisition_evidence_repository import InventoryAcquisitionEvidenceRepository
from services.asset_service import AssetService
from services.inventory_acquisition_evidence_service import InventoryAcquisitionEvidenceService


def services():
 tmp=tempfile.TemporaryDirectory(); db=DatabaseManager(Path(tmp.name)/'marketdex.sqlite3'); db.initialize(); events=EventRepository(); assets=AssetRepository(); AssetService(db,events,assets).create_asset(request_id='asset-request',asset_id='asset-1',asset_name='Asset',asset_type='SINGLE',state='COMPLETED'); return tmp,db,InventoryAcquisitionEvidenceService(db,events,assets,InventoryAcquisitionEvidenceRepository())


def test_records_immutable_canonical_acquisition_evidence_and_explicit_supersession():
 tmp,db,service=services()
 try:
  service.record(request_id='evidence-1',evidence_id='evidence-1',asset_id='asset-1',acquired_units=3,acquisition_date='2026-08-01',purchase_source_label='  TCGPlayer  ',provenance_reference='receipt-1')
  service.record(request_id='evidence-2',evidence_id='evidence-2',asset_id='asset-1',acquired_units=4,acquisition_date='2026-08-02',purchase_source_label='TCGPlayer',provenance_reference='receipt-2',supersedes_evidence_id='evidence-1')
  with db.read_connection() as c:
   rows=c.execute('SELECT acquisition_evidence_id,acquired_units,purchase_source_label,supersedes_acquisition_evidence_id FROM inventory_acquisition_evidence ORDER BY acquisition_evidence_id').fetchall()
   assert [(r['acquisition_evidence_id'],r['acquired_units'],r['purchase_source_label'],r['supersedes_acquisition_evidence_id']) for r in rows]==[('evidence-1',3,'TCGPlayer',None),('evidence-2',4,'TCGPlayer','evidence-1')]
   with pytest.raises(Exception):c.execute("UPDATE inventory_acquisition_evidence SET acquired_units=9 WHERE acquisition_evidence_id='evidence-1'")
 finally:tmp.cleanup()


@pytest.mark.parametrize('units,day,source',[(0,'2026-08-01','TCGPlayer'),(1,'2026-8-1','TCGPlayer'),(1,'2026-08-01','  ')])
def test_rejects_incomplete_or_malformed_evidence(units,day,source):
 tmp,_,service=services()
 try:
  with pytest.raises(ValueError):service.record(request_id='bad-'+str(units)+day,evidence_id='bad-'+str(units)+day,asset_id='asset-1',acquired_units=units,acquisition_date=day,purchase_source_label=source,provenance_reference='receipt')
 finally:tmp.cleanup()


def test_replay_and_missing_supersession_fail_closed():
 tmp,_,service=services()
 try:
  with pytest.raises(ValueError):service.record(request_id='missing',evidence_id='missing',asset_id='asset-1',acquired_units=1,acquisition_date='2026-08-01',purchase_source_label='TCGPlayer',provenance_reference='receipt',supersedes_evidence_id='absent')
  service.record(request_id='once',evidence_id='once',asset_id='asset-1',acquired_units=1,acquisition_date='2026-08-01',purchase_source_label='TCGPlayer',provenance_reference='receipt')
  with pytest.raises(ReplayRejected):service.record(request_id='once',evidence_id='twice',asset_id='asset-1',acquired_units=1,acquisition_date='2026-08-01',purchase_source_label='TCGPlayer',provenance_reference='receipt')
 finally:tmp.cleanup()
