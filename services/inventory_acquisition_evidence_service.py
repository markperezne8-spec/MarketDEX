from datetime import date
from .base_service import AuthoritativeService


class InventoryAcquisitionEvidenceService(AuthoritativeService):
 service_name='inventory_acquisition_evidence_service'
 def __init__(self,database,events,assets,evidence):super().__init__(database,events); self.assets,self.evidence=assets,evidence
 def record(self,*,request_id,evidence_id,asset_id,acquired_units,acquisition_date,purchase_source_label,provenance_reference,supersedes_evidence_id=None):
  evidence_id=str(evidence_id).strip(); asset_id=str(asset_id).strip(); label=str(purchase_source_label).strip(); provenance=str(provenance_reference).strip()
  if not evidence_id or not asset_id or not label or not provenance:raise ValueError('acquisition evidence identity, asset, source, and provenance are required')
  if type(acquired_units) is not int or acquired_units<=0:raise ValueError('acquired_units must be a positive integer')
  if not isinstance(acquisition_date,str):raise ValueError('acquisition_date must be ISO YYYY-MM-DD')
  try: parsed=date.fromisoformat(acquisition_date)
  except ValueError as exc:raise ValueError('acquisition_date must be ISO YYYY-MM-DD') from exc
  if parsed.isoformat()!=acquisition_date:raise ValueError('acquisition_date must be ISO YYYY-MM-DD')
  supersedes_evidence_id=None if supersedes_evidence_id is None else str(supersedes_evidence_id).strip()
  if supersedes_evidence_id=='':raise ValueError('supersedes_evidence_id must not be blank')
  payload={'evidence_id':evidence_id,'asset_id':asset_id,'acquired_units':acquired_units,'acquisition_date':acquisition_date,'purchase_source_label':label,'provenance_reference':provenance,'supersedes_evidence_id':supersedes_evidence_id}
  event=self._new_event('INVENTORY_ACQUISITION_EVIDENCE',request_id,payload)
  with self.database.transaction() as c:
   if self.assets.get(c,asset_id) is None:raise ValueError('Unknown asset')
   if supersedes_evidence_id and self.evidence.get(c,supersedes_evidence_id) is None:raise ValueError('Missing superseded acquisition evidence')
   self._append_event_and_audit(c,event,'record_acquisition_evidence')
   self.evidence.add(c,evidence_id=evidence_id,asset_id=asset_id,acquired_units=acquired_units,acquisition_date=acquisition_date,purchase_source_label=label,provenance_reference=provenance,supersedes_evidence_id=supersedes_evidence_id,request_id=request_id,event_id=event.event_id,recorded_at=event.committed_at)
   self._verify_event(c,event)
  return event
