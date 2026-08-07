class InventoryAcquisitionEvidenceRepository:
 def get(self,c,evidence_id):return c.execute('SELECT * FROM inventory_acquisition_evidence WHERE acquisition_evidence_id=?',(evidence_id,)).fetchone()
 def add(self,c,*,evidence_id,asset_id,acquired_units,acquisition_date,purchase_source_label,provenance_reference,supersedes_evidence_id,request_id,event_id,recorded_at):
  c.execute('INSERT INTO inventory_acquisition_evidence(acquisition_evidence_id,asset_id,acquired_units,acquisition_date,purchase_source_label,provenance_reference,supersedes_acquisition_evidence_id,request_id,event_id,recorded_at) VALUES (?,?,?,?,?,?,?,?,?,?)',(evidence_id,asset_id,acquired_units,acquisition_date,purchase_source_label,provenance_reference,supersedes_evidence_id,request_id,event_id,recorded_at))
